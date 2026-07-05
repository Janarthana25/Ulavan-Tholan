"""Fix .html links in JS files"""
import os

js_dir = r'frontend/static/js'

replacements = [
    ("'/login.html'",               "'/login'"),
    ('"/login.html"',               '"/login"'),
    ("'/dashboard.html'",           "'/dashboard'"),
    ('"/dashboard.html"',           '"/dashboard"'),
    ("'/disease-detection.html'",   "'/disease-detection'"),
    ('"/disease-detection.html"',   '"/disease-detection"'),
    ("'/crop-recommendation.html'", "'/crop-recommendation'"),
    ('"/crop-recommendation.html"', '"/crop-recommendation"'),
    ("'/analytics.html'",           "'/analytics'"),
    ('"/analytics.html"',           '"/analytics"'),
    ("'/voice-assistant.html'",     "'/voice-assistant'"),
    ('"/voice-assistant.html"',     '"/voice-assistant"'),
    # dashboard.js onclick strings
    ("'disease-detection.html'",    "'/disease-detection'"),
    ("'analytics.html'",            "'/analytics'"),
]

for fname in os.listdir(js_dir):
    if not fname.endswith('.js'):
        continue
    fpath = os.path.join(js_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {fname}')
    else:
        print(f'No changes: {fname}')

print('Done!')
