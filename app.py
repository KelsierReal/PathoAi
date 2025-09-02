from flask import Flask, request, render_template, jsonify
import os
import base64
import logging
import cv2
import numpy as np

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined mappings for 10 slides with detailed fake results
known_results = {
    'slide1': """Diagnosis: Plasmodium Falciparum Detected ...""",
    'slide2': """Diagnosis: Plasmodium Vivax Detected ...""",
    'slide3': """Diagnosis: No Malaria Detected ...""",
    'slide4': """Diagnosis: Plasmodium Ovale Detected ...""",
    'slide5': """Diagnosis: Plasmodium Malariae Detected ...""",
    'slide6': """Diagnosis: Mixed Infection (Falciparum + Vivax) ...""",
    'slide7': """Diagnosis: No Malaria Detected, Artifacts Noted ...""",
    'slide8': """Diagnosis: Plasmodium Knowlesi Detected ...""",
    'slide9': """Diagnosis: Suspected Malaria, Indeterminate Species ...""",
    'slide10': """Diagnosis: No Malaria Detected, Healthy Sample ..."""
}

def highlight_parasite(image_stream):
    """Simulate parasite highlighting with a red bounding box"""
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image data")

    # Fake bounding box in the middle of the image
    h, w, _ = img.shape
    start_point = (int(w * 0.4), int(h * 0.4))
    end_point = (int(w * 0.6), int(h * 0.6))
    color = (0, 0, 255)  # Red
    thickness = 3
    cv2.rectangle(img, start_point, end_point, color, thickness)

    # Encode back to base64
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')


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
    result = known_results.get(base_filename, "Diagnosis: No Diagnostic Data Available")

    # Format result for UI
    full_result = f"""
    <div class='result-section'>
        <h3>AI Diagnosis Report</h3>
        <pre>{result.strip()}</pre>
    </div>
    """

    # Highlight parasite & prepare preview
    try:
        file.stream.seek(0)  # Reset stream before processing
        highlighted_image = highlight_parasite(file.stream)
        mime_type = "image/png"
        logger.info("Parasite highlighted in image")
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        return jsonify({'error': f"Image processing error: {str(e)}"}), 500

    return jsonify({
        'result': full_result,
        'image_data': highlighted_image,
        'mime_type': mime_type
    })


if __name__ == '__main__':
    app.run(debug=True)
