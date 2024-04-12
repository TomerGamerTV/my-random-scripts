import base64
import os
from io import BytesIO
from PIL import Image
from tkinter import filedialog
import pyqrcode  # Using pyqrcode for QR code generation


def generate_qr_codes(images):
    for image_path in images:
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGBA')  # Convert to RGBA for compatibility
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(img.tobytes()).decode()
                filename = os.path.splitext(os.path.basename(image_path))[0]  # Define filename here
                qr = pyqrcode.create(img_str)
                qr.png(os.path.join(os.path.dirname(image_path),
                f"{filename}_QR.png"), scale=8)
                print(f"QR code generated for {filename}")

        except Exception as e:
            print(f"Error converting {image_path}: {e}")


def main():
    images = filedialog.askopenfilenames()

    if not images:
        print("No images selected")
        return

    generate_qr_codes(images)


if __name__ == "__main__":
    main()
