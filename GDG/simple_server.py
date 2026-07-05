"""
Simple HTTP Server - Ulavan Tholan
Fixed: CORS preflight (OPTIONS), missing API endpoints, proper routing
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs, unquote
import random

PORT = 8000

class UlavanTholanHandler(http.server.SimpleHTTPRequestHandler):

    # ------------------------------------------------------------------ GET --
    def do_GET(self):
        parsed = urlparse(unquote(self.path))
        path   = parsed.path

        # ---- Page routes ----
        route_map = {
            '/':                          'frontend/templates/index.html',
            '/login':                     'frontend/templates/login.html',
            '/login.html':                'frontend/templates/login.html',
            '/dashboard':                 'frontend/templates/dashboard.html',
            '/dashboard.html':            'frontend/templates/dashboard.html',
            '/disease-detection':         'frontend/templates/disease-detection.html',
            '/disease-detection.html':    'frontend/templates/disease-detection.html',
            '/crop-recommendation':       'frontend/templates/crop-recommendation.html',
            '/crop-recommendation.html':  'frontend/templates/crop-recommendation.html',
            '/voice-assistant':           'frontend/templates/voice-assistant.html',
            '/voice-assistant.html':      'frontend/templates/voice-assistant.html',
            '/analytics':                 'frontend/templates/analytics.html',
            '/analytics.html':            'frontend/templates/analytics.html',
            '/index.html':                'frontend/templates/index.html',
        }

        if path in route_map:
            self.path = '/' + route_map[path]
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # ---- Static files (CSS / JS / images) ----
        if path.startswith('/static/'):
            self.path = '/frontend' + path
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # ---- API routes ----
        if path.startswith('/api/'):
            self._handle_api_get(parsed)
            return

        # Fallback
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # ----------------------------------------------------------------- POST --
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/'):
            self._handle_api_post(parsed)
            return
        self.send_error(405, 'Method Not Allowed')

    # --------------------------------------------------------------- OPTIONS -
    # Required for browser CORS pre-flight on POST with JSON / multipart
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.send_header('Content-Length', '0')
        self.end_headers()

    # --------------------------------------------------------- API: GET ------
    def _handle_api_get(self, parsed):
        path = parsed.path

        # Health check
        if path == '/api/health':
            return self._json({
                'status':  'healthy',
                'service': 'Ulavan Tholan API',
                'version': '1.0.0'
            })

        # Weather
        if path == '/api/weather/current':
            return self._json({
                'success':  True,
                'location': 'India',
                'current':  {
                    'temperature': round(28 + random.uniform(-5, 5), 1),
                    'humidity':    round(65 + random.uniform(-15, 15), 0),
                    'rainfall':    round(random.uniform(0, 50), 1),
                    'wind_speed':  round(random.uniform(5, 25), 1),
                    'condition':   random.choice(['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy'])
                }
            })

        # Analytics dashboard
        if path == '/api/analytics/dashboard':
            return self._json({
                'success': True,
                'statistics': {
                    'total_diagnoses': 1247,
                    'healthy_plants':  892,
                    'diseased_plants': 355,
                    'accuracy_rate':   94.5,
                    'farmers_helped':  523
                },
                'disease_distribution': [
                    {'disease': 'Early Blight',    'percentage': 25.1},
                    {'disease': 'Late Blight',     'percentage': 18.9},
                    {'disease': 'Bacterial Spot',  'percentage': 15.2},
                    {'disease': 'Leaf Mold',       'percentage': 12.1},
                    {'disease': 'Others',          'percentage': 28.7}
                ]
            })

        # Disease history
        if path == '/api/disease/history':
            return self._json({
                'success': True,
                'history': [
                    {'id': 1, 'date': '2026-07-05', 'plant': 'Tomato',  'disease': 'Early Blight',   'confidence': 0.92, 'severity': 'High'},
                    {'id': 2, 'date': '2026-07-04', 'plant': 'Potato',  'disease': 'Healthy',        'confidence': 0.95, 'severity': 'None'},
                    {'id': 3, 'date': '2026-07-03', 'plant': 'Pepper',  'disease': 'Bacterial Spot', 'confidence': 0.88, 'severity': 'Moderate'}
                ]
            })

        self.send_error(404, 'API endpoint not found')

    # ------------------------------------------------------- API: POST -------
    def _handle_api_post(self, parsed):
        path           = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes     = self.rfile.read(content_length) if content_length > 0 else b''

        # Parse JSON body if sent as application/json
        body = {}
        ct   = self.headers.get('Content-Type', '')
        if 'application/json' in ct and body_bytes:
            try:
                body = json.loads(body_bytes)
            except Exception:
                pass

        # ---- Crop recommendation ----
        if path == '/api/crop/recommend':
            temp     = float(body.get('temperature', 28))
            rainfall = float(body.get('rainfall',    800))
            humidity = float(body.get('humidity',    65))
            season   = str(body.get('season',        '')).lower()
            ph       = float(body.get('ph_level',    6.5))

            recs = []

            if 25 <= temp <= 35 and rainfall > 1000 and humidity > 70:
                recs.append({
                    'name': 'Rice', 'confidence': 0.92,
                    'expected_yield': '4–5 tons/hectare', 'duration': '120–150 days',
                    'advantages':     ['High demand', 'Suitable for wet soil'],
                    'requirements':   ['Consistent water supply', 'Level field'],
                    'best_practices': ['Transplant at 25–30 days', 'Maintain 5–7 cm water']
                })

            if 15 <= temp <= 25 and 400 <= rainfall <= 800 and season in ['rabi', 'winter']:
                recs.append({
                    'name': 'Wheat', 'confidence': 0.88,
                    'expected_yield': '3–4 tons/hectare', 'duration': '120–130 days',
                    'advantages':     ['Cold tolerant', 'Good market price'],
                    'requirements':   ['Cool weather', 'Well-drained soil'],
                    'best_practices': ['Timely sowing', 'Seed treatment']
                })

            if 20 <= temp <= 32 and ph >= 5.5:
                recs.append({
                    'name': 'Tomato', 'confidence': 0.85,
                    'expected_yield': '40–60 tons/hectare', 'duration': '90–120 days',
                    'advantages':     ['High value', 'Multiple harvests'],
                    'requirements':   ['Well-drained soil', 'Drip irrigation'],
                    'best_practices': ['Transplanting method', 'Regular pest check']
                })

            if 21 <= temp <= 30 and rainfall > 500:
                recs.append({
                    'name': 'Maize', 'confidence': 0.82,
                    'expected_yield': '5–8 tons/hectare', 'duration': '100–120 days',
                    'advantages':     ['Versatile crop', 'Moderate water'],
                    'requirements':   ['Fertile soil', 'Good drainage'],
                    'best_practices': ['Timely weeding', 'Split N application']
                })

            if not recs:
                recs.append({
                    'name': 'Millets', 'confidence': 0.75,
                    'expected_yield': '1.5–2.5 tons/hectare', 'duration': '75–90 days',
                    'advantages':     ['Drought resistant', 'Nutritious'],
                    'requirements':   ['Low water', 'Sandy loam soil'],
                    'best_practices': ['Dry-land farming', 'Organic inputs']
                })

            recs.sort(key=lambda x: x['confidence'], reverse=True)
            return self._json({'success': True, 'recommendations': recs[:5]})

        # ---- Disease detection ----
        if path == '/api/disease/detect':
            # multipart upload — just return a realistic mock result
            # (In production this would call the ML model)
            diseases = [
                {
                    'success': True,
                    'primary_disease':          'Tomato Early Blight',
                    'plant':                    'Tomato',
                    'confidence':               0.92,
                    'confidence_percent':       '92%',
                    'severity':                 'High',
                    'is_healthy':               False,
                    'symptoms':                 ['Dark brown spots with rings', 'Lower leaves first', 'Yellowing around lesions'],
                    'treatment':                ['Apply Mancozeb or Chlorothalonil', 'Remove infected leaves', 'Spray every 7–10 days'],
                    'prevention':               ['Mulch around plants', 'Avoid overhead watering', 'Proper spacing'],
                    'fertilizer_recommendation':'High potassium fertilizer (5-10-10)',
                    'irrigation_advice':        'Morning watering at soil level',
                    'top_predictions': [
                        {'disease': 'Tomato Early Blight', 'confidence_percent': '92%'},
                        {'disease': 'Tomato Late Blight',  'confidence_percent': '6%'},
                        {'disease': 'Tomato Leaf Mold',    'confidence_percent': '2%'}
                    ]
                },
                {
                    'success': True,
                    'primary_disease':          'Healthy Plant',
                    'plant':                    'Tomato',
                    'confidence':               0.96,
                    'confidence_percent':       '96%',
                    'severity':                 'Low',
                    'is_healthy':               True,
                    'symptoms':                 ['No disease symptoms detected', 'Normal green foliage'],
                    'treatment':                ['Continue regular care', 'Monitor weekly'],
                    'prevention':               ['Regular monitoring', 'Proper watering', 'Balanced fertilization'],
                    'fertilizer_recommendation':'NPK 10-10-10 every 2 weeks',
                    'irrigation_advice':        '1–2 inches per week',
                    'top_predictions': [
                        {'disease': 'Healthy Plant',       'confidence_percent': '96%'},
                        {'disease': 'Early Blight (low)',  'confidence_percent': '3%'}
                    ]
                }
            ]
            return self._json(random.choice(diseases))

        # ---- Water advisory ----
        if path == '/api/water/advisory':
            moisture = float(body.get('soil_moisture', 50))
            crop     = str(body.get('crop_type', 'tomato')).lower()
            daily    = {'rice': 15, 'sugarcane': 12, 'wheat': 8, 'potato': 6}.get(crop, 6)
            needed   = moisture < 50
            urgency  = 'High' if moisture < 30 else ('Moderate' if moisture < 50 else 'Low')
            return self._json({
                'success': True,
                'advisory': {
                    'irrigation_needed':   needed,
                    'urgency':             urgency,
                    'message':             '⚠️ Irrigate soon' if needed else '✅ Moisture adequate',
                    'daily_requirement':   f'{daily} litres/plant',
                    'timing':              'Early morning 6–8 AM',
                    'water_saving_tip':    'Drip irrigation saves 30–50% water'
                }
            })

        # ---- Fertilizer recommendation ----
        if path == '/api/fertilizer/recommend':
            crop  = str(body.get('crop_type', 'tomato')).lower()
            soil  = str(body.get('soil_type', 'loamy')).lower()
            npk   = {'rice': (120,60,40), 'wheat': (150,60,40), 'tomato': (100,50,50),
                     'potato': (150,80,100), 'maize': (120,60,50)}.get(crop, (100,50,50))
            return self._json({
                'success': True,
                'recommendations': {
                    'primary_fertilizer':   f'NPK {npk[0]}-{npk[1]}-{npk[2]}',
                    'n_kg_ha':  npk[0],
                    'p_kg_ha':  npk[1],
                    'k_kg_ha':  npk[2],
                    'organic_alternative': '5–10 tons/ha compost or vermicompost',
                    'application_tips': [
                        'Apply when soil has adequate moisture',
                        'Split doses for better absorption',
                        'Avoid before heavy rain'
                    ]
                }
            })

        self.send_error(404, 'API endpoint not found')

    # --------------------------------------------------------- JSON helper ---
    def _json(self, data):
        payload = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type',   'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    # Override end_headers to inject CORS on every response
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    # Suppress console noise for 304 / normal requests
    def log_message(self, fmt, *args):
        pass  # Comment this line out if you want request logs


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PORT), UlavanTholanHandler) as httpd:
        print('=' * 60)
        print('🌱  Ulavan Tholan — Server Starting')
        print('=' * 60)
        print(f'✅  http://localhost:{PORT}')
        print(f'📄  /dashboard  /disease-detection  /crop-recommendation')
        print(f'📡  /api/health  /api/crop/recommend  /api/disease/detect')
        print(f'🛑  Press CTRL+C to stop')
        print('=' * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n🛑 Server stopped')


if __name__ == '__main__':
    run_server()
