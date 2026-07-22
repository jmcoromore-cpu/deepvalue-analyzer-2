"""Valoración por la fórmula de Benjamin Graham.

Número de Graham (valor intrínseco defensivo):  V = √(22,5 × BPA × Valor contable/acción)
Solo válido con BPA y valor contable positivos.
"""
from __future__ import annotations

import math
from typing import Optional

from ...models.schemas import FinancialStatements, ValuationModelResult


def value_graham(fs: FinancialStatements, shares: Optional[float]) -> ValuationModelResult:
    years = sorted(fs.years, reverse=True)
    eps = None
    for y in years:
        v = fs.income.get("eps_diluted", {}).get(y)
        if v not in (None, 0):
            eps = v
            break
    equity = None
    for y in years:
        v = fs.balance.get("total_equity", {}).get(y)
        if v not in (None, 0):
            equity = v
            break

    if eps is None and fs.income.get("net_income") and shares:
        for y in years:
            ni = fs.income.get("net_income", {}).get(y)
            if ni:
                eps = ni / shares
                break

    if not eps or not equity or not shares or eps <= 0:
        return ValuationModelResult(name="Graham", value_per_share=None, included=False,
                                    detail="Requiere BPA y valor contable positivos.")
    book_value_ps = equity / shares
    if book_value_ps <= 0:
        return ValuationModelResult(name="Graham", value_per_share=None, included=False,
                                    detail="Valor contable por acción no positivo.")
    value = math.sqrt(22.5 * eps * book_value_ps)
    detail = f"√(22,5 × BPA {eps:.2f} × VC/acción {book_value_ps:.2f})."
    return ValuationModelResult(name="Graham", value_per_share=round(value, 2),
                                included=True, detail=detail)
