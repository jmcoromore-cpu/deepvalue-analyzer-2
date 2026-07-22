"""Normalización de estados financieros.

Convierte el RawFinancials (crudo de las fuentes) en FinancialStatements:
completa partidas derivadas (margen bruto, EBITDA, EBIT, deuda neta, fondo de
maniobra, FCF, FCF/acción) y calcula variación anual, CAGR-5Y y CAGR-10Y,
replicando la lógica de la hoja DATA de la plantilla de valoración original.
"""
from __future__ import annotations

from typing import Dict, Optional

from ..data_sources.base import RawFinancials
from ..models.schemas import FinancialStatements, YearlyValue
from ..utils.math_utils import cagr, latest_value, series_to_sorted, yoy


def _get(block: Dict[str, Dict[int, float]], key: str, year: int) -> Optional[float]:
    return block.get(key, {}).get(year)


def _fill_derived_income(income: Dict[str, Dict[int, float]], years) -> None:
    for y in years:
        rev = _get(income, "revenue", y)
        cogs = _get(income, "cogs", y)
        # Margen bruto
        if income.get("gross_profit", {}).get(y) is None and rev is not None and cogs is not None:
            income.setdefault("gross_profit", {})[y] = rev - cogs
        # EBIT a partir de BAI + gastos financieros si falta
        ebit = _get(income, "ebit", y)
        pretax = _get(income, "pretax_income", y)
        interest = _get(income, "interest_expense", y)
        if ebit is None and pretax is not None and interest is not None:
            income.setdefault("ebit", {})[y] = pretax + abs(interest)


def _fill_derived_balance(balance: Dict[str, Dict[int, float]], years) -> None:
    for y in years:
        # Deuda neta = deuda LP + deuda CP - caja
        ltd = _get(balance, "long_term_debt", y) or 0.0
        std = _get(balance, "short_term_debt", y) or 0.0
        cash = _get(balance, "cash", y) or 0.0
        if any(_get(balance, k, y) is not None for k in ("long_term_debt", "short_term_debt", "cash")):
            balance.setdefault("net_debt", {})[y] = ltd + std - cash
        # Fondo de maniobra = AC - PC
        ac = _get(balance, "total_current_assets", y)
        pc = _get(balance, "total_current_liabilities", y)
        if ac is not None and pc is not None:
            balance.setdefault("working_capital", {})[y] = ac - pc


def _fill_derived_cashflow(cashflow: Dict[str, Dict[int, float]],
                           shares_by_year: Dict[int, float], years) -> None:
    for y in years:
        ocf = _get(cashflow, "operating_cash_flow", y)
        capex = _get(cashflow, "capex", y)
        if ocf is not None and capex is not None:
            # capex suele venir negativo en los cash flows -> sumamos su valor real
            fcf = ocf + capex if capex < 0 else ocf - capex
            cashflow.setdefault("free_cash_flow", {})[y] = fcf
            shares = shares_by_year.get(y)
            if shares:
                cashflow.setdefault("fcf_per_share", {})[y] = fcf / shares


def _yearly(series: Dict[int, Optional[float]]) -> YearlyValue:
    ordered = series_to_sorted(series)
    yv = YearlyValue(values=dict(series))
    if len(ordered) >= 2:
        yv.yoy = yoy(ordered[0][1], ordered[1][1])
    if len(ordered) >= 5:
        yv.cagr_5y = cagr(ordered[0][1], ordered[4][1], 4)
    if len(ordered) >= 10:
        yv.cagr_10y = cagr(ordered[0][1], ordered[9][1], 9)
    return yv


# Partidas que exponemos con CAGR en la tabla "derived" del frontend
_DERIVED_KEYS = {
    "revenue": "income", "gross_profit": "income", "ebitda": "income",
    "ebit": "income", "net_income": "income", "eps_diluted": "income",
    "total_assets": "balance", "total_equity": "balance", "net_debt": "balance",
    "operating_cash_flow": "cashflow", "free_cash_flow": "cashflow",
    "fcf_per_share": "cashflow",
}


def normalize(raw: RawFinancials) -> FinancialStatements:
    fs = FinancialStatements(
        years=raw.years,
        currency=raw.currency,
        shares_outstanding={y: raw.shares_by_year.get(y) for y in raw.years},
        balance={k: dict(v) for k, v in raw.balance.items()},
        income={k: dict(v) for k, v in raw.income.items()},
        cashflow={k: dict(v) for k, v in raw.cashflow.items()},
    )

    # Dividendo por acción desde la serie de dividendos si no viene en income
    if "dividend_per_share" not in fs.income and raw.dividends_by_year:
        fs.income["dividend_per_share"] = dict(raw.dividends_by_year)

    all_years = fs.years or sorted(
        {y for blk in (fs.balance, fs.income, fs.cashflow) for s in blk.values() for y in s},
        reverse=True,
    )

    _fill_derived_income(fs.income, all_years)
    _fill_derived_balance(fs.balance, all_years)
    _fill_derived_cashflow(fs.cashflow, raw.shares_by_year, all_years)

    for key, block_name in _DERIVED_KEYS.items():
        block = getattr(fs, block_name)
        if key in block and block[key]:
            fs.derived[key] = _yearly(block[key])

    return fs


def latest(fs: FinancialStatements, block_name: str, key: str) -> Optional[float]:
    block = getattr(fs, block_name)
    return latest_value(block.get(key, {}))
