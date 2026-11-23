# Guía para el informe PDF (lista de verificación)

Estructura exigida por la guía del Proyecto Integrador. Marca cada punto al completarlo.

## Portada
- [ ] Título, integrantes (con programa académico) y datos institucionales (UTS).

## 1. Datos de acceso y enlaces
- [ ] Aplicación web (URL activa) · [ ] Repositorio público · [ ] Video (8–10 min)
- [ ] Credenciales de prueba (solo si la app tuviera login; esta versión no lo requiere, indícalo).

## 2. Introducción
- [ ] Justificación y relación con Ingeniería de Sistemas (modelado computacional de problemas físicos).

## 3. Marco teórico (deducción formal)
- [ ] Discos: `V = π ∫ [f(x)]² dx` — a partir de la suma de volúmenes de cilindros `π f(xᵢ)² Δx`.
- [ ] Arandelas: `V = π ∫ ([R(x)]² − [r(x)]²) dx`.
- [ ] Cascarones: `V = 2π ∫ x·f(x) dx` — a partir de cilindros huecos `2π x f(x) Δx`.

## 4. Desarrollo de los ejemplos (uno por método)
Para cada ejemplo incluir: contexto de ingeniería · gráfica 2D de la región · solución analítica paso a paso ·
captura 3D del simulador · explicación breve del código.
- [ ] Ejemplo 1 (Discos) — con `f(x)` rotada alrededor de un eje principal.
- [ ] Ejemplo 2 (Arandelas) — entre dos funciones, con eje principal o **desplazado**.
- [ ] Ejemplo 3 (Cascarones) — con ventaja analítica explícita frente a arandelas.

## 5. Código y anexos
- [ ] Explicación de `calculo.py`, `visual.py` y `app.py` (código completo en el repositorio).
- [ ] Capturas guardadas en `docs/capturas/`.

## 6. Conclusiones y referencias
- [ ] Conclusiones propias · [ ] Referencias en formato académico.

## Rúbrica (para autoevaluarse)
| Criterio | Peso |
|---|---|
| Rigor matemático (3 ejemplos) | 30 % |
| Simulador y código | 35 % |
| Video de sustentación | 20 % |
| Informe escrito | 15 % |

## Entregables
| Entregable | Formato |
|---|---|
| Informe | PDF |
| Código fuente | Repositorio GitHub/GitLab con README |
| Simulador | URL web activa |
| Video | YouTube/Drive, 8–10 min, todos los integrantes participan |
