import re

from pydantic import BaseModel, EmailStr, field_validator


class RegistroPostulante(BaseModel):
    tipo_documento: str  # DNI / CE
    numero_documento: str
    nombres: str
    apellidos: str
    email: EmailStr
    telefono: str = ""
    password: str
    confirmar_password: str
    acepta_terminos: bool

    @field_validator("numero_documento")
    @classmethod
    def validar_documento(cls, v, info):
        tipo = info.data.get("tipo_documento")
        if tipo == "DNI" and not re.fullmatch(r"\d{8}", v):
            raise ValueError("El DNI debe tener 8 digitos")
        if tipo == "CE" and not re.fullmatch(r"[A-Za-z0-9]{6,12}", v):
            raise ValueError("Carne de Extranjeria invalido")
        return v

    @field_validator("password")
    @classmethod
    def validar_password_segura(cls, v):
        if len(v) < 8 or not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("La contrasena debe tener minimo 8 caracteres, con letras y numeros")
        return v

    @field_validator("confirmar_password")
    @classmethod
    def validar_coincide(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Las contrasenas no coinciden")
        return v

    @field_validator("acepta_terminos")
    @classmethod
    def validar_acepta(cls, v):
        if not v:
            raise ValueError("Debe aceptar los terminos y condiciones")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UsuarioOut(BaseModel):
    id: int
    email: str
    roles: list[str]
