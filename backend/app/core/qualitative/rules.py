"""Análisis cualitativo por reglas (fallback sin IA).

Construye una evaluación estructurada de moat, Porter y equipo gestor a partir
de las señales cuantitativas y del perfil de la empresa. Se usa cuando no hay
API key de Gemini, garantizando que la app siempre entregue análisis cualitativo.
"""
from __future__ import annotations

from typing import Dict, Optional

from ...models.schemas import (CompanyProfile, ManagementAnalysis, MoatAnalysis,
                              MoatType, PorterAnalysis, PorterForce,
                              QualitativeAnalysis)


def _strength_label(score: float) -> str:
    if score >= 70:
        return "Fuerte"
    if score >= 45:
        return "Moderada"
    if score >= 25:
        return "Débil"
    return "Ninguna"


def build_rule_based(profile: CompanyProfile, signals: Dict[str, Optional[float]],
                     moat_score: float) -> QualitativeAnalysis:
    roic = signals.get("avg_roic")
    gross = signals.get("avg_gross_margin")
    net = signals.get("avg_net_margin")
    stab = signals.get("net_margin_stability")

    # ---- Moat ----
    overall = "Wide" if moat_score >= 70 else "Narrow" if moat_score >= 45 else "None"
    types = [
        MoatType(name="Activos intangibles (marca/patentes/licencias)",
                 present=(gross or 0) > 0.4,
                 strength=_strength_label((gross or 0) * 150),
                 rationale=("Márgenes brutos elevados sugieren poder de fijación de precios / marca."
                            if (gross or 0) > 0.4 else
                            "Márgenes brutos moderados: sin evidencia clara de pricing power.")),
        MoatType(name="Costes de reemplazo (switching costs)",
                 present=None, strength="Requiere análisis cualitativo",
                 rationale="No inferible solo con datos financieros; evaluar dependencia del cliente."),
        MoatType(name="Efecto red",
                 present=None, strength="Requiere análisis cualitativo",
                 rationale="Depende del modelo de negocio (plataformas, marketplaces)."),
        MoatType(name="Ventajas en costes / economías de escala",
                 present=(roic or 0) > 0.12,
                 strength=_strength_label((roic or 0) * 400),
                 rationale=("ROIC alto y sostenido apunta a ventajas estructurales de coste."
                            if (roic or 0) > 0.12 else
                            "ROIC moderado: sin ventaja de coste evidente.")),
    ]
    moat = MoatAnalysis(
        overall_rating=overall, overall_score=moat_score, types=types,
        summary=(f"Score de moat cuantitativo: {moat_score:.0f}/100 ({overall}). "
                 f"ROIC medio {_pct(roic)}, margen bruto {_pct(gross)}, margen neto {_pct(net)}. "
                 "Los fosos de switching costs y efecto red requieren juicio cualitativo adicional."),
    )

    # ---- Porter (heurística conservadora) ----
    porter = PorterAnalysis(forces=[
        PorterForce(name="Rivalidad entre competidores",
                    intensity="Media", favorable_for_company=None,
                    rationale="Sin datos de cuota de mercado; márgenes estables sugieren rivalidad contenida."
                    if (stab is not None and stab < 0.05) else "Evaluar estructura del sector."),
        PorterForce(name="Amenaza de nuevos entrantes",
                    intensity="Baja" if (roic or 0) > 0.12 else "Media",
                    favorable_for_company=(roic or 0) > 0.12,
                    rationale="Retornos altos sostenidos implican barreras de entrada efectivas."
                    if (roic or 0) > 0.12 else "Retornos moderados: barreras de entrada inciertas."),
        PorterForce(name="Amenaza de sustitutivos / disrupción",
                    intensity="Media", favorable_for_company=None,
                    rationale="Riesgo de disrupción no evaluable con datos financieros; revisar el sector."),
        PorterForce(name="Poder de negociación de clientes",
                    intensity="Media", favorable_for_company=None,
                    rationale="Margen bruto alto sugiere bajo poder del cliente." if (gross or 0) > 0.4
                    else "Margen ajustado puede indicar clientes con poder."),
        PorterForce(name="Poder de negociación de proveedores",
                    intensity="Media", favorable_for_company=None,
                    rationale="Requiere análisis de la cadena de suministro."),
    ], summary="Análisis de Porter preliminar basado en señales financieras. "
               "Para un juicio completo, activa el análisis con IA.")

    # ---- Management ----
    management = ManagementAnalysis(
        capital_allocation="Evaluar reinversión vs dividendos/recompras a la luz del ROIC.",
        alignment="No evaluable sin datos de estructura accionarial y remuneración.",
        operating_skill=("Ejecución sólida: márgenes y retornos consistentes."
                         if (stab is not None and stab < 0.05 and (roic or 0) > 0.1)
                         else "Ejecución mixta o cíclica según la estabilidad de márgenes."),
        integrity="No evaluable con datos financieros; revisar histórico de guidance.",
        score=min(100.0, max(0.0, (roic or 0.08) * 400)),
        summary="Evaluación del equipo gestor limitada sin IA ni datos cualitativos externos.")

    return QualitativeAnalysis(
        moat=moat, porter=porter, management=management,
        business_quality=_business_quality(moat_score, roic, stab),
        ai_generated=False, confidence="Media (basado en reglas cuantitativas)")


def _business_quality(moat_score: float, roic: Optional[float], stab: Optional[float]) -> str:
    if moat_score >= 70 and (roic or 0) > 0.12:
        return "Negocio de alta calidad (Empresa Excelente)"
    if moat_score >= 45:
        return "Negocio de calidad media / cíclico aceptable"
    return "Negocio de calidad baja o difícil de evaluar"


def _pct(v: Optional[float]) -> str:
    return f"{v*100:.1f}%" if v is not None else "n/d"
