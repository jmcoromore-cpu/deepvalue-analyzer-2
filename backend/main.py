"""DeepValue Analyzer — API FastAPI.

Expone el endpoint de análisis fundamental a partir del ticker.
Documentación interactiva en /docs.
"""
from __future__ import annotations

from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.analyzer import Analyzer
from app.models.schemas import AnalysisResponse

settings = get_settings()

app = FastAPI(
    title="DeepValue Analyzer API",
    description="Análisis fundamental exhaustivo de empresas cotizadas a partir de su ticker.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_analyzer = Analyzer()
_cache: TTLCache = TTLCache(maxsize=256, ttl=settings.cache_ttl)


@app.get("/health")
def health():
    return {"status": "ok", "ai_enabled": settings.ai_enabled}


@app.get("/api/analyze/{ticker}", response_model=AnalysisResponse)
def analyze(
    ticker: str,
    margin_of_safety: float = Query(default=None, ge=0, le=0.9),
    discount_rate: float = Query(default=None, gt=0, le=0.5),
    terminal_growth: float = Query(default=None, ge=0, le=0.1),
    use_ai: bool = Query(default=True),
    refresh: bool = Query(default=False),
):
    """Devuelve el análisis fundamental completo de la empresa."""
    ticker = ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="El ticker no puede estar vacío.")

    cache_key = f"{ticker}|{margin_of_safety}|{discount_rate}|{terminal_growth}|{use_ai}"
    if not refresh and cache_key in _cache:
        return _cache[cache_key]

    try:
        result = _analyzer.analyze(
            ticker,
            margin_of_safety=margin_of_safety,
            discount_rate=discount_rate,
            terminal_growth=terminal_growth,
            use_ai=use_ai,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}")

    _cache[cache_key] = result
    return result


@app.get("/")
def root():
    return {
        "name": "DeepValue Analyzer",
        "docs": "/docs",
        "example": "/api/analyze/AAPL",
    }
