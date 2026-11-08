# Proyecto final — Caso 3: Banco Regional de Alimentos

**Curso:** Análisis de Algoritmos 190304006-1 — ITM, periodo 2026-2
**Caso asignado:** Caso 3 — Banco Regional de Alimentos
**Integrantes:**

* Samuel Cristobal Cuello Duque
* Daniel Felipe Marin Marin
* Tomas Gonzalez Zapata
* Carolina Arango Escobar

| Entrega | Fecha | Alcance |
| --- | --- | --- |
| Laboratorio 4 (15 %) | Miércoles 18 de noviembre de 2026 | Operación 3 — Cargue de los vehículos (programación dinámica) |
| Proyecto final (20 %) | Lunes 23 de noviembre de 2026 | Operación 4 — Saturación de la bodega, análisis del proceso completo, implicaciones e informe en PDF |

---

# 1. Análisis del problema

## 1.1 Descripción del problema computacional

**Pendiente para la entrega del 23 de noviembre.**

## 1.2 Operaciones críticas del proceso

**Pendiente para la entrega del 23 de noviembre.**

## 1.3 Costo energético del proceso actual (línea base)

**Pendiente para la entrega del 23 de noviembre.**

## 1.4 Operación 3 — Cargue de los vehículos: entradas, salida y restricciones

Para cada ruta hay que escoger qué lotes candidatos suben al vehículo para que el valor nutricional transportado sea el máximo sin superar su capacidad. El tamaño de la entrada es **n**, el número de lotes candidatos; como se verá, el costo depende también de la capacidad **W**.

| Elemento | Descripción |
| --- | --- |
| Entradas | `lotes`: lista de n lotes `(peso_kg, valor_nutricional, dias_para_vencer)`. El peso es un entero en kilogramos; el valor son las raciones del lote ponderadas por la prioridad de su categoría (proteína, frutas y verduras, otros). `capacidad_kg`: capacidad W del vehículo, entera, en kilogramos. |
| Volumen real | 14 vehículos de 2.500 a 4.000 kg; cada ruta tiene entre 300 y 600 lotes candidatos. |
| Salida | El valor nutricional máximo y los índices de los lotes que suben, en orden creciente. |
| Restricciones | (1) Ningún vehículo supera su capacidad. (2) Un lote no se fracciona: sube completo o no sube. (3) El valor cargado es el **máximo**, no una aproximación. (4) Las operaciones 1 a 3 terminan en la ventana de 2 horas (03:00 – 05:00), en un computador de 150 W, sin paralelismo. (5) El registro original de cada lote no se modifica (trazabilidad sanitaria). |
| Estrategia actual | Ordenar por vencimiento y cargar hasta que el siguiente lote ya no cabe. Cuesta Θ(n log n), pero no garantiza el máximo: los vehículos salen, en promedio, al 78 % de su capacidad. |

## 1.5 Operación 4 — Saturación de la bodega: entradas, salida y restricciones

**Pendiente para la entrega del 23 de noviembre.**

## 1.6 Supuestos

### Operación 3

1. **Una ruta por vehículo y por día:** cada día hay 14 instancias independientes, una por vehículo, y los lotes candidatos de una ruta no compiten con los de otra.
2. **Los candidatos ya están vigentes:** el filtro de lotes vencidos (ningún lote vencido se despacha) se aplica antes, en las operaciones 1 y 2. Por eso `dias_para_vencer` ≥ 1.
3. **Datos enteros:** pesos enteros ≥ 1 kg, valores enteros ≥ 0 ya ponderados por la prioridad de la categoría (el banco los calcula) y capacidad entera ≥ 0, todo en kilogramos.
4. **Cómo interpretamos la regla actual:** los lotes se ordenan por `dias_para_vencer`, de menor a mayor, y a igual vencimiento por orden de llegada (su índice). Se cargan en ese orden y la regla **se detiene en el primer lote que no cabe**, aunque detrás haya lotes más livianos que sí cabrían, porque el caso dice "hasta que ya no cabe el siguiente lote". Ejemplo: con 1.000 kg y lotes de 600, 500 y 200 kg en ese orden, carga el de 600, se detiene en el de 500 y no prueba el de 200.
5. **Regla por densidad (segundo contraste):** ordena por valor por kilogramo, de mayor a menor (a igual densidad, por índice). A diferencia de la regla actual, **salta** los lotes que no caben y sigue con los demás. Nunca fracciona un lote.
6. **Desempates:** si llevar o no llevar un lote da el mismo valor, la programación dinámica no lo lleva. Por eso puede devolver un conjunto de lotes distinto al de la solución exhaustiva con el mismo valor. Las pruebas comparan valores y verifican que los lotes de cada solución respeten la capacidad y sumen el valor reportado.
7. **Ventana:** los segundos que use esta operación salen de la misma ventana de 2 horas que necesitan las operaciones 1 y 2.

### Operación 4

**Pendiente para la entrega del 23 de noviembre.**

---

# 2. Diseño de la solución

## 2.1 Estructuras de datos seleccionadas

**Pendiente para la entrega del 23 de noviembre.**

## 2.2 Operación 3: mochila 0/1 por programación dinámica

### Por qué el problema admite programación dinámica

* **La decisión** es lote por lote: ¿sube o no sube? Para escribir la recurrencia se mira siempre el **último** lote del grupo considerado.
* **Subestructura óptima.** Sea una carga óptima con los lotes 1..i y capacidad w. Si incluye el lote i, el resto de la carga debe ser una carga óptima de los lotes 1..i − 1 con capacidad w − pᵢ: si existiera una mejor para esos kilogramos, se cambiaría esa parte y el total subiría, lo que contradice que era óptima (el argumento de "cortar y pegar"). Si no lo incluye, es una carga óptima de los lotes 1..i − 1 con capacidad w.
* **Subproblemas traslapados.** El mismo par (lotes considerados, kilogramos libres) aparece por caminos distintos. En el ejemplo de abajo, K[4][500] se necesita para K[5][500] (si no se lleva L4) y para K[5][700] (si se lleva L4, que pesa 200 kg). Una búsqueda que pruebe los 2ⁿ subconjuntos recalcula esos estados una y otra vez. La tabla solo tiene (n + 1)(W + 1) estados distintos: con 600 lotes y 4.000 kg son 2,4 millones, frente a 2⁶⁰⁰ ≈ 4·10¹⁸⁰ subconjuntos.
* **Por qué no basta una regla voraz:** una regla que elige una vez y no reconsidera (por vencimiento o por densidad) puede dejar un hueco que ningún lote llena. El contraejemplo calculado está en la sección 5.1.

### La recurrencia

**K[i][w]** = el mayor valor nutricional que se logra eligiendo **solo entre los i primeros lotes** con un vehículo de **w kilogramos**. El lote i pesa pᵢ y vale vᵢ.

```text
K[0][w] = 0                                         para todo w (caso base)
K[i][w] = K[i-1][w]                                 si p_i > w  (el lote i no cabe)
K[i][w] = max( K[i-1][w],  v_i + K[i-1][w - p_i] )  si p_i <= w
```

* `K[i-1][w]`: **no subir** el lote i. La capacidad sigue siendo w y quedan los i − 1 lotes anteriores.
* `v_i + K[i-1][w - p_i]`: **subir** el lote i. Se gana vᵢ y quedan w − pᵢ kilogramos para los lotes anteriores. Solo existe si el lote cabe.
* **Caso base:** sin lotes no hay valor (fila 0 en ceros). Con w = 0 tampoco cabe nada, porque todo peso es ≥ 1.
* **Orden de llenado:** cada fila depende solo de la anterior, así que se llena **fila por fila, de arriba hacia abajo** (i = 1, …, n). Dentro de una fila el orden de las columnas no importa.
* **Respuesta:** K[n][W]. Los lotes se recuperan recorriendo la tabla desde esa casilla hacia arriba.

### Ejemplo resuelto a mano

Una camioneta de **1.000 kg** y cinco lotes candidatos (es la misma instancia del contraejemplo de la sección 5.1):

| Lote | Peso (kg) | Valor (raciones ponderadas) | Días para vencer | Valor por kg |
| --- | ---: | ---: | ---: | ---: |
| L0 | 600 | 600 | 1 | 1,00 |
| L1 | 500 | 700 | 2 | 1,40 |
| L2 | 400 | 600 | 3 | 1,50 |
| L3 | 300 | 480 | 4 | 1,60 |
| L4 | 200 | 220 | 5 | 1,10 |

Todos los pesos son múltiplos de 100 kg, así que entre una centena y la siguiente la tabla no cambia (con 650 kg se logra lo mismo que con 600). Por eso basta llenar a mano las columnas 0, 100, …, 1.000. El programa llena las 1.001 columnas y [pruebas.py](src/cargue_vehiculos/pruebas.py) verifica que coincidan con esta tabla.

| i \ w (kg) | 0 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1.000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 (ninguno) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 (+L0) | 0 | 0 | 0 | 0 | 0 | 0 | 600 | 600 | 600 | 600 | 600 |
| 2 (+L1) | 0 | 0 | 0 | 0 | 0 | 700 | 700 | 700 | 700 | 700 | 700 |
| 3 (+L2) | 0 | 0 | 0 | 0 | 600 | 700 | 700 | 700 | 700 | 1.300 | 1.300 |
| 4 (+L3) | 0 | 0 | 0 | 480 | 600 | 700 | 700 | 1.080 | 1.180 | 1.300 | 1.300 |
| 5 (+L4) | 0 | 0 | 220 | 480 | 600 | 700 | 820 | 1.080 | 1.180 | 1.300 | **1.400** |

Cómo se llenan algunas casillas:

* **Fila 2 (L1: 500 kg, 700), w = 1.000:** no subir L1 da K[1][1.000] = 600; subirlo da 700 + K[1][500] = 700 + 0 = 700. Gana 700, porque L0 y L1 juntos pesan 1.100 kg y no caben.
* **Fila 3 (L2: 400 kg, 600), w = 900:** no subirlo da K[2][900] = 700; subirlo da 600 + K[2][500] = 600 + 700 = **1.300** (L1 + L2).
* **Fila 4 (L3: 300 kg, 480), w = 1.000:** no subirlo da K[3][1.000] = 1.300; subirlo da 480 + K[3][700] = 480 + 700 = 1.180. Gana 1.300: con cuatro lotes, lo mejor sigue siendo L1 + L2.

La última fila (L4: 200 kg, valor 220), con las dos opciones de cada casilla:

| w (kg) | (a) No subir L4: K[4][w] | (b) Subir L4: 220 + K[4][w − 200] | K[5][w] |
| ---: | ---: | ---: | ---: |
| 0 – 100 | 0, 0 | no cabe | 0, 0 |
| 200 | 0 | 220 + K[4][0] = 220 | 220 |
| 300 | 480 | 220 + K[4][100] = 220 | 480 |
| 400 | 600 | 220 + K[4][200] = 220 | 600 |
| 500 | 700 | 220 + K[4][300] = 700 | 700 (empate: no lo sube) |
| 600 | 700 | 220 + K[4][400] = 820 | 820 |
| 700 | 1.080 | 220 + K[4][500] = 920 | 1.080 |
| 800 | 1.180 | 220 + K[4][600] = 920 | 1.180 |
| 900 | 1.300 | 220 + K[4][700] = 1.300 | 1.300 (empate: no lo sube) |
| 1.000 | 1.300 | 220 + K[4][800] = **1.400** | **1.400** |

La casilla final muestra por qué hace falta la tabla: subir L4 solo conviene porque K[4][800] = 1.180 ya sabía que L1 y L3 caben juntos en 800 kg.

### Reconstrucción de la carga

Se parte de K[5][1.000] y se sube una fila por lote. Si la casilla cambió respecto a la fila de arriba, el lote se subió y la capacidad baja lo que pesa:

1. Fila 5 (L4), w = 1.000: K[5][1.000] = 1.400 ≠ K[4][1.000] = 1.300, así que **L4 sube**. Quedan 800 kg.
2. Fila 4 (L3), w = 800: K[4][800] = 1.180 ≠ K[3][800] = 700, así que **L3 sube**. Quedan 500 kg.
3. Fila 3 (L2), w = 500: K[3][500] = 700 = K[2][500] = 700, así que L2 no sube.
4. Fila 2 (L1), w = 500: K[2][500] = 700 ≠ K[1][500] = 0, así que **L1 sube**. Quedan 0 kg.
5. Fila 1 (L0), w = 0: K[1][0] = 0 = K[0][0], así que L0 no sube.

**Carga óptima: L1, L3 y L4**, con 500 + 300 + 200 = 1.000 kg (100 % de la capacidad) y un valor de 700 + 480 + 220 = **1.400**. La solución exhaustiva revisa los 2⁵ = 32 subconjuntos y llega al mismo valor.

### Estrategias de contraste

```text
EXHAUSTIVA(lotes, W):                    # la solución exacta para verificar
    mejor ← 0
    para cada x en {0,1}^n:              # 2^n subconjuntos
        peso ← Σ x_i·p_i ; valor ← Σ x_i·v_i      # revisa los n lotes
        si peso ≤ W y valor > mejor: mejor ← valor; guardar x
    devolver mejor y los i con x_i = 1

POR_VENCIMIENTO(lotes, W):               # la regla actual
    ordenar los lotes por días para vencer (a igual fecha, por llegada)
    para cada lote en ese orden:
        si no cabe: DETENERSE
        subirlo

POR_DENSIDAD(lotes, W):                  # la voraz tentadora
    ordenar los lotes por valor/peso, de mayor a menor
    para cada lote en ese orden:
        si cabe: subirlo                 # si no cabe, lo salta y sigue
```

### Cómo reduce el consumo energético

_En desarrollo._

## 2.3 Operación 4: tramo de mayor crecimiento del inventario

**Pendiente para la entrega del 23 de noviembre.**

---

# 3. Implementación

## 3.1 Tecnologías y herramientas

_En desarrollo._

## 3.2 Operación 3 — Cargue de los vehículos

_En desarrollo._

## 3.3 Operación 4 — Saturación de la bodega

**Pendiente para la entrega del 23 de noviembre.**

---

# 4. Evaluación del desempeño

## 4.1 Operación 3 — Cargue de los vehículos

_En desarrollo._

## 4.2 Operación 4 — Saturación de la bodega

**Pendiente para la entrega del 23 de noviembre.**

---

# 5. Análisis comparativo

## 5.1 Operación 3 — Cargue de los vehículos

_En desarrollo._

## 5.2 Operación 4 — Saturación de la bodega

**Pendiente para la entrega del 23 de noviembre.**

## 5.3 Comparación entre las operaciones y solución recomendada

**Pendiente para la entrega del 23 de noviembre.**

---

# 6. Implicaciones éticas, sociales y ambientales

## 6.1 Consumo energético

### Operación 3 — regla actual frente a programación dinámica

_En desarrollo._

### Operación 4 y proceso completo

**Pendiente para la entrega del 23 de noviembre.**

## 6.2 Personas: quién asume el costo cuando el algoritmo se equivoca o llega tarde

**Pendiente para la entrega del 23 de noviembre.**

## 6.3 Marco normativo y buenas prácticas

**Pendiente para la entrega del 23 de noviembre.**

## 6.4 Crecimiento: una segunda bodega con el doble de lotes y de vehículos

**Pendiente para la entrega del 23 de noviembre.**

---

# 7. Conclusiones

**Pendiente para la entrega del 23 de noviembre.**

---

# 8. Reproducción

_En desarrollo._

---

# Referencias

**Pendiente para la entrega del 23 de noviembre.**
