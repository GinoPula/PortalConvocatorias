from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import require_roles
from ..models import User
from ..services.audit import registrar
from ..services.cv_ai import evaluar_cv, extraer_texto, validar_pdf

router = APIRouter(prefix="/api/admin/cv-screening", tags=["cv-screening"])


@router.post("")
async def filtrar_cv(
    perfil_codigo: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: User = Depends(require_roles("ADMINISTRADOR", "RRHH")),
):
    """Pre-filtrado de un CV con IA para un cargo: extrae texto, le pide al
    modelo que complete el mismo cuestionario de perfil, y lo evalua con la
    misma logica determinista del formulario. No crea ninguna cuenta ni
    postulacion - solo devuelve el resultado para que RR.HH. lo revise."""
    contenido = await archivo.read()
    try:
        validar_pdf(contenido)
    except ValueError as e:
        raise HTTPException(400, str(e))

    texto = extraer_texto(contenido)
    if len(texto.strip()) < 30:
        raise HTTPException(400, "No se pudo leer texto del CV (ni directo ni por OCR). Prueba con otro archivo.")

    try:
        resultado = await evaluar_cv(perfil_codigo, texto)
    except KeyError:
        raise HTTPException(400, "Cargo no valido")
    except RuntimeError as e:
        raise HTTPException(500, str(e))

    # Sin datos personales del CV en el log de auditoria, solo el resultado.
    registrar(
        db, usuario.id, "EVALUAR", "CV_SCREENING",
        valor_nuevo=f"perfil={perfil_codigo}; cumple={resultado['evaluacion']['cumple']}",
    )
    db.commit()

    return {**resultado, "texto_extraido_preview": texto[:1500]}
