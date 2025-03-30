import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set up the Gemini API (users need to provide their own API key in .env or as environment variable)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBwPXL7FdEG7o9I1vMXtfUMtgobA-lRgGU')

def setup_gemini():
    """Initialize the Gemini API with the provided key."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "No Gemini API key found. Please set the GEMINI_API_KEY environment variable "
            "or create a .env file with your API key."
        )
    genai.configure(api_key=GEMINI_API_KEY)

def generate_recipe(detection_results: List[Dict[str, Any]], 
                    recipe_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a recipe based on the detected objects in an image.
    
    Args:
        detection_results: List of dictionaries containing detection results.
        recipe_type: Optional type of recipe to generate (e.g., 'breakfast', 'dinner', 'healthy').
                    
    Returns:
        Dict containing the generated recipe with title, ingredients, instructions, and notes.
    """
    try:
        if not GEMINI_API_KEY:
            return {
                "success": False,
                "error": "No Gemini API key provided. Please set the GEMINI_API_KEY environment variable.",
                "recipe": None
            }
            
        # Setup Gemini
        setup_gemini()
        
        # Extract food items from detection results
        food_items = []
        for item in detection_results:
            # Common food categories in COCO dataset
            food_categories = [
                'apple', 'orange', 'banana', 'carrot', 'broccoli', 'hot dog', 'pizza', 
                'donut', 'cake', 'sandwich', 'bowl', 'cup', 'fork', 'knife', 'spoon', 
                'dining table', 'refrigerator', 'oven', 'microwave', 'toaster', 'bottle',
                'wine glass', 'food', 'fruit', 'vegetable'
            ]
            
            if item['label'].lower() in food_categories or 'food' in item['label'].lower():
                food_items.append(item['label'])
        
        # If no food items are found, provide a message
        if not food_items:
            return {
                "success": True,
                "recipe": None,
                "message": "No food items detected in the image. Try an image with visible food items."
            }
        
        # Create the prompt for Gemini
        recipe_type_text = f" for a {recipe_type} dish" if recipe_type else ""
        prompt = f"""
        I have detected the following food items in an image: {', '.join(food_items)}.
        Please generate a creative recipe{recipe_type_text} using these ingredients.
        
        The recipe should include:
        1. A creative title
        2. List of ingredients (including the detected items and suggesting complementary ingredients)
        3. Step-by-step cooking instructions
        4. Serving suggestions
        5. Nutritional notes (optional)
        
        Format the response as JSON with the following structure:
        {{
            "title": "Recipe Title",
            "ingredients": ["Ingredient 1", "Ingredient 2", ...],
            "instructions": ["Step 1...", "Step 2...", ...],
            "serving_suggestions": "Suggestion text",
            "nutritional_notes": "Notes text"
        }}
        """
        
        # Try to generate content with Gemini
        try:
            # First try with gemini-1.0-pro
            model = genai.GenerativeModel('gemini-1.0-pro')
            response = model.generate_content(prompt)
        except Exception as model_error:
            try:
                # If that fails, try with gemini-pro
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
            except Exception as e:
                # If both fail, create a mock recipe for demonstration purposes
                return {
                    "success": True,
                    "recipe": {
                        "title": f"{'Breakfast' if recipe_type == 'breakfast' else 'Delicious'} {' & '.join(food_items)} Recipe",
                        "ingredients": [f"{item}" for item in food_items] + ["Salt and pepper to taste", "Olive oil", "Fresh herbs (optional)"],
                        "instructions": [
                            f"Prepare the {', '.join(food_items)} by washing and cutting them as needed.",
                            "Combine all ingredients in a bowl.",
                            "Season with salt, pepper, and your favorite herbs.",
                            "Enjoy your delicious creation!"
                        ],
                        "serving_suggestions": f"Serve your {' & '.join(food_items)} creation with a side of your choice.",
                        "nutritional_notes": "This recipe contains nutrients from the detected food items."
                    },
                    "detected_items": food_items,
                    "note": "This is a fallback recipe as Gemini API generation failed. Error: " + str(e)
                }
        
        # Parse the response
        if hasattr(response, 'text'):
            # Extract JSON from the response
            response_text = response.text
            
            # Simple parsing to extract JSON - in a real app, you'd want more robust parsing
            if "```json" in response_text and "```" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
            else:
                json_str = response_text
                
            import json
            try:
                recipe_data = json.loads(json_str)
                return {
                    "success": True,
                    "recipe": recipe_data,
                    "detected_items": food_items
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, create a simple fallback recipe
                return {
                    "success": True,
                    "recipe": {
                        "title": f"{'Breakfast' if recipe_type == 'breakfast' else 'Delicious'} {' & '.join(food_items)} Recipe",
                        "ingredients": [f"{item}" for item in food_items] + ["Salt and pepper to taste", "Olive oil", "Fresh herbs (optional)"],
                        "instructions": [
                            f"Prepare the {', '.join(food_items)} by washing and cutting them as needed.",
                            "Combine all ingredients in a bowl.",
                            "Season with salt, pepper, and your favorite herbs.",
                            "Enjoy your delicious creation!"
                        ],
                        "serving_suggestions": f"Serve your {' & '.join(food_items)} creation with a side of your choice.",
                        "nutritional_notes": "This recipe contains nutrients from the detected food items."
                    },
                    "detected_items": food_items,
                    "note": "This is a fallback recipe as JSON parsing failed."
                }
        else:
            # If response doesn't have text, create a fallback recipe
            return {
                "success": True,
                "recipe": {
                    "title": f"{'Breakfast' if recipe_type == 'breakfast' else 'Delicious'} {' & '.join(food_items)} Recipe",
                    "ingredients": [f"{item}" for item in food_items] + ["Salt and pepper to taste", "Olive oil", "Fresh herbs (optional)"],
                    "instructions": [
                        f"Prepare the {', '.join(food_items)} by washing and cutting them as needed.",
                        "Combine all ingredients in a bowl.",
                        "Season with salt, pepper, and your favorite herbs.",
                        "Enjoy your delicious creation!"
                    ],
                    "serving_suggestions": f"Serve your {' & '.join(food_items)} creation with a side of your choice.",
                    "nutritional_notes": "This recipe contains nutrients from the detected food items."
                },
                "detected_items": food_items,
                "note": "This is a fallback recipe as Gemini API response didn't contain text."
            }
            
    except Exception as e:
        # Create a simple fallback recipe when there's an error
        if 'food_items' in locals() and food_items:
            return {
                "success": True,
                "recipe": {
                    "title": f"{'Breakfast' if recipe_type == 'breakfast' else 'Delicious'} {' & '.join(food_items)} Recipe",
                    "ingredients": [f"{item}" for item in food_items] + ["Salt and pepper to taste", "Olive oil", "Fresh herbs (optional)"],
                    "instructions": [
                        f"Prepare the {', '.join(food_items)} by washing and cutting them as needed.",
                        "Combine all ingredients in a bowl.",
                        "Season with salt, pepper, and your favorite herbs.",
                        "Enjoy your delicious creation!"
                    ],
                    "serving_suggestions": f"Serve your {' & '.join(food_items)} creation with a side of your choice.",
                    "nutritional_notes": "This recipe contains nutrients from the detected food items."
                },
                "detected_items": food_items,
                "note": f"This is a fallback recipe. Error: {str(e)}"
            }
        else:
            return {
                "success": False,
                "error": f"Error generating recipe: {str(e)}",
                "detected_items": food_items if 'food_items' in locals() else []
            }

if __name__ == "__main__":
    # Example usage
    sample_detections = [
        {"label": "apple", "score": 0.95, "box": [10, 10, 100, 100]},
        {"label": "banana", "score": 0.92, "box": [150, 50, 250, 150]},
        {"label": "person", "score": 0.98, "box": [300, 100, 500, 400]}
    ]
    
    result = generate_recipe(sample_detections, "healthy breakfast")
    print(result) 