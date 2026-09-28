from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    tipo: str
    asunto: str
    mensaje: str
    enviada: bool
    creado_en: datetime

    class Config:
        from_attributes = True
