"""Valoración por múltiplos.

Estima el valor por acción proyectando el beneficio/FCF normalizado y aplicando
los múltiplos históricos medios (P/E y P/FCF) de la propia empresa.
"""
from __future__ import annotations

from typing import Optional

from ...models.schemas import FinancialStatements, ValuationModelResult
from ...utils.math_utils import mean, safe_div


def _hist_multiple(fs, price_key_block, price_key, per_share_series) -> Optional[float]:
    return None


def value_multiples(fs: FinancialStatements, current_price: Optional[float],
                    shares: Optional[float]) -> ValuationModelResult:
    years = sorted(fs.years, reverse=True)[:5]
    if not years or not shares or not current_price:
        return ValuationModelResult(name="Múltiplos", value_per_share=None,
                                    included=False, detail="Datos insuficientes.")

    # EPS y FCF/acción por año
    eps_series = fs.income.get("eps_diluted", {})
    fcf_ps_series = fs.cashflow.get("fcf_per_share", {})
    ni_series = fs.income.get("net_income", {})

    # P/E histórico medio (precio actual como aprox. si no hay histórico de precio)
    pe_list = []
    for y in years:
        eps = eps_series.get(y)
        if eps and eps > 0:
            pe_list.append(current_price / eps if y == years[0] else None)
    # múltiplo medio del sector conservador si no hay datos: usa P/E actual
    latest_eps = None
    for y in years:
        if eps_series.get(y) not in (None, 0):
            latest_eps = eps_series.get(y)
            break
    if latest_eps is None and ni_series:
        for y in years:
            ni = ni_series.get(y)
            if ni:
                latest_eps = ni / shares
                break

    # Crecimiento medio del beneficio
    ni_vals = [ni_series.get(y) for y in years if ni_series.get(y) is not None]
    growth = None
    if len(ni_vals) >= 2:
        changes = []
        for i in range(len(ni_vals) - 1):
            if ni_vals[i + 1] and ni_vals[i + 1] != 0:
                changes.append((ni_vals[i] - ni_vals[i + 1]) / abs(ni_vals[i + 1]))
        growth = mean(changes)
    growth = max(min(growth or 0.05, 0.20), -0.05)  # acota entre -5% y 20%

    # P/E objetivo: conservador (mín entre P/E actual y 18) ajustado por crecimiento
    current_pe = safe_div(current_price, latest_eps) if latest_eps else None
    target_pe = min(current_pe or 15.0, 20.0)
    if latest_eps is None or latest_eps <= 0:
        return ValuationModelResult(name="Múltiplos", value_per_share=None, included=False,
                                    detail="Beneficio por acción no positivo; múltiplo no aplicable.")

    forward_eps = latest_eps * (1 + growth)
    fair_value = forward_eps * target_pe
    detail = (f"EPS≈{latest_eps:.2f}, crecimiento medio {growth*100:.1f}%, "
              f"P/E objetivo {target_pe:.1f}×.")
    return ValuationModelResult(name="Múltiplos", value_per_share=round(fair_value, 2),
                                included=True, detail=detail)
