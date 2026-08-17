from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..core.database import get_db
from ..core.security import require_roles
from ..models import Convocation, Position, Requirement, User
from ..schemas.convocation import ConvocationIn, ConvocationOut, ConvocationListItem, PositionIn

router_public = APIRouter(prefix="/api/convocatorias", tags=["convocatorias-publico"])
router_admin = APIRouter(prefix="/api/admin/convocatorias", tags=["convocatorias-admin"])

# Estados visibles al ciudadano: solo lo publicado en adelante.
ESTADOS_PUBLICOS = {"PUBLICADA", "ABIERTA", "CERRADA", "EN_EVALUACION", "FINALIZADA"}

# Una vez publicada, estos campos ya no pueden editarse libremente (bloqueo de
# campos criticos exigido por el requerimiento - control de version simplificado).
CAMPOS_BLOQUEADOS_TRAS_PUBLICAR = {"codigo", "regimen"}


def _query_base(db: Session):
    return db.query(Convocation).options(
        joinedload(Convocation.plazas).joinedload(Position.requisitos),
        joinedload(Convocation.plazas).joinedload(Position.criterios_puntaje),
    ).filter(Convocation.eliminado == False)  # noqa: E712


# ---------- Portal publico ----------

@router_public.get("", response_model=list[ConvocationListItem])
def listar_publicas(
    regimen: str | None = None,
    sede: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = _query_base(db).filter(Convocation.estado.in_(ESTADOS_PUBLICOS))
    if regimen:
        query = query.filter(Convocation.regimen == regimen)
    if sede:
        query = query.filter(Convocation.sede == sede)
    if q:
        like = f"%{q}%"
        query = query.filter((Convocation.nombre.ilike(like)) | (Convocation.codigo.ilike(like)))
    return query.order_by(Convocation.fecha_publicacion.desc()).all()


@router_public.get("/{convocation_id}", response_model=ConvocationOut)
def detalle_publico(convocation_id: int, db: Session = Depends(get_db)):
    conv = _query_base(db).filter(Convocation.id == convocation_id).first()
    if not conv or conv.estado not in ESTADOS_PUBLICOS:
        raise HTTPException(404, "Convocatoria no encontrada")
    return conv


# ---------- Panel administrativo ----------

@router_admin.get("", response_model=list[ConvocationListItem])
def listar_admin(
    estado: str | None = None,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "AUDITOR")),
):
    query = _query_base(db)
    if estado:
        query = query.filter(Convocation.estado == estado)
    return query.order_by(Convocation.creado_en.desc()).all()


@router_admin.get("/{convocation_id}", response_model=ConvocationOut)
def detalle_admin(
    convocation_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH", "EVALUADOR", "SUPERVISOR", "AUDITOR")),
):
    conv = _query_base(db).filter(Convocation.id == convocation_id).first()
    if not conv:
        raise HTTPException(404, "Convocatoria no encontrada")
    return conv


@router_admin.post("", response_model=ConvocationOut)
def crear(
    payload: ConvocationIn,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    if db.query(Convocation).filter(Convocation.codigo == payload.codigo).first():
        raise HTTPException(400, "Ya existe una convocatoria con ese codigo")
    conv = Convocation(**payload.model_dump(), creado_por=usuario.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router_admin.put("/{convocation_id}", response_model=ConvocationOut)
def editar(
    convocation_id: int,
    payload: ConvocationIn,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    conv = db.query(Convocation).filter(Convocation.id == convocation_id, Convocation.eliminado == False).first()  # noqa: E712
    if not conv:
        raise HTTPException(404, "Convocatoria no encontrada")

    datos_nuevos = payload.model_dump()
    if conv.estado != "BORRADOR":
        for campo in CAMPOS_BLOQUEADOS_TRAS_PUBLICAR:
            if getattr(conv, campo) != datos_nuevos.get(campo):
                raise HTTPException(400, f"El campo '{campo}' no puede modificarse tras publicar la convocatoria")

    for campo, valor in datos_nuevos.items():
        setattr(conv, campo, valor)
    conv.actualizado_por = usuario.id
    db.commit()
    db.refresh(conv)
    return conv


@router_admin.post("/{convocation_id}/plazas", response_model=ConvocationOut)
def agregar_plaza(
    convocation_id: int,
    payload: PositionIn,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    conv = db.query(Convocation).filter(Convocation.id == convocation_id, Convocation.eliminado == False).first()  # noqa: E712
    if not conv:
        raise HTTPException(404, "Convocatoria no encontrada")

    datos = payload.model_dump()
    requisitos_in = datos.pop("requisitos")
    plaza = Position(convocation_id=conv.id, **datos)
    db.add(plaza)
    db.flush()
    for req in requisitos_in:
        db.add(Requirement(position_id=plaza.id, **req))
    db.commit()
    db.refresh(conv)
    return conv


TRANSICIONES_CONVOCATORIA = {
    "BORRADOR": {"PUBLICADA", "CANCELADA"},
    "PUBLICADA": {"ABIERTA", "CANCELADA"},
    "ABIERTA": {"CERRADA", "CANCELADA"},
    "CERRADA": {"EN_EVALUACION", "CANCELADA"},
    "EN_EVALUACION": {"FINALIZADA", "CANCELADA"},
}


@router_admin.post("/{convocation_id}/transicion/{nuevo_estado}", response_model=ConvocationOut)
def cambiar_estado(
    convocation_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    conv = db.query(Convocation).filter(Convocation.id == convocation_id, Convocation.eliminado == False).first()  # noqa: E712
    if not conv:
        raise HTTPException(404, "Convocatoria no encontrada")

    permitidos = TRANSICIONES_CONVOCATORIA.get(conv.estado, set())
    if nuevo_estado not in permitidos:
        raise HTTPException(400, f"No se puede pasar de '{conv.estado}' a '{nuevo_estado}'")

    conv.estado = nuevo_estado
    if nuevo_estado == "PUBLICADA":
        conv.fecha_publicacion = datetime.utcnow()
    conv.actualizado_por = usuario.id
    db.commit()
    db.refresh(conv)
    return conv


@router_admin.delete("/{convocation_id}")
def eliminar(
    convocation_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR")),
):
    conv = db.query(Convocation).filter(Convocation.id == convocation_id).first()
    if not conv:
        raise HTTPException(404, "Convocatoria no encontrada")
    conv.eliminado = True  # soft delete
    db.commit()
    return {"ok": True}
