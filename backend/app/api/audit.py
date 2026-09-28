from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import require_roles
from ..models import AuditLog, User
from ..schemas.audit import AuditLogOut

router = APIRouter(prefix="/api/admin/auditoria", tags=["auditoria"])

# Acciones y entidades que efectivamente se registran hoy (ver services/audit.py
# y sus llamadas). Sirve para poblar los filtros del panel sin inventar valores.
ACCIONES = ["LOGIN", "LOGOUT", "CREAR", "EDITAR", "ELIMINAR", "CAMBIO_ESTADO", "EVALUAR"]
ENTIDADES = ["USER", "CONVOCATION", "POSITION", "APPLICATION", "EVALUATION"]


@router.get("", response_model=list[AuditLogOut])
def listar(
    entidad: str | None = None,
    accion: str | None = None,
    q: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "AUDITOR")),
):
    query = db.query(AuditLog)
    if entidad:
        query = query.filter(AuditLog.entidad == entidad)
    if accion:
        query = query.filter(AuditLog.accion == accion)
    if q:
        query = query.join(User, AuditLog.user_id == User.id).filter(User.email.ilike(f"%{q}%"))
    return query.order_by(AuditLog.creado_en.desc()).offset(offset).limit(limit).all()
