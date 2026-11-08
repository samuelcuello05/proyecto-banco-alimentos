"""Medicion del cargue de vehiculos: PD, exhaustiva y reglas voraces."""

import math
import random
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt

from datos import generar_lotes, generar_ruta
from estrategia import Lote, cargar_vehiculo, cargar_vehiculo_contando
from exhaustivo import cargar_exhaustivo, cargar_exhaustivo_contando
from regla_actual import cargar_por_densidad, cargar_por_vencimiento


SEMILLA = 2026

CAPACIDAD_FIJA_KG = 3000

TAMANOS_EXHAUSTIVO = [4, 6, 8, 10, 12, 14, 16, 18, 20]

TAMANOS_GRANDES = [40, 80, 160, 320, 640, 1280, 2560]

N_FIJO = 200

CAPACIDADES_KG = [250, 500, 1000, 2000, 4000, 8000, 16000]

INSTANCIAS = 3

REPETICIONES = 5

REPETICIONES_EXHAUSTIVO = 3

REPETICIONES_REAL = 3

VEHICULOS = 14

DIAS_SIMULADOS = 5

LOTES_REALES = (300, 600)

CAPACIDAD_MAXIMA_KG = 4000

POTENCIA_KW = 0.150

VENTANA_S = 2 * 3600

DIAS_POR_ANIO = 300

SEGUNDOS_POR_ANIO = 365.25 * 24 * 3600

EDAD_UNIVERSO_ANIOS = 13.8e9

PD = "Programación dinámica"

EXHAUSTIVA = "Exhaustiva"

VENCIMIENTO = "Regla actual (vencimiento)"

DENSIDAD = "Voraz por densidad"

CARPETA_GRAFICAS = (
    Path(__file__).resolve().parents[2] / "graficas" / "cargue_vehiculos"
)

Solucion = Callable[[list[Lote], int], tuple[int, list[int]]]

SOLUCIONES_RAPIDAS: dict[str, Solucion] = {
    PD: cargar_vehiculo,
    VENCIMIENTO: cargar_por_vencimiento,
    DENSIDAD: cargar_por_densidad,
}

COLORES = {
    PD: "tab:blue",
    EXHAUSTIVA: "tab:red",
    VENCIMIENTO: "tab:orange",
    DENSIDAD: "tab:green",
}


def cronometrar(
    solucion: Solucion, lotes: list[Lote], capacidad_kg: int, repeticiones: int
) -> float:
    """Mide una solucion sobre una instancia y devuelve la mediana.

    Solo se cronometra la llamada a la solucion, nunca la generacion de
    los datos.

    Args:
        solucion: funcion de cargue a medir.
        lotes: lotes candidatos de la instancia.
        capacidad_kg: capacidad del vehiculo en kilogramos.
        repeticiones: cuantas veces se ejecuta la solucion.

    Returns:
        La mediana de los tiempos, en segundos.
    """
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        solucion(lotes, capacidad_kg)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos)


def medir_instancias(
    soluciones: dict[str, Solucion],
    instancias: list[tuple[list[Lote], int]],
    repeticiones: dict[str, int],
) -> dict[str, float]:
    """Mide varias soluciones sobre las mismas instancias.

    Args:
        soluciones: funciones a medir, por nombre.
        instancias: parejas (lotes, capacidad) compartidas por todas.
        repeticiones: repeticiones por instancia para cada solucion.

    Returns:
        El tiempo medio por instancia (media de las medianas), en
        segundos, para cada solucion.
    """
    medias = {}
    for nombre, solucion in soluciones.items():
        tiempos = [
            cronometrar(solucion, lotes, capacidad, repeticiones[nombre])
            for lotes, capacidad in instancias
        ]
        medias[nombre] = statistics.mean(tiempos)
    return medias


def verificar_pd_exhaustiva(lotes: list[Lote], capacidad_kg: int) -> None:
    """Comprueba que la PD y la exhaustiva den el mismo valor.

    Args:
        lotes: lotes candidatos de la instancia.
        capacidad_kg: capacidad del vehiculo en kilogramos.

    Raises:
        ValueError: si los valores no coinciden.
    """
    valor_pd, _ = cargar_vehiculo(lotes, capacidad_kg)
    valor_exhaustivo, _ = cargar_exhaustivo(lotes, capacidad_kg)
    if valor_pd != valor_exhaustivo:
        raise ValueError(f"PD {valor_pd} != exhaustiva {valor_exhaustivo}")


def experimento_n_pequeno() -> tuple[dict[str, list[float]], dict[str, list]]:
    """Mide las cuatro soluciones con n pequeno y W fija (experimento 1).

    Returns:
        Una tupla con los tiempos medios (s) por solucion y las
        operaciones contadas (celdas de la PD y lotes revisados por la
        exhaustiva), en el orden de TAMANOS_EXHAUSTIVO.
    """
    generador = random.Random(SEMILLA)
    soluciones = dict(SOLUCIONES_RAPIDAS)
    soluciones[EXHAUSTIVA] = cargar_exhaustivo
    repeticiones = {nombre: REPETICIONES for nombre in soluciones}
    repeticiones[EXHAUSTIVA] = REPETICIONES_EXHAUSTIVO
    tiempos: dict[str, list[float]] = {nombre: [] for nombre in soluciones}
    operaciones: dict[str, list] = {PD: [], EXHAUSTIVA: []}

    print(f"Experimento 1: n pequeno, W = {CAPACIDAD_FIJA_KG} kg")
    print(
        f"{'n':>3} | {'PD (ms)':>9} | {'Exhaust. (ms)':>13} | "
        f"{'Venc. (ms)':>10} | {'Dens. (ms)':>10} | {'Celdas PD':>9} | "
        f"{'Revisados exh.':>14}"
    )

    for n in TAMANOS_EXHAUSTIVO:
        instancias = [
            (generar_lotes(n, generador), CAPACIDAD_FIJA_KG)
            for _ in range(INSTANCIAS)
        ]
        for lotes, capacidad in instancias:
            verificar_pd_exhaustiva(lotes, capacidad)

        medias = medir_instancias(soluciones, instancias, repeticiones)
        for nombre, media in medias.items():
            tiempos[nombre].append(media)

        lotes, capacidad = instancias[0]
        operaciones[PD].append(cargar_vehiculo_contando(lotes, capacidad)[2])
        operaciones[EXHAUSTIVA].append(
            cargar_exhaustivo_contando(lotes, capacidad)[2]
        )

        print(
            f"{n:>3} | {medias[PD] * 1e3:>9.3f} | "
            f"{medias[EXHAUSTIVA] * 1e3:>13.3f} | "
            f"{medias[VENCIMIENTO] * 1e3:>10.4f} | "
            f"{medias[DENSIDAD] * 1e3:>10.4f} | "
            f"{operaciones[PD][-1]:>9} | {operaciones[EXHAUSTIVA][-1]:>14}"
        )

    return tiempos, operaciones


def experimento_n_grande() -> tuple[dict[str, list[float]], list[int]]:
    """Mide la PD y las reglas con n grande y W fija (experimento 2).

    Returns:
        Una tupla con los tiempos medios (s) por solucion y las celdas
        calculadas por la PD, en el orden de TAMANOS_GRANDES.
    """
    generador = random.Random(SEMILLA + 1)
    repeticiones = {nombre: REPETICIONES for nombre in SOLUCIONES_RAPIDAS}
    tiempos: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    celdas: list[int] = []

    print(f"\nExperimento 2: n grande, W = {CAPACIDAD_FIJA_KG} kg")
    print(
        f"{'n':>5} | {'PD (ms)':>9} | {'Venc. (ms)':>10} | "
        f"{'Dens. (ms)':>10} | {'Celdas PD':>10} | {'ns/celda':>8}"
    )

    for n in TAMANOS_GRANDES:
        instancias = [
            (generar_lotes(n, generador), CAPACIDAD_FIJA_KG)
            for _ in range(INSTANCIAS)
        ]
        medias = medir_instancias(SOLUCIONES_RAPIDAS, instancias, repeticiones)
        for nombre, media in medias.items():
            tiempos[nombre].append(media)

        lotes, capacidad = instancias[0]
        celdas.append(cargar_vehiculo_contando(lotes, capacidad)[2])

        print(
            f"{n:>5} | {medias[PD] * 1e3:>9.2f} | "
            f"{medias[VENCIMIENTO] * 1e3:>10.4f} | "
            f"{medias[DENSIDAD] * 1e3:>10.4f} | {celdas[-1]:>10} | "
            f"{medias[PD] / celdas[-1] * 1e9:>8.1f}"
        )

    return tiempos, celdas


def experimento_capacidad() -> tuple[dict[str, list[float]], list[int]]:
    """Mide la PD y las reglas con n fijo y W creciente (experimento 3).

    En cada capacidad se usan exactamente los mismos N_FIJO lotes.

    Returns:
        Una tupla con los tiempos medios (s) por solucion y las celdas
        calculadas por la PD, en el orden de CAPACIDADES_KG.
    """
    generador = random.Random(SEMILLA + 2)
    lotes_base = [generar_lotes(N_FIJO, generador) for _ in range(INSTANCIAS)]
    repeticiones = {nombre: REPETICIONES for nombre in SOLUCIONES_RAPIDAS}
    tiempos: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    celdas: list[int] = []

    print(f"\nExperimento 3: n = {N_FIJO} lotes, W creciente")
    print(
        f"{'W (kg)':>6} | {'PD (ms)':>9} | {'Venc. (ms)':>10} | "
        f"{'Dens. (ms)':>10} | {'Celdas PD':>9} | {'ns/celda':>8}"
    )

    for capacidad in CAPACIDADES_KG:
        instancias = [(lotes, capacidad) for lotes in lotes_base]
        medias = medir_instancias(SOLUCIONES_RAPIDAS, instancias, repeticiones)
        for nombre, media in medias.items():
            tiempos[nombre].append(media)

        celdas.append(cargar_vehiculo_contando(lotes_base[0], capacidad)[2])

        print(
            f"{capacidad:>6} | {medias[PD] * 1e3:>9.2f} | "
            f"{medias[VENCIMIENTO] * 1e3:>10.4f} | "
            f"{medias[DENSIDAD] * 1e3:>10.4f} | {celdas[-1]:>9} | "
            f"{medias[PD] / celdas[-1] * 1e9:>8.1f}"
        )

    return tiempos, celdas


def porcentaje_llenado(
    lotes: list[Lote], capacidad_kg: int, elegidos: list[int]
) -> float:
    """Calcula que porcentaje de la capacidad ocupa una carga.

    Args:
        lotes: lotes candidatos de la ruta.
        capacidad_kg: capacidad del vehiculo en kilogramos.
        elegidos: indices de los lotes cargados.

    Returns:
        El peso cargado como porcentaje de la capacidad.
    """
    return 100 * sum(lotes[i][0] for i in elegidos) / capacidad_kg


def experimento_volumen_real() -> dict[str, dict[str, float]]:
    """Simula DIAS_SIMULADOS dias de planeacion con VEHICULOS rutas reales.

    Cada ruta tiene entre 300 y 600 lotes y un vehiculo de 2.500 a 4.000
    kg, como informa el caso. Se mide el tiempo de cada dia completo y la
    calidad de cada regla frente al optimo de la PD.

    Returns:
        Por solucion: tiempo medio y maximo por dia (s), llenado medio
        (%) y valor medio como porcentaje del optimo. Para la PD incluye
        ademas las celdas medias por dia y los kg cargados por dia.
    """
    generador = random.Random(SEMILLA + 3)
    tiempos_dia: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    llenados: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    valores: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    kg_dia: dict[str, list[float]] = {
        nombre: [] for nombre in SOLUCIONES_RAPIDAS
    }
    celdas_dia: list[int] = []
    rutas_con_perdida_densidad = 0

    for _ in range(DIAS_SIMULADOS):
        rutas = [generar_ruta(generador) for _ in range(VEHICULOS)]
        celdas_dia.append(
            sum(len(lotes) * (capacidad + 1) for lotes, capacidad in rutas)
        )

        for nombre, solucion in SOLUCIONES_RAPIDAS.items():
            tiempo = 0.0
            for lotes, capacidad in rutas:
                tiempo += cronometrar(
                    solucion, lotes, capacidad, REPETICIONES_REAL
                )
            tiempos_dia[nombre].append(tiempo)

        kg = {nombre: 0.0 for nombre in SOLUCIONES_RAPIDAS}
        for lotes, capacidad in rutas:
            optimo, _ = cargar_vehiculo(lotes, capacidad)
            for nombre, solucion in SOLUCIONES_RAPIDAS.items():
                valor, elegidos = solucion(lotes, capacidad)
                llenado = porcentaje_llenado(lotes, capacidad, elegidos)
                llenados[nombre].append(llenado)
                valores[nombre].append(100 * valor / optimo)
                kg[nombre] += llenado * capacidad / 100
                if nombre == DENSIDAD and valor < optimo:
                    rutas_con_perdida_densidad += 1
        for nombre, total in kg.items():
            kg_dia[nombre].append(total)

    resumen = {}
    print(
        f"\nExperimento 4: volumen real ({VEHICULOS} rutas por dia, "
        f"{DIAS_SIMULADOS} dias)"
    )
    print(
        f"{'Solucion':<28} | {'t medio/dia (s)':>15} | "
        f"{'t max/dia (s)':>13} | {'Llenado (%)':>11} | "
        f"{'Valor/optimo (%)':>16} | {'kg/dia':>8}"
    )
    for nombre in SOLUCIONES_RAPIDAS:
        resumen[nombre] = {
            "tiempo_medio": statistics.mean(tiempos_dia[nombre]),
            "tiempo_maximo": max(tiempos_dia[nombre]),
            "llenado": statistics.mean(llenados[nombre]),
            "llenado_minimo": min(llenados[nombre]),
            "valor": statistics.mean(valores[nombre]),
            "valor_minimo": min(valores[nombre]),
            "kg_dia": statistics.mean(kg_dia[nombre]),
        }
        print(
            f"{nombre:<28} | {resumen[nombre]['tiempo_medio']:>15.4f} | "
            f"{resumen[nombre]['tiempo_maximo']:>13.4f} | "
            f"{resumen[nombre]['llenado']:>11.2f} | "
            f"{resumen[nombre]['valor']:>16.2f} | "
            f"{resumen[nombre]['kg_dia']:>8.0f}"
        )

    resumen[PD]["celdas_dia"] = statistics.mean(celdas_dia)
    print(
        f"Llenado minimo de una ruta: vencimiento "
        f"{resumen[VENCIMIENTO]['llenado_minimo']:.1f} %, densidad "
        f"{resumen[DENSIDAD]['llenado_minimo']:.1f} %, PD "
        f"{resumen[PD]['llenado_minimo']:.1f} %"
    )
    print(
        f"Peor ruta en valor: vencimiento "
        f"{resumen[VENCIMIENTO]['valor_minimo']:.1f} % del optimo, "
        f"densidad {resumen[DENSIDAD]['valor_minimo']:.2f} %"
    )
    print(
        f"La regla por densidad no llego al optimo en "
        f"{rutas_con_perdida_densidad} de {VEHICULOS * DIAS_SIMULADOS} rutas"
    )
    return resumen


def pendiente_log_log(x: list[float], y: list[float]) -> float:
    """Calcula la pendiente de la recta que mejor ajusta log(y) vs. log(x).

    Args:
        x: valores del eje horizontal, todos positivos.
        y: valores del eje vertical, todos positivos.

    Returns:
        La pendiente del ajuste por minimos cuadrados (1 = lineal).
    """
    logaritmos_x = [math.log10(valor) for valor in x]
    logaritmos_y = [math.log10(valor) for valor in y]
    return statistics.linear_regression(logaritmos_x, logaritmos_y).slope


def imprimir_factores(
    titulo: str, tamanos: list[int], tiempos: dict[str, list[float]]
) -> None:
    """Imprime cuanto se multiplica el tiempo en cada pareja n -> 2n.

    Args:
        titulo: encabezado del bloque.
        tamanos: tamanos medidos.
        tiempos: tiempos medios por solucion, en el orden de tamanos.
    """
    print(f"\n{titulo}")
    for i, tamano in enumerate(tamanos):
        if 2 * tamano in tamanos:
            j = tamanos.index(2 * tamano)
            factores = ", ".join(
                f"{nombre} x{valores[j] / valores[i]:.2f}"
                for nombre, valores in tiempos.items()
            )
            print(f"{tamano:>6} -> {2 * tamano:>6}: {factores}")


def imprimir_analisis(
    pequeno: dict[str, list[float]],
    operaciones: dict[str, list],
    grande: dict[str, list[float]],
    celdas_grande: list[int],
    capacidad: dict[str, list[float]],
    celdas_capacidad: list[int],
    real: dict[str, dict[str, float]],
) -> None:
    """Imprime factores, pendientes, extrapolacion y energia.

    Args:
        pequeno: tiempos del experimento 1.
        operaciones: operaciones del experimento 1.
        grande: tiempos del experimento 2.
        celdas_grande: celdas de la PD en el experimento 2.
        capacidad: tiempos del experimento 3.
        celdas_capacidad: celdas de la PD en el experimento 3.
        real: resumen del experimento 4.
    """
    imprimir_factores(
        "Factor al duplicar n (experimento 1)", TAMANOS_EXHAUSTIVO, pequeno
    )
    print("Factor de la exhaustiva por cada 2 lotes mas:")
    exhaustiva = pequeno[EXHAUSTIVA]
    print(
        ", ".join(
            f"{TAMANOS_EXHAUSTIVO[i]}->{TAMANOS_EXHAUSTIVO[i + 1]} "
            f"x{exhaustiva[i + 1] / exhaustiva[i]:.2f}"
            for i in range(len(exhaustiva) - 1)
        )
    )
    imprimir_factores(
        "Factor al duplicar n (experimento 2)", TAMANOS_GRANDES, grande
    )
    imprimir_factores(
        "Factor al duplicar W (experimento 3)", CAPACIDADES_KG, capacidad
    )
    imprimir_factores(
        "Factor de las operaciones al duplicar n (experimento 1)",
        TAMANOS_EXHAUSTIVO,
        {
            nombre: [float(v) for v in valores]
            for nombre, valores in operaciones.items()
        },
    )

    print("\nPendientes log-log (1 = lineal)")
    for nombre, valores in grande.items():
        print(
            f"{nombre} vs n: {pendiente_log_log(TAMANOS_GRANDES, valores):.3f}"
        )
    for nombre, valores in capacidad.items():
        print(
            f"{nombre} vs W: {pendiente_log_log(CAPACIDADES_KG, valores):.3f}"
        )
    ajuste_w = statistics.linear_regression(
        CAPACIDADES_KG, [t * 1e3 for t in capacidad[PD]]
    )
    print(
        f"Ajuste lineal PD vs W (n = {N_FIJO}): {ajuste_w.intercept:.2f} ms "
        f"+ {ajuste_w.slope * 1000:.2f} ms por cada 1000 kg"
    )
    pendiente_exhaustiva = statistics.linear_regression(
        TAMANOS_EXHAUSTIVO, [math.log2(t) for t in exhaustiva]
    ).slope
    print(
        f"Exhaustiva: log2(tiempo) crece {pendiente_exhaustiva:.3f} por lote "
        f"(x{2 ** pendiente_exhaustiva:.2f} por lote)"
    )

    ns_celda = [
        t / c * 1e9 for t, c in zip(grande[PD][3:], celdas_grande[3:])
    ] + [
        t / c * 1e9 for t, c in zip(capacidad[PD][2:], celdas_capacidad[2:])
    ]
    ns_min = min(ns_celda)
    ns_max = max(ns_celda)
    print(
        f"\nCosto por celda de la PD (n >= {TAMANOS_GRANDES[3]} y "
        f"W >= {CAPACIDADES_KG[2]}): {ns_min:.1f} a {ns_max:.1f} ns"
    )

    celdas_peor = VEHICULOS * LOTES_REALES[1] * (CAPACIDAD_MAXIMA_KG + 1)
    print(
        f"\nExtrapolacion PD, peor dia ({VEHICULOS} x {LOTES_REALES[1]} lotes "
        f"x {CAPACIDAD_MAXIMA_KG + 1} columnas = {celdas_peor} celdas): "
        f"{celdas_peor * ns_min / 1e9:.2f} a "
        f"{celdas_peor * ns_max / 1e9:.2f} s"
    )
    celdas_medias = real[PD]["celdas_dia"]
    print(
        f"Prediccion para el dia medio simulado ({celdas_medias:.0f} celdas): "
        f"{celdas_medias * ns_min / 1e9:.2f} a "
        f"{celdas_medias * ns_max / 1e9:.2f} s; medido: "
        f"{real[PD]['tiempo_medio']:.2f} s"
    )

    segundos_por_revision = exhaustiva[-1] / operaciones[EXHAUSTIVA][-1]
    print(
        f"\nExhaustiva: {segundos_por_revision * 1e9:.1f} ns por lote "
        f"revisado (n = {TAMANOS_EXHAUSTIVO[-1]})"
    )
    for n in LOTES_REALES:
        segundos = n * 2.0 ** n * segundos_por_revision
        anios = segundos / SEGUNDOS_POR_ANIO
        print(
            f"Exhaustiva con n = {n}: {anios:.2e} anios por ruta "
            f"({anios / EDAD_UNIVERSO_ANIOS:.2e} veces la edad del universo)"
        )
    n_ventana = 1
    revisiones = VEHICULOS * (n_ventana + 1) * 2.0 ** (n_ventana + 1)
    while revisiones * segundos_por_revision <= VENTANA_S:
        n_ventana += 1
        revisiones = VEHICULOS * (n_ventana + 1) * 2.0 ** (n_ventana + 1)
    print(
        f"Mayor n que la exhaustiva resuelve para {VEHICULOS} rutas en la "
        f"ventana de 2 h: {n_ventana} lotes por ruta"
    )

    print(f"\nEnergia (potencia {POTENCIA_KW} kW, {DIAS_POR_ANIO} dias/anio)")
    energias = {}
    for nombre, datos in real.items():
        kwh_dia = POTENCIA_KW * datos["tiempo_medio"] / 3600
        energias[nombre] = kwh_dia * DIAS_POR_ANIO
        print(
            f"{nombre}: {datos['tiempo_medio']:.4f} s/dia "
            f"({100 * datos['tiempo_medio'] / VENTANA_S:.4f} % de la ventana)"
            f" -> {kwh_dia:.3e} kWh/dia -> {energias[nombre]:.3e} kWh/anio"
        )
    kwh_peor = POTENCIA_KW * celdas_peor * ns_max / 1e9 / 3600
    print(
        f"PD en el peor dia: {kwh_peor:.3e} kWh/dia -> "
        f"{kwh_peor * DIAS_POR_ANIO:.3e} kWh/anio"
    )
    print(
        f"Diferencia anual PD - regla actual: "
        f"{energias[PD] - energias[VENCIMIENTO]:.3e} kWh"
    )
    kg_extra = real[PD]["kg_dia"] - real[VENCIMIENTO]["kg_dia"]
    print(
        f"Alimento adicional cargado por la PD: {kg_extra:.0f} kg/dia -> "
        f"{kg_extra * DIAS_POR_ANIO / 1000:.0f} t/anio"
    )


def graficar_tiempo_vs_n(
    pequeno: dict[str, list[float]], grande: dict[str, list[float]]
) -> None:
    """Grafica el tiempo medio contra n en dos paneles.

    Args:
        pequeno: tiempos del experimento 1 (incluye la exhaustiva).
        grande: tiempos del experimento 2 (sin la exhaustiva).
    """
    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(13, 5))

    for nombre, valores in pequeno.items():
        izquierda.plot(
            TAMANOS_EXHAUSTIVO, valores, marker="o", label=nombre,
            color=COLORES[nombre],
        )
    izquierda.set_yscale("log")
    izquierda.set_title(f"n ≤ 20 lotes (W = {CAPACIDAD_FIJA_KG} kg)")
    izquierda.set_xlabel("Número de lotes candidatos n")
    izquierda.set_ylabel("Tiempo medio por instancia (s, escala log)")
    izquierda.set_xticks(TAMANOS_EXHAUSTIVO)

    for nombre, valores in pequeno.items():
        tamanos = list(TAMANOS_EXHAUSTIVO)
        if nombre in grande:
            tamanos += TAMANOS_GRANDES
            valores = valores + grande[nombre]
        derecha.plot(
            tamanos, valores, marker="o", label=nombre, color=COLORES[nombre]
        )
    derecha.set_xscale("log")
    derecha.set_yscale("log")
    derecha.set_title(f"Todos los tamaños (W = {CAPACIDAD_FIJA_KG} kg)")
    derecha.set_xlabel("Número de lotes candidatos n (escala log)")
    derecha.set_ylabel("Tiempo medio por instancia (s, escala log)")

    for eje in (izquierda, derecha):
        eje.grid(True, which="both", alpha=0.3)

    manijas, etiquetas = izquierda.get_legend_handles_labels()
    figura.legend(manijas, etiquetas, loc="lower center", ncol=4)
    figura.suptitle("Cargue de vehículos: tiempo medio vs. número de lotes")
    figura.tight_layout(rect=(0, 0.07, 1, 1))
    figura.savefig(CARPETA_GRAFICAS / "tiempo_vs_n.png", dpi=150)
    plt.close(figura)


def graficar_operaciones_vs_n(
    operaciones: dict[str, list], celdas_grande: list[int]
) -> None:
    """Grafica las operaciones contadas contra n en dos paneles.

    Args:
        operaciones: celdas de la PD y lotes revisados por la exhaustiva
            en el experimento 1.
        celdas_grande: celdas de la PD en el experimento 2.
    """
    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(13, 5))
    etiquetas = {
        PD: "Programación dinámica (celdas calculadas)",
        EXHAUSTIVA: "Exhaustiva (lotes revisados)",
    }

    for nombre, valores in operaciones.items():
        izquierda.plot(
            TAMANOS_EXHAUSTIVO, valores, marker="o", label=etiquetas[nombre],
            color=COLORES[nombre],
        )
    izquierda.set_yscale("log")
    izquierda.set_title(f"n ≤ 20 lotes (W = {CAPACIDAD_FIJA_KG} kg)")
    izquierda.set_xlabel("Número de lotes candidatos n")
    izquierda.set_ylabel("Operaciones elementales (escala log)")
    izquierda.set_xticks(TAMANOS_EXHAUSTIVO)

    derecha.plot(
        TAMANOS_EXHAUSTIVO + TAMANOS_GRANDES,
        operaciones[PD] + celdas_grande,
        marker="o",
        label=etiquetas[PD],
        color=COLORES[PD],
    )
    derecha.plot(
        TAMANOS_EXHAUSTIVO, operaciones[EXHAUSTIVA], marker="o",
        label=etiquetas[EXHAUSTIVA], color=COLORES[EXHAUSTIVA],
    )
    derecha.set_xscale("log")
    derecha.set_yscale("log")
    derecha.set_title(f"Todos los tamaños (W = {CAPACIDAD_FIJA_KG} kg)")
    derecha.set_xlabel("Número de lotes candidatos n (escala log)")
    derecha.set_ylabel("Operaciones elementales (escala log)")

    for eje in (izquierda, derecha):
        eje.grid(True, which="both", alpha=0.3)
        eje.legend()

    figura.suptitle("Cargue de vehículos: operaciones contadas vs. n")
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "operaciones_vs_n.png", dpi=150)
    plt.close(figura)


def graficar_tiempo_vs_capacidad(capacidad: dict[str, list[float]]) -> None:
    """Grafica el tiempo medio contra la capacidad W con n fijo.

    Args:
        capacidad: tiempos del experimento 3 por solucion.
    """
    ajuste = statistics.linear_regression(
        CAPACIDADES_KG, [t * 1e3 for t in capacidad[PD]]
    )
    recta = [ajuste.intercept + ajuste.slope * w for w in CAPACIDADES_KG]

    figura, (izquierda, derecha) = plt.subplots(1, 2, figsize=(13, 5))
    for eje in (izquierda, derecha):
        for nombre, valores in capacidad.items():
            eje.plot(
                CAPACIDADES_KG, [t * 1e3 for t in valores], marker="o",
                label=nombre, color=COLORES[nombre],
            )
        eje.set_xlabel("Capacidad del vehículo W (kg)")
        eje.set_ylabel("Tiempo medio por instancia (ms)")
        eje.grid(True, which="both", alpha=0.3)

    izquierda.plot(
        CAPACIDADES_KG,
        recta,
        linestyle="--",
        color="gray",
        label=(
            f"Ajuste lineal PD: {ajuste.intercept:.2f} ms + "
            f"{ajuste.slope * 1000:.2f} ms por cada 1000 kg"
        ),
    )
    izquierda.set_title("Escala lineal")
    izquierda.legend()
    derecha.set_xscale("log")
    derecha.set_yscale("log")
    derecha.set_title("Escala log-log (las reglas no dependen de W)")
    derecha.set_xlabel("Capacidad del vehículo W (kg, escala log)")
    derecha.set_ylabel("Tiempo medio por instancia (ms, escala log)")
    derecha.legend()

    figura.suptitle(
        f"Cargue con n = {N_FIJO} lotes fijos: tiempo vs. capacidad W"
    )
    figura.tight_layout()
    figura.savefig(CARPETA_GRAFICAS / "tiempo_vs_capacidad.png", dpi=150)
    plt.close(figura)


if __name__ == "__main__":
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)

    tiempos_pequeno, operaciones_pequeno = experimento_n_pequeno()
    tiempos_grande, celdas_n = experimento_n_grande()
    tiempos_capacidad, celdas_w = experimento_capacidad()
    resumen_real = experimento_volumen_real()

    imprimir_analisis(
        tiempos_pequeno,
        operaciones_pequeno,
        tiempos_grande,
        celdas_n,
        tiempos_capacidad,
        celdas_w,
        resumen_real,
    )
    graficar_tiempo_vs_n(tiempos_pequeno, tiempos_grande)
    graficar_operaciones_vs_n(operaciones_pequeno, celdas_n)
    graficar_tiempo_vs_capacidad(tiempos_capacidad)

    print(f"\nGraficas guardadas en {CARPETA_GRAFICAS}")
