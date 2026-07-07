import os
import subprocess
import sys
import re

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
MAX_SIZE = 1500  # Maximum allowed width or height in pixels
TARGET_SIZE = 1280  # Target size for resizing

# Supported image extensions (case-insensitive)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.tiff', '.bmp')

def get_hero_images(site_dir):
    """Finds all images used in elements with a class containing 'hero' in HTML files."""
    hero_image_paths = set()
    
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Find all HTML tags to check their attributes
                    tag_pattern = re.compile(r'<([a-zA-Z0-9\-]+)([^>]*)>')
                    for match in tag_pattern.finditer(content):
                        attrs = match.group(2)
                        # Check if 'hero' is present in the attributes (e.g., class="hero")
                        if 'hero' in attrs.lower():
                            # Extract url(...) if present (used in inline styles for backgrounds)
                            url_match = re.search(r'url\([\'"]?([^\'"\)]+)[\'"]?\)', attrs)
                            if url_match:
                                img_url = url_match.group(1)
                                hero_image_paths.add((img_url, html_path))
                                
                            # Extract src="..." if present (used in <img> tags)
                            src_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', attrs)
                            if src_match:
                                img_url = src_match.group(1)
                                hero_image_paths.add((img_url, html_path))
                except Exception as e:
                    print(f"Error reading {html_path}: {e}", file=sys.stderr)

    resolved_paths = set()
    for img_url, html_path in hero_image_paths:
        # Ignore data URIs or absolute external URLs
        if img_url.startswith('data:') or img_url.startswith(('http://', 'https://')):
            continue
            
        if img_url.startswith('/'):
            # Absolute path relative to site root
            abs_path = os.path.join(site_dir, img_url.lstrip('/'))
        else:
            # Relative path from the HTML file's directory
            html_dir = os.path.dirname(html_path)
            abs_path = os.path.normpath(os.path.join(html_dir, img_url))
            
        resolved_paths.add(abs_path)
        
    return resolved_paths

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
    
    hero_images = get_hero_images(site_dir)
    print(f"Found {len(hero_images)} hero images to exclude.")
    
    image_paths = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                abs_path = os.path.join(root, file)
                if abs_path not in hero_images:
                    image_paths.append(abs_path)

    print(f"Found {len(image_paths)} images to process (excluding hero images).")
    
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
    print(f"Total hero images excluded: {len(hero_images)}")
    print(f"Total images scanned: {len(image_paths)}")
    print(f"Images larger than {MAX_SIZE}: {large_images_count}")
    print(f"Successfully resized images: {resized_count}")

if __name__ == '__main__':
    main()
