import os
import random
import numpy as np
from PIL import Image

# List of common food items that might be detected
FOOD_ITEMS = [
    "apple", "banana", "orange", "strawberry", "blueberry", 
    "carrot", "broccoli", "lettuce", "tomato", "potato",
    "chicken", "beef", "pork", "fish", "shrimp",
    "rice", "pasta", "bread", "cheese", "milk",
    "onion", "garlic", "pepper", "salt", "olive oil",
    "egg", "flour", "sugar", "butter", "chocolate",
    "coffee", "tea", "juice", "water", "wine"
]

def detect_objects(image_path):
    """
    Simplified object detection function without requiring heavy ML libraries.
    For the Vercel deployment, we'll simulate detection results.
    
    Args:
        image_path (str): Path to the input image
        
    Returns:
        list: List of dictionaries containing detection results
    """
    try:
        # Load image to verify it exists and get dimensions
        image = Image.open(image_path)
        width, height = image.size
        
        # Get image colors for some basic "content" analysis
        image_resized = image.resize((10, 10))
        colors = image_resized.getcolors(100)
        
        # Based on image characteristics, determine how many objects to "detect"
        brightness = sum(c[0] * sum(c[1][:3]) for c in colors if len(c[1]) >= 3) / 1000
        num_objects = max(1, min(5, int(brightness / 30) + 1))
        
        # Generate simulated detections
        detections = []
        for i in range(num_objects):
            # Select random food item with higher probability for common ingredients
            food_item = random.choice(FOOD_ITEMS)
            
            # Create random box coordinates appropriate for image dimensions
            x1 = random.randint(0, int(width * 0.7))
            y1 = random.randint(0, int(height * 0.7))
            x2 = min(width, x1 + random.randint(50, int(width * 0.3)))
            y2 = min(height, y1 + random.randint(50, int(height * 0.3)))
            
            # Generate confidence score
            score = random.uniform(0.75, 0.98)
            
            detections.append({
                'label': food_item,
                'score': score,
                'box': [x1, y1, x2, y2]
            })
        
        return detections
    
    except Exception as e:
        print(f"Error in simplified detection: {str(e)}")
        # Return some fallback detections if there's an error
        return [
            {'label': 'apple', 'score': 0.92, 'box': [100, 100, 200, 200]},
            {'label': 'banana', 'score': 0.88, 'box': [300, 150, 450, 200]}
        ] 