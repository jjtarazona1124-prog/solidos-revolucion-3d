# Guía del código (para estudiar y explicar en el video)

El proyecto separa **qué se calcula** (matemática) de **cómo se muestra** (gráficos e interfaz).

```
solidos/calculo.py   → la matemática: integrales exactas y numéricas
solidos/ejemplos.py  → los problemas del informe con su respuesta hecha a mano
solidos/visual.py    → el dibujo 2D y 3D (Plotly)
solidos/geogebra.py  → los comandos que construyen el mismo sólido en GeoGebra
app.py               → la página (Streamlit) que une todo
```

## 1. `calculo.py` — la matemática

1. **`parse_funcion("sqrt(x+1)")`** convierte el texto que escribe el usuario en una expresión de SymPy.
   Solo deja pasar caracteres matemáticos, para que nadie pueda ejecutar código dañino.
2. **`Problema`** guarda los datos: método, `f(x)`, `g(x)`, límites `a` y `b`, y el eje de giro `c`.
3. **`integrando()`** arma lo que va dentro de la integral:
   - Discos: `π·(f(x) − c)²` (el radio es la distancia de la curva al eje).
   - Arandelas: `π·[(f(x) − c)² − (g(x) − c)²]` (radio exterior² − radio interior²).
   - Cascarones: `2π·|x − c|·(f(x) − g(x))` (radio del cascarón × altura; el eje es la recta vertical `x = c`).
   - `_orientar` revisa el signo para que el resultado siempre sea positivo (así no importa cuál función
     escribas primero).
4. **`calcular()`** devuelve tres resultados del mismo volumen:
   - **Exacto**: SymPy integra de forma simbólica (`integrate`) y evalúa en `b` menos en `a`.
   - **Cuadratura**: SciPy (`quad`) aproxima la integral con un método numérico muy preciso.
   - **Riemann**: se parte `[a, b]` en `n` tramos, se evalúa el integrando en el punto medio de cada uno
     y se suman. Es exactamente la idea del marco teórico (suma de discos o arandelas).

## 2. `ejemplos.py`

Cada ejemplo guarda sus datos, el texto del contexto de ingeniería, la solución en LaTeX y el
`valor_analitico` calculado a mano. La pestaña "Desarrollo analítico" de la app compara ese valor con
el del software; si no coinciden, hay un error de planteamiento (casi siempre en el radio o en el eje).

## 3. `visual.py` — el dibujo

- **`figura_2d`**: dibuja `f(x)` y `g(x)`, sombrea la región y marca el eje de giro.
- **`figura_3d`**: gira la curva alrededor del eje. Un punto de altura `h(x)` está a distancia `h(x) − c`
  del eje; al girarlo un ángulo θ queda en `(x, c + (h − c)·cosθ, (h − c)·sinθ)`. Con θ de 0° a 360°
  se genera la superficie.
- **`_seccion_en`**: dibuja el disco (radio `|f − c|`) o la arandela (radios `|g − c|` y `|f − c|`) en una
  posición `x`. El control "número de secciones" dibuja varias, y la "sección resaltada" (verde) se mueve
  con un deslizador.

## 4. `geogebra.py` — el mismo sólido en GeoGebra

`comandos_geogebra(problema)` devuelve la lista de comandos que construyen el sólido:
1. Define `a`, `b`, `c`, `f(x)` (y `g(x)` si hace falta) con los datos del problema.
2. Crea dos deslizadores: `giro` (ángulo de 0 a 2π) y `t` (posición de la sección).
3. Crea el sólido con `Surface(...)`, una superficie paramétrica con la misma fórmula del giro que usa
   `visual.py`: un punto a distancia `h(u) − c` del eje queda en `(u, c + (h − c)·cos v, (h − c)·sin v)`.
4. Crea la sección (disco, arandela o cascarón) en `x = t`.
5. Calcula el volumen con `Integral(...)` para compararlo con el exacto.

`html_applet(comandos)` arma el applet de GeoGebra que ejecuta esos comandos al cargar; la app lo
muestra en la pestaña "GeoGebra". Para usar otra función o límites, basta cambiar `f(x)`, `a` y `b`.

## 5. `app.py` — la página

Streamlit ejecuta el archivo de arriba abajo cada vez que el usuario mueve un control:
1. La barra lateral lee el ejemplo (o los datos personalizados) y los controles de visualización.
2. Llama a `calcular(...)` y muestra los tres resultados con `st.metric`.
3. Muestra cinco pestañas: sólido 3D, región 2D, desarrollo analítico, convergencia (error vs. `n`) y GeoGebra.

## Preguntas que puede hacer el profesor

- **¿Por qué el radio exterior de la arandelas es `2x + 1`?** Porque el eje es `y = −1`: la distancia de
  `y = 2x` al eje es `2x − (−1)`.
- **¿Por qué el valor exacto y el numérico no son idénticos?** El exacto sale de la antiderivada; Riemann
  usa `n` tramos y el error baja al aumentar `n` (pestaña Convergencia).
- **¿Qué hace `c` en las fórmulas?** Desplaza el eje de giro: `c = 0` es el eje X (discos y arandelas) o el eje Y (cascarones).
- **¿Por qué cascarones en el Ejemplo 3?** Por arandelas habría que despejar `x` de `y = x³ + x`, una cúbica sin
  despeje sencillo; por cascarones la integral es de dos términos.

## 6. `tests/` — cómo se comprueba

- `test_calculo.py`: los 3 ejemplos coinciden con su solución analítica (exacto, cuadratura y Riemann), cilindros
  de control, eje desplazado, orientación de arandelas, validaciones y rechazo de entradas peligrosas.
- `test_app.py`: la app arranca sin excepciones y muestra las 3 métricas; el modo personalizado también carga.
- `test_geogebra.py`: los comandos generados contienen los deslizadores y la superficie del método.

Ejecutar: `python -m pytest -q`. Levantar la app: `streamlit run app.py` (abre <http://localhost:8501>).
