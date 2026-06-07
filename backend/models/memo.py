from pydantic import BaseModel


class RiskFlag(BaseModel):
    flag: str
    severity: str   # "high" | "medium" | "low"
    detail: str


class InvestmentMemo(BaseModel):
    project_name: str
    technology: str
    capacity_mw: float
    state: str
    county: str
    recommended_credit: str
    stacked_rate: float
    credit_value_millions: float
    irr_with_credits: float
    irr_without_credits: float
    irr_delta: float
    npv_with_credits: float
    payback_years: float
    regulatory_note: str
    risk_flags: list[RiskFlag]
    executive_summary: str
    credit_analysis: str
    financial_analysis: str
    recommendation: str
