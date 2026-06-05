# Crop water requirements (mm/day)
CROP_WATER_NEEDS = {
    "Tomato"     : {"base": 5.0, "stages": {"seedling": 2.5, "growing": 5.0, "flowering": 6.5, "fruiting": 5.5}},
    "Potato"     : {"base": 4.5, "stages": {"seedling": 2.0, "growing": 4.5, "flowering": 6.0, "fruiting": 4.0}},
    "Corn"       : {"base": 5.5, "stages": {"seedling": 3.0, "growing": 5.5, "flowering": 7.0, "fruiting": 5.0}},
    "Apple"      : {"base": 4.0, "stages": {"dormant": 1.0,  "growing": 4.0, "flowering": 5.0, "fruiting": 4.5}},
    "Grape"      : {"base": 3.5, "stages": {"dormant": 1.0,  "growing": 3.5, "flowering": 4.5, "fruiting": 4.0}},
    "Wheat"      : {"base": 4.0, "stages": {"seedling": 2.0, "growing": 4.0, "flowering": 5.5, "fruiting": 3.5}},
    "Rice"       : {"base": 8.0, "stages": {"seedling": 6.0, "growing": 8.0, "flowering": 9.0, "fruiting": 7.0}},
    "Pepper"     : {"base": 4.5, "stages": {"seedling": 2.5, "growing": 4.5, "flowering": 5.5, "fruiting": 4.5}},
    "Strawberry" : {"base": 3.5, "stages": {"seedling": 2.0, "growing": 3.5, "flowering": 4.5, "fruiting": 4.0}},
    "Soybean"    : {"base": 4.5, "stages": {"seedling": 2.5, "growing": 4.5, "flowering": 6.0, "fruiting": 4.5}},
}

def calculate_irrigation(
    crop: str,
    stage: str,
    temperature: float,
    humidity: float,
    rainfall: float,
    area: float,
    soil_type: str
) -> dict:

    # Base water need
    crop_data   = CROP_WATER_NEEDS.get(crop, {"base": 4.5, "stages": {}})
    base_need   = crop_data["stages"].get(stage, crop_data["base"])

    # Temperature adjustment
    if temperature > 35:
        temp_factor = 1.3
    elif temperature > 30:
        temp_factor = 1.15
    elif temperature < 15:
        temp_factor = 0.8
    else:
        temp_factor = 1.0

    # Humidity adjustment
    if humidity > 80:
        humidity_factor = 0.85
    elif humidity < 40:
        humidity_factor = 1.2
    else:
        humidity_factor = 1.0

    # Soil type adjustment
    soil_factors = {
        "Sandy"  : 1.3,
        "Loamy"  : 1.0,
        "Clay"   : 0.8,
        "Silt"   : 0.9
    }
    soil_factor = soil_factors.get(soil_type, 1.0)

    # Calculate daily water need
    daily_need  = base_need * temp_factor * humidity_factor * soil_factor

    # Subtract rainfall
    net_need    = max(0, daily_need - rainfall)

    # Calculate for area (1 mm = 1 liter per m²)
    area_m2     = area * 10000  # Convert hectares to m²
    total_liters = net_need * area_m2
    total_cubic  = total_liters / 1000

    # Irrigation schedule
    if net_need == 0:
        schedule = "No irrigation needed today — rainfall is sufficient"
        frequency = "Check tomorrow"
    elif net_need < 2:
        schedule = "Light irrigation recommended"
        frequency = "Every 3-4 days"
    elif net_need < 4:
        schedule = "Moderate irrigation needed"
        frequency = "Every 2 days"
    else:
        schedule = "Heavy irrigation required"
        frequency = "Daily"

    return {
        "crop"           : crop,
        "stage"          : stage,
        "daily_need_mm"  : round(daily_need, 2),
        "rainfall_mm"    : rainfall,
        "net_need_mm"    : round(net_need, 2),
        "total_liters"   : round(total_liters),
        "total_cubic_m"  : round(total_cubic, 2),
        "schedule"       : schedule,
        "frequency"      : frequency,
        "best_time"      : "Early morning (5-7 AM) or evening (6-8 PM)",
        "area_hectares"  : area
    }