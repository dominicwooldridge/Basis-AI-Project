def get_wind_capacity_factor(lat, lon, api_key):
    url = "https://developer.nlr.gov/api/wind-toolkit/v2/wind/wtk-srw-download"
    params = {
        "api_key": api_key,
        "lat": lat,
        "lon": lon,
        "year": 2023,
        "hub_height": 100,     # meters, typical utility-scale
        "email": "your@email.com"
    }
    # Wind Toolkit returns a CSV file via email for large requests
    # For capacity factor estimates, use ATB lookup table instead (see below)
    r = requests.get(url, params=params)
    return r