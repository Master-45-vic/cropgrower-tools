import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CropGrower Tools API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "External REST APIs for the CropGrower AI Assistant."
    
    MARKET_CSV_PATH: str = os.getenv("MARKET_CSV_PATH", "mandi_data.csv")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "66339df4c7f94263a6d131314260507")
    DATAGOV_API_KEY: str = os.getenv("DATAGOV_API_KEY", "579b464db66ec23bdd0000018de39ddd27d94fda6a49cf4c626394a9")

settings = Settings()
