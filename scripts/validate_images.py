#!/usr/bin/env python3
"""
Validate image paths in MDX documentation files.

This script scans all MDX files and:
- Finds all image references (markdown and HTML)
- Checks if referenced files exist
- Identifies different path patterns (relative, absolute, URLs)
- Reports broken and valid image links

Output:
- image_validation_report.json: Detailed analysis
- broken_images.txt: List of broken image references
- image_summary.txt: Statistics and findings
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from urllib.parse import urlparse


def extract_images_from_mdx(content: str, filepath: Path) -> List[Dict]:
    """
    Extract all image references from MDX content.

    Finds:
    - Markdown: ![alt](path)
    - HTML: <img src="path" />
    - Next.js Image: <Image src="path" />

    Returns list of dicts with image info.
    """
    images = []

    # Pattern for markdown images: ![alt text](path "optional title")
    md_pattern = r'!\[([^\]]*)\]\(([^\s\)]+)(?:\s+"([^"]*)")?\)'

    for match in re.finditer(md_pattern, content):
        alt_text = match.group(1)
        image_path = match.group(2)
        title = match.group(3) or ''

        images.append({
            'type': 'markdown',
            'path': image_path,
            'alt': alt_text,
            'title': title,
            'line': content[:match.start()].count('\n') + 1
        })

    # Pattern for HTML img tags: <img src="path" ... />
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']([^>]*)/?>'

    for match in re.finditer(html_pattern, content, re.IGNORECASE):
        image_path = match.group(1)
        rest_of_tag = match.group(2)

        # Try to extract alt text
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', rest_of_tag)
        alt_text = alt_match.group(1) if alt_match else ''

        images.append({
            'type': 'html',
            'path': image_path,
            'alt': alt_text,
            'title': '',
            'line': content[:match.start()].count('\n') + 1
        })

    # Pattern for Next.js Image component: <Image src="path" ... />
    next_pattern = r'<Image[^>]+src=["\']([^"\']+)["\']([^>]*)/?>'

    for match in re.finditer(next_pattern, content):
        image_path = match.group(1)
        rest_of_tag = match.group(2)

        # Try to extract alt text
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', rest_of_tag)
        alt_text = alt_match.group(1) if alt_match else ''

        images.append({
            'type': 'next-image',
            'path': image_path,
            'alt': alt_text,
            'title': '',
            'line': content[:match.start()].count('\n') + 1
        })

    return images


def classify_image_path(image_path: str) -> str:
    """
    Classify the type of image path.

    Returns: 'url', 'absolute', 'relative', 'data-uri'
    """
    if image_path.startswith('data:'):
        return 'data-uri'

    parsed = urlparse(image_path)
    if parsed.scheme in ('http', 'https'):
        return 'url'

    if image_path.startswith('/'):
        return 'absolute'

    return 'relative'


def resolve_image_path(image_path: str, mdx_file: Path, repo_root: Path) -> Optional[Path]:
    """
    Resolve an image path to an actual file location.

    Args:
        image_path: The path from the MDX file
        mdx_file: Path to the MDX file containing the reference
        repo_root: Root of the repository

    Returns:
        Resolved Path or None if it's a URL/data-uri
    """
    path_type = classify_image_path(image_path)

    # Can't resolve URLs or data URIs
    if path_type in ('url', 'data-uri'):
        return None

    if path_type == 'absolute':
        # Absolute paths are relative to repo root
        # Remove leading slash
        rel_path = image_path.lstrip('/')
        return repo_root / rel_path

    # Relative path - resolve relative to MDX file location
    mdx_dir = mdx_file.parent
    resolved = (mdx_dir / image_path).resolve()

    return resolved


def check_image_exists(resolved_path: Optional[Path]) -> Tuple[bool, str]:
    """
    Check if an image file exists.

    Returns:
        Tuple of (exists: bool, reason: str)
    """
    if resolved_path is None:
        return True, "URL or data URI (cannot check)"

    if not resolved_path.exists():
        return False, "File not found"

    if not resolved_path.is_file():
        return False, "Path exists but is not a file"

    # Check if it's an image file by extension
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}
    if resolved_path.suffix.lower() not in image_extensions:
        return False, f"Not an image file (extension: {resolved_path.suffix})"

    return True, "OK"


def validate_images_in_file(filepath: Path, repo_root: Path) -> Dict:
    """
    Validate all images in a single MDX file.

    Returns dict with file info and image validation results.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    images = extract_images_from_mdx(content, filepath)

    validated_images = []
    for img in images:
        path_type = classify_image_path(img['path'])
        resolved_path = resolve_image_path(img['path'], filepath, repo_root)
        exists, reason = check_image_exists(resolved_path)

        validated_images.append({
            **img,
            'path_type': path_type,
            'resolved_path': str(resolved_path) if resolved_path else None,
            'exists': exists,
            'status': reason
        })

    return {
        'file': str(filepath.relative_to(repo_root)),
        'total_images': len(images),
        'images': validated_images
    }


def generate_reports(all_results: List[Dict], output_dir: Path):
    """Generate validation reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Full JSON report
    json_path = output_dir / 'image_validation_report.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"✓ Wrote {json_path}")

    # Collect statistics
    total_files = len(all_results)
    total_images = sum(r['total_images'] for r in all_results)

    broken_images = []
    valid_images = []
    url_images = []
    path_types = {'relative': 0, 'absolute': 0, 'url': 0, 'data-uri': 0}

    for result in all_results:
        for img in result['images']:
            path_types[img['path_type']] += 1

            if img['path_type'] in ('url', 'data-uri'):
                url_images.append({
                    'file': result['file'],
                    'path': img['path'],
                    'line': img['line'],
                    'type': img['path_type']
                })
            elif not img['exists']:
                broken_images.append({
                    'file': result['file'],
                    'path': img['path'],
                    'line': img['line'],
                    'status': img['status'],
                    'resolved_path': img['resolved_path']
                })
            else:
                valid_images.append({
                    'file': result['file'],
                    'path': img['path'],
                    'line': img['line']
                })

    # 2. Broken images list
    broken_path = output_dir / 'broken_images.txt'
    with open(broken_path, 'w', encoding='utf-8') as f:
        f.write("BROKEN IMAGE REFERENCES\n")
        f.write("=" * 80 + "\n\n")

        if not broken_images:
            f.write("✓ No broken images found!\n")
        else:
            for img in broken_images:
                f.write(f"File: {img['file']} (line {img['line']})\n")
                f.write(f"  Path: {img['path']}\n")
                f.write(f"  Status: {img['status']}\n")
                if img['resolved_path']:
                    f.write(f"  Resolved to: {img['resolved_path']}\n")
                f.write("\n")

    print(f"✓ Wrote {broken_path} ({len(broken_images)} broken images)")

    # 3. Summary statistics
    summary_path = output_dir / 'image_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("IMAGE VALIDATION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total files scanned: {total_files}\n")
        f.write(f"Total images found: {total_images}\n\n")

        f.write("IMAGE STATUS:\n")
        f.write(f"  ✓ Valid local images: {len(valid_images)}\n")
        f.write(f"  ✗ Broken images: {len(broken_images)}\n")
        f.write(f"  → External URLs: {len(url_images)}\n\n")

        f.write("PATH TYPES:\n")
        f.write(f"  Relative paths: {path_types['relative']}\n")
        f.write(f"  Absolute paths: {path_types['absolute']}\n")
        f.write(f"  External URLs: {path_types['url']}\n")
        f.write(f"  Data URIs: {path_types['data-uri']}\n\n")

        if broken_images:
            f.write("=" * 80 + "\n")
            f.write("ACTION REQUIRED\n")
            f.write("=" * 80 + "\n")
            f.write(f"Found {len(broken_images)} broken image references.\n")
            f.write("See broken_images.txt for details.\n\n")

        # Files with most images
        files_by_image_count = sorted(all_results, key=lambda x: x['total_images'], reverse=True)[:10]
        f.write("FILES WITH MOST IMAGES (top 10):\n")
        for r in files_by_image_count:
            if r['total_images'] > 0:
                f.write(f"  {r['file']}: {r['total_images']} images\n")

    print(f"✓ Wrote {summary_path}")

    # Print summary to console
    print("\n" + "=" * 80)
    print("IMAGE VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Total images: {total_images}")
    print(f"Valid: {len(valid_images)}")
    print(f"Broken: {len(broken_images)}")
    print(f"External URLs: {len(url_images)}")
    print("=" * 80)

    if broken_images:
        print(f"\n⚠️  WARNING: Found {len(broken_images)} broken image references!")
        print("   See broken_images.txt for details.")


def main():
    """Main execution function."""
    repo_root = Path.cwd()
    portal_dir = repo_root / 'portal'

    if not portal_dir.exists():
        print(f"Error: Portal directory not found at {portal_dir}")
        return

    print(f"Scanning MDX files in {portal_dir}...")
    mdx_files = list(portal_dir.rglob('*.mdx'))
    print(f"Found {len(mdx_files)} MDX files\n")

    # Validate images in all files
    all_results = []
    files_with_images = 0

    for i, filepath in enumerate(mdx_files, 1):
        if i % 50 == 0:
            print(f"Processing file {i}/{len(mdx_files)}...")

        try:
            result = validate_images_in_file(filepath, repo_root)
            all_results.append(result)

            if result['total_images'] > 0:
                files_with_images += 1
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print(f"\nProcessed {len(mdx_files)} files")
    print(f"Files containing images: {files_with_images}")

    # Generate reports
    output_dir = repo_root / 'scripts' / 'output'
    print(f"\nGenerating reports in {output_dir}...")
    generate_reports(all_results, output_dir)

    print("\n✓ Image validation complete!")


if __name__ == '__main__':
    main()
