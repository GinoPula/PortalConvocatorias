"""Calculo deterministico de experiencia laboral total y por sector, a partir de las
fechas de inicio/fin registradas por el postulante. Se calcula en Python (no con IA)
por la misma razon que en el sistema PSRP anterior: la aritmetica de fechas debe ser
exacta y auditable, no una estimacion de un modelo de lenguaje."""
from datetime import date


def _dias_periodo(inicio: date | None, fin: date | None) -> int:
    if not inicio:
        return 0
    fin_real = fin or date.today()
    if fin_real < inicio:
        return 0
    return (fin_real - inicio).days


def calcular_experiencia(experiencias: list) -> dict:
    """experiencias: lista de WorkExperience (o similar con .sector/.fecha_inicio/.fecha_fin)."""
    dias_total = 0
    dias_publico = 0
    dias_privado = 0

    for exp in experiencias:
        dias = _dias_periodo(exp.fecha_inicio, exp.fecha_fin)
        dias_total += dias
        if (exp.sector or "").upper() == "PUBLICO":
            dias_publico += dias
        elif (exp.sector or "").upper() == "PRIVADO":
            dias_privado += dias

    anios = dias_total // 365
    resto = dias_total % 365
    meses = resto // 30
    dias = resto % 30

    return {
        "total_meses": round(dias_total / 30.44),
        "anios": anios,
        "meses": meses,
        "dias": dias,
        "meses_sector_publico": round(dias_publico / 30.44),
        "meses_sector_privado": round(dias_privado / 30.44),
    }
