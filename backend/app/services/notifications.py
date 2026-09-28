"""Encola una notificacion interna para un usuario. El envio real (correo)
se implementa aparte (Fase 6+); por ahora queda registrada y visible en
GET /api/postulante/notificaciones. No hace commit por su cuenta."""
from sqlalchemy.orm import Session

from ..models import Notification


def notificar(db: Session, user_id: int, tipo: str, asunto: str, mensaje: str):
    db.add(Notification(user_id=user_id, tipo=tipo, asunto=asunto, mensaje=mensaje))
