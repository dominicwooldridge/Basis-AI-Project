import requests

def get_solar_capacity_factor(lat, lon, system_capacity_kw, api_key):
    url = "https://developer.nlr.gov/api/pvwatts/v8/json"
    params = {
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "system_capacity": system_capacity_kw,
        "azimuth": 180,        # south-facing
        "tilt": lat * 0.76,    # optimal tilt approximation
        "array_type": 1,       # fixed open rack
        "module_type": 0,      # standard
        "losses": 14           # typical system losses %
    }
    r = requests.get(url, params=params)
    data = r.json()
    
    annual_kwh = data["outputs"]["ac_annual"]
    capacity_factor = annual_kwh / (system_capacity_kw * 8760)
    return round(capacity_factor, 4)