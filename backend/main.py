from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum

from backend.config import Config
from backend.models.intake import ProjectIntake
from backend.models.memo import InvestmentMemo
from backend.agents.orchestrator import OrchestratorAgent

Config.validate()

app = FastAPI(title="Basis", description="IRA deal underwriting assistant")

# Lambda handler — Mangum wraps the ASGI app for Lambda + Function URL
handler = Mangum(app, lifespan="off")


class ChatRequest(BaseModel):
    message: str
    context: dict = {}


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=InvestmentMemo)
async def analyze(project: ProjectIntake) -> InvestmentMemo:
    try:
        orchestrator = OrchestratorAgent()
        return await orchestrator.run(project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(response="Chat endpoint not yet implemented.")
