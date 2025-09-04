 ```python
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import os
import base64
import logging
from flask_session import Session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined credentials
PREDEFINED_USERNAME = 'Kelsier'
PREDEFINED_PASSWORD = 'Gondal'

# Predefined mappings for 20 slides with detailed fake results
known_results = {
    'slide1': {
        'diagnosis': 'Plasmodium Falciparum Detected',
        'confidence': 92,
        'severity': 'High',
        'explanation': 'The AI model detected characteristic ring forms and gametocytes, confirming Plasmodium Falciparum, the most severe malaria parasite linked to cerebral malaria and organ failure.',
        'recommendations': 'Initiate artemisinin-based combination therapy (ACT) immediately. Hospitalization is critical for severe cases. Consult an infectious disease specialist.',
        'highlights': ['Ring forms in red blood cells', 'Gametocytes']
    },
    'slide2': {
        'diagnosis': 'Plasmodium Vivax Detected',
        'confidence': 87,
        'severity': 'Moderate',
        'explanation': 'Enlarged red blood cells with Schüffner\'s dots and trophozoites observed, indicative of Plasmodium Vivax, known for relapsing malaria due to dormant liver hypnozoites.',
        'recommendations': 'Administer chloroquine followed by primaquine to eradicate liver stages. Monitor for relapses every 3-6 months.',
        'highlights': ['Enlarged RBCs with dots', 'Trophozoites']
    },
    'slide3': {
        'diagnosis': 'No Malaria Detected',
        'confidence': 95,
        'severity': 'None',
        'explanation': 'The blood smear shows normal erythrocytes with no parasitic forms, ruling out malaria infection.',
        'recommendations': 'Maintain mosquito prevention (nets, repellents). Retest if symptoms like fever or fatigue persist.',
        'highlights': []
    },
    'slide4': {
        'diagnosis': 'Plasmodium Ovale Detected',
        'confidence': 89,
        'severity': 'Low to Moderate',
        'explanation': 'Oval-shaped infected cells with James\' dots detected, characteristic of Plasmodium Ovale, a relapsing malaria species with milder symptoms.',
        'recommendations': 'Treat with chloroquine and primaquine. Schedule follow-up to monitor for relapses.',
        'highlights': ['Oval cells with dots']
    },
    'slide5': {
        'diagnosis': 'Plasmodium Malariae Detected',
        'confidence': 91,
        'severity': 'Moderate',
        'explanation': 'Band forms and rosette schizonts identified, typical of Plasmodium Malariae, which can cause chronic infections with quartan fever cycles.',
        'recommendations': 'Use chloroquine or ACT. Monitor kidney function to prevent nephrotic syndrome.',
        'highlights': ['Band forms', 'Rosette schizonts']
    },
    'slide6': {
        'diagnosis': 'Mixed Infection (Falciparum + Vivax)',
        'confidence': 85,
        'severity': 'High',
        'explanation': 'Both Falciparum ring forms and Vivax trophozoites detected, indicating a complex mixed infection that increases treatment complexity.',
        'recommendations': 'Broad-spectrum ACT required. Urgent hospital evaluation to manage potential complications.',
        'highlights': ['Ring forms', 'Trophozoites']
    },
    'slide7': {
        'diagnosis': 'No Malaria Detected, Artifacts Noted',
        'confidence': 93,
        'severity': 'None',
        'explanation': 'Staining artifacts mimicking parasites observed, but no confirmed infection. Erythrocytes appear structurally normal.',
        'recommendations': 'Ensure high-quality slide preparation and retest if symptomatic.',
        'highlights': ['Staining artifacts']
    },
    'slide8': {
        'diagnosis': 'Plasmodium Knowlesi Detected',
        'confidence': 88,
        'severity': 'Variable (Potentially High)',
        'explanation': 'Banana-shaped gametocytes and rapid replication cycles detected, consistent with Plasmodium Knowlesi, a zoonotic malaria prevalent in Southeast Asia.',
        'recommendations': 'ACT treatment. Report to health authorities in endemic regions.',
        'highlights': ['Banana-shaped gametocytes']
    },
    'slide9': {
        'diagnosis': 'Suspected Malaria, Indeterminate Species',
        'confidence': 80,
        'severity': 'Unknown',
        'explanation': 'Parasitic forms present, but poor slide quality prevents species identification. General malaria features like ring forms observed.',
        'recommendations': 'Retest with a high-quality sample. Consider empirical antimalarial treatment if symptoms are present.',
        'highlights': ['Parasitic forms']
    },
    'slide10': {
        'diagnosis': 'No Malaria Detected, Healthy Sample',
        'confidence': 98,
        'severity': 'None',
        'explanation': 'Pristine blood smear with healthy erythrocytes and no parasitic elements, confirming no malaria infection.',
        'recommendations': 'Maintain preventive measures (e.g., mosquito nets). Annual screening in endemic areas.',
        'highlights': []
    },
    'slide11': {
        'diagnosis': 'Plasmodium Falciparum (Early Stage)',
        'confidence': 90,
        'severity': 'Moderate to High',
        'explanation': 'Early ring forms detected, suggesting an initial Plasmodium Falciparum infection with potential for rapid progression.',
        'recommendations': 'Start ACT immediately. Monitor for severe symptoms like anemia or neurological signs.',
        'highlights': ['Early ring forms']
    },
    'slide12': {
        'diagnosis': 'Plasmodium Vivax (Relapse)',
        'confidence': 86,
        'severity': 'Moderate',
        'explanation': 'Reactivated hypnozoites detected, indicating a relapse of Plasmodium Vivax infection.',
        'recommendations': 'Administer primaquine to target liver stages. Follow up with blood tests.',
        'highlights': ['Hypnozoite reactivation']
    },
    'slide13': {
        'diagnosis': 'No Malaria, Possible Anemia',
        'confidence': 94,
        'severity': 'Low',
        'explanation': 'Normal erythrocytes but reduced cell density, suggesting possible anemia rather than malaria.',
        'recommendations': 'Conduct a complete blood count (CBC) to confirm anemia. Retest for malaria if symptoms persist.',
        'highlights': ['Low cell density']
    },
    'slide14': {
        'diagnosis': 'Plasmodium Ovale (Mild)',
        'confidence': 88,
        'severity': 'Low',
        'explanation': 'Mild infection with oval-shaped cells, consistent with Plasmodium Ovale.',
        'recommendations': 'Treat with chloroquine. Monitor for symptom recurrence.',
        'highlights': ['Oval cells']
    },
    'slide15': {
        'diagnosis': 'Plasmodium Malariae (Chronic)',
        'confidence': 90,
        'severity': 'Moderate',
        'explanation': 'Chronic infection with band forms, indicative of long-term Plasmodium Malariae presence.',
        'recommendations': 'Use ACT and monitor renal function. Schedule regular check-ups.',
        'highlights': ['Chronic band forms']
    },
    'slide16': {
        'diagnosis': 'Mixed Infection (Ovale + Knowlesi)',
        'confidence': 84,
        'severity': 'High',
        'explanation': 'Combination of Ovale oval cells and Knowlesi banana-shaped gametocytes detected.',
        'recommendations': 'Broad-spectrum ACT and urgent specialist consultation.',
        'highlights': ['Oval cells', 'Banana-shaped gametocytes']
    },
    'slide17': {
        'diagnosis': 'No Malaria, Bacterial Contamination',
        'confidence': 92,
        'severity': 'Low',
        'explanation': 'Bacterial artifacts detected, no malaria parasites present.',
        'recommendations': 'Improve slide preparation hygiene. Retest if needed.',
        'highlights': ['Bacterial artifacts']
    },
    'slide18': {
        'diagnosis': 'Plasmodium Knowlesi (Severe)',
        'confidence': 89,
        'severity': 'High',
        'explanation': 'High-density banana-shaped gametocytes, indicating severe Knowlesi infection.',
        'recommendations': 'Immediate ACT and hospitalization. Monitor for organ dysfunction.',
        'highlights': ['High-density gametocytes']
    },
    'slide19': {
        'diagnosis': 'Indeterminate Parasitic Infection',
        'confidence': 81,
        'severity': 'Unknown',
        'explanation': 'Unclear parasitic forms due to low-quality smear, possibly malaria.',
        'recommendations': 'Retest with a clearer sample. Consider antimalarial treatment if symptomatic.',
        'highlights': ['Unclear parasitic forms']
    },
    'slide20': {
        'diagnosis': 'Healthy Sample, No Abnormalities',
        'confidence': 99,
        'severity': 'None',
        'explanation': 'Perfect blood smear with no signs of malaria or other abnormalities.',
        'recommendations': 'Continue preventive measures. No further action needed.',
        'highlights': []
    }
}

@app.route('/', methods=['GET'])
def index():
    show_login = not session.get('logged_in', False)
    logger.info(f"Rendering index page, show_login: {show_login}")
    return render_template('index.html', show_login=show_login)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == PREDEFINED_USERNAME and password == PREDEFINED_PASSWORD:
        session['logged_in'] = True
        session['results_history'] = []
        session['settings'] = {
            'theme': 'dark',
            'notifications': True,
            'highlight_color': '#ff0000',
            'language': 'en',
            'contrast': 'normal',
            'font_size': 'medium'
        }
        logger.info("Login successful")
        return jsonify({'success': True})
    logger.warning("Login failed: incorrect credentials")
    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('results_history', None)
    session.pop('settings', None)
    logger.info("User logged out")
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('logged_in'):
        logger.error("Unauthorized upload attempt")
        return jsonify({'error': 'Please log in to upload images.'}), 401

    logger.info("Received upload request")
    if 'image' not in request.files:
        logger.error("No file uploaded")
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['image']
    filename = file.filename
    logger.info(f"Uploaded file: {filename}")

    # Extract base filename without extension
    base_filename, ext = os.path.splitext(filename)
    if ext.lower() not in ['.png', '.jpg', '.jpeg','.html']:
        logger.error(f"Invalid file format: {ext}")
        return jsonify({'error': 'Invalid file format. Please upload a .png or .jpg file.'}), 400

    # Get AI diagnosis based on base filename
    result = known_results.get(base_filename, {
        'diagnosis': 'No Diagnostic Data Available',
        'confidence': 0,
        'severity': 'Unknown',
        'explanation': 'The uploaded slide does not match any known demo samples (slide1 to slide20, .png or .jpg).',
        'recommendations': 'Rename your file to match a demo slide (e.g., slide1.jpg) or upload a supported sample.',
        'highlights': []
    })

    # Format result for UI
    full_result = f"""
<div class='result-section'>
    <h3>AI Diagnosis Report</h3>
    <pre>
Diagnosis: {result['diagnosis']}
Confidence: {result['confidence']}%
Severity: {result['severity']}
Explanation: {result['explanation']}
Recommendations: {result['recommendations']}
Highlights: {', '.join(result['highlights']) if result['highlights'] else 'None'}
    </pre>
</div>
"""

    # Encode image for preview
    try:
        file.stream.seek(0)
        image_data = base64.b64encode(file.stream.read()).decode('utf-8')
        mime_type = file.mimetype
        logger.info("Image encoded for preview")
    except Exception as e:
        logger.error(f"Image encoding error: {str(e)}")
        return jsonify({'error': f"Image processing error: {str(e)}"}), 500

    # Save to history
    session['results_history'].append({
        'filename': filename,
        'result': result,
        'image_data': image_data,
        'mime_type': mime_type,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    return jsonify({
        'result': full_result,
        'image_data': image_data,
        'mime_type': mime_type,
        'confidence': result['confidence'],
        'highlights': result['highlights']
    })

@app.route('/history', methods=['GET'])
def history():
    if not session.get('logged_in'):
        logger.error("Unauthorized history access")
        return jsonify({'error': 'Please log in to view history.'}), 401

    history = session.get('results_history', [])
    return jsonify({'history': history})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('logged_in'):
        logger.error("Unauthorized settings access")
        return jsonify({'error': 'Please log in to update settings.'}), 401

    if request.method == 'POST':
        settings = request.json
        session['settings'] = settings
        logger.info("Settings updated")
        return jsonify({'success': True})

    return jsonify({'settings': session.get('settings', {
        'theme': 'dark',
        'notifications': True,
        'highlight_color': '#ff0000',
        'language': 'en',
        'contrast': 'normal',
        'font_size': 'medium'
    })})
```
