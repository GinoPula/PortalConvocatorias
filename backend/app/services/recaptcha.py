"""Verifica un token de Google reCAPTCHA v3 contra la API de Google antes de
dejar pasar un login. A diferencia de v2 (casilla), v3 no tiene "aprobado/
rechazado" propio: devuelve un puntaje de 0.0 (probable bot) a 1.0 (probable
humano), y quien integra la API decide el umbral. Sin RECAPTCHA_SECRET_KEY
configurada la verificacion falla siempre (fail closed): un login mal
configurado no debe quedar sin proteccion por un descuido en el .env."""
import httpx

from ..core.config import settings

GOOGLE_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verificar_recaptcha(token: str, action_esperada: str = "", ip: str = "") -> bool:
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

    if not resultado.get("success"):
        return False
    if action_esperada and "action" in resultado and resultado.get("action") != action_esperada:
        return False
    # Una clave v3 real siempre incluye "score"; las claves de prueba de Google
    # (utiles solo en desarrollo local) no lo incluyen - en ese caso no hay
    # puntaje que exigir, "success" ya es la unica senal disponible.
    if "score" in resultado and float(resultado["score"]) < settings.RECAPTCHA_MIN_SCORE:
        return False
    return True
