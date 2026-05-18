import os
import glob
import re
import urllib.parse

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
best_dir = os.path.join(site_dir, "Best")

if not os.path.exists(best_dir):
    print(f"Error: Best directory not found at {best_dir}")
    exit(1)

best_files = set(os.listdir(best_dir))

html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)

hero_images_found = set()

for html_file in html_files:
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue
        
    # Type 1: <img ... class="...hero-img...">
    imgs = re.findall(r'<img[^>]+>', content)
    for img in imgs:
        if 'hero-img' in img:
            src_match = re.search(r'src="([^"]+)"', img)
            if src_match:
                hero_images_found.add((html_file, src_match.group(1)))
                
    # Type 2: background: url('...') inline style on elements with 'hero' class
    # Catch any element that has 'hero' in its class and an inline background image
    all_elements = re.findall(r'<[a-zA-Z0-9\-]+[^>]+>', content)
    for el in all_elements:
        class_match = re.search(r'class="([^"]*)"', el)
        if class_match and 'hero' in class_match.group(1):
            bg_match = re.search(r'background(?:-image)?:\s*url\([\'"]?([^\'"\)]+)[\'"]?\)', el)
            if bg_match:
                hero_images_found.add((html_file, bg_match.group(1)))

missing_in_best = set()

for html_file, src in hero_images_found:
    if src.startswith('http') or src.startswith('data:'):
        continue
        
    filename = os.path.basename(urllib.parse.unquote(src))
    
    if filename not in best_files:
        missing_in_best.add(filename)

print(f"Total unique hero images referenced in HTML: {len(set([src for _, src in hero_images_found]))}")
print(f"Hero images NOT in Best folder ({len(missing_in_best)}):")
print("-" * 40)
for f in sorted(missing_in_best):
    print(f)
