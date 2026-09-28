"""Cuestionario de perfil por cargo, derivado de los TDR.

Es la unica fuente de las preguntas y reglas: el frontend las descarga desde
GET /api/auth/perfiles y el backend las vuelve a evaluar al guardar, de modo que
la decision "cumple / no cumple" nunca depende de lo que calcule el cliente.

Las preguntas eliminatorias son los "Requisitos minimos del Locador" del TDR.
Las respuestas tienen caracter de declaracion jurada; RR.HH. las verifica
despues contra los documentos.
"""

SI_NO = "si_no"
NUMERO = "numero"
OPCION = "opcion"


def _si_no(id_, texto, eliminatoria=True):
    return {"id": id_, "texto": texto, "tipo": SI_NO, "eliminatoria": eliminatoria}


def _numero(id_, texto, minimo):
    return {"id": id_, "texto": texto, "tipo": NUMERO, "eliminatoria": True, "minimo": minimo}


def _preguntas_comunes(experiencia_especifica, certificado, curso):
    return [
        _si_no("ruc_habilitado", "Tengo Registro Unico de Contribuyente (RUC) habilitado"),
        _si_no("cci_registrado", "Tengo Codigo de Cuenta Interbancario (CCI) registrado y asociado a mi RUC"),
        _si_no("rnp", "Cuento con Registro Nacional de Proveedores (RNP)"),
        _si_no("secundaria_completa", "Tengo secundaria completa"),
        _numero("anios_experiencia_general", "Anios de experiencia general en entidades publicas y/o privadas (minimo 3)", 3),
        _numero("anios_experiencia_especifica", experiencia_especifica, 2),
        _si_no("certificado_cargo", certificado),
        _si_no("curso_seguridad", curso),
        _si_no("dj_celular", "Declaro contar con un celular operativo con camara fotografica y acceso a internet"),
        _si_no("dj_epp", "Declaro contar con Equipo de Proteccion Personal completo para la intervencion"),
        _si_no(
            "dj_herramientas",
            "Declaro contar con kit de herramientas minimo: 2 llaves francesas (grande y mediana), "
            "2 desarmadores (plano y estrella), 1 alicate universal y 1 llave ajustable universal",
        ),
        _si_no(
            "dj_iso37001",
            "Declaro tener conocimiento de ISO 37001:2016 (sistema de gestion antisoborno) y de Gestion de Riesgo",
        ),
        _si_no("sctr", "Me comprometo a contar con SCTR vigente (salud y pension) al inicio del servicio", eliminatoria=False),
    ]


CATEGORIAS_LICENCIA = ["Ninguna", "A-I", "A-IIa", "A-IIb", "A-IIIa", "A-IIIb", "A-IIIc"]

PERFILES = {
    "CONDUCTOR_VEHICULO_PESADO": {
        "nombre": "Conductor de vehiculo pesado",
        "preguntas": [
            {
                "id": "licencia_categoria",
                "texto": "Categoria de tu licencia de conducir vigente (se exige como minimo A-IIIb)",
                "tipo": OPCION,
                "eliminatoria": True,
                "opciones": CATEGORIAS_LICENCIA,
                "validas": ["A-IIIb", "A-IIIc"],
            },
            _si_no(
                "sin_faltas_graves",
                "No registro en mi Record de Conductor faltas graves o muy graves en los ultimos 12 meses",
            ),
            *_preguntas_comunes(
                "Anios de experiencia como conductor de vehiculo pesado (minimo 2)",
                "Cuento con certificado y/o constancia de conductor de vehiculo pesado",
                "Cuento con curso y/o capacitacion en seguridad vial y/o manejo defensivo",
            ),
        ],
    },
    "OPERADOR_MAQUINARIA_PESADA": {
        "nombre": "Operador de maquinaria pesada",
        "preguntas": _preguntas_comunes(
            "Anios de experiencia como operador de maquinaria pesada (minimo 2)",
            "Cuento con certificado y/o constancia de curso de Operacion de Maquinaria Pesada",
            "Cuento con certificado y/o constancia de cursos de prevencion de accidentes y/o seguridad y salud en el trabajo",
        ),
    },
}


def listar_perfiles() -> list[dict]:
    return [{"codigo": codigo, **datos} for codigo, datos in PERFILES.items()]


def _coincide(pregunta: dict, valor) -> bool:
    if pregunta["tipo"] == SI_NO:
        return valor is True
    if pregunta["tipo"] == NUMERO:
        return valor is not None and valor >= pregunta["minimo"]
    return valor in pregunta["validas"]


def _motivo(pregunta: dict, valor) -> str:
    if pregunta["tipo"] == NUMERO:
        return f"Requisito no cumplido - {pregunta['texto']}: declaraste {valor if valor is not None else 0}"
    if pregunta["tipo"] == OPCION:
        return f"Requisito no cumplido - {pregunta['texto']}: declaraste {valor or 'sin respuesta'}"
    return f"Requisito no cumplido - {pregunta['texto']}"


def _normalizar(pregunta: dict, valor):
    """Devuelve el valor validado y tipado, o lanza ValueError si es de un tipo invalido."""
    if valor is None or valor == "":
        return None
    if pregunta["tipo"] == SI_NO:
        if not isinstance(valor, bool):
            raise ValueError(f"Respuesta invalida en '{pregunta['id']}'")
        return valor
    if pregunta["tipo"] == NUMERO:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0 or valor > 80:
            raise ValueError(f"Respuesta invalida en '{pregunta['id']}'")
        return valor
    if valor not in pregunta["opciones"]:
        raise ValueError(f"Respuesta invalida en '{pregunta['id']}'")
    return valor


def evaluar_perfil(perfil_codigo: str, respuestas: dict) -> dict:
    """Evalua las respuestas contra el perfil. Una pregunta eliminatoria sin
    responder cuenta como incumplida. Lanza KeyError si el perfil no existe y
    ValueError si alguna respuesta tiene un tipo invalido."""
    perfil = PERFILES[perfil_codigo]

    normalizadas = {}
    motivos = []
    for pregunta in perfil["preguntas"]:
        valor = _normalizar(pregunta, respuestas.get(pregunta["id"]))
        normalizadas[pregunta["id"]] = valor
        if pregunta["eliminatoria"] and not _coincide(pregunta, valor):
            motivos.append(_motivo(pregunta, valor))

    return {"cumple": not motivos, "motivos": motivos, "respuestas": normalizadas}
