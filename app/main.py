from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.config import settings
from app.weather import router as weather_router
from app.soil import router as soil_router
from app.market import router as market_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    servers=[
        {
            "url": "https://cropgrower-tools.onrender.com",
            "description": "Production Server"
        }
    ]
)

# Include the tool routers
app.include_router(weather_router, tags=["Weather"])
app.include_router(soil_router, tags=["Soil"])
app.include_router(market_router, tags=["Market"])

@app.get("/", include_in_schema=False)
def read_root():
    """
    Redirect the root URL to the Swagger documentation.
    """
    return RedirectResponse(url="/docs")
