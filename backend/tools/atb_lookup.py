# Approximate capacity factors by technology and region
# Source: NREL 2024 ATB
ATB_CAPACITY_FACTORS = {
    "solar": {
        "southwest": 0.29,   # CA, AZ, NV, NM
        "southeast": 0.24,
        "midwest": 0.21,
        "northeast": 0.18,
        "northwest": 0.20,
        "default": 0.22
    },
    "wind_onshore": {
        "great_plains": 0.45,  # TX, KS, OK, ND, SD
        "midwest": 0.38,
        "southeast": 0.28,
        "northeast": 0.32,
        "default": 0.35
    },
    "wind_offshore": {
        "northeast": 0.45,
        "southeast": 0.40,
        "default": 0.42
    },
    "geothermal": {"default": 0.85},
    "hydro": {"default": 0.40},
    "storage": {"default": None}  # storage doesn't have a capacity factor
}