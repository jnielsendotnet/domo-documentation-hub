#!/usr/bin/env python3
"""
Detect changes between mapped source and migrated files.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
MIGRATED_REPO = SCRIPT_DIR.parent.parent
SOURCE_REPO = MIGRATED_REPO.parent / "domo-developer-portal"

def load_mapping():
    """Load file mapping."""
    mapping_file = OUTPUT_DIR / "file_mapping.json"

    if not mapping_file.exists():
        print("ERROR: Mapping file not found. Run create_mapping.py first.")
        exit(1)

    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_git_history(repo_path, file_path, since_date="2025-07-01"):
    """Get git history for a file since a specific date."""
    try:
        cmd = [
            'git', '-C', str(repo_path),
            'log', f'--since={since_date}',
            '--pretty=format:%H|%ad|%s', '--date=short',
            '--', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        if not result.stdout:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({
                        'hash': parts[0],
                        'date': parts[1],
                        'message': parts[2]
                    })
        return commits
    except Exception as e:
        return []

def categorize_change(source_item, migrated_item, source_commits):
    """Categorize the type of change between source and migrated files."""
    source_hash = source_item.get('content_hash')
    migrated_hash = migrated_item.get('content_hash')

    # Check if content is identical
    if source_hash and migrated_hash and source_hash == migrated_hash:
        return 'unchanged', 'Content is identical'

    # Check if file was modified since July 2025
    if source_commits:
        commit_count = len(source_commits)
        latest_commit = source_commits[0] if source_commits else None

        # Determine magnitude based on commit count and messages
        major_keywords = ['feat', 'breaking', 'major', 'rewrite', 'refactor']
        minor_keywords = ['fix', 'update', 'docs', 'chore', 'style']

        has_major = any(
            any(keyword in commit['message'].lower() for keyword in major_keywords)
            for commit in source_commits
        )

        if has_major or commit_count > 5:
            return 'major_update', f'{commit_count} commits since July 2025, includes major changes'
        elif commit_count > 0:
            return 'minor_update', f'{commit_count} commits since July 2025'

    # If no commits but hashes differ, content diverged at some point
    if source_hash != migrated_hash:
        return 'content_diff', 'Content differs but no recent git history'

    return 'unknown', 'Unable to determine change type'

def analyze_new_files(ambiguous_files):
    """Analyze files that don't have a mapping (genuinely new)."""
    new_files = []

    for source_item in ambiguous_files:
        source_path = source_item.get('path', '')
        commits = get_git_history(SOURCE_REPO, source_path)

        # Check if file was added since July 2025
        is_new = False
        added_date = None

        if commits:
            # Check if this is a new file (has an "Add" or "feat" commit)
            for commit in reversed(commits):  # Check oldest first
                if any(keyword in commit['message'].lower() for keyword in ['add', 'feat', 'create', 'new']):
                    is_new = True
                    added_date = commit['date']
                    break

        new_files.append({
            'source': source_item,
            'is_new': is_new,
            'added_date': added_date,
            'commits': commits
        })

    return new_files

def main():
    """Main execution."""
    print("=" * 60)
    print("Detecting Changes Between Repositories")
    print("=" * 60)

    # Load mapping
    mapping = load_mapping()

    print(f"\nAnalyzing {len(mapping['mapped'])} mapped files...")

    # Analyze mapped files
    changes = {
        'new': [],
        'major_update': [],
        'minor_update': [],
        'content_diff': [],
        'unchanged': [],
        'unknown': []
    }

    for idx, mapped_item in enumerate(mapping['mapped'], 1):
        source = mapped_item['source']
        migrated = mapped_item['migrated']
        source_path = source.get('path', '')

        print(f"\r  Processing: {idx}/{len(mapping['mapped'])}", end='', flush=True)

        # Get git history for source file
        commits = get_git_history(SOURCE_REPO, source_path)

        # Categorize change
        change_type, reason = categorize_change(source, migrated, commits)

        # Store change record
        change_record = {
            'stoplight_id': mapped_item.get('stoplight_id'),
            'source_path': source_path,
            'migrated_path': migrated.get('path', ''),
            'confidence': mapped_item.get('confidence', 'unknown'),
            'match_method': mapped_item.get('match_method', 'unknown'),
            'change_type': change_type,
            'reason': reason,
            'commit_count': len(commits),
            'latest_commit': commits[0] if commits else None,
            'commits': commits[:5]  # Store up to 5 most recent commits
        }

        changes[change_type].append(change_record)

    print()  # New line after progress

    # Analyze new files (ambiguous/unmapped)
    print(f"\nAnalyzing {len(mapping.get('ambiguous', []))} potentially new files...")
    new_files_analysis = analyze_new_files(mapping.get('ambiguous', []))

    # Filter for genuinely new files
    genuinely_new = [item for item in new_files_analysis if item['is_new']]
    changes['new'] = genuinely_new

    # Build final output
    changes_output = {
        'summary': {
            'total_analyzed': len(mapping['mapped']),
            'new_files': len(changes['new']),
            'major_updates': len(changes['major_update']),
            'minor_updates': len(changes['minor_update']),
            'content_diff': len(changes['content_diff']),
            'unchanged': len(changes['unchanged']),
            'unknown': len(changes['unknown'])
        },
        'changes': changes
    }

    # Save changes
    output_file = OUTPUT_DIR / "changes_detected.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(changes_output, f, indent=2)

    print(f"\n" + "=" * 60)
    print("Change Detection Summary")
    print("=" * 60)
    print(f"Total analyzed: {changes_output['summary']['total_analyzed']}")
    print(f"\nNew files: {changes_output['summary']['new_files']}")
    print(f"Major updates: {changes_output['summary']['major_updates']}")
    print(f"Minor updates: {changes_output['summary']['minor_updates']}")
    print(f"Content differs: {changes_output['summary']['content_diff']}")
    print(f"Unchanged: {changes_output['summary']['unchanged']}")
    print(f"Unknown: {changes_output['summary']['unknown']}")

    print(f"\nChanges saved to: {output_file}")
    print("\nNext: Run generate_merge_list.py to create merge recommendations")

if __name__ == "__main__":
    main()
