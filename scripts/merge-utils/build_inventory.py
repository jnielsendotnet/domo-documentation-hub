#!/usr/bin/env python3
"""
Build inventory of documentation files from both source and migrated repositories.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import hashlib

# Repository paths
SCRIPT_DIR = Path(__file__).parent
MIGRATED_REPO = SCRIPT_DIR.parent.parent  # domo-documentation-hub
SOURCE_REPO = MIGRATED_REPO.parent / "domo-developer-portal"

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        # Simple YAML parser for key: value pairs
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter

def get_file_hash(file_path):
    """Compute MD5 hash of file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Normalize content: strip frontmatter for comparison
            content_without_frontmatter = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            return hashlib.md5(content_without_frontmatter.encode()).hexdigest()
    except Exception as e:
        return None

def scan_source_repo():
    """Scan source repository (domo-developer-portal)."""
    print(f"Scanning source repository: {SOURCE_REPO}")

    docs_dir = SOURCE_REPO / "docs"
    if not docs_dir.exists():
        print(f"ERROR: Source docs directory not found: {docs_dir}")
        return []

    inventory = []

    # Find all .md and .yaml files
    for ext in ['**/*.md', '**/*.yaml']:
        for file_path in docs_dir.glob(ext):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract metadata
                frontmatter = extract_frontmatter(content)
                stoplight_id = frontmatter.get('stoplight-id', None)

                # Get title from frontmatter or first heading
                title = frontmatter.get('title', '')
                if not title:
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1)

                # Get file stats
                stats = file_path.stat()

                # Relative path from docs directory
                rel_path = str(file_path.relative_to(SOURCE_REPO))

                inventory.append({
                    'path': rel_path,
                    'filename': file_path.name,
                    'type': file_path.suffix,
                    'title': title,
                    'stoplight_id': stoplight_id,
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    'content_hash': get_file_hash(file_path)
                })

            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")

    print(f"Found {len(inventory)} files in source repository")
    return inventory

def scan_migrated_repo():
    """Scan migrated repository (domo-documentation-hub)."""
    print(f"Scanning migrated repository: {MIGRATED_REPO}")

    portal_dir = MIGRATED_REPO / "portal"
    if not portal_dir.exists():
        print(f"ERROR: Portal directory not found: {portal_dir}")
        return []

    inventory = []

    # Find all .mdx files in portal directory
    for file_path in portal_dir.glob('*.mdx'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata
            frontmatter = extract_frontmatter(content)
            title = frontmatter.get('title', '')
            permalink = frontmatter.get('permalink', '')
            sidebar_title = frontmatter.get('sidebarTitle', '')

            # Extract hash prefix from filename (before first hyphen)
            filename_parts = file_path.stem.split('-', 1)
            hash_prefix = filename_parts[0] if len(filename_parts) > 0 else ''

            # Get file stats
            stats = file_path.stat()

            # Relative path from migrated repo root
            rel_path = str(file_path.relative_to(MIGRATED_REPO))

            inventory.append({
                'path': rel_path,
                'filename': file_path.name,
                'type': file_path.suffix,
                'title': title,
                'sidebar_title': sidebar_title,
                'permalink': permalink,
                'hash_prefix': hash_prefix,
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'content_hash': get_file_hash(file_path)
            })

        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")

    print(f"Found {len(inventory)} files in migrated repository")
    return inventory

def main():
    """Main execution."""
    print("=" * 60)
    print("Building Documentation Repository Inventories")
    print("=" * 60)

    # Scan both repositories
    source_inventory = scan_source_repo()
    migrated_inventory = scan_migrated_repo()

    # Save inventories
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    source_output = output_dir / "source_inventory.json"
    migrated_output = output_dir / "migrated_inventory.json"

    with open(source_output, 'w', encoding='utf-8') as f:
        json.dump(source_inventory, f, indent=2)
    print(f"\nSource inventory saved to: {source_output}")

    with open(migrated_output, 'w', encoding='utf-8') as f:
        json.dump(migrated_inventory, f, indent=2)
    print(f"Migrated inventory saved to: {migrated_output}")

    # Summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(f"Source repository files: {len(source_inventory)}")

    # Count by type
    source_md = sum(1 for item in source_inventory if item['type'] == '.md')
    source_yaml = sum(1 for item in source_inventory if item['type'] == '.yaml')
    source_with_id = sum(1 for item in source_inventory if item['stoplight_id'])
    source_without_id = len(source_inventory) - source_with_id

    print(f"  - Markdown files (.md): {source_md}")
    print(f"  - YAML files (.yaml): {source_yaml}")
    print(f"  - Files with stoplight-id: {source_with_id}")
    print(f"  - Files without stoplight-id: {source_without_id}")

    print(f"\nMigrated repository files: {len(migrated_inventory)}")
    print(f"  - All files are .mdx in /portal/")

    print("\nInventory build complete!")

if __name__ == "__main__":
    main()
