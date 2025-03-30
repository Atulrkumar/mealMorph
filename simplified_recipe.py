import os
import random
from typing import List, Dict, Any, Optional
import json

# Try to import Google Generative AI for Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load Gemini API key from environment
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Fallback recipes for common ingredients
FALLBACK_RECIPES = {
    "apple": {
        "title": "Simple Apple Dessert",
        "ingredients": [
            "2 apples, sliced",
            "2 tablespoons honey or maple syrup",
            "1/2 teaspoon cinnamon",
            "1/4 cup granola",
            "Greek yogurt (optional)"
        ],
        "instructions": [
            "Slice the apples into thin pieces.",
            "Mix with honey and cinnamon.",
            "Top with granola and yogurt if desired.",
            "Serve immediately or chill for a refreshing dessert."
        ],
        "serving_suggestions": "Serve in a decorative bowl with a mint leaf for garnish.",
        "nutritional_notes": "Apples are rich in fiber and antioxidants. This dessert provides natural sweetness with minimal added sugars."
    },
    "banana": {
        "title": "Banana Smoothie Bowl",
        "ingredients": [
            "2 ripe bananas, frozen",
            "1/2 cup milk of choice",
            "1 tablespoon nut butter",
            "1/2 teaspoon vanilla extract",
            "Toppings: sliced fruits, nuts, seeds, granola"
        ],
        "instructions": [
            "Blend frozen bananas, milk, nut butter, and vanilla until smooth.",
            "Pour into a bowl.",
            "Top with your favorite toppings.",
            "Enjoy immediately."
        ],
        "serving_suggestions": "Best enjoyed fresh. Add a drizzle of honey or maple syrup for extra sweetness.",
        "nutritional_notes": "Bananas provide potassium and natural energy. This bowl makes a nutritious breakfast or post-workout snack."
    }
}

def setup_gemini():
    """Initialize the Gemini API with the provided key."""
    if not GEMINI_API_KEY or not GEMINI_AVAILABLE:
        return False
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    except:
        return False

def generate_recipe(detection_results: List[Dict[str, Any]], recipe_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a recipe based on the detected objects in an image.
    Will use Gemini API if available, otherwise falls back to pre-defined recipes.
    
    Args:
        detection_results: List of dictionaries containing detection results.
        recipe_type: Optional type of recipe to generate.
                    
    Returns:
        Dict containing the generated recipe with title, ingredients, instructions, and notes.
    """
    try:
        # Extract food items from detection results
        food_items = [item['label'] for item in detection_results 
                      if item['label'] in FALLBACK_RECIPES or 'food' in item['label'].lower()]
        
        # If no food items found
        if not food_items:
            return {
                "success": True,
                "recipe": None,
                "message": "No food items detected in the image. Try an image with visible food items."
            }
        
        # Try to use Gemini API if available
        gemini_setup = GEMINI_AVAILABLE and GEMINI_API_KEY and setup_gemini()
        
        if gemini_setup:
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
            
            try:
                # First try with gemini-1.0-pro or gemini-pro
                model_name = "gemini-pro" # Adjust model name based on Gemini API version
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                # Parse the response
                if hasattr(response, 'text'):
                    response_text = response.text
                    
                    # Extract JSON from the response
                    if "```json" in response_text and "```" in response_text:
                        json_str = response_text.split("```json")[1].split("```")[0].strip()
                    elif "{" in response_text and "}" in response_text:
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        json_str = response_text[start:end]
                    else:
                        json_str = response_text
                    
                    try:
                        recipe_data = json.loads(json_str)
                        return {
                            "success": True,
                            "recipe": recipe_data,
                            "detected_items": food_items
                        }
                    except json.JSONDecodeError:
                        # Fall back to our simplified approach
                        pass
            except Exception as e:
                print(f"Gemini API error: {str(e)}")
                # Continue to fallback method
        
        # Fallback recipe generation logic
        main_ingredient = food_items[0]  # Use the first detected food item
        
        if main_ingredient in FALLBACK_RECIPES:
            recipe = FALLBACK_RECIPES[main_ingredient]
        else:
            # Generic recipe if no specific one is available
            recipe = {
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
            }
            
            # Modify recipe based on recipe type if specified
            if recipe_type:
                recipe["title"] = f"{recipe_type.capitalize()} {' & '.join(food_items)} Recipe"
                
                if recipe_type == "breakfast":
                    recipe["instructions"].insert(1, "Heat a pan and cook your mixture until golden brown.")
                elif recipe_type == "dessert":
                    recipe["ingredients"].append("2 tablespoons of honey or sugar")
                    recipe["instructions"].insert(1, "Add sweetener to taste.")
                elif recipe_type == "dinner":
                    recipe["ingredients"].append("Your choice of protein (chicken, fish, tofu)")
                    recipe["instructions"].insert(1, "Cook your protein until done and combine with other ingredients.")
        
        return {
            "success": True,
            "recipe": recipe,
            "detected_items": food_items,
            "note": "This is a simplified recipe generated for the online demo."
        }
            
    except Exception as e:
        print(f"Recipe generation error: {str(e)}")
        return {
            "success": False,
            "error": f"Error generating recipe: {str(e)}",
            "detected_items": [] 
        } 