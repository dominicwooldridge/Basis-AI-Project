import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_electricity_price(state_code: str, sector: str = "COM") -> dict:
    """
    Get average retail electricity price for a state.
    
    sector options:
      RES - Residential
      COM - Commercial  
      IND - Industrial
      ALL - All sectors
    """
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    params = {
        "api_key": os.getenv("EIA_API_KEY"),
        "data[]": "price",
        "facets[stateid][]": state_code.upper(),
        "facets[sectorid][]": sector,
        "frequency": "annual",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1   # just the most recent year
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["response"]["data"]

    if not data:
        return None

    row = data[0]
    return {
        "state": state_code,
        "sector": sector,
        "year": row["period"],
        "price_cents_per_kwh": float(row["price"]),
        "price_dollars_per_mwh": float(row["price"]) * 10
    }