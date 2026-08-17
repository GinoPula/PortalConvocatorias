from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..core.database import get_db
from ..core.security import require_roles
from ..models import (
    Application,
    ApplicationStatusHistory,
    Evaluation,
    EvaluationItem,
    Position,
    Requirement,
    Score,
    ScoringCriterion,
    User,
)
from ..schemas.convocation import PositionOut, ScoringCriterionIn, ScoringCriterionOut
from ..schemas.evaluation import EvaluationCreate, EvaluationOut, RankingItem

router = APIRouter(prefix="/api/admin/postulaciones", tags=["evaluaciones"])
router_ranking = APIRouter(prefix="/api/admin/plazas", tags=["evaluaciones"])


@router_ranking.get("/{position_id}", response_model=PositionOut)
def obtener_plaza(
    position_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "EVALUADOR", "SUPERVISOR", "AUDITOR")),
):
    plaza = db.query(Position).filter(Position.id == position_id).first()
    if not plaza:
        raise HTTPException(404, "Plaza no encontrada")
    return plaza


@router_ranking.post("/{position_id}/criterios", response_model=ScoringCriterionOut)
def agregar_criterio_puntaje(
    position_id: int,
    payload: ScoringCriterionIn,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    plaza = db.query(Position).filter(Position.id == position_id).first()
    if not plaza:
        raise HTTPException(404, "Plaza no encontrada")
    criterio = ScoringCriterion(position_id=position_id, **payload.model_dump())
    db.add(criterio)
    db.commit()
    db.refresh(criterio)
    return criterio


@router.post("/{application_id}/evaluacion", response_model=EvaluationOut)
def registrar_evaluacion(
    application_id: int,
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("EVALUADOR", "ADMINISTRADOR", "RRHH")),
):
    aplicacion = db.query(Application).filter(Application.id == application_id).first()
    if not aplicacion:
        raise HTTPException(404, "Postulacion no encontrada")
    if aplicacion.estado != "EN_EVALUACION":
        raise HTTPException(400, "Solo se puede evaluar una postulacion en estado EN_EVALUACION")

    # Validar que los requirement_id e items pertenezcan efectivamente a la plaza de esta postulacion.
    requisitos_validos = {r.id for r in aplicacion.plaza.requisitos}
    for item in payload.items:
        if item.requirement_id not in requisitos_validos:
            raise HTTPException(400, f"El requisito {item.requirement_id} no pertenece a esta plaza")

    criterios_por_id = {c.id: c for c in aplicacion.plaza.criterios_puntaje}
    for puntaje in payload.puntajes:
        criterio = criterios_por_id.get(puntaje.scoring_criterion_id)
        if not criterio:
            raise HTTPException(400, f"El criterio {puntaje.scoring_criterion_id} no pertenece a esta plaza")
        if puntaje.puntaje_obtenido > float(criterio.puntaje_maximo):
            raise HTTPException(400, f"El puntaje de '{criterio.nombre}' excede el maximo permitido ({criterio.puntaje_maximo})")

    evaluacion = aplicacion.evaluacion
    if evaluacion:
        db.query(EvaluationItem).filter(EvaluationItem.evaluation_id == evaluacion.id).delete()
        db.query(Score).filter(Score.evaluation_id == evaluacion.id).delete()
    else:
        evaluacion = Evaluation(application_id=aplicacion.id)
        db.add(evaluacion)
        db.flush()

    evaluacion.evaluador_id = usuario.id
    evaluacion.resultado = payload.resultado
    evaluacion.observaciones = payload.observaciones
    evaluacion.puntaje_total = sum((p.puntaje_obtenido for p in payload.puntajes), 0.0)
    evaluacion.aprobado_por_supervisor = False

    for item in payload.items:
        db.add(EvaluationItem(evaluation_id=evaluacion.id, **item.model_dump()))
    for puntaje in payload.puntajes:
        db.add(Score(evaluation_id=evaluacion.id, **puntaje.model_dump()))

    nuevo_estado = "APTA" if payload.resultado == "APTO" else "NO_APTA"
    db.add(ApplicationStatusHistory(
        application_id=aplicacion.id, estado_anterior=aplicacion.estado, estado_nuevo=nuevo_estado,
        comentario=f"Evaluacion registrada: {payload.resultado}", cambiado_por=usuario.id,
    ))
    aplicacion.estado = nuevo_estado

    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router.get("/{application_id}/evaluacion", response_model=EvaluationOut)
def obtener_evaluacion(
    application_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("EVALUADOR", "ADMINISTRADOR", "RRHH", "SUPERVISOR", "AUDITOR")),
):
    evaluacion = db.query(Evaluation).filter(Evaluation.application_id == application_id).first()
    if not evaluacion:
        raise HTTPException(404, "Esta postulacion aun no tiene evaluacion registrada")
    return evaluacion


@router.post("/{application_id}/evaluacion/aprobar", response_model=EvaluationOut)
def aprobar_evaluacion(
    application_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("SUPERVISOR")),
):
    """Segunda instancia: el Supervisor revisa y aprueba la evaluacion de un Evaluador."""
    evaluacion = db.query(Evaluation).filter(Evaluation.application_id == application_id).first()
    if not evaluacion:
        raise HTTPException(404, "Esta postulacion aun no tiene evaluacion registrada")
    evaluacion.supervisor_id = usuario.id
    evaluacion.aprobado_por_supervisor = True
    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router_ranking.get("/{position_id}/ranking", response_model=list[RankingItem])
def ranking_por_plaza(
    position_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "SUPERVISOR", "AUDITOR")),
):
    plaza = db.query(Position).filter(Position.id == position_id).first()
    if not plaza:
        raise HTTPException(404, "Plaza no encontrada")

    aplicaciones = (
        db.query(Application)
        .options(joinedload(Application.evaluacion), joinedload(Application.postulante))
        .filter(Application.position_id == position_id)
        .all()
    )

    items = []
    for a in aplicaciones:
        if not a.evaluacion:
            continue
        items.append(RankingItem(
            application_id=a.id,
            postulante_nombre=f"{a.postulante.nombres} {a.postulante.apellidos}",
            postulante_documento=a.postulante.numero_documento,
            puntaje_total=float(a.evaluacion.puntaje_total) if a.evaluacion.puntaje_total is not None else None,
            resultado=a.evaluacion.resultado,
            estado_postulacion=a.estado,
        ))
    items.sort(key=lambda x: (x.puntaje_total is None, -(x.puntaje_total or 0)))
    return items
