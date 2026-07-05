"""
Ulavan Tholan - FastAPI Backend
AI-Powered Smart Agriculture Platform
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
import shutil
from datetime import datetime
import json
import random

# Import ML predictor
from backend.ml.predictor import get_predictor

# Initialize FastAPI app
app = FastAPI(
    title="Ulavan Tholan API",
    description="AI-Powered Smart Agriculture Platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Create uploads directory
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==================== Pydantic Models ====================

class CropRecommendationRequest(BaseModel):
    soil_type: str
    temperature: float
    humidity: float
    rainfall: float
    season: str
    ph_level: Optional[float] = 6.5

class WaterAdvisoryRequest(BaseModel):
    crop_type: str
    soil_moisture: float
    temperature: float
    rainfall: float
    growth_stage: str

class FertilizerRequest(BaseModel):
    crop_type: str
    soil_type: str
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None

# ==================== Root & Health ====================

@app.get("/")
async def root():
    """Root endpoint - serve frontend"""
    return FileResponse("frontend/templates/index.html")

@app.get("/login")
async def login():
    """Serve login page"""
    return FileResponse("frontend/templates/login.html")

@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "service": "Ulavan Tholan API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ==================== Disease Detection ====================

@app.post("/api/disease/detect")
async def detect_disease(file: UploadFile = File(...)):
    """
    Detect plant disease from uploaded image
    Returns: Disease name, confidence, treatment, prevention
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get prediction
        predictor = get_predictor()
        result = predictor.predict(filepath)
        
        if result['success']:
            # Add file info to result
            result['uploaded_file'] = filename
            result['upload_time'] = datetime.now().isoformat()
            
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Prediction failed'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@app.get("/api/disease/history")
async def get_disease_history():
    """Get disease detection history"""
    # Mock data - in production, fetch from database
    history = [
        {
            "id": 1,
            "date": "2026-07-03",
            "plant": "Tomato",
            "disease": "Early Blight",
            "confidence": 0.92,
            "severity": "High"
        },
        {
            "id": 2,
            "date": "2026-07-02",
            "plant": "Potato",
            "disease": "Healthy",
            "confidence": 0.95,
            "severity": "None"
        },
        {
            "id": 3,
            "date": "2026-07-01",
            "plant": "Pepper",
            "disease": "Bacterial Spot",
            "confidence": 0.88,
            "severity": "Moderate"
        }
    ]
    return {"success": True, "history": history, "count": len(history)}

# ==================== Crop Recommendation ====================

@app.post("/api/crop/recommend")
async def recommend_crop(request: CropRecommendationRequest):
    """
    Recommend suitable crops based on environmental conditions
    """
    try:
        # Crop recommendation logic (simplified)
        crops = _get_crop_recommendations(
            request.soil_type,
            request.temperature,
            request.humidity,
            request.rainfall,
            request.season,
            request.ph_level
        )
        
        return {
            "success": True,
            "recommendations": crops,
            "conditions": {
                "soil_type": request.soil_type,
                "temperature": request.temperature,
                "humidity": request.humidity,
                "rainfall": request.rainfall,
                "season": request.season,
                "ph_level": request.ph_level
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_crop_recommendations(soil_type, temperature, humidity, rainfall, season, ph_level):
    """Internal crop recommendation logic"""
    crops = []
    
    # Rice
    if 25 <= temperature <= 35 and rainfall > 1000 and humidity > 70:
        crops.append({
            "name": "Rice",
            "confidence": 0.92,
            "expected_yield": "4-5 tons/hectare",
            "duration": "120-150 days",
            "advantages": ["High market demand", "Suitable for wet conditions", "Multiple varieties available"],
            "requirements": ["Consistent water supply", "Well-leveled field", "Organic matter rich soil"],
            "best_practices": ["Transplant at 25-30 days", "Maintain 2-3 inches water", "Apply nitrogen in splits"]
        })
    
    # Wheat
    if 15 <= temperature <= 25 and 400 <= rainfall <= 800 and season.lower() in ['winter', 'rabi']:
        crops.append({
            "name": "Wheat",
            "confidence": 0.88,
            "expected_yield": "3-4 tons/hectare",
            "duration": "120-130 days",
            "advantages": ["Cold tolerant", "Good market price", "Established value chain"],
            "requirements": ["Cool weather", "Well-drained soil", "2-3 irrigations"],
            "best_practices": ["Timely sowing", "Seed treatment", "Weed management"]
        })
    
    # Tomato
    if 20 <= temperature <= 30 and ph_level >= 6.0:
        crops.append({
            "name": "Tomato",
            "confidence": 0.85,
            "expected_yield": "40-60 tons/hectare",
            "duration": "90-120 days",
            "advantages": ["High value crop", "Multiple harvests", "Good processing demand"],
            "requirements": ["Well-drained soil", "Regular irrigation", "Staking support"],
            "best_practices": ["Transplanting method", "Drip irrigation", "Regular pest monitoring"]
        })
    
    # Maize/Corn
    if 21 <= temperature <= 30 and rainfall > 500:
        crops.append({
            "name": "Maize (Corn)",
            "confidence": 0.82,
            "expected_yield": "5-8 tons/hectare",
            "duration": "100-120 days",
            "advantages": ["Versatile crop", "Multiple uses", "Moderate water requirement"],
            "requirements": ["Fertile soil", "Good drainage", "Adequate spacing"],
            "best_practices": ["Timely weeding", "Split nitrogen application", "Pest control"]
        })
    
    # Cotton
    if temperature > 25 and 600 <= rainfall <= 1200 and season.lower() in ['summer', 'kharif']:
        crops.append({
            "name": "Cotton",
            "confidence": 0.79,
            "expected_yield": "2-3 tons/hectare",
            "duration": "150-180 days",
            "advantages": ["Cash crop", "Long growing season", "Industrial demand"],
            "requirements": ["Black soil preferred", "Warm weather", "Pest management"],
            "best_practices": ["Bt varieties", "Integrated pest management", "Proper spacing"]
        })
    
    # Sugarcane
    if 25 <= temperature <= 35 and rainfall > 1500:
        crops.append({
            "name": "Sugarcane",
            "confidence": 0.80,
            "expected_yield": "80-100 tons/hectare",
            "duration": "12-18 months",
            "advantages": ["High biomass", "Ratoon crops", "Sugar industry support"],
            "requirements": ["High water requirement", "Fertile soil", "Long duration"],
            "best_practices": ["Healthy seed cane", "Trash mulching", "Earthing up"]
        })
    
    # Default recommendation if no crops match
    if not crops:
        crops.append({
            "name": "Millets (Bajra/Jowar)",
            "confidence": 0.75,
            "expected_yield": "1.5-2.5 tons/hectare",
            "duration": "75-90 days",
            "advantages": ["Drought resistant", "Nutritious", "Climate resilient"],
            "requirements": ["Low water requirement", "Sandy loam soil", "Minimal inputs"],
            "best_practices": ["Dry land farming", "Intercropping", "Organic farming"]
        })
    
    # Sort by confidence
    crops.sort(key=lambda x: x['confidence'], reverse=True)
    
    return crops[:5]  # Return top 5

# ==================== Water Advisory ====================

@app.post("/api/water/advisory")
async def water_advisory(request: WaterAdvisoryRequest):
    """
    Provide irrigation recommendations
    """
    try:
        advisory = _calculate_water_advisory(
            request.crop_type,
            request.soil_moisture,
            request.temperature,
            request.rainfall,
            request.growth_stage
        )
        
        return {
            "success": True,
            "advisory": advisory,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _calculate_water_advisory(crop_type, soil_moisture, temperature, rainfall, growth_stage):
    """Calculate irrigation recommendations"""
    
    # Base water requirement (liters per day per plant)
    water_req_map = {
        "rice": 15,
        "wheat": 8,
        "tomato": 5,
        "potato": 6,
        "cotton": 7,
        "sugarcane": 12,
        "maize": 6
    }
    
    base_req = water_req_map.get(crop_type.lower(), 5)
    
    # Adjust for growth stage
    stage_multiplier = {
        "seedling": 0.6,
        "vegetative": 1.0,
        "flowering": 1.3,
        "fruiting": 1.4,
        "maturity": 0.8
    }
    
    multiplier = stage_multiplier.get(growth_stage.lower(), 1.0)
    daily_requirement = base_req * multiplier
    
    # Adjust for temperature
    if temperature > 35:
        daily_requirement *= 1.3
    elif temperature > 30:
        daily_requirement *= 1.15
    
    # Check soil moisture
    if soil_moisture < 30:
        irrigation_needed = True
        urgency = "High"
        message = "⚠️ Immediate irrigation required"
    elif soil_moisture < 50:
        irrigation_needed = True
        urgency = "Moderate"
        message = "💧 Irrigation recommended soon"
    else:
        irrigation_needed = False
        urgency = "Low"
        message = "✅ Soil moisture is adequate"
    
    # Rainfall adjustment
    if rainfall > 10:
        irrigation_needed = False
        message = "🌧️ Recent rainfall sufficient"
    
    return {
        "irrigation_needed": irrigation_needed,
        "urgency": urgency,
        "message": message,
        "daily_requirement": f"{daily_requirement:.1f} liters/plant",
        "soil_moisture_status": f"{soil_moisture}%",
        "optimal_moisture": "60-80%",
        "next_irrigation": "Tomorrow morning" if irrigation_needed else "Monitor in 2-3 days",
        "irrigation_method": "Drip irrigation recommended",
        "timing": "Early morning (6-8 AM) or evening (6-8 PM)",
        "rainfall_forecast": "Check local forecast",
        "water_conservation_tips": [
            "Use mulch to retain moisture",
            "Drip irrigation saves 30-50% water",
            "Avoid irrigation during hot midday",
            "Check soil moisture before watering"
        ]
    }

# ==================== Weather ====================

@app.get("/api/weather/current")
async def get_weather(location: str = "India"):
    """Get current weather data"""
    # Mock weather data - in production, integrate actual weather API
    weather = {
        "success": True,
        "location": location,
        "current": {
            "temperature": round(28 + random.uniform(-5, 5), 1),
            "humidity": round(65 + random.uniform(-15, 15), 0),
            "rainfall": round(random.uniform(0, 50), 1),
            "wind_speed": round(random.uniform(5, 25), 1),
            "condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]),
            "uv_index": random.randint(3, 10)
        },
        "forecast": [
            {
                "day": "Today",
                "temp_max": 32,
                "temp_min": 24,
                "rainfall": 5,
                "condition": "Partly Cloudy"
            },
            {
                "day": "Tomorrow",
                "temp_max": 31,
                "temp_min": 23,
                "rainfall": 12,
                "condition": "Rainy"
            },
            {
                "day": "Day 3",
                "temp_max": 30,
                "temp_min": 22,
                "rainfall": 8,
                "condition": "Cloudy"
            }
        ],
        "farming_advice": [
            "Good conditions for outdoor activities",
            "Monitor for afternoon thunderstorms",
            "Optimal for pesticide application in morning"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    return weather

# ==================== Fertilizer Recommendation ====================

@app.post("/api/fertilizer/recommend")
async def recommend_fertilizer(request: FertilizerRequest):
    """Recommend fertilizers based on crop and soil"""
    try:
        recommendations = _get_fertilizer_recommendations(
            request.crop_type,
            request.soil_type,
            request.nitrogen,
            request.phosphorus,
            request.potassium
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_fertilizer_recommendations(crop_type, soil_type, nitrogen, phosphorus, potassium):
    """Get fertilizer recommendations"""
    
    crop_requirements = {
        "rice": {"N": 120, "P": 60, "K": 40},
        "wheat": {"N": 150, "P": 60, "K": 40},
        "tomato": {"N": 100, "P": 50, "K": 50},
        "potato": {"N": 150, "P": 80, "K": 100},
        "cotton": {"N": 120, "P": 60, "K": 60},
        "maize": {"N": 120, "P": 60, "K": 50}
    }
    
    req = crop_requirements.get(crop_type.lower(), {"N": 100, "P": 50, "K": 50})
    
    # Calculate deficiency
    n_deficit = req["N"] - (nitrogen or 0)
    p_deficit = req["P"] - (phosphorus or 0)
    k_deficit = req["K"] - (potassium or 0)
    
    recommendations = {
        "primary_fertilizer": f"NPK {req['N']}-{req['P']}-{req['K']}",
        "application_schedule": [
            {
                "stage": "Basal (At planting)",
                "npk": f"{req['N']//3}-{req['P']}-{req['K']//2}",
                "quantity": "200 kg/hectare",
                "timing": "Just before planting"
            },
            {
                "stage": "Top dressing 1",
                "npk": f"{req['N']//3}-0-{req['K']//2}",
                "quantity": "150 kg/hectare",
                "timing": "3-4 weeks after planting"
            },
            {
                "stage": "Top dressing 2",
                "npk": f"{req['N']//3}-0-0",
                "quantity": "100 kg/hectare",
                "timing": "6-7 weeks after planting"
            }
        ],
        "organic_alternatives": [
            "Compost: 5-10 tons/hectare",
            "Vermicompost: 2-3 tons/hectare",
            "Green manure: Grow and incorporate before planting",
            "Farmyard manure: 10-15 tons/hectare"
        ],
        "micronutrients": [
            "Zinc sulfate: 25 kg/hectare",
            "Boron: 5 kg/hectare",
            "Iron chelate: As foliar spray"
        ],
        "application_tips": [
            "Apply fertilizers when soil has adequate moisture",
            "Avoid application before heavy rain",
            "Mix with soil, don't leave on surface",
            "Use split application for better efficiency",
            "Foliar spray for quick nutrient boost"
        ],
        "soil_amendments": [
            f"Add lime if pH < 6.0" if soil_type else "Test soil pH regularly",
            "Gypsum for sodic soils",
            "Organic matter improves all soil types"
        ]
    }
    
    return recommendations

# ==================== Analytics ====================

@app.get("/api/analytics/dashboard")
async def get_analytics():
    """Get dashboard analytics data"""
    return {
        "success": True,
        "statistics": {
            "total_diagnoses": 1247,
            "healthy_plants": 892,
            "diseased_plants": 355,
            "accuracy_rate": 94.5,
            "farmers_helped": 523
        },
        "disease_distribution": [
            {"disease": "Early Blight", "count": 89, "percentage": 25.1},
            {"disease": "Late Blight", "count": 67, "percentage": 18.9},
            {"disease": "Bacterial Spot", "count": 54, "percentage": 15.2},
            {"disease": "Leaf Mold", "count": 43, "percentage": 12.1},
            {"disease": "Others", "count": 102, "percentage": 28.7}
        ],
        "monthly_trends": [
            {"month": "Jan", "diagnoses": 98},
            {"month": "Feb", "diagnoses": 112},
            {"month": "Mar", "diagnoses": 145},
            {"month": "Apr", "diagnoses": 187},
            {"month": "May", "diagnoses": 223},
            {"month": "Jun", "diagnoses": 267},
            {"month": "Jul", "diagnoses": 215}
        ],
        "crop_analytics": [
            {"crop": "Tomato", "count": 423, "health_rate": 71.4},
            {"crop": "Potato", "count": 389, "health_rate": 68.9},
            {"crop": "Pepper", "count": 267, "health_rate": 75.3},
            {"crop": "Others", "count": 168, "health_rate": 72.6}
        ]
    }

# ==================== Run Server ====================

if __name__ == "__main__":
    print("🌱 Starting Ulavan Tholan API Server...")
    print("📡 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
