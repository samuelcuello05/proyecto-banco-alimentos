"""Reglas voraces de cargue: la actual (vencimiento) y por densidad.

Ninguna de las dos garantiza el maximo valor nutricional. Se usan como
linea base del proceso actual y como segundo contraste.
"""

from estrategia import Lote


def cargar_por_vencimiento(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Reproduce el procedimiento actual: carga por vencimiento.

    Se detiene en el primer lote que ya no cabe.

    El orden es por dias para vencer, de menor a mayor; a igual
    vencimiento se respeta el orden de llegada (indice), porque el
    ordenamiento de Python es estable.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional cargado y los indices de los lotes cargados.
    """
    orden = sorted(range(len(lotes)), key=lambda i: lotes[i][2])
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []

    for i in orden:
        peso, valor_lote, _ = lotes[i]
        if peso > libre:
            break
        elegidos.append(i)
        libre -= peso
        valor += valor_lote

    elegidos.sort()
    return valor, elegidos


def cargar_por_densidad(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Carga por mayor valor por kilogramo; no garantiza el optimo.

    A diferencia de la regla actual, no se detiene en el primer lote que
    no cabe: lo salta y sigue con los de menor densidad. A igual
    densidad va primero el de menor indice.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional cargado y los indices de los lotes cargados.
    """
    orden = sorted(
        range(len(lotes)), key=lambda i: (-lotes[i][1] / lotes[i][0], i)
    )
    libre = capacidad_kg
    valor = 0
    elegidos: list[int] = []

    for i in orden:
        peso, valor_lote, _ = lotes[i]
        if peso <= libre:
            elegidos.append(i)
            libre -= peso
            valor += valor_lote

    elegidos.sort()
    return valor, elegidos
