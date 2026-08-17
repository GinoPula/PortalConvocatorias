from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import require_roles
from ..models import AcademicRecord, Document, DocumentType, Training, User, WorkExperience
from ..schemas.postulant import (
    AcademicRecordIn,
    AcademicRecordOut,
    DocumentOut,
    ExperienciaResumen,
    PostulantOut,
    PostulantUpdate,
    TrainingIn,
    TrainingOut,
    WorkExperienceIn,
    WorkExperienceOut,
)
from ..services.experience import calcular_experiencia
from ..services.storage import guardar_documento_pdf, ruta_absoluta

router = APIRouter(prefix="/api/postulante", tags=["postulante"])


def _requiere_postulante(user: User = Depends(require_roles("POSTULANTE"))):
    if not user.postulante:
        raise HTTPException(400, "El usuario no tiene un perfil de postulante asociado")
    return user.postulante


# ---------- Perfil ----------

@router.get("/profile", response_model=PostulantOut)
def obtener_perfil(postulante=Depends(_requiere_postulante)):
    return postulante


@router.put("/profile", response_model=PostulantOut)
def editar_perfil(payload: PostulantUpdate, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(postulante, campo, valor)
    db.commit()
    db.refresh(postulante)
    return postulante


# ---------- Formacion academica ----------

@router.get("/academic-records", response_model=list[AcademicRecordOut])
def listar_formacion(postulante=Depends(_requiere_postulante)):
    return postulante.formacion_academica


@router.post("/academic-records", response_model=AcademicRecordOut)
def crear_formacion(payload: AcademicRecordIn, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    registro = AcademicRecord(postulant_id=postulante.id, **payload.model_dump())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.delete("/academic-records/{registro_id}")
def eliminar_formacion(registro_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    registro = db.query(AcademicRecord).filter(
        AcademicRecord.id == registro_id, AcademicRecord.postulant_id == postulante.id
    ).first()
    if not registro:
        raise HTTPException(404, "Registro no encontrado")
    db.delete(registro)
    db.commit()
    return {"ok": True}


# ---------- Experiencia laboral ----------

@router.get("/work-experiences", response_model=list[WorkExperienceOut])
def listar_experiencia(postulante=Depends(_requiere_postulante)):
    return postulante.experiencia_laboral


@router.post("/work-experiences", response_model=WorkExperienceOut)
def crear_experiencia(payload: WorkExperienceIn, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    registro = WorkExperience(postulant_id=postulante.id, **payload.model_dump())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.delete("/work-experiences/{registro_id}")
def eliminar_experiencia(registro_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    registro = db.query(WorkExperience).filter(
        WorkExperience.id == registro_id, WorkExperience.postulant_id == postulante.id
    ).first()
    if not registro:
        raise HTTPException(404, "Registro no encontrado")
    db.delete(registro)
    db.commit()
    return {"ok": True}


@router.get("/work-experiences/resumen", response_model=ExperienciaResumen)
def resumen_experiencia(postulante=Depends(_requiere_postulante)):
    return calcular_experiencia(postulante.experiencia_laboral)


# ---------- Capacitaciones ----------

@router.get("/trainings", response_model=list[TrainingOut])
def listar_capacitaciones(postulante=Depends(_requiere_postulante)):
    return postulante.capacitaciones


@router.post("/trainings", response_model=TrainingOut)
def crear_capacitacion(payload: TrainingIn, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    registro = Training(postulant_id=postulante.id, **payload.model_dump())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


# ---------- Documentos ----------

@router.get("/documents", response_model=list[DocumentOut])
def listar_documentos(postulante=Depends(_requiere_postulante)):
    return postulante.documentos


@router.post("/documents", response_model=DocumentOut)
async def subir_documento(
    document_type_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    postulante=Depends(_requiere_postulante),
):
    tipo = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not tipo:
        raise HTTPException(400, "Tipo de documento invalido")

    nombre_almacenado, tamano = await guardar_documento_pdf(archivo, postulante.id)

    documento = Document(
        postulant_id=postulante.id,
        document_type_id=document_type_id,
        nombre_original=archivo.filename,
        nombre_almacenado=nombre_almacenado,
        tamano_bytes=tamano,
        estado="CARGADO",
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento


@router.get("/documents/{document_id}/descargar")
def descargar_documento(document_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    documento = db.query(Document).filter(Document.id == document_id).first()
    if not documento:
        raise HTTPException(404, "Documento no encontrado")
    # Un postulante solo puede acceder a sus propios documentos.
    if documento.postulant_id != postulante.id:
        raise HTTPException(403, "No tienes acceso a este documento")
    return FileResponse(ruta_absoluta(documento.nombre_almacenado), filename=documento.nombre_original, media_type="application/pdf")


@router.delete("/documents/{document_id}")
def eliminar_documento(document_id: int, db: Session = Depends(get_db), postulante=Depends(_requiere_postulante)):
    documento = db.query(Document).filter(Document.id == document_id).first()
    if not documento or documento.postulant_id != postulante.id:
        raise HTTPException(404, "Documento no encontrado")
    db.delete(documento)
    db.commit()
    return {"ok": True}
