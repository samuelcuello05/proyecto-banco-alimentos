"""Cargue de un vehiculo del banco de alimentos por programacion dinamica.

Es una mochila 0/1: cada lote sube completo o no sube. La tabla
K[i][w] guarda el mayor valor nutricional que se logra eligiendo solo
entre los i primeros lotes con un vehiculo de w kilogramos.
"""

Lote = tuple[int, int, int]  # (peso_kg, valor_nutricional, dias_para_vencer)


def llenar_tabla(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[list[list[int]], int]:
    """Llena la tabla de la mochila 0/1 fila por fila.

    La fila i corresponde al lote lotes[i - 1], porque la fila 0 es el
    caso base (ningun lote considerado). Cada celda compara dos opciones:
    no llevar el lote, K[i - 1][w], o llevarlo si cabe,
    valor + K[i - 1][w - peso]. Ante un empate se queda sin el lote.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        Una tupla con la tabla de (n + 1) filas y (capacidad_kg + 1)
        columnas y el numero de celdas calculadas fuera del caso base.
    """
    n = len(lotes)
    tabla = [[0] * (capacidad_kg + 1) for _ in range(n + 1)]
    celdas = 0

    for i in range(1, n + 1):
        peso, valor, _ = lotes[i - 1]
        anterior = tabla[i - 1]
        actual = tabla[i]

        for w in range(capacidad_kg + 1):
            no_llevar = anterior[w]
            actual[w] = no_llevar

            if peso <= w:
                llevar = valor + anterior[w - peso]
                if llevar > no_llevar:
                    actual[w] = llevar

        celdas += capacidad_kg + 1

    return tabla, celdas


def reconstruir_lotes(
    lotes: list[Lote], tabla: list[list[int]], capacidad_kg: int
) -> list[int]:
    """Recupera los lotes de una carga optima recorriendo la tabla.

    Se parte de la esquina inferior derecha y se sube una fila por lote.
    Si K[i][w] es distinto de K[i - 1][w], el lote i cambio el resultado,
    asi que se cargo y la capacidad libre baja lo que pesa.

    Args:
        lotes: los mismos lotes con que se lleno la tabla.
        tabla: tabla devuelta por llenar_tabla.
        capacidad_kg: capacidad con que se lleno la tabla.

    Returns:
        Los indices de los lotes cargados, en orden creciente.
    """
    elegidos: list[int] = []
    w = capacidad_kg

    for i in range(len(lotes), 0, -1):
        if tabla[i][w] != tabla[i - 1][w]:
            elegidos.append(i - 1)
            w -= lotes[i - 1][0]

    elegidos.reverse()
    return elegidos


def cargar_vehiculo_contando(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int], int]:
    """Resuelve el cargue y ademas informa cuantas celdas calculo.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional maximo, los indices de los lotes cargados
        y el numero de celdas calculadas.
    """
    tabla, celdas = llenar_tabla(lotes, capacidad_kg)
    elegidos = reconstruir_lotes(lotes, tabla, capacidad_kg)
    return tabla[len(lotes)][capacidad_kg], elegidos, celdas


def cargar_vehiculo(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[int, list[int]]:
    """Elige los lotes de mayor valor nutricional que caben en el vehiculo.

    Args:
        lotes: lotes candidatos de la ruta; no se fraccionan.
        capacidad_kg: capacidad maxima del vehiculo en kilogramos.

    Returns:
        El valor nutricional maximo y los indices de los lotes cargados.
    """
    valor, elegidos, _ = cargar_vehiculo_contando(lotes, capacidad_kg)
    return valor, elegidos
