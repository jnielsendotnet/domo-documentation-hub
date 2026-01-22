#!/usr/bin/env python3
"""
Fix broken Stoplight image paths in MDX files.

This script updates old Stoplight API paths to the new simplified paths:
OLD: /images/dev/stoplight.io/api/v1/projects/.../branches/.../images/assets/images/FILE
NEW: /images/dev/stoplight.io/images/FILE

OLD: /images/dev/stoplight.io/api/v1/projects/.../branches/.../images/assets/tutorials/...
NEW: /images/dev/stoplight.io/tutorials/...
"""

import re
from pathlib import Path
from typing import Tuple, List
import argparse


def fix_stoplight_paths(content: str, filepath: Path, repo_root: Path, dry_run: bool = False) -> Tuple[str, List[str]]:
    """
    Fix Stoplight image paths in content.

    Returns:
        Tuple of (updated_content, list_of_changes)
    """
    changes = []
    updated_content = content

    # Pattern for old Stoplight paths
    # Matches: /images/dev/stoplight.io/api/v1/projects/{id}/branches/{id}/images/assets/{type}/{filename}
    old_pattern = r'/images/dev/stoplight\.io/api/v1/projects/[^/]+/branches/[^/]+/images/assets/(images|tutorials)/(.+?)(?=[\)\s"\'])'

    def replacement(match):
        asset_type = match.group(1)  # 'images' or 'tutorials'
        rest_of_path = match.group(2)  # filename or subfolder/filename

        # Build new path
        new_path = f'/images/dev/stoplight.io/{asset_type}/{rest_of_path}'

        # Verify the file exists
        resolved = repo_root / new_path.lstrip('/')
        if not resolved.exists():
            # Try without subfolder if it's a tutorial
            if asset_type == 'tutorials' and '/' in rest_of_path:
                # Sometimes the subfolder structure changed
                filename = Path(rest_of_path).name
                new_path_alt = f'/images/dev/stoplight.io/{asset_type}/{filename}'
                resolved_alt = repo_root / new_path_alt.lstrip('/')
                if resolved_alt.exists():
                    new_path = new_path_alt
                    changes.append(f"  → {match.group(0)} → {new_path} (simplified path)")
                    return new_path

            changes.append(f"  → {match.group(0)} → {new_path} (⚠️ file not found)")
        else:
            changes.append(f"  → {match.group(0)} → {new_path} (✓)")

        return new_path

    # Apply the replacement
    updated_content = re.sub(old_pattern, replacement, updated_content)

    return updated_content, changes


def process_file(filepath: Path, repo_root: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """
    Process a single MDX file to fix image paths.

    Returns:
        Tuple of (modified: bool, changes: List[str])
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    updated_content, changes = fix_stoplight_paths(original_content, filepath, repo_root, dry_run)

    if updated_content != original_content:
        if not dry_run:
            # Write the updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        return True, changes
    else:
        return False, []


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fix broken Stoplight image paths in MDX files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to process'
    )

    args = parser.parse_args()

    repo_root = Path.cwd()
    portal_dir = repo_root / 'portal'

    if not portal_dir.exists():
        print(f"Error: Portal directory not found at {portal_dir}")
        return

    print(f"Scanning MDX files in {portal_dir}...")
    mdx_files = list(portal_dir.rglob('*.mdx'))

    if args.limit:
        mdx_files = mdx_files[:args.limit]

    print(f"Processing {len(mdx_files)} MDX files\n")

    mode_str = "DRY RUN" if args.dry_run else "LIVE"
    print(f"{'='*80}")
    print(f"MODE: {mode_str}")
    print(f"{'='*80}\n")

    if not args.dry_run:
        response = input("Proceed with fixing image paths? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Process files
    modified_files = []
    all_changes = []
    total_changes = 0

    for i, filepath in enumerate(mdx_files, 1):
        if i % 50 == 0:
            print(f"Processing file {i}/{len(mdx_files)}...")

        try:
            modified, changes = process_file(filepath, repo_root, dry_run=args.dry_run)

            if modified:
                rel_path = filepath.relative_to(repo_root)
                modified_files.append(str(rel_path))
                all_changes.append({
                    'file': str(rel_path),
                    'changes': changes
                })
                total_changes += len(changes)

                print(f"[{i}/{len(mdx_files)}] {rel_path}")
                for change in changes:
                    print(change)
                print()

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # Print summary
    print(f"\n{'='*80}")
    print("FIX SUMMARY")
    print(f"{'='*80}")
    print(f"Files modified: {len(modified_files)}")
    print(f"Total path changes: {total_changes}")
    print(f"{'='*80}\n")

    if args.dry_run:
        print("\n⚠ This was a DRY RUN - no files were modified")
        print("  Run without --dry-run to apply changes")
    else:
        print("\n✓ Image paths have been updated!")
        print("\nNext steps:")
        print("1. Run: python scripts/validate_images.py")
        print("2. Verify the changes reduced broken images")
        print("3. Commit the changes if everything looks good")


if __name__ == '__main__':
    main()
