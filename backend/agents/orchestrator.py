from backend.models.intake import ProjectIntake
from backend.models.memo import InvestmentMemo
from backend.agents.news import NewsAgent
from backend.agents.credit_id import CreditIdentificationAgent
from backend.agents.bonus_adder import BonusAdderAgent
from backend.agents.financial_model import FinancialModelAgent
from backend.agents.memo import MemoAgent


class OrchestratorAgent:
    def __init__(self):
        self.news_agent      = NewsAgent()
        self.credit_agent    = CreditIdentificationAgent()
        self.adder_agent     = BonusAdderAgent()
        self.financial_agent = FinancialModelAgent()
        self.memo_agent      = MemoAgent()

    async def run(self, project: ProjectIntake) -> InvestmentMemo:
        print(f"\n[News] Fetching IRA regulatory updates for {project.technology}/{project.state}...")
        news = await self.news_agent.run(project.technology, project.state)
        material = "material changes found" if news.has_material_changes else "no material changes"
        print(f"  {len(news.items)} items — {material}")

        print("\n[1/4] CreditIdentificationAgent running...")
        credit = await self.credit_agent.run(project, news)
        print(f"  Recommended: {credit.recommended_credit} (Section {credit.credit_section})")
        print(f"  Base rate: {credit.base_rate:.0%} | PWA: {credit.pwa_compliant}")

        print("\n[2/4] BonusAdderAgent running...")
        adder = await self.adder_agent.run(project, credit)
        print(f"  Energy community: {adder.energy_community_qualifies} ({adder.energy_community_type})")
        print(f"  Domestic content: {adder.domestic_content_qualifies}")
        print(f"  Stacked rate: {adder.stacked_rate:.0%}")

        print("\n[3/4] FinancialModelAgent running...")
        financial = await self.financial_agent.run(project, adder)
        print(f"  IRR with credits: {financial.irr_with_credits:.1%}")
        print(f"  IRR without:      {financial.irr_without_credits:.1%}")
        print(f"  Credit value:     ${financial.credit_value_millions:.1f}M")

        print("\n[4/4] MemoAgent running...")
        memo = await self.memo_agent.run(project, credit, adder, financial, news)
        print("  Investment memo generated.")

        return memo
