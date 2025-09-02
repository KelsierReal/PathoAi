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
PREDEFINED_USERNAME = 'kelsier'
PREDEFINED_PASSWORD = 'robotics'

# Predefined mappings for 10 slides with detailed fake results
known_results = {
    'slide1': """
Diagnosis: Plasmodium Falciparum Detected
Confidence: 92%
Severity: High
Explanation: The AI model detected characteristic ring forms and gametocytes, confirming Plasmodium Falciparum, the most severe malaria parasite linked to cerebral malaria and organ failure.
Recommendations: Initiate artemisinin-based combination therapy (ACT) immediately. Hospitalization is critical for severe cases. Consult an infectious disease specialist.
Highlights: Ring forms in red blood cells.
""",
    'slide2': """
Diagnosis: Plasmodium Vivax Detected
Confidence: 87%
Severity: Moderate
Explanation: Enlarged red blood cells with Schüffner's dots and trophozoites observed, indicative of Plasmodium Vivax, known for relapsing malaria due to dormant liver hypnozoites.
Recommendations: Administer chloroquine followed by primaquine to eradicate liver stages. Monitor for relapses every 3-6 months.
Highlights: Enlarged RBCs with dots.
""",
    'slide3': """
Diagnosis: No Malaria Detected
Confidence: 95%
Status: Clear
Explanation: The blood smear shows normal erythrocytes with no parasitic forms, ruling out malaria infection.
Recommendations: Maintain mosquito prevention (nets, repellents). Retest if symptoms like fever or fatigue persist.
Highlights: Normal cells.
""",
    'slide4': """
Diagnosis: Plasmodium Ovale Detected
Confidence: 89%
Severity: Low to Moderate
Explanation: Oval-shaped infected cells with James' dots detected, characteristic of Plasmodium Ovale, a relapsing malaria species with milder symptoms.
Recommendations: Treat with chloroquine and primaquine. Schedule follow-up to monitor for relapses.
Highlights: Oval cells with dots.
""",
    'slide5': """
Diagnosis: Plasmodium Malariae Detected
Confidence: 91%
Severity: Moderate
Explanation: Band forms and rosette schizonts identified, typical of Plasmodium Malariae, which can cause chronic infections with quartan fever cycles.
Recommendations: Use chloroquine or ACT. Monitor kidney function to prevent nephrotic syndrome.
Highlights: Band forms.
""",
    'slide6': """
Diagnosis: Mixed Infection (Falciparum + Vivax)
Confidence: 85%
Severity: High
Explanation: Both Falciparum ring forms and Vivax trophozoites detected, indicating a complex mixed infection that increases treatment complexity.
Recommendations: Broad-spectrum ACT required. Urgent hospital evaluation to manage potential complications.
Highlights: Ring forms and trophozoites.
""",
    'slide7': """
Diagnosis: No Malaria Detected, Artifacts Noted
Confidence: 93%
Status: Clear with Notes
Explanation: Staining artifacts mimicking parasites observed, but no confirmed infection. Erythrocytes appear structurally normal.
Recommendations: Ensure high-quality slide preparation and retest if symptomatic.
Highlights: Staining artifacts.
""",
    'slide8': """
Diagnosis: Plasmodium Knowlesi Detected
Confidence: 88%
Severity: Variable (Potentially High)
Explanation: Banana-shaped gametocytes and rapid replication cycles detected, consistent with Plasmodium Knowlesi, a zoonotic malaria prevalent in Southeast Asia.
Recommendations: ACT treatment. Report to health authorities in endemic regions.
Highlights: Banana-shaped gametocytes.
""",
    'slide9': """
Diagnosis: Suspected Malaria, Indeterminate Species
Confidence: 80%
Severity: Unknown
Explanation: Parasitic forms present, but poor slide quality prevents species identification. General malaria features like ring forms observed.
Recommendations: Retest with a high-quality sample. Consider empirical antimalarial treatment if symptoms are present.
Highlights: Parasitic forms.
""",
    'slide10': """
Diagnosis: No Malaria Detected, Healthy Sample
Confidence: 98%
Status: Clear
Explanation: Pristine blood smear with healthy erythrocytes and no parasitic elements, confirming no malaria infection.
Recommendations: Maintain preventive measures (e.g., mosquito nets). Annual screening in endemic areas.
Highlights: Healthy erythrocytes.
"""
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
        session['settings'] = {'theme': 'dark', 'notifications': True, 'highlight_color': 'red', 'language': 'en'}
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
    if ext.lower() not in ['.png', '.jpg', '.jpeg']:
        logger.error(f"Invalid file format: {ext}")
        return jsonify({'error': 'Invalid file format. Please upload a .png or .jpg file.'}), 400

    # Get AI diagnosis based on base filename
    result = known_results.get(base_filename, """
Diagnosis: No Diagnostic Data Available
Explanation: The uploaded slide does not match any known demo samples (slide1 to slide10, .png or .jpg).
Recommendations: Rename your file to match a demo slide (e.g., slide1.jpg) or upload a supported sample.
Highlights: No highlights available.
""")

    # Format result for UI
    full_result = f"""
<div class='result-section'>
    <h3>AI Diagnosis Report</h3>
    <pre>{result.strip()}</pre>
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
        'result': result.strip(),
        'image_data': image_data,
        'mime_type': mime_type,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    return jsonify({
        'result': full_result,
        'image_data': image_data,
        'mime_type': mime_type
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

    return jsonify({'settings': session.get('settings', {'theme': 'dark', 'notifications': True, 'highlight_color': 'red', 'language': 'en'})})

if __name__ == '__main__':
    app.run(debug=True)
```
