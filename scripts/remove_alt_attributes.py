import re
import os
import glob

site_dir = "/Volumes/Samsung X5 SSD/Projektek/Site"
html_files = glob.glob(os.path.join(site_dir, '**/*.html'), recursive=True)

print(f"Scanning and cleaning {len(html_files)} HTML files (strict tag attribute parser)...")

modified_count = 0
total_removed = 0

def remove_alt_from_tag_content(tag_content):
    global total_removed
    result = []
    i = 0
    in_double_quotes = False
    in_single_quotes = False
    length = len(tag_content)
    local_removed = 0
    
    while i < length:
        char = tag_content[i]
        
        if char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
            result.append(char)
            i += 1
        elif char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
            result.append(char)
            i += 1
        elif not in_double_quotes and not in_single_quotes:
            # We are outside quotes!
            # Check if this is the start of the 'alt' attribute
            is_alt = False
            if i + 3 <= length and tag_content[i:i+3].lower() == 'alt':
                # Check boundary: next char must not be a word char
                next_is_boundary = (i + 3 == length) or (not tag_content[i+3].isalnum() and tag_content[i+3] != '_')
                prev_is_boundary = (i == 0) or (not tag_content[i-1].isalnum() and tag_content[i-1] != '_')
                if next_is_boundary and prev_is_boundary:
                    is_alt = True
            
            if is_alt:
                # Consume it and its value
                j = i + 3
                # skip whitespace before '='
                while j < length and tag_content[j].isspace():
                    j += 1
                
                if j < length and tag_content[j] == '=':
                    j += 1 # consume '='
                    # skip whitespace after '='
                    while j < length and tag_content[j].isspace():
                        j += 1
                    
                    if j < length:
                        if tag_content[j] == '"':
                            # consume until next double quote
                            j += 1
                            while j < length and tag_content[j] != '"':
                                j += 1
                            if j < length:
                                j += 1 # consume closing quote
                        elif tag_content[j] == "'":
                            # consume until next single quote
                            j += 1
                            while j < length and tag_content[j] != "'":
                                j += 1
                            if j < length:
                                j += 1 # consume closing quote
                        else:
                            # unquoted value, consume until whitespace or '>'
                            while j < length and not tag_content[j].isspace() and tag_content[j] != '>':
                                j += 1
                
                # Remove preceding whitespace from our result to avoid duplicate spaces
                while result and result[-1].isspace():
                    result.pop()
                
                # Advance i to j
                i = j
                local_removed += 1
            else:
                result.append(char)
                i += 1
        else:
            result.append(char)
            i += 1
            
    total_removed += local_removed
    return ''.join(result)

def process_tags(match):
    return remove_alt_from_tag_content(match.group(0))

for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        continue

    removed_before = total_removed
    
    # Process only HTML tags: <[^>]+>
    new_content = re.sub(r'<[^>]+>', process_tags, content)
    
    if total_removed > removed_before:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            num_removed = total_removed - removed_before
            print(f"Cleaned {num_removed} alt attribute(s) in: {os.path.relpath(filepath, site_dir)}")
            modified_count += 1
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

print(f"\nDone! Modified {modified_count} files, removing {total_removed} alt attribute(s) strictly inside tags in total.")
