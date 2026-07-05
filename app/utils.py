from fastapi import HTTPException
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def handle_api_error(service_name: str, error: Exception):
    """
    Standardize error handling across different external API calls.
    """
    logger.error(f"Error communicating with {service_name}: {error}")
    raise HTTPException(status_code=502, detail=f"Failed to fetch data from {service_name}. Please try again later.")
