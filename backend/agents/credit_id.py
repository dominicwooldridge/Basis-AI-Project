from langchain_core.messages import HumanMessage

from backend.agents.base import BaseAgent
from backend.models.intake import ProjectIntake
from backend.models.agents import CreditIdentificationResult, NewsResult


class CreditIdentificationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.structured_llm = self.llm.with_structured_output(CreditIdentificationResult)

    async def run(self, project: ProjectIntake, news: NewsResult) -> CreditIdentificationResult:
        # Compute deterministically — do not let the LLM touch these
        pwa_compliant          = project.prevailing_wage_compliant and project.apprenticeship_compliant
        pwa_multiplier_applied = pwa_compliant
        base_rate              = 0.30 if pwa_multiplier_applied else 0.06
        base_ptc_rate          = 1.5  if pwa_multiplier_applied else 0.3

        prompt = (
            f"You are an IRA Section 48E/45Y tax credit analyst.\n\n"
            f"Project: {project.name}\n"
            f"Technology: {project.technology}, {project.capacity_mw} MW\n"
            f"State: {project.state} | Placed in service: {project.placed_in_service_date}\n\n"
            f"The following values have been computed for you — return them exactly:\n"
            f"  pwa_compliant = {pwa_compliant}\n"
            f"  pwa_multiplier_applied = {pwa_multiplier_applied}\n"
            f"  base_rate = {base_rate}  (decimal)\n"
            f"  base_ptc_rate_cents_per_kwh = {base_ptc_rate}\n\n"
            f"Your job:\n"
            f"1. Recommend ITC or PTC (recommended_credit). "
            f"ITC (48E) is a one-time % of CapEx — better for capital-intensive projects. "
            f"PTC (45Y) is per-kWh over 10 years — better for high-capacity-factor projects. "
            f"Solar utility-scale almost always favours ITC.\n"
            f"2. Set credit_section to '48E' if ITC or '45Y' if PTC.\n"
            f"3. Write a 1-2 sentence analyst_note.\n\n"
            f"Regulatory context: {news.regulatory_note}\n\n"
            f"IMPORTANT: return base_rate as {base_rate} (decimal, not percentage)."
        )

        return await self.structured_llm.ainvoke([HumanMessage(content=prompt)])
