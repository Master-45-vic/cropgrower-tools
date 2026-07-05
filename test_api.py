from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /weather...")
response = client.get("/weather?city=Mumbai")
print("Status:", response.status_code)
print("JSON:", response.json())
print("-" * 50)

print("Testing /soil...")
response = client.get("/soil?latitude=19.0760&longitude=72.8777")
print("Status:", response.status_code)
print("JSON:", response.json())
print("-" * 50)

print("Testing /market...")
response = client.get("/market?crop_name=Tomato")
print("Status:", response.status_code)
print("JSON:", response.json())
print("-" * 50)

print("Testing /openapi.json...")
response = client.get("/openapi.json")
print("Status:", response.status_code)
if response.status_code == 200:
    print("OpenAPI spec available!")
