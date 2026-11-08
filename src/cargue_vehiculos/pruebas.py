"""Pruebas con assert para el cargue de vehiculos."""

import random
from collections.abc import Callable

from datos import generar_lotes
from estrategia import Lote, cargar_vehiculo, llenar_tabla
from exhaustivo import cargar_exhaustivo
from regla_actual import cargar_por_densidad, cargar_por_vencimiento


SEMILLA = 2026

INSTANCIAS_PEQUENAS = 30

INSTANCIAS_REPRESENTATIVAS = 10

Solucion = Callable[[list[Lote], int], tuple[int, list[int]]]

SOLUCIONES: list[Solucion] = [
    cargar_vehiculo,
    cargar_exhaustivo,
    cargar_por_vencimiento,
    cargar_por_densidad,
]

# Ejemplo resuelto a mano en el README y contraejemplo de las dos reglas.
EJEMPLO: list[Lote] = [
    (600, 600, 1),
    (500, 700, 2),
    (400, 600, 3),
    (300, 480, 4),
    (200, 220, 5),
]

CAPACIDAD_EJEMPLO = 1000

# Tabla calculada a mano: columnas w = 0, 100, ..., 1000 kg.
TABLA_A_MANO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 600, 600, 600, 600, 600],
    [0, 0, 0, 0, 0, 700, 700, 700, 700, 700, 700],
    [0, 0, 0, 0, 600, 700, 700, 700, 700, 1300, 1300],
    [0, 0, 0, 480, 600, 700, 700, 1080, 1180, 1300, 1300],
    [0, 0, 220, 480, 600, 700, 820, 1080, 1180, 1300, 1400],
]


def verificar_carga(
    lotes: list[Lote], capacidad_kg: int, valor: int, elegidos: list[int]
) -> None:
    """Revisa la restriccion del negocio sobre una carga.

    Ningun vehiculo supera su capacidad, ningun lote se fracciona (cada
    indice aparece una sola vez, completo) y el valor devuelto es la
    suma de los valores de los lotes cargados.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.
        valor: valor nutricional que devolvio la solucion.
        elegidos: indices de los lotes que devolvio la solucion.
    """
    assert elegidos == sorted(set(elegidos)), elegidos
    assert all(0 <= i < len(lotes) for i in elegidos), elegidos
    assert sum(lotes[i][0] for i in elegidos) <= capacidad_kg, elegidos
    assert sum(lotes[i][1] for i in elegidos) == valor, (valor, elegidos)


def verificar_instancia(
    lotes: list[Lote], capacidad_kg: int
) -> tuple[bool, bool]:
    """Compara las cuatro soluciones sobre una misma instancia.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.

    Returns:
        Una tupla que indica si la regla por vencimiento y la regla por
        densidad, en ese orden, quedaron por debajo del optimo.
    """
    copia = list(lotes)
    optimo, elegidos = cargar_vehiculo(lotes, capacidad_kg)
    verificar_carga(lotes, capacidad_kg, optimo, elegidos)

    exacto, elegidos_exacto = cargar_exhaustivo(lotes, capacidad_kg)
    verificar_carga(lotes, capacidad_kg, exacto, elegidos_exacto)
    assert optimo == exacto, (lotes, capacidad_kg)

    fallas = []
    for regla in (cargar_por_vencimiento, cargar_por_densidad):
        valor, cargados = regla(lotes, capacidad_kg)
        verificar_carga(lotes, capacidad_kg, valor, cargados)
        assert valor <= optimo, (regla.__name__, lotes, capacidad_kg)
        fallas.append(valor < optimo)

    verificar_vencimiento(lotes, capacidad_kg)
    verificar_densidad(lotes, capacidad_kg)
    assert lotes == copia
    return fallas[0], fallas[1]


def verificar_vencimiento(lotes: list[Lote], capacidad_kg: int) -> None:
    """Revisa que la regla actual cargue un prefijo del orden por vencimiento.

    Los lotes cargados deben ser los primeros k del orden por dias para
    vencer (estable), y el siguiente, si existe, no debe caber.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.
    """
    _, cargados = cargar_por_vencimiento(lotes, capacidad_kg)
    orden = sorted(range(len(lotes)), key=lambda i: lotes[i][2])
    k = len(cargados)
    assert sorted(orden[:k]) == cargados, cargados

    if k < len(lotes):
        libre = capacidad_kg - sum(lotes[i][0] for i in cargados)
        assert lotes[orden[k]][0] > libre, (lotes, capacidad_kg)


def verificar_densidad(lotes: list[Lote], capacidad_kg: int) -> None:
    """Revisa que la regla por densidad no deje un lote que aun cabia.

    Como la capacidad libre solo baja, todo lote que la regla dejo por
    fuera debe pesar mas de lo que quedo libre al final.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.
    """
    _, cargados = cargar_por_densidad(lotes, capacidad_kg)
    libre = capacidad_kg - sum(lotes[i][0] for i in cargados)
    for i in range(len(lotes)):
        if i not in cargados:
            assert lotes[i][0] > libre, (lotes, capacidad_kg, i)


def todas_dan(lotes: list[Lote], capacidad_kg: int) -> set[tuple]:
    """Devuelve los resultados distintos de las cuatro soluciones.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.

    Returns:
        Conjunto con cada pareja (valor, indices) devuelta, con los
        indices como tupla.
    """
    resultados = set()
    for solucion in SOLUCIONES:
        valor, elegidos = solucion(lotes, capacidad_kg)
        resultados.add((valor, tuple(elegidos)))
    return resultados


# Casos limite: sin lotes, capacidad 0, un solo lote y nada que quepa.
assert todas_dan([], 1000) == {(0, ())}
assert todas_dan(EJEMPLO, 0) == {(0, ())}
assert todas_dan([(300, 450, 2)], 1000) == {(450, (0,))}
assert todas_dan([(1200, 900, 1)], 1000) == {(0, ())}
assert todas_dan([(1100, 500, 1), (1500, 900, 2), (2000, 1200, 3)], 1000) == {
    (0, ())
}

# Todo cabe y llenado exacto: las cuatro soluciones cargan todo.
assert todas_dan([(200, 300, 3), (300, 500, 1), (400, 450, 2)], 1000) == {
    (1250, (0, 1, 2))
}
assert todas_dan([(400, 500, 2), (600, 700, 1)], 1000) == {(1200, (0, 1))}

# Solo cabe un lote a la vez: la regla actual se queda con el primero que
# vence y la programacion dinamica con el de mayor valor.
SOLO_UNO: list[Lote] = [(600, 500, 1), (600, 900, 2), (700, 800, 3)]
assert cargar_vehiculo(SOLO_UNO, 1000) == (900, [1])
assert cargar_exhaustivo(SOLO_UNO, 1000) == (900, [1])
assert cargar_por_vencimiento(SOLO_UNO, 1000) == (500, [0])
assert cargar_por_densidad(SOLO_UNO, 1000) == (900, [1])

# Ejemplo a mano: valor, lotes y cada casilla de la tabla.
tabla, celdas = llenar_tabla(EJEMPLO, CAPACIDAD_EJEMPLO)
assert celdas == len(EJEMPLO) * (CAPACIDAD_EJEMPLO + 1)
for i, fila in enumerate(TABLA_A_MANO):
    for columna, esperado in enumerate(fila):
        assert tabla[i][columna * 100] == esperado, (i, columna)
    for w in range(CAPACIDAD_EJEMPLO + 1):
        assert tabla[i][w] == tabla[i][w // 100 * 100], (i, w)

assert cargar_vehiculo(EJEMPLO, CAPACIDAD_EJEMPLO) == (1400, [1, 3, 4])
assert cargar_exhaustivo(EJEMPLO, CAPACIDAD_EJEMPLO) == (1400, [1, 3, 4])

# Contraejemplo: las dos reglas voraces dan menos que el optimo.
assert cargar_por_vencimiento(EJEMPLO, CAPACIDAD_EJEMPLO) == (600, [0])
assert cargar_por_densidad(EJEMPLO, CAPACIDAD_EJEMPLO) == (1300, [2, 3, 4])
assert verificar_instancia(EJEMPLO, CAPACIDAD_EJEMPLO) == (True, True)

generador = random.Random(SEMILLA)
fallas_vencimiento = 0
fallas_densidad = 0

# Instancias pequenas con pesos y valores al azar.
for _ in range(INSTANCIAS_PEQUENAS):
    n = generador.randint(0, 12)
    lotes = [
        (
            generador.randint(1, 20),
            generador.randint(1, 50),
            generador.randint(1, 10),
        )
        for _ in range(n)
    ]
    capacidad = generador.randint(0, 60)
    falla_v, falla_d = verificar_instancia(lotes, capacidad)
    fallas_vencimiento += falla_v
    fallas_densidad += falla_d

# Instancias pequenas con la misma estructura que las de la medicion.
for _ in range(INSTANCIAS_REPRESENTATIVAS):
    lotes = generar_lotes(generador.randint(1, 12), generador)
    capacidad = generador.randint(1000, 4000)
    falla_v, falla_d = verificar_instancia(lotes, capacidad)
    fallas_vencimiento += falla_v
    fallas_densidad += falla_d

total = INSTANCIAS_PEQUENAS + INSTANCIAS_REPRESENTATIVAS
print(
    f"Todas las pruebas pasaron ({total} instancias aleatorias con "
    f"semilla {SEMILLA})."
)
print(
    f"La regla por vencimiento quedo por debajo del optimo en "
    f"{fallas_vencimiento} de {total} instancias y la regla por densidad "
    f"en {fallas_densidad} de {total}."
)
