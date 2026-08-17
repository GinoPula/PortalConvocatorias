from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class DocumentType(Base):
    """Tipo de documento: CV, DNI, Titulo, Certificado, Licencia de conducir, etc."""

    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)


class Document(Base):
    """Documento PDF de la biblioteca documental del postulante. El archivo fisico se
    guarda en STORAGE_PATH (fuera de cualquier ruta estatica publica); solo el
    endpoint autorizado /api/postulante/documents/{id} puede entregarlo."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    postulant_id = Column(Integer, ForeignKey("postulants.id"), nullable=False)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)

    nombre_original = Column(String, nullable=False)
    nombre_almacenado = Column(String, nullable=False, unique=True)  # nombre en disco, no adivinable
    tamano_bytes = Column(Integer, default=0)
    estado = Column(String, default="CARGADO")

    creado_en = Column(DateTime, default=datetime.utcnow)

    postulante = relationship("Postulant", back_populates="documentos")
    tipo = relationship("DocumentType")
