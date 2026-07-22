"""Agregador de fuentes.

Combina las distintas fuentes en un único RawFinancials, dando prioridad a la
fuente con más profundidad histórica para las series y completando huecos con
las demás. También decide el orden de preferencia según el mercado del ticker.
"""
from __future__ import annotations

from typing import Dict, List

from .alphavantage_source import AlphaVantageSource
from .base import RawFinancials
from .edgar_source import EdgarSource
from .yfinance_source import YFinanceSource


def _looks_us(ticker: str) -> bool:
    """Heurística: los tickers con punto (IBE.MC, BMW.DE) no son de EE. UU."""
    return "." not in ticker and "-" not in ticker[1:]


def _merge_series(primary: Dict[str, Dict[int, float]],
                  secondary: Dict[str, Dict[int, float]]) -> Dict[str, Dict[int, float]]:
    out: Dict[str, Dict[int, float]] = {k: dict(v) for k, v in primary.items()}
    for key, series in secondary.items():
        if key not in out:
            out[key] = dict(series)
        else:
            for year, val in series.items():
                out[key].setdefault(year, val)
    return out


class DataAggregator:
    def __init__(self) -> None:
        self.yf = YFinanceSource()
        self.edgar = EdgarSource()
        self.av = AlphaVantageSource()

    def fetch(self, ticker: str) -> RawFinancials:
        ticker = ticker.strip().upper()
        warnings: List[str] = []

        yf_data = self.yf.fetch(ticker)

        edgar_data = None
        if _looks_us(ticker):
            edgar_data = self.edgar.fetch(ticker)

        # Base: la fuente con más años de histórico entre yfinance y EDGAR.
        base = yf_data
        other = edgar_data
        if edgar_data and edgar_data.ok and len(edgar_data.years) > len(yf_data.years):
            base, other = edgar_data, yf_data

        merged = RawFinancials(ticker=ticker, source=base.source)
        merged.balance = dict(base.balance)
        merged.income = dict(base.income)
        merged.cashflow = dict(base.cashflow)
        merged.dividends_by_year = dict(base.dividends_by_year)
        merged.shares_by_year = dict(base.shares_by_year)

        # Perfil: preferimos yfinance (más rico) y completamos con lo demás.
        profile_order = [yf_data, edgar_data, self.av.fetch(ticker) if self.av.enabled else None]
        used_sources: List[str] = []
        for src in profile_order:
            if not src or not src.ok:
                continue
            used_sources.append(src.source)
            for attr in ("name", "sector", "industry", "country", "website",
                         "currency", "description", "market_cap",
                         "shares_outstanding", "current_price"):
                if getattr(merged, attr) in (None, "") and getattr(src, attr) not in (None, ""):
                    setattr(merged, attr, getattr(src, attr))

        # Combina series con la otra fuente principal (rellena huecos).
        if other and other.ok:
            merged.balance = _merge_series(merged.balance, other.balance)
            merged.income = _merge_series(merged.income, other.income)
            merged.cashflow = _merge_series(merged.cashflow, other.cashflow)
            if not merged.dividends_by_year:
                merged.dividends_by_year = dict(other.dividends_by_year)

        years = set()
        for block in (merged.balance, merged.income, merged.cashflow):
            for s in block.values():
                years.update(s.keys())
        merged.years = sorted(years, reverse=True)[:10]

        if not merged.shares_by_year and merged.shares_outstanding:
            for y in merged.years:
                merged.shares_by_year[y] = merged.shares_outstanding

        merged.ok = bool(merged.years) or bool(merged.name)
        if not merged.ok:
            merged.error = yf_data.error or "No se pudieron obtener datos para este ticker."
        merged.source = "+".join(dict.fromkeys(used_sources)) or "none"
        return merged
