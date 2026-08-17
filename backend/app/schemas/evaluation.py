from datetime import datetime

from pydantic import BaseModel


class EvaluationItemIn(BaseModel):
    requirement_id: int
    cumple: bool
    comentario: str = ""


class ScoreIn(BaseModel):
    scoring_criterion_id: int
    puntaje_obtenido: float
    comentario: str = ""


class EvaluationCreate(BaseModel):
    resultado: str  # APTO / NO_APTO / OBSERVADO
    observaciones: str = ""
    items: list[EvaluationItemIn] = []
    puntajes: list[ScoreIn] = []


class EvaluationItemOut(EvaluationItemIn):
    id: int

    class Config:
        from_attributes = True


class ScoreOut(ScoreIn):
    id: int

    class Config:
        from_attributes = True


class EvaluationOut(BaseModel):
    id: int
    application_id: int
    evaluador_id: int | None
    supervisor_id: int | None
    resultado: str
    puntaje_total: float | None
    observaciones: str
    aprobado_por_supervisor: bool
    creado_en: datetime
    items: list[EvaluationItemOut] = []

    class Config:
        from_attributes = True


class RankingItem(BaseModel):
    application_id: int
    postulante_nombre: str
    postulante_documento: str
    puntaje_total: float | None
    resultado: str
    estado_postulacion: str
