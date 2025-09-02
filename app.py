from flask import Flask, request, render_template, jsonify
import os
import base64
import logging
import cv2
import numpy as np

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fake AI results for slides
known_results = {
    "slide1": "Diagnosis: Plasmodium Falciparum Detected\nConfidence: 92%\nSeverity: High",
    "slide2": "Diagnosis: Plasmodium Vivax Detected\nConfidence: 87%\nSeverity: Moderate",
    "slide3": "Diagnosis: No Malaria Detected\nConfidence: 95%\nStatus: Clear",
    "slide4": "Diagnosis: Plasmodium Ovale Detected\nConfidence: 89%\nSeverity: Low to Moderate",
    "slide5": "Diagnosis: Plasmodium Malariae Detected\nConfidence: 91%\nSeverity: Moderate",
    "slide6": "Diagnosis: Mixed Infection (Falciparum + Vivax)\nConfidence: 85%\nSeverity: High",
    "slide7": "Diagnosis: No Malaria Detected, Artifacts Noted\nConfidence: 93%",
    "slide8": "Diagnosis: Plasmodium Knowlesi Detected\nConfidence: 88%",
    "slide9": "Diagnosis: Suspected Malaria, Indeterminate Species\nConfidence: 80%",
    "slide10": "Diagnosis: No Malaria Detected, Healthy Sample\nConfidence: 98%"
}

def highlight_parasite(file_bytes):
    """
    Fake parasite highlighting by drawing a red rectangle in the middle of the image.
    """
    np_bytes = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image could not be decoded. Possibly corrupt or unsupported format.")

    h, w, _ = img.shape

    # Fake bounding box in the center
    start_point = (int(w * 0.4), int(h * 0.4))
    end_point = (int(w * 0.6), int(h * 0.6))
    color = (0, 0, 255)  # Red box
    thickness = 3

    cv2.rectangle(img, start_point, end_point, color, thickness)

    # Encode back to base64 PNG
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    filename = file.filename

    if filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        return jsonify({"error": "Invalid file format. Please upload .jpg or .png"}), 400

    # Get base name (without extension)
    base_filename = os.path.splitext(filename)[0]

    # Pick fake result
    result = known_results.get(base_filename, "Diagnosis: No Diagnostic Data Available")

    # Prepare result for frontend
    formatted_result = f"""
    <div class="result-section">
        <h3>AI Diagnosis Report</h3>
        <pre>{result}</pre>
    </div>
    """

    try:
        # Read image once
        file_bytes = file.read()
        highlighted_image = highlight_parasite(file_bytes)
        mime_type = "image/png"
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": f"Image processing error: {str(e)}"}), 500

    return jsonify({
        "result": formatted_result,
        "image_data": highlighted_image,
        "mime_type": mime_type
    })


if __name__ == "__main__":
    app.run(debug=True)
