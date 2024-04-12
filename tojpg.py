import os
from PIL import Image

def convert_png_to_jpg():
    for file in os.listdir('.'):
        if file.endswith('.png'):
            try:
                img = Image.open(file)
                rgb_img = img.convert('RGB')
                rgb_img.save(file.replace('png', 'jpg'), quality=95)
                print(f"Converted {file} to JPG.")
            except OSError:
                print(f"Couldn't convert {file}. It might be corrupted or not a valid image file.")

convert_png_to_jpg()
