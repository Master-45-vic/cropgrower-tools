import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.config import settings

router = APIRouter()

class MarketPrice(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    min_price: str
    max_price: str
    modal_price: str
    arrival_date: str

class MarketResponse(BaseModel):
    crop: str
    state: Optional[str] = None
    records_found: int
    prices: List[MarketPrice]

@router.get("/market", response_model=MarketResponse)
def get_market_price(crop: str = Query(..., description="Name of the crop/commodity"), state: Optional[str] = Query(None, description="Name of the state")):
    api_key = settings.DATAGOV_API_KEY
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    # Capitalize first letters as data.gov.in usually expects title case for commodities and states
    crop_formatted = crop.title()
    
    query_params = {
        "api-key": api_key,
        "format": "json",
        "limit": "10",
        "filters[commodity]": crop_formatted
    }
    
    if state:
        query_params["filters[state]"] = state.title()

    try:
        # We use a custom User-Agent because data.gov.in sometimes blocks default python-requests
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, params=query_params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Check if the API returned an error message in the body
        if data.get("status") == "error":
            raise HTTPException(status_code=502, detail=f"Data.gov.in API Error: {data.get('message', 'Unknown error')}")
            
        records = data.get("records", [])
        
        parsed_prices = []
        for row in records:
            parsed_prices.append(
                MarketPrice(
                    state=row.get("state", "Unknown"),
                    district=row.get("district", "Unknown"),
                    market=row.get("market", "Unknown"),
                    commodity=row.get("commodity", "Unknown"),
                    min_price=f"INR {row.get('min_price', 'N/A')} per Quintal",
                    max_price=f"INR {row.get('max_price', 'N/A')} per Quintal",
                    modal_price=f"INR {row.get('modal_price', 'N/A')} per Quintal",
                    arrival_date=row.get("arrival_date", "Unknown")
                )
            )
            
        return MarketResponse(
            crop=crop_formatted,
            state=state.title() if state else "All India",
            records_found=len(parsed_prices),
            prices=parsed_prices
        )

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="The Government Mandi API (data.gov.in) is currently responding too slowly or is down. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch data from data.gov.in: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
