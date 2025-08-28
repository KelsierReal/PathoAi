from flask import Flask, request, render_template, jsonify
import os
import base64
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined mappings for 10 slides with detailed fake results
known_results = {
    'slide1': """
Diagnosis: Plasmodium Falciparum Detected
Confidence: 92%
Severity: High
Explanation: The AI model detected characteristic ring forms and gametocytes, confirming Plasmodium Falciparum, the most severe malaria parasite linked to cerebral malaria and organ failure.
Recommendations: Initiate artemisinin-based combination therapy (ACT) immediately. Hospitalization is critical for severe cases. Consult an infectious disease specialist.
""",
    'slide2': """
Diagnosis: Plasmodium Vivax Detected
Confidence: 87%
Severity: Moderate
Explanation: Enlarged red blood cells with Schüffner's dots and trophozoites observed, indicative of Plasmodium Vivax, known for relapsing malaria due to dormant liver hypnozoites.
Recommendations: Administer chloroquine followed by primaquine to eradicate liver stages. Monitor for relapses every 3-6 months.
""",
    'slide3': """
Diagnosis: No Malaria Detected
Confidence: 95%
Status: Clear
Explanation: The blood smear shows normal erythrocytes with no parasitic forms, ruling out malaria infection.
Recommendations: Continue mosquito prevention (nets, repellents). Retest if symptoms like fever or fatigue persist.
""",
    'slide4': """
Diagnosis: Plasmodium Ovale Detected
Confidence: 89%
Severity: Low to Moderate
Explanation: Oval-shaped infected cells with James' dots detected, characteristic of Plasmodium Ovale, a relapsing malaria species with milder symptoms.
Recommendations: Treat with chloroquine and primaquine. Schedule follow-up to monitor for relapses.
""",
    'slide5': """
Diagnosis: Plasmodium Malariae Detected
Confidence: 91%
Severity: Moderate
Explanation: Band forms and rosette schizonts identified, typical of Plasmodium Malariae, which can cause chronic infections with quartan fever cycles.
Recommendations: Use chloroquine or ACT. Monitor kidney function to prevent nephrotic syndrome.
""",
    'slide6': """
Diagnosis: Mixed Infection (Falciparum + Vivax)
Confidence: 85%
Severity: High
Explanation: Both Falciparum ring forms and Vivax trophozoites detected, indicating a complex mixed infection that increases treatment complexity.
Recommendations: Broad-spectrum ACT required. Urgent hospital evaluation to manage potential complications.
""",
    'slide7': """
Diagnosis: No Malaria Detected, Artifacts Noted
Confidence: 93%
Status: Clear with Notes
Explanation: Staining artifacts mimicking parasites observed, but no confirmed infection. Erythrocytes appear structurally normal.
Recommendations: Ensure high-quality slide preparation and retest if symptomatic.
""",
    'slide8': """
Diagnosis: Plasmodium Knowlesi Detected
Confidence: 88%
Severity: Variable (Potentially High)
Explanation: Banana-shaped gametocytes and rapid replication cycles detected, consistent with Plasmodium Knowlesi, a zoonotic malaria prevalent in Southeast Asia.
Recommendations: ACT treatment. Report to health authorities in endemic regions.
""",
    'slide9': """
Diagnosis: Suspected Malaria, Indeterminate Species
Confidence: 80%
Severity: Unknown
Explanation: Parasitic forms present, but poor slide quality prevents species identification. General malaria features like ring forms observed.
Recommendations: Retest with a high-quality sample. Consider empirical antimalarial treatment if symptoms are present.
""",
    'slide10': """
Diagnosis: No Malaria Detected, Healthy Sample
Confidence: 98%
Status: Clear
Explanation: Pristine blood smear with healthy erythrocytes and no parasitic elements, confirming no malaria infection.
Recommendations: Maintain preventive measures (e.g., mosquito nets). Annual screening in endemic areas.
"""
}

@app.route('/', methods=['GET'])
def index():
    logger.info("Rendering index page")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
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

    return jsonify({
        'result': full_result,
        'image_data': image_data,
        'mime_type': mime_type
    })
