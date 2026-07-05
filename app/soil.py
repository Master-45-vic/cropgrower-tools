import requests
from fastapi import APIRouter
from pydantic import BaseModel
from app.utils import handle_api_error

router = APIRouter()

class SoilResponse(BaseModel):
    latitude: str
    longitude: str
    soil_type: str
    ph: str
    nitrogen: str
    phosphorus: str
    potassium: str
    organic_carbon: str
    texture: str
    recommendation: str

def get_soil_texture_class(sand: float, silt: float, clay: float) -> str:
    """
    Simple approximation of soil texture class based on sand, silt, and clay percentages.
    """
    if sand + silt + clay == 0:
        return "Unknown"
    
    # Normalize to 100% just in case
    total = sand + silt + clay
    sand_pct = (sand / total) * 100
    silt_pct = (silt / total) * 100
    clay_pct = (clay / total) * 100
    
    if clay_pct >= 40:
        return "Clay"
    elif sand_pct >= 85:
        return "Sand"
    elif silt_pct >= 80:
        return "Silt"
    elif sand_pct >= 45 and clay_pct <= 35:
        return "Sandy Loam"
    elif clay_pct >= 27 and clay_pct <= 40 and sand_pct <= 20:
        return "Silty Clay Loam"
    else:
        return "Loam"

def generate_soil_recommendation(ph: float, texture: str) -> str:
    rec = []
    if ph > 0:
        if ph < 5.5:
            rec.append("Soil is quite acidic; consider applying agricultural lime.")
        elif ph > 7.5:
            rec.append("Soil is alkaline; consider applying sulfur or organic matter.")
        elif 5.5 <= ph <= 7.5:
            rec.append("Soil pH is optimal for most crops (like tomatoes, wheat).")
            
    if "Sand" in texture:
        rec.append("Sandy soil drains quickly; frequent light irrigation is recommended.")
    elif "Clay" in texture:
        rec.append("Clay soil retains water well; avoid overwatering to prevent waterlogging.")
        
    return " ".join(rec)

@router.get("/soil", response_model=SoilResponse)
def get_soil(latitude: float, longitude: float):
    try:
        # Fetch data from SoilGrids API for top 0-5cm
        soilgrids_url = (
            f"https://rest.isric.org/soilgrids/v2.0/properties/query"
            f"?lon={longitude}&lat={latitude}"
            f"&property=phh2o&property=nitrogen&property=soc"
            f"&property=sand&property=silt&property=clay"
            f"&depth=0-5cm"
        )
        
        response = requests.get(soilgrids_url)
        response.raise_for_status()
        data = response.json()
        
        properties = data.get("properties", {}).get("layers", [])
        
        # Helper to extract mean value and apply conversion factor
        def extract_val(prop_name: str, d_factor: float) -> float:
            for layer in properties:
                if layer["name"] == prop_name:
                    depths = layer.get("depths", [])
                    if depths:
                        mean_val = depths[0].get("values", {}).get("mean")
                        if mean_val is not None:
                            return round(mean_val / d_factor, 2)
            return 0.0

        # Extract specific properties
        # phh2o: mapped as pH*10, target is standard pH (d_factor = 10)
        ph_val = extract_val("phh2o", 10.0)
        
        # nitrogen: mapped as cg/kg, target is g/kg (d_factor = 100)
        n_val = extract_val("nitrogen", 100.0)
        
        # soc (organic carbon): mapped as dg/kg, target is g/kg (d_factor = 10)
        oc_val = extract_val("soc", 10.0)
        
        # texture components: mapped as g/kg, target is % (d_factor = 10)
        sand_val = extract_val("sand", 10.0)
        silt_val = extract_val("silt", 10.0)
        clay_val = extract_val("clay", 10.0)
        
        texture_desc = f"Sand {sand_val}%, Silt {silt_val}%, Clay {clay_val}%"
        soil_type = get_soil_texture_class(sand_val, silt_val, clay_val)
        
        recommendation = generate_soil_recommendation(ph_val, soil_type)
        if not recommendation:
            recommendation = "Soil properties appear standard. Proceed with normal cultivation."

        return SoilResponse(
            latitude=str(latitude),
            longitude=str(longitude),
            soil_type=soil_type,
            ph=str(ph_val) if ph_val else "N/A",
            nitrogen=f"{n_val} g/kg" if n_val else "N/A",
            phosphorus="N/A",
            potassium="N/A",
            organic_carbon=f"{oc_val} g/kg" if oc_val else "N/A",
            texture=texture_desc,
            recommendation=recommendation
        )

    except Exception as e:
        handle_api_error("SoilGrids", e)
