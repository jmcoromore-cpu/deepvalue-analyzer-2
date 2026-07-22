"""Cálculo de ratios financieros.

Replica la hoja RATIOS de la plantilla: liquidez, actividad, solvencia y
rentabilidad, cada uno con su fórmula, rango óptimo y un semáforo
(verde/ámbar/rojo) basado en umbrales. Incluye el chequeo ROE vs ROIC.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from ..models.schemas import (FinancialStatements, Ratio, RatioGroup,
                              RatioLight, RatiosBundle)
from ..utils.math_utils import safe_div


def _series(fs: FinancialStatements, block: str, key: str) -> Dict[int, Optional[float]]:
    return getattr(fs, block).get(key, {})


def _g(fs, block, key, year):
    return getattr(fs, block).get(key, {}).get(year)


def _light_threshold(value: Optional[float], green, amber, higher_is_better: bool) -> RatioLight:
    """Aplica umbrales. green/amber son los cortes."""
    if value is None:
        return RatioLight.NEUTRAL
    if higher_is_better:
        if value >= green:
            return RatioLight.GREEN
        if value >= amber:
            return RatioLight.AMBER
        return RatioLight.RED
    else:
        if value <= green:
            return RatioLight.GREEN
        if value <= amber:
            return RatioLight.AMBER
        return RatioLight.RED


def _build_ratio(fs, name, formula, optimal, unit, higher, calc: Callable[[int], Optional[float]],
                 green=None, amber=None, band: Optional[tuple] = None) -> Ratio:
    series: Dict[int, Optional[float]] = {}
    for y in fs.years:
        series[y] = calc(y)
    latest = None
    for y in sorted(series, reverse=True):
        if series[y] is not None:
            latest = series[y]
            break
    if band is not None:
        # band = (min_ok, max_ok): verde dentro de la banda, ámbar cerca, rojo lejos
        lo, hi = band
        if latest is None:
            light = RatioLight.NEUTRAL
        elif lo <= latest <= hi:
            light = RatioLight.GREEN
        elif lo * 0.7 <= latest <= hi * 1.3:
            light = RatioLight.AMBER
        else:
            light = RatioLight.RED
    elif green is not None and amber is not None:
        light = _light_threshold(latest, green, amber, higher)
    else:
        light = RatioLight.NEUTRAL
    return Ratio(name=name, series=series, latest=latest, formula=formula,
                 optimal_range=optimal, light=light, higher_is_better=higher, unit=unit)


def compute_ratios(fs: FinancialStatements) -> RatiosBundle:
    # ---------------- Liquidez ----------------
    liquidity = RatioGroup(title="Liquidez", ratios=[
        _build_ratio(fs, "Current Ratio", "Activo Corriente / Pasivo Corriente",
                     "min 1 / ópt 1,5-2", "x", True,
                     lambda y: safe_div(_g(fs, "balance", "total_current_assets", y),
                                        _g(fs, "balance", "total_current_liabilities", y)),
                     green=1.5, amber=1.0),
        _build_ratio(fs, "Acid Test (prueba ácida)",
                     "(Activo Corriente − Inventarios) / Pasivo Corriente",
                     "min 0,8 / ópt 1,5", "x", True,
                     lambda y: safe_div(
                         (_g(fs, "balance", "total_current_assets", y) or 0)
                         - (_g(fs, "balance", "inventories", y) or 0),
                         _g(fs, "balance", "total_current_liabilities", y)),
                     green=1.0, amber=0.8),
        _build_ratio(fs, "Cash Ratio", "Caja / Pasivo Corriente",
                     "min 0,2 / ópt 0,3", "x", True,
                     lambda y: safe_div(_g(fs, "balance", "cash", y),
                                        _g(fs, "balance", "total_current_liabilities", y)),
                     green=0.3, amber=0.2),
    ])

    # ---------------- Actividad (días, menos es mejor) ----------------
    activity = RatioGroup(title="Actividad", ratios=[
        _build_ratio(fs, "Días de Activos", "Activo Total / Ventas × 365",
                     "cuanto menor, mejor", "días", False,
                     lambda y: (safe_div(_g(fs, "balance", "total_assets", y),
                                         _g(fs, "income", "revenue", y)) or 0) * 365
                     if _g(fs, "income", "revenue", y) else None,
                     green=365, amber=730),
        _build_ratio(fs, "Días de Cobro", "Cuentas a cobrar / Ventas × 365",
                     "cuanto menor, mejor", "días", False,
                     lambda y: (safe_div(_g(fs, "balance", "accounts_receivable", y),
                                         _g(fs, "income", "revenue", y)) or 0) * 365
                     if _g(fs, "income", "revenue", y) else None,
                     green=60, amber=120),
        _build_ratio(fs, "Días de Pago", "Cuentas a pagar / Coste ventas × 365",
                     "cuanto mayor, mejor", "días", True,
                     lambda y: (safe_div(_g(fs, "balance", "accounts_payable", y),
                                         _g(fs, "income", "cogs", y)) or 0) * 365
                     if _g(fs, "income", "cogs", y) else None),
        _build_ratio(fs, "Rotación de Inventario", "Inventarios / Coste ventas × 365",
                     "cuanto menor, mejor", "días", False,
                     lambda y: (safe_div(_g(fs, "balance", "inventories", y),
                                         _g(fs, "income", "cogs", y)) or 0) * 365
                     if _g(fs, "income", "cogs", y) else None,
                     green=60, amber=120),
    ])

    # ---------------- Solvencia ----------------
    solvency = RatioGroup(title="Solvencia", ratios=[
        _build_ratio(fs, "Debt Ratio", "Pasivo Total / Activo Total",
                     "ópt 50-70%", "%", False,
                     lambda y: safe_div(_g(fs, "balance", "total_liabilities", y),
                                        _g(fs, "balance", "total_assets", y)),
                     band=(0.5, 0.7)),
        _build_ratio(fs, "Coef. Endeudamiento", "Pasivo Total / Patrimonio Neto",
                     "ópt 1,5-2", "x", False,
                     lambda y: safe_div(_g(fs, "balance", "total_liabilities", y),
                                        _g(fs, "balance", "total_equity", y)),
                     band=(1.0, 2.0)),
        _build_ratio(fs, "Calidad de la Deuda", "Deuda CP / Deuda Total",
                     "ópt 20-40% (menor mejor)", "%", False,
                     lambda y: safe_div(
                         _g(fs, "balance", "short_term_debt", y),
                         (_g(fs, "balance", "short_term_debt", y) or 0)
                         + (_g(fs, "balance", "long_term_debt", y) or 0)),
                     green=0.4, amber=0.6),
        _build_ratio(fs, "Cobertura de Intereses", "EBIT / Gastos financieros",
                     "> 4-5×, riesgo < 1,5", "x", True,
                     lambda y: safe_div(_g(fs, "income", "ebit", y),
                                        abs(_g(fs, "income", "interest_expense", y))
                                        if _g(fs, "income", "interest_expense", y) else None),
                     green=5.0, amber=2.0),
        _build_ratio(fs, "Deuda Neta / EBIT", "Deuda Neta / EBIT",
                     "cuanto menor, mejor (< 3)", "x", False,
                     lambda y: safe_div(_g(fs, "balance", "net_debt", y),
                                        _g(fs, "income", "ebit", y)),
                     green=3.0, amber=5.0),
    ])

    # ---------------- Rentabilidad ----------------
    profitability = RatioGroup(title="Rentabilidad", ratios=[
        _build_ratio(fs, "Margen Bruto", "(Ventas − Coste ventas) / Ventas",
                     "cuanto mayor, ópt 40%", "%", True,
                     lambda y: safe_div(
                         (_g(fs, "income", "revenue", y) or 0) - (_g(fs, "income", "cogs", y) or 0),
                         _g(fs, "income", "revenue", y)),
                     green=0.40, amber=0.20),
        _build_ratio(fs, "Margen Neto", "Beneficio Neto / Ventas",
                     "cuanto mayor, ópt 10%", "%", True,
                     lambda y: safe_div(_g(fs, "income", "net_income", y),
                                        _g(fs, "income", "revenue", y)),
                     green=0.10, amber=0.05),
        _build_ratio(fs, "ROA", "Beneficio Neto / Activos",
                     "cuanto mayor, mejor", "%", True,
                     lambda y: safe_div(_g(fs, "income", "net_income", y),
                                        _g(fs, "balance", "total_assets", y)),
                     green=0.07, amber=0.03),
        _build_ratio(fs, "ROE", "Beneficio Neto / Patrimonio Neto",
                     "cuanto mayor, mejor", "%", True,
                     lambda y: safe_div(_g(fs, "income", "net_income", y),
                                        _g(fs, "balance", "total_equity", y)),
                     green=0.15, amber=0.08),
        _build_ratio(fs, "ROCE", "EBIT / (Activos − Pasivo Corriente)",
                     "cuanto mayor, mejor", "%", True,
                     lambda y: safe_div(
                         _g(fs, "income", "ebit", y),
                         (_g(fs, "balance", "total_assets", y) or 0)
                         - (_g(fs, "balance", "total_current_liabilities", y) or 0)),
                     green=0.15, amber=0.08),
        _build_ratio(fs, "ROIC", "EBIT·(1−t) / (Patrimonio + Deuda Neta)",
                     "cuanto mayor, mejor (> WACC)", "%", True,
                     lambda y: _roic(fs, y),
                     green=0.12, amber=0.07),
    ])

    bundle = RatiosBundle(liquidity=liquidity, activity=activity,
                          solvency=solvency, profitability=profitability)
    bundle.roe_vs_roic_note = _roe_vs_roic_note(fs)
    return bundle


def _roic(fs: FinancialStatements, year: int) -> Optional[float]:
    ebit = _g(fs, "income", "ebit", year)
    pretax = _g(fs, "income", "pretax_income", year)
    tax = _g(fs, "income", "income_tax", year)
    equity = _g(fs, "balance", "total_equity", year)
    net_debt = _g(fs, "balance", "net_debt", year)
    if ebit is None or equity is None:
        return None
    tax_rate = 0.0
    if pretax and tax and pretax != 0:
        tax_rate = max(0.0, min(0.5, tax / pretax))
    invested = equity + (net_debt or 0)
    return safe_div(ebit * (1 - tax_rate), invested)


def _roe_vs_roic_note(fs: FinancialStatements) -> Optional[str]:
    """Chequeo de la diapositiva 192 del curso."""
    years = sorted(fs.years, reverse=True)[:3]
    roe_vals, roic_vals = [], []
    for y in years:
        ni = _g(fs, "income", "net_income", y)
        eq = _g(fs, "balance", "total_equity", y)
        roe = safe_div(ni, eq)
        roic = _roic(fs, y)
        if roe is not None:
            roe_vals.append(roe)
        if roic is not None:
            roic_vals.append(roic)
    if not roe_vals or not roic_vals:
        return None
    roe = sum(roe_vals) / len(roe_vals)
    roic = sum(roic_vals) / len(roic_vals)
    if roe > roic * 1.15:
        return ("ROE > ROIC de forma persistente: el retorno del accionista se apoya en "
                "APALANCAMIENTO. Sostenible si el negocio es robusto; arriesgado si es de baja calidad.")
    if roic > roe * 1.15:
        return ("ROIC > ROE de forma persistente: la empresa ACUMULA CAJA. Puede indicar gran "
                "robustez (caja neta excedentaria) o una posible mala asignación de capital.")
    return "ROE y ROIC alineados: estructura de retorno equilibrada."
