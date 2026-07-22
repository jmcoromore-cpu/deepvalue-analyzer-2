"""Veredicto final: traduce el score en COMPRAR / MANTENER / EVITAR.

Combina el score numérico con condiciones de guarda (p. ej. no recomendar
COMPRAR si cotiza muy por encima del precio máximo de compra), y redacta la
tesis y los riesgos (de la IA si está disponible, o generados por reglas).
"""
from __future__ import annotations

from typing import List, Optional

from ..models.schemas import (Decision, QualitativeAnalysis, ScoreBreakdown,
                              ValuationResult, Verdict)


def build_verdict(score: ScoreBreakdown, valuation: ValuationResult,
                  qualitative: QualitativeAnalysis,
                  ai_thesis: str = "", ai_risks: Optional[List[str]] = None) -> Verdict:
    final = score.final_score

    # Guarda por valoración: penaliza compra si cotiza caro
    overpriced = (valuation.discount_to_max_buy is not None
                  and valuation.discount_to_max_buy < -0.15)
    cheap = (valuation.discount_to_max_buy is not None
             and valuation.discount_to_max_buy >= 0)

    if final >= 68 and not overpriced:
        decision = Decision.BUY
    elif final >= 45 or (final >= 40 and cheap):
        decision = Decision.HOLD
    else:
        decision = Decision.AVOID

    # Si el score es alto pero está caro, degradar a MANTENER
    if decision == Decision.BUY and overpriced:
        decision = Decision.HOLD

    confidence = qualitative.confidence or "Media"

    strengths = _strengths(score, valuation, qualitative)
    risks = ai_risks or _default_risks(score, valuation, qualitative)
    thesis = ai_thesis or _default_thesis(decision, score, valuation, qualitative)

    return Verdict(decision=decision, final_score=final, confidence=confidence,
                   thesis=thesis, strengths=strengths, risks=risks)


def _strengths(score, valuation, qa) -> List[str]:
    out = []
    if score.quant_detail.get("salud_financiera", 0) >= 65:
        out.append("Balance sólido y buena salud financiera.")
    if score.quant_detail.get("calidad_rentabilidad", 0) >= 65:
        out.append("Alta rentabilidad (márgenes y retornos sobre el capital).")
    if qa.moat.overall_rating in ("Wide", "Narrow"):
        out.append(f"Ventaja competitiva ({qa.moat.overall_rating}).")
    if valuation.discount_to_max_buy is not None and valuation.discount_to_max_buy >= 0:
        out.append("Cotiza por debajo del precio máximo de compra (margen de seguridad).")
    return out or ["Sin fortalezas destacadas según los datos disponibles."]


def _default_risks(score, valuation, qa) -> List[str]:
    out = []
    if score.quant_detail.get("salud_financiera", 100) < 45:
        out.append("Liquidez o solvencia por debajo de los rangos óptimos.")
    if valuation.discount_to_max_buy is not None and valuation.discount_to_max_buy < -0.15:
        out.append("Cotiza por encima del precio máximo de compra: poco margen de seguridad.")
    if qa.moat.overall_rating == "None":
        out.append("Sin ventaja competitiva evidente: retornos vulnerables a la competencia.")
    return out or ["Riesgos habituales del mercado y de ejecución del negocio."]


def _default_thesis(decision, score, valuation, qa) -> str:
    q = qa.business_quality or "calidad de negocio no concluyente"
    v = ""
    if valuation.mean_valuation and valuation.current_price:
        up = (valuation.upside_vs_price or 0) * 100
        v = f" La valoración media ({valuation.mean_valuation}) implica un potencial del {up:.0f}% frente al precio actual."
    return (f"Veredicto {decision.value} con un score de {score.final_score:.0f}/100. "
            f"Se clasifica como: {q}.{v} "
            "Recuerda que esta evaluación es educativa y no constituye asesoramiento financiero.")
