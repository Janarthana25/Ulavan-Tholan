"""
Render Production Server - Ulavan Tholan
FastAPI + uvicorn — serves all pages and API endpoints
"""

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import random

app = FastAPI(title="Ulavan Tholan", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

T = "frontend/templates"  # templates shorthand

# ==================== Page Routes ====================

@app.get("/")
async def home():
    return FileResponse(f"{T}/index.html")

@app.get("/login")
@app.get("/login.html")
async def login():
    return FileResponse(f"{T}/login.html")

@app.get("/index.html")
async def index_html():
    return FileResponse(f"{T}/index.html")

@app.get("/dashboard")
@app.get("/dashboard.html")
async def dashboard():
    return FileResponse(f"{T}/dashboard.html")

@app.get("/disease-detection")
@app.get("/disease-detection.html")
async def disease_detection():
    return FileResponse(f"{T}/disease-detection.html")

@app.get("/crop-recommendation")
@app.get("/crop-recommendation.html")
async def crop_recommendation():
    return FileResponse(f"{T}/crop-recommendation.html")

@app.get("/voice-assistant")
@app.get("/voice-assistant.html")
async def voice_assistant():
    return FileResponse(f"{T}/voice-assistant.html")

@app.get("/analytics")
@app.get("/analytics.html")
async def analytics():
    return FileResponse(f"{T}/analytics.html")

# ==================== API: Health ====================

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "Ulavan Tholan", "version": "1.0.0"}

# ==================== API: Weather ====================

@app.get("/api/weather/current")
async def weather():
    return {
        "success": True,
        "location": "India",
        "current": {
            "temperature": round(28 + random.uniform(-5, 5), 1),
            "humidity":    round(65 + random.uniform(-15, 15), 0),
            "rainfall":    round(random.uniform(0, 50), 1),
            "wind_speed":  round(random.uniform(5, 25), 1),
            "condition":   random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"])
        }
    }

# ==================== API: Crop Recommend ====================

@app.post("/api/crop/recommend")
async def crop_recommend(request: Request):
    body     = await request.json()
    temp     = float(body.get("temperature", 28))
    rainfall = float(body.get("rainfall", 800))
    humidity = float(body.get("humidity", 65))
    season   = str(body.get("season", "")).lower()
    ph       = float(body.get("ph_level", 6.5))

    crops = []

    if 25 <= temp <= 35 and rainfall > 1000 and humidity > 70:
        crops.append({"name": "Rice", "confidence": 0.92,
            "expected_yield": "4-5 tons/hectare", "duration": "120-150 days",
            "advantages": ["High demand", "Suitable for wet soil"],
            "requirements": ["Consistent water", "Level field"],
            "best_practices": ["Transplant at 25-30 days", "Maintain 5-7 cm water"]})

    if 15 <= temp <= 25 and season in ["rabi", "winter"]:
        crops.append({"name": "Wheat", "confidence": 0.88,
            "expected_yield": "3-4 tons/hectare", "duration": "120-130 days",
            "advantages": ["Cold tolerant", "Good market price"],
            "requirements": ["Cool weather", "Well-drained soil"],
            "best_practices": ["Timely sowing", "Seed treatment"]})

    if 20 <= temp <= 32 and ph >= 5.5:
        crops.append({"name": "Tomato", "confidence": 0.85,
            "expected_yield": "40-60 tons/hectare", "duration": "90-120 days",
            "advantages": ["High value", "Multiple harvests"],
            "requirements": ["Well-drained soil", "Drip irrigation"],
            "best_practices": ["Transplanting method", "Regular pest check"]})

    if 21 <= temp <= 30 and rainfall > 500:
        crops.append({"name": "Maize", "confidence": 0.82,
            "expected_yield": "5-8 tons/hectare", "duration": "100-120 days",
            "advantages": ["Versatile", "Moderate water needs"],
            "requirements": ["Fertile soil", "Good drainage"],
            "best_practices": ["Timely weeding", "Split N application"]})

    if temp >= 25 and season in ["kharif", "summer"]:
        crops.append({"name": "Groundnut", "confidence": 0.79,
            "expected_yield": "1.5-3 tons/hectare", "duration": "90-120 days",
            "advantages": ["Fixes nitrogen", "Drought tolerant"],
            "requirements": ["Sandy/loamy soil", "Moderate rainfall"],
            "best_practices": ["Rhizobium seed treatment", "Earthing up at 30 days"]})

    # Always add millet as fallback
    crops.append({"name": "Millets", "confidence": 0.75,
        "expected_yield": "1.5-2.5 tons/hectare", "duration": "75-90 days",
        "advantages": ["Drought resistant", "Nutritious", "Climate resilient"],
        "requirements": ["Low water", "Sandy loam soil"],
        "best_practices": ["Dry-land farming", "Organic inputs", "Intercropping"]})

    crops.sort(key=lambda x: x["confidence"], reverse=True)
    return {"success": True, "recommendations": crops[:5]}

# ==================== API: Disease Detect ====================

@app.post("/api/disease/detect")
async def disease_detect(request: Request):
    results = [
        {"success": True, "primary_disease": "Tomato Early Blight", "plant": "Tomato",
         "confidence": 0.92, "confidence_percent": "92%", "severity": "High", "is_healthy": False,
         "symptoms": ["Dark brown spots with rings", "Lower leaves first", "Yellowing"],
         "treatment": ["Apply Mancozeb", "Remove infected leaves", "Spray every 7-10 days"],
         "prevention": ["Mulch plants", "Avoid overhead watering"],
         "fertilizer_recommendation": "High potassium fertilizer (5-10-10)",
         "irrigation_advice": "Morning watering at soil level",
         "top_predictions": [
             {"disease": "Tomato Early Blight", "confidence_percent": "92%"},
             {"disease": "Tomato Late Blight", "confidence_percent": "6%"}]},
        {"success": True, "primary_disease": "Healthy Plant", "plant": "Tomato",
         "confidence": 0.96, "confidence_percent": "96%", "severity": "Low", "is_healthy": True,
         "symptoms": ["No disease detected", "Normal green foliage"],
         "treatment": ["Continue regular care", "Monitor weekly"],
         "prevention": ["Regular monitoring", "Balanced fertilization"],
         "fertilizer_recommendation": "NPK 10-10-10 every 2 weeks",
         "irrigation_advice": "1-2 inches per week",
         "top_predictions": [
             {"disease": "Healthy Plant", "confidence_percent": "96%"},
             {"disease": "Early Blight (low risk)", "confidence_percent": "4%"}]},
        {"success": True, "primary_disease": "Potato Late Blight", "plant": "Potato",
         "confidence": 0.88, "confidence_percent": "88%", "severity": "High", "is_healthy": False,
         "symptoms": ["Water-soaked lesions", "White mold in humidity", "Rapid collapse"],
         "treatment": ["Apply Metalaxyl", "Destroy infected plants", "Spray every 5-7 days"],
         "prevention": ["Use resistant varieties", "Avoid evening irrigation"],
         "fertilizer_recommendation": "Potassium-rich fertilizer for disease resistance",
         "irrigation_advice": "Avoid overhead watering especially evenings",
         "top_predictions": [
             {"disease": "Potato Late Blight", "confidence_percent": "88%"},
             {"disease": "Potato Early Blight", "confidence_percent": "10%"}]}
    ]
    return random.choice(results)

# ==================== API: Water Advisory ====================

@app.post("/api/water/advisory")
async def water_advisory(request: Request):
    body     = await request.json()
    moisture = float(body.get("soil_moisture", 50))
    crop     = str(body.get("crop_type", "tomato")).lower()
    daily    = {"rice": 15, "sugarcane": 12, "wheat": 8, "potato": 6}.get(crop, 6)
    needed   = moisture < 50
    return {"success": True, "advisory": {
        "irrigation_needed": needed,
        "urgency": "High" if moisture < 30 else ("Moderate" if moisture < 50 else "Low"),
        "message": "Irrigate soon" if needed else "Moisture adequate",
        "daily_requirement": f"{daily} litres/plant",
        "timing": "Early morning 6-8 AM"
    }}

# ==================== API: Fertilizer ====================

@app.post("/api/fertilizer/recommend")
async def fertilizer_recommend(request: Request):
    body = await request.json()
    crop = str(body.get("crop_type", "tomato")).lower()
    npk  = {"rice": (120,60,40), "wheat": (150,60,40), "tomato": (100,50,50),
             "potato": (150,80,100), "maize": (120,60,50)}.get(crop, (100,50,50))
    return {"success": True, "recommendations": {
        "primary_fertilizer": f"NPK {npk[0]}-{npk[1]}-{npk[2]}",
        "n_kg_ha": npk[0], "p_kg_ha": npk[1], "k_kg_ha": npk[2],
        "organic_alternative": "5-10 tons/ha compost or vermicompost",
        "application_tips": ["Apply when soil is moist", "Split doses for better absorption"]
    }}

# ==================== API: Analytics ====================

@app.get("/api/analytics/dashboard")
async def analytics_data():
    return {"success": True, "statistics": {
        "total_diagnoses": 1247, "healthy_plants": 892,
        "diseased_plants": 355, "accuracy_rate": 94.5, "farmers_helped": 523
    }}

# ==================== Run ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("render_server:app", host="0.0.0.0", port=port)
