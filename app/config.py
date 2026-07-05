import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CropGrower Tools API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "External REST APIs for the CropGrower AI Assistant."
    
    # Path to the local CSV database for market data
    MARKET_CSV_PATH: str = os.getenv("MARKET_CSV_PATH", "mandi_data.csv")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "66339df4c7f94263a6d131314260507")

settings = Settings()
