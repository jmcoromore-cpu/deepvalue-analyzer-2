# Metodología de análisis — DeepValue Analyzer

Este documento describe el marco conceptual que implementa la aplicación. El objetivo
es que el análisis sea **transparente y auditable**: cada número y cada juicio cualitativo
tiene una fuente y una regla explícita detrás.

El enfoque es de **inversión en valor a largo plazo (5-10 años)**, no de trading. Se combina
un pilar **cuantitativo** (replicando la lógica de una plantilla de valoración probada) con
un pilar **cualitativo** basado en el marco de Pat Dorsey, Michael Porter y Warren Buffett.

---

## 1. Pilar cuantitativo

### 1.1 Estados financieros normalizados

Los datos de las distintas fuentes se normalizan a un modelo común con 10 años de histórico
cuando está disponible:

- **Balance:** caja, cuentas a cobrar, inventarios, activo corriente, intangibles, goodwill,
  PP&E, activo total; deuda corto plazo, cuentas a pagar, pasivo corriente, deuda largo plazo,
  pasivo total; reservas, autocartera, prima de emisión, patrimonio neto. Se derivan
  **Deuda Neta** (`Deuda LP + Deuda CP − Caja`) y **Fondo de Maniobra** (`AC − PC`).
- **Cuenta de resultados:** ingresos, coste de ventas, margen bruto, gastos de venta/admin,
  I+D, EBITDA, EBIT, gastos financieros, BAI, impuestos, beneficio neto, BPA diluido, dividendo/acción.
- **Flujos de caja:** flujo operativo, D&A, CAPEX, **Free Cash Flow** (`FCO − CAPEX`),
  FCF/acción, flujos de inversión y financiación, recompras y dividendos pagados.

Para cada partida se calcula la **variación anual**, el **CAGR a 5 años** y el **CAGR a 10 años**.

### 1.2 Ratios financieros

Cada ratio se acompaña de su **rango óptimo** para alimentar el sistema de semáforos
(verde = óptimo, ámbar = aceptable, rojo = riesgo).

| Categoría | Ratios |
|---|---|
| **Liquidez** | Current Ratio, Acid Test (prueba ácida), Cash Ratio |
| **Actividad** | Días de activos, de cobro, de pago, rotación de inventario |
| **Solvencia** | Debt Ratio, Coeficiente de endeudamiento, Calidad de la deuda, Cobertura de intereses, Deuda Neta / EBIT |
| **Rentabilidad** | Margen bruto, margen neto, Pay-Out (sobre BPA y FCF), ROA, ROE, ROCE, **ROIC** |

**Chequeo ROE vs ROIC** (diapositiva 192 del curso): si `ROE > ROIC` de forma persistente,
el retorno del accionista se apoya en **apalancamiento**; si `ROIC > ROE`, la empresa
**acumula caja** (posible mala asignación de capital o gran robustez). Esto se reporta explícitamente.

### 1.3 Modelos de valoración

Se calculan cuatro valoraciones independientes y se promedian:

1. **Múltiplos:** proyección normalizada de ventas/EBITDA/beneficio/FCF con múltiplos históricos medios.
2. **Descuento de Flujos de Caja (DCF):** proyección del FCF, descuento a WACC y valor terminal
   por crecimiento a perpetuidad (Gordon).
3. **Descuento de Dividendos:** modelo de Gordon sobre el dividendo por acción.
4. **Graham:** fórmula del *Número de Graham* / valor intrínseco de Benjamin Graham.

Con la **valoración media** se aplica un **margen de seguridad** (20 % por defecto) para obtener
el **precio máximo de compra**, que se compara con el precio actual.

---

## 2. Pilar cualitativo

Basado en el marco del curso de análisis fundamental (Francisco Parga, CFA), que sintetiza a
Pat Dorsey, Michael Porter y Warren Buffett.

### 2.1 Ventajas competitivas — los 4 fosos de Pat Dorsey

> *"Ventaja competitiva: poseer algo difícilmente replicable que me permita obtener retornos
> extraordinarios de manera sostenible."*

1. **Activos intangibles:** marcas (que influyen en la conducta del consumidor, no solo notoriedad),
   patentes, licencias y concesiones administrativas.
2. **Costes de reemplazo (switching costs):** cuando cambiar de producto cuesta más que el beneficio →
   clientes cautivos y poder de fijación de precios.
3. **Efecto red:** el valor crece con el número de usuarios (directo, indirecto, de datos, de
   rendimiento tecnológico, social). Dinámicas *winner-takes-all*.
4. **Ventajas en costes:** procesos más eficientes, ubicación ventajosa, acceso a activos únicos,
   economías de escala (fabricación, distribución, nicho).

Además se evalúa la **cultura empresarial** ("el comportamiento cuando nadie mira") como fuente
de foso cuando es real.

### 2.2 Las 5 Fuerzas de Porter

1. Grado de rivalidad entre competidores actuales.
2. Amenaza de nuevos entrantes (depende de las **barreras de entrada**).
3. Amenaza de productos sustitutivos (incluye el **riesgo de disrupción**).
4. Poder de negociación de los clientes.
5. Poder de negociación de los proveedores.

### 2.3 Equipo gestor

- **Asignación de capital:** cómo emplea el excedente de caja (reinversión, M&A, dividendos, recompras)
  y si esas decisiones maximizan el valor por acción.
- **Alineamiento de intereses:** *skin in the game*, estructura accionarial (familia/accionista de
  referencia), estructura de la remuneración (fijo vs variable y qué incentiva).
- **Pericia operativa:** conocen y ejecutan bien el negocio ("mirar lo que hacen, no lo que dicen").
- **Integridad:** cumplimiento de *guidance* pasados, reconocimiento de errores.

---

## 3. Score y veredicto

El veredicto final combina ambos pilares con pesos configurables (por defecto 55 % cuantitativo /
45 % cualitativo):

- **Score cuantitativo (0-100):** salud financiera (liquidez/solvencia), calidad (márgenes, ROIC,
  crecimiento del FCF/acción) y valoración (precio actual vs precio máximo de compra con margen de seguridad).
- **Score cualitativo (0-100):** intensidad y durabilidad del moat, resultado del análisis de Porter,
  y calidad del equipo gestor.

El score combinado se traduce en un veredicto: **COMPRAR / MANTENER / EVITAR**, siempre acompañado
del *porqué* (tesis de inversión, riesgos estructurales y nivel de confianza).

---

## 4. Notas sobre las fuentes y la IA

- Los **datos financieros** provienen de fuentes verificables (yfinance, SEC EDGAR, Alpha Vantage).
  El modelo de IA **no inventa cifras**: recibe los datos ya calculados y produce únicamente el
  juicio cualitativo, señalando su nivel de confianza.
- La cobertura y la profundidad histórica dependen de la fuente. EDGAR ofrece más años pero solo
  para empresas de EE. UU.; yfinance da cobertura mundial con menos histórico.

---

## 5. Aviso legal

Esta herramienta es de carácter **educativo e informativo**. No constituye asesoramiento financiero
ni una recomendación de inversión. Ninguna de las salidas debe interpretarse como una orden de compra
o venta. Realiza tu propia diligencia debida y, si lo necesitas, consulta a un asesor financiero
autorizado antes de tomar decisiones de inversión.
