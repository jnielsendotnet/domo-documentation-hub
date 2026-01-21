#!/usr/bin/env python3
"""
Build stoplight-id to title mapping from docs.json
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def extract_stoplight_id(path: str) -> Tuple[Optional[str], str]:
    """
    Extract stoplight ID and title suffix from portal path.

    Examples:
        "/portal/d01f63a6ba662-domo-developer-portal"
        -> ("d01f63a6ba662", "domo-developer-portal")

        "portal/wjqiqhsvpadon-ai-service-layer-api"
        -> ("wjqiqhsvpadon", "ai-service-layer-api")
    """
    # Remove leading slash and "portal/"
    path_clean = path.lstrip('/').replace('portal/', '', 1)

    # Split on first hyphen to get ID and suffix
    match = re.match(r'^([a-z0-9]+)-(.+)$', path_clean)
    if match:
        return match.group(1), match.group(2)

    # If no match, return None for ID
    return None, path_clean


def kebab_to_title(kebab_str: str) -> str:
    """Convert kebab-case to Title Case"""
    return kebab_str.replace('-', ' ').title()


def extract_portal_mappings(
    obj: Any,
    current_label: str = '',
    parent_labels: List[str] = None,
    depth: int = 0
) -> List[Dict[str, str]]:
    """
    Recursively extract portal page mappings from docs.json structure.

    Returns list of dicts with: {label, path, stoplight_id, title_from_path, context}
    """
    if parent_labels is None:
        parent_labels = []

    if depth > 50:  # Prevent infinite recursion
        return []

    mappings = []

    if isinstance(obj, dict):
        # Update current label from context
        label = current_label
        new_parent_labels = parent_labels.copy()

        if 'label' in obj:
            label = obj['label']
            new_parent_labels.append(label)
        elif 'group' in obj:
            label = obj['group']
            new_parent_labels.append(label)
        elif 'tab' in obj and not current_label:
            label = obj['tab']
            new_parent_labels.append(label)

        # Check for direct page reference
        if 'page' in obj and isinstance(obj['page'], str) and 'portal/' in obj['page']:
            stoplight_id, suffix = extract_stoplight_id(obj['page'])
            if stoplight_id:
                mappings.append({
                    'label': label,
                    'path': obj['page'],
                    'stoplight_id': stoplight_id,
                    'title_from_path': kebab_to_title(suffix),
                    'permalink_suffix': suffix,
                    'context': ' > '.join(new_parent_labels)
                })

        # Check pages array
        if 'pages' in obj and isinstance(obj['pages'], list):
            for item in obj['pages']:
                if isinstance(item, str) and 'portal/' in item:
                    stoplight_id, suffix = extract_stoplight_id(item)
                    if stoplight_id:
                        mappings.append({
                            'label': label,
                            'path': item,
                            'stoplight_id': stoplight_id,
                            'title_from_path': kebab_to_title(suffix),
                            'permalink_suffix': suffix,
                            'context': ' > '.join(new_parent_labels)
                        })
                elif isinstance(item, dict):
                    mappings.extend(extract_portal_mappings(item, label, new_parent_labels, depth + 1))

        # Recurse through other values
        for k, v in obj.items():
            if k not in ['page', 'pages', 'label', 'group', 'tab']:
                if isinstance(v, (dict, list)):
                    mappings.extend(extract_portal_mappings(v, current_label, parent_labels, depth + 1))

    elif isinstance(obj, list):
        for item in obj:
            mappings.extend(extract_portal_mappings(item, current_label, parent_labels, depth + 1))

    return mappings


def build_mapping(docs_json_path: Path) -> Dict[str, Dict[str, str]]:
    """Build the stoplight-id -> title mapping"""
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mappings = extract_portal_mappings(data)

    # Convert list to dict keyed by stoplight_id
    mapping_dict = {}
    for m in mappings:
        sid = m['stoplight_id']
        if sid in mapping_dict:
            # Handle duplicates - keep first occurrence
            print(f"Warning: Duplicate stoplight-id {sid}")
            print(f"  Existing: {mapping_dict[sid]}")
            print(f"  New: {m}")
            print(f"  Keeping existing entry")
        else:
            mapping_dict[sid] = m

    return mapping_dict


def main():
    repo_root = Path(__file__).parent.parent.parent
    docs_json = repo_root / 'docs.json'
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)

    if not docs_json.exists():
        print(f"Error: {docs_json} not found")
        return 1

    print(f"Building mapping from {docs_json}...")
    mapping = build_mapping(docs_json)

    # Save mapping
    output_file = output_dir / 'mapping_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)

    print(f"\nMapping complete!")
    print(f"  Total entries: {len(mapping)}")
    print(f"  Output: {output_file}")

    # Generate summary report
    report_file = output_dir / 'mapping_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Stoplight ID to Title Mapping Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total mappings: {len(mapping)}\n\n")

        for sid, info in sorted(mapping.items()):
            f.write(f"{sid}\n")
            f.write(f"  Label: {info['label']}\n")
            f.write(f"  Path: {info['path']}\n")
            f.write(f"  Title from path: {info['title_from_path']}\n")
            f.write(f"  Permalink: {sid}-{info['permalink_suffix']}\n")
            f.write(f"  Context: {info['context']}\n")
            f.write("\n")

    print(f"  Report: {report_file}")

    return 0


if __name__ == '__main__':
    exit(main())
