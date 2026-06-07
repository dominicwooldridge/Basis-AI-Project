import geopandas as gpd
from shapely.geometry import Point
from functools import lru_cache

@lru_cache(maxsize=1)
def load_energy_communities():
    coal = gpd.read_file("basis/backend/data/coal_closure_communities.geojson")
    msa = gpd.read_file("basis/backend/data/msa_energy_communities.geojson")
    return coal, msa

def check_energy_community(lat: float, lon: float) -> dict:
    coal, msa = load_energy_communities()
    point = Point(lon, lat)
    
    in_coal = coal[coal.geometry.contains(point)]
    in_msa = msa[msa.geometry.contains(point)]
    
    return {
        "qualifies": len(in_coal) > 0 or len(in_msa) > 0,
        "coal_closure": len(in_coal) > 0,
        "msa_fossil_fuel": len(in_msa) > 0,
        "adder_pct": 10 if (len(in_coal) > 0 or len(in_msa) > 0) else 0
    }