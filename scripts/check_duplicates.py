import re
from collections import Counter
import glob
import os

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)

all_images = []
duplicates_across_site = Counter()

for html_file in html_files:
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        continue

    # find all image src attributes
    matches = re.findall(r'<img[^>]+src="([^"]+)"', content)
    
    # Check for duplicates within this specific file
    counts = Counter(matches)
    duplicates_in_file = {src: count for src, count in counts.items() if count > 1}
    
    if duplicates_in_file:
        print(f"Duplicates in {os.path.relpath(html_file, site_dir)}:")
        for src, count in duplicates_in_file.items():
            print(f"  - {src} (used {count} times)")
            
    # Add to global counter
    duplicates_across_site.update(matches)

# Check global duplicates
global_dupes = {src: count for src, count in duplicates_across_site.items() if count > 1}
print(f"\nTotal images used across all HTML files: {len(duplicates_across_site)}")
print(f"Total unique images used more than once across the entire site: {len(global_dupes)}")
