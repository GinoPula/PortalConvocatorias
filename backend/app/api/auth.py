import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user, hash_password, verify_password
from ..models import User, Postulant, Role
from ..schemas.auth import RegistroPostulante, LoginRequest, UsuarioOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limiting simple en memoria para login (proteccion basica contra fuerza bruta).
# En un despliegue multi-proceso esto deberia moverse a Redis (ver Fase 6/7).
_intentos_login: dict[str, list[float]] = {}
MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 300


def _revisar_rate_limit(clave: str):
    ahora = time.time()
    intentos = [t for t in _intentos_login.get(clave, []) if ahora - t < VENTANA_SEGUNDOS]
    if len(intentos) >= MAX_INTENTOS:
        raise HTTPException(429, "Demasiados intentos. Intenta de nuevo en unos minutos.")
    intentos.append(ahora)
    _intentos_login[clave] = intentos


def _serializar(user: User) -> UsuarioOut:
    return UsuarioOut(id=user.id, email=user.email, roles=[r.nombre for r in user.roles])


@router.post("/register", response_model=UsuarioOut)
def registrar_postulante(payload: RegistroPostulante, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Ya existe una cuenta con ese correo")
    if db.query(Postulant).filter(Postulant.numero_documento == payload.numero_documento).first():
        raise HTTPException(400, "Ya existe una cuenta con ese numero de documento")

    rol_postulante = db.query(Role).filter(Role.nombre == "POSTULANTE").first()
    if not rol_postulante:
        raise HTTPException(500, "Rol POSTULANTE no configurado - correr seed_roles.py")

    user = User(email=payload.email, password_hash=hash_password(payload.password), activo=True)
    user.roles.append(rol_postulante)
    db.add(user)
    db.flush()

    postulante = Postulant(
        user_id=user.id,
        tipo_documento=payload.tipo_documento,
        numero_documento=payload.numero_documento,
        nombres=payload.nombres,
        apellidos=payload.apellidos,
        telefono=payload.telefono,
    )
    db.add(postulante)
    db.commit()
    return _serializar(user)


@router.post("/login", response_model=UsuarioOut)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    _revisar_rate_limit(payload.email.lower())

    user = db.query(User).filter(User.email == payload.email, User.activo == True).first()  # noqa: E712
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Correo o contrasena incorrectos")

    request.session["user_id"] = user.id
    return _serializar(user)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/me", response_model=UsuarioOut)
def me(user: User = Depends(get_current_user)):
    return _serializar(user)
