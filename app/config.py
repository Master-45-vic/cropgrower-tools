import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CropGrower Tools API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "External REST APIs for the CropGrower AI Assistant."
    
    # Path to the local CSV database for market data
    MARKET_CSV_PATH: str = os.getenv("MARKET_CSV_PATH", "mandi_data.csv")

settings = Settings()
