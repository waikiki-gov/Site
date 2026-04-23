import re
import os
import glob
import urllib.parse

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
images_dir = os.path.join(site_dir, "images")

# Collect all image filenames referenced in any HTML file
referenced_filenames = set()

html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)
print(f"Scanning {len(html_files)} HTML files...")

for html_file in html_files:
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue

    # img src attributes
    srcs = re.findall(r'<img[^>]+src="([^"]+)"', content)
    # link href attributes (e.g. preload)
    srcs += re.findall(r'<link[^>]+href="([^"]+)"', content)
    # inline CSS url() references (e.g. background: url('...'))
    srcs += re.findall(r"url\(['\"]?([^'\")\s]+)['\"]?\)", content)

    for src in srcs:
        # Only care about local images in the images/ folder
        if 'images/' in src and not src.startswith('http'):
            filename = os.path.basename(urllib.parse.unquote(src))
            referenced_filenames.add(filename)

print(f"Found {len(referenced_filenames)} unique images referenced in HTML files.")

# Find all files in /images directory
all_images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f)) and not f.startswith('.')]
print(f"Found {len(all_images)} total files in /images folder.")

# Find unreferenced images
unreferenced = [f for f in all_images if f not in referenced_filenames]
print(f"\n{len(unreferenced)} unreferenced images to delete:")

for filename in sorted(unreferenced):
    print(f"  - {filename}")

if unreferenced:
    confirm = input(f"\nDelete {len(unreferenced)} files? (yes/no): ").strip().lower()
    if confirm == 'yes':
        for filename in unreferenced:
            path = os.path.join(images_dir, filename)
            os.remove(path)
            print(f"Deleted: {filename}")
        print("Done.")
    else:
        print("Aborted. No files were deleted.")
else:
    print("Nothing to delete.")
