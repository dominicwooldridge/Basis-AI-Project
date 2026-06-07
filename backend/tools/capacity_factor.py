"""
Capacity factor lookup.

For solar: tries NREL PVWatts API first, falls back to ATB regional table.
For all other technologies: uses ATB regional table directly.
"""

import os
import requests
from backend.tools.atb_lookup import ATB_CAPACITY_FACTORS

PVWATTS_URL = "https://developer.nrel.gov/api/pvwatts/v8/json"

_SOUTHWEST  = {"CA", "AZ", "NV", "NM", "UT", "CO"}
_GREAT_PLAINS = {"TX", "KS", "OK", "ND", "SD", "NE"}
_SOUTHEAST  = {"FL", "GA", "AL", "MS", "SC", "NC", "LA", "AR"}
_MIDWEST    = {"IL", "IN", "OH", "MI", "WI", "MN", "IA", "MO"}
_NORTHEAST  = {"NY", "MA", "CT", "RI", "NH", "VT", "ME", "PA", "NJ", "DE", "MD"}
_NORTHWEST  = {"WA", "OR", "ID", "MT", "WY"}


def _state_to_region(state: str) -> str:
    s = state.upper()
    if s in _SOUTHWEST:    return "southwest"
    if s in _GREAT_PLAINS: return "great_plains"
    if s in _SOUTHEAST:    return "southeast"
    if s in _MIDWEST:      return "midwest"
    if s in _NORTHEAST:    return "northeast"
    if s in _NORTHWEST:    return "northwest"
    return "default"


def _pvwatts(lat: float, lon: float, capacity_kw: float, api_key: str) -> float:
    params = {
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "system_capacity": capacity_kw,
        "azimuth": 180,
        "tilt": round(lat * 0.76, 1),
        "array_type": 1,
        "module_type": 0,
        "losses": 14,
    }
    r = requests.get(PVWATTS_URL, params=params, timeout=15)
    r.raise_for_status()
    annual_kwh = r.json()["outputs"]["ac_annual"]
    return round(annual_kwh / (capacity_kw * 8760), 4)


def _atb(technology: str, state: str) -> float:
    region = _state_to_region(state)
    tech_data = ATB_CAPACITY_FACTORS.get(technology, {})
    return tech_data.get(region, tech_data.get("default", 0.25))


def get_capacity_factor(technology: str, lat: float, lon: float, state: str, capacity_mw: float) -> float:
    if technology == "solar":
        api_key = os.getenv("NREL_API_KEY")
        if api_key:
            try:
                return _pvwatts(lat, lon, capacity_mw * 1000, api_key)
            except Exception:
                pass
        return _atb("solar", state)

    return _atb(technology, state)
