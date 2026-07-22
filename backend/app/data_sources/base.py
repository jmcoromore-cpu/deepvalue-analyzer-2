"""Interfaz abstracta para las fuentes de datos financieros.

Cada fuente concreta (yfinance, EDGAR, Alpha Vantage) implementa este contrato
y devuelve un RawFinancials con la mayor cantidad de campos que pueda rellenar.
El aggregator las combina.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Claves canónicas de partidas (nombres internos usados en todo el sistema).
# Cada fuente debe mapear sus datos a estas claves.
BALANCE_KEYS = [
    "cash", "accounts_receivable", "inventories", "total_current_assets",
    "intangibles", "goodwill", "ppe", "total_assets",
    "short_term_debt", "accounts_payable", "total_current_liabilities",
    "long_term_debt", "total_liabilities",
    "retained_earnings", "treasury_stock", "additional_paid_in_capital", "total_equity",
]
INCOME_KEYS = [
    "revenue", "cogs", "gross_profit", "sga", "rnd", "ebitda", "ebit",
    "interest_expense", "pretax_income", "income_tax", "net_income",
    "eps_diluted", "dividend_per_share",
]
CASHFLOW_KEYS = [
    "operating_income", "depreciation_amortization", "operating_cash_flow",
    "capex", "investing_cash_flow", "debt_issued", "debt_repaid",
    "stock_repurchased", "dividends_paid", "financing_cash_flow",
]


@dataclass
class RawFinancials:
    """Datos crudos de una fuente, ya mapeados a claves canónicas.

    Cada diccionario tiene la forma  {clave_canonica: {año: valor}}.
    """
    ticker: str
    source: str
    # Perfil
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None
    # Series
    balance: Dict[str, Dict[int, float]] = field(default_factory=dict)
    income: Dict[str, Dict[int, float]] = field(default_factory=dict)
    cashflow: Dict[str, Dict[int, float]] = field(default_factory=dict)
    shares_by_year: Dict[int, float] = field(default_factory=dict)
    price_by_year: Dict[int, float] = field(default_factory=dict)
    dividends_by_year: Dict[int, float] = field(default_factory=dict)
    years: List[int] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None


class DataProvider(ABC):
    """Contrato de una fuente de datos."""

    name: str = "base"

    @abstractmethod
    def fetch(self, ticker: str) -> RawFinancials:
        """Devuelve los datos crudos de la empresa. No debe lanzar: si falla,
        devuelve RawFinancials(ok=False, error=...)."""
        raise NotImplementedError
