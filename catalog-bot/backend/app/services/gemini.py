import google.generativeai as genai
from app.core.config import settings
import json
import re

genai.configure(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = 'gemini-1.5-pro'

def analyze_product_image_and_text(image_path: str, caption: str) -> dict:
    """
    Passes the image and user text to Gemini API.
    Forces JSON output so we can reliably extract keywords.
    """
    prompt = f"""
    Analyze this product image and the following user text: "{caption}".
    Generate a JSON response containing ONLY the following keys:
    - "title": SEO Optimized Title (max 150 chars).
    - "bullet_points": Array of 5 bullet points.
    - "description": Detailed Description.
    - "search_terms": Array of 5-7 Backend Search Terms/Hashtags.
    - "visual_features": Dictionary of visual features (color, pattern, material).
    - "primary_keyword": A 2-4 word string representing the main product category (e.g. "black cotton shirt") to be used for price comparison scraping.
    
    Do NOT wrap in markdown formatting or backticks, just return raw JSON text.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        image_file = genai.upload_file(path=image_path)
        
        response = model.generate_content([prompt, image_file])
        
        # Parse JSON
        text_output = response.text
        # Optional: clean markdown if it accidentally added it
        text_output = re.sub(r'```json\n|\n```', '', text_output).strip()
        
        data = json.loads(text_output)
        return data
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {}
