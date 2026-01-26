#!/usr/bin/env python3
"""
Scan portal files and analyze current state
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    exit(1)


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Extract YAML frontmatter from markdown content.

    Returns: (frontmatter_dict, content_without_frontmatter)
    """
    # Match frontmatter block
    fm_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = fm_pattern.match(content)

    if match:
        try:
            fm_yaml = match.group(1)
            fm_dict = yaml.safe_load(fm_yaml) or {}
            content_without_fm = content[match.end():]
            return fm_dict, content_without_fm
        except yaml.YAMLError as e:
            print(f"YAML parse error: {e}")
            return None, content

    return None, content


def extract_h1_title(content: str) -> Optional[str]:
    """Extract first H1 heading from markdown content"""
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return h1_match.group(1).strip() if h1_match else None


def extract_stoplight_from_filename(filename: str) -> Optional[str]:
    """Extract stoplight-id from filename like '6a5d7a2870145-getting-data.mdx'"""
    match = re.match(r'^([a-z0-9]+)-(.+)\.(md|mdx)$', filename)
    return match.group(1) if match else None


def scan_portal_files(portal_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Scan all portal files and analyze their state"""
    analysis = {}

    # Scan .md files
    for filepath in portal_dir.rglob('*.md'):
        scan_file(filepath, analysis, portal_dir)

    # Scan .mdx files
    for filepath in portal_dir.rglob('*.mdx'):
        scan_file(filepath, analysis, portal_dir)

    return analysis


def scan_file(filepath: Path, analysis: Dict, portal_dir: Path):
    """Scan a single file and add to analysis"""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Extract frontmatter
    frontmatter, content_body = extract_frontmatter(content)

    # Extract H1
    h1_title = extract_h1_title(content_body)

    # Get stoplight-id from frontmatter or filename
    stoplight_id = None
    if frontmatter and 'stoplight-id' in frontmatter:
        stoplight_id = frontmatter['stoplight-id']
    else:
        stoplight_id = extract_stoplight_from_filename(filepath.name)

    # Determine if update needed
    needs_update = False
    update_reason = []

    if frontmatter:
        if 'title' not in frontmatter:
            needs_update = True
            update_reason.append('missing title')
        if 'permalink' not in frontmatter:
            needs_update = True
            update_reason.append('missing permalink')
        if 'sidebarTitle' not in frontmatter:
            needs_update = True
            update_reason.append('missing sidebarTitle')
    else:
        needs_update = True
        update_reason.append('no frontmatter')

    # Store analysis - use relative path from portal directory
    try:
        rel_path = str(filepath.relative_to(portal_dir))
    except ValueError:
        # If file is not under portal_dir, use full relative path from repo root
        rel_path = str(filepath)

    analysis[rel_path] = {
        'absolute_path': str(filepath),
        'has_frontmatter': frontmatter is not None,
        'stoplight_id': stoplight_id,
        'current_frontmatter': frontmatter,
        'h1_title': h1_title,
        'needs_update': needs_update,
        'update_reason': ', '.join(update_reason) if update_reason else None
    }


def main():
    repo_root = Path(__file__).parent.parent.parent
    portal_dir = repo_root / 'portal'
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)

    if not portal_dir.exists():
        print(f"Error: {portal_dir} not found")
        return 1

    print(f"Scanning files in {portal_dir}...")
    analysis = scan_portal_files(portal_dir)

    # Save analysis
    output_file = output_dir / 'file_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    # Generate summary
    total = len(analysis)
    needs_update = sum(1 for f in analysis.values() if f['needs_update'])
    has_stoplight = sum(1 for f in analysis.values() if f['stoplight_id'])
    no_frontmatter = sum(1 for f in analysis.values() if not f['has_frontmatter'])

    print(f"\nScan complete!")
    print(f"  Total files: {total}")
    print(f"  Needs update: {needs_update}")
    print(f"  Has stoplight-id: {has_stoplight}")
    print(f"  No frontmatter: {no_frontmatter}")
    print(f"  Output: {output_file}")

    # Generate report
    report_file = output_dir / 'scan_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Portal Files Scan Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total files: {total}\n")
        f.write(f"Files needing update: {needs_update}\n")
        f.write(f"Files with stoplight-id: {has_stoplight}\n")
        f.write(f"Files without frontmatter: {no_frontmatter}\n\n")

        f.write("\nFiles Needing Update:\n")
        f.write("-" * 70 + "\n")
        for path, info in sorted(analysis.items()):
            if info['needs_update']:
                f.write(f"\n{path}\n")
                f.write(f"  Stoplight ID: {info['stoplight_id']}\n")
                f.write(f"  H1 Title: {info['h1_title']}\n")
                f.write(f"  Reason: {info['update_reason']}\n")

    print(f"  Report: {report_file}")

    return 0


if __name__ == '__main__':
    exit(main())
