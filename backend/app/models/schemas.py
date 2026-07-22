"""Modelos Pydantic: contrato de datos de la API.

Definen la forma normalizada de todo lo que viaja por el sistema, desde la
extracción de datos hasta la respuesta final del endpoint de análisis.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
#  Estados financieros normalizados
# --------------------------------------------------------------------------- #
class YearlyValue(BaseModel):
    """Una serie temporal de una métrica: {año: valor}."""
    values: Dict[int, Optional[float]] = Field(default_factory=dict)
    yoy: Optional[float] = None          # variación último año
    cagr_5y: Optional[float] = None
    cagr_10y: Optional[float] = None


class FinancialStatements(BaseModel):
    """Todas las partidas normalizadas, cada una como serie {año: valor}."""
    # Metadatos
    years: List[int] = Field(default_factory=list)
    currency: Optional[str] = None
    shares_outstanding: Dict[int, Optional[float]] = Field(default_factory=dict)

    # Series (nombre de partida -> {año: valor})
    balance: Dict[str, Dict[int, Optional[float]]] = Field(default_factory=dict)
    income: Dict[str, Dict[int, Optional[float]]] = Field(default_factory=dict)
    cashflow: Dict[str, Dict[int, Optional[float]]] = Field(default_factory=dict)

    # Derivados con CAGR (para la tabla del frontend)
    derived: Dict[str, YearlyValue] = Field(default_factory=dict)


class CompanyProfile(BaseModel):
    ticker: str
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
    cap_type: Optional[str] = None       # Mega/Large/Mid/Small/Micro Cap
    sources: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
#  Ratios
# --------------------------------------------------------------------------- #
class RatioLight(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"
    NEUTRAL = "neutral"


class Ratio(BaseModel):
    name: str
    series: Dict[int, Optional[float]] = Field(default_factory=dict)
    latest: Optional[float] = None
    formula: str = ""
    optimal_range: str = ""
    light: RatioLight = RatioLight.NEUTRAL
    higher_is_better: Optional[bool] = None
    unit: str = ""                       # "%", "x", "días", ...


class RatioGroup(BaseModel):
    title: str
    ratios: List[Ratio] = Field(default_factory=list)


class RatiosBundle(BaseModel):
    liquidity: RatioGroup
    activity: RatioGroup
    solvency: RatioGroup
    profitability: RatioGroup
    roe_vs_roic_note: Optional[str] = None


# --------------------------------------------------------------------------- #
#  Valoración
# --------------------------------------------------------------------------- #
class ValuationModelResult(BaseModel):
    name: str
    value_per_share: Optional[float] = None
    included: bool = True
    detail: str = ""


class ValuationResult(BaseModel):
    models: List[ValuationModelResult] = Field(default_factory=list)
    mean_valuation: Optional[float] = None
    margin_of_safety: float = 0.20
    max_buy_price: Optional[float] = None
    current_price: Optional[float] = None
    upside_vs_price: Optional[float] = None      # (valoración media / precio) - 1
    discount_to_max_buy: Optional[float] = None  # 1 - precio/precio_max_compra


# --------------------------------------------------------------------------- #
#  Cualitativo
# --------------------------------------------------------------------------- #
class MoatType(BaseModel):
    name: str
    present: Optional[bool] = None
    strength: str = ""       # "Fuerte" / "Moderada" / "Débil" / "Ninguna"
    rationale: str = ""


class MoatAnalysis(BaseModel):
    overall_rating: str = ""             # Wide / Narrow / None
    overall_score: Optional[float] = None
    types: List[MoatType] = Field(default_factory=list)
    summary: str = ""


class PorterForce(BaseModel):
    name: str
    intensity: str = ""      # Alta / Media / Baja (para la empresa: baja = favorable)
    favorable_for_company: Optional[bool] = None
    rationale: str = ""


class PorterAnalysis(BaseModel):
    forces: List[PorterForce] = Field(default_factory=list)
    summary: str = ""


class ManagementAnalysis(BaseModel):
    capital_allocation: str = ""
    alignment: str = ""
    operating_skill: str = ""
    integrity: str = ""
    score: Optional[float] = None
    summary: str = ""


class QualitativeAnalysis(BaseModel):
    moat: MoatAnalysis = Field(default_factory=MoatAnalysis)
    porter: PorterAnalysis = Field(default_factory=PorterAnalysis)
    management: ManagementAnalysis = Field(default_factory=ManagementAnalysis)
    business_quality: str = ""
    ai_generated: bool = False
    confidence: str = ""     # Alta / Media / Baja
    raw_ai_markdown: str = ""


# --------------------------------------------------------------------------- #
#  Scoring y veredicto
# --------------------------------------------------------------------------- #
class Decision(str, Enum):
    BUY = "COMPRAR"
    HOLD = "MANTENER"
    AVOID = "EVITAR"


class ScoreBreakdown(BaseModel):
    quant_score: float = 0.0             # 0-100
    qual_score: float = 0.0              # 0-100
    final_score: float = 0.0             # 0-100
    quant_detail: Dict[str, float] = Field(default_factory=dict)
    qual_detail: Dict[str, float] = Field(default_factory=dict)


class Verdict(BaseModel):
    decision: Decision
    final_score: float
    confidence: str = ""
    thesis: str = ""
    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
#  Respuesta completa
# --------------------------------------------------------------------------- #
class AnalysisResponse(BaseModel):
    profile: CompanyProfile
    financials: FinancialStatements
    ratios: RatiosBundle
    valuation: ValuationResult
    qualitative: QualitativeAnalysis
    scoring: ScoreBreakdown
    verdict: Verdict
    warnings: List[str] = Field(default_factory=list)
    generated_at: str = ""
