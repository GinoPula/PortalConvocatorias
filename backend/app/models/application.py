from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base

ESTADOS_POSTULACION = [
    "BORRADOR", "RECIBIDA", "EN_EVALUACION", "APTA", "NO_APTA",
    "ENTREVISTA", "SELECCIONADA", "NO_SELECCIONADA", "RETIRADA", "APELACION",
]

# Transiciones permitidas - validadas SIEMPRE en el backend, nunca se acepta
# un estado arbitrario enviado desde el cliente.
TRANSICIONES_PERMITIDAS = {
    "BORRADOR": {"RECIBIDA"},
    "RECIBIDA": {"EN_EVALUACION", "RETIRADA"},
    "EN_EVALUACION": {"APTA", "NO_APTA"},
    "APTA": {"ENTREVISTA", "RETIRADA"},
    "NO_APTA": {"APELACION"},
    "APELACION": {"EN_EVALUACION"},
    "ENTREVISTA": {"SELECCIONADA", "NO_SELECCIONADA"},
    "SELECCIONADA": set(),
    "NO_SELECCIONADA": set(),
    "RETIRADA": set(),
}


class Application(Base):
    """Postulacion de un Postulant a una Position (plaza) especifica."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    postulant_id = Column(Integer, ForeignKey("postulants.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    estado = Column(String, nullable=False, default="BORRADOR")

    declaracion_jurada_aceptada = Column(Boolean, default=False)
    declaracion_jurada_fecha = Column(DateTime, nullable=True)
    declaracion_jurada_ip = Column(String, default="")

    codigo_constancia = Column(String, nullable=True, unique=True)

    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    postulante = relationship("Postulant", back_populates="postulaciones")
    plaza = relationship("Position", back_populates="postulaciones")
    documentos = relationship("ApplicationDocument", back_populates="postulacion", cascade="all, delete-orphan")
    historial_estados = relationship(
        "ApplicationStatusHistory", back_populates="postulacion", cascade="all, delete-orphan"
    )
    evaluacion = relationship("Evaluation", back_populates="postulacion", uselist=False)

    @property
    def postulante_nombre(self):
        return f"{self.postulante.nombres} {self.postulante.apellidos}" if self.postulante else None

    @property
    def postulante_documento(self):
        return self.postulante.numero_documento if self.postulante else None

    @property
    def plaza_cargo(self):
        return self.plaza.cargo if self.plaza else None


class ApplicationDocument(Base):
    """Documento adjuntado especificamente a una postulacion (puede referenciar un
    Document ya existente del postulante, o ser especifico de esta postulacion)."""

    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    postulacion = relationship("Application", back_populates="documentos")


class ApplicationStatusHistory(Base):
    """Historial de transiciones de estado de una postulacion (auditoria de la
    maquina de estados)."""

    __tablename__ = "application_status_history"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    estado_anterior = Column(String, nullable=True)
    estado_nuevo = Column(String, nullable=False)
    comentario = Column(Text, default="")
    cambiado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    cambiado_en = Column(DateTime, default=datetime.utcnow)

    postulacion = relationship("Application", back_populates="historial_estados")
