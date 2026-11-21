"""Tramo de mayor crecimiento del inventario con el algoritmo de Kadane.

Es una programacion dinamica de un solo recorrido: M[j], la mejor suma
de un tramo que termina exactamente en la hora j, cumple
M[j] = max(serie[j], M[j - 1] + serie[j]). Solo se guarda M[j - 1].
"""

from regla_actual import Tramo


def tramo_kadane_contando(serie: list[int]) -> tuple[int, int, int, int]:
    """Recorre la serie una vez y cuenta los elementos visitados.

    Si la mejor suma que termina en la hora anterior es negativa,
    arrastrarla solo resta: el tramo vuelve a empezar en la hora actual.
    A igual suma se conserva el primer tramo encontrado.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        La suma maxima, el inicio y el fin del tramo, y el numero de
        elementos visitados.

    Raises:
        ValueError: si la serie esta vacia.
    """
    if not serie:
        raise ValueError("La serie debe tener al menos una hora")

    actual = serie[0]
    inicio_actual = 0
    mejor_suma = actual
    mejor_inicio = 0
    mejor_fin = 0
    visitados = 1

    for j in range(1, len(serie)):
        if actual < 0:
            actual = serie[j]
            inicio_actual = j
        else:
            actual += serie[j]

        if actual > mejor_suma:
            mejor_suma = actual
            mejor_inicio = inicio_actual
            mejor_fin = j
        visitados += 1

    return mejor_suma, mejor_inicio, mejor_fin, visitados


def tramo_kadane(serie: list[int]) -> Tramo:
    """Encuentra el tramo de horas con mayor crecimiento en un recorrido.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        Una tupla (suma_kg, inicio, fin) del tramo de mayor suma.

    Raises:
        ValueError: si la serie esta vacia.
    """
    suma, inicio, fin, _ = tramo_kadane_contando(serie)
    return suma, inicio, fin
