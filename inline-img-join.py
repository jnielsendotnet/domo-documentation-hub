#!/usr/bin/env python3
"""Join inline <img> icon tags to the end of the preceding non-blank line."""

import re
import subprocess
import sys

IMG_LINE_PATTERN = re.compile(
    r"^<img src=\"[^\"]+\" style=\{\{width: 20, height: 20, display: 'inline',"
    r" verticalAlign: 'start', margin: '0'\}\}/>"
)

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

def process_content(content):
    lines = content.split("\n")
    result = []
    joins = 0
    for line in lines:
        if IMG_LINE_PATTERN.match(line):
            # Remove any trailing blank lines and join to the previous non-blank line
            while result and result[-1].strip() == "":
                result.pop()
            if result:
                result[-1] = result[-1] + line
                joins += 1
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result), joins

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    updated, joins = process_content(original)

    if updated == original:
        return 0

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)

    return joins

def main():
    files = get_queued_files()
    if not files:
        print("No queued ja/s/article/ files found.")
        sys.exit(0)

    total_joins = 0
    total_files = 0

    for path in files:
        n = process_file(path)
        if n:
            print(f"  {n:3d} join(s): {path}")
            total_joins += n
            total_files += 1

    print(f"\nDone. {total_joins} join(s) across {total_files} file(s).")

if __name__ == "__main__":
    main()
