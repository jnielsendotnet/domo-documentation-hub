#!/usr/bin/env python3
"""
Migrate H1 titles to frontmatter and apply sidebar title recommendations.

This script performs the actual title cleanup:
1. Migrates H1 headers to frontmatter title field
2. Applies AI-generated sidebar titles (if available)
3. Removes redundant H1 headers from content
4. Removes redundant sidebar titles

Features:
- Dry-run mode for preview
- Batch processing by directory or count
- Detailed logging
- Validation
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import shutil
import re


def load_analysis() -> Dict:
    """Load the title analysis from Phase 1."""
    analysis_path = Path('scripts/update_frontmatter/output/title_analysis.json')

    if not analysis_path.exists():
        raise FileNotFoundError(
            f"Analysis file not found at {analysis_path}. "
            "Please run analyze_titles.py first."
        )

    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert list to dict keyed by relative_path
    return {item['relative_path']: item for item in data}


def load_recommendations() -> Optional[Dict]:
    """Load AI-generated sidebar title recommendations from Phase 2."""
    rec_path = Path('scripts/update_frontmatter/output/sidebar_title_recommendations.json')

    if not rec_path.exists():
        return None

    with open(rec_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_frontmatter_raw(content: str) -> Tuple[Optional[str], Optional[str], int]:
    """
    Extract YAML frontmatter as raw text, preserving formatting.

    Returns:
        Tuple of (frontmatter_text, frontmatter_dict, end_line_number)
    """
    if not content.startswith('---'):
        return None, None, 0

    lines = content.split('\n')
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return None, None, 0

    # Extract YAML content
    yaml_content = '\n'.join(lines[1:end_idx])

    try:
        frontmatter_dict = yaml.safe_load(yaml_content)
        return yaml_content, frontmatter_dict, end_idx + 1
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
        return None, None, 0


def serialize_frontmatter(fm_dict: Dict) -> str:
    """
    Serialize frontmatter dict to YAML string.

    Handles special characters and maintains field order.
    """
    # Use yaml.dump with proper configuration
    yaml_str = yaml.dump(
        fm_dict,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000,  # Prevent line wrapping
    )

    # Handle special characters that need quoting
    lines = []
    for line in yaml_str.split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            value = value.strip()

            # Quote values with special characters if not already quoted
            if value and not (value.startswith('"') or value.startswith("'")):
                if any(char in value for char in [':', '#', '[', ']', '{', '}', '&', '*', '!', '|', '>', '@', '`']):
                    # Escape double quotes in value
                    value = value.replace('"', '\\"')
                    line = f"{key}: \"{value}\""

        lines.append(line)

    return '\n'.join(lines)


def update_frontmatter(fm_dict: Dict, new_title: Optional[str], new_sidebar: Optional[str], remove_sidebar: bool = False) -> Dict:
    """
    Update frontmatter with new title and sidebar title.

    Args:
        fm_dict: Original frontmatter dictionary
        new_title: New title to set (from H1)
        new_sidebar: New sidebar title (from AI recommendations)
        remove_sidebar: If True, remove sidebarTitle field

    Returns:
        Updated frontmatter dictionary
    """
    updated = fm_dict.copy()

    # Update title if provided
    if new_title:
        updated['title'] = new_title

    # Handle sidebar title
    if remove_sidebar:
        # Remove redundant sidebar title
        updated.pop('sidebarTitle', None)
    elif new_sidebar:
        # Add or update sidebar title
        updated['sidebarTitle'] = new_sidebar
    # If neither remove_sidebar nor new_sidebar, keep existing

    return updated


def remove_h1_line(content: str, line_num: int) -> str:
    """
    Remove the H1 line at the specified line number.

    Args:
        content: Full file content
        line_num: 1-indexed line number to remove

    Returns:
        Content with H1 line removed
    """
    lines = content.split('\n')

    # Convert to 0-indexed
    idx = line_num - 1

    if 0 <= idx < len(lines):
        # Remove the line
        del lines[idx]

        # Also remove trailing blank line if it exists
        if idx < len(lines) and lines[idx].strip() == '':
            del lines[idx]

    return '\n'.join(lines)


def migrate_file_title(
    filepath: str,
    analysis_data: Dict,
    recommendations: Optional[Dict],
    skip_ai: bool = False,
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Migrate title for a single file.

    Returns:
        Tuple of (success, message)
    """
    file_info = analysis_data.get(filepath)
    if not file_info:
        return False, "File not found in analysis"

    # Skip files without frontmatter
    if not file_info.get('has_frontmatter'):
        return False, "No frontmatter"

    # Determine what to do based on category
    h1_exists = file_info['h1']['exists']
    h1_text = file_info['h1'].get('text')
    h1_line = file_info['h1'].get('line_number')
    h1_matches_title = file_info['analysis'].get('h1_matches_title', False)

    current_title = file_info['frontmatter']['title']
    current_sidebar = file_info['frontmatter'].get('sidebarTitle', '')

    # Determine new title and whether to remove H1
    new_title = None
    remove_h1 = False
    update_needed = False

    if h1_exists:
        if not h1_matches_title:
            # Category A: H1 differs - migrate title
            new_title = h1_text
            remove_h1 = True
            update_needed = True
        else:
            # Category B: H1 matches - just remove H1
            remove_h1 = True
            update_needed = True
    else:
        # Category C: No H1 - check for redundant sidebar title
        if current_sidebar and current_sidebar.strip().lower() == current_title.strip().lower():
            update_needed = True

    # Get AI recommendation for sidebar title
    new_sidebar = None
    remove_sidebar = False

    if not skip_ai and recommendations and filepath in recommendations:
        rec_data = recommendations[filepath]
        rec = rec_data.get('recommendation', {})

        if rec.get('needs_sidebar_title') and rec.get('sidebar_title'):
            new_sidebar = rec['sidebar_title']
            update_needed = True
        elif current_sidebar and current_title:
            # Check if current sidebar is redundant
            if current_sidebar.strip().lower() == current_title.strip().lower():
                remove_sidebar = True
                update_needed = True
    else:
        # No AI recommendations - check for redundant sidebar
        if current_sidebar and current_title:
            if current_sidebar.strip().lower() == current_title.strip().lower():
                remove_sidebar = True
                update_needed = True

    if not update_needed:
        return False, "No changes needed"

    # Load file content
    full_path = Path(filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Extract frontmatter
    fm_raw, fm_dict, fm_end_line = extract_frontmatter_raw(original_content)

    if fm_dict is None:
        return False, "Failed to parse frontmatter"

    # Update frontmatter
    updated_fm = update_frontmatter(fm_dict, new_title, new_sidebar, remove_sidebar)

    # Serialize updated frontmatter
    updated_fm_str = serialize_frontmatter(updated_fm)

    # Reconstruct file
    lines = original_content.split('\n')
    content_after_fm = '\n'.join(lines[fm_end_line:])

    new_content = f"---\n{updated_fm_str}\n---\n{content_after_fm}"

    # Remove H1 if needed
    if remove_h1 and h1_line:
        # Adjust line number since we've rebuilt the file
        # H1 line number is relative to original file
        # Need to calculate new position after frontmatter
        new_h1_line = h1_line - fm_end_line + updated_fm_str.count('\n') + 3  # +3 for --- lines

        # Actually, easier to just find and remove from content_after_fm
        content_lines = content_after_fm.split('\n')
        h1_idx_in_content = h1_line - fm_end_line - 1  # 0-indexed relative to content

        if 0 <= h1_idx_in_content < len(content_lines):
            del content_lines[h1_idx_in_content]

            # Remove trailing blank line if present
            if h1_idx_in_content < len(content_lines) and content_lines[h1_idx_in_content].strip() == '':
                del content_lines[h1_idx_in_content]

            content_after_fm = '\n'.join(content_lines)
            new_content = f"---\n{updated_fm_str}\n---\n{content_after_fm}"

    # Generate change summary
    changes = []
    if new_title:
        changes.append(f"Title: '{current_title}' → '{new_title}'")
    if new_sidebar:
        changes.append(f"Sidebar: '{current_sidebar}' → '{new_sidebar}'")
    if remove_sidebar:
        changes.append(f"Remove redundant sidebar: '{current_sidebar}'")
    if remove_h1:
        changes.append(f"Remove H1 at line {h1_line}")

    change_msg = "; ".join(changes)

    # Write file if not dry-run
    if not dry_run:
        # Create backup
        backup_path = full_path.with_suffix(full_path.suffix + '.backup')
        shutil.copy2(full_path, backup_path)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Remove backup if successful
            backup_path.unlink()

            return True, change_msg
        except Exception as e:
            # Restore from backup
            shutil.copy2(backup_path, full_path)
            backup_path.unlink()
            return False, f"Error writing file: {e}"
    else:
        return True, f"[DRY RUN] {change_msg}"


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Migrate H1 titles to frontmatter and apply sidebar recommendations'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--skip-ai',
        action='store_true',
        help='Skip applying AI-generated sidebar titles'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to process'
    )
    parser.add_argument(
        '--directory',
        help='Process only files in this directory (e.g., "Apps" or "API-Reference")'
    )
    parser.add_argument(
        '--category',
        choices=['A', 'B', 'C'],
        help='Process only files in specific category (A=migrate title, B=remove H1, C=no H1)'
    )

    args = parser.parse_args()

    # Load analysis
    print("Loading analysis data...")
    try:
        analysis_data = load_analysis()
        print(f"✓ Loaded analysis for {len(analysis_data)} files")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    # Load recommendations
    recommendations = None
    if not args.skip_ai:
        print("Loading AI recommendations...")
        recommendations = load_recommendations()
        if recommendations:
            print(f"✓ Loaded recommendations for {len(recommendations)} files")
        else:
            print("⚠ No AI recommendations found (run generate_sidebar_titles.py)")
            print("  Proceeding without AI sidebar titles (can use --skip-ai to suppress this warning)")

    # Filter files to process
    files_to_process = list(analysis_data.keys())

    # Apply filters
    if args.directory:
        dir_filter = f"portal/{args.directory}"
        files_to_process = [f for f in files_to_process if f.startswith(dir_filter)]
        print(f"Filtered to {len(files_to_process)} files in {args.directory}")

    if args.category:
        # Filter by category
        from analyze_titles import classify_file
        files_to_process = [
            f for f in files_to_process
            if classify_file(analysis_data[f]) == args.category
        ]
        print(f"Filtered to {len(files_to_process)} files in category {args.category}")

    if args.limit:
        files_to_process = files_to_process[:args.limit]
        print(f"Limited to {args.limit} files")

    if not files_to_process:
        print("No files to process!")
        return

    # Show mode
    mode_str = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"MODE: {mode_str}")
    print(f"Files to process: {len(files_to_process)}")
    print(f"{'='*60}\n")

    if not args.dry_run:
        response = input("Proceed with migration? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Process files
    results = {
        'success': [],
        'skipped': [],
        'errors': []
    }

    for i, filepath in enumerate(files_to_process, 1):
        print(f"[{i}/{len(files_to_process)}] Processing {filepath}...")

        success, message = migrate_file_title(
            filepath,
            analysis_data,
            recommendations,
            skip_ai=args.skip_ai,
            dry_run=args.dry_run
        )

        if success:
            results['success'].append((filepath, message))
            print(f"  ✓ {message}")
        elif "No changes needed" in message:
            results['skipped'].append((filepath, message))
            print(f"  - {message}")
        else:
            results['errors'].append((filepath, message))
            print(f"  ✗ {message}")

    # Print summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {len(results['success'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"{'='*60}\n")

    if results['errors']:
        print("ERRORS:")
        for filepath, message in results['errors']:
            print(f"  {filepath}: {message}")

    # Save detailed log
    log_dir = Path('scripts/update_frontmatter/output')
    log_path = log_dir / 'migration_log.json'

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Detailed log saved to {log_path}")

    if args.dry_run:
        print("\n⚠ This was a DRY RUN - no files were modified")
        print("  Run without --dry-run to apply changes")


if __name__ == '__main__':
    main()
