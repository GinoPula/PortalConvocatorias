"""Compara el perfil de un Postulant contra los Requirement de una Position.
La IA puede ayudar a extraer datos del perfil (Fase 5), pero esta comparacion
y la decision de bloqueo es siempre determinista y auditable."""
from .experience import calcular_experiencia

NIVELES_FORMACION = ["SECUNDARIA", "TECNICO", "BACHILLER", "TITULO", "MAESTRIA", "DOCTORADO"]


def _nivel_maximo_formacion(formacion_academica: list) -> str | None:
    alcanzado = None
    for registro in formacion_academica:
        nivel = (registro.nivel or "").upper()
        if nivel in NIVELES_FORMACION:
            if alcanzado is None or NIVELES_FORMACION.index(nivel) > NIVELES_FORMACION.index(alcanzado):
                alcanzado = nivel
    return alcanzado


def _cumple_formacion(postulante, valor_requerido: str) -> tuple[bool, str]:
    requerido = valor_requerido.upper()
    alcanzado = _nivel_maximo_formacion(postulante.formacion_academica)
    if not alcanzado:
        return False, "No se registro formacion academica"
    if requerido not in NIVELES_FORMACION:
        return alcanzado == requerido, f"Nivel registrado: {alcanzado}"
    cumple = NIVELES_FORMACION.index(alcanzado) >= NIVELES_FORMACION.index(requerido)
    return cumple, f"Nivel registrado: {alcanzado}"


def _cumple_experiencia(postulante, valor_requerido: str) -> tuple[bool, str]:
    # valor_requerido esperado como "N anios" o "N meses"
    partes = valor_requerido.strip().split()
    try:
        cantidad = int(partes[0])
    except (ValueError, IndexError):
        return False, "Requisito de experiencia mal configurado"
    unidad = partes[1].lower() if len(partes) > 1 else "anios"
    meses_requeridos = cantidad * 12 if unidad.startswith("anio") else cantidad

    resumen = calcular_experiencia(postulante.experiencia_laboral)
    cumple = resumen["total_meses"] >= meses_requeridos
    return cumple, f"Experiencia registrada: {resumen['anios']} anios, {resumen['meses']} meses"


def _cumple_curso(postulante, valor_requerido: str) -> tuple[bool, str]:
    nombres = [c.nombre.upper() for c in postulante.capacitaciones]
    cumple = any(valor_requerido.upper() in n for n in nombres)
    return cumple, "Curso encontrado en capacitaciones" if cumple else "Curso no registrado"


VALIDADORES = {
    "FORMACION": _cumple_formacion,
    "EXPERIENCIA": _cumple_experiencia,
    "CURSO": _cumple_curso,
}


def validar_requisitos(postulante, requisitos: list) -> list[dict]:
    resultado = []
    for req in requisitos:
        validador = VALIDADORES.get(req.tipo.upper())
        if validador:
            cumple, motivo = validador(postulante, req.valor)
        else:
            # Tipos sin validador automatico (ej. LICENCIA, OTRO) quedan pendientes
            # de verificacion manual por RR.HH. - no bloquean la postulacion.
            cumple, motivo = True, "Requiere verificacion manual"
        resultado.append({
            "requirement_id": req.id,
            "tipo": req.tipo,
            "descripcion": req.descripcion,
            "valor_requerido": req.valor,
            "obligatorio": req.obligatorio,
            "cumple": cumple,
            "motivo": motivo,
        })
    return resultado
