"""Fix all .html links in templates to use clean URLs for Render deployment"""
import os

templates_dir = r'frontend/templates'

replacements = [
    ('href="dashboard.html"',           'href="/dashboard"'),
    ('href="disease-detection.html"',   'href="/disease-detection"'),
    ('href="crop-recommendation.html"', 'href="/crop-recommendation"'),
    ('href="voice-assistant.html"',     'href="/voice-assistant"'),
    ('href="analytics.html"',           'href="/analytics"'),
    ('href="login.html"',               'href="/login"'),
    ("href='dashboard.html'",           "href='/dashboard'"),
    ("href='disease-detection.html'",   "href='/disease-detection'"),
    ("href='crop-recommendation.html'", "href='/crop-recommendation'"),
    ("href='voice-assistant.html'",     "href='/voice-assistant'"),
    ("href='analytics.html'",           "href='/analytics'"),
    ("href='login.html'",               "href='/login'"),
    # JS location redirects
    ("location.href='disease-detection.html'", "location.href='/disease-detection'"),
    ("location.href='analytics.html'",         "location.href='/analytics'"),
    ("location.href='dashboard.html'",         "location.href='/dashboard'"),
    ('location.href="disease-detection.html"', 'location.href="/disease-detection"'),
    ('location.href="analytics.html"',         'location.href="/analytics"'),
    ('location.href="dashboard.html"',         'location.href="/dashboard"'),
    # onclick redirects
    ("href='disease-detection.html'",   "href='/disease-detection'"),
]

for fname in os.listdir(templates_dir):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(templates_dir, fname)
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
