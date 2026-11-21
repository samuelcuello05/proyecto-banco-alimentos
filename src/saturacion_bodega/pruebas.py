"""Pruebas con assert para el analisis de saturacion de la bodega."""

import random
from collections.abc import Callable

from datos import generar_serie
from divide_y_venceras import (
    suma_cruzada,
    tramo_divide_y_venceras,
    tramo_maximo_contando,
)
from kadane import tramo_kadane
from regla_actual import Tramo, tramo_fuerza_bruta


SEMILLA = 2026

SERIES_PEQUENAS = 30

SERIES_REPRESENTATIVAS = 10

Estrategia = Callable[[list[int]], Tramo]

ESTRATEGIAS: list[Estrategia] = [
    tramo_fuerza_bruta,
    tramo_divide_y_venceras,
    tramo_kadane,
]

# Ejemplo resuelto a mano en el README: ocho horas de una categoria.
EJEMPLO = [-120, 340, -60, 250, -400, 180, 260, -90]


def verificar_serie(serie: list[int]) -> None:
    """Compara las tres estrategias sobre una misma serie.

    Las tres deben dar la misma suma maxima (la restriccion del negocio:
    el tramo reportado es el de mayor crecimiento acumulado), cada tramo
    devuelto debe sumar lo que se reporta y la serie no debe cambiar.

    Args:
        serie: cambio neto del inventario por hora, con al menos un
            elemento.
    """
    copia = list(serie)
    suma_optima = tramo_fuerza_bruta(serie)[0]

    for estrategia in ESTRATEGIAS:
        suma, inicio, fin = estrategia(serie)
        assert suma == suma_optima, (estrategia.__name__, serie)
        assert 0 <= inicio <= fin < len(serie), (estrategia.__name__, serie)
        assert sum(serie[inicio:fin + 1]) == suma, (estrategia.__name__, serie)

    assert serie == copia


# Serie vacia: no hay tramo que reportar.
for estrategia in ESTRATEGIAS:
    try:
        estrategia([])
    except ValueError:
        pass
    else:
        raise AssertionError(f"{estrategia.__name__} acepto una serie vacia")

# Casos limite: un solo elemento, todos negativos y todos positivos.
for estrategia in ESTRATEGIAS:
    assert estrategia([7]) == (7, 0, 0)
    assert estrategia([-7]) == (-7, 0, 0)
    assert estrategia([0]) == (0, 0, 0)
    assert estrategia([-80, -30, -60, -20, -50]) == (-20, 3, 3)
    assert estrategia([40, 10, 70]) == (120, 0, 2)

# Ejemplo a mano: el mejor tramo cruza el centro (horas 1 a 6).
for estrategia in ESTRATEGIAS:
    assert estrategia(EJEMPLO) == (570, 1, 6)
assert tramo_maximo_contando(EJEMPLO, 0, 3)[:3] == (530, 1, 3)
assert tramo_maximo_contando(EJEMPLO, 4, 7)[:3] == (440, 5, 6)
assert suma_cruzada(EJEMPLO, 0, 3, 7) == (570, 1, 6)

# Cruce obligado: aunque ambos lados sean negativos, el tramo cruzado
# toma al menos un elemento de cada mitad.
assert suma_cruzada([-5, -1, -2, -6], 0, 1, 3) == (-3, 1, 2)

generador = random.Random(SEMILLA)

for _ in range(SERIES_PEQUENAS):
    n = generador.randint(1, 80)
    verificar_serie([generador.randint(-500, 500) for _ in range(n)])

for _ in range(SERIES_REPRESENTATIVAS):
    verificar_serie(generar_serie(generador.randint(1, 600), generador))

total = SERIES_PEQUENAS + SERIES_REPRESENTATIVAS
print(
    f"Todas las pruebas pasaron ({total} series aleatorias con semilla "
    f"{SEMILLA})."
)
