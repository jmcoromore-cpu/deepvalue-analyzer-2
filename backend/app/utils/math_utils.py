"""Utilidades numéricas compartidas."""
from __future__ import annotations

import math
from typing import Dict, List, Optional


def safe_div(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den is None or den == 0:
        return None
    try:
        r = num / den
        if math.isnan(r) or math.isinf(r):
            return None
        return r
    except (TypeError, ZeroDivisionError):
        return None


def cagr(latest: Optional[float], oldest: Optional[float], periods: int) -> Optional[float]:
    """Tasa compuesta de crecimiento anual. Requiere valores positivos."""
    if latest is None or oldest is None or periods <= 0:
        return None
    if oldest <= 0 or latest <= 0:
        return None
    try:
        return (latest / oldest) ** (1 / periods) - 1
    except (ValueError, ZeroDivisionError):
        return None


def yoy(latest: Optional[float], previous: Optional[float]) -> Optional[float]:
    if latest is None or previous in (None, 0):
        return None
    return (latest - previous) / abs(previous)


def series_to_sorted(series: Dict[int, Optional[float]]) -> List[tuple]:
    """Devuelve [(año, valor), ...] ordenado de más reciente a más antiguo."""
    return sorted(((y, v) for y, v in series.items()), key=lambda x: x[0], reverse=True)


def latest_value(series: Dict[int, Optional[float]]) -> Optional[float]:
    s = series_to_sorted(series)
    for _, v in s:
        if v is not None:
            return v
    return None


def value_for_year(series: Dict[int, Optional[float]], year: int) -> Optional[float]:
    return series.get(year)


def mean(values: List[Optional[float]]) -> Optional[float]:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)
