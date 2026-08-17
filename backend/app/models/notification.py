from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from ..core.database import Base


class Notification(Base):
    """Cola de notificaciones (correo / interna). El envio efectivo (SMTP) se
    implementa en Fase 6+; por ahora solo se modela y encola el evento."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tipo = Column(String, nullable=False)  # REGISTRO / CONFIRMACION / POSTULACION_RECIBIDA / CAMBIO_ESTADO / RESULTADO / RECUPERACION_CLAVE
    asunto = Column(String, default="")
    mensaje = Column(Text, default="")
    enviada = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    enviada_en = Column(DateTime, nullable=True)
