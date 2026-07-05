/**
 * Dashboard JavaScript - Ulavan Tholan
 * Fixed: modal auto-open, stat persistence, crop advisory count, activity feed
 */

// ==================== Safe module reference ====================
// Use window.UlavanTholan safely — main.js loads before this but we guard anyway
function getUtil(name) {
    return window.UlavanTholan ? window.UlavanTholan[name] : null;
}

// ==================== Init ====================
document.addEventListener('DOMContentLoaded', async () => {

    // Ensure ALL modals are hidden immediately on load — belt-and-suspenders fix
    document.querySelectorAll('.modal-backdrop').forEach(m => {
        m.classList.remove('modal-open');
    });

    // Greet user
    const email = sessionStorage.getItem('userEmail') || 'Farmer';
    const name = email.split('@')[0];
    const welcomeEl = document.getElementById('welcomeTitle');
    if (welcomeEl) {
        const greet = (window.LangManager ? window.LangManager.t('dash_welcome') : null) || 'Welcome back';
        welcomeEl.textContent = `${greet}, ${name} 👋`;
    }

    // Setup logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.doLogout();
        });
    }

    // Load all dashboard data from localStorage
    loadUserStats();
    loadUserActivity();
    loadWeather();
    rotateAIRecommendations();
    setupModalButtons();

    // Apply translations
    if (window.LangManager) window.LangManager.applyAll();
});

// ==================== User Stats ====================
// Reads from localStorage keys written by disease-detection.js and crop-recommendation.js
function loadUserStats() {
    const diagnoses = JSON.parse(localStorage.getItem('diagnoses') || '[]');
    const cropRecs  = JSON.parse(localStorage.getItem('cropRecs')  || '[]');

    const totalDiag    = diagnoses.length;
    const healthyCount = diagnoses.filter(d => d.is_healthy).length;
    const healthyPct   = totalDiag > 0 ? Math.round((healthyCount / totalDiag) * 100) + '%' : '—';
    const lastScan     = totalDiag > 0
        ? new Date(diagnoses[0].timestamp).toLocaleDateString()
        : 'Never';

    setEl('statDiag',       totalDiag);
    setEl('statHealthy',    healthyPct);
    setEl('statCrops',      cropRecs.length);
    setEl('statLastScan',   lastScan);
    setEl('statDiagChange', totalDiag > 0 ? `${totalDiag} scans done` : 'Start detecting');
}

// ==================== User Activity ====================
function loadUserActivity() {
    const activities = JSON.parse(localStorage.getItem('activities') || '[]');
    const list = document.getElementById('activityList');
    if (!list) return;

    if (activities.length === 0) {
        list.innerHTML = `
            <li style="text-align:center;padding:3rem 1rem;background:var(--light-gray);
                       border-radius:var(--radius-md);list-style:none;">
                <div style="font-size:3rem;margin-bottom:1rem;opacity:0.4;">📋</div>
                <div style="color:var(--medium-gray);font-weight:600;">No activity yet</div>
                <div style="font-size:0.9rem;color:var(--medium-gray);margin-top:0.5rem;">
                    Start by detecting a disease or getting crop recommendations
                </div>
                <a href="disease-detection.html"
                   class="clay-button clay-button-primary"
                   style="margin-top:1.5rem;display:inline-block;text-decoration:none;">
                    🔍 Detect Now
                </a>
            </li>`;
    } else {
        list.innerHTML = activities.map(a => `
            <li class="activity-item">
                <div class="activity-title">${a.icon || '📌'} ${a.title}</div>
                <div class="activity-description">${a.description}</div>
                <div class="activity-time">${a.time}</div>
            </li>`).join('');
    }
}

// ==================== Weather ====================
async function loadWeather() {
    try {
        const apiReq = getUtil('apiRequest');
        const data   = apiReq ? await apiReq('/weather/current?location=India') : null;
        if (data && data.current) {
            setEl('weatherTemp',      data.current.temperature);
            setEl('weatherCondition', data.current.condition);
            setEl('weatherHumidity',  data.current.humidity);
            setEl('weatherRainfall',  data.current.rainfall);
            setEl('weatherWind',      data.current.wind_speed);
            return;
        }
    } catch (_) { /* fall through to mock */ }

    // Fallback mock values
    setEl('weatherTemp',      Math.round(28 + (Math.random() * 6 - 3)));
    setEl('weatherCondition', '⛅ Partly Cloudy');
    setEl('weatherHumidity',  Math.round(60 + Math.random() * 20));
    setEl('weatherRainfall',  Math.round(Math.random() * 30));
    setEl('weatherWind',      Math.round(10  + Math.random() * 15));

    // Refresh every 10 mins
    setTimeout(loadWeather, 600000);
}

// ==================== AI Recommendations ====================
function rotateAIRecommendations() {
    const messages = [
        {
            msg:  'Based on current weather patterns, we recommend reducing irrigation by 20% for the next 3 days. Expected rainfall: 15mm.',
            tags: ['💧 Water Management', '🌧️ Weather Alert', '⚡ High Priority']
        },
        {
            msg:  'Excellent time for planting winter crops. Soil temperature and moisture levels are optimal for wheat and mustard.',
            tags: ['🌱 Crop Planning', '📅 Seasonal Advisory', '✅ Recommended']
        },
        {
            msg:  'Disease risk is moderate this week. Consider applying neem oil spray on your crops as a preventive measure.',
            tags: ['🛡️ Disease Prevention', '🌿 Organic', '⚠️ Watch Out']
        },
        {
            msg:  'Nitrogen levels may be low. Consider applying urea at 50 kg/acre within the next week for better yield.',
            tags: ['🧪 Fertilizer', '📈 Yield Boost', '🔔 Action Needed']
        }
    ];

    let i = 0;
    function update() {
        const m      = messages[i % messages.length];
        const msgEl  = document.getElementById('aiMessage');
        const tagsEl = document.getElementById('aiTags');
        if (msgEl)  msgEl.textContent = m.msg;
        if (tagsEl) tagsEl.innerHTML  = m.tags.map(t => `<div class="ai-tag">${t}</div>`).join('');
        i++;
    }
    update();
    setInterval(update, 12000);
}

// ==================== Modals ====================
// openModal / closeModal use CSS class .modal-open on .modal-backdrop
// The CSS rule   .modal-backdrop { display:none!important }
// and            .modal-backdrop.modal-open { display:flex!important }
// ensure modals never auto-show regardless of any other stylesheet

function openModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.remove('modal-open');
        document.body.style.overflow = '';
    }
}

// Expose globally so inline onclick="closeModal(...)" in HTML works
window.closeModal = closeModal;
window.openModal  = openModal;

function setupModalButtons() {
    // Water Plan button
    const waterBtn = document.getElementById('waterBtn');
    if (waterBtn) {
        waterBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('waterModal');
        });
    }

    // Fertilizer button
    const fertBtn = document.getElementById('fertBtn');
    if (fertBtn) {
        fertBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('fertModal');
        });
    }

    // Close on backdrop click
    document.querySelectorAll('.modal-backdrop').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal(overlay.id);
        });
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-backdrop.modal-open').forEach(m => closeModal(m.id));
        }
    });
}

// ==================== Water Advisory ====================
window.getWaterAdvisory = async function () {
    const crop      = document.getElementById('waterCrop').value;
    const moisture  = parseFloat(document.getElementById('waterMoisture').value) || 45;
    const stage     = document.getElementById('waterStage').value;
    const resultDiv = document.getElementById('waterResult');
    if (!resultDiv) return;

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div style="text-align:center;padding:1rem;">⏳ Calculating...</div>';

    await sleep(800);

    const needsWater = moisture < 50;
    const urgency    = moisture < 30 ? 'High 🔴' : moisture < 50 ? 'Moderate 🟡' : 'Low 🟢';
    const dailyReqMap = { rice: 15, sugarcane: 12, cotton: 8, wheat: 7, potato: 6 };
    const dailyReq   = dailyReqMap[crop] || 6;

    resultDiv.innerHTML = `
        <div class="advisory-result">
            <h4>💧 Irrigation Advisory</h4>
            <p><b>Crop:</b> ${cap(crop)} &nbsp;|&nbsp; <b>Stage:</b> ${cap(stage)}</p>
            <p><b>Soil Moisture:</b> ${moisture}%</p>
            <p><b>Irrigation Needed:</b> ${needsWater ? '✅ Yes' : '❌ Not yet'}</p>
            <p><b>Urgency:</b> ${urgency}</p>
            <p><b>Daily Requirement:</b> ~${dailyReq} litres/plant</p>
            <p><b>Best Time:</b> Early morning 6–8 AM or evening 6–8 PM</p>
            <p><b>Tip:</b> Drip irrigation saves 30–50% water vs flood irrigation.</p>
        </div>`;

    persistActivity({ icon: '💧', title: 'Water Plan Checked',
        description: `${cap(crop)} — Moisture: ${moisture}%`, time: timeLabel() });
};

// ==================== Fertilizer Recommendation ====================
window.getFertRecommendation = async function () {
    const crop      = document.getElementById('fertCrop').value;
    const soil      = document.getElementById('fertSoil').value;
    const resultDiv = document.getElementById('fertResult');
    if (!resultDiv) return;

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<div style="text-align:center;padding:1rem;">⏳ Calculating...</div>';

    await sleep(800);

    const npkMap = {
        tomato: { N: 100, P: 50,  K: 50  },
        rice:   { N: 120, P: 60,  K: 40  },
        wheat:  { N: 150, P: 60,  K: 40  },
        potato: { N: 150, P: 80,  K: 100 },
        maize:  { N: 120, P: 60,  K: 50  }
    };
    const req = npkMap[crop] || { N: 100, P: 50, K: 50 };

    resultDiv.innerHTML = `
        <div class="advisory-result">
            <h4>🧪 Fertilizer Plan for ${cap(crop)}</h4>
            <p><b>Soil Type:</b> ${cap(soil)}</p>
            <p><b>Recommended NPK:</b>
                <span class="badge badge-green">N: ${req.N} kg/ha</span>
                <span class="badge badge-blue">P: ${req.P} kg/ha</span>
                <span class="badge badge-yellow">K: ${req.K} kg/ha</span>
            </p>
            <p><b>Application 1 (Basal):</b> ${Math.round(req.N/3)}-${req.P}-${Math.round(req.K/2)} kg/ha</p>
            <p><b>Application 2 (3–4 weeks):</b> ${Math.round(req.N/3)}-0-${Math.round(req.K/2)} kg/ha</p>
            <p><b>Application 3 (6–7 weeks):</b> ${Math.round(req.N/3)}-0-0 kg/ha</p>
            <p><b>Organic Alternative:</b> 5–10 tons/ha compost or vermicompost</p>
        </div>`;

    persistActivity({ icon: '🧪', title: 'Fertilizer Plan',
        description: `${cap(crop)} on ${cap(soil)} soil`, time: timeLabel() });
};

// ==================== Helpers ====================
function setEl(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function cap(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

function timeLabel() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Persist activity to localStorage + refresh activity list on dashboard
function persistActivity(activity) {
    const activities = JSON.parse(localStorage.getItem('activities') || '[]');
    activities.unshift(activity);
    if (activities.length > 15) activities.pop();
    localStorage.setItem('activities', JSON.stringify(activities));
    loadUserActivity(); // refresh the list immediately
    loadUserStats();    // refresh counts too
}

// Inject keyframe animations
const style = document.createElement('style');
style.textContent = `
@keyframes ripple        { to { transform: translate(-50%,-50%) scale(4); opacity:0; } }
@keyframes slideInRight  { from { opacity:0; transform:translateX(50px); }  to { opacity:1; transform:translateX(0); } }
@keyframes slideOutRight { from { opacity:1; }                               to { opacity:0; transform:translateX(100px); } }
@keyframes fadeInLeft    { from { opacity:0; transform:translateX(-30px); } to { opacity:1; transform:translateX(0); } }
@keyframes fadeInDown    { from { opacity:0; transform:translateY(-20px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeIn        { from { opacity:0; } to { opacity:1; } }
@keyframes slideUp       { from { opacity:0; transform:translateY(40px) scale(0.97); }
                           to   { opacity:1; transform:translateY(0)   scale(1); } }
`;
document.head.appendChild(style);

console.log('📊 Dashboard loaded');
