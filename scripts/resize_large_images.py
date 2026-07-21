import os
import subprocess
import sys

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
MAX_SIZE = 5520  # Maximum allowed width or height in pixels
TARGET_SIZE = 5120  # Target size for resizing

# Supported image extensions (case-insensitive)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.tiff', '.bmp')

def get_image_dimensions(file_path):
    """Returns (width, height) of an image using 'identify' command, or (None, None) on error."""
    try:
        result = subprocess.run(
            ['identify', '-format', '%w %h', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        parts = output.split()
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except Exception as e:
        print(f"Error identifying {file_path}: {e}", file=sys.stderr)
    return None, None

def resize_image(file_path):
    """Resizes the image using 'mogrify -resize {TARGET_SIZE}x{TARGET_SIZE}>'."""
    try:
        subprocess.run(
            ['mogrify', '-resize', f'{TARGET_SIZE}x{TARGET_SIZE}>', file_path],
            check=True
        )
        return True
    except Exception as e:
        print(f"Error resizing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    print(f"Scanning for images in: {site_dir}")
    
    image_paths = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                image_paths.append(os.path.join(root, file))

    print(f"Found {len(image_paths)} images total.")
    
    large_images_count = 0
    resized_count = 0
    
    for path in image_paths:
        rel_path = os.path.relpath(path, site_dir)
        width, height = get_image_dimensions(path)
        
        if width is None or height is None:
            continue
            
        if width > MAX_SIZE or height > MAX_SIZE:
            large_images_count += 1
            print(f"Large image found: {rel_path} ({width}x{height}px)")
            
            # Perform resize
            if resize_image(path):
                new_width, new_height = get_image_dimensions(path)
                if new_width and new_height:
                    print(f"  -> Resized to {new_width}x{new_height}px")
                else:
                    print("  -> Resized successfully")
                resized_count += 1
            else:
                print("  -> Failed to resize")

    print("\nSummary:")
    print(f"Total images scanned: {len(image_paths)}")
    print(f"Images larger than {MAX_SIZE}: {large_images_count}")
    print(f"Successfully resized images: {resized_count}")

if __name__ == '__main__':
    main()
