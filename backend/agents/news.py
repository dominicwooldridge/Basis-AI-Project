import asyncio
from langchain_core.messages import HumanMessage

from backend.agents.base import BaseAgent
from backend.models.agents import NewsResult
from backend.tools.web_search import search_web_async


class NewsAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.structured_llm = self.llm.with_structured_output(NewsResult)

    async def run(self, technology: str, state: str) -> NewsResult:
        queries = [
            "IRA Inflation Reduction Act energy community bonus adder update 2025",
            f"ITC PTC clean energy tax credit {technology} update 2025 IRS Treasury",
            "Section 48E 45Y domestic content prevailing wage IRA notice 2025",
        ]

        results = await asyncio.gather(*[search_web_async(q) for q in queries])
        combined = "\n\n---\n\n".join(
            f"Search: {q}\n{r}" for q, r in zip(queries, results)
        )

        prompt = (
            f"You are an IRA regulatory analyst tracking tax credit policy changes.\n\n"
            f"Project type: {technology} in {state}\n\n"
            f"Below are recent web search results about IRA energy tax credit updates.\n"
            f"Extract 2-4 relevant news items and assess whether any represent material "
            f"changes to ITC/PTC eligibility, bonus adder rules, or domestic content rules "
            f"that would affect a {technology} project in {state}.\n\n"
            f"Search results:\n{combined[:6000]}\n\n"
            f"Return structured output with items, has_material_changes, and a concise "
            f"regulatory_note (2-3 sentences) summarizing anything that affects this project."
        )

        return await self.structured_llm.ainvoke([HumanMessage(content=prompt)])
