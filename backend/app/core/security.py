"""Hash de contrasenas (PBKDF2-SHA256) y dependencias de autenticacion/RBAC.
Sesion manejada via cookie firmada (Starlette SessionMiddleware), igual que
en el sistema PSRP anterior - reutilizamos el patron ya validado en produccion."""
import hashlib
import hmac
import os

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .database import get_db
from ..models.user import User

ITERACIONES = 200_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERACIONES)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split(":")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERACIONES)
    return hmac.compare_digest(dk.hex(), hash_hex)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(401, "No autenticado")
    user = db.query(User).filter(User.id == user_id, User.activo == True).first()  # noqa: E712
    if not user:
        raise HTTPException(401, "No autenticado")
    return user


def require_roles(*roles_permitidos: str):
    """Dependencia de autorizacion: exige que el usuario tenga al menos uno de los
    roles indicados. Se valida SIEMPRE en el servidor, nunca solo en el frontend."""

    def dependencia(user: User = Depends(get_current_user)) -> User:
        nombres_rol = {r.nombre for r in user.roles}
        if not nombres_rol.intersection(roles_permitidos):
            raise HTTPException(403, "No tienes permiso para realizar esta accion")
        return user

    return dependencia
