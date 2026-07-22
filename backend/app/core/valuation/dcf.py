"""Valoración por Descuento de Flujos de Caja (DCF).

Proyecta el Free Cash Flow a 5 años con una tasa de crecimiento acotada,
descuenta a la tasa (WACC) indicada y añade un valor terminal por el modelo
de crecimiento a perpetuidad de Gordon.
"""
from __future__ import annotations

from typing import Optional

from ...models.schemas import FinancialStatements, ValuationModelResult
from ...utils.math_utils import mean


def value_dcf(fs: FinancialStatements, shares: Optional[float],
              net_debt: Optional[float], discount_rate: float,
              terminal_growth: float) -> ValuationModelResult:
    fcf_series = fs.cashflow.get("free_cash_flow", {})
    years = sorted(fs.years, reverse=True)[:5]
    fcf_vals = [fcf_series.get(y) for y in years if fcf_series.get(y) is not None]

    if not fcf_vals or not shares:
        return ValuationModelResult(name="DCF", value_per_share=None, included=False,
                                    detail="FCF histórico insuficiente.")
    base_fcf = fcf_vals[0]
    if base_fcf <= 0:
        # usa la media si el último es negativo
        base_fcf = mean(fcf_vals) or 0
    if base_fcf <= 0:
        return ValuationModelResult(name="DCF", value_per_share=None, included=False,
                                    detail="FCF medio no positivo; DCF no aplicable.")

    # Crecimiento medio histórico del FCF, acotado
    changes = []
    for i in range(len(fcf_vals) - 1):
        prev = fcf_vals[i + 1]
        if prev and prev > 0:
            changes.append((fcf_vals[i] - prev) / prev)
    g = mean(changes) if changes else 0.05
    g = max(min(g, 0.15), 0.0)

    if discount_rate <= terminal_growth:
        discount_rate = terminal_growth + 0.03  # evita división negativa

    # Proyección a 5 años + valor terminal
    pv = 0.0
    fcf = base_fcf
    for t in range(1, 6):
        fcf *= (1 + g)
        pv += fcf / ((1 + discount_rate) ** t)
    terminal_value = fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv += terminal_value / ((1 + discount_rate) ** 5)

    equity_value = pv - (net_debt or 0)
    value_per_share = equity_value / shares
    detail = (f"FCF base≈{base_fcf:,.0f}, g={g*100:.1f}%, WACC={discount_rate*100:.1f}%, "
              f"g∞={terminal_growth*100:.1f}%.")
    return ValuationModelResult(name="DCF", value_per_share=round(value_per_share, 2),
                                included=value_per_share > 0, detail=detail)
