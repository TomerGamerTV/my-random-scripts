from PIL import Image
import os

# Define target resolution
TARGET_WIDTH = 400
TARGET_HEIGHT = 100

# Get current directory
current_dir = os.getcwd()

# Supported image extensions
image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

# Process each image in the directory
for filename in os.listdir(current_dir):
    if filename.lower().endswith(image_extensions):
        # Open image
        with Image.open(filename) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to exactly 400x100, stretching to fit
            img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            
            # Create new filename
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_min{ext}"
            
            # Save resized image
            img.save(new_filename, quality=95)
