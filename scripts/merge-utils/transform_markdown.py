#!/usr/bin/env python3
"""
Transform Stoplight markdown to Mintlify format.
"""

import sys
import re
from pathlib import Path

def transform_markdown(content, title, sidebar_title=None):
    """Transform Stoplight markdown to Mintlify format."""

    # Remove stoplight-id frontmatter if present
    content = re.sub(r'^---\s*\nstoplight-id:.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Remove title from content (will be in frontmatter)
    content = re.sub(r'^#\s+.*?\n', '', content, count=1)

    # Transform image paths
    content = re.sub(r'\!\[(.*?)\]\((\.\.\/)*assets\/images\/(.*?)\)', r'![\1](/images/dev/\3)', content)

    # Transform blockquote tips/notes/warnings to Mintlify components
    content = re.sub(r'>\s*\*\*Tip:\*\*\s*(.*?)(?=\n\n|\n$)', r'<Tip>\n\1\n</Tip>', content, flags=re.MULTILINE)
    content = re.sub(r'>\s*\*\*Note:\*\*\s*(.*?)(?=\n\n|\n$)', r'<Info>\n\1\n</Info>', content, flags=re.MULTILINE)
    content = re.sub(r'>\s*\*\*Warning:\*\*\s*(.*?)(?=\n\n|\n$)', r'<Warning>\n\1\n</Warning>', content, flags=re.MULTILINE)
    content = re.sub(r'>\s*\*\*BETA:\*\*\s*(.*?)(?=\n\n|\n$)', r'<Warning>\n**BETA:** \1\n</Warning>', content, flags=re.MULTILINE)

    # Transform code blocks with language
    content = re.sub(r'```(\w+)', r'```\1', content)

    # Create frontmatter
    sidebar = sidebar_title or title
    frontmatter = f'---\ntitle: "{title}"\nsidebarTitle: "{sidebar}"\n---\n\n'

    return frontmatter + content.strip()

def main():
    if len(sys.argv) < 4:
        print("Usage: python transform_markdown.py <input_file> <output_file> <title> [sidebar_title]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    title = sys.argv[3]
    sidebar_title = sys.argv[4] if len(sys.argv) > 4 else None

    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Transform
    transformed = transform_markdown(content, title, sidebar_title)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transformed)

    print(f"✓ Transformed {input_file.name} -> {output_file.name}")

if __name__ == "__main__":
    main()
