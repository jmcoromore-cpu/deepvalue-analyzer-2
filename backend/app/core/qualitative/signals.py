"""Señales cuantitativas de calidad del negocio.

Traducen los estados financieros en indicios objetivos de ventaja competitiva,
que sirven tanto para el veredicto por reglas como de evidencia para la IA.
Basado en el marco del curso: márgenes altos y sostenidos, ROIC elevado,
crecimiento del FCF/acción, estabilidad, etc.
"""
from __future__ import annotations

import statistics
from typing import Dict, List, Optional

from ...models.schemas import FinancialStatements
from ...utils.math_utils import safe_div


def _avg_margin(fs: FinancialStatements, num_key: str, num_block: str) -> Optional[float]:
    years = sorted(fs.years, reverse=True)[:5]
    vals = []
    for y in years:
        num = getattr(fs, num_block).get(num_key, {}).get(y)
        rev = fs.income.get("revenue", {}).get(y)
        m = safe_div(num, rev)
        if m is not None:
            vals.append(m)
    return sum(vals) / len(vals) if vals else None


def _avg_roic(fs: FinancialStatements) -> Optional[float]:
    from ..ratios import _roic
    years = sorted(fs.years, reverse=True)[:5]
    vals = [_roic(fs, y) for y in years]
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _margin_stability(fs: FinancialStatements) -> Optional[float]:
    """Desviación típica del margen neto (menor = más predecible)."""
    years = sorted(fs.years, reverse=True)[:5]
    vals = []
    for y in years:
        m = safe_div(fs.income.get("net_income", {}).get(y),
                     fs.income.get("revenue", {}).get(y))
        if m is not None:
            vals.append(m)
    if len(vals) < 3:
        return None
    return statistics.pstdev(vals)


def compute_signals(fs: FinancialStatements) -> Dict[str, Optional[float]]:
    gross = _avg_margin(fs, "gross_profit", "income")
    net = _avg_margin(fs, "net_income", "income")
    roic = _avg_roic(fs)
    stability = _margin_stability(fs)

    fcf_ps = fs.derived.get("fcf_per_share")
    fcf_growth = fcf_ps.cagr_5y if fcf_ps else None
    rev = fs.derived.get("revenue")
    rev_growth = rev.cagr_5y if rev else None

    return {
        "avg_gross_margin": gross,
        "avg_net_margin": net,
        "avg_roic": roic,
        "net_margin_stability": stability,   # menor es mejor
        "fcf_per_share_cagr_5y": fcf_growth,
        "revenue_cagr_5y": rev_growth,
    }


def moat_signal_strength(signals: Dict[str, Optional[float]]) -> float:
    """Puntúa 0-100 la intensidad del moat según señales cuantitativas."""
    score = 0.0
    weight = 0.0

    roic = signals.get("avg_roic")
    if roic is not None:
        weight += 35
        score += 35 * _band(roic, 0.07, 0.20)

    gross = signals.get("avg_gross_margin")
    if gross is not None:
        weight += 20
        score += 20 * _band(gross, 0.20, 0.55)

    net = signals.get("avg_net_margin")
    if net is not None:
        weight += 20
        score += 20 * _band(net, 0.05, 0.20)

    fcf_g = signals.get("fcf_per_share_cagr_5y")
    if fcf_g is not None:
        weight += 15
        score += 15 * _band(fcf_g, 0.0, 0.15)

    stab = signals.get("net_margin_stability")
    if stab is not None:
        weight += 10
        # menor desviación = mejor
        score += 10 * (1 - _band(stab, 0.0, 0.15))

    if weight == 0:
        return 50.0
    return round(score / weight * 100, 1)


def _band(value: float, low: float, high: float) -> float:
    """Normaliza a 0-1 dentro de [low, high]."""
    if high == low:
        return 0.5
    return max(0.0, min(1.0, (value - low) / (high - low)))
