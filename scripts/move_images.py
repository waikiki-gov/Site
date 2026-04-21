import re
import os
import shutil
import urllib.parse

html_file = "/Volumes/Samsung X5 SSD/Projektek/Site/hu/raimondo-and-selena-detailed.html"
img_dir = "/Volumes/Samsung X5 SSD/Projektek/Site/img"
images_dir = "/Volumes/Samsung X5 SSD/Projektek/Site/images"

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# find all img/ files
matches = re.findall(r'src="\.\./img/([^"]+)"', content)

# move them
for filename in set(matches):
    decoded_filename = urllib.parse.unquote(filename)
    src_path = os.path.join(img_dir, decoded_filename)
    dst_path = os.path.join(images_dir, decoded_filename)
    if os.path.exists(src_path):
        print(f"Moving {decoded_filename}...")
        shutil.move(src_path, dst_path)
    elif os.path.exists(dst_path):
        print(f"File {decoded_filename} already in images_dir")
    else:
        print(f"Warning: {decoded_filename} not found in {img_dir}")

# update html
new_content = content.replace('src="../img/', 'src="../images/')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done.")
