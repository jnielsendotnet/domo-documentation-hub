#!/usr/bin/env python3
"""
Update docs.json to replace old article references with new portal paths.
Only updates references that have corresponding portal files.
"""
import json
import re
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DOCS_JSON = BASE_DIR / "docs.json"
OUTPUT_DIR = Path(__file__).parent / "output"
MAPPING_FILE = OUTPUT_DIR / "mapping_output.json"

def load_portal_mapping():
    """Load the portal mapping from mapping_output.json."""
    print(f"Loading portal mapping from {MAPPING_FILE}...")

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    print(f"Loaded {len(mapping)} portal files")
    return mapping

def scan_docs_json_for_stoplight_ids(docs_content, portal_mapping):
    """Find which stoplight IDs are already in docs.json and which portal files are missing."""
    # Find all references in docs.json - could be paths like "portal/xxx" or just stoplight IDs

    # Get all stoplight IDs from portal mapping
    portal_ids = set(portal_mapping.keys())

    # Find all string values in docs.json
    all_strings = re.findall(r'"([^"]+)"', docs_content)

    # Check which portal IDs are present
    found_ids = set()
    old_article_refs = set()

    for s in all_strings:
        # Check if it's a portal reference
        if 'portal/' in s:
            # Extract the stoplight ID from paths like "portal/d01f63a6ba662-domo-developer-portal"
            match = re.search(r'portal/([a-z0-9]+)-', s)
            if match:
                sid = match.group(1)
                if sid in portal_ids:
                    found_ids.add(sid)
        # Check if it's just a stoplight ID
        elif s in portal_ids:
            found_ids.add(s)
        # Check if it's an old article reference
        elif s.startswith('s/article/'):
            old_article_refs.add(s)

    missing_ids = portal_ids - found_ids

    print(f"\nDocs.json analysis:")
    print(f"  Portal files already referenced: {len(found_ids)}")
    print(f"  Portal files missing from docs.json: {len(missing_ids)}")
    print(f"  Old article references (s/article/*): {len(old_article_refs)}")

    return found_ids, missing_ids, old_article_refs

def build_reference_format(stoplight_id, info):
    """Build the reference format for docs.json - just use the permalink."""
    # Use the permalink which is like "d01f63a6ba662-domo-developer-portal"
    return info['permalink_suffix']

def main():
    # Load portal mapping
    portal_mapping = load_portal_mapping()

    # Load docs.json
    print(f"\nLoading {DOCS_JSON}...")
    with open(DOCS_JSON, 'r', encoding='utf-8') as f:
        docs_content = f.read()

    # Analyze current state
    found_ids, missing_ids, old_article_refs = scan_docs_json_for_stoplight_ids(docs_content, portal_mapping)

    # Create a mapping of what could be updated
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal portal files available: {len(portal_mapping)}")
    print(f"Already in docs.json: {len(found_ids)}")
    print(f"Missing from docs.json: {len(missing_ids)}")
    print(f"Old article references: {len(old_article_refs)}")

    # Save missing IDs report
    missing_report = OUTPUT_DIR / "missing_from_docs_json.json"
    missing_list = []
    for sid in sorted(missing_ids):
        info = portal_mapping[sid]
        missing_list.append({
            'stoplight_id': sid,
            'title': info['title_from_path'],
            'path': info['path'],
            'context': info['context'],
            'reference': build_reference_format(sid, info)
        })

    with open(missing_report, 'w', encoding='utf-8') as f:
        json.dump(missing_list, f, indent=2)

    print(f"\nMissing portal files report saved to {missing_report}")

    # Show sample of missing files
    if missing_list:
        print("\nSample of missing portal files (first 10):")
        for item in missing_list[:10]:
            print(f"  {item['stoplight_id']}: {item['title']} ({item['context']})")
            print(f"    Reference: \"{item['reference']}\"")

    print("\n" + "="*70)
    print("Note: This script analyzed the current state.")
    print("To update docs.json, you'll need to manually add the missing references")
    print("or we can create a script to do automatic replacements.")
    print("="*70)

if __name__ == "__main__":
    main()
