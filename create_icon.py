"""
Create a professional icon for Eye Mouse Control application
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_eye_icon():
    """Create a professional eye icon for the application"""
    
    # Create a high-resolution icon (256x256)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle (dark blue)
    margin = 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(20, 50, 100, 255), outline=(255, 255, 255, 255), width=3)
    
    # Eye shape
    eye_margin = 40
    draw.ellipse([eye_margin, size//2-30, size-eye_margin, size//2+30], 
                fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Iris
    iris_size = 40
    iris_x = size // 2
    iris_y = size // 2
    draw.ellipse([iris_x-iris_size, iris_y-iris_size, iris_x+iris_size, iris_y+iris_size], 
                fill=(100, 150, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Pupil
    pupil_size = 15
    draw.ellipse([iris_x-pupil_size, iris_y-pupil_size, iris_x+pupil_size, iris_y+pupil_size], 
                fill=(0, 0, 0, 255))
    
    # Highlight
    highlight_size = 8
    draw.ellipse([iris_x+10-highlight_size, iris_y-10-highlight_size, 
                 iris_x+10+highlight_size, iris_y-10+highlight_size], 
                fill=(255, 255, 255, 255))
    
    # Save as ICO file with multiple sizes
    icon_sizes = [16, 32, 48, 64, 128, 256]
    icon_images = []
    
    for icon_size in icon_sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icon_images.append(resized)
    
    # Save as ICO
    icon_images[0].save('eye_mouse_control.ico', 
                       format='ICO', 
                       sizes=[(img.width, img.height) for img in icon_images],
                       append_images=icon_images[1:])
    
    print("✅ Professional icon created: eye_mouse_control.ico")
    return 'eye_mouse_control.ico'

if __name__ == "__main__":
    create_eye_icon()
