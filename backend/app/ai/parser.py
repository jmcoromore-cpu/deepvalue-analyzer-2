"""Convierte el JSON estructurado de la IA en los modelos de la aplicación.

Al recibir el análisis ya estructurado (no texto libre), el mapeo es directo y
fiable: cada campo del JSON va a su lugar, sin adivinanzas ni troceo de texto.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from ..models.schemas import (ManagementAnalysis, MoatAnalysis, MoatType,
                              PorterAnalysis, PorterForce, QualitativeAnalysis)


def _present_to_bool(value) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in ("sí", "si", "true", "yes"):
        return True
    if s in ("no", "false"):
        return False
    return None  # "Parcial" u otros -> indeterminado


def _clean(value) -> str:
    return str(value).strip() if value is not None else ""


def parse_ai_json(data: Dict) -> Tuple[QualitativeAnalysis, str, Optional[List[str]]]:
    """Devuelve (QualitativeAnalysis, tesis, riesgos)."""
    qa = QualitativeAnalysis(ai_generated=True)

    # --- MOAT ---
    moat_data = data.get("moat", {}) or {}
    types = []
    for t in moat_data.get("types", []) or []:
        types.append(MoatType(
            name=_clean(t.get("name")) or "Tipo de foso",
            present=_present_to_bool(t.get("present")),
            strength=_clean(t.get("strength")) or "n/d",
            rationale=_clean(t.get("rationale")),
        ))
    qa.moat = MoatAnalysis(
        overall_rating=_clean(moat_data.get("overall_rating")) or "Narrow",
        summary=_clean(moat_data.get("summary")),
        types=types,
    )

    # --- PORTER ---
    porter_data = data.get("porter", {}) or {}
    forces = []
    for f in porter_data.get("forces", []) or []:
        fav = f.get("favorable_for_company")
        forces.append(PorterForce(
            name=_clean(f.get("name")) or "Fuerza",
            intensity=_clean(f.get("intensity")) or "n/d",
            favorable_for_company=bool(fav) if isinstance(fav, bool) else None,
            rationale=_clean(f.get("rationale")),
        ))
    qa.porter = PorterAnalysis(summary=_clean(porter_data.get("summary")), forces=forces)

    # --- MANAGEMENT ---
    mgmt = data.get("management", {}) or {}
    qa.management = ManagementAnalysis(
        capital_allocation=_clean(mgmt.get("capital_allocation")),
        alignment=_clean(mgmt.get("alignment")),
        operating_skill=_clean(mgmt.get("operating_skill")),
        integrity=_clean(mgmt.get("integrity")),
        summary="",  # vacío a propósito: el frontend muestra los 4 campos detallados
    )

    # --- Calidad, confianza ---
    qa.business_quality = _clean(data.get("business_quality"))
    qa.confidence = _clean(data.get("confidence")) or "Media"

    # --- Tesis y riesgos ---
    thesis = _clean(data.get("thesis"))
    risks_raw = data.get("risks", []) or []
    risks = [_clean(r) for r in risks_raw if _clean(r)]
    return qa, thesis, (risks or None)
