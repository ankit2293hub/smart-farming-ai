import requests
import os

def get_weather(city: str) -> dict:
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "")
        if not api_key:
            return {"error": "API key not configured"}

        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if "error" in data:
            return {"error": data["error"]["message"]}

        weather = {
            "city"        : data["location"]["name"],
            "temperature" : data["current"]["temp_c"],
            "humidity"    : data["current"]["humidity"],
            "description" : data["current"]["condition"]["text"],
            "wind_speed"  : data["current"]["wind_kph"],
            "feels_like"  : data["current"]["feelslike_c"],
        }
        weather["disease_risk"] = calculate_disease_risk(
            weather["temperature"],
            weather["humidity"]
        )
        return weather

    except Exception as e:
        return {"error": str(e)}


def calculate_disease_risk(temp: float, humidity: float) -> dict:
    risks = {}

    if humidity > 80 and 10 < temp < 24:
        risks["Late Blight"]      = "🔴 High"
    elif humidity > 70 and 10 < temp < 24:
        risks["Late Blight"]      = "🟡 Medium"
    else:
        risks["Late Blight"]      = "🟢 Low"

    if 20 < temp < 30 and humidity < 60:
        risks["Powdery Mildew"]   = "🔴 High"
    elif 15 < temp < 30 and humidity < 70:
        risks["Powdery Mildew"]   = "🟡 Medium"
    else:
        risks["Powdery Mildew"]   = "🟢 Low"

    if humidity > 75 and 15 < temp < 25:
        risks["Rust"]             = "🔴 High"
    elif humidity > 65 and 15 < temp < 25:
        risks["Rust"]             = "🟡 Medium"
    else:
        risks["Rust"]             = "🟢 Low"

    if humidity > 80 and temp > 28:
        risks["Bacterial Blight"] = "🔴 High"
    elif humidity > 70 and temp > 25:
        risks["Bacterial Blight"] = "🟡 Medium"
    else:
        risks["Bacterial Blight"] = "🟢 Low"

    return risks