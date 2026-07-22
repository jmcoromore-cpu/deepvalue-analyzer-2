"""Analista cualitativo con Google Gemini.

Construye un prompt que incorpora el marco de análisis fundamental del curso
(Pat Dorsey + Porter + Buffett) y alimenta al modelo con los datos financieros
YA CALCULADOS (el modelo no inventa cifras). Devuelve el informe en Markdown y
una versión estructurada del veredicto cualitativo.
"""
from __future__ import annotations

import json
from typing import Dict, Optional

from ..config import get_settings
from ..models.schemas import (CompanyProfile, QualitativeAnalysis, ValuationResult)

SYSTEM_PROMPT = """
Eres un Analista Financiero Senior especializado en Inversión en Valor (Value Investing)
a largo plazo (5-10 años). Tu objetivo NO es hacer trading ni buscar puntos de entrada
especulativos, sino evaluar la CALIDAD FUNDAMENTAL del negocio, la durabilidad de sus
ventajas competitivas y su viabilidad como inversión de por vida.

Aplicas rigurosamente el siguiente marco (Pat Dorsey, Michael Porter, Warren Buffett):

1. VENTAJAS COMPETITIVAS (MOAT) — los 4 fosos de Pat Dorsey:
   - Activos intangibles: marcas que influyen en la conducta del consumidor (no solo
     notoriedad), patentes, licencias, concesiones administrativas.
   - Costes de reemplazo (switching costs): clientes cautivos, poder de fijación de precios.
   - Efecto red: el valor crece con el número de usuarios (dinámicas winner-takes-all).
   - Ventajas en costes: procesos eficientes, ubicación, activos únicos, economías de escala.
   Considera también la cultura empresarial cuando sea un foso real.

2. LAS 5 FUERZAS DE PORTER: rivalidad, nuevos entrantes (barreras de entrada),
   sustitutivos (riesgo de disrupción), poder de clientes, poder de proveedores.

3. EQUIPO GESTOR: asignación de capital (reinversión vs M&A vs dividendos vs recompras),
   alineamiento de intereses (skin in the game, estructura accionarial, remuneración),
   pericia operativa e integridad.

REGLAS ESTRICTAS:
- NO inventes cifras. Usa solo los datos financieros que se te proporcionan.
- Distingue claramente lo que puedes inferir de los datos de lo que es juicio de negocio.
- Señala tu nivel de confianza (Alta / Media / Baja) al final.
- Sé objetivo y equilibrado: expón tanto fortalezas como riesgos estructurales.
"""

USER_TEMPLATE = """
Analiza la calidad fundamental del negocio de **{name}** (ticker {ticker}, sector {sector},
industria {industry}, país {country}).

Descripción del negocio:
{description}

Datos financieros y señales cuantitativas ya calculadas (NO inventes otras cifras):
```json
{signals_json}
```

Resumen de valoración (precio actual vs valoración media de 4 modelos):
{valuation_summary}

Devuelve un informe en Markdown con EXACTAMENTE estas secciones y encabezados:

## MOAT
Evalúa cada uno de los 4 tipos de foso (intangibles, costes de reemplazo, efecto red,
ventajas en costes). Para cada uno indica: Presente (Sí/No/Parcial) y Fuerza (Fuerte/Moderada/Débil/Ninguna).
Termina con una línea "MOAT_GLOBAL: Wide|Narrow|None".

## PORTER
Analiza las 5 fuerzas. Para cada una indica intensidad (Alta/Media/Baja) y si es favorable
para la empresa.

## EQUIPO_GESTOR
Evalúa asignación de capital, alineamiento de intereses, pericia operativa e integridad,
con la información disponible.

## CALIDAD_NEGOCIO
Clasifica el negocio (Empresa Excelente / Negocio Cíclico Aceptable / Negocio Deficiente) y explica.

## TESIS
Tesis de inversión a 5-10 años: ¿por qué merece o no la pena tenerla en cartera?

## RIESGOS
Lista los principales riesgos estructurales (viñetas).

## CONFIANZA
Indica "CONFIANZA: Alta|Media|Baja" y una frase justificando.
"""


class GeminiAnalyst:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.ai_enabled

    def analyze(self, profile: CompanyProfile, signals: Dict,
                valuation: ValuationResult) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            model = genai.GenerativeModel(
                model_name=self.settings.gemini_model,
                system_instruction=SYSTEM_PROMPT,
            )
            val_summary = self._valuation_summary(valuation)
            prompt = USER_TEMPLATE.format(
                name=profile.name or profile.ticker,
                ticker=profile.ticker,
                sector=profile.sector or "n/d",
                industry=profile.industry or "n/d",
                country=profile.country or "n/d",
                description=(profile.description or "n/d")[:1500],
                signals_json=json.dumps(signals, indent=2, default=str, ensure_ascii=False),
                valuation_summary=val_summary,
            )
            resp = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 2048},
            )
            return resp.text
        except Exception as exc:  # noqa: BLE001
            return f"__AI_ERROR__: {exc}"

    @staticmethod
    def _valuation_summary(v: ValuationResult) -> str:
        parts = []
        for m in v.models:
            if m.included and m.value_per_share:
                parts.append(f"{m.name}={m.value_per_share}")
        line = ", ".join(parts) if parts else "sin valoraciones válidas"
        return (f"Precio actual: {v.current_price}. Valoración media: {v.mean_valuation}. "
                f"Precio máx. compra (margen {int(v.margin_of_safety*100)}%): {v.max_buy_price}. "
                f"Modelos: {line}. Potencial vs precio: "
                f"{round((v.upside_vs_price or 0)*100, 1)}%.")
