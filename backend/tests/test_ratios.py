from app.core.financials import normalize
from app.core.ratios import compute_ratios


def _get(group, name):
    for r in group.ratios:
        if r.name.startswith(name):
            return r
    raise AssertionError(f"ratio {name} no encontrado")


def test_current_ratio(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    cr = _get(ratios.liquidity, "Current Ratio")
    # 400 / 200 = 2.0
    assert abs(cr.latest - 2.0) < 1e-6
    assert cr.light.value == "green"


def test_gross_margin(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    gm = _get(ratios.profitability, "Margen Bruto")
    # (1000-550)/1000 = 0.45
    assert abs(gm.latest - 0.45) < 1e-6
    assert gm.light.value == "green"


def test_net_margin(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    nm = _get(ratios.profitability, "Margen Neto")
    # 184/1000 = 0.184
    assert abs(nm.latest - 0.184) < 1e-6


def test_roe(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    roe = _get(ratios.profitability, "ROE")
    # 184/500 = 0.368
    assert abs(roe.latest - 0.368) < 1e-6


def test_interest_coverage(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    ic = _get(ratios.solvency, "Cobertura de Intereses")
    # 250/20 = 12.5
    assert abs(ic.latest - 12.5) < 1e-6
    assert ic.light.value == "green"


def test_net_debt_derived(raw_testco):
    fs = normalize(raw_testco)
    # net debt = 250 + 50 - 200 = 100
    assert fs.balance["net_debt"][2024] == 100
