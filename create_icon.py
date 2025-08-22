from PIL import Image, ImageDraw, ImageFont
import os

def create_webminer_icon():
    """Create a simple icon for WebMiner"""
    
    # Create a 256x256 image with a dark blue background
    size = 256
    img = Image.new('RGBA', (size, size), (44, 62, 80, 255))  # Dark blue background
    draw = ImageDraw.Draw(img)
    
    # Draw a web-like pattern (simplified)
    # Outer circle
    draw.ellipse([20, 20, size-20, size-20], outline=(52, 152, 219, 255), width=8)
    
    # Inner circle
    draw.ellipse([60, 60, size-60, size-60], outline=(52, 152, 219, 255), width=6)
    
    # Center circle
    draw.ellipse([100, 100, size-100, size-100], fill=(52, 152, 219, 255))
    
    # Draw some connecting lines to represent web scraping
    # Vertical lines
    draw.line([(size//2, 30), (size//2, 100)], fill=(46, 204, 113, 255), width=4)
    draw.line([(size//2, 156), (size//2, 226)], fill=(46, 204, 113, 255), width=4)
    
    # Horizontal lines
    draw.line([(30, size//2), (100, size//2)], fill=(46, 204, 113, 255), width=4)
    draw.line([(156, size//2), (226, size//2)], fill=(46, 204, 113, 255), width=4)
    
    # Diagonal lines
    draw.line([(60, 60), (100, 100)], fill=(46, 204, 113, 255), width=3)
    draw.line([(196, 196), (156, 156)], fill=(46, 204, 113, 255), width=3)
    draw.line([(196, 60), (156, 100)], fill=(46, 204, 113, 255), width=3)
    draw.line([(60, 196), (100, 156)], fill=(46, 204, 113, 255), width=3)
    
    # Add "WM" text in the center
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "WM" text
    text = "WM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw text with white color
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Save as ICO file
    img.save("icon.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("✅ Icon created: icon.ico")
    print("📁 Icon saved with multiple sizes for Windows compatibility")

if __name__ == "__main__":
    try:
        create_webminer_icon()
    except ImportError:
        print("❌ PIL (Pillow) not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"], check=True)
        print("✅ Pillow installed. Creating icon...")
        create_webminer_icon()
