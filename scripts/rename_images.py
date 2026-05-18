import re
import os
import glob
import urllib.parse

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)

print(f"Scanning {len(html_files)} HTML files for images...")

unique_images = []
for html_file in html_files:
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue
        
    matches = re.findall(r'<img[^>]+src="([^"]+)"', content)
    for src in matches:
        if src.startswith('http') or src.startswith('data:'):
            continue
            
        old_abs_path = os.path.abspath(os.path.join(os.path.dirname(html_file), urllib.parse.unquote(src)))
        
        if old_abs_path not in unique_images:
            unique_images.append(old_abs_path)

print(f"Found {len(unique_images)} unique images referenced in HTML files.")

image_renames = {}
assigned_paths = set()

# Pre-fill assigned_paths with existing names that already follow the image-X pattern
for old_abs_path in unique_images:
    old_filename = os.path.basename(old_abs_path)
    if re.match(r'^image-\d+', old_filename):
        image_renames[old_abs_path] = old_abs_path
        assigned_paths.add(old_abs_path)

counter = 1
for old_abs_path in unique_images:
    if old_abs_path in image_renames:
        continue
        
    old_dir = os.path.dirname(old_abs_path)
    _, ext = os.path.splitext(old_abs_path)
    if not ext:
        ext = '.jpg'
        
    while True:
        new_filename = f"image-{counter}{ext}"
        new_abs_path = os.path.join(old_dir, new_filename)
        if new_abs_path not in assigned_paths and not os.path.exists(new_abs_path):
            break
        counter += 1
        
    image_renames[old_abs_path] = new_abs_path
    assigned_paths.add(new_abs_path)

# Perform the actual file renaming
for old_abs_path, new_abs_path in image_renames.items():
    if old_abs_path != new_abs_path:
        if os.path.exists(old_abs_path):
            try:
                os.rename(old_abs_path, new_abs_path)
                print(f"Renamed: {os.path.basename(old_abs_path)} -> {os.path.basename(new_abs_path)}")
            except Exception as e:
                print(f"Error renaming {old_abs_path}: {e}")
        else:
            if os.path.exists(new_abs_path):
                print(f"Already renamed: {os.path.basename(old_abs_path)} -> {os.path.basename(new_abs_path)}")
            else:
                print(f"Warning: File not found on disk: {old_abs_path}")

# Update all HTML files with the new references
for html_file in html_files:
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue
        
    def replace_src(match):
        src = match.group(1)
        if src.startswith('http') or src.startswith('data:'):
            return match.group(0)
            
        old_abs_path = os.path.abspath(os.path.join(os.path.dirname(html_file), urllib.parse.unquote(src)))
        
        if old_abs_path in image_renames:
            new_abs_path = image_renames[old_abs_path]
            if old_abs_path != new_abs_path:
                new_filename = os.path.basename(new_abs_path)
                if '/' in src:
                    head, tail = src.rsplit('/', 1)
                    new_src = f"{head}/{new_filename}"
                else:
                    new_src = new_filename
                return match.group(0).replace(f'"{src}"', f'"{new_src}"')
                
        return match.group(0)

    new_content = re.sub(r'<img[^>]+src="([^"]+)"', replace_src, content)
    
    if new_content != content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated references in: {os.path.relpath(html_file, site_dir)}")

print("Done.")
