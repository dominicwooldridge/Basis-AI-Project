from pydantic import BaseModel
import boto3
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage


def _make_llm():
    session = boto3.Session(profile_name="GSB570-BedrockOnly-490332585640")
    return ChatBedrock(
        model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
        client=session.client("bedrock-runtime", region_name="us-west-2"),
        model_kwargs={"temperature": 0, "max_tokens": 256},
    )


# ---------- Pydantic result schemas ----------

class CreditResult(BaseModel):
    base_rate: float
    pwa_compliant: bool


class AdderResult(BaseModel):
    energy_community: bool
    adder: float
    stacked_rate: float


class SummaryResult(BaseModel):
    summary: str
    credit_value_millions: float


# ---------- Sub-agents ----------

class CreditAgent:
    def __init__(self):
        self.llm = _make_llm().with_structured_output(CreditResult)

    def run(self, project: dict) -> CreditResult:
        prompt = (
            "You are an IRA tax credit analyst.\n\n"
            "Rule: Under IRA Section 48E the base ITC rate is 6%. "
            "If the project meets BOTH prevailing wage AND apprenticeship requirements "
            "a 5x multiplier applies, making the rate 30% (0.30).\n\n"
            f"- Prevailing wage compliant: {project['prevailing_wage_compliant']}\n"
            f"- Apprenticeship compliant:  {project['apprenticeship_compliant']}\n\n"
            "Return base_rate as a decimal (e.g. 0.30) and pwa_compliant as a boolean."
        )
        return self.llm.invoke([HumanMessage(content=prompt)])


class AdderAgent:
    def __init__(self):
        self.llm = _make_llm().with_structured_output(AdderResult)

    @staticmethod
    def _is_energy_community(state: str, county: str) -> bool:
        # Kern County, CA is a designated coal closure community per IRS Notice 2023-29
        return state == "CA" and county.lower() == "kern"

    def run(self, project: dict, credit: CreditResult) -> AdderResult:
        qualifies = self._is_energy_community(project["state"], project["county"])
        prompt = (
            "You are an IRA bonus adder analyst.\n\n"
            f"Base ITC rate: {credit.base_rate} (decimal)\n"
            f"Energy community qualification (geocoder result): {qualifies}\n"
            "(Kern County, CA is a designated coal closure energy community "
            "per IRS Notice 2023-29.)\n\n"
            "Rule: if energy_community is True, adder = 0.10 and "
            "stacked_rate = base_rate + 0.10. "
            "If False, adder = 0.0 and stacked_rate = base_rate.\n\n"
            "Return energy_community (bool), adder (decimal), stacked_rate (decimal)."
        )
        return self.llm.invoke([HumanMessage(content=prompt)])


class SummaryAgent:
    def __init__(self):
        self.llm = _make_llm().with_structured_output(SummaryResult)

    def run(self, project: dict, adder: AdderResult) -> SummaryResult:
        credit_value = round(adder.stacked_rate * project["capex_millions"], 1)
        prompt = (
            "You are an IRA investment analyst.\n\n"
            f"Project: {project['name']}, {project['capacity_mw']} MW solar, "
            f"{project['county']} County, {project['state']}\n"
            f"CapEx: ${project['capex_millions']}M\n"
            f"Stacked ITC rate: {adder.stacked_rate:.0%} "
            f"(base 30% + energy community +{adder.adder:.0%})\n"
            f"Credit value: ${credit_value}M\n\n"
            "Write a one-paragraph plain-English summary (under 80 words) for the developer. "
            "Mention the energy community qualification specifically.\n"
            f"Return summary (string) and credit_value_millions = {credit_value} exactly."
        )
        return self.llm.invoke([HumanMessage(content=prompt)])


# ---------- Orchestrator ----------

class OrchestratorAgent:
    def __init__(self):
        self.credit_agent = CreditAgent()
        self.adder_agent = AdderAgent()
        self.summary_agent = SummaryAgent()

    def run(self, project: dict) -> dict:
        print("[1/3] CreditAgent running...")
        credit = self.credit_agent.run(project)
        pwa_label = "PWA compliant" if credit.pwa_compliant else "PWA non-compliant"
        print(f"  Base ITC rate: {credit.base_rate:.0%} ({pwa_label})")

        print("\n[2/3] AdderAgent running...")
        adder = self.adder_agent.run(project, credit)
        community_label = "YES — Kern County qualifies" if adder.energy_community else "NO"
        print(f"  Energy community: {community_label}")
        print(f"  Stacked credit rate: {adder.stacked_rate:.0%}")

        print("\n[3/3] SummaryAgent running...")
        summary = self.summary_agent.run(project, adder)
        print(f"  {summary.summary}")

        print("\n=== Result ===")
        print(f"  Credit value: ${summary.credit_value_millions:.1f}M on ${project['capex_millions']:.0f}M project")
        print(f"  Stacked rate: {adder.stacked_rate:.0%}")

        return {"credit": credit, "adder": adder, "summary": summary}
