import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> dict:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return {"error": "City not found"}

        weather = {
            "city"        : data["name"],
            "temperature" : data["main"]["temp"],
            "humidity"    : data["main"]["humidity"],
            "description" : data["weather"][0]["description"],
            "wind_speed"  : data["wind"]["speed"],
            "feels_like"  : data["main"]["feels_like"],
        }

        # Disease risk based on weather
        weather["disease_risk"] = calculate_disease_risk(
            weather["temperature"],
            weather["humidity"]
        )

        return weather

    except Exception as e:
        return {"error": str(e)}


def calculate_disease_risk(temp: float, humidity: float) -> dict:
    risks = {}

    # Late blight risk (potato/tomato) — loves cool humid weather
    if humidity > 80 and 10 < temp < 24:
        risks["Late Blight"]       = "🔴 High"
    elif humidity > 70 and 10 < temp < 24:
        risks["Late Blight"]       = "🟡 Medium"
    else:
        risks["Late Blight"]       = "🟢 Low"

    # Powdery mildew — warm dry weather
    if 20 < temp < 30 and humidity < 60:
        risks["Powdery Mildew"]    = "🔴 High"
    elif 15 < temp < 30 and humidity < 70:
        risks["Powdery Mildew"]    = "🟡 Medium"
    else:
        risks["Powdery Mildew"]    = "🟢 Low"

    # Rust — warm humid weather
    if humidity > 75 and 15 < temp < 25:
        risks["Rust"]              = "🔴 High"
    elif humidity > 65 and 15 < temp < 25:
        risks["Rust"]              = "🟡 Medium"
    else:
        risks["Rust"]              = "🟢 Low"

    # Bacterial blight — hot humid weather
    if humidity > 80 and temp > 28:
        risks["Bacterial Blight"]  = "🔴 High"
    elif humidity > 70 and temp > 25:
        risks["Bacterial Blight"]  = "🟡 Medium"
    else:
        risks["Bacterial Blight"]  = "🟢 Low"

    return risks