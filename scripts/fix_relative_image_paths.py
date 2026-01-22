#!/usr/bin/env python3
"""
Fix relative and incorrect image paths that point to images in stoplight directory.

This script finds images with wrong paths (relative paths, /images/dev/, /assets/)
that actually exist in images/dev/stoplight.io/images/ and updates them to the
correct absolute path.
"""

import re
from pathlib import Path
from typing import Tuple, List, Set
import argparse
import json


def load_stoplight_images(repo_root: Path) -> Set[str]:
    """Load all image filenames from stoplight directory."""
    stoplight_dir = repo_root / 'images/dev/stoplight.io/images'
    if not stoplight_dir.exists():
        return set()

    return set(f.name for f in stoplight_dir.glob('*') if f.is_file())


def fix_image_paths_to_stoplight(content: str, stoplight_images: Set[str], filepath: Path, repo_root: Path) -> Tuple[str, List[str]]:
    """
    Fix image paths that reference files in stoplight directory.

    Patterns to fix:
    - ../../assets/images/filename.png
    - ../../../../../assets/images/filename.png
    - /assets/images/filename.png
    - /images/dev/filename.png
    - ../../../images/dev/stoplight.io/images/images/filename.png (double images)

    Returns:
        Tuple of (updated_content, list_of_changes)
    """
    changes = []
    updated_content = content

    # Pattern 1: Relative paths to assets/images
    pattern1 = r'(\.\./)+assets/images/([^)\s"\'\]]+)'

    def fix_relative_assets(match):
        filename = match.group(2)
        if filename in stoplight_images:
            new_path = f'/images/dev/stoplight.io/images/{filename}'
            changes.append(f"  ✓ {match.group(0)} → {new_path}")
            return new_path
        return match.group(0)

    updated_content = re.sub(pattern1, fix_relative_assets, updated_content)

    # Pattern 2: Absolute paths to /assets/images
    pattern2 = r'/assets/images/([^)\s"\'\]]+)'

    def fix_absolute_assets(match):
        filename = match.group(1)
        if filename in stoplight_images:
            new_path = f'/images/dev/stoplight.io/images/{filename}'
            changes.append(f"  ✓ {match.group(0)} → {new_path}")
            return new_path
        return match.group(0)

    updated_content = re.sub(pattern2, fix_absolute_assets, updated_content)

    # Pattern 3: /images/dev/filename.png (missing stoplight.io/images)
    pattern3 = r'/images/dev/([^/\s)\"\'\]]+\.(png|jpg|jpeg|gif|svg|webp))'

    def fix_images_dev(match):
        filename = match.group(1)
        if filename in stoplight_images:
            new_path = f'/images/dev/stoplight.io/images/{filename}'
            changes.append(f"  ✓ {match.group(0)} → {new_path}")
            return new_path
        return match.group(0)

    updated_content = re.sub(pattern3, fix_images_dev, updated_content)

    # Pattern 4: Relative paths with multiple ../../../
    pattern4 = r'(\.\./)+images/dev/stoplight\.io/images/images/([^)\s"\'\]]+)'

    def fix_double_images(match):
        filename = match.group(2)
        # Remove duplicate "images" directory
        new_path = f'/images/dev/stoplight.io/images/{filename}'
        changes.append(f"  ✓ {match.group(0)} → {new_path}")
        return new_path

    updated_content = re.sub(pattern4, fix_double_images, updated_content)

    # Pattern 5: Relative paths to images/dev/stoplight.io/images (but not from portal)
    pattern5 = r'(\.\./)+images/dev/stoplight\.io/images/([^)\s"\'\]]+)'

    def fix_relative_stoplight(match):
        filename = Path(match.group(2)).name
        if filename in stoplight_images:
            new_path = f'/images/dev/stoplight.io/images/{filename}'
            changes.append(f"  ✓ {match.group(0)} → {new_path}")
            return new_path
        return match.group(0)

    updated_content = re.sub(pattern5, fix_relative_stoplight, updated_content)

    # Pattern 6: Fix paths like ../../../../../assets/images/
    pattern6 = r'\.\.(/\.\.)+/assets/images/([^)\s"\'\]]+)'

    def fix_deep_relative(match):
        filename = match.group(2)
        if filename in stoplight_images:
            new_path = f'/images/dev/stoplight.io/images/{filename}'
            changes.append(f"  ✓ {match.group(0)} → {new_path}")
            return new_path
        return match.group(0)

    updated_content = re.sub(pattern6, fix_deep_relative, updated_content)

    return updated_content, changes


def process_file(filepath: Path, stoplight_images: Set[str], repo_root: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """
    Process a single MDX file to fix image paths.

    Returns:
        Tuple of (modified: bool, changes: List[str])
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    updated_content, changes = fix_image_paths_to_stoplight(original_content, stoplight_images, filepath, repo_root)

    if updated_content != original_content:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        return True, changes
    else:
        return False, []


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fix relative and incorrect image paths to stoplight directory'
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

    # Load stoplight images
    print("Loading stoplight images...")
    stoplight_images = load_stoplight_images(repo_root)
    print(f"Found {len(stoplight_images)} images in stoplight directory\n")

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
            modified, changes = process_file(filepath, stoplight_images, repo_root, dry_run=args.dry_run)

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

    # Save detailed log
    if not args.dry_run and modified_files:
        log_path = repo_root / 'scripts' / 'output' / 'relative_path_fixes.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(all_changes, f, indent=2, ensure_ascii=False)
        print(f"✓ Detailed log saved to {log_path}\n")

    if args.dry_run:
        print("\n⚠ This was a DRY RUN - no files were modified")
        print("  Run without --dry-run to apply changes")
    else:
        print("\n✓ Image paths have been updated!")
        print("\nNext steps:")
        print("1. Run: python scripts/validate_images.py")
        print("2. Verify broken images count decreased")
        print("3. Commit the changes")


if __name__ == '__main__':
    main()
