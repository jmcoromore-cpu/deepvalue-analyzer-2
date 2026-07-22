"""Parser del informe Markdown de Gemini a estructura tipada.

Extrae secciones (MOAT, PORTER, EQUIPO_GESTOR, etc.) y las mapea a los modelos
Pydantic. Es tolerante: si el modelo no sigue el formato, conserva el texto crudo.
"""
from __future__ import annotations

import re
from typing import Dict, List

from ..models.schemas import (ManagementAnalysis, MoatAnalysis, MoatType,
                              PorterAnalysis, PorterForce, QualitativeAnalysis)


def _split_sections(md: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current = None
    buf: List[str] = []
    for line in md.splitlines():
        m = re.match(r"^#+\s*([A-ZÁÉÍÓÚÑ_]+)", line.strip())
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).upper()
            buf = []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def parse_ai_markdown(md: str) -> QualitativeAnalysis:
    qa = QualitativeAnalysis(ai_generated=True, raw_ai_markdown=md)
    sections = _split_sections(md)

    # MOAT
    moat_txt = sections.get("MOAT", "")
    rating = "Narrow"
    rm = re.search(r"MOAT_GLOBAL:\s*(Wide|Narrow|None)", moat_txt, re.IGNORECASE)
    if rm:
        rating = rm.group(1).capitalize()
    qa.moat = MoatAnalysis(overall_rating=rating, summary=moat_txt[:900],
                           types=_parse_moat_types(moat_txt))

    # PORTER
    porter_txt = sections.get("PORTER", "")
    qa.porter = PorterAnalysis(summary=porter_txt[:900], forces=_parse_porter(porter_txt))

    # MANAGEMENT
    mgmt_txt = sections.get("EQUIPO_GESTOR", "") or sections.get("EQUIPO", "")
    qa.management = ManagementAnalysis(summary=mgmt_txt[:900])

    # CALIDAD
    qa.business_quality = sections.get("CALIDAD_NEGOCIO", "").split("\n")[0][:200] \
        if sections.get("CALIDAD_NEGOCIO") else ""

    # CONFIANZA
    conf_txt = sections.get("CONFIANZA", "")
    cm = re.search(r"CONFIANZA:\s*(Alta|Media|Baja)", conf_txt, re.IGNORECASE)
    qa.confidence = cm.group(1).capitalize() if cm else "Media"

    return qa, sections


def _parse_moat_types(txt: str) -> List[MoatType]:
    known = [
        ("Activos intangibles", ["intangible", "marca", "patente", "licencia"]),
        ("Costes de reemplazo", ["reemplazo", "switching", "cautiv"]),
        ("Efecto red", ["efecto red", "network"]),
        ("Ventajas en costes", ["coste", "escala"]),
    ]
    out = []
    low = txt.lower()
    for name, kws in known:
        idx = min([low.find(k) for k in kws if low.find(k) >= 0] or [-1])
        rationale = ""
        strength = ""
        if idx >= 0:
            snippet = txt[idx:idx + 240]
            rationale = snippet.replace("\n", " ").strip()
            sm = re.search(r"(Fuerte|Moderada|D[ée]bil|Ninguna)", snippet, re.IGNORECASE)
            if sm:
                strength = sm.group(1)
        out.append(MoatType(name=name, strength=strength or "n/d", rationale=rationale))
    return out


def _parse_porter(txt: str) -> List[PorterForce]:
    forces = [
        ("Rivalidad entre competidores", ["rivalidad", "competidores"]),
        ("Amenaza de nuevos entrantes", ["entrantes", "barreras"]),
        ("Amenaza de sustitutivos", ["sustitut", "disrupci"]),
        ("Poder de clientes", ["clientes"]),
        ("Poder de proveedores", ["proveedores"]),
    ]
    out = []
    low = txt.lower()
    for name, kws in forces:
        idx = min([low.find(k) for k in kws if low.find(k) >= 0] or [-1])
        rationale, intensity = "", ""
        if idx >= 0:
            snippet = txt[idx:idx + 220]
            rationale = snippet.replace("\n", " ").strip()
            im = re.search(r"(Alta|Media|Baja)", snippet, re.IGNORECASE)
            if im:
                intensity = im.group(1).capitalize()
        out.append(PorterForce(name=name, intensity=intensity or "n/d", rationale=rationale))
    return out


def extract_thesis_risks(sections: Dict[str, str]):
    thesis = sections.get("TESIS", "").strip()
    risks_txt = sections.get("RIESGOS", "")
    risks = []
    for line in risks_txt.splitlines():
        s = line.strip("-•* ").strip()
        if s and len(s) > 3:
            risks.append(s)
    return thesis, risks[:8]
