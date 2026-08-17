from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..core.database import Base

ESTADOS_CONVOCATORIA = ["BORRADOR", "PUBLICADA", "ABIERTA", "CERRADA", "EN_EVALUACION", "FINALIZADA", "CANCELADA"]


class Convocation(Base):
    """Convocatoria laboral. Maquina de estados: BORRADOR -> PUBLICADA -> ABIERTA ->
    CERRADA -> EN_EVALUACION -> FINALIZADA (o CANCELADA antes de FINALIZADA)."""

    __tablename__ = "convocations"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False, unique=True, index=True)
    nombre = Column(String, nullable=False)
    regimen = Column(String, default="")  # CAS / LOCADOR_OTROS
    dependencia = Column(String, default="")
    es_en_sede = Column(Boolean, default=False)
    sede = Column(String, default="")  # departamento seleccionado, solo si es_en_sede=True
    descripcion = Column(String, default="")  # "Acerca del puesto"
    requisitos_texto = Column(String, default="")
    deseable_texto = Column(String, default="")
    objetivo = Column(String, default="")
    estado = Column(String, nullable=False, default="BORRADOR")

    fecha_publicacion = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)

    eliminado = Column(Boolean, default=False)  # soft delete
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    actualizado_por = Column(Integer, ForeignKey("users.id"), nullable=True)

    plazas = relationship("Position", back_populates="convocatoria", cascade="all, delete-orphan")
    documentos = relationship("ConvocationDocument", back_populates="convocatoria", cascade="all, delete-orphan")


class ConvocationDocument(Base):
    """Bases, TDR, cronograma, anexos y comunicados de una convocatoria."""

    __tablename__ = "convocation_documents"

    id = Column(Integer, primary_key=True)
    convocation_id = Column(Integer, ForeignKey("convocations.id"), nullable=False)

    tipo = Column(String, nullable=False)  # BASES / TDR / CRONOGRAMA / ANEXO / COMUNICADO
    nombre_original = Column(String, nullable=False)
    nombre_almacenado = Column(String, nullable=False, unique=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    convocatoria = relationship("Convocation", back_populates="documentos")


class Position(Base):
    """Plaza dentro de una convocatoria."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    convocation_id = Column(Integer, ForeignKey("convocations.id"), nullable=False)

    codigo = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    numero_plazas = Column(Integer, default=1)
    remuneracion = Column(Numeric(10, 2), nullable=True)
    lugar = Column(String, default="")
    tipo_contrato = Column(String, default="")
    jornada = Column(String, default="")

    eliminado = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    convocatoria = relationship("Convocation", back_populates="plazas")
    requisitos = relationship("Requirement", back_populates="plaza", cascade="all, delete-orphan")
    criterios_puntaje = relationship("ScoringCriterion", back_populates="plaza", cascade="all, delete-orphan")
    postulaciones = relationship("Application", back_populates="plaza")


class Requirement(Base):
    """Requisito configurable de una plaza (el 'motor de requisitos').
    Ej: tipo=EXPERIENCIA, valor='3 anios', obligatorio=True."""

    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    tipo = Column(String, nullable=False)  # FORMACION / EXPERIENCIA / LICENCIA / CURSO / OTRO
    descripcion = Column(String, default="")
    valor = Column(String, nullable=False)
    obligatorio = Column(Boolean, default=True)

    plaza = relationship("Position", back_populates="requisitos")


class ScoringCriterion(Base):
    """Criterio y peso de la matriz de puntaje de una plaza."""

    __tablename__ = "scoring_criteria"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    nombre = Column(String, nullable=False)  # ej. "Formacion", "Experiencia especifica", "Entrevista"
    puntaje_maximo = Column(Numeric(5, 2), nullable=False)

    plaza = relationship("Position", back_populates="criterios_puntaje")
