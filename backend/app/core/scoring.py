"""Scoring cuantitativo y combinación con el cualitativo.

Produce un score 0-100 por pilar y el score final ponderado, replicando la
filosofía de la plantilla: salud financiera + calidad + valoración vs precio.
"""
from __future__ import annotations

from typing import Dict, Optional

from ..models.schemas import (RatioLight, RatiosBundle, ScoreBreakdown,
                              ValuationResult)


def _light_score(light: RatioLight) -> Optional[float]:
    return {RatioLight.GREEN: 1.0, RatioLight.AMBER: 0.5,
            RatioLight.RED: 0.0}.get(light)


def _group_score(group) -> Optional[float]:
    vals = [_light_score(r.light) for r in group.ratios if _light_score(r.light) is not None]
    return sum(vals) / len(vals) if vals else None


def quant_score(ratios: RatiosBundle, valuation: ValuationResult) -> Dict[str, float]:
    detail: Dict[str, float] = {}

    # Salud financiera (liquidez + solvencia)
    liq = _group_score(ratios.liquidity)
    sol = _group_score(ratios.solvency)
    health = _avg([liq, sol])
    detail["salud_financiera"] = round((health or 0.5) * 100, 1)

    # Calidad (rentabilidad)
    prof = _group_score(ratios.profitability)
    detail["calidad_rentabilidad"] = round((prof or 0.5) * 100, 1)

    # Valoración: descuento respecto al precio máximo de compra
    val_score = 0.5
    if valuation.discount_to_max_buy is not None:
        d = valuation.discount_to_max_buy
        # d>0 => cotiza por debajo del precio máx de compra (bueno)
        val_score = max(0.0, min(1.0, 0.5 + d))
    elif valuation.upside_vs_price is not None:
        val_score = max(0.0, min(1.0, 0.5 + valuation.upside_vs_price / 2))
    detail["valoracion"] = round(val_score * 100, 1)

    # Score cuantitativo ponderado
    total = (detail["salud_financiera"] * 0.30
             + detail["calidad_rentabilidad"] * 0.35
             + detail["valoracion"] * 0.35)
    detail["_total"] = round(total, 1)
    return detail


def qual_score(moat_score: Optional[float], management_score: Optional[float],
               porter_favorable_ratio: Optional[float]) -> Dict[str, float]:
    detail: Dict[str, float] = {}
    detail["moat"] = round(moat_score if moat_score is not None else 50.0, 1)
    detail["equipo_gestor"] = round(management_score if management_score is not None else 50.0, 1)
    detail["porter"] = round((porter_favorable_ratio if porter_favorable_ratio is not None else 0.5) * 100, 1)
    total = detail["moat"] * 0.50 + detail["equipo_gestor"] * 0.25 + detail["porter"] * 0.25
    detail["_total"] = round(total, 1)
    return detail


def combine(quant: Dict[str, float], qual: Dict[str, float],
            quant_weight: float, qual_weight: float) -> ScoreBreakdown:
    q = quant.get("_total", 50.0)
    ql = qual.get("_total", 50.0)
    total_w = quant_weight + qual_weight or 1.0
    final = (q * quant_weight + ql * qual_weight) / total_w
    return ScoreBreakdown(
        quant_score=round(q, 1), qual_score=round(ql, 1), final_score=round(final, 1),
        quant_detail={k: v for k, v in quant.items() if not k.startswith("_")},
        qual_detail={k: v for k, v in qual.items() if not k.startswith("_")},
    )


def _avg(vals):
    nums = [v for v in vals if v is not None]
    return sum(nums) / len(nums) if nums else None
