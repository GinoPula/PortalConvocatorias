from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    position_id: int
    declaracion_jurada_aceptada: bool


class RequisitoValidado(BaseModel):
    requirement_id: int
    tipo: str
    descripcion: str
    valor_requerido: str
    obligatorio: bool
    cumple: bool
    motivo: str = ""


class ValidacionPrevia(BaseModel):
    puede_postular: bool
    requisitos: list[RequisitoValidado]
    motivo_bloqueo: str = ""


class ApplicationStatusHistoryOut(BaseModel):
    estado_anterior: str | None
    estado_nuevo: str
    comentario: str
    cambiado_en: datetime

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: int
    position_id: int
    estado: str
    declaracion_jurada_aceptada: bool
    declaracion_jurada_fecha: datetime | None
    codigo_constancia: str | None
    creado_en: datetime
    postulante_nombre: str | None = None
    postulante_documento: str | None = None
    plaza_cargo: str | None = None

    class Config:
        from_attributes = True


class ApplicationDetail(ApplicationOut):
    historial_estados: list[ApplicationStatusHistoryOut] = []

    class Config:
        from_attributes = True


class TransicionEstado(BaseModel):
    comentario: str = ""
