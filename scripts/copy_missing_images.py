#!/usr/bin/env python3
"""
Find and copy missing images from domo-developer-portal to this repo.

This script:
1. Reads the broken images report
2. Checks if those images exist in ../domo-developer-portal/assets/images/
3. Copies found images to images/dev/stoplight.io/images/
4. Reports which images were found and which are truly missing
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Set


def load_broken_images(repo_root: Path) -> List[Dict]:
    """Load broken images from validation report."""
    report_path = repo_root / 'scripts/output/image_validation_report.json'

    with open(report_path, 'r') as f:
        data = json.load(f)

    broken = []
    for file_data in data:
        for img in file_data.get('images', []):
            if not img.get('exists'):
                path = img.get('path', '')
                # Skip API endpoints and empty paths
                if path and '/domo/avatars' not in path and 'web-assets.domo.com' not in path:
                    filename = Path(path).name
                    if filename and '.' in filename:  # Has extension
                        broken.append({
                            'filename': filename,
                            'mdx_file': file_data['file'],
                            'original_path': path
                        })

    return broken


def find_images_in_developer_portal(developer_portal_root: Path) -> Dict[str, Path]:
    """
    Find all images in domo-developer-portal.

    Returns dict mapping filename to full path.
    """
    images_dir = developer_portal_root / 'assets' / 'images'

    if not images_dir.exists():
        print(f"Warning: {images_dir} not found")
        return {}

    image_map = {}
    for img_file in images_dir.rglob('*'):
        if img_file.is_file() and img_file.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}:
            image_map[img_file.name] = img_file

    return image_map


def main():
    """Main execution function."""
    repo_root = Path.cwd()
    developer_portal_root = repo_root.parent / 'domo-developer-portal'

    if not developer_portal_root.exists():
        print(f"Error: domo-developer-portal not found at {developer_portal_root}")
        print("Expected directory structure:")
        print("  ../domo-developer-portal/")
        print("  ../domo-documentation-hub/")
        return

    print("Loading broken images report...")
    broken_images = load_broken_images(repo_root)

    # Get unique filenames
    unique_filenames = {}
    for item in broken_images:
        filename = item['filename']
        if filename not in unique_filenames:
            unique_filenames[filename] = []
        unique_filenames[filename].append(item)

    print(f"Found {len(unique_filenames)} unique broken image filenames")
    print(f"Referenced {len(broken_images)} times across documentation\n")

    print("Searching domo-developer-portal...")
    developer_images = find_images_in_developer_portal(developer_portal_root)
    print(f"Found {len(developer_images)} images in domo-developer-portal\n")

    # Find matches
    found_images = []
    not_found_images = []

    for filename in unique_filenames:
        if filename in developer_images:
            found_images.append({
                'filename': filename,
                'source_path': developer_images[filename],
                'references': unique_filenames[filename]
            })
        else:
            not_found_images.append({
                'filename': filename,
                'references': unique_filenames[filename]
            })

    print(f"✓ Found {len(found_images)} missing images in domo-developer-portal")
    print(f"✗ Still missing {len(not_found_images)} images\n")

    if found_images:
        print("Images that can be copied:")
        print("=" * 80)
        for item in found_images[:20]:
            print(f"  {item['filename']} ({len(item['references'])} references)")
        if len(found_images) > 20:
            print(f"  ... and {len(found_images) - 20} more")

        print(f"\n{'='*80}")
        response = input(f"Copy {len(found_images)} images to images/dev/stoplight.io/images/? (yes/no): ")

        if response.lower() == 'yes':
            target_dir = repo_root / 'images/dev/stoplight.io/images'
            target_dir.mkdir(parents=True, exist_ok=True)

            copied = 0
            skipped = 0

            for item in found_images:
                source = item['source_path']
                target = target_dir / item['filename']

                if target.exists():
                    print(f"  ⊘ {item['filename']} (already exists)")
                    skipped += 1
                else:
                    try:
                        shutil.copy2(source, target)
                        print(f"  ✓ {item['filename']}")
                        copied += 1
                    except Exception as e:
                        print(f"  ✗ {item['filename']}: {e}")

            print(f"\n{'='*80}")
            print(f"Copied: {copied}")
            print(f"Skipped: {skipped}")
            print(f"{'='*80}\n")

            print("Next steps:")
            print("1. Run: python scripts/validate_images.py")
            print("2. Verify broken images count decreased")
            print("3. Commit the new images")
        else:
            print("Aborted.")

    if not_found_images:
        print(f"\n{'='*80}")
        print("STILL MISSING")
        print(f"{'='*80}")
        print(f"{len(not_found_images)} images not found in domo-developer-portal:")
        for item in not_found_images[:30]:
            print(f"  {item['filename']} ({len(item['references'])} references)")
        if len(not_found_images) > 30:
            print(f"  ... and {len(not_found_images) - 30} more")

        # Save report
        missing_report_path = repo_root / 'scripts/output/truly_missing_images.json'
        with open(missing_report_path, 'w', encoding='utf-8') as f:
            json.dump(not_found_images, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved detailed report to {missing_report_path}")


if __name__ == '__main__':
    main()
