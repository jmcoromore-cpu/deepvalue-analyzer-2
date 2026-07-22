"""Fuente de datos yfinance (Yahoo Finance).

Cobertura mundial. Fuente primaria del sistema. Mapea los estados financieros
anuales de Yahoo a las claves canónicas de base.py.
"""
from __future__ import annotations

import math
from typing import Dict, Optional

from .base import DataProvider, RawFinancials


def _safe(v) -> Optional[float]:
    try:
        if v is None:
            return None
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


# Mapa: clave canónica -> lista de posibles etiquetas de yfinance (en orden de preferencia)
_BALANCE_MAP = {
    "cash": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
    "accounts_receivable": ["Accounts Receivable", "Receivables"],
    "inventories": ["Inventory"],
    "total_current_assets": ["Current Assets"],
    "intangibles": ["Other Intangible Assets", "Goodwill And Other Intangible Assets"],
    "goodwill": ["Goodwill"],
    "ppe": ["Net PPE", "Gross PPE"],
    "total_assets": ["Total Assets"],
    "short_term_debt": ["Current Debt", "Current Debt And Capital Lease Obligation"],
    "accounts_payable": ["Accounts Payable", "Payables"],
    "total_current_liabilities": ["Current Liabilities"],
    "long_term_debt": ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"],
    "total_liabilities": ["Total Liabilities Net Minority Interest", "Total Liabilities"],
    "retained_earnings": ["Retained Earnings"],
    "treasury_stock": ["Treasury Stock"],
    "additional_paid_in_capital": ["Additional Paid In Capital", "Capital Stock"],
    "total_equity": ["Stockholders Equity", "Total Equity Gross Minority Interest"],
}
_INCOME_MAP = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "cogs": ["Cost Of Revenue"],
    "gross_profit": ["Gross Profit"],
    "sga": ["Selling General And Administration", "Selling General And Administrative"],
    "rnd": ["Research And Development"],
    "ebitda": ["EBITDA", "Normalized EBITDA"],
    "ebit": ["EBIT", "Operating Income"],
    "interest_expense": ["Interest Expense"],
    "pretax_income": ["Pretax Income"],
    "income_tax": ["Tax Provision"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "eps_diluted": ["Diluted EPS"],
}
_CASHFLOW_MAP = {
    "operating_income": ["Operating Income", "Net Income From Continuing Operations"],
    "depreciation_amortization": ["Depreciation And Amortization", "Depreciation Amortization Depletion"],
    "operating_cash_flow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
    "capex": ["Capital Expenditure", "Purchase Of PPE"],
    "investing_cash_flow": ["Investing Cash Flow"],
    "debt_issued": ["Issuance Of Debt", "Long Term Debt Issuance"],
    "debt_repaid": ["Repayment Of Debt", "Long Term Debt Payments"],
    "stock_repurchased": ["Repurchase Of Capital Stock"],
    "dividends_paid": ["Cash Dividends Paid", "Common Stock Dividend Paid"],
    "financing_cash_flow": ["Financing Cash Flow"],
}


def _extract(df, label_map: Dict[str, list]) -> Dict[str, Dict[int, float]]:
    out: Dict[str, Dict[int, float]] = {}
    if df is None or getattr(df, "empty", True):
        return out
    index = {str(i): i for i in df.index}
    for canon, labels in label_map.items():
        for label in labels:
            if label in index:
                row = df.loc[index[label]]
                series: Dict[int, float] = {}
                for col, val in row.items():
                    year = getattr(col, "year", None)
                    v = _safe(val)
                    if year is not None and v is not None:
                        series[int(year)] = v
                if series:
                    out[canon] = series
                    break
    return out


class YFinanceSource(DataProvider):
    name = "yfinance"

    def fetch(self, ticker: str) -> RawFinancials:
        raw = RawFinancials(ticker=ticker, source=self.name)
        try:
            import yfinance as yf

            tk = yf.Ticker(ticker)
            info = {}
            try:
                info = tk.get_info() or {}
            except Exception:
                info = getattr(tk, "info", {}) or {}

            raw.name = info.get("longName") or info.get("shortName")
            raw.sector = info.get("sector")
            raw.industry = info.get("industry")
            raw.country = info.get("country")
            raw.website = info.get("website")
            raw.currency = info.get("financialCurrency") or info.get("currency")
            raw.description = info.get("longBusinessSummary")
            raw.market_cap = _safe(info.get("marketCap"))
            raw.shares_outstanding = _safe(info.get("sharesOutstanding"))
            raw.current_price = _safe(
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("previousClose")
            )

            raw.balance = _extract(tk.balance_sheet, _BALANCE_MAP)
            raw.income = _extract(tk.income_stmt, _INCOME_MAP)
            raw.cashflow = _extract(tk.cashflow, _CASHFLOW_MAP)

            # Dividendo por acción por año (a partir de la serie de dividendos)
            try:
                divs = tk.dividends
                if divs is not None and not divs.empty:
                    by_year: Dict[int, float] = {}
                    for date, amount in divs.items():
                        y = getattr(date, "year", None)
                        a = _safe(amount)
                        if y is not None and a is not None:
                            by_year[int(y)] = by_year.get(int(y), 0.0) + a
                    raw.dividends_by_year = by_year
            except Exception:
                pass

            # Años disponibles (unión de los tres estados)
            years = set()
            for block in (raw.balance, raw.income, raw.cashflow):
                for series in block.values():
                    years.update(series.keys())
            raw.years = sorted(years, reverse=True)

            # Nº de acciones por año (aprox.: shares_outstanding constante como fallback)
            if raw.shares_outstanding:
                for y in raw.years:
                    raw.shares_by_year[y] = raw.shares_outstanding

            if not raw.years and not raw.name:
                raw.ok = False
                raw.error = "yfinance no devolvió datos para el ticker."
        except Exception as exc:  # noqa: BLE001
            raw.ok = False
            raw.error = f"yfinance error: {exc}"
        return raw
