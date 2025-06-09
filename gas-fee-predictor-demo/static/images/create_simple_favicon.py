from PIL import Image, ImageDraw
import os

def create_ethereum_favicon(output_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Create a simple Ethereum-like favicon."""
    # Create a list to store images of different sizes
    images = []
    
    # Create images of different sizes
    for size in sizes:
        # Create a new image with a transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calculate dimensions
        border = int(size * 0.1)
        inner_size = size - 2 * border
        
        # Draw a hexagon (Ethereum-like shape)
        # Calculate points for a hexagon
        center_x, center_y = size // 2, size // 2
        radius = inner_size // 2
        points = []
        for i in range(6):
            angle = i * 60
            x = center_x + radius * 0.866 * (1 if angle % 180 == 0 else -1)
            y = center_y + radius * 0.5 * (1 if angle < 180 else -1)
            points.append((x, y))
        
        # Draw the hexagon
        draw.polygon(points, fill=(52, 152, 219))  # Blue color
        
        # Add to list of images
        images.append(img)
    
    # Save as ICO
    images[0].save(output_path, format='ICO', sizes=[(size, size) for size in sizes], append_images=images[1:])
    print(f"Created favicon.ico at {output_path}")

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define output path
    ico_path = os.path.join(script_dir, 'favicon.ico')
    
    # Create favicon
    create_ethereum_favicon(ico_path)
