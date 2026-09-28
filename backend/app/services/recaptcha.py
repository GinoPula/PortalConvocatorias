"""Verifica un token de Google reCAPTCHA v2 contra la API de Google antes de
dejar pasar un login. Sin RECAPTCHA_SECRET_KEY configurada la verificacion
falla siempre (fail closed): un login mal configurado no debe quedar sin
proteccion por un descuido en el .env."""
import httpx

from ..core.config import settings

GOOGLE_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verificar_recaptcha(token: str, ip: str = "") -> bool:
    if not settings.RECAPTCHA_SECRET_KEY or not token:
        return False
    datos = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    if ip:
        datos["remoteip"] = ip
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(GOOGLE_VERIFY_URL, data=datos)
            resultado = resp.json()
    except (httpx.HTTPError, ValueError):
        return False
    return bool(resultado.get("success"))
