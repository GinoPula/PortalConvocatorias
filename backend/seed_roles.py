"""Siembra los roles base del RBAC y un usuario Administrador inicial.
Uso: python seed_roles.py"""
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Role, User, DocumentType

ROLES = [
    ("POSTULANTE", "Ciudadano que se registra y postula a convocatorias"),
    ("ADMINISTRADOR", "Administracion general del portal"),
    ("RRHH", "Gestiona convocatorias, plazas y postulaciones"),
    ("EVALUADOR", "Evalua postulaciones asignadas"),
    ("SUPERVISOR", "Revisa y aprueba evaluaciones"),
    ("AUDITOR", "Acceso de solo lectura y auditoria"),
]

TIPOS_DOCUMENTO = ["CV", "DNI", "Titulo", "Certificado", "Constancia de trabajo", "Licencia de conducir", "Otro"]


def run():
    db = SessionLocal()
    try:
        roles_por_nombre = {}
        for nombre, descripcion in ROLES:
            rol = db.query(Role).filter(Role.nombre == nombre).first()
            if not rol:
                rol = Role(nombre=nombre, descripcion=descripcion)
                db.add(rol)
                db.flush()
                print(f"Rol creado: {nombre}")
            roles_por_nombre[nombre] = rol

        for nombre in TIPOS_DOCUMENTO:
            existente = db.query(DocumentType).filter(DocumentType.nombre == nombre).first()
            if not existente:
                db.add(DocumentType(nombre=nombre))
                print(f"Tipo de documento creado: {nombre}")

        admin = db.query(User).filter(User.email == "admin@vivienda.gob.pe").first()
        if not admin:
            admin = User(
                email="admin@vivienda.gob.pe",
                password_hash=hash_password("Admin123"),
                activo=True,
                email_confirmado=True,
            )
            admin.roles.append(roles_por_nombre["ADMINISTRADOR"])
            db.add(admin)
            print("Usuario administrador creado: admin@vivienda.gob.pe / Admin123")

        db.commit()
        print("Siembra completada.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
