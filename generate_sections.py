#!/usr/bin/env python3
"""Generate remaining HTML sections from markdown content."""

import re

MD_FILE = "content/Family/Raimondo-and-Selena.md"
HTML_FILE = "hu/raimondo-and-selena-detailed.html"
PLACEHOLDER_IMG = "../images/UniversalUpscaler_3bb39436-c2b1-4464-a324-b162d990ad35.jpg"

def gallery_block():
    return f"""            <div class="image-gallery ">
                <div class="gallery-item "><img src="{PLACEHOLDER_IMG}" class="gallery-image-cover" /></div>
                <div class="gallery-item "><img src="{PLACEHOLDER_IMG}" class="gallery-image-cover" /></div>
                <div class="gallery-item "><img src="{PLACEHOLDER_IMG}" class="gallery-image-cover" /></div>
            </div>"""

def section_block(title, paragraphs):
    """Build HTML for one section: h2 + paragraphs with gallery after first p."""
    lines = []
    lines.append(f'            <h2 class="section-title text-3xl font-bold mt-12 mb-6 narrative-section-title">{title}</h2>')
    for i, p in enumerate(paragraphs):
        extra_class = ' mt-4' if i > 0 else ''
        lines.append(f'            <p class="narrative-text{extra_class}">{p}</p>')
        # Add gallery after first paragraph only
        if i == 0:
            lines.append(gallery_block())
    return "\n".join(lines)

def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by ## headers
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    
    result = []
    for sec in sections[1:]:  # skip preamble
        lines = sec.strip().split('\n')
        title = lines[0].strip()
        # Collect non-empty, non-header lines as paragraphs
        paragraphs = []
        for line in lines[1:]:
            line = line.strip()
            if line and not line.startswith('#'):
                # Escape & for HTML
                line = line.replace('&', '&amp;')
                paragraphs.append(line)
        if paragraphs:
            result.append((title, paragraphs))
    return result

# Sections already in the HTML (by title)
existing = {
    "Seven Seas High School",
    "Raimondo és Bailey élete az óceánjárón",
    "Raimondo palotája",
    "Raimondo és Selena megismerkedése",
    "Miss Supranational szépségverseny",
    "Az InterMedic bejelenti az életelixírt",
    "Egyetemi tanulmányok",
    "Raimondo és Selena Egyiptomban",
    "2015-ben Raimondo szenátor lett",
    "Selena Gomez családja",
    "A 2015-ös EU csúcstalálkozó",
    "Nemzetközi találkozók",
    "További események",
    "Waikiki-i kormány év eleji értékelése",
    "Ünnepségek",
    "Raimondo és Bailey magánélete",
    "A szenátus első éves konferenciája",
    "Raimondo 20. születésnapja",
    "Utazás Angliába",
    "Mega épületek",
    "Raimondo és Selena személyes fejlődése",
    "Young Hollywood Awards 2016",
}

all_sections = parse_md(MD_FILE)

# Find sections not yet in HTML
new_sections = [(t, p) for t, p in all_sections if t not in existing]

print(f"Found {len(new_sections)} new sections to add:")
for t, p in new_sections:
    print(f"  - {t} ({len(p)} paragraphs)")

# Generate HTML
new_html_parts = []
for title, paragraphs in new_sections:
    new_html_parts.append(section_block(title, paragraphs))

new_html = "\n".join(new_html_parts)

# Read existing HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Insert before the closing </div> that ends narrative-content (line 235)
# Find the last image gallery div before </div></section><footer>
insert_marker = """            </div>
        </div>
    </section>
    <footer>"""

replacement = f"""            </div>
{new_html}
        </div>
    </section>
    <footer>"""

if insert_marker in html_content:
    html_content = html_content.replace(insert_marker, replacement, 1)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\nSuccessfully inserted {len(new_sections)} sections into {HTML_FILE}")
else:
    print("ERROR: Could not find insertion point in HTML!")
    # Debug: show what we're looking for
    print("Looking for marker...")
    # Try to find it differently
    lines = html_content.split('\n')
    for i, line in enumerate(lines):
        if '</section>' in line and i > 200:
            print(f"  Line {i+1}: {line[:80]}")
