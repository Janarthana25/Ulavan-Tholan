# 🚀 Ulavan Tholan - Quick Start Guide

Get up and running in 5 minutes!

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 4GB+ RAM
- Modern web browser (Chrome, Firefox, Edge, Safari)

## ⚡ Quick Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- TensorFlow (AI/ML)
- Uvicorn (server)
- And other dependencies

### 2. Run the Application

```bash
python run.py
```

That's it! The application will start automatically.

## 🌐 Access the Application

Once started, open your browser and navigate to:

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📱 Using the Application

### Landing Page
- View features, statistics, and testimonials
- Click "Get Started" or "Dashboard" to begin

### Dashboard
1. View real-time weather data
2. See AI-powered recommendations
3. Check crop health statistics
4. Access quick actions

### Disease Detection
1. Click "Disease Detection" in navigation
2. Upload a crop image or use camera
3. Click "Analyze with AI"
4. View detailed diagnosis and treatment

### Crop Recommendation
1. Navigate to "Crop Advisory"
2. Enter your farm conditions:
   - Soil type
   - Temperature
   - Humidity
   - Rainfall
   - Season
3. Get AI-powered crop suggestions

## 🎨 Try Sample Data

### Disease Detection
- Click "Try these samples" buttons on the detection page
- Choose: Tomato, Potato, or Pepper disease samples
- View instant AI diagnosis results

### Crop Recommendation
- Click "Fill Sample Data" button
- Form auto-fills with realistic values
- Submit to see crop recommendations

## 🤖 About the ML Model

The application uses a **pre-trained** disease detection system that works without downloading the full PlantVillage dataset.

### To Train Your Own Model:

1. Download PlantVillage dataset:
   - Visit: https://www.kaggle.com/datasets/mohitsingh1804/plantvillage
   - Download and extract to `backend/ml/plantvillage/`

2. Run training script:
```bash
cd backend/ml
python train_model.py
```

Training takes:
- **CPU**: 2-4 hours
- **GPU**: 30-60 minutes

## 🎯 Features to Try

### ✅ Working Out of the Box
- ✅ Landing page with animations
- ✅ Dashboard with weather widget
- ✅ Disease detection (demo mode)
- ✅ Crop recommendations
- ✅ Water advisory
- ✅ Fertilizer suggestions
- ✅ Analytics dashboard
- ✅ Dark/Light theme toggle
- ✅ Fully responsive design

### 🔧 Requires Training
- ML Model training
- Custom dataset integration
- Production deployment

## 📚 API Endpoints

### Test the API directly:

```bash
# Health check
curl http://localhost:8000/api/health

# Weather data
curl http://localhost:8000/api/weather/current?location=India

# Crop recommendation
curl -X POST http://localhost:8000/api/crop/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "soil_type": "loamy",
    "temperature": 28,
    "humidity": 65,
    "rainfall": 1200,
    "season": "kharif",
    "ph_level": 6.5
  }'
```

## 🛠️ Troubleshooting

### Port Already in Use
If port 8000 is already taken:
```python
# Edit run.py and change port:
uvicorn.run("backend.main:app", port=8080)
```

### Module Not Found
Make sure you're in the project root:
```bash
pip install -r requirements.txt
```

### TensorFlow Issues
If TensorFlow installation fails:
```bash
# Try CPU-only version
pip install tensorflow-cpu==2.15.0
```

## 🎨 Customization

### Change Theme Colors
Edit `frontend/static/css/main.css`:
```css
:root {
  --primary-green: #4CAF50;  /* Change this */
  --forest-green: #2E7D32;   /* And this */
}
```

### Add Your Logo
Replace the emoji in navigation:
```html
<!-- frontend/templates/index.html -->
<span class="nav-logo-icon">🌱</span>
<!-- Change to: -->
<img src="/static/images/logo.png" alt="Logo">
```

## 📱 Mobile Testing

The app is fully responsive! Test on:
- iPhone (Safari)
- Android (Chrome)
- iPad/Tablets
- Desktop browsers

## 🌟 Next Steps

1. **Explore the Dashboard**
   - Check weather widget
   - View AI recommendations
   - Try quick actions

2. **Test Disease Detection**
   - Upload crop images
   - Try sample images
   - View treatment recommendations

3. **Get Crop Advice**
   - Enter farm conditions
   - View recommendations
   - Read best practices

4. **Customize**
   - Change colors
   - Add your branding
   - Extend functionality

## 💡 Tips

- Use the theme toggle (bottom right) for dark mode
- All animations are CSS-based (no JavaScript libraries)
- The design uses modern claymorphism style
- Mobile navigation works with hamburger menu
- Sample data available for quick testing

## 🐛 Found a Bug?

Create an issue on GitHub with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)

## 🎓 Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- TensorFlow: https://www.tensorflow.org/
- Plant Disease Dataset: https://www.kaggle.com/datasets/mohitsingh1804/plantvillage

## 📞 Need Help?

- Check the main [README.md](README.md)
- Review API docs at `/docs`
- Check browser console for errors
- Verify Python version: `python --version`

---

<div align="center">

**🌱 Happy Farming with AI!**

**Made with 💚 for Indian Farmers**

</div>
