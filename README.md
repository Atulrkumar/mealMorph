# Object Detection & Recipe Generator Web Application

A web application that allows users to upload images to detect objects and generate recipes based on detected food items. The application uses a pretrained Faster R-CNN model for object detection and Google's Gemini AI for recipe generation.

## Features

- Upload images via drag-and-drop or file selection
- Real-time object detection using pretrained models
- Visual display of detection results with bounding boxes
- Detailed JSON output of all detections
- Recipe generation based on detected food items
- Multiple recipe types (breakfast, lunch, dinner, etc.)
- Support for both PyTorch and MMDetection backends
- Responsive web interface

## Screenshot

![Object Detection & Recipe Generator Web App Screenshot](screenshot.png)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/object-detection-recipe-webapp.git
cd object-detection-recipe-webapp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a `.env` file in the project root (copy from `.env.example`)
   - Add your API key to the `.env` file: `GEMINI_API_KEY=your_key_here`

4. For MMDetection, download the pretrained model (optional - only if using MMDetection):
```bash
mkdir -p checkpoints
wget -P checkpoints https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth
```

## Running the Web App

Start the Flask development server:
```bash
python app.py
```

Then open your web browser and navigate to: http://127.0.0.1:5000/

## Deploying to Vercel

This application is fully configured for deployment on Vercel's serverless platform. Follow these steps to deploy:

1. Install the Vercel CLI:
```bash
npm install -g vercel
```

2. Login to your Vercel account:
```bash
vercel login
```

3. Deploy the application:
```bash
vercel
```

4. Configure environment variables in the Vercel dashboard:
   - Go to your project in the Vercel dashboard
   - Navigate to Settings > Environment Variables
   - Add `GEMINI_API_KEY` with your API key
   - Add `SECRET_KEY` with a secure random string

5. For production deployment, run:
```bash
vercel --prod
```

Note: The deployed version uses simplified object detection and recipe generation to work within Vercel's serverless environment limitations. Heavy ML models are not compatible with serverless functions, so the app falls back to a simplified implementation.

## Using the Web Interface

1. Click "Select Image" or drag and drop an image onto the upload area
2. Optionally select a recipe type (breakfast, dinner, etc.)
3. The application will process the image and display detection results
4. View the bounding boxes on the image preview
5. See detection details in the "Summary" tab
6. View the generated recipe in the "Recipe" tab (if food items were detected)
7. Access raw JSON data in the "JSON Data" tab

## Output Format

### Detection Results

The detection results are returned as an array of objects with the following format:

```json
[
  {
    "label": "apple",
    "score": 0.98,
    "box": [x1, y1, x2, y2] 
  },
  {
    "label": "banana",
    "score": 0.95,
    "box": [x1, y1, x2, y2]
  },
  ...
]
```

### Recipe Format

Recipes are generated in the following format:

```json
{
  "title": "Apple Banana Smoothie",
  "ingredients": [
    "2 ripe bananas",
    "1 apple, cored and chopped",
    "1 cup yogurt",
    "..."
  ],
  "instructions": [
    "Add all ingredients to a blender.",
    "Blend until smooth.",
    "..."
  ],
  "serving_suggestions": "Serve immediately in a tall glass...",
  "nutritional_notes": "This smoothie is rich in potassium..."
}
```

## How It Works

1. **Object Detection**: The application uses either PyTorch's implementation of Faster R-CNN or MMDetection to detect objects in the uploaded image.

2. **Food Item Identification**: It identifies food items from the detected objects based on a list of common food categories.

3. **Recipe Generation**: When food items are detected, it sends a request to Google's Gemini AI with the list of detected food items and requested recipe type to generate a recipe.

4. **Display**: The generated recipe is displayed in a user-friendly format alongside the detection results.

## Traditional Deployment

For traditional production deployment, consider:
- Using a production WSGI server like Gunicorn
- Setting up behind Nginx or similar web server
- Configuring proper security headers
- Implementing rate limiting for the upload endpoint

```bash
# Example production deployment with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## Customization

- The application uses either PyTorch or MMDetection for object detection
- Recipe generation is powered by Google's Gemini AI
- You can modify detection parameters in `app.py`
- You can customize the recipe generation prompt in `recipe_generator.py`
- Customize the UI by editing the templates and static files 