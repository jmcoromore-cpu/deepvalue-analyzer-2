from app.core.financials import normalize
from app.core.valuation.engine import run_valuation
from app.core.valuation.graham import value_graham


def test_free_cash_flow(raw_testco):
    fs = normalize(raw_testco)
    # FCF 2024 = 260 + (-80) = 180
    assert fs.cashflow["free_cash_flow"][2024] == 180
    assert abs(fs.cashflow["fcf_per_share"][2024] - 1.8) < 1e-6


def test_graham(raw_testco):
    fs = normalize(raw_testco)
    res = value_graham(fs, shares=100.0)
    # sqrt(22.5 * 1.84 * 5.0) = sqrt(207) ≈ 14.39
    assert res.included
    assert abs(res.value_per_share - 14.39) < 0.1


def test_valuation_engine_runs(raw_testco):
    fs = normalize(raw_testco)
    res = run_valuation(fs, current_price=10.0, shares=100.0,
                        margin_of_safety=0.20, discount_rate=0.09, terminal_growth=0.025)
    assert res.mean_valuation is not None
    assert res.max_buy_price is not None
    # margin of safety aplicado correctamente
    assert abs(res.max_buy_price - res.mean_valuation * 0.8) < 0.01
    # al menos 3 de los 4 modelos deben incluirse con estos datos
    assert sum(1 for m in res.models if m.included) >= 3
