"""Medicion del tramo de saturacion: fuerza bruta, DyV y Kadane."""

import math
import random
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt

from datos import generar_serie
from divide_y_venceras import (
    tramo_divide_y_venceras,
    tramo_divide_y_venceras_contando,
)
from kadane import tramo_kadane, tramo_kadane_contando
from regla_actual import (
    Tramo,
    tramo_fuerza_bruta,
    tramo_fuerza_bruta_contando,
)


SEMILLA = 2026

TAMANOS = [1125, 2250, 4500, 9000, 18000, 36000, 72000]

TAMANO_MAXIMO_FUERZA_BRUTA = 36000

TAMANO_REAL = 36000

CATEGORIAS = 40

REPETICIONES = 3

POTENCIA_KW = 0.150

EJECUCIONES_POR_ANIO = 12

FUERZA_BRUTA = "Fuerza bruta (actual)"

DIVIDE_Y_VENCERAS = "Divide y vencerás"

KADANE = "Kadane"

CARPETA_GRAFICAS = (
    Path(__file__).resolve().parents[2] / "graficas" / "saturacion_bodega"
)

Estrategia = Callable[[list[int]], Tramo]

ESTRATEGIAS: dict[str, Estrategia] = {
    FUERZA_BRUTA: tramo_fuerza_bruta,
    DIVIDE_Y_VENCERAS: tramo_divide_y_venceras,
    KADANE: tramo_kadane,
}

CONTADORAS: dict[str, Callable[[list[int]], tuple[int, int, int, int]]] = {
    FUERZA_BRUTA: tramo_fuerza_bruta_contando,
    DIVIDE_Y_VENCERAS: tramo_divide_y_venceras_contando,
    KADANE: tramo_kadane_contando,
}

COLORES = {
    FUERZA_BRUTA: "tab:red",
    DIVIDE_Y_VENCERAS: "tab:blue",
    KADANE: "tab:green",
}


def cronometrar(estrategia: Estrategia, serie: list[int]) -> float:
    """Mide una estrategia REPETICIONES veces y devuelve la mediana.

    Solo se cronometra la llamada, nunca la generacion de la serie.

    Args:
        estrategia: funcion que encuentra el tramo maximo.
        serie: cambio neto del inventario por hora.

    Returns:
        La mediana de los tiempos, en segundos.
    """
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        estrategia(serie)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos)


def tamanos_de(nombre: str) -> list[int]:
    """Devuelve los tamanos en que se mide una estrategia.

    Args:
        nombre: nombre de la estrategia.

    Returns:
        Todos los TAMANOS, salvo para la fuerza bruta, que se detiene en
        TAMANO_MAXIMO_FUERZA_BRUTA.
    """
    if nombre == FUERZA_BRUTA:
        return [n for n in TAMANOS if n <= TAMANO_MAXIMO_FUERZA_BRUTA]
    return list(TAMANOS)


def medir() -> tuple[dict[str, list[float]], dict[str, list[int]]]:
    """Mide las tres estrategias con la misma serie en cada tamano.

    En cada tamano se verifica que las estrategias den la misma suma
    maxima antes de cronometrar.

    Returns:
        Una tupla con los tiempos (s) y las operaciones contadas por
        estrategia, en el orden de tamanos_de(nombre).

    Raises:
        ValueError: si dos estrategias dan sumas distintas.
    """
    generador = random.Random(SEMILLA)
    tiempos: dict[str, list[float]] = {nombre: [] for nombre in ESTRATEGIAS}
    operaciones: dict[str, list[int]] = {nombre: [] for nombre in ESTRATEGIAS}

    print("Tramo de mayor crecimiento: tiempo por serie (una categoria)")
    print(
        f"{'n':>6} | {'F. bruta (s)':>12} | {'DyV (ms)':>9} | "
        f"{'Kadane (ms)':>11} | {'Suma max (kg)':>13} | "
        f"{'Ops F. bruta':>12} | {'Ops DyV':>9} | {'Ops Kadane':>10}"
    )

    for n in TAMANOS:
        serie = generar_serie(n, generador)
        sumas = set()
        fila = {}

        for nombre, contadora in CONTADORAS.items():
            if n not in tamanos_de(nombre):
                continue
            suma, _, _, contadas = contadora(serie)
            sumas.add(suma)
            operaciones[nombre].append(contadas)
            tiempos[nombre].append(cronometrar(ESTRATEGIAS[nombre], serie))
            fila[nombre] = (tiempos[nombre][-1], contadas)

        if len(sumas) != 1:
            raise ValueError(f"Las estrategias no coinciden con n = {n}")

        bruta = fila.get(FUERZA_BRUTA)
        texto_bruta = f"{bruta[0]:>12.3f}" if bruta else f"{'-':>12}"
        ops_bruta = f"{bruta[1]:>12}" if bruta else f"{'-':>12}"
        print(
            f"{n:>6} | {texto_bruta} | "
            f"{fila[DIVIDE_Y_VENCERAS][0] * 1e3:>9.2f} | "
            f"{fila[KADANE][0] * 1e3:>11.3f} | {sumas.pop():>13} | "
            f"{ops_bruta} | {fila[DIVIDE_Y_VENCERAS][1]:>9} | "
            f"{fila[KADANE][1]:>10}"
        )

    return tiempos, operaciones


def pendiente_log_log(x: list[float], y: list[float]) -> float:
    """Calcula la pendiente de la recta que mejor ajusta log(y) vs. log(x).

    Args:
        x: valores del eje horizontal, todos positivos.
        y: valores del eje vertical, todos positivos.

    Returns:
        La pendiente del ajuste por minimos cuadrados (1 = lineal,
        2 = cuadratico).
    """
    logaritmos_x = [math.log10(valor) for valor in x]
    logaritmos_y = [math.log10(valor) for valor in y]
    return statistics.linear_regression(logaritmos_x, logaritmos_y).slope


def imprimir_analisis(
    tiempos: dict[str, list[float]], operaciones: dict[str, list[int]]
) -> None:
    """Imprime factores, pendientes, escala real y energia.

    Args:
        tiempos: tiempos medidos por estrategia.
        operaciones: operaciones contadas por estrategia.
    """
    print("\nFactor al duplicar n (tiempo / operaciones)")
    for nombre in ESTRATEGIAS:
        tamanos = tamanos_de(nombre)
        factores = []
        for i in range(1, len(tamanos)):
            factor_t = tiempos[nombre][i] / tiempos[nombre][i - 1]
            factor_o = operaciones[nombre][i] / operaciones[nombre][i - 1]
            factores.append(f"x{factor_t:.2f}/x{factor_o:.2f}")
        print(f"{nombre}: {', '.join(factores)}")

    print("\nFactor esperado para n log n al duplicar n:")
    print(
        ", ".join(
            f"x{2 * math.log2(2 * n) / math.log2(n):.2f}"
            for n in TAMANOS[:-1]
        )
    )

    print("\nPendientes log-log del tiempo (1 = lineal, 2 = cuadratico)")
    for nombre in ESTRATEGIAS:
        pendiente = pendiente_log_log(tamanos_de(nombre), tiempos[nombre])
        print(f"{nombre}: {pendiente:.3f}")

    indice_real = TAMANOS.index(TAMANO_REAL)
    print(
        f"\nVolumen real: {CATEGORIAS} categorias x {TAMANO_REAL} horas "
        f"(medido directamente con n = {TAMANO_REAL})"
    )
    energias = {}
    for nombre in ESTRATEGIAS:
        segundos = tiempos[nombre][indice_real] * CATEGORIAS
        kwh = POTENCIA_KW * segundos / 3600
        energias[nombre] = kwh * EJECUCIONES_POR_ANIO
        print(
            f"{nombre}: {segundos:.2f} s por ejecucion "
            f"({segundos / 60:.2f} min) -> {kwh:.3e} kWh por ejecucion -> "
            f"{energias[nombre]:.3e} kWh/anio ({EJECUCIONES_POR_ANIO} "
            f"ejecuciones)"
        )
    print(
        f"Ahorro anual frente a la fuerza bruta: Kadane "
        f"{energias[FUERZA_BRUTA] - energias[KADANE]:.3e} kWh, divide y "
        f"venceras {energias[FUERZA_BRUTA] - energias[DIVIDE_Y_VENCERAS]:.3e}"
        f" kWh"
    )

    tramos_reales = operaciones[FUERZA_BRUTA][indice_real]
    segundos_por_tramo = tiempos[FUERZA_BRUTA][indice_real] / tramos_reales
    sumas_cubicas = TAMANO_REAL * (TAMANO_REAL + 1) * (TAMANO_REAL + 2) / 6
    dias_cubica = sumas_cubicas * segundos_por_tramo * CATEGORIAS / 86400
    print(
        f"\nCosto medido por tramo evaluado: {segundos_por_tramo * 1e9:.1f} "
        f"ns. Si el programa recalculara cada suma desde cero (Theta(n^3), "
        f"{sumas_cubicas:.2e} sumas por categoria), tardaria unos "
        f"{dias_cubica:.0f} dias para las {CATEGORIAS} categorias"
    )

    indice_crecimiento = TAMANOS.index(2 * TAMANO_REAL)
    for nombre in (DIVIDE_Y_VENCERAS, KADANE):
        segundos = tiempos[nombre][indice_crecimiento] * CATEGORIAS
        print(
            f"Crecimiento (n = {2 * TAMANO_REAL}): {nombre} "
            f"{segundos:.2f} s para {CATEGORIAS} categorias"
        )
    factor_bruta = (2 * TAMANO_REAL / TAMANO_REAL) ** 2
    segundos = tiempos[FUERZA_BRUTA][indice_real] * CATEGORIAS * factor_bruta
    print(
        f"Crecimiento (n = {2 * TAMANO_REAL}): fuerza bruta estimada "
        f"{segundos / 60:.1f} min (x{factor_bruta:.0f} por ser cuadratica)"
    )


def graficar(
    valores: dict[str, list],
    archivo: str,
    titulo: str,
    etiqueta_y: str,
    etiquetas: dict[str, str],
) -> None:
    """Grafica una magnitud contra n en escala lineal y log-log.

    Args:
        valores: tiempos u operaciones por estrategia.
        archivo: nombre del PNG dentro de CARPETA_GRAFICAS.
        titulo: titulo general de la figura.
        etiqueta_y: rotulo del eje vertical, con unidades.
        etiquetas: texto de la leyenda para cada estrategia.
    """
    figura, (lineal, logaritmica) = plt.subplots(1, 2, figsize=(13, 5))

    for eje in (lineal, logaritmica):
        for nombre, datos in valores.items():
            eje.plot(
                tamanos_de(nombre), datos, marker="o",
                label=etiquetas[nombre], color=COLORES[nombre],
            )
        eje.axvline(
            TAMANO_REAL, color="gray", linestyle=":",
            label=f"Volumen real ({TAMANO_REAL} horas)",
        )
        eje.set_xlabel("Horas de la serie n")
        eje.grid(True, which="both", alpha=0.3)

    lineal.set_title("Escala lineal")
    lineal.set_ylabel(etiqueta_y)
    logaritmica.set_xscale("log")
    logaritmica.set_yscale("log")
    logaritmica.set_title("Escala log-log")
    logaritmica.set_xlabel("Horas de la serie n (escala log)")
    logaritmica.set_ylabel(f"{etiqueta_y} (escala log)")

    manijas, textos = lineal.get_legend_handles_labels()
    figura.legend(manijas, textos, loc="lower center", ncol=4)
    figura.suptitle(titulo)
    figura.tight_layout(rect=(0, 0.07, 1, 1))
    figura.savefig(CARPETA_GRAFICAS / archivo, dpi=150)
    plt.close(figura)


if __name__ == "__main__":
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)

    tiempos_medidos, operaciones_contadas = medir()
    imprimir_analisis(tiempos_medidos, operaciones_contadas)

    graficar(
        tiempos_medidos,
        "tiempo_vs_n.png",
        "Saturación de la bodega: tiempo por categoría vs. horas de la serie",
        "Tiempo por serie (s)",
        {nombre: nombre for nombre in ESTRATEGIAS},
    )
    graficar(
        operaciones_contadas,
        "operaciones_vs_n.png",
        "Saturación de la bodega: operaciones contadas vs. horas de la serie",
        "Operaciones elementales",
        {
            FUERZA_BRUTA: "Fuerza bruta (tramos evaluados)",
            DIVIDE_Y_VENCERAS: "Divide y vencerás (elementos recorridos)",
            KADANE: "Kadane (elementos visitados)",
        },
    )

    print(f"\nGraficas guardadas en {CARPETA_GRAFICAS}")
