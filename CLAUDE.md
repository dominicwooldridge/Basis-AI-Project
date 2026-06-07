# Basis — CLAUDE.md

This file is the persistent project context for Claude Code. Read it at the
start of every session before touching any file.

---

## What this project is

Basis is an agentic AI deal underwriting assistant for renewable energy project
developers under the Inflation Reduction Act (IRA). A developer submits project
specs via a form; a multi-agent backend pipeline runs a full credit analysis and
returns a structured investment memo showing what IRA tax credits they qualify
for and what that does to their project economics (IRR, NPV).

---

## Tech stack

- Backend: Python, FastAPI, LangChain, Claude claude-sonnet-4-20250514
- Frontend: React (Vite), Tailwind CSS
- Financial model: custom DCF module using numpy
- Validation: Pydantic v2
- Env management: python-dotenv

---

## File structure

```
basis/
  .env                          # API keys — never commit
  .gitignore
  CLAUDE.md                     # this file
  backend/
    main.py                     # FastAPI app — routes: /analyze, /chat, /health
    agents/
      base.py                   # BaseAgent ABC — shared LLM instantiation
      orchestrator.py           # OrchestratorAgent — coordinates sub-agents
      credit_id.py              # CreditIdentificationAgent
      bonus_adder.py            # BonusAdderAgent
      financial_model.py        # FinancialModelAgent
      memo.py                   # MemoAgent
    models/
      intake.py                 # ProjectIntake Pydantic schema
      agents.py                 # CreditIdentificationResult, BonusAdderResult,
                                #   FinancialModelResult schemas
      memo.py                   # InvestmentMemo schema
    tools/
      web_search.py             # LangChain web search — IRS/Treasury guidance
      geocoder.py               # energy community point-in-polygon lookup
      energy_mapping.py         # supporting geo utilities (merge into geocoder.py)
      capacity_factor.py        # NREL PVWatts + ATB fallback (merge pvwatts.py
                                #   + wind_toolkit.py + atb_lookup.py into this)
      eia_prices.py             # EIA retail electricity price by state
      dcf.py                    # NPV / IRR / payback calculations (pure numpy)
      atb_lookup.py             # ATB regional capacity factor table (NREL 2024 ATB)
      pvwatts.py                # NREL PVWatts API (solar capacity factor)
      wind_toolkit.py           # NREL Wind Toolkit API
    credit_logic/
      davisbacon.py             # Davis-Bacon prevailing wage logic
      multiplier.py             # ITC/PTC base rate multiplier logic
      risk_flags.py             # risk flag generation
    data/
      reference/                # statutory credit documents
        26_USC_45.html          # IRC §45 — legacy PTC
        26_USC_45Y.html         # IRC §45Y — Clean Electricity PTC
        26_USC_48.html          # IRC §48 — legacy ITC
        26_USC_48E.html         # IRC §48E — Clean Electricity ITC
        Inflation_Reduction_Act.pdf
        IRS_Credit_Statement.pdf
      notices/                  # IRS Treasury notices
        n-23-29.pdf             # energy community guidance
        n-23-47.pdf             # prevailing wage & apprenticeship
        n-24-30.pdf             # domestic content
        n-24-41.pdf             # domestic content update
        n-24-48.pdf
        n-25-31.pdf
        low_income/             # low-income community bonus adder
          2024-19617.pdf
          2025-00331.pdf
          rp-25-11.pdf
        appendices/
          placed_in_service_6-6-2024/
          placed_in_service_12-31-2022/
          placed_in_service_after_6-22-2025/
      geo/                      # spatial data — download before running
        coal_closure_communities.geojson     # NOT YET DOWNLOADED
        msa_energy_communities.geojson       # NOT YET DOWNLOADED
  frontend/                     # React app — not started yet
```

---

## Environment variables

All loaded via python-dotenv from `.env` at project root.
Call `load_dotenv()` once at the top of `main.py` only.

```
ANTHROPIC_API_KEY=       # Claude API — required for all agents
NREL_API_KEY=            # NREL PVWatts API — solar capacity factors
EIA_API_KEY=             # EIA API — electricity prices by state
```

---

## Multi-agent architecture

The pipeline uses an orchestrator + four specialized sub-agents.
The orchestrator coordinates; sub-agents do the analysis.

```
OrchestratorAgent
  └── CreditIdentificationAgent  →  CreditIdentificationResult
  └── BonusAdderAgent            →  BonusAdderResult
        (receives CreditIdentificationResult)
  └── FinancialModelAgent        →  FinancialModelResult
        (receives BonusAdderResult)
  └── MemoAgent                  →  InvestmentMemo
        (receives all three results)
```

### Sub-agent responsibilities

**CreditIdentificationAgent**
- Determines which IRA credits apply: 48E ITC, 45Y PTC, 45V, 45X, 48C
- Makes ITC vs PTC election recommendation
- Calls web_search tool to verify current IRS/Treasury rates
- Returns: CreditIdentificationResult

**BonusAdderAgent**
- Checks all four bonus adder eligibilities:
  - Prevailing wage & apprenticeship → 5x multiplier (6% → 30%)
  - Domestic content → +10%
  - Energy community → +10% (uses geocoder tool)
  - Low-income community → +10% or +20%
- Returns: BonusAdderResult with final stacked rate

**FinancialModelAgent**
- Runs DCF in two scenarios: with credits and without
- Calls pvwatts tool (solar) or atb_lookup (other tech) for capacity factor
- Calls eia_prices tool if no PPA rate provided
- Returns: FinancialModelResult with IRR, NPV, payback, IRR delta

**MemoAgent**
- Synthesizes all results into structured investment memo
- Generates risk flags
- Returns: InvestmentMemo

### Key constraint
Every sub-agent must return a validated Pydantic object using
LangChain's `.with_structured_output()`. Never return raw LLM text
from a sub-agent.

---

## IRA credit logic — reference

### Base rates (48E ITC)
- Without prevailing wage & apprenticeship (PWA): 6%
- With PWA compliance: 30%  (5x multiplier)

### Bonus adders (stack on top of base rate)
- Domestic content: +10%  (threshold: 40% for solar/storage, 20% for wind)
- Energy community: +10%  (check geocoder against geo/ shapefiles)
- Low-income community: +10% or +20% (census tract lookup)
- Maximum stacked ITC: ~50%

### PWA requirements (BOTH required for multiplier)
- Prevailing wage: Davis-Bacon rates for all construction workers
- Apprenticeship: 10-15% of labor hours from DOL-registered programs

### ITC vs PTC
- ITC (48E): one-time credit on CapEx, taken in year project placed in service
- PTC (45Y): per-kWh production credit over 10 years
- Developer elects one — cannot take both on same project
- Agent models both and recommends higher NPV option

### Placed-in-service date matters
Rules differ by placed-in-service window. Match project date to
the correct appendices folder in data/notices/appendices/.

---

## Data sources

| Data | Source | Status |
|------|--------|--------|
| ITC/PTC credit rules | backend/data/reference/ | ✅ collected |
| IRS Treasury notices | backend/data/notices/ | ✅ collected |
| Energy community (coal closure) | NETL ArcGIS REST API | ❌ not downloaded |
| Energy community (MSA/non-MSA) | NETL ArcGIS REST API | ❌ not downloaded |
| Solar capacity factor | NREL PVWatts API | ✅ API ready |
| Wind capacity factor | ATB lookup table (atb_lookup.py) | ✅ implemented |
| Electricity prices | EIA API (eia_prices.py) | ✅ API ready |
| Prevailing wage schedules | Self-reported — no download needed | ✅ n/a |

### Download geo data (run once before first agent run)

```python
# Run this script to download energy community shapefiles
# Output: backend/data/geo/coal_closure_communities.geojson
#         backend/data/geo/msa_energy_communities.geojson

COAL_URL = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/2024_Coal_Closure_Energy_Communities/FeatureServer/0/query"
MSA_URL  = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/2024_MSAs_NonMSAs_that_are_Energy_Communities/FeatureServer/0/query"
```

---

## FastAPI routes

```
GET  /health     → health check
POST /analyze    → accepts ProjectIntake JSON, returns InvestmentMemo
POST /chat       → accepts ChatRequest, returns ChatResponse
```

Run from project root:
```bash
uvicorn backend.main:app --reload
```

---

## Build order

Track progress here. Do not skip steps.

- [ ] models/intake.py          — ProjectIntake Pydantic schema
- [ ] models/agents.py          — result schemas for all sub-agents
- [ ] models/memo.py            — InvestmentMemo schema
- [ ] tools/dcf.py              — NPV/IRR/payback (pure numpy, no LLM)
- [ ] tools/geocoder.py         — energy community lookup (merge geocoder + energy_mapping)
- [ ] tools/capacity_factor.py  — NREL PVWatts + ATB fallback (merge 3 files)
- [ ] tools/eia_prices.py       — EIA price lookup (already drafted)
- [ ] tools/web_search.py       — LangChain web search wrapper
- [ ] agents/base.py            — BaseAgent ABC
- [ ] agents/credit_id.py       — CreditIdentificationAgent
- [ ] agents/bonus_adder.py     — BonusAdderAgent
- [ ] agents/financial_model.py — FinancialModelAgent
- [ ] agents/memo.py            — MemoAgent
- [ ] agents/orchestrator.py    — OrchestratorAgent
- [ ] main.py                   — FastAPI app wiring
- [ ] Tests for dcf.py and geocoder.py
- [ ] frontend/                 — React app (start after backend is working end-to-end)

---

## Coding conventions

- Python 3.11+
- Pydantic v2 — use `model_validator`, `field_validator` not v1 syntax
- Async throughout — all agent `run()` methods are `async def`
- Type hints on every function signature
- No hardcoded API keys — always `os.getenv()`
- File names: snake_case, no spaces
- Do not modify files in data/ — treat as read-only reference material