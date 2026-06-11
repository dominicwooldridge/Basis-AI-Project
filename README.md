# Basis

Basis is an agentic AI deal underwriting assistant for renewable energy project developers operating under the Inflation Reduction Act (IRA). A developer submits project specs; a multi-agent backend pipeline runs a full credit analysis and returns a structured investment memo showing which IRA tax credits apply and what they do to project economics (IRR, NPV, payback period).

---

## What it does

Given a project's technology, location, capacity, CapEx, and compliance status, Basis:

1. Fetches live regulatory updates about IRA tax credit rules (web search)
2. Identifies which credits apply (48E ITC or 45Y PTC) and the base credit rate
3. Stacks applicable bonus adders — energy community, domestic content, low-income community
4. Runs a discounted cash flow model in two scenarios: with and without IRA credits
5. Synthesizes everything into a structured investment memo with risk flags and a recommendation

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11, FastAPI, LangChain |
| LLM | Claude 3.5 Haiku via AWS Bedrock (`anthropic.claude-3-5-haiku-20241022-v1:0`) |
| Financial model | numpy / numpy-financial (pure DCF, no LLM) |
| Data validation | Pydantic v2 |
| Deployment | AWS Lambda + Mangum (Function URL for 15-min timeout) |
| Frontend | React, Vite, Tailwind CSS |
| Web search | DuckDuckGo via `langchain-community` |
| Geo lookup | geopandas + shapely |
| Capacity factors | NREL PVWatts API (solar) / ATB lookup table (wind, other) |
| Electricity prices | EIA API |

---

## Multi-agent pipeline

```
OrchestratorAgent
  ├── NewsAgent               → NewsResult
  ├── CreditIdentificationAgent (receives NewsResult)       → CreditIdentificationResult
  ├── BonusAdderAgent         (receives CreditResult)       → BonusAdderResult
  ├── FinancialModelAgent     (receives BonusAdderResult)   → FinancialModelResult
  └── MemoAgent               (receives all four results)   → InvestmentMemo
```

### Agent responsibilities

**NewsAgent**  
Runs three parallel DuckDuckGo searches for IRA regulatory updates relevant to the project's technology and state. The LLM extracts 2–4 structured news items and writes a `regulatory_note` summarizing anything material to credit eligibility.

**CreditIdentificationAgent**  
Determines the applicable credit section (48E ITC or 45Y PTC) and base rate. The base rate is computed deterministically in Python (6% without PWA compliance, 30% with), then passed to the LLM as a hard fact. The LLM only decides ITC vs. PTC and writes an analyst note.

**BonusAdderAgent**  
Checks all four IRA bonus adder eligibilities. All arithmetic is in Python:
- Energy community: +10% (geocoder point-in-polygon against NETL shapefiles)
- Domestic content: +10% (project's domestic content % vs. statutory threshold)
- Low-income community: +10% or +20% (not yet implemented)
- Prevailing wage multiplier is captured in the base rate, not here

The LLM only writes a summary narrative; it never touches the numbers.

**FinancialModelAgent**  
Runs the DCF model twice (with and without ITC credit) using numpy-financial. Capacity factor comes from NREL PVWatts API (solar) or the ATB lookup table (other technologies). If no PPA rate is provided, it looks up the EIA retail electricity price for the project's state. The LLM echoes the computed values and writes a 2–3 sentence interpretation.

**MemoAgent**  
Synthesizes all prior results into a structured `InvestmentMemo` with sections for executive summary, credit analysis, financial analysis, recommendation, and risk flags. All numeric fields (IRR, stacked rate, NPV) are passed as Python-computed hard facts; the LLM writes narrative only.

> **Core design principle:** The LLM never computes numbers. All rates, adders, IRR, and NPV are calculated in Python and passed to agents as facts. Agents are responsible only for qualitative reasoning and narrative generation.

---

## IRA credit logic

### Base rates (Section 48E ITC)
| Condition | Rate |
|---|---|
| Without prevailing wage & apprenticeship (PWA) | 6% |
| With PWA compliance | 30% (5× multiplier) |

### Bonus adders (stack on top of base rate)
| Adder | Amount | Threshold |
|---|---|---|
| Domestic content | +10% | ≥40% by cost (solar/storage), ≥20% (wind) |
| Energy community | +10% | Coal closure or MSA/non-MSA energy community |
| Low-income community | +10% or +20% | Census tract lookup |

Maximum stacked ITC rate: ~50%

### ITC vs. PTC election
- **ITC (48E):** One-time credit on CapEx, taken in the year the project is placed in service. Better for capital-intensive projects.
- **PTC (45Y):** Per-kWh production credit over 10 years. Better for high-capacity-factor projects.
- Basis models both and recommends the higher-NPV option.

---

## Project structure

```
basis/
  backend/
    main.py                   # FastAPI app — /analyze, /chat, /health; Mangum Lambda handler
    config.py                 # Environment variable validation
    agents/
      base.py                 # BaseAgent ABC — sets up ChatBedrock
      orchestrator.py         # Coordinates all sub-agents sequentially
      news.py                 # NewsAgent — web search for regulatory updates
      credit_id.py            # CreditIdentificationAgent
      bonus_adder.py          # BonusAdderAgent
      financial_model.py      # FinancialModelAgent
      memo.py                 # MemoAgent
    models/
      intake.py               # ProjectIntake — intake form Pydantic schema
      agents.py               # Result schemas for each sub-agent
      memo.py                 # InvestmentMemo output schema
    tools/
      dcf.py                  # NPV / IRR / payback (pure numpy, no LLM)
      geocoder.py             # Energy community point-in-polygon lookup
      capacity_factor.py      # NREL PVWatts + ATB fallback
      eia_prices.py           # EIA retail electricity price by state
      web_search.py           # Async DuckDuckGo wrapper
    credit_logic/
      davisbacon.py           # Davis-Bacon prevailing wage logic
      multiplier.py           # ITC/PTC base rate multiplier logic
      risk_flags.py           # Risk flag generation
    data/
      reference/              # IRC §45, §45Y, §48, §48E statutory text; IRA PDF
      notices/                # IRS Treasury notices (energy community, PWA, domestic content)
      geo/                    # Energy community shapefiles (download before first run)
  frontend/
    src/
      App.jsx                 # Top-level state machine (form → loading → result → error)
      components/
        IntakeForm.jsx        # Project intake form with pre-filled demo
        Pipeline.jsx          # Animated 5-step progress indicator
        MemoCard.jsx          # Investment memo display
    vite.config.js            # Dev proxy: /analyze, /health → localhost:8000
  Dockerfile                  # Lambda container image
  deploy.ps1                  # ECR push + Lambda deploy script
  requirements.txt
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS account with Bedrock access (Claude 3.5 Haiku enabled in us-west-2)
- AWS SSO profile configured (see `.env`)

### 1. Clone and create the virtual environment

```bash
git clone https://github.com/dominicwooldridge/Basis-AI-Project.git
cd Basis-AI-Project
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file at the project root (never commit this):

```
ANTHROPIC_API_KEY=      # not used directly — AWS Bedrock handles auth
NREL_API_KEY=           # NREL PVWatts API key
EIA_API_KEY=            # EIA API key
AWS_PROFILE=            # AWS SSO profile name with Bedrock access
AWS_REGION=us-west-2
```

### 3. Download energy community shapefiles (run once)

```python
# backend/data/geo/ — run this script to download NETL shapefiles
COAL_URL = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/2024_Coal_Closure_Energy_Communities/FeatureServer/0/query"
MSA_URL  = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/2024_MSAs_NonMSAs_that_are_Energy_Communities/FeatureServer/0/query"
# Output: backend/data/geo/coal_closure_communities.geojson
#         backend/data/geo/msa_energy_communities.geojson
```

If shapefiles are absent, the geocoder defaults to `energy_community_qualifies = False`.

### 4. Run locally

```bash
# Backend
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/analyze` to `http://localhost:8000`.

---

## API

### `POST /analyze`

Accepts a `ProjectIntake` JSON body, runs the full pipeline, returns an `InvestmentMemo`.

**Request body**
```json
{
  "name": "Kern County Solar",
  "technology": "solar",
  "capacity_mw": 100,
  "lat": 35.37,
  "lon": -118.83,
  "state": "CA",
  "county": "Kern",
  "capex_millions": 120,
  "placed_in_service_date": "2025-01-01",
  "prevailing_wage_compliant": true,
  "apprenticeship_compliant": true,
  "domestic_content_pct": 45,
  "ppa_rate_dollars_per_mwh": 65,
  "discount_rate": 0.08,
  "project_life_years": 25
}
```

**Response** — `InvestmentMemo` with fields including:
- `recommended_credit`, `stacked_rate`, `credit_value_millions`
- `irr_with_credits`, `irr_without_credits`, `irr_delta`, `npv_with_credits`
- `executive_summary`, `credit_analysis`, `financial_analysis`, `recommendation`
- `risk_flags[]` — each with `flag`, `severity`, `detail`

### `GET /health`
Returns `{"status": "ok"}`.

---

## Deployment (AWS Lambda)

The app is packaged as a Lambda container image using Mangum to wrap the FastAPI ASGI app. Lambda Function URLs are used instead of API Gateway to avoid the 29-second timeout limit.

```powershell
# Build and deploy (requires Docker and AWS CLI)
.\deploy.ps1
```

The script:
1. Builds the Docker image from `Dockerfile`
2. Pushes to Amazon ECR
3. Creates or updates the Lambda function
4. Creates a Function URL if one doesn't exist

---

## Disclaimer

Basis is a research tool for illustrative purposes only. It is not tax or legal advice. Do not rely on its output for investment decisions. Tax credit eligibility involves complex statutory requirements — consult a qualified tax attorney or CPA.
