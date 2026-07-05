# CropGrower Tools API

This project provides external REST APIs for the CropGrower AI assistant. It includes tools for checking live weather, soil conditions, and market (mandi) prices.

## Features

- **Weather API (`/weather`)**: Fetches live weather conditions using the free Open-Meteo API.
- **Soil API (`/soil`)**: Retrieves soil properties (pH, Nitrogen, Organic Carbon, Texture) using the free SoilGrids REST API.
- **Market API (`/market`)**: Retrieves crop market prices using a locally queryable dataset.

## Installation

1. Clone this repository:
```bash
git clone <repository_url>
cd cropgrower-tools
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

Run the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Testing APIs

You can test the APIs directly via the automatically generated Swagger UI:
- Open your browser and go to: `http://127.0.0.1:8000/docs`

You can also use `curl` or Postman:
```bash
curl "http://127.0.0.1:8000/weather?city=Mumbai"
curl "http://127.0.0.1:8000/soil?latitude=19.0760&longitude=72.8777"
curl "http://127.0.0.1:8000/market?crop_name=Tomato"
```

## Deployment

The project is designed to be easily deployable on modern PaaS platforms without code changes.

### Render
1. Create a new "Web Service" on Render.
2. Connect your repository.
3. Render will automatically detect the `Dockerfile`.
4. Leave the start command empty (handled by Dockerfile).
5. Click "Create Web Service".

### Railway / IBM Cloud
Similar to Render, simply connect your repository or push your Docker image to the respective container registry, and deploy using the provided `Dockerfile`.

## Importing to IBM watsonx.ai Agent Lab

To import these tools into IBM watsonx.ai Agent Lab:
1. Deploy the API so it is publicly accessible.
2. Obtain your deployed OpenAPI specification URL (e.g., `https://your-app-url.com/openapi.json`).
3. In IBM Agent Lab, add a new tool and select the **OpenAPI** option.
4. Provide the URL to your `openapi.json` file. The lab will automatically discover the `/weather`, `/soil`, and `/market` endpoints.

## Notes
- **Market API**: The current market API searches a local `mandi_data.csv` dataset since a reliable free live Mandi API is unavailable. You can update this CSV file with fresh data from data.gov.in or Agmarknet.
- **Soil API**: The SoilGrids API provides standard properties like pH, Nitrogen, and Texture. It does not provide Phosphorus or Potassium in its basic query, so those are returned as "N/A".
