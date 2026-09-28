"""Crea y publica las convocatorias de locadores de la UBO Tumbes (PNC-Maquinarias):
Conductor de vehiculo pesado y Operador de maquinaria pesada, segun sus TDR.
Es idempotente: si ya existe una plaza con el mismo perfil, no la duplica.
Uso: python seed_convocatorias_tumbes.py"""
from datetime import datetime

from app.core.database import SessionLocal
from app.models import Convocation, Position, Requirement

DEPENDENCIA = "Programa Nuestras Ciudades - PNC Maquinarias"
LUGAR = "Unidad Basica Operativa Tumbes"
MARCO = (
    "Intervenciones por Declaratoria de Estado de Emergencia, en el marco del Decreto Supremo N° 124-2026-PCM "
    "(FTI N.° 073-2026-LD-E-TUM y FTI N.° 074-2026-LD-E-TUM)."
)

REQ_COMUNES_DJ = (
    "Declaraciones juradas: celular operativo con camara e internet; Equipo de Proteccion Personal completo; "
    "kit de herramientas minimo; conocimiento de ISO 37001:2016 y Gestion de Riesgo"
)
REQ_COMUNES_ADMIN = "RUC habilitado, CCI registrado asociado al RUC y Registro Nacional de Proveedores (RNP)"
REQ_SCTR = "SCTR vigente (salud y pension), a presentar al inicio del servicio"

CONVOCATORIAS = [
    {
        "nombre": "Servicio de conduccion de vehiculo pesado - UBO Tumbes",
        "perfil_codigo": "CONDUCTOR_VEHICULO_PESADO",
        "cargo": "Conductor de vehiculo pesado",
        "objetivo": (
            "Contratar el servicio de conduccion de vehiculo pesado para la ejecucion de intervenciones priorizadas "
            "por la Autoridad Nacional del Agua (ANA) en el ambito de la Unidad Basica Operativa Tumbes del "
            "PNC-Maquinarias."
        ),
        "descripcion": (
            f"Servicio de conduccion de vehiculo pesado para la UBO Tumbes. {MARCO}\n\n"
            "Actividades:\n"
            "- Conducir y transportar material con la unidad asignada, segun la programacion y metas de la UBO.\n"
            "- Registrar diariamente los Partes Diarios de la unidad asignada.\n"
            "- Capturar fotografias diarias de horometros y/o odometros, al inicio y termino de la jornada.\n"
            "- Inspeccionar la unidad al inicio y termino de la jornada.\n"
            "- Recibir y devolver la unidad en las mismas condiciones operativas.\n"
            "- Cumplir el Reglamento Nacional de Transito y la normativa del MTC.\n"
            "- Comunicar a la Coordinacion de la UBO, en un maximo de 24 horas, cualquier incidencia.\n\n"
            "Plazo: hasta 30 dias calendario. Lugar: ambito de la UBO Tumbes."
        ),
        "requisitos_texto": (
            "- Licencia de conducir minima clase A, categoria III B.\n"
            "- Secundaria completa.\n"
            "- Experiencia general minima de 3 anios en entidades publicas y/o privadas.\n"
            "- Experiencia especifica minima de 2 anios como conductor de vehiculo pesado.\n"
            "- Certificado y/o constancia de conductor de vehiculo pesado.\n"
            "- Curso y/o capacitacion en seguridad vial y/o manejo defensivo.\n"
            "- No registrar en el Record de Conductor faltas graves o muy graves en los ultimos 12 meses.\n"
            f"- {REQ_COMUNES_ADMIN}.\n"
            f"- {REQ_COMUNES_DJ}.\n"
            f"- {REQ_SCTR}."
        ),
        "requisitos": [
            ("LICENCIA", "Licencia de conducir", "Licencia de conducir minima clase A, categoria III B (A-IIIb)"),
            ("FORMACION", "Secundaria completa", "SECUNDARIA"),
            ("EXPERIENCIA", "Experiencia general en entidades publicas y/o privadas", "3 anios"),
            ("OTRO", "Experiencia especifica", "Minimo 2 anios como conductor de vehiculo pesado"),
            ("OTRO", "Capacitacion", "Certificado y/o constancia de conductor de vehiculo pesado"),
            ("OTRO", "Capacitacion", "Curso y/o capacitacion en seguridad vial y/o manejo defensivo"),
            ("OTRO", "Record de Conductor", "Sin faltas graves o muy graves en los ultimos 12 meses"),
            ("OTRO", "Condiciones generales", REQ_COMUNES_ADMIN),
            ("OTRO", "Declaraciones juradas", REQ_COMUNES_DJ),
            ("OTRO", "Seguro", REQ_SCTR),
        ],
    },
    {
        "nombre": "Servicio de operacion de maquinaria pesada - UBO Tumbes",
        "perfil_codigo": "OPERADOR_MAQUINARIA_PESADA",
        "cargo": "Operador de maquinaria pesada",
        "objetivo": (
            "Contratar los servicios de un operador de maquinaria pesada para la ejecucion de intervenciones "
            "priorizadas por la Autoridad Nacional del Agua (ANA) en el ambito de la Unidad Basica Operativa Tumbes "
            "del PNC-Maquinarias."
        ),
        "descripcion": (
            f"Servicio de operacion de maquinaria pesada para la UBO Tumbes. {MARCO}\n\n"
            "Actividades:\n"
            "- Realizar actividades operativas de movimiento de tierras, segun la programacion y metas de la UBO.\n"
            "- Registrar diariamente los Partes Diarios de la unidad asignada.\n"
            "- Capturar fotografias diarias de los horometros, al inicio y termino de la jornada.\n"
            "- Inspeccionar la unidad al inicio y termino de la jornada.\n"
            "- Recibir y devolver la unidad en las mismas condiciones operativas.\n"
            "- Comunicar a la Coordinacion de la UBO, en un maximo de 24 horas, cualquier incidencia.\n\n"
            "Plazo: 30 dias calendario. Lugar: ambito de la UBO Tumbes."
        ),
        "requisitos_texto": (
            "- Secundaria completa.\n"
            "- Experiencia general minima de 3 anios en entidades publicas y/o privadas.\n"
            "- Experiencia minima de 2 anios como operador de maquinaria pesada.\n"
            "- Certificado y/o constancia de curso de Operacion de Maquinaria Pesada.\n"
            "- Certificado y/o constancia de cursos de prevencion de accidentes y/o seguridad y salud en el trabajo.\n"
            f"- {REQ_COMUNES_ADMIN}.\n"
            f"- {REQ_COMUNES_DJ}.\n"
            f"- {REQ_SCTR}."
        ),
        "requisitos": [
            ("FORMACION", "Secundaria completa", "SECUNDARIA"),
            ("EXPERIENCIA", "Experiencia general en entidades publicas y/o privadas", "3 anios"),
            ("OTRO", "Experiencia especifica", "Minimo 2 anios como operador de maquinaria pesada"),
            ("OTRO", "Capacitacion", "Certificado y/o constancia de curso de Operacion de Maquinaria Pesada"),
            ("OTRO", "Capacitacion", "Certificado y/o constancia de cursos de prevencion de accidentes y/o seguridad y salud en el trabajo"),
            ("OTRO", "Condiciones generales", REQ_COMUNES_ADMIN),
            ("OTRO", "Declaraciones juradas", REQ_COMUNES_DJ),
            ("OTRO", "Seguro", REQ_SCTR),
        ],
    },
]


def _siguiente_codigo(db) -> str:
    patron = f"LOC-{datetime.utcnow().year}-"
    maximo = 0
    for (codigo,) in db.query(Convocation.codigo).filter(Convocation.codigo.like(f"{patron}%")).all():
        try:
            maximo = max(maximo, int(codigo.rsplit("-", 1)[-1]))
        except ValueError:
            continue
    return f"{patron}{maximo + 1:03d}"


def run():
    db = SessionLocal()
    try:
        for datos in CONVOCATORIAS:
            ya_existe = db.query(Position).join(Convocation).filter(
                Position.perfil_codigo == datos["perfil_codigo"],
                Position.eliminado == False,  # noqa: E712
                Convocation.eliminado == False,  # noqa: E712
            ).first()
            if ya_existe:
                print(f"Ya existe una convocatoria para {datos['perfil_codigo']}, se omite.")
                continue

            ahora = datetime.utcnow()
            codigo = _siguiente_codigo(db)
            convocatoria = Convocation(
                codigo=codigo,
                nombre=datos["nombre"],
                regimen="LOCADOR",
                dependencia=DEPENDENCIA,
                es_en_sede=True,
                sede="Tumbes",
                descripcion=datos["descripcion"],
                requisitos_texto=datos["requisitos_texto"],
                objetivo=datos["objetivo"],
                estado="ABIERTA",
                fecha_publicacion=ahora,
                fecha_inicio=ahora,
            )
            db.add(convocatoria)
            db.flush()

            plaza = Position(
                convocation_id=convocatoria.id,
                codigo=f"{codigo}-P01",
                cargo=datos["cargo"],
                numero_plazas=1,
                lugar=LUGAR,
                tipo_contrato="Locacion de servicios",
                perfil_codigo=datos["perfil_codigo"],
            )
            db.add(plaza)
            db.flush()

            for tipo, descripcion, valor in datos["requisitos"]:
                db.add(Requirement(position_id=plaza.id, tipo=tipo, descripcion=descripcion, valor=valor, obligatorio=True))

            print(f"Convocatoria creada y abierta: {codigo} - {datos['nombre']}")

        db.commit()
        print("Listo.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
