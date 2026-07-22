from app.core.financials import normalize
from app.core.qualitative.signals import compute_signals, moat_signal_strength
from app.core.ratios import compute_ratios
from app.core.scoring import combine, qual_score, quant_score
from app.core.valuation.engine import run_valuation
from app.core.verdict import build_verdict
from app.core.qualitative.rules import build_rule_based
from app.models.schemas import CompanyProfile


def test_moat_signal_high_quality(raw_testco):
    fs = normalize(raw_testco)
    signals = compute_signals(fs)
    score = moat_signal_strength(signals)
    # TESTCO tiene ROIC y márgenes altos -> moat score elevado
    assert score >= 60


def test_full_scoring_pipeline(raw_testco):
    fs = normalize(raw_testco)
    ratios = compute_ratios(fs)
    val = run_valuation(fs, 10.0, 100.0, 0.20, 0.09, 0.025)
    signals = compute_signals(fs)
    moat = moat_signal_strength(signals)
    profile = CompanyProfile(ticker="TESTCO", name="Test")
    qa = build_rule_based(profile, signals, moat)

    q = quant_score(ratios, val)
    ql = qual_score(moat, qa.management.score, 0.5)
    score = combine(q, ql, 0.55, 0.45)
    assert 0 <= score.final_score <= 100

    verdict = build_verdict(score, val, qa)
    assert verdict.decision.value in ("COMPRAR", "MANTENER", "EVITAR")
    assert verdict.thesis
