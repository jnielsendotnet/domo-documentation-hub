#!/usr/bin/env python3
"""
Rebuild the portal mapping from the actual file locations and update docs.json references.
"""
import json
import re
from pathlib import Path
import shutil

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
PORTAL_DIR = BASE_DIR / "portal"
DOCS_JSON = BASE_DIR / "docs.json"
OUTPUT_DIR = Path(__file__).parent / "output"

def extract_frontmatter(content):
    """Extract YAML frontmatter from MDX content."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        # Simple YAML parsing
        fm_dict = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                fm_dict[key.strip()] = value.strip().strip('"').strip("'")
        return fm_dict
    return {}

def scan_portal_files():
    """Scan all portal files and build mapping."""
    print(f"Scanning portal files in {PORTAL_DIR}...")
    mapping = {}

    for mdx_file in PORTAL_DIR.rglob("*.mdx"):
        try:
            with open(mdx_file, 'r', encoding='utf-8') as f:
                content = f.read()
                fm = extract_frontmatter(content)

                stoplight_id = fm.get('stoplight-id', '')
                if not stoplight_id:
                    continue

                # Get the relative path from portal directory
                rel_path = mdx_file.relative_to(PORTAL_DIR)
                # Remove .mdx extension
                ref_path = str(rel_path).replace('.mdx', '')

                mapping[stoplight_id] = {
                    'title': fm.get('title', ''),
                    'permalink': fm.get('permalink', ''),
                    'file_path': str(rel_path),
                    'reference': ref_path,
                    'full_path': str(mdx_file.relative_to(BASE_DIR))
                }
        except Exception as e:
            print(f"Error reading {mdx_file}: {e}")

    print(f"Found {len(mapping)} portal files with stoplight-ids")
    return mapping

def find_old_references_in_docs_json(docs_content):
    """Find all portal references in docs.json."""
    # Pattern to match portal references like "/portal/xxx-xxx" or "portal/xxx-xxx"
    pattern = r'"/?portal/([a-z0-9]+-[a-z0-9-]+)"'
    matches = re.finditer(pattern, docs_content)

    old_refs = {}
    for match in matches:
        full_ref = match.group(0).strip('"')
        filename = match.group(1)

        # Extract potential stoplight ID (everything before first dash)
        parts = filename.split('-')
        if parts:
            potential_id = parts[0]
            if potential_id not in old_refs:
                old_refs[potential_id] = []
            old_refs[potential_id].append(full_ref)

    print(f"\nFound {len(old_refs)} unique stoplight IDs in docs.json")
    return old_refs

def update_docs_json(mapping, docs_json_path):
    """Update docs.json with new portal references."""
    print(f"\nUpdating {docs_json_path}...")

    # Read docs.json
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    backup_path = docs_json_path.parent / "docs.json.backup"
    shutil.copy(docs_json_path, backup_path)
    print(f"Backup created: {backup_path}")

    # Track replacements
    replacements = {}
    updated_content = content

    # For each file in mapping, find and replace references
    for stoplight_id, info in mapping.items():
        # Look for various reference patterns
        patterns = [
            rf'"/portal/{stoplight_id}-[^"]*"',  # /portal/id-xxx
            rf'"portal/{stoplight_id}-[^"]*"',   # portal/id-xxx
        ]

        new_ref = f'portal/{info["reference"]}'

        for pattern in patterns:
            matches = re.finditer(pattern, updated_content)
            for match in matches:
                old_ref = match.group(0).strip('"')
                # Replace in content
                updated_content = updated_content.replace(f'"{old_ref}"', f'"{new_ref}"')
                replacements[old_ref] = new_ref

    # Write updated content
    with open(docs_json_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Updated {len(replacements)} references in docs.json")
    return replacements

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Scan portal files
    mapping = scan_portal_files()

    # Save new mapping
    mapping_file = OUTPUT_DIR / "portal_mapping_new.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    print(f"\nNew mapping saved to {mapping_file}")

    # Update docs.json
    replacements = update_docs_json(mapping, DOCS_JSON)

    # Save replacements report
    replacements_file = OUTPUT_DIR / "docs_json_replacements.json"
    with open(replacements_file, 'w', encoding='utf-8') as f:
        json.dump(replacements, f, indent=2)
    print(f"Replacements report saved to {replacements_file}")

    # Create summary report
    report_file = OUTPUT_DIR / "update_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Docs.json Update Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total portal files scanned: {len(mapping)}\n")
        f.write(f"References updated in docs.json: {len(replacements)}\n\n")

        f.write("\nSample Replacements:\n")
        f.write("-" * 70 + "\n")
        for i, (old, new) in enumerate(list(replacements.items())[:20]):
            f.write(f"\n{old}\n  -> {new}\n")
            if i >= 19:
                break

        if len(replacements) > 20:
            f.write(f"\n... and {len(replacements) - 20} more replacements\n")

    print(f"Report saved to {report_file}")

    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)
    print(f"✓ Scanned {len(mapping)} portal files")
    print(f"✓ Updated {len(replacements)} references in docs.json")
    print(f"✓ Backup saved to docs.json.backup")

if __name__ == "__main__":
    main()
