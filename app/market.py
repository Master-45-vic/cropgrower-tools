import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class MarketResponse(BaseModel):
    commodity: str
    market: str
    district: str
    state: str
    price: str
    date: str

@router.get("/market", response_model=MarketResponse)
def get_market_price(crop_name: str):
    csv_path = settings.MARKET_CSV_PATH
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail="Market dataset is currently unavailable.")
        
    try:
        df = pd.read_csv(csv_path)
        
        # Support partial matching (case-insensitive)
        # For example, searching "Tomato" should match "Tomato(Local)", "Tomato Hybrid"
        mask = df['commodity'].str.contains(crop_name, case=False, na=False)
        matched_records = df[mask]
        
        if matched_records.empty:
            raise HTTPException(status_code=404, detail=f"No market data found for crop: {crop_name}")
            
        # If date is available, sort to get the latest record
        if 'date' in df.columns:
            matched_records = matched_records.sort_values(by='date', ascending=False)
            
        latest_record = matched_records.iloc[0]
        
        return MarketResponse(
            commodity=str(latest_record.get('commodity', '')),
            market=str(latest_record.get('market', 'Unknown')),
            district=str(latest_record.get('district', 'Unknown')),
            state=str(latest_record.get('state', 'Unknown')),
            price=f"INR {latest_record.get('price', 'N/A')} / Quintal",
            date=str(latest_record.get('date', 'Unknown'))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error reading market data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing market data.")
