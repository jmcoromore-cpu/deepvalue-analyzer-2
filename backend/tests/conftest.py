"""Datos financieros sintéticos de referencia para los tests.

Empresa ficticia 'TESTCO' con cifras redondas y coherentes, para verificar
que ratios y valoraciones se calculan como esperamos.
"""
import pytest

from app.data_sources.base import RawFinancials


@pytest.fixture
def raw_testco() -> RawFinancials:
    years = [2024, 2023, 2022, 2021, 2020]
    raw = RawFinancials(ticker="TESTCO", source="test", name="Test Company",
                        sector="Technology", currency="USD",
                        market_cap=1000.0, shares_outstanding=100.0, current_price=10.0,
                        years=years)
    raw.shares_by_year = {y: 100.0 for y in years}

    # Balance (crece 5%/año hacia atrás)
    raw.balance = {
        "cash":                    {2024: 200, 2023: 190, 2022: 180, 2021: 170, 2020: 160},
        "accounts_receivable":     {2024: 100, 2023: 95,  2022: 90,  2021: 85,  2020: 80},
        "inventories":             {2024: 50,  2023: 48,  2022: 46,  2021: 44,  2020: 42},
        "total_current_assets":    {2024: 400, 2023: 380, 2022: 360, 2021: 340, 2020: 320},
        "goodwill":                {2024: 30,  2023: 30,  2022: 30,  2021: 30,  2020: 30},
        "ppe":                     {2024: 600, 2023: 560, 2022: 520, 2021: 480, 2020: 440},
        "total_assets":            {2024: 1000, 2023: 950, 2022: 900, 2021: 850, 2020: 800},
        "short_term_debt":         {2024: 50,  2023: 50,  2022: 50,  2021: 50,  2020: 50},
        "accounts_payable":        {2024: 80,  2023: 76,  2022: 72,  2021: 68,  2020: 64},
        "total_current_liabilities":{2024: 200, 2023: 190, 2022: 180, 2021: 170, 2020: 160},
        "long_term_debt":          {2024: 250, 2023: 250, 2022: 250, 2021: 250, 2020: 250},
        "total_liabilities":       {2024: 500, 2023: 480, 2022: 460, 2021: 440, 2020: 420},
        "total_equity":            {2024: 500, 2023: 470, 2022: 440, 2021: 410, 2020: 380},
    }
    raw.income = {
        "revenue":          {2024: 1000, 2023: 920, 2022: 850, 2021: 790, 2020: 740},
        "cogs":             {2024: 550,  2023: 510, 2022: 475, 2021: 445, 2020: 420},
        "sga":              {2024: 150,  2023: 140, 2022: 130, 2021: 120, 2020: 115},
        "ebit":             {2024: 250,  2023: 225, 2022: 205, 2021: 190, 2020: 175},
        "interest_expense": {2024: 20,   2023: 20,  2022: 20,  2021: 20,  2020: 20},
        "pretax_income":    {2024: 230,  2023: 205, 2022: 185, 2021: 170, 2020: 155},
        "income_tax":       {2024: 46,   2023: 41,  2022: 37,  2021: 34,  2020: 31},
        "net_income":       {2024: 184,  2023: 164, 2022: 148, 2021: 136, 2020: 124},
        "eps_diluted":      {2024: 1.84, 2023: 1.64, 2022: 1.48, 2021: 1.36, 2020: 1.24},
        "dividend_per_share":{2024: 0.50, 2023: 0.45, 2022: 0.40, 2021: 0.36, 2020: 0.32},
    }
    raw.cashflow = {
        "operating_cash_flow": {2024: 260, 2023: 235, 2022: 210, 2021: 195, 2020: 180},
        "capex":               {2024: -80, 2023: -75, 2022: -70, 2021: -65, 2020: -60},
        "depreciation_amortization": {2024: 50, 2023: 47, 2022: 44, 2021: 41, 2020: 38},
        "dividends_paid":      {2024: -50, 2023: -45, 2022: -40, 2021: -36, 2020: -32},
    }
    raw.dividends_by_year = {2024: 0.50, 2023: 0.45, 2022: 0.40, 2021: 0.36, 2020: 0.32}
    return raw
