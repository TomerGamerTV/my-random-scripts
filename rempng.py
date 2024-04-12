import os

def delete_png_files():
    for file in os.listdir('.'):
        if file.endswith('.png'):
            try:
                os.remove(file)
                print(f"Deleted {file}")
            except OSError as e:
                print(f"Error: {e.strerror} - {file}")

delete_png_files()
