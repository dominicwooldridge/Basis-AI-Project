from pydantic import BaseModel


class NewsItem(BaseModel):
    headline: str
    summary: str
    relevance: str   # how it affects IRA credits for this project type


class NewsResult(BaseModel):
    items: list[NewsItem]
    has_material_changes: bool
    regulatory_note: str   # concise note passed downstream to credit agent


class CreditIdentificationResult(BaseModel):
    recommended_credit: str          # "ITC" or "PTC"
    credit_section: str              # "48E" or "45Y"
    base_rate: float                 # decimal (e.g. 0.30)
    pwa_compliant: bool
    pwa_multiplier_applied: bool
    base_ptc_rate_cents_per_kwh: float
    analyst_note: str


class BonusAdderResult(BaseModel):
    domestic_content_adder: float
    energy_community_adder: float
    low_income_adder: float
    stacked_rate: float
    energy_community_qualifies: bool
    energy_community_type: str       # "coal_closure" | "msa_fossil_fuel" | "none"
    domestic_content_qualifies: bool
    analyst_note: str


class FinancialModelResult(BaseModel):
    capacity_factor: float
    annual_production_mwh: float
    electricity_price_dollars_per_mwh: float
    credit_value_millions: float
    npv_with_credits: float
    irr_with_credits: float
    payback_years_with_credits: float
    npv_without_credits: float
    irr_without_credits: float
    payback_years_without_credits: float
    irr_delta: float
    analyst_note: str
