"""Registro de auditoria: quien hizo que, sobre que registro, y cuando.
Se llama explicitamente al final de cada endpoint que escribe, dentro de la
misma transaccion (no hace commit por su cuenta - lo hace el endpoint)."""
from sqlalchemy.orm import Session

from ..models import AuditLog


def registrar(
    db: Session,
    user_id: int | None,
    accion: str,
    entidad: str,
    entidad_id: int | None = None,
    valor_anterior: str | None = None,
    valor_nuevo: str | None = None,
    ip: str = "",
):
    db.add(AuditLog(
        user_id=user_id,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip=ip,
    ))
