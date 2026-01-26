#!/usr/bin/env python3
"""
Update portal files with proper frontmatter
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    exit(1)


def load_mapping(mapping_file: Path) -> Dict[str, Dict[str, str]]:
    """Load the stoplight-id mapping"""
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_analysis(analysis_file: Path) -> Dict[str, Dict[str, Any]]:
    """Load the file analysis"""
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def determine_title(
    file_info: Dict[str, Any],
    mapping: Dict[str, Dict[str, str]]
) -> str:
    """
    Determine the best title for a file.

    Priority:
    1. Label from docs.json mapping (most authoritative)
    2. Existing title in frontmatter (if present)
    3. H1 heading from file content
    4. Title inferred from path/filename
    """
    stoplight_id = file_info.get('stoplight_id')

    # Priority 1: docs.json label
    if stoplight_id and stoplight_id in mapping:
        return mapping[stoplight_id]['label']

    # Priority 2: Existing frontmatter title
    if file_info.get('current_frontmatter') and 'title' in file_info['current_frontmatter']:
        return file_info['current_frontmatter']['title']

    # Priority 3: H1 heading
    if file_info.get('h1_title'):
        return file_info['h1_title']

    # Priority 4: Infer from mapping or filename
    if stoplight_id and stoplight_id in mapping:
        return mapping[stoplight_id]['title_from_path']

    # Last resort: use filename
    filepath = Path(file_info['absolute_path'])
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


def generate_permalink(
    stoplight_id: Optional[str],
    title: str
) -> str:
    """Generate permalink from stoplight-id and title"""
    if not stoplight_id:
        # If no stoplight-id, use just kebab-case title
        kebab_title = title.lower().replace(' ', '-').replace('_', '-')
        kebab_title = re.sub(r'[^a-z0-9-]', '', kebab_title)
        return kebab_title

    # Standard format: {stoplight_id}-{kebab-case-title}
    kebab_title = title.lower().replace(' ', '-').replace('_', '-')
    # Remove any special characters
    kebab_title = re.sub(r'[^a-z0-9-]', '', kebab_title)
    # Remove multiple consecutive hyphens
    kebab_title = re.sub(r'-+', '-', kebab_title)
    # Remove leading/trailing hyphens
    kebab_title = kebab_title.strip('-')

    return f"{stoplight_id}-{kebab_title}"


def sanitize_title_for_yaml(title: str) -> str:
    """Sanitize title for safe YAML output"""
    # Remove markdown links [text](url) -> text
    title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)
    # Remove code backticks
    title = re.sub(r'`([^`]+)`', r'\1', title)
    # Remove extra whitespace
    title = ' '.join(title.split())
    return title


def build_new_frontmatter(
    file_info: Dict[str, Any],
    mapping: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """Build the new frontmatter dict"""
    title = determine_title(file_info, mapping)
    title = sanitize_title_for_yaml(title)

    stoplight_id = file_info.get('stoplight_id')
    permalink = generate_permalink(stoplight_id, title)

    # Start with existing frontmatter (preserve custom fields)
    new_fm = file_info.get('current_frontmatter', {}).copy() if file_info.get('current_frontmatter') else {}

    # Update/add required fields
    new_fm['title'] = title
    new_fm['permalink'] = permalink
    new_fm['sidebarTitle'] = title

    # Keep stoplight-id if exists
    if stoplight_id:
        new_fm['stoplight-id'] = stoplight_id

    return new_fm


def format_frontmatter_yaml(fm_dict: Dict[str, Any]) -> str:
    """Format frontmatter dict as YAML with proper formatting"""
    # Custom formatting for cleaner output
    lines = ['---']

    # Order: title, permalink, sidebarTitle, stoplight-id, then rest
    key_order = ['title', 'permalink', 'sidebarTitle', 'stoplight-id']

    for key in key_order:
        if key in fm_dict:
            value = fm_dict[key]
            if isinstance(value, str) and (' ' in value or ':' in value or value.startswith('#')):
                # Escape double quotes in value
                escaped_value = value.replace('"', '\\"')
                lines.append(f'{key}: "{escaped_value}"')
            else:
                lines.append(f'{key}: {value}')

    # Add remaining fields
    for key, value in fm_dict.items():
        if key not in key_order:
            if isinstance(value, str):
                escaped_value = value.replace('"', '\\"')
                lines.append(f'{key}: "{escaped_value}"')
            elif isinstance(value, list):
                lines.append(f'{key}: {json.dumps(value)}')
            else:
                lines.append(f'{key}: {value}')

    lines.append('---')
    return '\n'.join(lines)


def clean_internal_links(content: str) -> str:
    """
    Remove domain from /s/article references since docs live in same site now.
    Pattern: https://docs.domo.com/s/article/123 → /s/article/123
    """
    patterns = [
        (r'https?://docs\.domo\.com(/s/article/[^)\s\]"\']+)', r'\1'),
        (r'https?://[^/]+\.domo\.com(/s/article/[^)\s\]"\']+)', r'\1'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def update_file(
    filepath: Path,
    file_info: Dict[str, Any],
    mapping: Dict[str, Dict[str, str]],
    dry_run: bool = True
) -> bool:
    """
    Update a single file with new frontmatter.

    Returns True if file was updated, False otherwise.
    """
    # Read current content
    content = filepath.read_text(encoding='utf-8')

    # Build new frontmatter
    new_fm = build_new_frontmatter(file_info, mapping)
    new_fm_yaml = format_frontmatter_yaml(new_fm)

    # Remove existing frontmatter if present
    fm_pattern = re.compile(r'^---\s*\n.*?\n---\s*\n', re.DOTALL)
    content_body = fm_pattern.sub('', content, count=1)

    # Clean internal links in content body
    content_body = clean_internal_links(content_body)

    # Combine new frontmatter with content
    new_content = new_fm_yaml + '\n' + content_body

    if dry_run:
        print(f"\n{'='*70}")
        print(f"File: {filepath}")
        print(f"{'='*70}")
        print("New frontmatter:")
        print(new_fm_yaml)
        print(f"{'='*70}\n")
        return False
    else:
        # Write updated content
        filepath.write_text(new_content, encoding='utf-8')
        return True


def main():
    parser = argparse.ArgumentParser(description='Update portal file frontmatter')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--limit', type=int, help='Limit number of files to update')
    args = parser.parse_args()

    # Load data
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'output'

    mapping_file = output_dir / 'mapping_output.json'
    analysis_file = output_dir / 'file_analysis.json'

    if not mapping_file.exists():
        print(f"Error: {mapping_file} not found. Run 01_build_mapping.py first.")
        sys.exit(1)

    if not analysis_file.exists():
        print(f"Error: {analysis_file} not found. Run 02_scan_files.py first.")
        sys.exit(1)

    print("Loading mapping and analysis...")
    mapping = load_mapping(mapping_file)
    analysis = load_analysis(analysis_file)

    # Filter files that need update
    files_to_update = {
        path: info for path, info in analysis.items()
        if info['needs_update']
    }

    print(f"\nFiles to update: {len(files_to_update)}")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    # Update files
    updated_count = 0
    for i, (path, info) in enumerate(sorted(files_to_update.items())):
        if args.limit and i >= args.limit:
            break

        filepath = Path(info['absolute_path'])
        success = update_file(filepath, info, mapping, dry_run=args.dry_run)
        if success:
            updated_count += 1
            print(f"Updated: {path}")

    if not args.dry_run:
        print(f"\nUpdate complete! Updated {updated_count} files.")
    else:
        print(f"\nDry run complete. Would update {min(len(files_to_update), args.limit) if args.limit else len(files_to_update)} files.")
        print("Run without --dry-run to apply changes.")

    return 0


if __name__ == '__main__':
    exit(main())
