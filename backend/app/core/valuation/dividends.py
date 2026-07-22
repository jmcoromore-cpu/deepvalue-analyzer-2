"""Valoración por Descuento de Dividendos (modelo de Gordon).

Valor = D1 / (r − g), con D1 el dividendo esperado el próximo año.
Solo aplica a empresas que pagan dividendo de forma consistente.
"""
from __future__ import annotations

from typing import Optional

from ...models.schemas import FinancialStatements, ValuationModelResult
from ...utils.math_utils import mean


def value_dividends(fs: FinancialStatements, discount_rate: float,
                    terminal_growth: float) -> ValuationModelResult:
    dps_series = fs.income.get("dividend_per_share", {})
    years = sorted(fs.years, reverse=True)[:5]
    dps_vals = [dps_series.get(y) for y in years if dps_series.get(y) is not None]

    if not dps_vals or dps_vals[0] in (None, 0):
        return ValuationModelResult(name="Dividendos", value_per_share=None, included=False,
                                    detail="No paga dividendo consistente.")
    d0 = dps_vals[0]
    # Crecimiento medio del dividendo, acotado
    changes = []
    for i in range(len(dps_vals) - 1):
        prev = dps_vals[i + 1]
        if prev and prev > 0:
            changes.append((dps_vals[i] - prev) / prev)
    g = mean(changes) if changes else terminal_growth
    g = max(min(g, 0.10), 0.0)
    r = discount_rate if discount_rate > g else g + 0.03

    d1 = d0 * (1 + g)
    value = d1 / (r - g)
    detail = f"D0={d0:.2f}, g={g*100:.1f}%, r={r*100:.1f}% (Gordon)."
    return ValuationModelResult(name="Dividendos", value_per_share=round(value, 2),
                                included=True, detail=detail)
