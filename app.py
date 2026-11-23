"""Simulador interactivo de sólidos de revolución (Streamlit + SymPy + Plotly 3D).

Ejecutar:  streamlit run app.py
"""

from __future__ import annotations

import base64
import html

import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import sympy as sp

from solidos.calculo import Problema, calcular, parse_funcion, riemann_punto_medio
from solidos.ejemplos import EJEMPLOS, problema_desde_ejemplo
from solidos.geogebra import comandos_geogebra, html_applet
from solidos.visual import figura_2d, figura_3d, figura_convergencia

st.set_page_config(
    page_title="Sólidos de revolución",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="auto",
)

NOMBRES_METODO = {"discos": "Discos", "arandelas": "Arandelas", "cascarones": "Cascarones"}
ETIQUETA_EJE = {"discos": "y", "arandelas": "y", "cascarones": "x"}
FORMULAS = {
    "discos": "V = π ∫<sub>a</sub><sup>b</sup> [f(x) − c]² dx",
    "arandelas": "V = π ∫<sub>a</sub><sup>b</sup> [R(x)² − r(x)²] dx",
    "cascarones": "V = 2π ∫<sub>a</sub><sup>b</sup> |x − c| · [f(x) − g(x)] dx",
}

# --------------------------------------------------------------------------- #
# Identidad visual: pieza torneada, líneas de taller y papel de plano
# --------------------------------------------------------------------------- #
CSS = """
:root {
  --ink: #16222E; --muted: #5D6C7B; --paper: #F2F4F6; --panel: #FFFFFF;
  --panel-suave: #F8F9FA; --segmento: #E8ECF0;
  --texto-medio: #3E4C59; --texto-suave: #7A8896;
  --line: #DFE5EA; --blue: #1B5E9E; --copper: #B4703F; --verdigris: #2E7D6F;
  --sombra: rgba(16, 25, 34, .08); --resalte: rgba(255, 255, 255, .7);
  color-scheme: light;
}
html, body, .stApp { background: var(--paper); }
.stApp {
  background-image: radial-gradient(900px 420px at 80% -10%, rgba(27, 94, 158, .09), transparent 62%);
  background-attachment: fixed;
  color: var(--ink);
}
html, body, .stApp, [data-testid="stSidebar"] {
  font-family: "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
}
h1, h2, h3, h4 { font-family: "Bahnschrift", "Segoe UI Variable Display", "Segoe UI", sans-serif; letter-spacing: -0.01em; }
.block-container { padding: 2rem 2.4rem 3rem; max-width: 1180px; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none; }
[data-testid="stExpandSidebarButton"] {
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
  padding: 3px 5px; box-shadow: 0 1px 2px var(--sombra);
}
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: transparent; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }

/* Hero */
.hero {
  position: relative; overflow: hidden; border-radius: 18px; border: 1px solid #1E2C38;
  background: linear-gradient(140deg, #17242F 0%, #101922 62%, #0F1A23 100%);
  color: #EDF2F6; padding: 30px 34px; display: grid;
  grid-template-columns: minmax(0, 1fr) 272px; gap: 28px; align-items: center;
}
.hero::before {
  content: ""; position: absolute; left: 0; right: 0; top: 0; height: 6px;
  background: repeating-linear-gradient(90deg, rgba(232, 178, 92, .85) 0 2px, transparent 2px 10px);
  opacity: .55;
}
.hero::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(520px 260px at 90% 6%, rgba(232, 178, 92, .16), transparent 66%);
}
.hero__texto { position: relative; z-index: 1; }
.hero__kicker { margin: 0 0 10px; font-size: 12.5px; color: #9FB0BE; }
.hero h1 { margin: 0 0 10px; font-size: clamp(28px, 3.2vw, 42px); line-height: 1.02; font-weight: 600; color: #F7FAFC; }
.hero__sub { margin: 0 0 16px; max-width: 54ch; font-size: 14.5px; line-height: 1.55; color: #B9C7D3; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  font-size: 12px; color: #DCE6EE; background: rgba(255, 255, 255, .06);
  border: 1px solid rgba(255, 255, 255, .14); padding: 4px 10px; border-radius: 999px; white-space: nowrap;
}
.hero__formula {
  margin: 16px 0 0; padding: 9px 14px; border-left: 2px solid rgba(232, 178, 92, .8);
  border-radius: 4px; background: rgba(255, 255, 255, .045);
  font-family: "Cambria Math", Cambria, Georgia, serif; font-size: 17px; color: #EFE2C6;
}
.hero__pieza {
  position: relative; z-index: 1; justify-self: end; width: 100%; max-width: 272px;
  aspect-ratio: 272 / 200;
  background: url("data:image/svg+xml;base64,__SVG__") center / contain no-repeat;
}

/* Métricas */
[data-testid="stMetric"] {
  position: relative; overflow: hidden; background: var(--panel);
  border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px 14px;
  --tick: var(--blue);
}
[data-testid="stMetric"]::before {
  content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px;
  background: repeating-linear-gradient(90deg, var(--tick) 0 2px, transparent 2px 7px);
}
[data-testid="stColumn"]:nth-of-type(2) [data-testid="stMetric"] { --tick: var(--copper); }
[data-testid="stColumn"]:nth-of-type(3) [data-testid="stMetric"] { --tick: var(--verdigris); }
[data-testid="stMetricLabel"] p { font-size: 12.5px; color: var(--muted); font-weight: 500; }
[data-testid="stMetricValue"] {
  font-family: "Bahnschrift", "Segoe UI Variable Display", "Segoe UI", sans-serif;
  font-size: clamp(24px, 2.6vw, 34px); font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em; color: var(--ink);
}
[data-testid="stMetricDelta"] { font-size: 12px; color: var(--muted) !important; }
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] { height: 100%; }
[data-testid="stColumn"] [data-testid="stElementContainer"]:has([data-testid="stMetric"]) { flex: 1 1 auto; }
[data-testid="stMetric"] { height: 100%; }
[data-testid="stMetric"]::before { border-radius: 14px 14px 0 0; }

/* Pestañas y paneles de gráficas */
[data-testid="stTabs"] [role="tablist"] {
  gap: 4px; padding: 5px; border: 1px solid var(--line); border-radius: 12px;
  background: var(--segmento); overflow-x: auto; flex-wrap: nowrap;
  width: fit-content; max-width: 100%;
}
[data-testid="stTab"] {
  padding: 8px 14px; border-radius: 9px; color: var(--texto-medio); cursor: pointer;
}
[data-testid="stTab"]:hover { background: var(--resalte); color: var(--ink); }
[data-testid="stTab"][aria-selected="true"] {
  background: var(--panel); color: var(--ink); font-weight: 600;
  box-shadow: 0 1px 2px var(--sombra);
}
[data-testid="stTab"] p { font-size: 13.5px; margin: 0; white-space: nowrap; }
[data-testid="stTab"] .react-aria-SelectionIndicator { display: none; }
[data-testid="stTabPanel"] { border: 0; padding-top: .35rem; }
[data-testid="stElementContainer"]:has(.hero) { margin-bottom: 10px; }
[data-testid="stPlotlyChart"] {
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 6px;
}

/* Barra lateral */
[data-testid="stSidebar"] { background: var(--panel-suave); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] > div { min-width: 318px; }
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: 13.5px; }
.rotulo {
  margin: 4px 0 12px; padding-bottom: 7px; border-bottom: 1px solid var(--line);
  font-size: 13px; font-weight: 600; color: var(--ink);
}
.contexto {
  margin: 8px 0 4px; padding: 12px 14px; background: var(--panel);
  border: 1px solid var(--line); border-radius: 12px;
}
.contexto .prog { margin: 0 0 6px; font-size: 11.5px; font-weight: 600; color: var(--copper); }
.contexto p { margin: 0; font-size: 12.8px; line-height: 1.5; color: var(--texto-medio); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { font-size: 12px; color: var(--muted); }

/* Pie */
.pie {
  margin-top: 26px; padding-top: 14px; border-top: 1px solid var(--line);
  display: flex; justify-content: space-between; gap: 14px; font-size: 12px; color: var(--texto-suave);
}

/* Tabla de convergencia */
.tabla-envoltura {
  margin: 2px 0 14px; border: 1px solid var(--line); border-radius: 12px;
  overflow: hidden; background: var(--panel);
}
table.tabla { width: 100%; border-collapse: collapse; font-size: 13px; color: var(--texto-medio); }
table.tabla thead th {
  padding: 9px 14px; background: var(--panel-suave); color: var(--muted);
  font-weight: 600; text-align: right; border-bottom: 1px solid var(--line);
}
table.tabla tbody td {
  padding: 8px 14px; text-align: right; font-variant-numeric: tabular-nums;
  border-top: 1px solid var(--line);
}
table.tabla tbody tr:first-child td { border-top: 0; }
table.tabla thead th:first-child, table.tabla tbody td:first-child { text-align: left; }
table.tabla tbody tr:nth-child(even) { background: rgba(127, 160, 190, .05); }

@media (max-width: 760px) {
  .block-container { padding: 3.4rem 1rem 2rem; }
  .hero { grid-template-columns: 1fr; padding: 22px 20px; }
  .hero__pieza { display: none; }
  .hero h1 { font-size: 30px; }
  .hero__formula { font-size: 15px; }
  .pie { flex-direction: column; gap: 4px; }
}
"""

CSS_OSCURO = """
:root {
  --ink: #E6EDF3; --muted: #93A4B3; --paper: #0B131B; --panel: #131E28;
  --panel-suave: #0F1822; --segmento: #182430; --line: #24323F;
  --texto-medio: #C2CED8; --texto-suave: #8598A8;
  --blue: #57A9E6; --copper: #D9A05B; --verdigris: #5FBFAE;
  --sombra: rgba(0, 0, 0, .45); --resalte: rgba(255, 255, 255, .06);
  color-scheme: dark;
}
.stApp {
  background-image: radial-gradient(900px 420px at 80% -10%, rgba(87, 169, 230, .14), transparent 62%);
}
[data-testid="stWidgetLabel"] p { color: var(--ink); }
[data-testid="stMarkdownContainer"] p { color: var(--texto-medio); }
[data-testid="stCaptionContainer"] p { color: var(--texto-suave); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--texto-medio); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--texto-suave); }
[data-testid="stMetricLabel"] p { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--ink); }
[data-testid="stMetricDelta"] { color: var(--muted) !important; }
[data-testid="stTab"] { color: var(--texto-medio); }
[data-testid="stTab"]:hover { background: var(--resalte); color: var(--ink); }
[data-testid="stTab"][aria-selected="true"] { background: var(--panel); color: var(--ink); }
.contexto { background: var(--panel); border-color: var(--line); }
.contexto p { color: var(--texto-medio); }
.pie { color: var(--texto-suave); }
[data-baseweb="input"], [data-baseweb="input"] > div, [data-baseweb="select"] > div,
[data-baseweb="textarea"], [data-testid="stNumberInput"] button {
  background: var(--panel) !important; border-color: var(--line) !important; color: var(--ink) !important;
}
input, textarea { color: var(--ink) !important; }
[data-baseweb="input"] input { background: transparent !important; }
[data-baseweb="select"] div, [data-baseweb="select"] span { color: var(--ink) !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background: var(--panel) !important; }
[data-baseweb="menu"] li, [data-baseweb="popover"] [role="option"] { background: var(--panel) !important; color: var(--ink) !important; }
[data-baseweb="menu"] li:hover, [data-baseweb="popover"] [role="option"]:hover { background: var(--segmento) !important; }
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--blue) !important; border-color: var(--blue) !important;
}
[data-testid="stAlert"] {
  background: #12222B !important; border: 1px solid #1E3A45 !important; color: var(--ink) !important;
}
[data-testid="stAlert"] p { color: var(--ink) !important; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary {
  background: var(--panel) !important; border-color: var(--line) !important; color: var(--ink) !important;
}
pre, code { background: #0A1219 !important; color: #DCE6EE !important; }
[data-testid="stTooltipContent"] {
  background: var(--panel) !important; border: 1px solid var(--line) !important; color: var(--ink) !important;
}
"""

COMPONENTE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 272 200">
  <line x1="136" y1="10" x2="136" y2="192" stroke="#465C6E" stroke-width="1" stroke-dasharray="2 5"/>
  <g stroke="#465C6E" stroke-width="1" opacity=".7">
    <line x1="129" y1="29" x2="143" y2="29"/>
    <line x1="129" y1="78" x2="143" y2="78"/>
    <line x1="129" y1="127" x2="143" y2="127"/>
    <line x1="129" y1="176" x2="143" y2="176"/>
  </g>
  <path d="M136 22 C 178 40, 196 74, 190 108 C 184 144, 166 174, 136 184"
        fill="none" stroke="#E8B25C" stroke-width="1.8" stroke-linecap="round"/>
  <g fill="none" stroke="#8FA3B4" stroke-width="1">
    <ellipse cx="136" cy="46" rx="20" ry="5.5" opacity=".75"/>
    <ellipse cx="136" cy="82" rx="33" ry="8" opacity=".85"/>
    <ellipse cx="136" cy="152" rx="26" ry="6.5" opacity=".7"/>
  </g>
  <ellipse cx="136" cy="118" rx="30" ry="7.5"
           fill="rgba(127, 195, 174, .22)" stroke="#7FC3AE" stroke-width="1.4"/>
  <circle cx="136" cy="118" r="1.6" fill="#7FC3AE"/>
</svg>
"""

SVG_PIEZA = base64.b64encode(COMPONENTE_SVG.encode("utf-8")).decode("ascii")

st.markdown(f"<style>{CSS.replace('__SVG__', SVG_PIEZA)}</style>", unsafe_allow_html=True)

# ----------------------------- Barra lateral ----------------------------- #
with st.sidebar:
    st.html('<p class="rotulo">Problema</p>')
    modo = st.radio(
        "Modo",
        ["Ejemplos", "Personalizado"],
        horizontal=True,
        label_visibility="collapsed",
    )

problema: Problema | None = None
ejemplo = None
error: str | None = None
metodo_actual = "discos"
programa: str | None = None
eje_actual = 0.0

try:
    if modo == "Ejemplos":
        nombre = st.sidebar.selectbox("Ejemplo", list(EJEMPLOS))
        ejemplo = EJEMPLOS[nombre]
        problema = problema_desde_ejemplo(nombre)
        metodo_actual = ejemplo["metodo"]
        programa = ejemplo["programa"]
        eje_actual = float(ejemplo["eje"])
        st.sidebar.html(
            f'<div class="contexto"><p class="prog">{html.escape(programa)}</p>'
            f"<p>{html.escape(ejemplo['contexto'])}</p></div>"
        )
    else:
        metodo_actual = st.sidebar.selectbox(
            "Método", list(NOMBRES_METODO), format_func=NOMBRES_METODO.get
        )
        f_txt = st.sidebar.text_input("f(x)", "sqrt(x)" if metodo_actual == "discos" else "x**2")
        g_txt = "0"
        if metodo_actual != "discos":
            g_txt = st.sidebar.text_input("g(x)", "x" if metodo_actual == "arandelas" else "0")
        col_a, col_b = st.sidebar.columns(2)
        a = col_a.number_input("a", value=0.0)
        b = col_b.number_input("b", value=4.0 if metodo_actual == "discos" else 1.0)
        etiqueta_eje = "x = c (eje vertical)" if metodo_actual == "cascarones" else "y = c (eje horizontal)"
        eje_actual = st.sidebar.number_input(f"Eje de giro {etiqueta_eje}", value=0.0)
        problema = Problema(
            metodo=metodo_actual,
            f=parse_funcion(f_txt),
            g=parse_funcion(g_txt),
            a=a,
            b=b,
            eje=eje_actual,
        )
        st.sidebar.html(
            '<div class="contexto"><p class="prog">Modo personalizado</p>'
            "<p>Escribe las funciones con <b>^</b> o <b>**</b> para las potencias. "
            "Solo se admite la variable x.</p></div>"
        )
except ValueError as exc:
    error = str(exc)

st.sidebar.html('<p class="rotulo">Visualización</p>')
angulo = st.sidebar.slider("Ángulo de giro (°)", 10, 360, 360, step=10)
n_secciones = st.sidebar.slider("Secciones dibujadas", 0, 40, 6)
resolucion = st.sidebar.slider("Resolución de la malla", 20, 120, 60, step=10)
n_riemann = st.sidebar.slider("Subdivisiones n (Riemann)", 4, 1000, 100)

st.sidebar.html('<p class="rotulo">Apariencia</p>')
st.sidebar.toggle(
    "Interfaz oscura",
    value=False,
    key="tema_oscuro",
    help="Cambia entre papel claro y taller nocturno.",
)

tema = "oscuro" if st.session_state.get("tema_oscuro") else "claro"
if tema == "oscuro":
    st.markdown(f"<style>{CSS_OSCURO}</style>", unsafe_allow_html=True)

# --------------------------------- Hero ---------------------------------- #
eje_para_mostrar = eje_actual
if problema is not None:
    eje_para_mostrar = problema.eje

chips = [NOMBRES_METODO[metodo_actual]]
if ejemplo is not None:
    chips.append(nombre.split("·")[0].strip())
chips.append(f"eje {ETIQUETA_EJE[metodo_actual]} = {eje_para_mostrar:g}")

st.html(
    f"""
    <section class="hero">
      <div class="hero__texto">
        <p class="hero__kicker">Proyecto Integrador de Cálculo Integral (UTS)</p>
        <h1>Sólidos de revolución</h1>
        <p class="hero__sub">El volumen de una pieza torneada, por tres caminos a la vez:
        la antiderivada, la cuadratura numérica y la suma de Riemann.</p>
        <div class="chips">{"".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)}</div>
        <p class="hero__formula">{FORMULAS[metodo_actual]}</p>
      </div>
      <div class="hero__pieza" aria-hidden="true"></div>
    </section>
    """
)

if error or problema is None:
    st.error(error or "Define el problema en la barra lateral.")
    st.stop()

try:
    resultado = calcular(problema, n_riemann=n_riemann)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

pos_corte = st.sidebar.slider(
    "Sección resaltada (x)",
    float(problema.a),
    float(problema.b),
    float((problema.a + problema.b) / 2),
)

# ------------------------------- Métricas -------------------------------- #
c1, c2, c3 = st.columns(3, gap="medium")
if resultado.exacto is not None:
    c1.metric(
        "Volumen exacto",
        f"{resultado.exacto:.6f} u³",
        help="Antiderivada calculada con SymPy y evaluada entre a y b.",
    )
else:
    c1.metric(
        "Volumen exacto",
        "No disponible",
        help="SymPy no encontró una antiderivada cerrada para este integrando.",
    )
c2.metric(
    "Cuadratura numérica",
    f"{resultado.cuadratura:.6f} u³",
    help="Integración adaptativa de SciPy (quad); sirve de referencia numérica.",
)
c3.metric(
    "Suma de Riemann",
    f"{resultado.riemann:.6f} u³",
    help="Regla del punto medio con n subdivisiones de [a, b]. El número de tramos se ajusta en la barra lateral.",
)
if resultado.error_absoluto is not None:
    st.caption(
        f"Suma de Riemann con n = {n_riemann}: se aparta del volumen exacto en "
        f"{resultado.error_absoluto:.1e} u³. Los tres valores deben coincidir."
    )
else:
    st.caption(f"Suma de Riemann con n = {n_riemann}, frente a la cuadratura numérica.")

# -------------------------------- Pestañas ------------------------------- #
tab3d, tab2d, tabcalc, tabconv, tabgg = st.tabs(
    [
        ":material/view_in_ar: Sólido 3D",
        ":material/show_chart: Región 2D",
        ":material/functions: Desarrollo analítico",
        ":material/trending_down: Convergencia",
        ":material/public: GeoGebra",
    ]
)

with tab3d:
    st.caption(
        "Arrastra para rotar y usa la rueda para acercar. En rojo, las secciones que forman el "
        "volumen; en verde, la sección resaltada."
    )
    st.plotly_chart(
        figura_3d(
            problema,
            angulo=angulo,
            resolucion=resolucion,
            n_secciones=n_secciones,
            pos_corte=pos_corte,
            tema=tema,
        ),
        width="stretch",
        config={"displaylogo": False},
    )

with tab2d:
    st.plotly_chart(
        figura_2d(problema, tema=tema),
        width="stretch",
        config={"displaylogo": False},
    )

with tabcalc:
    st.markdown("**Integrando**")
    st.latex(sp.latex(resultado.integrando))
    if resultado.antiderivada is not None:
        st.markdown("**Antiderivada**")
        st.latex(sp.latex(resultado.antiderivada))
        st.markdown("**Evaluación en [a, b]**")
        st.latex(
            r"V=" + sp.latex(resultado.exacto_simbolico)
            + r"\approx " + f"{resultado.exacto:.6f}"
        )
    else:
        st.warning("SymPy no encontró una antiderivada cerrada; se usa solo la aproximación numérica.")
    if ejemplo is not None:
        st.markdown("**Solución analítica del informe (a mano)**")
        st.latex(ejemplo["solucion_latex"])
        diff = abs(ejemplo["valor_analitico"] - resultado.cuadratura)
        st.success(
            f"Valor analítico = {ejemplo['valor_analitico']:.6f} u³ · "
            f"diferencia con el software: {diff:.2e}"
        )

with tabconv:
    ns = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
    vals = [riemann_punto_medio(resultado.integrando, problema.a, problema.b, n) for n in ns]
    ref = resultado.exacto if resultado.exacto is not None else resultado.cuadratura
    errores = [abs(v - ref) for v in vals]
    filas = "".join(
        f"<tr><td>{n}</td><td>{v:.6f}</td><td>{e:.2e}</td></tr>"
        for n, v, e in zip(ns, vals, errores)
    )
    st.html(
        '<div class="tabla-envoltura"><table class="tabla">'
        "<thead><tr><th>n</th><th>Riemann</th><th>Error absoluto</th></tr></thead>"
        f"<tbody>{filas}</tbody></table></div>"
    )
    if max(errores) > 1e-12:
        st.plotly_chart(
            figura_convergencia(ns, errores, tema=tema),
            width="stretch",
            config={"displaylogo": False},
        )
        st.caption("El error de la regla del punto medio decrece aproximadamente como 1/n².")
    else:
        st.info(
            "En este ejemplo el integrando es lineal: la regla del punto medio coincide con el valor "
            "exacto en todas las subdivisiones y el error cae a cero."
        )

with tabgg:
    st.markdown(
        "**Mismo sólido construido en GeoGebra 3D.** El deslizador `giro` gira la curva y el deslizador "
        "`t` mueve la sección (disco, arandela o cascarón). Requiere conexión a internet."
    )
    comandos = comandos_geogebra(problema)
    components.html(html_applet(comandos), height=606, scrolling=False)
    with st.expander("Comandos de GeoGebra (para pegar uno por uno en geogebra.org/3d)"):
        st.code("\n".join(comandos), language="text")
        st.caption(
            "Abre geogebra.org/3d, pega cada línea en la barra de entrada y pulsa Enter. "
            "El comando `V = ...` muestra el volumen calculado por GeoGebra."
        )

st.html(
    '<footer class="pie"><span>Simulador educativo de Cálculo Integral</span>'
    "<span>SymPy, SciPy y Plotly</span></footer>"
)
