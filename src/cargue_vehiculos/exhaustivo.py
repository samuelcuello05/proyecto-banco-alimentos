"""Cargue de un vehiculo probando todos los subconjuntos de lotes."""

from itertools import product

from estrategia import Lote


def cargar_exhaustivo_contando(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Prueba los 2^n subconjuntos y cuenta los lotes revisados.

    Cada fila de interruptores que entrega product es un subconjunto:
    interruptores[i] == 1 significa que el lote i sube al vehiculo. Por
    cada subconjunto se revisan los n lotes, asi que se cuentan n
    operaciones por subconjunto. Ante un empate se conserva el primer
    subconjunto encontrado.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional maximo, los indices de los lotes cargados
        y el numero de lotes revisados.
    """
    n = len(lotes)
    mejor_valor = 0
    mejores: tuple[int, ...] = (0,) * n
    revisados = 0

    for interruptores in product([0, 1], repeat=n):
        peso = 0
        valor = 0

        for i in range(n):
            if interruptores[i] == 1:
                peso += lotes[i][0]
                valor += lotes[i][1]

        revisados += n

        if peso <= capacidad_kg and valor > mejor_valor:
            mejor_valor = valor
            mejores = interruptores

    elegidos = [i for i in range(n) if mejores[i] == 1]
    return mejor_valor, elegidos, revisados


def cargar_exhaustivo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Calcula el mismo resultado probando todos los subconjuntos de lotes.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional maximo y los indices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_exhaustivo_contando(lotes, capacidad_kg)
    return valor, elegidos
