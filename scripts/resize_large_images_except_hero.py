import os
import subprocess
import sys
import re

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
TARGET_WIDTH = 2560
TARGET_HEIGHT = 1440

# Supported image extensions (case-insensitive)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg')

def get_excluded_images(site_dir):
    """Finds all images used in elements with a class containing 'hero' or 'portrait' in HTML files."""
    excluded_image_paths = set()
    
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
                                excluded_image_paths.add((img_url, html_path))
                                
                            # Extract src="..." if present (used in <img> tags)
                            src_match = re.search(r'src=[\'"]([^\'"]+)[\'"]', attrs)
                            if src_match:
                                img_url = src_match.group(1)
                                excluded_image_paths.add((img_url, html_path))

                    # Also find images within 'portrait' class divs
                    portrait_pattern = re.compile(r'<div[^>]*class="[^"]*portrait[^"]*"[^>]*>\s*<img[^>]*src=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
                    for match in portrait_pattern.finditer(content):
                        excluded_image_paths.add((match.group(1), html_path))

                except Exception as e:
                    print(f"Error reading {html_path}: {e}", file=sys.stderr)

    resolved_paths = set()
    for img_url, html_path in excluded_image_paths:
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
    """Resizes and crops the image to exactly {TARGET_WIDTH}x{TARGET_HEIGHT}."""
    try:
        subprocess.run(
            ['mogrify', '-resize', f'{TARGET_WIDTH}x{TARGET_HEIGHT}^', '-gravity', 'center', '-extent', f'{TARGET_WIDTH}x{TARGET_HEIGHT}', file_path],
            check=True
        )
        return True
    except Exception as e:
        print(f"Error resizing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    print(f"Scanning for images in: {site_dir}")
    
    excluded_images = get_excluded_images(site_dir)
    print(f"Found {len(excluded_images)} excluded images (hero/portrait).")
    
    image_paths = []
    for root, dirs, files in os.walk(site_dir):
        # Skip hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.startswith('UniversalUpscaler'):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                abs_path = os.path.join(root, file)
                if abs_path not in excluded_images:
                    image_paths.append(abs_path)

    print(f"Found {len(image_paths)} images to process (excluding hero/portrait images).")
    
    images_to_resize_count = 0
    resized_count = 0
    
    for path in image_paths:
        rel_path = os.path.relpath(path, site_dir)
        width, height = get_image_dimensions(path)
        
        if width is None or height is None:
            continue
            
        if width != TARGET_WIDTH or height != TARGET_HEIGHT:
            images_to_resize_count += 1
            print(f"Image needs resizing/cropping: {rel_path} ({width}x{height}px)")
            
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
    print(f"Total hero/portrait images excluded: {len(excluded_images)}")
    print(f"Total images scanned: {len(image_paths)}")
    print(f"Images needing resize/crop: {images_to_resize_count}")
    print(f"Successfully resized images: {resized_count}")

if __name__ == '__main__':
    main()
