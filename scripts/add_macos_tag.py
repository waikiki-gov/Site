#!/usr/bin/env python3
"""
add_macos_tag.py
Adds macOS Finder tags exclusively to all .jpg / .jpeg files in a specified folder
and its subfolders recursively.

Usage Examples:
  # Basic usage with command line arguments (tags only .jpg/.jpeg files)
  python3 scripts/add_macos_tag.py "/path/to/folder" -t "Review" -c blue

  # Add multiple tags to .jpg files
  python3 scripts/add_macos_tag.py "/path/to/images" -t "Hold-program" -t "2026" -c purple

  # Dry-run preview
  python3 scripts/add_macos_tag.py "./images" -t "Archived" -c red --dry-run

  # Interactive mode (prompts for inputs if no arguments given)
  python3 scripts/add_macos_tag.py
"""

import argparse
import os
import plistlib
import re
import subprocess
import sys
from pathlib import Path

# macOS Finder tag color map
COLOR_MAP = {
    "none": 0,
    "gray": 1,
    "grey": 1,
    "green": 2,
    "purple": 3,
    "blue": 4,
    "yellow": 5,
    "red": 6,
    "orange": 7,
}

COLOR_NAMES = {
    0: "None",
    1: "Gray",
    2: "Green",
    3: "Purple",
    4: "Blue",
    5: "Yellow",
    6: "Red",
    7: "Orange",
}


def clean_path_string(raw_path: str) -> str:
    """Clean and normalize a directory or file path from user input or drag-and-drop."""
    if not raw_path:
        return ""
    p = raw_path.strip()

    # Strip surrounding single or double quotes repeatedly
    while len(p) >= 2 and ((p[0] == "'" and p[-1] == "'") or (p[0] == '"' and p[-1] == '"')):
        p = p[1:-1].strip()

    # Expand user tilde (~) at beginning
    p = os.path.expanduser(p)

    # Handle backslash escapes (e.g. terminal drag-and-drop: "Mobile\ Documents" -> "Mobile Documents")
    if not os.path.exists(p) and "\\" in p:
        unescaped = re.sub(r"\\([ \t\(\)\[\]\{\}\'\"&!$#~`+=,;*?])", r"\1", p)
        if os.path.exists(unescaped):
            p = unescaped
        else:
            p = unescaped

    # Fix missing tildes in macOS iCloud Mobile Documents path (e.g., comappleCloudDocs -> com~apple~CloudDocs)
    if not os.path.exists(p) and ("comappleCloudDocs" in p or "com~appleCloudDocs" in p or "comapple~CloudDocs" in p):
        fixed_icloud = re.sub(r"com~?apple~?CloudDocs", "com~apple~CloudDocs", p)
        if os.path.exists(fixed_icloud):
            p = fixed_icloud

    # Also check if user entered a relative folder name in current working directory
    if not os.path.exists(p):
        cwd_candidate = os.path.join(os.getcwd(), p)
        if os.path.exists(cwd_candidate):
            p = cwd_candidate

    return p


def check_macos():
    """Ensure script is running on macOS."""
    if sys.platform != "darwin":
        print("Error: This script requires macOS to set Finder tags.", file=sys.stderr)
        sys.exit(1)


def get_existing_tags(file_path: str) -> list:
    """Retrieve existing macOS Finder tags for a file."""
    try:
        res = subprocess.run(
            ["xattr", "-px", "com.apple.metadata:_kMDItemUserTags", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        hex_data = res.stdout.replace("\n", "").replace(" ", "")
        if not hex_data:
            return []
        raw_bytes = bytes.fromhex(hex_data)
        tags = plistlib.loads(raw_bytes)
        return tags if isinstance(tags, list) else []
    except Exception:
        return []


def format_tag(tag_name: str, color_code: int = 0) -> str:
    """Format tag string with color code for macOS plist format."""
    clean_name = tag_name.strip().strip("'\"")
    if "\n" in clean_name:
        return clean_name
    return f"{clean_name}\n{color_code}" if color_code > 0 else clean_name


def set_macos_tags(file_path: str, tags: list):
    """Write macOS Finder tags extended attribute."""
    plist_data = plistlib.dumps(tags, fmt=plistlib.FMT_BINARY)
    hex_str = plist_data.hex()
    subprocess.run(
        ["xattr", "-wx", "com.apple.metadata:_kMDItemUserTags", hex_str, file_path],
        check=True,
        capture_output=True,
    )


def tag_file(
    file_path: str,
    new_tag_formatted: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> bool:
    """Add a tag to a single file."""
    existing_tags = get_existing_tags(file_path)

    # Check if tag already exists (compare base tag names)
    target_base = new_tag_formatted.split("\n")[0].strip().lower()

    if overwrite:
        final_tags = [new_tag_formatted]
    else:
        # Avoid duplicates with same tag name
        final_tags = [
            t
            for t in existing_tags
            if t.split("\n")[0].strip().lower() != target_base
        ]
        final_tags.append(new_tag_formatted)

    if not dry_run:
        try:
            set_macos_tags(file_path, final_tags)
        except Exception as e:
            print(f"  [ERROR] Failed to tag {file_path}: {e}", file=sys.stderr)
            return False

    return True


def tag_folder_recursive(
    target_dir: str,
    tags: list,
    color_code: int = 0,
    overwrite: bool = False,
    include_dirs: bool = False,
    extensions: list = None,
    dry_run: bool = False,
    verbose: bool = True,
):
    """Recursively tag all .jpg / .jpeg files in a folder and its subfolders."""
    cleaned_dir = clean_path_string(str(target_dir))
    target_path = Path(cleaned_dir).expanduser().resolve()

    if not target_path.exists():
        print(f"Error: Directory '{cleaned_dir or target_dir}' does not exist.", file=sys.stderr)
        return

    if not target_path.is_dir():
        print(f"Error: Path '{cleaned_dir or target_dir}' is not a directory.", file=sys.stderr)
        return

    formatted_tags = [format_tag(t, color_code) for t in tags]

    # Default to .jpg and .jpeg if no extensions specified
    if extensions is None:
        extensions = [".jpg", ".jpeg"]

    # Normalize extensions
    norm_exts = set()
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext.startswith("."):
            ext = "." + ext
        norm_exts.add(ext)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing folder: {target_path}")
    print(f"Tags to apply: {', '.join(tags)} (Color: {COLOR_NAMES.get(color_code, 'None')})")
    print(f"Target file types: {', '.join(sorted(norm_exts))}")
    if overwrite:
        print("Mode: Overwrite existing tags")
    else:
        print("Mode: Append to existing tags")
    print("-" * 60)

    total_files = 0
    tagged_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(target_path):
        # Optional: tag directories themselves
        if include_dirs:
            for d in dirs:
                dir_path = os.path.join(root, d)
                for ft in formatted_tags:
                    tag_file(dir_path, ft, overwrite=overwrite, dry_run=dry_run)
                if verbose:
                    rel_dir = os.path.relpath(dir_path, target_path)
                    print(f"  [DIR]  {rel_dir}")

        for f in files:
            # Skip macOS hidden metadata files
            if f.startswith("._") or f == ".DS_Store":
                continue

            file_path = os.path.join(root, f)
            rel_file = os.path.relpath(file_path, target_path)

            file_ext = os.path.splitext(f)[1].lower()
            if file_ext not in norm_exts:
                skipped_count += 1
                continue

            total_files += 1
            success = True
            for ft in formatted_tags:
                if not tag_file(file_path, ft, overwrite=overwrite, dry_run=dry_run):
                    success = False

            if success:
                tagged_count += 1
                if verbose:
                    print(f"  [TAGGED JPG] {rel_file}")
            else:
                skipped_count += 1

    print("-" * 60)
    print(f"Summary:")
    print(f"  - Total matching .jpg files found: {total_files}")
    print(f"  - Successfully tagged:             {tagged_count}")
    if skipped_count > 0:
        print(f"  - Skipped (non-jpg / errors):      {skipped_count}")
    print(f"{'Simulation completed without making changes.' if dry_run else 'All .jpg files tagged successfully!'}\n")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Recursively apply macOS Finder tags exclusively to .jpg / .jpeg files in a folder and subfolders."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Path to the directory containing .jpg files to tag",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="append",
        dest="tags",
        help="Tag name to apply (can specify multiple times or comma-separated)",
    )
    parser.add_argument(
        "-c",
        "--color",
        default="none",
        help="Tag color: none, red, orange, yellow, green, blue, purple, gray (default: none)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite and remove existing tags on files instead of appending",
    )
    parser.add_argument(
        "--include-dirs",
        action="store_true",
        help="Also apply tags to subdirectories in addition to .jpg files",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        default=[".jpg", ".jpeg"],
        help="Target file extensions (default: .jpg .jpeg)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the operation without modifying files",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode with minimal console output",
    )
    return parser.parse_args()


def interactive_mode():
    """Prompt user for details if script is executed without arguments."""
    print("=" * 60)
    print("   macOS Recursive Finder Tagging Utility (.JPG Files)")
    print("=" * 60)

    current_cwd = os.getcwd()
    try:
        subdirs = [
            d
            for d in sorted(os.listdir(current_cwd))
            if os.path.isdir(os.path.join(current_cwd, d)) and not d.startswith(".")
        ]
    except Exception:
        subdirs = []

    print(f"\nCurrent Directory:\n  {current_cwd}")

    if subdirs:
        print("\nAvailable Subfolders in Current Directory:")
        for idx, d in enumerate(subdirs, 1):
            print(f"  [{idx:2d}] {d}")
        print("  [ 0] Entire Current Directory")
        print("-" * 60)

    # Folder prompt with validation
    while True:
        prompt_text = "Enter folder path, name, or number [0]: " if subdirs else "Enter folder path (or press Enter for current directory): "
        folder_raw = input(prompt_text).strip()
        if not folder_raw or folder_raw == "0":
            folder = current_cwd
            break

        # Check if user entered an index number from the subdirs list
        if folder_raw.isdigit() and subdirs:
            idx = int(folder_raw)
            if 1 <= idx <= len(subdirs):
                folder = os.path.join(current_cwd, subdirs[idx - 1])
                break

        folder_clean = clean_path_string(folder_raw)
        folder_path = Path(folder_clean).expanduser().resolve()

        if folder_path.exists() and folder_path.is_dir():
            folder = str(folder_path)
            break
        elif not folder_path.exists():
            print(f"  [!] Directory '{folder_clean}' does not exist. Please try again.")
        else:
            print(f"  [!] Path '{folder_clean}' is not a directory. Please try again.")

    # Tag prompt
    tag_input = input("\nEnter tag name (e.g. 'Project', 'Reviewed', 'Hold-program'): ").strip()
    while not tag_input:
        tag_input = input("Tag name cannot be empty. Please enter a tag name: ").strip()

    tags = [t.strip().strip("'\"") for t in tag_input.split(",") if t.strip().strip("'\"")]

    # Color prompt
    print("\nAvailable Colors:")
    print("  0: None (Default), 1: Gray, 2: Green, 3: Purple, 4: Blue, 5: Yellow, 6: Red, 7: Orange")
    color_choice = input("Enter color name or number (default: None): ").strip().lower().strip("'\"")

    if not color_choice:
        color_code = 0
    elif color_choice.isdigit():
        color_code = int(color_choice) if int(color_choice) in COLOR_NAMES else 0
    else:
        color_code = COLOR_MAP.get(color_choice, 0)

    # Overwrite prompt
    ov_choice = input("\nOverwrite existing tags? (y/N): ").strip().lower().strip("'\"")
    overwrite = ov_choice in ("y", "yes")

    return folder, tags, color_code, overwrite


def main():
    check_macos()
    args = parse_arguments()

    if not args.folder and not args.tags:
        folder, tags, color_code, overwrite = interactive_mode()
        dry_run = args.dry_run
        include_dirs = args.include_dirs
        extensions = args.extensions
        verbose = not args.quiet
    else:
        folder = clean_path_string(args.folder) if args.folder else os.getcwd()

        # Parse tags
        tags = []
        if args.tags:
            for t in args.tags:
                for sub_t in t.split(","):
                    cleaned_t = sub_t.strip().strip("'\"")
                    if cleaned_t:
                        tags.append(cleaned_t)
        if not tags:
            tags = ["Tagged"]

        # Parse color
        color_val = args.color.lower().strip().strip("'\"")
        if color_val.isdigit():
            color_code = int(color_val) if int(color_val) in COLOR_NAMES else 0
        else:
            color_code = COLOR_MAP.get(color_val, 0)

        overwrite = args.overwrite
        dry_run = args.dry_run
        include_dirs = args.include_dirs
        extensions = args.extensions
        verbose = not args.quiet

    tag_folder_recursive(
        target_dir=folder,
        tags=tags,
        color_code=color_code,
        overwrite=overwrite,
        include_dirs=include_dirs,
        extensions=extensions,
        dry_run=dry_run,
        verbose=verbose,
    )


if __name__ == "__main__":
    main()

