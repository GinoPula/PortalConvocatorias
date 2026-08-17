"""Almacenamiento de documentos PDF fuera de cualquier ruta estatica publica.
Los archivos se guardan con un nombre generado (no adivinable) dentro de
STORAGE_PATH/postulant_<id>/, y solo se sirven a traves de un endpoint que
verifica autorizacion (ver app/api/postulant.py)."""
import os
import uuid

from fastapi import HTTPException, UploadFile

from ..core.config import settings

TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024  # 10 MB
MAGIC_PDF = b"%PDF-"


async def guardar_documento_pdf(archivo: UploadFile, postulant_id: int) -> tuple[str, int]:
    """Valida que sea realmente un PDF (extension, content-type y firma binaria) y
    lo guarda. Devuelve (nombre_almacenado, tamano_bytes)."""
    if not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "El archivo debe tener extension .pdf")
    if archivo.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(400, "Tipo de archivo no permitido")

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(400, "El archivo supera el tamano maximo permitido (10 MB)")
    if not contenido.startswith(MAGIC_PDF):
        raise HTTPException(400, "El archivo no es un PDF valido")

    carpeta = os.path.join(settings.STORAGE_PATH, f"postulant_{postulant_id}")
    os.makedirs(carpeta, exist_ok=True)

    nombre_almacenado = f"{uuid.uuid4().hex}.pdf"
    ruta = os.path.join(carpeta, nombre_almacenado)
    with open(ruta, "wb") as f:
        f.write(contenido)

    return f"postulant_{postulant_id}/{nombre_almacenado}", len(contenido)


def ruta_absoluta(nombre_almacenado: str) -> str:
    return os.path.join(settings.STORAGE_PATH, nombre_almacenado)
