#!/usr/bin/env python3
"""
Analyze title handling across all portal MDX files.

This script scans all MDX files in the portal directory and analyzes:
- Frontmatter titles vs H1 headers
- Sidebar titles and their relationship to main titles
- Categorizes files for different migration strategies

Output files:
- title_analysis.json: Complete structured data for all files
- h1_migrations_needed.csv: Files where H1 differs from frontmatter
- h1_removals_only.txt: Files where H1 matches frontmatter
- no_h1_files.txt: Files without H1
- summary_stats.txt: Statistics and category counts
"""

import os
import re
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], int]:
    """
    Extract YAML frontmatter from MDX content.

    Returns:
        Tuple of (frontmatter_dict, end_line_number)
    """
    if not content.startswith('---'):
        return None, 0

    # Find the closing ---
    lines = content.split('\n')
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, 0

    # Extract and parse YAML
    yaml_content = '\n'.join(lines[1:end_idx])
    try:
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter, end_idx + 1
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
        return None, 0


def sanitize_h1_text(h1_line: str) -> str:
    """
    Remove Markdown formatting from H1 text.

    Handles:
    - Inline code: `text`
    - Bold: **text** or __text__
    - Italic: *text* or _text_
    - Links: [text](url)
    - HTML tags
    """
    text = h1_line.strip()

    # Remove leading # symbols
    text = re.sub(r'^#+\s*', '', text)

    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove bold and italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    return text.strip()


def find_first_h1(content: str, after_line: int) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Find the first H1 header after the frontmatter.

    Returns:
        Tuple of (h1_text, line_number, raw_h1_line)
    """
    lines = content.split('\n')

    # Skip frontmatter and look for H1
    in_code_block = False
    for i in range(after_line, len(lines)):
        line = lines[i]

        # Track code blocks to avoid H1s inside them
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for H1 (# at start of line)
        if re.match(r'^#\s+', line):
            h1_text = sanitize_h1_text(line)
            return h1_text, i + 1, line  # 1-indexed line number

    return None, None, None


def parse_mdx_file(filepath: Path) -> Dict:
    """
    Parse an MDX file and extract title information.

    Returns:
        Dictionary with file analysis data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter, fm_end_line = extract_frontmatter(content)

    if frontmatter is None:
        return {
            'filepath': str(filepath),
            'relative_path': str(filepath.relative_to(Path.cwd())),
            'error': 'No frontmatter found',
            'has_frontmatter': False
        }

    # Find first H1
    h1_text, h1_line_num, h1_raw = find_first_h1(content, fm_end_line)

    # Extract frontmatter fields
    fm_title = frontmatter.get('title', '')
    fm_sidebar = frontmatter.get('sidebarTitle', '')
    fm_permalink = frontmatter.get('permalink', '')
    fm_stoplight_id = frontmatter.get('stoplight-id', '')

    # Determine if H1 matches title
    h1_matches_title = False
    if h1_text and fm_title:
        h1_matches_title = h1_text.strip().lower() == fm_title.strip().lower()

    # Determine if sidebar matches title
    sidebar_matches_title = False
    if fm_sidebar and fm_title:
        sidebar_matches_title = fm_sidebar.strip().lower() == fm_title.strip().lower()

    return {
        'filepath': str(filepath),
        'relative_path': str(filepath.relative_to(Path.cwd())),
        'has_frontmatter': True,
        'frontmatter': {
            'title': fm_title,
            'sidebarTitle': fm_sidebar,
            'permalink': fm_permalink,
            'stoplight_id': fm_stoplight_id
        },
        'h1': {
            'text': h1_text,
            'line_number': h1_line_num,
            'raw': h1_raw,
            'exists': h1_text is not None
        },
        'analysis': {
            'h1_matches_title': h1_matches_title,
            'sidebar_matches_title': sidebar_matches_title,
            'has_sidebar_title': bool(fm_sidebar)
        }
    }


def classify_file(file_data: Dict) -> str:
    """
    Classify file into migration categories.

    Categories:
    - A: Has H1 that differs from frontmatter title (needs migration)
    - B: Has H1 that matches frontmatter title (just remove H1)
    - C: No H1 found (keep existing title, manual review)
    - D: Error or invalid
    """
    if not file_data.get('has_frontmatter'):
        return 'D'

    if not file_data['h1']['exists']:
        return 'C'

    if file_data['analysis']['h1_matches_title']:
        return 'B'

    return 'A'


def generate_reports(all_files: List[Dict], output_dir: Path):
    """
    Generate all output reports.
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Classify files
    categories = {'A': [], 'B': [], 'C': [], 'D': []}
    for file_data in all_files:
        category = classify_file(file_data)
        categories[category].append(file_data)

    # 1. Complete JSON output
    json_path = output_dir / 'title_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_files, f, indent=2, ensure_ascii=False)
    print(f"✓ Wrote {json_path}")

    # 2. CSV for H1 migrations needed (Category A)
    csv_path = output_dir / 'h1_migrations_needed.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File Path', 'Current Title', 'H1 Title', 'Current Sidebar', 'Permalink', 'H1 Line'])
        for file_data in categories['A']:
            writer.writerow([
                file_data['relative_path'],
                file_data['frontmatter']['title'],
                file_data['h1']['text'],
                file_data['frontmatter']['sidebarTitle'],
                file_data['frontmatter']['permalink'],
                file_data['h1']['line_number']
            ])
    print(f"✓ Wrote {csv_path} ({len(categories['A'])} files)")

    # 3. List of files where H1 matches (Category B)
    txt_path = output_dir / 'h1_removals_only.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("Files where H1 matches frontmatter title (just remove H1):\n\n")
        for file_data in categories['B']:
            f.write(f"{file_data['relative_path']} (line {file_data['h1']['line_number']})\n")
    print(f"✓ Wrote {txt_path} ({len(categories['B'])} files)")

    # 4. List of files without H1 (Category C)
    no_h1_path = output_dir / 'no_h1_files.txt'
    with open(no_h1_path, 'w', encoding='utf-8') as f:
        f.write("Files without H1 header (manual review needed):\n\n")
        for file_data in categories['C']:
            f.write(f"{file_data['relative_path']}\n")
            f.write(f"  Current title: {file_data['frontmatter']['title']}\n\n")
    print(f"✓ Wrote {no_h1_path} ({len(categories['C'])} files)")

    # 5. Summary statistics
    stats_path = output_dir / 'summary_stats.txt'
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("TITLE ANALYSIS SUMMARY\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total files scanned: {len(all_files)}\n\n")

        f.write("CATEGORY BREAKDOWN:\n")
        f.write(f"  Category A (H1 differs, needs migration): {len(categories['A'])}\n")
        f.write(f"  Category B (H1 matches, just remove): {len(categories['B'])}\n")
        f.write(f"  Category C (No H1, manual review): {len(categories['C'])}\n")
        f.write(f"  Category D (Errors/Invalid): {len(categories['D'])}\n\n")

        # Calculate percentages
        total = len(all_files)
        f.write("PERCENTAGES:\n")
        f.write(f"  Files with H1: {(len(categories['A']) + len(categories['B'])) / total * 100:.1f}%\n")
        f.write(f"  Files without H1: {len(categories['C']) / total * 100:.1f}%\n")
        f.write(f"  Files needing title migration: {len(categories['A']) / total * 100:.1f}%\n\n")

        # Sidebar title analysis
        files_with_sidebar = sum(1 for f in all_files if f.get('frontmatter', {}).get('sidebarTitle'))
        sidebar_matches = sum(1 for f in all_files if f.get('analysis', {}).get('sidebar_matches_title'))

        f.write("SIDEBAR TITLE ANALYSIS:\n")
        f.write(f"  Files with sidebarTitle: {files_with_sidebar}\n")
        f.write(f"  Redundant sidebar titles (match main title): {sidebar_matches}\n\n")

        f.write("=" * 60 + "\n")
        f.write("NEXT STEPS:\n")
        f.write("=" * 60 + "\n")
        f.write("1. Review h1_migrations_needed.csv for files needing title updates\n")
        f.write("2. Review no_h1_files.txt for files needing manual attention\n")
        f.write("3. Run generate_sidebar_titles.py to create AI recommendations\n")
        f.write("4. Test migrate_titles.py on a small batch\n")

    print(f"✓ Wrote {stats_path}")

    # Print summary to console
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total files: {len(all_files)}")
    print(f"Category A (needs migration): {len(categories['A'])}")
    print(f"Category B (remove H1 only): {len(categories['B'])}")
    print(f"Category C (no H1): {len(categories['C'])}")
    print(f"Category D (errors): {len(categories['D'])}")
    print("=" * 60)


def main():
    """Main execution function."""
    # Find portal directory
    portal_dir = Path.cwd() / 'portal'

    if not portal_dir.exists():
        print(f"Error: Portal directory not found at {portal_dir}")
        return

    print(f"Scanning MDX files in {portal_dir}...")

    # Find all MDX files
    mdx_files = list(portal_dir.rglob('*.mdx')) + list(portal_dir.rglob('*.yaml'))
    print(f"Found {len(mdx_files)} MDX/YAML files\n")

    # Parse all files
    all_files = []
    for i, filepath in enumerate(mdx_files, 1):
        if i % 50 == 0:
            print(f"Processing file {i}/{len(mdx_files)}...")

        try:
            file_data = parse_mdx_file(filepath)
            all_files.append(file_data)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            all_files.append({
                'filepath': str(filepath),
                'relative_path': str(filepath.relative_to(Path.cwd())),
                'error': str(e),
                'has_frontmatter': False
            })

    print(f"\nProcessed {len(all_files)} files")

    # Generate reports
    output_dir = Path.cwd() / 'scripts' / 'update_frontmatter' / 'output'
    print(f"\nGenerating reports in {output_dir}...")
    generate_reports(all_files, output_dir)

    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
