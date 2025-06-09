import os
import cairosvg
from PIL import Image
import io

def svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert SVG to ICO with multiple sizes."""
    # Read the SVG file
    with open(svg_path, 'rb') as svg_file:
        svg_data = svg_file.read()
    
    # Create a list to store images of different sizes
    images = []
    
    # Convert SVG to PNG at different sizes
    for size in sizes:
        png_data = cairosvg.svg2png(bytestring=svg_data, output_width=size, output_height=size)
        img = Image.open(io.BytesIO(png_data))
        images.append(img)
    
    # Save as ICO
    images[0].save(ico_path, format='ICO', sizes=[(size, size) for size in sizes], append_images=images[1:])
    print(f"Created favicon.ico at {ico_path}")

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    svg_path = os.path.join(script_dir, 'favicon.svg')
    ico_path = os.path.join(script_dir, 'favicon.ico')
    
    # Convert SVG to ICO
    svg_to_ico(svg_path, ico_path)
