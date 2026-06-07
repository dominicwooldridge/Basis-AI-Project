from agents import OrchestratorAgent

demo_project = {
    "name": "Kern County Solar Demo",
    "technology": "solar",
    "capacity_mw": 100,
    "lat": 35.37,
    "lon": -118.83,
    "state": "CA",
    "county": "Kern",
    "capex_millions": 120.0,
    "prevailing_wage_compliant": True,
    "apprenticeship_compliant": True,
    "domestic_content_pct": 45.0,
    "discount_rate": 0.08,
    "project_life_years": 25,
}

if __name__ == "__main__":
    print("=== Basis Multi-Agent Demo ===\n")
    OrchestratorAgent().run(demo_project)
