from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Evaluation(Base):
    """Evaluacion curricular de una postulacion."""

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False, unique=True)
    evaluador_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    resultado = Column(String, default="")  # APTO / NO_APTO / OBSERVADO
    puntaje_total = Column(Numeric(6, 2), nullable=True)
    observaciones = Column(Text, default="")
    aprobado_por_supervisor = Column(Boolean, default=False)

    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    postulacion = relationship("Application", back_populates="evaluacion")
    items = relationship("EvaluationItem", back_populates="evaluacion", cascade="all, delete-orphan")


class EvaluationItem(Base):
    """Item evaluado contra un Requirement especifico de la plaza."""

    __tablename__ = "evaluation_items"

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)

    cumple = Column(Boolean, nullable=True)
    comentario = Column(Text, default="")

    evaluacion = relationship("Evaluation", back_populates="items")


class Score(Base):
    """Puntaje otorgado por criterio de la matriz de puntaje (ScoringCriterion)."""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    scoring_criterion_id = Column(Integer, ForeignKey("scoring_criteria.id"), nullable=False)

    puntaje_obtenido = Column(Numeric(5, 2), nullable=False, default=0)
    comentario = Column(Text, default="")
