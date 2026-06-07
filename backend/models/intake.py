from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


class ProjectIntake(BaseModel):
    name: str
    technology: str          # solar | wind_onshore | wind_offshore | geothermal | storage
    capacity_mw: float
    lat: float
    lon: float
    state: str               # 2-letter code
    county: str
    capex_millions: float
    placed_in_service_date: date
    prevailing_wage_compliant: bool = False
    apprenticeship_compliant: bool = False
    domestic_content_pct: float = 0.0
    ppa_rate_dollars_per_mwh: Optional[float] = None  # None → look up via EIA
    discount_rate: float = 0.08
    project_life_years: int = 25

    @field_validator("state")
    @classmethod
    def upper_state(cls, v: str) -> str:
        return v.upper()

    @field_validator("technology")
    @classmethod
    def lower_technology(cls, v: str) -> str:
        return v.lower()
