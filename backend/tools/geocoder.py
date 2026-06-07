"""
Energy community point-in-polygon lookup.

Reads the geojson shapefiles downloaded from NETL ArcGIS.
Returns gracefully if files have not yet been downloaded.

To download the shapefiles, run:
    python -c "from backend.tools.geocoder import download_geo_data; download_geo_data()"
"""

from pathlib import Path
from functools import lru_cache

import requests
import geopandas as gpd
from shapely.geometry import Point

DATA_DIR   = Path(__file__).parent.parent / "data" / "geo"
COAL_FILE  = DATA_DIR / "coal_closure_communities.geojson"
MSA_FILE   = DATA_DIR / "msa_energy_communities.geojson"

COAL_URL = (
    "https://arcgis.netl.doe.gov/server/rest/services/Hosted/"
    "2024_Coal_Closure_Energy_Communities/FeatureServer/0/query"
)
MSA_URL = (
    "https://arcgis.netl.doe.gov/server/rest/services/Hosted/"
    "2024_MSAs_NonMSAs_that_are_Energy_Communities/FeatureServer/0/query"
)


def download_geo_data() -> None:
    """Download NETL energy community shapefiles and save to data/geo/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for url, path, name in [
        (COAL_URL, COAL_FILE, "Coal Closure"),
        (MSA_URL,  MSA_FILE,  "MSA/Non-MSA"),
    ]:
        features, offset, batch = [], 0, 2000
        while True:
            r = requests.get(url, params={
                "where": "1=1", "outFields": "*", "f": "geojson",
                "resultOffset": offset, "resultRecordCount": batch,
                "geometryPrecision": 6,
            }, timeout=60)
            r.raise_for_status()
            chunk = r.json().get("features", [])
            features.extend(chunk)
            print(f"{name}: {len(features)} features...")
            if len(chunk) < batch:
                break
            offset += batch
        gdf = gpd.GeoDataFrame.from_features(
            {"type": "FeatureCollection", "features": features}, crs="EPSG:4326"
        )
        gdf.to_file(path, driver="GeoJSON")
        print(f"Saved {path.name}: {len(gdf)} records")


@lru_cache(maxsize=1)
def _load_layers() -> tuple:
    if not COAL_FILE.exists() or not MSA_FILE.exists():
        return None, None
    return gpd.read_file(COAL_FILE), gpd.read_file(MSA_FILE)


def check_energy_community(lat: float, lon: float) -> dict:
    coal, msa = _load_layers()

    if coal is None:
        return {
            "qualifies": False,
            "coal_closure": False,
            "msa_fossil_fuel": False,
            "community_type": "none",
            "adder_pct": 0,
            "data_available": False,
        }

    point = Point(lon, lat)
    in_coal = not coal[coal.geometry.contains(point)].empty
    in_msa  = not msa[msa.geometry.contains(point)].empty
    qualifies = in_coal or in_msa

    return {
        "qualifies": qualifies,
        "coal_closure": in_coal,
        "msa_fossil_fuel": in_msa,
        "community_type": "coal_closure" if in_coal else ("msa_fossil_fuel" if in_msa else "none"),
        "adder_pct": 10 if qualifies else 0,
        "data_available": True,
    }
