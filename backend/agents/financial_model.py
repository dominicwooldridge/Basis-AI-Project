from langchain_core.messages import HumanMessage

from backend.agents.base import BaseAgent
from backend.models.intake import ProjectIntake
from backend.models.agents import BonusAdderResult, FinancialModelResult
from backend.tools.capacity_factor import get_capacity_factor
from backend.tools.eia_prices import get_electricity_price
from backend.tools.dcf import run_dcf


class FinancialModelAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.structured_llm = self.llm.with_structured_output(FinancialModelResult)

    async def run(
        self, project: ProjectIntake, adder: BonusAdderResult
    ) -> FinancialModelResult:
        # --- Deterministic computations (no LLM) ---
        cf = get_capacity_factor(
            project.technology, project.lat, project.lon,
            project.state, project.capacity_mw
        )
        annual_mwh = project.capacity_mw * cf * 8760  # MW × hours = MWh

        if project.ppa_rate_dollars_per_mwh:
            price = project.ppa_rate_dollars_per_mwh
        else:
            eia = get_electricity_price(project.state, sector="COM")
            price = eia["price_dollars_per_mwh"] if eia else 60.0

        annual_revenue_m = (annual_mwh * price) / 1_000_000
        credit_value_m   = adder.stacked_rate * project.capex_millions

        with_credits = run_dcf(
            capex_millions=project.capex_millions,
            annual_revenue_millions=annual_revenue_m,
            discount_rate=project.discount_rate,
            years=project.project_life_years,
            itc_credit_millions=credit_value_m,
        )
        without_credits = run_dcf(
            capex_millions=project.capex_millions,
            annual_revenue_millions=annual_revenue_m,
            discount_rate=project.discount_rate,
            years=project.project_life_years,
            itc_credit_millions=0.0,
        )

        irr_delta = with_credits["irr"] - without_credits["irr"]

        # --- LLM call: echo computed values + write analyst_note ---
        prompt = (
            f"You are a renewable energy financial analyst.\n\n"
            f"The following values were computed by deterministic Python tools. "
            f"Return them exactly as given and write a concise analyst_note "
            f"(2-3 sentences) interpreting the financial result.\n\n"
            f"capacity_factor: {cf}\n"
            f"annual_production_mwh: {round(annual_mwh)}\n"
            f"electricity_price_dollars_per_mwh: {round(price, 2)}\n"
            f"credit_value_millions: {round(credit_value_m, 2)}\n"
            f"npv_with_credits: {with_credits['npv']}\n"
            f"irr_with_credits: {with_credits['irr']}\n"
            f"payback_years_with_credits: {with_credits['payback_years']}\n"
            f"npv_without_credits: {without_credits['npv']}\n"
            f"irr_without_credits: {without_credits['irr']}\n"
            f"payback_years_without_credits: {without_credits['payback_years']}\n"
            f"irr_delta: {round(irr_delta, 4)}\n"
        )

        return await self.structured_llm.ainvoke([HumanMessage(content=prompt)])
