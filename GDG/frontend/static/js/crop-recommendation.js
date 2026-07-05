/**
 * Crop Recommendation JavaScript - Ulavan Tholan
 * Fixed: loading overlay, relaxed conditions, proper API fallback
 */

// ==================== Init ====================
document.addEventListener('DOMContentLoaded', () => {

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.doLogout();
        });
    }

    // Apply translations
    if (window.LangManager) window.LangManager.applyAll();

    // Add sample data button inside the form
    const cropForm = document.getElementById('cropForm');
    if (cropForm) {
        const sampleBtn = document.createElement('button');
        sampleBtn.type = 'button';
        sampleBtn.textContent = '📝 Fill Sample Data';
        sampleBtn.className = 'clay-button';
        sampleBtn.style.cssText = 'margin-bottom:1.2rem;width:100%;';
        sampleBtn.addEventListener('click', fillSampleData);
        cropForm.insertBefore(sampleBtn, cropForm.firstChild);

        cropForm.addEventListener('submit', handleSubmit);
    }
});

// ==================== Loading helpers ====================
function showLoading() {
    const el = document.getElementById('loadingOverlay');
    if (el) el.style.display = 'flex';
}

function hideLoading() {
    const el = document.getElementById('loadingOverlay');
    if (el) el.style.display = 'none';
}

// ==================== Form Submit ====================
async function handleSubmit(e) {
    e.preventDefault();

    const soilType    = document.getElementById('soilType').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const humidity    = parseFloat(document.getElementById('humidity').value);
    const rainfall    = parseFloat(document.getElementById('rainfall').value);
    const season      = document.getElementById('season').value;
    const phLevel     = parseFloat(document.getElementById('phLevel').value) || 6.5;

    // Validate
    if (!soilType || !season) {
        alert('Please select Soil Type and Season.');
        return;
    }
    if (isNaN(temperature) || isNaN(humidity) || isNaN(rainfall)) {
        alert('Please enter valid numbers for Temperature, Humidity, and Rainfall.');
        return;
    }

    showLoading();

    try {
        let recommendations = null;

        // Try API first
        try {
            const resp = await fetch('/api/crop/recommend', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    soil_type: soilType,
                    temperature, humidity, rainfall, season,
                    ph_level: phLevel
                }),
                signal: AbortSignal.timeout(5000)
            });
            if (resp.ok) {
                const json = await resp.json();
                if (json && json.success && json.recommendations && json.recommendations.length > 0) {
                    recommendations = json.recommendations;
                }
            }
        } catch (_) {
            // API not reachable — use local engine
        }

        // Local fallback — always produces results
        if (!recommendations || recommendations.length === 0) {
            recommendations = localRecommend(soilType, temperature, humidity, rainfall, season, phLevel);
        }

        hideLoading();
        displayResults(recommendations);
        saveToStorage(recommendations[0].name, soilType, temperature, humidity, rainfall, season);

    } catch (err) {
        hideLoading();
        console.error('Crop recommendation error:', err);
        alert('Something went wrong. Please try again.');
    }
}

// ==================== Local Recommendation Engine ====================
// Relaxed conditions — always returns at least 3 crops for any Indian farm inputs
function localRecommend(soil, temp, humidity, rainfall, season, ph) {
    const all = [
        {
            name: 'Rice',
            score: scoreRice(temp, humidity, rainfall),
            confidence: 0.92,
            expected_yield: '4–5 tons/hectare',
            duration: '120–150 days',
            advantages: ['High market demand', 'Suitable for wet soil', 'Multiple varieties available'],
            requirements: ['Good water supply', 'Level field', 'Rich organic soil'],
            best_practices: ['Transplant at 25–30 days', 'Maintain 5–7 cm water', 'Apply nitrogen in splits']
        },
        {
            name: 'Wheat',
            score: scoreWheat(temp, humidity, rainfall, season),
            confidence: 0.88,
            expected_yield: '3–4 tons/hectare',
            duration: '120–130 days',
            advantages: ['Cold tolerant', 'Good market price', 'Wide adaptability'],
            requirements: ['Cool weather', 'Well-drained soil', '2–3 irrigations'],
            best_practices: ['Timely sowing', 'Seed treatment', 'Proper weed management']
        },
        {
            name: 'Tomato',
            score: scoreTomato(temp, ph),
            confidence: 0.85,
            expected_yield: '40–60 tons/hectare',
            duration: '90–120 days',
            advantages: ['High value crop', 'Multiple harvests possible', 'Strong processing demand'],
            requirements: ['Well-drained soil', 'Regular irrigation', 'Staking support'],
            best_practices: ['Use transplanting method', 'Drip irrigation preferred', 'Regular pest monitoring']
        },
        {
            name: 'Maize',
            score: scoreMaize(temp, rainfall),
            confidence: 0.82,
            expected_yield: '5–8 tons/hectare',
            duration: '100–120 days',
            advantages: ['Versatile uses', 'Moderate water needs', 'Fast growing'],
            requirements: ['Fertile soil', 'Good drainage', 'Adequate plant spacing'],
            best_practices: ['Timely weeding', 'Split nitrogen application', 'Pest monitoring']
        },
        {
            name: 'Cotton',
            score: scoreCotton(temp, rainfall, season),
            confidence: 0.79,
            expected_yield: '2–3 tons/hectare',
            duration: '150–180 days',
            advantages: ['Important cash crop', 'High industrial demand', 'Multiple by-products'],
            requirements: ['Warm weather', 'Black/red soil preferred', 'Pest management'],
            best_practices: ['Use Bt varieties', 'Integrated pest management', 'Proper row spacing']
        },
        {
            name: 'Groundnut',
            score: scoreGroundnut(temp, rainfall, soil, season),
            confidence: 0.80,
            expected_yield: '1.5–3 tons/hectare',
            duration: '90–120 days',
            advantages: ['Fixes nitrogen in soil', 'Drought tolerant', 'High oil content'],
            requirements: ['Sandy/loamy soil', 'Moderate rainfall', 'Well-drained field'],
            best_practices: ['Seed treatment with Rhizobium', 'Earthing up at 30 days', 'Harvesting at leaf yellowing']
        },
        {
            name: 'Sunflower',
            score: scoreSunflower(temp, rainfall),
            confidence: 0.77,
            expected_yield: '1.5–2.5 tons/hectare',
            duration: '85–100 days',
            advantages: ['Drought tolerant', 'Short duration', 'Good oil quality'],
            requirements: ['Well-drained soil', 'Moderate temperature', 'Adequate spacing'],
            best_practices: ['Sow in rows', 'Hand pollination helps yield', 'Bird protection at maturity']
        },
        {
            name: 'Millets (Bajra/Jowar)',
            score: 0.6, // Always available as safe fallback
            confidence: 0.75,
            expected_yield: '1.5–2.5 tons/hectare',
            duration: '75–90 days',
            advantages: ['Very drought resistant', 'Highly nutritious', 'Climate resilient'],
            requirements: ['Low water requirement', 'Sandy/loam soil', 'Minimal inputs'],
            best_practices: ['Dry-land farming suitable', 'Intercropping works well', 'Organic farming compatible']
        }
    ];

    // Sort by score descending, return top 5
    return all
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(c => {
            // Adjust confidence based on score
            c.confidence = Math.min(0.95, Math.max(0.60, c.score));
            return c;
        });
}

// Scoring functions — each returns 0.0–1.0
function scoreRice(temp, humidity, rainfall) {
    let s = 0.5;
    if (temp >= 25 && temp <= 35) s += 0.2;
    else if (temp >= 20 && temp <= 38) s += 0.1;
    if (humidity >= 70) s += 0.15;
    else if (humidity >= 55) s += 0.08;
    if (rainfall >= 1000) s += 0.15;
    else if (rainfall >= 600) s += 0.08;
    return Math.min(s, 0.95);
}

function scoreWheat(temp, humidity, rainfall, season) {
    let s = 0.4;
    if (temp >= 15 && temp <= 25) s += 0.25;
    else if (temp >= 10 && temp <= 30) s += 0.12;
    if (['rabi', 'winter'].includes(season.toLowerCase())) s += 0.2;
    if (rainfall >= 300 && rainfall <= 1000) s += 0.1;
    return Math.min(s, 0.92);
}

function scoreTomato(temp, ph) {
    let s = 0.5;
    if (temp >= 20 && temp <= 30) s += 0.25;
    else if (temp >= 15 && temp <= 35) s += 0.12;
    if (ph >= 6.0 && ph <= 7.0) s += 0.2;
    else if (ph >= 5.5 && ph <= 7.5) s += 0.1;
    return Math.min(s, 0.90);
}

function scoreMaize(temp, rainfall) {
    let s = 0.5;
    if (temp >= 21 && temp <= 30) s += 0.2;
    else if (temp >= 18 && temp <= 35) s += 0.1;
    if (rainfall >= 500 && rainfall <= 1200) s += 0.2;
    else if (rainfall >= 300) s += 0.1;
    return Math.min(s, 0.88);
}

function scoreCotton(temp, rainfall, season) {
    let s = 0.35;
    if (temp >= 25 && temp <= 35) s += 0.25;
    else if (temp >= 20 && temp <= 40) s += 0.1;
    if (['kharif', 'summer'].includes(season.toLowerCase())) s += 0.2;
    if (rainfall >= 500 && rainfall <= 1500) s += 0.15;
    return Math.min(s, 0.85);
}

function scoreGroundnut(temp, rainfall, soil, season) {
    let s = 0.4;
    if (temp >= 25 && temp <= 30) s += 0.2;
    else if (temp >= 20 && temp <= 35) s += 0.1;
    if (['sandy', 'loamy', 'red'].includes(soil.toLowerCase())) s += 0.15;
    if (['kharif', 'rabi'].includes(season.toLowerCase())) s += 0.1;
    if (rainfall >= 400 && rainfall <= 1200) s += 0.15;
    return Math.min(s, 0.88);
}

function scoreSunflower(temp, rainfall) {
    let s = 0.4;
    if (temp >= 20 && temp <= 30) s += 0.2;
    if (rainfall >= 400 && rainfall <= 1000) s += 0.15;
    return Math.min(s, 0.82);
}

// ==================== Display Results ====================
function displayResults(crops) {
    const container   = document.getElementById('resultsContainer');
    const cropResults = document.getElementById('cropResults');

    if (!container || !cropResults) {
        console.error('Results container not found');
        return;
    }

    // Clear and show container FIRST
    cropResults.innerHTML = '';
    container.style.display = 'block';
    container.style.opacity = '1';
    container.style.visibility = 'visible';

    crops.forEach((crop, index) => {
        const card = document.createElement('div');
        card.className = 'clay-card';
        // No animation — just show immediately with no opacity tricks
        card.style.cssText = 'margin-bottom:1.5rem; opacity:1; visibility:visible;';

        const pct        = Math.round(crop.confidence * 100);
        const confColor  = pct >= 80 ? '#2E7D32' : pct >= 65 ? '#F57F17' : '#757575';

        card.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem;flex-wrap:wrap;gap:0.5rem;">
                <h3 style="color:var(--forest-green);font-size:1.4rem;margin:0;font-weight:700;">🌾 ${crop.name}</h3>
                <span style="background:${confColor};color:#fff;padding:0.4rem 1rem;
                             border-radius:20px;font-weight:700;font-size:0.9rem;">
                    ${pct}% Match
                </span>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;
                        padding:1rem;background:var(--light-gray);border-radius:12px;">
                <div>
                    <div style="font-size:0.82rem;color:var(--medium-gray);margin-bottom:0.2rem;">Expected Yield</div>
                    <div style="font-weight:600;color:var(--forest-green);">📊 ${crop.expected_yield}</div>
                </div>
                <div>
                    <div style="font-size:0.82rem;color:var(--medium-gray);margin-bottom:0.2rem;">Duration</div>
                    <div style="font-weight:600;color:var(--forest-green);">⏱️ ${crop.duration}</div>
                </div>
            </div>

            <div style="margin-bottom:1rem;">
                <h4 style="color:var(--forest-green);margin-bottom:0.6rem;">✅ Advantages</h4>
                ${buildList(crop.advantages, '#2E7D32')}
            </div>

            <div style="margin-bottom:1rem;">
                <h4 style="color:var(--forest-green);margin-bottom:0.6rem;">📋 Requirements</h4>
                ${buildList(crop.requirements, '#0277BD')}
            </div>

            <div>
                <h4 style="color:var(--forest-green);margin-bottom:0.6rem;">💡 Best Practices</h4>
                ${buildList(crop.best_practices, '#E65100')}
            </div>`;

        cropResults.appendChild(card);
    });

    // Scroll to results
    setTimeout(() => {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function buildList(items, color) {
    if (!items || !items.length) return '<p style="color:var(--medium-gray);">—</p>';
    return `<ul style="list-style:none;padding:0;margin:0;">` +
        items.map(item => `
            <li style="padding:0.45rem 0.5rem 0.45rem 1.8rem;margin-bottom:0.35rem;
                       background:var(--light-gray);border-radius:8px;position:relative;font-size:0.92rem;">
                <span style="position:absolute;left:0.6rem;color:${color};font-weight:700;">•</span>
                ${item}
            </li>`).join('') +
        '</ul>';
}

// ==================== Save to localStorage ====================
function saveToStorage(topCrop, soilType, temperature, humidity, rainfall, season) {
    // Save crop recommendation record
    const cropRecs = JSON.parse(localStorage.getItem('cropRecs') || '[]');
    cropRecs.unshift({
        timestamp: new Date().toISOString(),
        topCrop, soilType, temperature, humidity, rainfall, season
    });
    if (cropRecs.length > 30) cropRecs.pop();
    localStorage.setItem('cropRecs', JSON.stringify(cropRecs));

    // Save to activity log
    const activities = JSON.parse(localStorage.getItem('activities') || '[]');
    activities.unshift({
        icon:        '🌾',
        title:       'Crop Recommendation',
        description: `${topCrop} recommended for ${soilType} soil`,
        time:        new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    if (activities.length > 15) activities.pop();
    localStorage.setItem('activities', JSON.stringify(activities));
}

// ==================== Sample Data ====================
function fillSampleData() {
    document.getElementById('soilType').value    = 'loamy';
    document.getElementById('temperature').value = '28';
    document.getElementById('humidity').value    = '65';
    document.getElementById('rainfall').value    = '800';
    document.getElementById('phLevel').value     = '6.5';
    document.getElementById('season').value      = 'kharif';
}

// Inject fadeInUp animation
const s = document.createElement('style');
s.textContent = `
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(24px); }
    to   { opacity:1; transform:translateY(0); }
}`;
document.head.appendChild(s);

console.log('🌾 Crop Recommendation loaded');
