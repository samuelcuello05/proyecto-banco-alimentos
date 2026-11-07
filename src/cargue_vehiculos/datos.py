"""Generador de lotes y rutas sinteticas para el cargue de vehiculos.

Los lotes imitan la estructura que describe el caso: peso entero en
kilogramos, valor nutricional = raciones ponderadas por la prioridad de
la categoria, y dias para vencer. Hay dos tipos de lote: cajas sueltas
(livianas) y lotes grandes de una o varias estibas (pesados). La
proporcion y el peso de los lotes grandes se calibraron para que la
regla actual (cargar por vencimiento hasta que el siguiente lote no
cabe) llene en promedio cerca del 78 % del vehiculo, como reporta el
banco.
"""

import random

from estrategia import Lote


PRIORIDADES = {"proteina": 3, "frutas y verduras": 2, "otros": 1}

PROBABILIDAD_CATEGORIA = {
    "proteina": 0.25,
    "frutas y verduras": 0.35,
    "otros": 0.40,
}

PROBABILIDAD_LOTE_GRANDE = 0.60

PESO_CAJA_KG = (10, 150)

PESO_LOTE_GRANDE_KG = (500, 2000)

RACIONES_POR_KG = (1.0, 3.0)

DIAS_PARA_VENCER = (1, 20)

LOTES_POR_RUTA = (300, 600)

CAPACIDAD_KG = (2500, 4000)


def generar_lote(generador: random.Random) -> Lote:
    """Genera un lote candidato con datos plausibles.

    Args:
        generador: generador pseudoaleatorio con semilla fija.

    Returns:
        Una tupla (peso_kg, valor_nutricional, dias_para_vencer).
    """
    if generador.random() < PROBABILIDAD_LOTE_GRANDE:
        peso = generador.randint(*PESO_LOTE_GRANDE_KG)
    else:
        peso = generador.randint(*PESO_CAJA_KG)

    categoria = generador.choices(
        list(PROBABILIDAD_CATEGORIA),
        weights=list(PROBABILIDAD_CATEGORIA.values()),
    )[0]
    raciones = round(peso * generador.uniform(*RACIONES_POR_KG))
    valor = raciones * PRIORIDADES[categoria]
    dias = generador.randint(*DIAS_PARA_VENCER)
    return peso, valor, dias


def generar_lotes(n: int, generador: random.Random) -> list[Lote]:
    """Genera n lotes candidatos.

    Args:
        n: cantidad de lotes.
        generador: generador pseudoaleatorio con semilla fija, para que
            las mediciones sean reproducibles.

    Returns:
        Una lista con n lotes (peso_kg, valor_nutricional,
        dias_para_vencer).
    """
    return [generar_lote(generador) for _ in range(n)]


def generar_ruta(generador: random.Random) -> tuple[list[Lote], int]:
    """Genera una ruta con el volumen real que informa el caso.

    Args:
        generador: generador pseudoaleatorio con semilla fija.

    Returns:
        Una tupla con los lotes candidatos de la ruta (entre 300 y 600)
        y la capacidad del vehiculo en kilogramos (entre 2.500 y 4.000).
    """
    n = generador.randint(*LOTES_POR_RUTA)
    capacidad = generador.randint(*CAPACIDAD_KG)
    return generar_lotes(n, generador), capacidad
