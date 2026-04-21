#!/usr/bin/env python3
"""Replace <InlineImage src="..." /> with <img> tags in queued ja/s/article/ files."""

import re
import subprocess
import sys

INLINE_IMAGE_PATTERN = re.compile(r'<InlineImage\s+src="([^"]+)"\s*/>')
BROKEN_STYLE_PATTERN = re.compile(
    r"style=\{\{width: 20, height: 20, display: \\'inline\\', verticalAlign: \\'start\\', margin: \\'0\\'\}\}"
)
IMPORT_PATTERN = re.compile(
    r'^import\s+\{InlineImage\}\s+from\s+"[^"]+/InlineImage\.mdx";\n?',
    re.MULTILINE
)
CORRECT_STYLE = "style={{width: 20, height: 20, display: 'inline', verticalAlign: 'start', margin: '0'}}"

def inline_image_replacement(m):
    return f'<img src="{m.group(1)}" {CORRECT_STYLE}/>'

def get_queued_files():
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, check=True
    )
    files = []
    for line in result.stdout.splitlines():
        path = line[3:].strip()
        if path.startswith("ja/s/article/") and path.endswith(".mdx"):
            files.append(path)
    return files

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    # Remove InlineImage import lines
    updated = IMPORT_PATTERN.sub("", original)
    # Fix any previously mangled style attributes (backslash-escaped quotes)
    updated = BROKEN_STYLE_PATTERN.sub(CORRECT_STYLE, updated)
    # Replace any remaining InlineImage tags
    updated = INLINE_IMAGE_PATTERN.sub(inline_image_replacement, updated)

    if updated == original:
        return 0

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)

    count = (
        len(IMPORT_PATTERN.findall(original))
        + len(INLINE_IMAGE_PATTERN.findall(original))
        + len(BROKEN_STYLE_PATTERN.findall(original))
    )
    return count

def main():
    files = get_queued_files()
    if not files:
        print("No queued ja/s/article/ files found.")
        sys.exit(0)

    total_replacements = 0
    total_files = 0

    for path in files:
        n = process_file(path)
        if n:
            print(f"  {n:3d} replacement(s): {path}")
            total_replacements += n
            total_files += 1

    print(f"\nDone. {total_replacements} replacement(s) across {total_files} file(s).")

if __name__ == "__main__":
    main()
