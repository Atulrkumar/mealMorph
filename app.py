import os
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import object detection functionality
try:
    # First try to import the simplified detection for Vercel
    from simplified_detection import detect_objects
    DETECTION_FN = detect_objects
    IMPLEMENTATION = "Simplified (Vercel)"
except ImportError:
    try:
        from object_detection import detect_objects as torch_detect
        DETECTION_FN = torch_detect
        IMPLEMENTATION = "PyTorch"
    except ImportError:
        try:
            from cpu_mmdet_object_detection import detect_objects as mmdet_detect
            DETECTION_FN = lambda image_path: mmdet_detect(image_path, device='cpu')
            IMPLEMENTATION = "MMDetection (CPU)"
        except ImportError:
            print("WARNING: No object detection implementation found. Using fallback detection.")
            # Define a fallback detection function
            def fallback_detect(image_path):
                return [{"label": "food", "confidence": 0.95, "bbox": [10, 10, 100, 100]}]
            DETECTION_FN = fallback_detect
            IMPLEMENTATION = "Fallback (No ML)"

# Import recipe generation functionality
try:
    # First try to import the simplified recipe generator for Vercel
    from simplified_recipe import generate_recipe
    RECIPE_GENERATION_AVAILABLE = True
except ImportError:
    try:
        from recipe_generator import generate_recipe
        RECIPE_GENERATION_AVAILABLE = True
    except ImportError:
        RECIPE_GENERATION_AVAILABLE = False
        print("WARNING: Recipe generation not available. Missing recipe modules or required dependencies.")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', 
                          implementation=IMPLEMENTATION,
                          recipe_available=RECIPE_GENERATION_AVAILABLE,
                          gemini_configured=bool(os.environ.get('GEMINI_API_KEY')))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent collisions
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Run object detection
            detection_results = DETECTION_FN(filepath)
            
            # Get recipe type if specified
            recipe_type = request.form.get('recipe_type', None)
            
            # Generate recipe if available and requested
            recipe_data = None
            if RECIPE_GENERATION_AVAILABLE and request.form.get('generate_recipe') == 'true':
                recipe_data = generate_recipe(detection_results, recipe_type)
            
            # Return results as JSON
            return jsonify({
                'status': 'success',
                'filename': unique_filename,
                'image_url': url_for('uploaded_file', filename=unique_filename),
                'detections': detection_results,
                'count': len(detection_results),
                'recipe': recipe_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Detection error: {str(e)}"
            }), 500
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid file type. Allowed types: jpg, jpeg, png'
    }), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generate-recipe', methods=['POST'])
def generate_recipe_api():
    if not RECIPE_GENERATION_AVAILABLE:
        return jsonify({
            'status': 'error',
            'message': 'Recipe generation is not available'
        }), 501
    
    try:
        data = request.json
        detection_results = data.get('detections', [])
        recipe_type = data.get('recipe_type')
        
        recipe_data = generate_recipe(detection_results, recipe_type)
        
        return jsonify({
            'status': 'success',
            'recipe': recipe_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Error generating recipe: {str(e)}"
        }), 500

# Vercel serverless function entry point
from http.server import BaseHTTPRequestHandler

def handler(event, context):
    return app

if __name__ == '__main__':
    app.run(debug=True) 