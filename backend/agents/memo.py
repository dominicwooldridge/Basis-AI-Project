from langchain_core.messages import HumanMessage

from backend.agents.base import BaseAgent
from backend.models.intake import ProjectIntake
from backend.models.agents import (
    CreditIdentificationResult, BonusAdderResult, FinancialModelResult, NewsResult
)
from backend.models.memo import InvestmentMemo


class MemoAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.structured_llm = self.llm.with_structured_output(InvestmentMemo)

    async def run(
        self,
        project: ProjectIntake,
        credit: CreditIdentificationResult,
        adder: BonusAdderResult,
        financial: FinancialModelResult,
        news: NewsResult,
    ) -> InvestmentMemo:
        adder_lines = []
        if adder.energy_community_qualifies:
            adder_lines.append(f"Energy community (+10%, {adder.energy_community_type})")
        if adder.domestic_content_qualifies:
            adder_lines.append("Domestic content (+10%)")
        adder_summary = "; ".join(adder_lines) if adder_lines else "None"

        prompt = (
            f"You are a senior renewable energy investment analyst. "
            f"Write a structured investment memo for the following project.\n\n"
            f"PROJECT\n"
            f"Name: {project.name}\n"
            f"Technology: {project.technology}, {project.capacity_mw} MW\n"
            f"Location: {project.county} County, {project.state}\n"
            f"CapEx: ${project.capex_millions}M | Placed in service: {project.placed_in_service_date}\n\n"
            f"CREDIT ANALYSIS\n"
            f"Recommended: {credit.recommended_credit} (Section {credit.credit_section})\n"
            f"Base rate: {credit.base_rate} decimal (PWA compliant: {credit.pwa_compliant})\n"
            f"Bonus adders: {adder_summary}\n"
            f"Stacked rate: {adder.stacked_rate} decimal\n"
            f"Credit value: ${financial.credit_value_millions:.1f}M\n\n"
            f"FINANCIAL MODEL\n"
            f"Capacity factor: {financial.capacity_factor} decimal | "
            f"Annual production: {financial.annual_production_mwh:,.0f} MWh\n"
            f"Electricity price: ${financial.electricity_price_dollars_per_mwh:.2f}/MWh\n"
            f"With credits: IRR {financial.irr_with_credits} decimal, "
            f"NPV ${financial.npv_with_credits:.1f}M, "
            f"Payback {financial.payback_years_with_credits:.1f} yrs\n"
            f"Without credits: IRR {financial.irr_without_credits} decimal, "
            f"NPV ${financial.npv_without_credits:.1f}M\n"
            f"IRR delta: {financial.irr_delta} decimal\n\n"
            f"REGULATORY\n{news.regulatory_note}\n\n"
            f"INSTRUCTIONS\n"
            f"- executive_summary: 3-4 sentences, highlight credit value and IRR impact\n"
            f"- credit_analysis: 2-3 sentences on credit structure and bonus adder eligibility\n"
            f"- financial_analysis: 2-3 sentences on DCF results and what drives returns\n"
            f"- recommendation: 2 sentences — invest/proceed/monitor and key condition\n"
            f"- risk_flags: 2-4 items with severity (high/medium/low) and one-sentence detail\n"
            f"- regulatory_note: use the regulatory context provided.\n"
            f"- IMPORTANT: all rate and IRR fields must be returned as decimals (e.g. 0.40 not 40.0, 0.14 not 14.0).\n"
            f"- Pass through all numeric fields exactly as given above."
        )

        return await self.structured_llm.ainvoke([HumanMessage(content=prompt)])
