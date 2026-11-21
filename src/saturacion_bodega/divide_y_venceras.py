"""Tramo de mayor crecimiento del inventario por divide y venceras.

Se trabaja solo con indices: la serie nunca se copia ni se modifica.
"""

from regla_actual import Tramo


def suma_cruzada(
    serie: list[int], inicio: int, medio: int, fin: int
) -> Tramo:
    """Encuentra el mejor tramo que cruza el punto medio.

    El tramo incluye siempre serie[medio] y serie[medio + 1]: se extiende
    hacia la izquierda desde medio y hacia la derecha desde medio + 1,
    guardando la mejor suma de cada lado.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.
        inicio: primer indice del rango (inclusive).
        medio: ultimo indice de la mitad izquierda.
        fin: ultimo indice del rango (inclusive).

    Returns:
        Una tupla (suma_kg, inicio, fin) del mejor tramo cruzado.
    """
    mejor_izquierda = serie[medio]
    indice_izquierda = medio
    suma = 0
    for i in range(medio, inicio - 1, -1):
        suma += serie[i]
        if suma > mejor_izquierda:
            mejor_izquierda = suma
            indice_izquierda = i

    mejor_derecha = serie[medio + 1]
    indice_derecha = medio + 1
    suma = 0
    for j in range(medio + 1, fin + 1):
        suma += serie[j]
        if suma > mejor_derecha:
            mejor_derecha = suma
            indice_derecha = j

    return mejor_izquierda + mejor_derecha, indice_izquierda, indice_derecha


def tramo_maximo_contando(
    serie: list[int], inicio: int, fin: int
) -> tuple[int, int, int, int]:
    """Resuelve el rango inicio..fin y cuenta los elementos recorridos.

    Divide el rango en dos mitades, resuelve cada una recursivamente,
    calcula el mejor tramo que cruza el centro y devuelve el mejor de los
    tres. A igual suma prefiere la mitad izquierda, luego la derecha y
    por ultimo el tramo cruzado.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.
        inicio: primer indice del rango (inclusive).
        fin: ultimo indice del rango (inclusive).

    Returns:
        La suma maxima, el inicio y el fin del tramo, y el numero de
        elementos recorridos (los de cada suma cruzada mas uno por cada
        caso base).
    """
    if inicio == fin:
        return serie[inicio], inicio, fin, 1

    medio = (inicio + fin) // 2
    resultado_izquierda = tramo_maximo_contando(serie, inicio, medio)
    resultado_derecha = tramo_maximo_contando(serie, medio + 1, fin)
    izquierda = resultado_izquierda[:3]
    derecha = resultado_derecha[:3]
    cruzado = suma_cruzada(serie, inicio, medio, fin)

    recorridos = resultado_izquierda[3] + resultado_derecha[3]
    recorridos += fin - inicio + 1

    if izquierda[0] >= derecha[0] and izquierda[0] >= cruzado[0]:
        mejor = izquierda
    elif derecha[0] >= cruzado[0]:
        mejor = derecha
    else:
        mejor = cruzado

    suma, mejor_inicio, mejor_fin = mejor
    return suma, mejor_inicio, mejor_fin, recorridos


def tramo_divide_y_venceras_contando(
    serie: list[int],
) -> tuple[int, int, int, int]:
    """Aplica divide y venceras a toda la serie y cuenta los recorridos.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        La suma maxima, el inicio y el fin del tramo, y el numero de
        elementos recorridos.

    Raises:
        ValueError: si la serie esta vacia.
    """
    if not serie:
        raise ValueError("La serie debe tener al menos una hora")
    return tramo_maximo_contando(serie, 0, len(serie) - 1)


def tramo_divide_y_venceras(serie: list[int]) -> Tramo:
    """Encuentra el tramo de horas con mayor crecimiento por divide y venceras.

    Args:
        serie: cambio neto del inventario por hora, en kilogramos.

    Returns:
        Una tupla (suma_kg, inicio, fin) del tramo de mayor suma.

    Raises:
        ValueError: si la serie esta vacia.
    """
    suma, inicio, fin, _ = tramo_divide_y_venceras_contando(serie)
    return suma, inicio, fin
