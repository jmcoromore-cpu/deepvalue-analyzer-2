"""Orquestador del análisis completo.

Une todas las piezas: datos -> normalización -> ratios -> valoración ->
señales -> cualitativo (IA o reglas) -> scoring -> veredicto -> respuesta.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..ai.gemini_analyst import GeminiAnalyst
from ..ai.parser import parse_ai_json
from ..config import get_settings
from ..data_sources.aggregator import DataAggregator
from ..models.schemas import (AnalysisResponse, CompanyProfile,
                              QualitativeAnalysis)
from .financials import normalize
from .qualitative.rules import build_rule_based
from .qualitative.signals import compute_signals, moat_signal_strength
from .ratios import compute_ratios
from .scoring import combine, qual_score, quant_score
from .valuation.engine import run_valuation
from .verdict import build_verdict


def _cap_type(mc: Optional[float]) -> Optional[str]:
    if mc is None:
        return None
    if mc > 200e9:
        return "Mega Cap"
    if mc > 10e9:
        return "Large Cap"
    if mc > 2e9:
        return "Mid Cap"
    if mc > 300e6:
        return "Small Cap"
    return "Micro Cap"


class Analyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.aggregator = DataAggregator()
        self.ai = GeminiAnalyst()

    def analyze(self, ticker: str, margin_of_safety: Optional[float] = None,
                discount_rate: Optional[float] = None,
                terminal_growth: Optional[float] = None,
                use_ai: bool = True) -> AnalysisResponse:
        s = self.settings
        mos = margin_of_safety if margin_of_safety is not None else s.default_margin_of_safety
        dr = discount_rate if discount_rate is not None else s.default_discount_rate
        tg = terminal_growth if terminal_growth is not None else s.default_terminal_growth

        warnings: List[str] = []
        raw = self.aggregator.fetch(ticker)
        if not raw.ok:
            raise ValueError(raw.error or f"No se pudieron obtener datos para {ticker}.")
        if raw.source == "none" or not raw.years:
            warnings.append("Cobertura de datos limitada para este ticker.")

        profile = CompanyProfile(
            ticker=raw.ticker, name=raw.name, sector=raw.sector, industry=raw.industry,
            country=raw.country, website=raw.website, currency=raw.currency,
            description=raw.description, market_cap=raw.market_cap,
            shares_outstanding=raw.shares_outstanding, current_price=raw.current_price,
            cap_type=_cap_type(raw.market_cap),
            sources=raw.source.split("+") if raw.source else [],
        )

        fs = normalize(raw)
        ratios = compute_ratios(fs)

        shares = raw.shares_outstanding
        if not shares and raw.market_cap and raw.current_price:
            shares = raw.market_cap / raw.current_price
        valuation = run_valuation(fs, raw.current_price, shares, mos, dr, tg)

        signals = compute_signals(fs)
        moat_score = moat_signal_strength(signals)

        # --- Cualitativo: IA (JSON estructurado) o reglas ---
        qualitative: QualitativeAnalysis
        ai_thesis, ai_risks = "", None
        if use_ai and self.ai.enabled:
            result = self.ai.analyze(profile, signals, valuation)
            if result and result.get("ok"):
                qualitative, ai_thesis, ai_risks = parse_ai_json(result["data"])
                # completa el score cuantitativo del moat en la estructura de la IA
                qualitative.moat.overall_score = moat_score
            else:
                err = (result or {}).get("error", "desconocido")
                warnings.append(f"IA no disponible; se usó análisis por reglas. Error IA: {err}")
                qualitative = build_rule_based(profile, signals, moat_score)
        else:
            if use_ai and not self.ai.enabled:
                warnings.append("Sin GEMINI_API_KEY: veredicto cualitativo generado por reglas.")
            qualitative = build_rule_based(profile, signals, moat_score)

        # --- Scoring ---
        porter_fav = _porter_favorable_ratio(qualitative)
        mgmt_sc = qualitative.management.score
        q_detail = quant_score(ratios, valuation)
        ql_detail = qual_score(qualitative.moat.overall_score or moat_score, mgmt_sc, porter_fav)
        score = combine(q_detail, ql_detail, s.quant_weight, s.qual_weight)

        verdict = build_verdict(score, valuation, qualitative, ai_thesis, ai_risks)

        return AnalysisResponse(
            profile=profile, financials=fs, ratios=ratios, valuation=valuation,
            qualitative=qualitative, scoring=score, verdict=verdict,
            warnings=warnings,
            generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )


def _porter_favorable_ratio(qa: QualitativeAnalysis) -> Optional[float]:
    forces = qa.porter.forces
    if not forces:
        return None
    known = [f.favorable_for_company for f in forces if f.favorable_for_company is not None]
    if not known:
        # deriva de la intensidad: Baja = favorable
        low = sum(1 for f in forces if f.intensity.lower() == "baja")
        return low / len(forces)
    return sum(1 for k in known if k) / len(known)
