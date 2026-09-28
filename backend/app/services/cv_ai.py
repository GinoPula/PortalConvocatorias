"""Pre-filtrado de CV con IA (Fase 5 mencionada en perfil_screening.py).

Extrae el texto de un PDF (con OCR de respaldo para CV escaneados), le pide a
un modelo de OpenAI que complete las MISMAS preguntas del cuestionario de
perfil a partir de ese texto, y evalua el resultado con la misma logica
determinista que usa el formulario (evaluar_perfil). La IA solo ayuda a leer
el CV: nunca decide por su cuenta si alguien cumple o no, y cualquier dato
que no diga explicitamente el CV se deja en null en vez de asumirse.

Es una herramienta de pre-filtrado para RR.HH., no crea cuentas ni
postulaciones - el resultado se muestra para que RR.HH. lo revise.
"""
import io
import json

import openai
import pdfplumber
import pytesseract
from openai import AsyncOpenAI
from pdf2image import convert_from_bytes

from ..core.config import settings
from .perfil_screening import NUMERO, OPCION, SI_NO, PERFILES, evaluar_perfil

TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024
MAGIC_PDF = b"%PDF-"
MIN_CARACTERES_TEXTO_NATIVO = 200  # menos que esto -> se asume CV escaneado, se intenta OCR


def validar_pdf(contenido: bytes) -> None:
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise ValueError("El archivo supera el tamano maximo permitido (10 MB)")
    if not contenido.startswith(MAGIC_PDF):
        raise ValueError("El archivo no es un PDF valido")


def extraer_texto(contenido: bytes) -> str:
    """Texto nativo del PDF; si hay muy poco (CV escaneado), intenta OCR con Tesseract."""
    with pdfplumber.open(io.BytesIO(contenido)) as pdf:
        texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)

    if len(texto.strip()) >= MIN_CARACTERES_TEXTO_NATIVO:
        return texto

    try:
        paginas_imagen = convert_from_bytes(contenido, dpi=200)
        texto_ocr = "\n".join(pytesseract.image_to_string(img, lang="spa") for img in paginas_imagen)
    except Exception:
        return texto

    return texto_ocr if len(texto_ocr.strip()) > len(texto.strip()) else texto


def _schema_json(perfil_codigo: str) -> dict:
    """JSON schema de salida armado desde las mismas preguntas del cuestionario,
    para que el modelo devuelva exactamente los campos que evaluar_perfil()
    sabe interpretar."""
    perfil = PERFILES[perfil_codigo]
    propiedades = {}
    for p in perfil["preguntas"]:
        if p["tipo"] == SI_NO:
            propiedades[p["id"]] = {"type": ["boolean", "null"], "description": p["texto"]}
        elif p["tipo"] == NUMERO:
            propiedades[p["id"]] = {"type": ["number", "null"], "description": p["texto"]}
        elif p["tipo"] == OPCION:
            propiedades[p["id"]] = {
                "type": ["string", "null"],
                "enum": p["opciones"] + [None],
                "description": p["texto"],
            }
    return {
        "type": "object",
        "properties": propiedades,
        "required": list(propiedades.keys()),
        "additionalProperties": False,
    }


INSTRUCCIONES = (
    "Eres un asistente que lee hojas de vida (CV) en espanol y extrae datos objetivos para un "
    "proceso de seleccion de personal. No inventes ni asumas nada que no este explicito en el "
    "texto: si el CV no menciona un dato, responde null para ese campo (nunca false ni 0 por "
    "defecto). Para preguntas de si/no, responde true solo si el CV lo declara o se desprende "
    "claramente del texto (por ejemplo, un certificado mencionado por su nombre); si no aparece, "
    "responde null, no false. El cargo al que postula es '{cargo}'."
)


async def evaluar_cv(perfil_codigo: str, texto_cv: str) -> dict:
    if perfil_codigo not in PERFILES:
        raise KeyError(perfil_codigo)
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY no esta configurada en el servidor")

    perfil = PERFILES[perfil_codigo]
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        respuesta = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": INSTRUCCIONES.format(cargo=perfil["nombre"])},
                {"role": "user", "content": f"Texto del CV:\n\n{texto_cv[:12000]}"},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "datos_cv", "schema": _schema_json(perfil_codigo), "strict": True},
            },
        )
    except openai.AuthenticationError:
        raise RuntimeError("La clave de OpenAI (OPENAI_API_KEY) no es valida. Verificala en el .env del servidor.")
    except openai.RateLimitError as e:
        if "credit" in str(e).lower() or "quota" in str(e).lower():
            raise RuntimeError(
                "La cuenta de OpenAI no tiene creditos disponibles. Carga saldo en "
                "platform.openai.com/settings/organization/billing y vuelve a intentar."
            )
        raise RuntimeError("Se alcanzo el limite de uso de la API de OpenAI por ahora. Intenta de nuevo en unos minutos.")
    except openai.APIError as e:
        raise RuntimeError(f"Error al conectar con OpenAI: {e}")

    datos_extraidos = json.loads(respuesta.choices[0].message.content)
    evaluacion = evaluar_perfil(perfil_codigo, datos_extraidos)
    return {"respuestas_extraidas": datos_extraidos, "evaluacion": evaluacion}
