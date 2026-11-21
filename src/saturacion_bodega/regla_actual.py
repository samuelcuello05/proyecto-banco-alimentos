"""Procedimiento actual: evaluar todos los tramos de horas posibles.

Tramo = tuple[int, int, int]: (suma_kg, inicio, fin), con inicio y fin
inclusivos. Se toma la interpretacion mas favorable al programa actual:
la suma de cada tramo se acumula a partir de la del tramo anterior, en
lugar de recalcularla desde cero.
"""

Tramo = tuple[int, int, int]  # (suma_kg, inicio, fin)


def tramo_fuerza_bruta_contando(serie: list[int]) -> tuple[int, int, int, int]:
    """Prueba todos los pares (i, j) y cuenta los tramos evaluados.

    Para cada inicio i, el ciclo interno extiende el tramo hasta j
    sumando un solo elemento, asi que cada tramo cuesta Theta(1) y hay
    n (n + 1) / 2 tramos. A igual suma se conserva el primero encontrado
    (menor inicio y, a igual inicio, menor fin).

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        La suma maxima, el inicio y el fin del tramo, y el numero de
        tramos evaluados.

    Raises:
        ValueError: si la serie esta vacia.
    """
    if not serie:
        raise ValueError("La serie debe tener al menos una hora")

    n = len(serie)
    mejor_suma = serie[0]
    mejor_inicio = 0
    mejor_fin = 0
    evaluados = 0

    for i in range(n):
        suma = 0
        for j in range(i, n):
            suma += serie[j]
            if suma > mejor_suma:
                mejor_suma = suma
                mejor_inicio = i
                mejor_fin = j
        evaluados += n - i

    return mejor_suma, mejor_inicio, mejor_fin, evaluados


def tramo_fuerza_bruta(serie: list[int]) -> Tramo:
    """Encuentra el tramo de horas con mayor crecimiento del inventario.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        Una tupla (suma_kg, inicio, fin) del tramo de mayor suma.

    Raises:
        ValueError: si la serie esta vacia.
    """
    suma, inicio, fin, _ = tramo_fuerza_bruta_contando(serie)
    return suma, inicio, fin
