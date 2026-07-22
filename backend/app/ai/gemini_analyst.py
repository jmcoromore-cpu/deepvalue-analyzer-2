"""Analista cualitativo con Google Gemini.

Pide a Gemini que devuelva el análisis YA ESTRUCTURADO en JSON (no texto libre),
usando el marco del curso (Pat Dorsey + Porter + Buffett). Así cada campo se
rellena de forma fiable, sin necesidad de trocear texto. El modelo no inventa
cifras: recibe los datos financieros ya calculados y solo emite el juicio.
"""
from __future__ import annotations

import json
from typing import Dict, Optional

from ..config import get_settings
from ..models.schemas import CompanyProfile, ValuationResult

SYSTEM_PROMPT = """
Eres un Analista Financiero Senior especializado en Inversión en Valor (Value Investing)
a largo plazo (5-10 años). Evalúas la CALIDAD FUNDAMENTAL del negocio y la durabilidad de
sus ventajas competitivas, no el trading a corto plazo.

Aplicas el marco de Pat Dorsey (4 fosos: activos intangibles, costes de reemplazo,
efecto red, ventajas en costes), las 5 Fuerzas de Michael Porter, y los criterios de
Warren Buffett sobre equipo gestor (asignación de capital, alineamiento de intereses /
skin in the game, pericia operativa e integridad).

REGLAS ESTRICTAS:
- NO inventes cifras financieras. Usa solo los datos que se te proporcionan.
- Sé objetivo y equilibrado: expón fortalezas y también riesgos estructurales.
- Responde EXCLUSIVAMENTE con un objeto JSON válido que siga el esquema pedido.
  No añadas texto fuera del JSON ni bloques de código markdown.
"""

# Estructura JSON exacta que debe devolver el modelo.
JSON_INSTRUCTIONS = """
Devuelve un JSON con EXACTAMENTE esta estructura (rellena todos los campos en español):

{
  "moat": {
    "overall_rating": "Wide | Narrow | None",
    "summary": "2-3 frases sobre la ventaja competitiva global.",
    "types": [
      {"name": "Activos intangibles", "present": "Sí | No | Parcial", "strength": "Fuerte | Moderada | Débil | Ninguna", "rationale": "1-2 frases."},
      {"name": "Costes de reemplazo", "present": "Sí | No | Parcial", "strength": "Fuerte | Moderada | Débil | Ninguna", "rationale": "1-2 frases."},
      {"name": "Efecto red", "present": "Sí | No | Parcial", "strength": "Fuerte | Moderada | Débil | Ninguna", "rationale": "1-2 frases."},
      {"name": "Ventajas en costes", "present": "Sí | No | Parcial", "strength": "Fuerte | Moderada | Débil | Ninguna", "rationale": "1-2 frases."}
    ]
  },
  "porter": {
    "summary": "2-3 frases sobre la estructura competitiva del sector.",
    "forces": [
      {"name": "Rivalidad entre competidores", "intensity": "Alta | Media | Baja", "favorable_for_company": true, "rationale": "1-2 frases."},
      {"name": "Amenaza de nuevos entrantes", "intensity": "Alta | Media | Baja", "favorable_for_company": true, "rationale": "1-2 frases."},
      {"name": "Amenaza de sustitutivos", "intensity": "Alta | Media | Baja", "favorable_for_company": true, "rationale": "1-2 frases."},
      {"name": "Poder de clientes", "intensity": "Alta | Media | Baja", "favorable_for_company": true, "rationale": "1-2 frases."},
      {"name": "Poder de proveedores", "intensity": "Alta | Media | Baja", "favorable_for_company": true, "rationale": "1-2 frases."}
    ]
  },
  "management": {
    "capital_allocation": "1-2 frases sobre asignación de capital.",
    "alignment": "1-2 frases sobre alineamiento de intereses / skin in the game.",
    "operating_skill": "1-2 frases sobre pericia operativa.",
    "integrity": "1-2 frases sobre integridad."
  },
  "business_quality": "Empresa Excelente | Negocio Cíclico Aceptable | Negocio Deficiente — con breve explicación.",
  "thesis": "Tesis de inversión a 5-10 años (3-4 frases).",
  "risks": ["Riesgo estructural 1", "Riesgo estructural 2", "Riesgo estructural 3"],
  "confidence": "Alta | Media | Baja"
}

Nota sobre "favorable_for_company": true si esa fuerza es favorable para la empresa
(por ejemplo, intensidad baja de rivalidad o de amenaza suele ser favorable), false si no.
"""

USER_TEMPLATE = """
Analiza la calidad fundamental del negocio de {name} (ticker {ticker}, sector {sector},
industria {industry}, país {country}).

Descripción del negocio:
{description}

Señales cuantitativas ya calculadas (NO inventes otras cifras):
{signals_json}

Resumen de valoración:
{valuation_summary}

{json_instructions}
"""


class GeminiAnalyst:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.ai_enabled

    def analyze(self, profile: CompanyProfile, signals: Dict,
                valuation: ValuationResult) -> Optional[Dict]:
        """Devuelve {'ok': True, 'data': {...}} con el JSON del modelo,
        o {'ok': False, 'error': '...'} si algo falla. None si la IA está desactivada."""
        if not self.enabled:
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            model = genai.GenerativeModel(
                model_name=self.settings.gemini_model,
                system_instruction=SYSTEM_PROMPT,
            )
            prompt = USER_TEMPLATE.format(
                name=profile.name or profile.ticker,
                ticker=profile.ticker,
                sector=profile.sector or "n/d",
                industry=profile.industry or "n/d",
                country=profile.country or "n/d",
                description=(profile.description or "n/d")[:1500],
                signals_json=json.dumps(signals, indent=2, default=str, ensure_ascii=False),
                valuation_summary=self._valuation_summary(valuation),
                json_instructions=JSON_INSTRUCTIONS,
            )
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    # Amplio: los modelos "pensantes" (Gemini 2.5) gastan tokens
                    # razonando; con un límite bajo la respuesta llegaría vacía/cortada.
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
            )
            text, reason = self._response_text(resp)
            data = self._extract_json(text)
            if data is None:
                detail = "respuesta vacía o incompleta"
                if reason:
                    detail += f" (motivo: {reason})"
                return {"ok": False, "error": f"La IA no devolvió un JSON válido ({detail})."}
            return {"ok": True, "data": data}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def _response_text(resp) -> "tuple[str, Optional[str]]":
        """Extrae el texto de la respuesta de forma robusta y el finish_reason.

        Evita que resp.text lance si la respuesta viene sin partes claras.
        """
        reason = None
        # Intento directo
        try:
            if getattr(resp, "text", None):
                return resp.text, reason
        except Exception:  # noqa: BLE001
            pass
        # Recorre los candidatos manualmente
        try:
            for cand in getattr(resp, "candidates", []) or []:
                reason = str(getattr(cand, "finish_reason", "")) or reason
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", []) if content else []
                buf = []
                for p in parts:
                    t = getattr(p, "text", None)
                    if t:
                        buf.append(t)
                if buf:
                    return "".join(buf), reason
        except Exception:  # noqa: BLE001
            pass
        return "", reason

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict]:
        if not text:
            return None
        t = text.strip()
        # Quita vallas de markdown si las hubiera (```json ... ```)
        if t.startswith("```"):
            t = t.strip("`")
            if t.lower().startswith("json"):
                t = t[4:]
        # Recorta al primer { y último }
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            t = t[start:end + 1]
        try:
            return json.loads(t)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _valuation_summary(v: ValuationResult) -> str:
        parts = [f"{m.name}={m.value_per_share}" for m in v.models
                 if m.included and m.value_per_share]
        line = ", ".join(parts) if parts else "sin valoraciones válidas"
        return (f"Precio actual: {v.current_price}. Valoración media: {v.mean_valuation}. "
                f"Precio máx. compra (margen {int(v.margin_of_safety*100)}%): {v.max_buy_price}. "
                f"Modelos: {line}. Potencial vs precio: {round((v.upside_vs_price or 0)*100, 1)}%.")
