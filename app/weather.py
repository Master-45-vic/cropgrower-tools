import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils import handle_api_error
from app.config import settings

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

def generate_recommendation(weather_desc: str, rain_prob: int) -> str:
    weather_desc_lower = weather_desc.lower()
    
    if rain_prob > 60 or "rain" in weather_desc_lower or "shower" in weather_desc_lower or "thunder" in weather_desc_lower:
        return "Rain expected today. Delay irrigation."
    elif "clear" in weather_desc_lower or "sunny" in weather_desc_lower:
        return "Sunny and clear weather. Suitable for harvesting and spraying."
    elif "snow" in weather_desc_lower or "ice" in weather_desc_lower:
        return "Cold weather/snow expected. Protect sensitive crops."
    else:
        return "Cloudy or mixed weather. Proceed with normal farming activities."

@router.get("/weather", response_model=WeatherResponse)
def get_weather(city: str):
    try:
        # WeatherAPI requires a single request for current and forecast data
        api_key = settings.WEATHER_API_KEY
        weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no"
        
        weather_response = requests.get(weather_url)
        
        # If city is not found, WeatherAPI returns 400 with an error object
        if weather_response.status_code == 400:
            raise HTTPException(status_code=404, detail="City not found.")
            
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        location = weather_data.get("location", {})
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", {}).get("forecastday", [])

        city_name = location.get("name", city)
        temp = current.get("temp_c", "N/A")
        humidity = current.get("humidity", "N/A")
        pressure = current.get("pressure_mb", "N/A")
        wind_speed = current.get("wind_kph", "N/A")
        
        weather_desc = current.get("condition", {}).get("text", "Unknown")
        
        rain_prob = 0
        if forecast and len(forecast) > 0:
            rain_prob = forecast[0].get("day", {}).get("daily_chance_of_rain", 0)

        # Make sure rain_prob is an integer
        try:
            rain_prob = int(rain_prob)
        except (ValueError, TypeError):
            rain_prob = 0

        recommendation = generate_recommendation(weather_desc, rain_prob)

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
        handle_api_error("WeatherAPI", e)
