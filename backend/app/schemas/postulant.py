from datetime import date

from pydantic import BaseModel


class PostulantUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    direccion: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None
    telefono: str | None = None
    ruc: str | None = None


class PostulantOut(BaseModel):
    id: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None
    sexo: str
    direccion: str
    departamento: str
    provincia: str
    distrito: str
    telefono: str
    ruc: str

    class Config:
        from_attributes = True


class AcademicRecordIn(BaseModel):
    nivel: str
    institucion: str = ""
    carrera: str = ""
    grado: str = ""
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: str = ""
    documento_id: int | None = None


class AcademicRecordOut(AcademicRecordIn):
    id: int

    class Config:
        from_attributes = True


class WorkExperienceIn(BaseModel):
    institucion: str
    sector: str  # PUBLICO / PRIVADO
    cargo: str = ""
    fecha_inicio: date | None = None
    fecha_fin: date | None = None  # null = actualidad
    descripcion: str = ""
    documento_id: int | None = None


class WorkExperienceOut(WorkExperienceIn):
    id: int

    class Config:
        from_attributes = True


class TrainingIn(BaseModel):
    nombre: str
    institucion: str = ""
    horas: int | None = None
    fecha: date | None = None
    documento_id: int | None = None


class TrainingOut(TrainingIn):
    id: int

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: int
    document_type_id: int
    nombre_original: str
    tamano_bytes: int
    estado: str

    class Config:
        from_attributes = True


class ExperienciaResumen(BaseModel):
    total_meses: int
    anios: int
    meses: int
    dias: int
    meses_sector_publico: int
    meses_sector_privado: int
