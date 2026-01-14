#!/usr/bin/env python3
"""
Create mapping between source and migrated documentation files.
"""

import json
from pathlib import Path
from difflib import SequenceMatcher

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"

def load_inventories():
    """Load source and migrated inventories."""
    source_file = OUTPUT_DIR / "source_inventory.json"
    migrated_file = OUTPUT_DIR / "migrated_inventory.json"

    if not source_file.exists() or not migrated_file.exists():
        print("ERROR: Inventory files not found. Run build_inventory.py first.")
        exit(1)

    with open(source_file, 'r', encoding='utf-8') as f:
        source = json.load(f)

    with open(migrated_file, 'r', encoding='utf-8') as f:
        migrated = json.load(f)

    return source, migrated

def similarity_ratio(str1, str2):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def create_stoplight_mapping(source, migrated):
    """Create mapping using stoplight-id (primary method)."""
    print("\nCreating mappings using stoplight-id...")

    # Build index of migrated files by hash_prefix
    migrated_index = {}
    for item in migrated:
        hash_prefix = item.get('hash_prefix', '')
        if hash_prefix:
            migrated_index[hash_prefix] = item

    print(f"  Migrated files indexed: {len(migrated_index)}")

    # Match source files
    mapped = []
    unmapped_source = []

    for source_item in source:
        stoplight_id = source_item.get('stoplight_id')

        if stoplight_id and stoplight_id in migrated_index:
            # Perfect match found
            migrated_item = migrated_index[stoplight_id]
            mapped.append({
                'stoplight_id': stoplight_id,
                'source': source_item,
                'migrated': migrated_item,
                'confidence': 'high',
                'match_method': 'stoplight_id'
            })
        else:
            unmapped_source.append(source_item)

    print(f"  Matched files (stoplight-id): {len(mapped)}")
    print(f"  Unmapped source files: {len(unmapped_source)}")

    return mapped, unmapped_source, list(migrated_index.values())

def fuzzy_match_unmapped(unmapped_source, migrated_files, already_mapped_stoplight_ids):
    """Attempt fuzzy matching for files without stoplight-id."""
    print("\nAttempting fuzzy matching for unmapped files...")

    # Filter out already-mapped migrated files
    available_migrated = [
        m for m in migrated_files
        if m.get('hash_prefix') not in already_mapped_stoplight_ids
    ]

    fuzzy_mapped = []
    ambiguous = []

    for source_item in unmapped_source:
        source_title = source_item.get('title', '')
        source_filename = source_item.get('filename', '').replace('.md', '').replace('.yaml', '')

        best_match = None
        best_score = 0

        for migrated_item in available_migrated:
            migrated_title = migrated_item.get('title', '')
            migrated_filename = migrated_item.get('filename', '').replace('.mdx', '')

            # Calculate similarity scores
            title_score = similarity_ratio(source_title, migrated_title) if source_title and migrated_title else 0
            filename_score = similarity_ratio(source_filename, migrated_filename)

            # Weighted average (title is more important)
            combined_score = (title_score * 0.7) + (filename_score * 0.3)

            if combined_score > best_score:
                best_score = combined_score
                best_match = migrated_item

        # Threshold for fuzzy matching
        if best_score > 0.6:  # 60% similarity threshold
            confidence = 'medium' if best_score > 0.8 else 'low'
            fuzzy_mapped.append({
                'stoplight_id': None,
                'source': source_item,
                'migrated': best_match,
                'confidence': confidence,
                'match_method': 'fuzzy',
                'similarity_score': round(best_score, 3)
            })
            # Remove from available pool
            available_migrated.remove(best_match)
        else:
            ambiguous.append(source_item)

    print(f"  Fuzzy matched files: {len(fuzzy_mapped)}")
    print(f"  Ambiguous files (needs review): {len(ambiguous)}")

    return fuzzy_mapped, ambiguous

def identify_unmapped_migrated(migrated_files, all_mapped):
    """Identify migrated files that have no source match."""
    mapped_hash_prefixes = {m['migrated']['hash_prefix'] for m in all_mapped if m['migrated'].get('hash_prefix')}

    unmapped_migrated = [
        m for m in migrated_files
        if m.get('hash_prefix') not in mapped_hash_prefixes
    ]

    return unmapped_migrated

def main():
    """Main execution."""
    print("=" * 60)
    print("Creating File Mappings")
    print("=" * 60)

    # Load inventories
    source, migrated = load_inventories()

    # Step 1: Map using stoplight-id
    mapped_by_id, unmapped_source, migrated_files = create_stoplight_mapping(source, migrated)

    # Step 2: Fuzzy match remaining files
    already_mapped_ids = {m['stoplight_id'] for m in mapped_by_id if m['stoplight_id']}
    fuzzy_mapped, ambiguous = fuzzy_match_unmapped(unmapped_source, migrated_files, already_mapped_ids)

    # Combine all mappings
    all_mapped = mapped_by_id + fuzzy_mapped

    # Step 3: Identify unmapped migrated files
    unmapped_migrated = identify_unmapped_migrated(migrated, all_mapped)

    # Build final mapping structure
    mapping = {
        'summary': {
            'total_source_files': len(source),
            'total_migrated_files': len(migrated),
            'mapped_files': len(all_mapped),
            'mapped_by_stoplight_id': len(mapped_by_id),
            'mapped_by_fuzzy': len(fuzzy_mapped),
            'unmapped_migrated': len(unmapped_migrated),
            'ambiguous': len(ambiguous)
        },
        'mapped': all_mapped,
        'ambiguous': ambiguous,
        'unmapped_migrated': unmapped_migrated
    }

    # Save mapping
    output_file = OUTPUT_DIR / "file_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n" + "=" * 60)
    print("Mapping Summary")
    print("=" * 60)
    print(f"Total source files: {mapping['summary']['total_source_files']}")
    print(f"Total migrated files: {mapping['summary']['total_migrated_files']}")
    print(f"\nMapped files: {mapping['summary']['mapped_files']}")
    print(f"  - By stoplight-id (high confidence): {mapping['summary']['mapped_by_stoplight_id']}")
    print(f"  - By fuzzy matching (medium/low confidence): {mapping['summary']['mapped_by_fuzzy']}")
    print(f"\nUnmapped migrated files: {mapping['summary']['unmapped_migrated']}")
    print(f"Ambiguous source files (needs review): {mapping['summary']['ambiguous']}")

    print(f"\nMapping saved to: {output_file}")
    print("\nNext: Run detect_changes.py to analyze content differences")

if __name__ == "__main__":
    main()
