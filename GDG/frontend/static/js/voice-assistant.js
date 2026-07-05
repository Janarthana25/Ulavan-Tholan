/**
 * Voice Assistant - Ulavan Tholan
 * Dedicated page for AI voice interactions
 */

// ==================== Voice Assistant Variables ====================
let voiceLang = 'en-IN';
let recognition = null;
let isListening = false;

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    // Setup logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.doLogout();
        });
    }

    // Apply translations
    if (window.LangManager) {
        window.LangManager.applyAll();
    }

    // Check for speech recognition support
    checkSpeechSupport();
});

// ==================== Speech Recognition Support ====================
function checkSpeechSupport() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        const status = document.getElementById('voiceStatus');
        if (status) {
            status.innerHTML = '❌ Speech recognition not supported.<br>Please use Chrome browser for best experience.';
            status.style.color = '#f44336';
        }
        const mic = document.getElementById('voiceMic');
        if (mic) {
            mic.style.opacity = '0.4';
            mic.style.cursor = 'not-allowed';
        }
        return false;
    }
    return true;
}

// ==================== Language Selection ====================
window.setVoiceLang = function(lang) {
    voiceLang = lang;
    console.log(`🌍 Voice language changed to: ${lang}`);
    
    // Update language button styles
    document.querySelectorAll('.voice-page .lang-btn').forEach(b => {
        b.classList.toggle('active-lang',
            (lang === 'en-IN' && b.textContent === 'English') ||
            (lang === 'ta-IN' && b.textContent === 'தமிழ்') ||
            (lang === 'hi-IN' && b.textContent === 'हिंदी')
        );
    });
    
    // Update status message based on language
    const status = document.getElementById('voiceStatus');
    if (status && !isListening) {
        const statusText = lang === 'ta-IN' ? 'மைக்ரோஃபோனை கிளிக் செய்து பேசுங்கள்' :
                          lang === 'hi-IN' ? 'बोलने के लिए माइक्रोफ़ोन पर क्लिक करें' :
                          'Click microphone to speak';
        status.textContent = statusText;
    }
    
    const langName = lang === 'ta-IN' ? 'Tamil' : lang === 'hi-IN' ? 'Hindi' : 'English';
    window.UlavanTholan.showNotification(`🌍 Language changed to ${langName}`, 'info');
};

// ==================== Voice Recognition ====================
window.toggleVoice = function() {
    if (!checkSpeechSupport()) {
        return;
    }

    if (isListening) {
        stopListening();
        return;
    }

    startListening();
};

function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = voiceLang;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.continuous = false;

    const mic = document.getElementById('voiceMic');
    const status = document.getElementById('voiceStatus');
    const transcript = document.getElementById('voiceTranscript');
    const responseSection = document.getElementById('responseSection');

    recognition.onstart = () => {
        isListening = true;
        console.log('🎤 Speech recognition started');
        
        if (mic) {
            mic.style.transform = 'scale(1.3)';
            mic.textContent = '🔴';
            mic.style.animation = 'pulse 1s infinite';
        }
        
        if (status) {
            const listeningText = voiceLang === 'ta-IN' ? '🎙️ கேட்டுக்கொண்டிருக்கிறேன்... இப்போது பேசுங்கள்' :
                                 voiceLang === 'hi-IN' ? '🎙️ सुन रहा हूँ... अब बोलें' :
                                 '🎙️ Listening... Speak now';
            status.textContent = listeningText;
            status.style.color = 'var(--primary-green)';
        }
        
        if (transcript) {
            transcript.textContent = 'Listening for your voice...';
        }
        
        if (responseSection) {
            responseSection.style.display = 'none';
        }
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        console.log('🗣️ Speech recognized:', text);
        
        if (transcript) {
            transcript.textContent = text;
        }
        
        // Get AI response
        const answer = getVoiceAnswer(text.toLowerCase(), voiceLang);
        showResponse(answer);
        
        // Speak the response
        speakResponse(answer, voiceLang);
        
        // Save to activity log
        saveActivity(text, answer);
    };

    recognition.onerror = (event) => {
        console.error('🚫 Speech recognition error:', event.error);
        isListening = false;
        
        if (status) {
            const errorText = voiceLang === 'ta-IN' ? '❌ பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்' :
                             voiceLang === 'hi-IN' ? '❌ त्रुटि हुई। कृपया पुनः प्रयास करें' :
                             '❌ Error occurred. Please try again';
            status.textContent = errorText + ': ' + event.error;
            status.style.color = '#f44336';
        }
        
        resetMicrophone();
    };

    recognition.onend = () => {
        isListening = false;
        console.log('🎤 Speech recognition ended');
        resetMicrophone();
        
        if (status) {
            const readyText = voiceLang === 'ta-IN' ? 'மீண்டும் பேச மைக்ரோஃபோனை கிளிக் செய்யவும்' :
                             voiceLang === 'hi-IN' ? 'फिर से बोलने के लिए माइक्रोफ़ोन पर क्लिक करें' :
                             'Click microphone to speak again';
            status.textContent = readyText;
            status.style.color = 'var(--medium-gray)';
        }
    };

    try {
        recognition.start();
    } catch (error) {
        console.error('Failed to start speech recognition:', error);
        window.UlavanTholan.showNotification('❌ Failed to start voice recognition', 'error');
    }
}

function stopListening() {
    if (recognition) {
        recognition.stop();
    }
    isListening = false;
    resetMicrophone();
    console.log('🛑 Speech recognition stopped by user');
}

function resetMicrophone() {
    const mic = document.getElementById('voiceMic');
    if (mic) {
        mic.style.transform = 'scale(1)';
        mic.textContent = '🎤';
        mic.style.animation = 'float 3s ease-in-out infinite';
    }
}

// ==================== AI Response System ====================
function getVoiceAnswer(text, lang) {
    const responses = {
        'en-IN': {
            default: "I'm your AI farming assistant. I can help with crop diseases, irrigation, fertilizers, weather, and general farming advice. What would you like to know?",
            disease: "For plant diseases, I recommend taking a photo of the affected plant and using our Disease Detection feature for accurate diagnosis. Common treatments include neem oil spray, copper fungicides, or removing affected parts.",
            water: "Proper irrigation depends on your crop type and soil. Generally, water when soil moisture drops below 40%. Early morning (6-8 AM) is the best time. Drip irrigation saves 30-50% water compared to flood irrigation.",
            fertilizer: "For balanced nutrition, use NPK fertilizers in split doses. Organic options like compost and vermicompost are excellent for soil health. Soil testing helps determine exact nutrient needs.",
            weather: "Current weather conditions look favorable for most crops. Monitor for sudden temperature changes and rainfall patterns. Use weather forecasts for irrigation and pest management planning.",
            crop: "Choose crops based on your soil type, climate, and market demand. Crop rotation helps maintain soil fertility. Consider local varieties that are adapted to your region.",
            pest: "For natural pest control, use neem oil spray in the evening. Beneficial insects like ladybugs help control aphids. Avoid pesticides during flowering to protect pollinators.",
            organic: "Organic farming improves soil health and reduces chemical inputs. Use compost, green manure, and beneficial microorganisms. Crop rotation and companion planting are key practices."
        },
        'ta-IN': {
            default: "நான் உங்கள் AI விவசாய உதவியாளர். பயிர் நோய்கள், நீர்ப்பாசனம், உரங்கள், வானிலை மற்றும் விவசாய ஆலோசனைகள் குறித்து உதவ முடியும். எது தெரிந்துகொள்ள விரும்புகிறீர்கள்?",
            disease: "தாவர நோய்களுக்கு, பாதிக்கப்பட்ட தாவரத்தின் புகைப்படம் எடுத்து எங்கள் நோய் கண்டறிதல் அம்சத்தைப் பயன்படுத்துங்கள். வேப்பெண்ணெய் தெளித்தல், தாமிர பூஞ்சைக் கொல்லிகள் அல்லது பாதிக்கப்பட்ட பகுதிகளை அகற்றுதல் போன்ற சிகிச்சைகள் உள்ளன.",
            water: "சரியான நீர்ப்பாசனம் உங்கள் பயிர் வகை மற்றும் மண்ணைப் பொறுத்தது. மண் ஈரப்பதம் 40%க்குக் கீழே போகும்போது நீர் பாய்ச்சுங்கள். அதிகாலை (6-8 மணி) சிறந்த நேரம்.",
            fertilizer: "சமச்சீர் ஊட்டச்சத்துக்கு NPK உரங்களைப் பிளவு அளவுகளில் பயன்படுத்துங்கள். தொழுவுரம் மற்றும் மண்புழு உரம் போன்ற இயற்கை உரங்கள் மண் ஆரோக்கியத்திற்கு நல்லது.",
            weather: "தற்போதைய வானிலை பெரும்பாலான பயிர்களுக்கு சாதகமாக உள்ளது. திடீர் வெப்பநிலை மாற்றங்கள் மற்றும் மழைப்பொழிவு முறைகளை கண்காணிக்கவும்.",
            crop: "உங்கள் மண் வகை, காலநிலை மற்றும் சந்தை தேவையின் அடிப்படையில் பயிர்களைத் தேர்வு செய்யுங்கள். பயிர் சுழற்சி மண் வளத்தைப் பராமரிக்க உதவுகிறது.",
            pest: "இயற்கை பூச்சிக் கட்டுப்பாட்டிற்கு மாலை நேரத்தில் வேப்பெண்ணெய் தெளியுங்கள். வண்டுகள் போன்ற நன்மை பயக்கும் பூச்சிகள் அசுவினிகளைக் கட்டுப்படுத்த உதவுகின்றன।"
        },
        'hi-IN': {
            default: "मैं आपका AI कृषि सहायक हूं। फसल रोग, सिंचाई, उर्वरक, मौसम और सामान्य कृषि सलाह में मदद कर सकता हूं। आप क्या जानना चाहते हैं?",
            disease: "पौधों की बीमारियों के लिए, प्रभावित पौधे की तस्वीर लें और सटीक निदान के लिए हमारी रोग पहचान सुविधा का उपयोग करें। सामान्य उपचार में नीम तेल स्प्रे, कॉपर कवकनाशी शामिल हैं।",
            water: "उचित सिंचाई आपकी फसल के प्रकार और मिट्टी पर निर्भर करती है। जब मिट्टी की नमी 40% से नीचे हो तो पानी दें। सुबह (6-8 बजे) सबसे अच्छा समय है।",
            fertilizer: "संतुलित पोषण के लिए NPK उर्वरकों का विभाजित खुराक में उपयोग करें। खाद और वर्मी कंपोस्ट जैसे जैविक विकल्प मिट्टी के स्वास्थ्य के लिए उत्कृष्ट हैं।",
            weather: "वर्तमान मौसम की स्थिति अधिकांश फसलों के लिए अनुकूल दिख रही है। अचानक तापमान परिवर्तन और वर्षा पैटर्न की निगरानी करें।",
            crop: "अपनी मिट्टी के प्रकार, जलवायु और बाजार की मांग के आधार पर फसलों का चयन करें। फसल चक्र मिट्टी की उर्वरता बनाए रखने में मदद करता है।",
            pest: "प्राकृतिक कीट नियंत्रण के लिए शाम को नीम का तेल स्प्रे करें। लेडीबग जैसे लाभकारी कीड़े एफिड्स को नियंत्रित करने में मदद करते हैं।"
        }
    };

    const r = responses[lang] || responses['en-IN'];
    
    // Enhanced keyword matching
    if (text.includes('disease') || text.includes('sick') || text.includes('spot') || text.includes('நோய்') || text.includes('रोग') || text.includes('बीमारी')) return r.disease;
    if (text.includes('water') || text.includes('irrig') || text.includes('rain') || text.includes('நீர்') || text.includes('पानी') || text.includes('सिंचाई')) return r.water;
    if (text.includes('fertilizer') || text.includes('nutrient') || text.includes('manure') || text.includes('உரம்') || text.includes('उर्वरक') || text.includes('खाद')) return r.fertilizer;
    if (text.includes('weather') || text.includes('climate') || text.includes('வானிலை') || text.includes('मौसम') || text.includes('जलवायु')) return r.weather;
    if (text.includes('crop') || text.includes('plant') || text.includes('grow') || text.includes('பயிர்') || text.includes('फसल') || text.includes('पौधे')) return r.crop;
    if (text.includes('pest') || text.includes('insect') || text.includes('bug') || text.includes('பூச்சி') || text.includes('कीट') || text.includes('कीड़े')) return r.pest;
    if (text.includes('organic') || text.includes('natural') || text.includes('இயற்கை') || text.includes('जैविक') || text.includes('प्राकृतिक')) return r.organic;
    
    return r.default;
}

function showResponse(response) {
    const responseSection = document.getElementById('responseSection');
    const responseDiv = document.getElementById('voiceResponse');
    
    if (responseSection && responseDiv) {
        responseDiv.innerHTML = response;
        responseSection.style.display = 'block';
        responseSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function speakResponse(text, lang) {
    if (window.speechSynthesis) {
        // Stop any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        utterance.onstart = () => {
            console.log('🔊 Starting text-to-speech');
        };
        
        utterance.onend = () => {
            console.log('✅ Text-to-speech completed');
        };
        
        utterance.onerror = (e) => {
            console.error('🚫 Speech synthesis error:', e);
        };
        
        setTimeout(() => {
            window.speechSynthesis.speak(utterance);
        }, 500);
    }
}

// ==================== Sample Questions ====================
window.askSample = function(question) {
    const transcript = document.getElementById('voiceTranscript');
    if (transcript) {
        transcript.textContent = question;
    }
    
    const answer = getVoiceAnswer(question.toLowerCase(), voiceLang);
    showResponse(answer);
    speakResponse(answer, voiceLang);
    saveActivity(question, answer);
    
    window.UlavanTholan.showNotification('🤖 Sample question answered!', 'success');
};

// ==================== Utility Functions ====================
window.clearConversation = function() {
    const transcript = document.getElementById('voiceTranscript');
    const responseSection = document.getElementById('responseSection');
    
    if (transcript) {
        transcript.textContent = 'Your speech will appear here...';
    }
    
    if (responseSection) {
        responseSection.style.display = 'none';
    }
    
    // Stop any ongoing speech
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    
    // Stop listening if active
    if (isListening) {
        stopListening();
    }
    
    window.UlavanTholan.showNotification('🗑️ Conversation cleared', 'info');
};

window.goBack = function() {
    // Stop any ongoing speech or recognition
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    if (isListening && recognition) {
        recognition.stop();
    }
    
    // Navigate back to dashboard
    window.location.href = '/dashboard';
};

function saveActivity(question, answer) {
    try {
        const activities = JSON.parse(localStorage.getItem('activities') || '[]');
        const activity = {
            icon: '🎤',
            title: 'Voice Question Asked',
            description: question.substring(0, 50) + (question.length > 50 ? '...' : ''),
            time: 'Just now'
        };
        
        activities.unshift(activity);
        if (activities.length > 15) activities.pop();
        localStorage.setItem('activities', JSON.stringify(activities));
        
        console.log('💾 Activity saved to localStorage');
    } catch (error) {
        console.error('Failed to save activity:', error);
    }
}

// ==================== Animations ====================
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
    0% { transform: scale(1.3); }
    50% { transform: scale(1.4); }
    100% { transform: scale(1.3); }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
`;
document.head.appendChild(style);

console.log('🎤 Voice Assistant page loaded successfully');