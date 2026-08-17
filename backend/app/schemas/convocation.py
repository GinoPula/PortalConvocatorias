from datetime import datetime

from pydantic import BaseModel


class RequirementIn(BaseModel):
    tipo: str
    descripcion: str = ""
    valor: str
    obligatorio: bool = True


class ScoringCriterionIn(BaseModel):
    nombre: str
    puntaje_maximo: float


class ScoringCriterionOut(ScoringCriterionIn):
    id: int

    class Config:
        from_attributes = True


class PositionIn(BaseModel):
    codigo: str
    cargo: str
    numero_plazas: int = 1
    remuneracion: float | None = None
    lugar: str = ""
    tipo_contrato: str = ""
    jornada: str = ""
    requisitos: list[RequirementIn] = []


class ConvocationIn(BaseModel):
    codigo: str
    nombre: str
    regimen: str = ""
    dependencia: str = ""
    sede: str = ""
    descripcion: str = ""
    objetivo: str = ""
    fecha_inicio: datetime | None = None
    fecha_cierre: datetime | None = None


class RequirementOut(RequirementIn):
    id: int

    class Config:
        from_attributes = True


class PositionOut(BaseModel):
    id: int
    codigo: str
    cargo: str
    numero_plazas: int
    remuneracion: float | None
    lugar: str
    tipo_contrato: str
    jornada: str
    requisitos: list[RequirementOut] = []
    criterios_puntaje: list[ScoringCriterionOut] = []

    class Config:
        from_attributes = True


class ConvocationOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    regimen: str
    dependencia: str
    sede: str
    descripcion: str
    objetivo: str
    estado: str
    fecha_publicacion: datetime | None
    fecha_inicio: datetime | None
    fecha_cierre: datetime | None
    plazas: list[PositionOut] = []

    class Config:
        from_attributes = True


class ConvocationListItem(BaseModel):
    id: int
    codigo: str
    nombre: str
    regimen: str
    sede: str
    estado: str
    fecha_cierre: datetime | None

    class Config:
        from_attributes = True
