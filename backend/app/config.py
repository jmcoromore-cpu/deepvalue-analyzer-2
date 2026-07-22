"""Configuración central de la aplicación.

Carga las variables de entorno desde .env usando pydantic-settings.
Todos los parámetros tienen valores por defecto sensatos para que la app
funcione aunque falten claves opcionales.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Localiza el archivo .env de forma robusta, sin depender de desde qué carpeta
# se arranque la app. config.py está en backend/app/config.py, así que:
#   - _BACKEND_DIR = backend/
#   - _ROOT_DIR    = raíz del proyecto (deepvalue-analyzer/)
# Se aceptan .env tanto en la raíz del proyecto como dentro de backend/.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _BACKEND_DIR.parent
_ENV_FILES = (str(_ROOT_DIR / ".env"), str(_BACKEND_DIR / ".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Identidad SEC ---
    sec_identity: str = Field(default="DeepValue Analyzer contact@example.com")

    # --- Gemini ---
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-1.5-flash")

    # --- Alpha Vantage ---
    alphavantage_api_key: str = Field(default="")

    # --- Parámetros de análisis ---
    default_margin_of_safety: float = Field(default=0.20)
    default_discount_rate: float = Field(default=0.09)
    default_terminal_growth: float = Field(default=0.025)
    quant_weight: float = Field(default=0.55)
    qual_weight: float = Field(default=0.45)

    # --- CORS ---
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")

    # --- Caché ---
    cache_ttl: int = Field(default=3600)

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
