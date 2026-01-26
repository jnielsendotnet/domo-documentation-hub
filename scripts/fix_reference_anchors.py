#!/usr/bin/env python3
"""
Fix anchor links in reference.mdx by adding HTML anchor tags before headings.

The table links point to anchors like #auth-authenticationsuccess,
but markdown auto-generates IDs without hyphens (like #authauthenticationsuccess).
This script adds <a id="..."></a> tags before headings to match the table links.
"""

import re
from pathlib import Path

def extract_anchor_links(content):
    """Extract all anchor links from markdown tables."""
    # Pattern: [text](#anchor-id)
    pattern = r'\[([^\]]+)\]\(#([a-z0-9_-]+)\)'
    matches = re.finditer(pattern, content)

    anchor_map = {}
    for match in matches:
        link_text = match.group(1)
        anchor_id = match.group(2)
        anchor_map[anchor_id] = link_text

    return anchor_map

def normalize_text(text):
    """Normalize text for comparison."""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def fix_reference_anchors(file_path):
    """Add anchor tags before headings in reference.mdx."""
    print(f"Reading {file_path}")
    content = file_path.read_text(encoding='utf-8')

    # Extract all anchor links from tables
    anchor_map = extract_anchor_links(content)
    print(f"\nFound {len(anchor_map)} anchor links to fix")

    lines = content.split('\n')
    modified_lines = []
    added_count = 0
    used_anchors = set()

    for i, line in enumerate(lines):
        # Check if this is a #### heading
        if line.startswith('####'):
            heading_text = line.replace('####', '').strip()
            heading_normalized = normalize_text(heading_text)

            # Find matching anchor
            best_match = None
            best_score = 0

            for anchor_id, link_text in anchor_map.items():
                if anchor_id in used_anchors:
                    continue

                link_normalized = normalize_text(link_text)

                # Exact match
                if heading_normalized == link_normalized:
                    best_match = anchor_id
                    best_score = 1.0
                    break

                # Partial match
                if link_normalized in heading_normalized or heading_normalized in link_normalized:
                    score = min(len(heading_normalized), len(link_normalized)) / max(len(heading_normalized), len(link_normalized))
                    if score > best_score:
                        best_score = score
                        best_match = anchor_id

            # Add anchor if we found a good match
            if best_match and best_score >= 0.8:
                modified_lines.append(f'<a id="{best_match}"></a>')
                modified_lines.append(line)
                used_anchors.add(best_match)
                added_count += 1
                print(f"✓ Added anchor #{best_match} before: {heading_text}")
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    # Write back
    new_content = '\n'.join(modified_lines)
    file_path.write_text(new_content, encoding='utf-8')

    print(f"\n✅ Added {added_count} anchor tags")

    # Report unused anchors
    unused = set(anchor_map.keys()) - used_anchors
    if unused:
        print(f"\n⚠️  {len(unused)} anchors have no matching heading:")
        for anchor in sorted(unused):
            print(f"   #{anchor}: {anchor_map[anchor]}")

def main():
    reference_file = Path('/Users/jon.tiritilli/dev/domo-documentation-hub/portal/Connectors/Custom-Connectors/reference.mdx')

    if not reference_file.exists():
        print(f"❌ File not found: {reference_file}")
        return

    fix_reference_anchors(reference_file)

if __name__ == '__main__':
    main()
