"""Motor de valoración: combina los 4 modelos.

Calcula cada valoración, promedia las incluidas, aplica el margen de seguridad
para obtener el precio máximo de compra y calcula el potencial vs precio actual.
Replica la lógica de la hoja VALUATION de la plantilla original.
"""
from __future__ import annotations

from typing import Optional

from ...models.schemas import FinancialStatements, ValuationResult
from ...utils.math_utils import latest_value, mean
from .dcf import value_dcf
from .dividends import value_dividends
from .graham import value_graham
from .multiples import value_multiples


def run_valuation(fs: FinancialStatements, current_price: Optional[float],
                  shares: Optional[float], margin_of_safety: float,
                  discount_rate: float, terminal_growth: float) -> ValuationResult:
    net_debt = latest_value(fs.balance.get("net_debt", {}))

    models = [
        value_multiples(fs, current_price, shares),
        value_dcf(fs, shares, net_debt, discount_rate, terminal_growth),
        value_dividends(fs, discount_rate, terminal_growth),
        value_graham(fs, shares),
    ]

    included_values = [m.value_per_share for m in models
                       if m.included and m.value_per_share and m.value_per_share > 0]
    mean_val = mean(included_values) if included_values else None

    result = ValuationResult(
        models=models,
        mean_valuation=round(mean_val, 2) if mean_val else None,
        margin_of_safety=margin_of_safety,
        current_price=current_price,
    )
    if mean_val:
        result.max_buy_price = round(mean_val * (1 - margin_of_safety), 2)
        if current_price and current_price > 0:
            result.upside_vs_price = round(mean_val / current_price - 1, 4)
            result.discount_to_max_buy = round(1 - current_price / result.max_buy_price, 4) \
                if result.max_buy_price else None
    return result
