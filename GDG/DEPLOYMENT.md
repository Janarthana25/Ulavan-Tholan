# 🚀 Ulavan Tholan - Deployment Guide

Complete guide for deploying Ulavan Tholan to production environments.

---

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [SSL/HTTPS Setup](#ssl-https-setup)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring & Logging](#monitoring--logging)

---

## 🖥️ Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
```

### Development Mode
```bash
# Backend with auto-reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access application
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/backend/uploads
      - ./backend/ml/models:/app/backend/ml/models
    environment:
      - ENVIRONMENT=production
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped

  # Optional: Add PostgreSQL
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ulavan_tholan
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Optional: Add Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Run

```bash
# Build image
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Using Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB**
```bash
eb init -p python-3.9 ulavan-tholan --region us-east-1
```

3. **Create Environment**
```bash
eb create ulavan-tholan-prod
```

4. **Deploy**
```bash
eb deploy
```

5. **Open Application**
```bash
eb open
```

#### Using EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Type: t2.medium or larger
   - Storage: 20GB+
   - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Connect to Instance**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Setup Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.9 python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Clone repository
git clone https://github.com/yourusername/ulavan-tholan.git
cd ulavan-tholan

# Install dependencies
pip3 install -r requirements.txt

# Install Gunicorn
pip3 install gunicorn
```

4. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/ulavan-tholan.service
```

```ini
[Unit]
Description=Ulavan Tholan FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/ulavan-tholan
Environment="PATH=/home/ubuntu/ulavan-tholan/venv/bin"
ExecStart=/home/ubuntu/ulavan-tholan/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

5. **Start Service**
```bash
sudo systemctl start ulavan-tholan
sudo systemctl enable ulavan-tholan
sudo systemctl status ulavan-tholan
```

6. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/ulavan-tholan
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ulavan-tholan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build Container**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ulavan-tholan
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy ulavan-tholan \
  --image gcr.io/YOUR_PROJECT/ulavan-tholan \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Microsoft Azure

#### Using App Service

1. **Create App Service**
```bash
az webapp up --name ulavan-tholan --runtime "PYTHON:3.9"
```

2. **Configure Settings**
```bash
az webapp config appsettings set --resource-group myResourceGroup --name ulavan-tholan --settings WEBSITE_RUN_FROM_PACKAGE="1"
```

### Heroku

1. **Create Procfile**
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

2. **Create runtime.txt**
```
python-3.9.18
```

3. **Deploy**
```bash
# Login
heroku login

# Create app
heroku create ulavan-tholan

# Deploy
git push heroku main

# Open app
heroku open
```

---

## ⚙️ Environment Configuration

### Create .env file

```bash
# Application
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ulavan_tholan
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://localhost:6379/0

# ML Model
MODEL_PATH=backend/ml/models/plant_disease_model.h5
CLASSES_PATH=backend/ml/models/class_names.json

# File Upload
UPLOAD_DIR=backend/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# External APIs (if using)
WEATHER_API_KEY=your-weather-api-key
WEATHER_API_URL=https://api.weatherapi.com/v1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Load Environment Variables

```python
# backend/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = ""
    secret_key: str = "dev-secret-key"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🗄️ Database Setup

### PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE ulavan_tholan;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create diagnoses table
CREATE TABLE diagnoses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    image_path VARCHAR(500) NOT NULL,
    disease_name VARCHAR(255) NOT NULL,
    plant_type VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    severity VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create crops table
CREATE TABLE crop_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    soil_type VARCHAR(100),
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT,
    recommended_crops JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_diagnoses_user_id ON diagnoses(user_id);
CREATE INDEX idx_diagnoses_created_at ON diagnoses(created_at);
CREATE INDEX idx_recommendations_user_id ON crop_recommendations(user_id);
```

### Database Migration (using Alembic)

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration
alembic upgrade head
```

---

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### Update Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... rest of proxy settings
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## ⚡ Performance Optimization

### Gunicorn Configuration

```python
# gunicorn_config.py
workers = 4  # 2-4 x CPU cores
worker_class = 'uvicorn.workers.UvicornWorker'
bind = '0.0.0.0:8000'
keepalive = 120
timeout = 120
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'
```

### Redis Caching

```python
# backend/cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### Static File CDN

```python
# Use CDN for static files
STATIC_URL = "https://cdn.yourdomain.com/static/"
```

---

## 📊 Monitoring & Logging

### Logging Setup

```python
# backend/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=10
            ),
            logging.StreamHandler()
        ]
    )
```

### Application Monitoring

```python
# backend/middleware.py
from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Duration: {duration:.2f}s"
    )
    
    return response
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ml_model_loaded": predictor.model is not None,
        "database_connected": True  # Check actual DB connection
    }
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill process
sudo kill -9 <PID>
```

2. **Permission denied for uploads**
```bash
sudo chown -R www-data:www-data backend/uploads
sudo chmod -R 755 backend/uploads
```

3. **TensorFlow not loading**
```bash
# Install CPU version if no GPU
pip uninstall tensorflow
pip install tensorflow-cpu
```

4. **Nginx 502 Bad Gateway**
```bash
# Check if app is running
systemctl status ulavan-tholan
# Check logs
sudo tail -f /var/log/nginx/error.log
```

---

## ✅ Pre-Deployment Checklist

- [ ] Update SECRET_KEY in environment variables
- [ ] Set DEBUG=false in production
- [ ] Configure ALLOWED_ORIGINS
- [ ] Setup SSL certificate
- [ ] Configure database backups
- [ ] Setup monitoring and logging
- [ ] Test all API endpoints
- [ ] Verify file upload limits
- [ ] Enable firewall
- [ ] Setup automated backups
- [ ] Configure CDN for static files
- [ ] Test responsive design
- [ ] Verify ML model loading
- [ ] Setup error tracking (Sentry)
- [ ] Configure rate limiting
- [ ] Test payment integration (if applicable)

---

<div align="center">

**🚀 Ready for Production!**

**Ulavan Tholan - Empowering Agriculture**

</div>
