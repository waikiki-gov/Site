import os
import re

def get_css_selectors(css_content):
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Remove @keyframes blocks
    css_content = re.sub(r'@keyframes.*?\{.*?\}\s*\}', '', css_content, flags=re.DOTALL)
    # Simple @keyframes removal (might need improvement for nested braces)
    
    classes = set()
    ids = set()
    
    # Find all blocks of selectors
    # This matches everything before a {
    selector_blocks = re.findall(r'([^{}]+)\{', css_content)
    
    for block in selector_blocks:
        # Ignore @ rules like @media, @import
        if '@' in block:
            continue
            
        # Split by comma for multiple selectors
        selectors = block.split(',')
        for selector in selectors:
            # Find classes: .className
            # We want to avoid matching things like .5rem
            # Class names must start with a letter or underscore, or a hyphen followed by a letter/underscore
            found_classes = re.findall(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', selector)
            classes.update(found_classes)
            
            # Find IDs: #idName
            found_ids = re.findall(r'#([a-zA-Z_][a-zA-Z0-9_-]*)', selector)
            ids.update(found_ids)
            
    return classes, ids

def search_in_files(selectors, root_dir):
    used_selectors = set()
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.html', '.js')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for selector in selectors:
                            # For classes, we look for "selector" in class="..." or classList.add("selector")
                            # For IDs, we look for id="selector" or getElementById("selector")
                            # But since it's a simple search, just checking if the string exists is usually enough for a first pass
                            # unless the class name is very short like "a" or "s".
                            if selector in content:
                                used_selectors.add(selector)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    return used_selectors

def main():
    root_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
    css_dir = os.path.join(root_dir, "css")
    
    all_unused = {}

    for file in os.listdir(css_dir):
        if file.endswith('.css'):
            css_path = os.path.join(css_dir, file)
            with open(css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classes, ids = get_css_selectors(content)
            all_selectors = classes.union(ids)
            
            # Filter out common false positives
            all_selectors = {s for s in all_selectors if len(s) > 1} # Ignore single letter classes if any
            
            used = search_in_files(all_selectors, root_dir)
            unused = all_selectors - used
            
            if unused:
                all_unused[file] = sorted(list(unused))

    for file, unused in all_unused.items():
        print(f"--- Unused selectors in {file} ---")
        for s in unused:
            print(s)
        print()

if __name__ == "__main__":
    main()
