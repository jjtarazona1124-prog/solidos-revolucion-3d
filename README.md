# 🌀 Simulador de Sólidos de Revolución 3D

Proyecto Integrador de Cálculo Integral — Ingeniería de Sistemas (UTS).

Aplicación interactiva que modela y calcula el volumen de sólidos de revolución, mostrando el sólido
en 3D (rotable), las secciones transversales que lo forman y el contraste entre el resultado
exacto (SymPy) y las aproximaciones numéricas (cuadratura de SciPy y suma de Riemann).

## 🔗 Enlaces del proyecto

| Recurso | Enlace / Información |
|---|---|
| Aplicación web (simulador) |https://solidos-revolucion-3d-o6ncdy7aznnahanfaxa92c.streamlit.app |
| Credenciales de prueba | No requiere inicio de sesión (acceso libre) |
| Repositorio |https://github.com/jjtarazona1124-prog/solidos-revolucion-3d.git|
| Video de sustentación (8–10 min) |https://drive.google.com/file/d/1u2S4zMU5RRh-CVHMfev-lERp3HpY6qcz/view?usp=sharing  |

## 👥 Integrantes

| Nombre | Programa académico | 
|---|---
| Juan Jose Tarazona| Ingeniería de Sistemas |  
| Jose Miguel Santamaria | Ingeniería de Sistemas | 
|Juan Esteban Mantilla| Ingeniería de Sistemas | 
| Fernando Escobar | Ingeniería Electrónica | 

## ✨ Funcionalidades

- Ejemplos contextualizados por método (el de arandelas con eje desplazado `y = −1`).
- Pestaña GeoGebra: el mismo sólido construido en GeoGebra 3D (applet incrustado, con deslizadores
  de giro y de sección) y los comandos para pegarlos en geogebra.org/3d.
- Modo personalizado: ingresa `f(x)`, `g(x)`, límites `a`, `b` y el eje de giro.
- Sólido 3D interactivo (rotar, acercar) con ángulo de giro ajustable para ver cómo se forma.
- Secciones transversales (disco / arandela) y una sección resaltada con deslizador.
- Resultado exacto simbólico, cuadratura numérica y **suma de Riemann** con error.
- Pestaña de convergencia (error vs. número de subdivisiones `n`).
- Pestaña de desarrollo analítico: integrando, antiderivada y evaluación.
- Entrada de funciones validada (no ejecuta código arbitrario).

## 📐 Fórmulas

| Método | Volumen |
|---|---|
| Discos | `V = π ∫ₐᵇ [f(x) − c]² dx` |
| Arandelas | `V = π ∫ₐᵇ [R(x)² − r(x)²] dx`, con `R = \|f − c\|`, `r = \|g − c\|` |

`c = 0` corresponde al eje X; `c ≠ 0` es un eje desplazado `y = c`.

## 🧪 Ejemplos incluidos

| # | Método | Programa | Problema | Volumen exacto |
|---|---|---|---|---|
| 1 | Discos | Sistemas | `f(x) = √(x+1)`, `x ∈ [0, 3]`, eje X | `15π/2 ≈ 23.5619` |
| 2 | Arandelas | Electrónica | entre `y = 2x` y `y = x²`, `x ∈ [0, 2]`, eje `y = −1` | `104π/15 ≈ 21.7817` |
| 3 | Cascarones | Sistemas | `y = x³ + x`, `x ∈ [0, 1]`, eje Y | `16π/15 ≈ 3.3510` |

## 🚀 Instalación y ejecución local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La app abre en <http://localhost:8501>. No hay build ni paso de compilación: el proyecto se ejecuta
directamente con Streamlit.

## ☁️ Despliegue en Streamlit Community Cloud

1. Sube este repositorio a GitHub (público).
2. Entra a <https://share.streamlit.io> e inicia sesión con GitHub.
3. **New app** → elige el repositorio, rama `main` y archivo principal `app.py`.
4. **Deploy** y copia la URL en la tabla de enlaces de arriba y en el informe.

## 🗂️ Estructura

```
.
├── app.py                  # Interfaz Streamlit
├── solidos/
│   ├── calculo.py          # Motor: integrales exactas (SymPy) y numéricas (SciPy/NumPy)
│   ├── ejemplos.py         # Los ejemplos con su solución analítica
│   ├── visual.py           # Región 2D y sólido 3D (Plotly)
│   └── geogebra.py         # Comandos y applet de GeoGebra 3D
├── tests/                  # Pruebas automáticas (pytest)
├── docs/
│   ├── GUIA_INFORME.md     # Lista de verificación del informe PDF
│   ├── EXPLICACION_CODIGO.md  # Guía del código para estudiar y explicar en el video
│   └── capturas/           # Capturas de pantalla para el informe
├── .github/workflows/      # Integración continua (pytest)
├── .streamlit/config.toml  # Tema de la app
├── requirements.txt
├── requirements-dev.txt
└── LICENSE
```

## ✅ Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Las pruebas comprueban que los ejemplos coinciden con la solución analítica, casos de
validación (cilindros), el manejo del eje de giro y el rechazo de entradas peligrosas.

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
