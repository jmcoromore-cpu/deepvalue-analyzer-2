"""Fuente de datos SEC EDGAR (solo empresas de EE. UU.).

Usa la API de datos de la SEC (companyconcept / companyfacts) para obtener
históricos anuales (hasta 10+ años). Enriquece los datos de yfinance con más
profundidad histórica cuando la empresa cotiza en EE. UU.

No requiere API key, pero la SEC exige un User-Agent con un correo de contacto
(ver SEC_IDENTITY en .env).
"""
from __future__ import annotations

import math
from typing import Dict, Optional

import requests

from ..config import get_settings
from .base import DataProvider, RawFinancials

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def _safe(v) -> Optional[float]:
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


# Mapa: clave canónica -> lista de conceptos US-GAAP en EDGAR (orden de preferencia)
_GAAP = {
    # balance
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "accounts_receivable": ["AccountsReceivableNetCurrent"],
    "inventories": ["InventoryNet"],
    "total_current_assets": ["AssetsCurrent"],
    "goodwill": ["Goodwill"],
    "intangibles": ["IntangibleAssetsNetExcludingGoodwill", "FiniteLivedIntangibleAssetsNet"],
    "ppe": ["PropertyPlantAndEquipmentNet"],
    "total_assets": ["Assets"],
    "short_term_debt": ["DebtCurrent", "LongTermDebtCurrent"],
    "accounts_payable": ["AccountsPayableCurrent"],
    "total_current_liabilities": ["LiabilitiesCurrent"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "total_liabilities": ["Liabilities"],
    "retained_earnings": ["RetainedEarningsAccumulatedDeficit"],
    "additional_paid_in_capital": ["AdditionalPaidInCapital", "AdditionalPaidInCapitalCommonStock"],
    "total_equity": ["StockholdersEquity"],
    # income
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
    "gross_profit": ["GrossProfit"],
    "sga": ["SellingGeneralAndAdministrativeExpense"],
    "rnd": ["ResearchAndDevelopmentExpense"],
    "ebit": ["OperatingIncomeLoss"],
    "interest_expense": ["InterestExpense"],
    "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"],
    "income_tax": ["IncomeTaxExpenseBenefit"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    # cashflow
    "depreciation_amortization": ["DepreciationDepletionAndAmortization", "DepreciationAmortizationAndAccretionNet"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "investing_cash_flow": ["NetCashProvidedByUsedInInvestingActivities"],
    "dividends_paid": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "stock_repurchased": ["PaymentsForRepurchaseOfCommonStock"],
    "financing_cash_flow": ["NetCashProvidedByUsedInFinancingActivities"],
}

_BALANCE_SET = {"cash", "accounts_receivable", "inventories", "total_current_assets",
                "goodwill", "intangibles", "ppe", "total_assets", "short_term_debt",
                "accounts_payable", "total_current_liabilities", "long_term_debt",
                "total_liabilities", "retained_earnings", "additional_paid_in_capital",
                "total_equity"}
_INCOME_SET = {"revenue", "cogs", "gross_profit", "sga", "rnd", "ebit",
               "interest_expense", "pretax_income", "income_tax", "net_income", "eps_diluted"}
_CASH_SET = {"depreciation_amortization", "operating_cash_flow", "capex",
             "investing_cash_flow", "dividends_paid", "stock_repurchased", "financing_cash_flow"}


class EdgarSource(DataProvider):
    name = "sec_edgar"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.headers = {"User-Agent": self.settings.sec_identity or "DeepValue contact@example.com"}

    def _cik_for_ticker(self, ticker: str) -> Optional[str]:
        try:
            r = requests.get(SEC_TICKERS_URL, headers=self.headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            t = ticker.upper()
            for entry in data.values():
                if entry.get("ticker", "").upper() == t:
                    return str(entry["cik_str"]).zfill(10)
        except Exception:
            return None
        return None

    def _annual_series(self, facts: dict, concepts: list) -> Dict[int, float]:
        """Extrae la serie anual (form 10-K, fp FY) para el primer concepto que exista."""
        usgaap = facts.get("facts", {}).get("us-gaap", {})
        for concept in concepts:
            node = usgaap.get(concept)
            if not node:
                continue
            units = node.get("units", {})
            # elige la unidad con más datos (USD, USD/shares, etc.)
            unit_key = max(units, key=lambda k: len(units[k])) if units else None
            if not unit_key:
                continue
            series: Dict[int, float] = {}
            for item in units[unit_key]:
                if item.get("form") != "10-K":
                    continue
                fy = item.get("fy")
                fp = item.get("fp")
                val = _safe(item.get("val"))
                if fy is None or val is None:
                    continue
                if fp and fp != "FY":
                    continue
                series[int(fy)] = val
            if series:
                return series
        return {}

    def fetch(self, ticker: str) -> RawFinancials:
        raw = RawFinancials(ticker=ticker, source=self.name)
        cik = self._cik_for_ticker(ticker)
        if not cik:
            raw.ok = False
            raw.error = "Ticker no encontrado en SEC (¿empresa no estadounidense?)."
            return raw
        try:
            r = requests.get(SEC_FACTS_URL.format(cik=cik), headers=self.headers, timeout=25)
            r.raise_for_status()
            facts = r.json()
            raw.name = facts.get("entityName")

            for canon, concepts in _GAAP.items():
                series = self._annual_series(facts, concepts)
                if not series:
                    continue
                if canon in _BALANCE_SET:
                    raw.balance[canon] = series
                elif canon in _INCOME_SET:
                    raw.income[canon] = series
                elif canon in _CASH_SET:
                    raw.cashflow[canon] = series

            years = set()
            for block in (raw.balance, raw.income, raw.cashflow):
                for s in block.values():
                    years.update(s.keys())
            raw.years = sorted(years, reverse=True)

            if not raw.years:
                raw.ok = False
                raw.error = "EDGAR no devolvió series anuales utilizables."
        except Exception as exc:  # noqa: BLE001
            raw.ok = False
            raw.error = f"EDGAR error: {exc}"
        return raw
