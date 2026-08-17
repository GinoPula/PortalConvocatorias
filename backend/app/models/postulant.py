from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Postulant(Base):
    """Datos personales del postulante. Relacion 1:1 con User cuando el rol es POSTULANTE."""

    __tablename__ = "postulants"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    tipo_documento = Column(String, nullable=False)  # DNI / CE
    numero_documento = Column(String, nullable=False, unique=True, index=True)
    nombres = Column(String, nullable=False, default="")
    apellidos = Column(String, nullable=False, default="")
    fecha_nacimiento = Column(Date, nullable=True)
    sexo = Column(String, default="")
    direccion = Column(String, default="")
    departamento = Column(String, default="")
    provincia = Column(String, default="")
    distrito = Column(String, default="")
    telefono = Column(String, default="")
    ruc = Column(String, default="")

    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="postulante")
    formacion_academica = relationship("AcademicRecord", back_populates="postulante", cascade="all, delete-orphan")
    experiencia_laboral = relationship("WorkExperience", back_populates="postulante", cascade="all, delete-orphan")
    capacitaciones = relationship("Training", back_populates="postulante", cascade="all, delete-orphan")
    documentos = relationship("Document", back_populates="postulante", cascade="all, delete-orphan")
    postulaciones = relationship("Application", back_populates="postulante")


class AcademicRecord(Base):
    """Formacion academica: secundaria, tecnico, bachiller, titulo, maestria, doctorado."""

    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True)
    postulant_id = Column(Integer, ForeignKey("postulants.id"), nullable=False)

    nivel = Column(String, nullable=False)
    institucion = Column(String, default="")
    carrera = Column(String, default="")
    grado = Column(String, default="")
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    estado = Column(String, default="")  # EN_CURSO / CONCLUIDO / EGRESADO
    documento_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    postulante = relationship("Postulant", back_populates="formacion_academica")


class WorkExperience(Base):
    """Experiencia laboral, con sector publico/privado para el calculo de dias por sector."""

    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True)
    postulant_id = Column(Integer, ForeignKey("postulants.id"), nullable=False)

    institucion = Column(String, nullable=False, default="")
    sector = Column(String, default="")  # PUBLICO / PRIVADO
    cargo = Column(String, default="")
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)  # null = actualidad
    descripcion = Column(Text, default="")
    documento_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    postulante = relationship("Postulant", back_populates="experiencia_laboral")


class Training(Base):
    """Curso o capacitacion."""

    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True)
    postulant_id = Column(Integer, ForeignKey("postulants.id"), nullable=False)

    nombre = Column(String, nullable=False)
    institucion = Column(String, default="")
    horas = Column(Integer, nullable=True)
    fecha = Column(Date, nullable=True)
    documento_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    postulante = relationship("Postulant", back_populates="capacitaciones")
