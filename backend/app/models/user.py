from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from ..core.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    """Rol del sistema: POSTULANTE, ADMINISTRADOR, RRHH, EVALUADOR, SUPERVISOR, AUDITOR."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, default="")

    permisos = relationship("Permission", secondary=role_permissions, back_populates="roles")
    usuarios = relationship("User", secondary=user_roles, back_populates="roles")


class Permission(Base):
    """Permiso granular (ej. 'convocatorias.crear', 'postulaciones.evaluar')."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False, unique=True)
    descripcion = Column(String, default="")

    roles = relationship("Role", secondary=role_permissions, back_populates="permisos")


class User(Base):
    """Cuenta de acceso: tanto postulantes ciudadanos como personal interno
    (RR.HH., Evaluador, Supervisor, Auditor, Administrador) son User con roles distintos."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    email_confirmado = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    actualizado_por = Column(Integer, ForeignKey("users.id"), nullable=True)

    roles = relationship("Role", secondary=user_roles, back_populates="usuarios")
    postulante = relationship("Postulant", back_populates="user", uselist=False)
