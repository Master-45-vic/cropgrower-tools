import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils import handle_api_error

router = APIRouter()

class WeatherResponse(BaseModel):
    city: str
    temperature: str
    humidity: str
    pressure: str
    wind_speed: str
    weather: str
    rain_probability: str
    recommendation: str

def get_weather_description(code: int) -> str:
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
        61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
        80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail"
    }
    return weather_codes.get(code, "Unknown")

def generate_recommendation(weather_code: int, rain_prob: int) -> str:
    if rain_prob > 60 or weather_code in [61, 63, 65, 80, 81, 82, 95, 96, 99]:
        return "Rain expected today. Delay irrigation."
    elif weather_code in [0, 1, 2]:
        return "Sunny and clear weather. Suitable for harvesting and spraying."
    elif weather_code in [71, 73, 75, 85, 86]:
        return "Snow expected. Protect sensitive crops."
    else:
        return "Cloudy or mixed weather. Proceed with normal farming activities."

@router.get("/weather", response_model=WeatherResponse)
def get_weather(city: str):
    try:
        # Step 1: Geocoding (City name to Lat/Lon)
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geocode_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            raise HTTPException(status_code=404, detail="City not found.")

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        city_name = location["name"]

        # Step 2: Fetch Weather Data
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weather_code"
            "&daily=precipitation_probability_max&timezone=auto"
        )
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data["current"]
        daily = weather_data["daily"]

        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        pressure = current["surface_pressure"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]
        
        # Get today's max rain probability
        rain_prob = daily["precipitation_probability_max"][0] if "precipitation_probability_max" in daily and len(daily["precipitation_probability_max"]) > 0 else 0

        weather_desc = get_weather_description(weather_code)
        recommendation = generate_recommendation(weather_code, rain_prob)

        return WeatherResponse(
            city=city_name,
            temperature=f"{temp} °C",
            humidity=f"{humidity} %",
            pressure=f"{pressure} hPa",
            wind_speed=f"{wind_speed} km/h",
            weather=weather_desc,
            rain_probability=f"{rain_prob} %",
            recommendation=recommendation
        )

    except HTTPException:
        raise
    except Exception as e:
        handle_api_error("Open-Meteo", e)
