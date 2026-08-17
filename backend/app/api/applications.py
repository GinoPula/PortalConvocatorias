import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from ..core.database import get_db
from ..core.security import get_current_user, require_roles
from ..models import (
    Application,
    ApplicationStatusHistory,
    Position,
    User,
    TRANSICIONES_PERMITIDAS,
)
from ..schemas.application import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationOut,
    TransicionEstado,
    ValidacionPrevia,
)
from ..services.requirements_engine import validar_requisitos

router_postulante = APIRouter(prefix="/api/postulante/postulaciones", tags=["postulaciones-postulante"])
router_admin = APIRouter(prefix="/api/admin/postulaciones", tags=["postulaciones-admin"])


def _requiere_postulante(user: User = Depends(require_roles("POSTULANTE"))):
    if not user.postulante:
        raise HTTPException(400, "El usuario no tiene un perfil de postulante asociado")
    return user.postulante


def _validacion_previa(postulante, plaza: Position) -> ValidacionPrevia:
    if not plaza.convocatoria or plaza.convocatoria.estado != "ABIERTA":
        return ValidacionPrevia(puede_postular=False, requisitos=[], motivo_bloqueo="La convocatoria no esta abierta para postulaciones")

    ahora = datetime.utcnow()
    if plaza.convocatoria.fecha_cierre and ahora > plaza.convocatoria.fecha_cierre:
        return ValidacionPrevia(puede_postular=False, requisitos=[], motivo_bloqueo="La convocatoria ya cerro (fecha limite vencida)")
    if plaza.convocatoria.fecha_inicio and ahora < plaza.convocatoria.fecha_inicio:
        return ValidacionPrevia(puede_postular=False, requisitos=[], motivo_bloqueo="La convocatoria aun no inicia el periodo de postulacion")

    resultado = validar_requisitos(postulante, plaza.requisitos)
    falta_obligatorio = any(not r["cumple"] and r["obligatorio"] for r in resultado)
    return ValidacionPrevia(
        puede_postular=not falta_obligatorio,
        requisitos=resultado,
        motivo_bloqueo="No cumples uno o mas requisitos obligatorios" if falta_obligatorio else "",
    )


# ---------- Postulante ----------

@router_postulante.get("/validar/{position_id}", response_model=ValidacionPrevia)
def validar_antes_de_postular(position_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    plaza = db.query(Position).options(joinedload(Position.requisitos), joinedload(Position.convocatoria)).filter(
        Position.id == position_id, Position.eliminado == False  # noqa: E712
    ).first()
    if not plaza:
        raise HTTPException(404, "Plaza no encontrada")
    return _validacion_previa(postulante, plaza)


@router_postulante.post("", response_model=ApplicationOut)
def postular(payload: ApplicationCreate, request: Request, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    if not payload.declaracion_jurada_aceptada:
        raise HTTPException(400, "Debe aceptar la declaracion jurada para postular")

    plaza = db.query(Position).options(joinedload(Position.requisitos), joinedload(Position.convocatoria)).filter(
        Position.id == payload.position_id, Position.eliminado == False  # noqa: E712
    ).first()
    if not plaza:
        raise HTTPException(404, "Plaza no encontrada")

    ya_postulo = db.query(Application).filter(
        Application.postulant_id == postulante.id, Application.position_id == plaza.id
    ).first()
    if ya_postulo:
        raise HTTPException(400, "Ya has postulado a esta plaza")

    validacion = _validacion_previa(postulante, plaza)
    if not validacion.puede_postular:
        raise HTTPException(400, validacion.motivo_bloqueo or "No cumples los requisitos de la plaza")

    aplicacion = Application(
        postulant_id=postulante.id,
        position_id=plaza.id,
        estado="RECIBIDA",
        declaracion_jurada_aceptada=True,
        declaracion_jurada_fecha=datetime.utcnow(),
        declaracion_jurada_ip=request.client.host if request.client else "",
    )
    db.add(aplicacion)
    db.flush()
    aplicacion.codigo_constancia = f"CONST-{aplicacion.id}-{uuid.uuid4().hex[:8].upper()}"
    db.add(ApplicationStatusHistory(application_id=aplicacion.id, estado_anterior=None, estado_nuevo="RECIBIDA"))
    db.commit()
    db.refresh(aplicacion)
    return aplicacion


@router_postulante.get("", response_model=list[ApplicationOut])
def mis_postulaciones(db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    return db.query(Application).filter(Application.postulant_id == postulante.id).order_by(Application.creado_en.desc()).all()


@router_postulante.get("/{application_id}", response_model=ApplicationDetail)
def detalle_postulacion(application_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    aplicacion = db.query(Application).options(joinedload(Application.historial_estados)).filter(
        Application.id == application_id, Application.postulant_id == postulante.id
    ).first()
    if not aplicacion:
        raise HTTPException(404, "Postulacion no encontrada")
    return aplicacion


@router_postulante.post("/{application_id}/retirar", response_model=ApplicationOut)
def retirar_postulacion(application_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    aplicacion = db.query(Application).filter(
        Application.id == application_id, Application.postulant_id == postulante.id
    ).first()
    if not aplicacion:
        raise HTTPException(404, "Postulacion no encontrada")
    if "RETIRADA" not in TRANSICIONES_PERMITIDAS.get(aplicacion.estado, set()):
        raise HTTPException(400, f"No se puede retirar una postulacion en estado '{aplicacion.estado}'")

    db.add(ApplicationStatusHistory(application_id=aplicacion.id, estado_anterior=aplicacion.estado, estado_nuevo="RETIRADA"))
    aplicacion.estado = "RETIRADA"
    db.commit()
    db.refresh(aplicacion)
    return aplicacion


# ---------- Admin / RR.HH. / Evaluador ----------

@router_admin.get("", response_model=list[ApplicationOut])
def listar_admin(
    position_id: int | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "EVALUADOR", "SUPERVISOR", "AUDITOR")),
):
    query = db.query(Application)
    if position_id:
        query = query.filter(Application.position_id == position_id)
    if estado:
        query = query.filter(Application.estado == estado)
    return query.order_by(Application.creado_en.desc()).all()


@router_admin.post("/{application_id}/transicion/{nuevo_estado}", response_model=ApplicationOut)
def cambiar_estado_admin(
    application_id: int,
    nuevo_estado: str,
    payload: TransicionEstado,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "EVALUADOR", "SUPERVISOR")),
):
    aplicacion = db.query(Application).filter(Application.id == application_id).first()
    if not aplicacion:
        raise HTTPException(404, "Postulacion no encontrada")

    permitidos = TRANSICIONES_PERMITIDAS.get(aplicacion.estado, set())
    if nuevo_estado not in permitidos:
        raise HTTPException(400, f"No se puede pasar de '{aplicacion.estado}' a '{nuevo_estado}'")

    db.add(ApplicationStatusHistory(
        application_id=aplicacion.id,
        estado_anterior=aplicacion.estado,
        estado_nuevo=nuevo_estado,
        comentario=payload.comentario,
        cambiado_por=usuario.id,
    ))
    aplicacion.estado = nuevo_estado
    db.commit()
    db.refresh(aplicacion)
    return aplicacion
