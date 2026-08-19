from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import hash_password, require_roles
from ..models import Role, User
from ..schemas.auth import ROLES_STAFF, UsuarioStaffIn, UsuarioStaffOut

router = APIRouter(prefix="/api/admin/usuarios", tags=["usuarios-admin"])


def _serializar(user: User) -> UsuarioStaffOut:
    return UsuarioStaffOut(id=user.id, email=user.email, roles=[r.nombre for r in user.roles], activo=user.activo)


@router.get("", response_model=list[UsuarioStaffOut])
def listar(
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR")),
):
    staff = (
        db.query(User)
        .join(User.roles)
        .filter(Role.nombre.in_(ROLES_STAFF))
        .distinct()
        .order_by(User.creado_en.desc())
        .all()
    )
    return [_serializar(u) for u in staff]


@router.post("", response_model=UsuarioStaffOut)
def crear(
    payload: UsuarioStaffIn,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR")),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Ya existe una cuenta con ese correo")

    roles = db.query(Role).filter(Role.nombre.in_(payload.roles)).all()
    if len(roles) != len(set(payload.roles)):
        raise HTTPException(500, "Algun rol no esta configurado - correr seed_roles.py")

    nuevo = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        activo=True,
        email_confirmado=True,
        creado_por=usuario.id,
    )
    nuevo.roles = roles
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return _serializar(nuevo)


@router.post("/{user_id}/desactivar", response_model=UsuarioStaffOut)
def desactivar(
    user_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR")),
):
    if user_id == usuario.id:
        raise HTTPException(400, "No puedes desactivar tu propia cuenta")
    objetivo = db.query(User).filter(User.id == user_id).first()
    if not objetivo:
        raise HTTPException(404, "Usuario no encontrado")
    objetivo.activo = False
    objetivo.actualizado_por = usuario.id
    db.commit()
    db.refresh(objetivo)
    return _serializar(objetivo)


@router.post("/{user_id}/activar", response_model=UsuarioStaffOut)
def activar(
    user_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR")),
):
    objetivo = db.query(User).filter(User.id == user_id).first()
    if not objetivo:
        raise HTTPException(404, "Usuario no encontrado")
    objetivo.activo = True
    objetivo.actualizado_por = usuario.id
    db.commit()
    db.refresh(objetivo)
    return _serializar(objetivo)
