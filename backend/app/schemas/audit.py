from datetime import datetime

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    user_id: int | None
    usuario_email: str | None = None
    accion: str
    entidad: str
    entidad_id: int | None
    valor_anterior: str | None
    valor_nuevo: str | None
    ip: str
    creado_en: datetime

    class Config:
        from_attributes = True
