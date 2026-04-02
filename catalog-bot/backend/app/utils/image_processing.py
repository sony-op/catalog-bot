import os
from rembg import remove
from PIL import Image

def process_product_image(input_path: str) -> str:
    """
    Takes an input image path, removes the background, applies a white solid background,
    resizes to 1000x1000 pixels, and returns the output path.
    """
    try:
        # Load the input image
        input_image = Image.open(input_path)
        
        # Remove background (returns an RGBA image)
        output_rgba = remove(input_image)
        
        # Create a solid white background 1000x1000
        background = Image.new("RGBA", (1000, 1000), (255, 255, 255, 255))
        
        # Calculate aspect ratio of the extracted product to fit inside 1000x1000 with a little margin
        target_size = 900
        output_rgba.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Paste the product onto the center of the white background
        x = (1000 - output_rgba.width) // 2
        y = (1000 - output_rgba.height) // 2
        background.paste(output_rgba, (x, y), output_rgba)
        
        # Convert back to RGB and save
        final_image = background.convert("RGB")
        
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_processed.jpg"
        
        final_image.save(output_path, "JPEG", quality=90)
        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        # In case of error, just return the original input path safely
        return input_path
