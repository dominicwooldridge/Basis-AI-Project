from langchain_core.messages import HumanMessage

from backend.agents.base import BaseAgent
from backend.models.intake import ProjectIntake
from backend.models.agents import BonusAdderResult, CreditIdentificationResult
from backend.tools.geocoder import check_energy_community


_DC_THRESHOLD = {"solar": 40.0, "storage": 40.0, "wind_onshore": 20.0, "wind_offshore": 20.0}


class BonusAdderAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.structured_llm = self.llm.with_structured_output(BonusAdderResult)

    async def run(
        self, project: ProjectIntake, credit: CreditIdentificationResult
    ) -> BonusAdderResult:
        # --- All arithmetic computed in Python ---
        ec           = check_energy_community(project.lat, project.lon)
        dc_threshold = _DC_THRESHOLD.get(project.technology, 40.0)

        ec_qualifies = ec["qualifies"]
        dc_qualifies = project.domestic_content_pct >= dc_threshold

        ec_adder  = 0.10 if ec_qualifies else 0.0
        dc_adder  = 0.10 if dc_qualifies else 0.0
        li_adder  = 0.0
        stacked   = round(credit.base_rate + ec_adder + dc_adder + li_adder, 4)

        ec_type = ec["community_type"]
        ec_data = ec["data_available"]

        prompt = (
            f"You are an IRA bonus adder analyst.\n\n"
            f"The following values have been computed — return them exactly:\n"
            f"  energy_community_qualifies = {ec_qualifies} "
            f"({'geocoder confirmed' if ec_data else 'shapefile unavailable — defaulting to False'})\n"
            f"  energy_community_type = '{ec_type}'\n"
            f"  domestic_content_qualifies = {dc_qualifies} "
            f"({project.domestic_content_pct}% vs {dc_threshold}% threshold)\n"
            f"  energy_community_adder = {ec_adder}  (decimal)\n"
            f"  domestic_content_adder = {dc_adder}  (decimal)\n"
            f"  low_income_adder = {li_adder}\n"
            f"  stacked_rate = {stacked}  (decimal) — this is final, do not recalculate\n\n"
            f"Write a 1-2 sentence analyst_note summarising which adders applied and why.\n\n"
            f"IMPORTANT: return stacked_rate as {stacked} exactly (decimal, not percentage)."
        )

        return await self.structured_llm.ainvoke([HumanMessage(content=prompt)])
