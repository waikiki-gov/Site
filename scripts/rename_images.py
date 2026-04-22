import re
import os
import glob
import urllib.parse

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
html_file = os.path.join(site_dir, "hu/raimondo-and-selena-detailed.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all image sources
matches = re.findall(r'<img[^>]+src="([^"]+)"', content)

# Preserve order and keep unique
unique_srcs = []
for src in matches:
    if src not in unique_srcs:
        unique_srcs.append(src)

renames = {}
counter = 1

print(f"Found {len(unique_srcs)} unique images in the webpage.")

for old_src in unique_srcs:
    # Skip absolute URLs (like http...)
    if old_src.startswith('http'):
        continue
        
    old_filename = os.path.basename(urllib.parse.unquote(old_src))
    old_dir = os.path.dirname(old_src) # e.g. "../images"
    
    # Get extension
    _, ext = os.path.splitext(old_filename)
    if not ext:
        ext = '.jpg'
        
    new_filename = f"image-{counter}{ext}"
    new_src = f"{old_dir}/{new_filename}"
    
    old_file_path = os.path.abspath(os.path.join(os.path.dirname(html_file), urllib.parse.unquote(old_src)))
    new_file_path = os.path.abspath(os.path.join(os.path.dirname(html_file), old_dir, new_filename))
    
    if os.path.exists(old_file_path):
        # Only rename if paths are different (avoids issues if already named image-X)
        if old_file_path != new_file_path:
            # Handle case where new_file_path might already exist from a previous run or other page
            # We will overwrite if necessary or maybe it's the exact same? 
            # We'll just rename
            try:
                os.rename(old_file_path, new_file_path)
                renames[old_src] = new_src
                print(f"Renamed: {old_filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {old_filename}: {e}")
    else:
        # maybe it was already renamed?
        if os.path.exists(new_file_path):
            renames[old_src] = new_src
            print(f"Already renamed: {old_filename} -> {new_filename}")
        else:
            print(f"Warning: File not found on disk: {old_file_path}")
            
    counter += 1

# Update all HTML files with the new paths to avoid breaking other pages
html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)

for h_file in html_files:
    try:
        with open(h_file, 'r', encoding='utf-8') as f:
            h_content = f.read()
    except Exception:
        continue
        
    new_h_content = h_content
    for old_src, new_src in renames.items():
        # Replace the exact src string in the HTML
        new_h_content = new_h_content.replace(f'src="{old_src}"', f'src="{new_src}"')
        
    if new_h_content != h_content:
        with open(h_file, 'w', encoding='utf-8') as f:
            f.write(new_h_content)
        print(f"Updated references in: {os.path.relpath(h_file, site_dir)}")

print("Done.")
