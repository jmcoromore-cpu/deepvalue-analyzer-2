"""Fuente Alpha Vantage (opcional, requiere API key gratuita).

Se usa como complemento: rellena precio, market cap y algunos fundamentales
del OVERVIEW cuando faltan en otras fuentes. Si no hay API key, se desactiva.
"""
from __future__ import annotations

import math
from typing import Optional

import requests

from ..config import get_settings
from .base import DataProvider, RawFinancials

BASE = "https://www.alphavantage.co/query"


def _safe(v) -> Optional[float]:
    try:
        if v in (None, "None", "-", ""):
            return None
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


class AlphaVantageSource(DataProvider):
    name = "alphavantage"

    def __init__(self) -> None:
        self.key = get_settings().alphavantage_api_key.strip()

    @property
    def enabled(self) -> bool:
        return bool(self.key)

    def fetch(self, ticker: str) -> RawFinancials:
        raw = RawFinancials(ticker=ticker, source=self.name)
        if not self.enabled:
            raw.ok = False
            raw.error = "Alpha Vantage desactivado (sin API key)."
            return raw
        try:
            r = requests.get(
                BASE,
                params={"function": "OVERVIEW", "symbol": ticker, "apikey": self.key},
                timeout=20,
            )
            r.raise_for_status()
            data = r.json() or {}
            if not data or "Symbol" not in data:
                raw.ok = False
                raw.error = "Alpha Vantage sin datos (posible límite de peticiones)."
                return raw
            raw.name = data.get("Name")
            raw.sector = data.get("Sector")
            raw.industry = data.get("Industry")
            raw.country = data.get("Country")
            raw.currency = data.get("Currency")
            raw.description = data.get("Description")
            raw.market_cap = _safe(data.get("MarketCapitalization"))
            raw.shares_outstanding = _safe(data.get("SharesOutstanding"))
        except Exception as exc:  # noqa: BLE001
            raw.ok = False
            raw.error = f"Alpha Vantage error: {exc}"
        return raw
