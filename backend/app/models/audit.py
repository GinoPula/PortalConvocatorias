from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from ..core.database import Base


class AuditLog(Base):
    """Auditoria generica: quien hizo que, sobre que registro, y cuando.
    Se escribe desde una dependencia de FastAPI compartida (Fase 6), no manualmente
    en cada endpoint, para garantizar cobertura consistente."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    accion = Column(String, nullable=False)  # LOGIN / LOGOUT / CREAR / EDITAR / ELIMINAR / PUBLICAR / CERRAR / EVALUAR / CAMBIO_ESTADO / DESCARGA / EXPORTAR
    entidad = Column(String, nullable=False)  # nombre de la tabla/entidad afectada
    entidad_id = Column(Integer, nullable=True)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    ip = Column(String, default="")
    creado_en = Column(DateTime, default=datetime.utcnow)
