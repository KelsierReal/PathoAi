from flask import Flask, request, render_template, jsonify
import subprocess
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
Explanation: The AI model identified characteristic ring forms and gametocytes, indicative of Plasmodium Falciparum, the most severe malaria parasite causing complications like cerebral malaria.
Recommendations: Immediate initiation of artemisinin-based combination therapy (ACT). Hospitalization recommended for severe symptoms. Consult a specialist.
""",
    'slide2': """
Diagnosis: Plasmodium Vivax Detected
Confidence: 87%
Severity: Moderate
Explanation: Enlarged red blood cells with Schüffner's dots and trophozoites observed, typical of Plasmodium Vivax, which can cause relapsing malaria due to liver hypnozoites.
Recommendations: Administer chloroquine followed by primaquine to clear liver stages. Monitor for relapse over 6-12 months.
""",
    'slide3': """
Diagnosis: No Malaria Detected
Confidence: 95%
Status: Clear
Explanation: Blood smear shows normal erythrocytes with no parasitic forms. No evidence of malaria infection.
Recommendations: Maintain mosquito prevention (nets, repellents). Retest if symptoms persist.
""",
    'slide4': """
Diagnosis: Plasmodium Ovale Detected
Confidence: 89%
Severity: Low to Moderate
Explanation: Oval-shaped infected cells with James' dots detected, characteristic of Plasmodium Ovale, a less common relapsing malaria species.
Recommendations: Chloroquine treatment followed by primaquine. Schedule follow-up to monitor for relapses.
""",
    'slide5': """
Diagnosis: Plasmodium Malariae Detected
Confidence: 91%
Severity: Moderate
Explanation: Band forms and rosette schizonts identified, typical of Plasmodium Malariae, which may lead to chronic infections with quartan fever cycles.
Recommendations: Chloroquine or ACT. Monitor kidney function due to potential nephrotic syndrome.
""",
    'slide6': """
Diagnosis: Mixed Infection (Falciparum + Vivax)
Confidence: 85%
Severity: High
Explanation: Both Falciparum ring forms and Vivax trophozoites detected, indicating a complex mixed infection requiring aggressive treatment.
Recommendations: Broad-spectrum ACT. Urgent hospital evaluation to manage complications.
""",
    'slide7': """
Diagnosis: No Malaria Detected, Artifacts Noted
Confidence: 93%
Status: Clear with Notes
Explanation: Staining artifacts mimicking parasites observed, but no confirmed infection. Erythrocytes appear normal.
Recommendations: Ensure clean slide preparation and retest if symptoms persist.
""",
    'slide8': """
Diagnosis: Plasmodium Knowlesi Detected
Confidence: 88%
Severity: Variable (Potentially High)
Explanation: Banana-shaped gametocytes and rapid replication cycles detected, consistent with Plasmodium Knowlesi, a zoonotic malaria prevalent in Southeast Asia.
Recommendations: ACT treatment. Notify health authorities in endemic regions.
""",
    'slide9': """
Diagnosis: Suspected Malaria, Indeterminate Species
Confidence: 80%
Severity: Unknown
Explanation: Parasitic forms present, but poor slide quality prevents species identification. General malaria features like ring forms observed.
Recommendations: Retest with a high-quality sample. Consider empirical antimalarial treatment if clinically indicated.
""",
    'slide10': """
Diagnosis: No Malaria Detected, Healthy Sample
Confidence: 98%
Status: Clear
Explanation: Pristine blood smear with healthy erythrocytes and no parasitic elements, indicating no malaria infection.
Recommendations: Continue preventive measures. Annual screening in endemic areas.
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

    # Get Python result based on base filename
    py_result = known_results.get(base_filename, """
Diagnosis: No Diagnostic Data Available
Explanation: The uploaded slide does not match any known demo samples (slide1 to slide10, .png or .jpg).
Recommendations: Rename your file to match a demo slide (e.g., slide1.jpg) or upload a supported sample.
""")

    # Run C program
    c_output = ''
    try:
        c_output = subprocess.check_output('./analysis', shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        logger.info("C program executed successfully")
    except subprocess.CalledProcessError as e:
        c_output = f"C Analysis Error: {e.output.decode('utf-8')}"
        logger.error(f"C program error: {c_output}")
    except Exception as e:
        c_output = f"C Analysis Error: {str(e)}"
        logger.error(f"C program exception: {c_output}")

    # Run Java program
    java_output = ''
    try:
        java_output = subprocess.check_output('java ReportGenerator', shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        logger.info("Java program executed successfully")
    except subprocess.CalledProcessError as e:
        java_output = f"Java Report Error: {e.output.decode('utf-8')}"
        logger.error(f"Java program error: {java_output}")
    except Exception as e:
        java_output = f"Java Report Error: {str(e)}"
        logger.error(f"Java program exception: {java_output}")

    # Combine outputs with HTML formatting
    full_result = f"""
<div class='result-section'>
    <h3>AI Diagnosis</h3>
    <pre>{py_result.strip()}</pre>
</div>
<div class='result-section'>
    <h3>Low-Level Image Scan (C)</h3>
    <pre>{c_output.strip()}</pre>
</div>
<div class='result-section'>
    <h3>Medical Report (Java)</h3>
    <pre>{java_output.strip()}</pre>
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
