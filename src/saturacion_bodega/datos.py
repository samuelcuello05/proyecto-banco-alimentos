"""Generador de series sinteticas para el analisis de saturacion.

Cada valor es el cambio neto del inventario de una categoria en una hora
de operacion, en kilogramos: lo que entro menos lo que salio o se
descarto (puede ser negativo). La serie imita tres efectos: en las
primeras horas del dia se recibe mas de lo que se despacha, en las
ultimas se despacha mas, y a lo largo del anio hay una temporada de
cosecha con mas donaciones.
"""

import math
import random


HORAS_POR_DIA = 12

DIAS_POR_ANIO = 300

TENDENCIA_HORARIA_KG = 60

AMPLITUD_TEMPORADA_KG = 40

DESVIACION_KG = 150


def generar_serie(n: int, generador: random.Random) -> list[int]:
    """Genera n cambios netos horarios del inventario de una categoria.

    Args:
        n: cantidad de horas de la serie.
        generador: generador pseudoaleatorio con semilla fija, para que
            las mediciones sean reproducibles.

    Returns:
        Una lista de n enteros (kilogramos por hora), positivos o
        negativos.
    """
    serie = []
    for hora in range(n):
        hora_del_dia = hora % HORAS_POR_DIA
        dia_del_anio = (hora // HORAS_POR_DIA) % DIAS_POR_ANIO

        if hora_del_dia < HORAS_POR_DIA // 2:
            tendencia = TENDENCIA_HORARIA_KG
        else:
            tendencia = -TENDENCIA_HORARIA_KG

        angulo = 2 * math.pi * dia_del_anio / DIAS_POR_ANIO
        temporada = AMPLITUD_TEMPORADA_KG * math.sin(angulo)
        ruido = generador.gauss(0, DESVIACION_KG)
        serie.append(round(tendencia + temporada + ruido))

    return serie
