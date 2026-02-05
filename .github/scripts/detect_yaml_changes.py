#!/usr/bin/env python3
"""
Detect changed YAML files in source repository.

This script:
1. Compares source YAML files with destination YAML files
2. Checks file modification times
3. Outputs list of files that need syncing
4. Creates summary of changes
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


def find_yaml_files(source_dir: str) -> List[str]:
    """Find all YAML files in source directory"""
    yaml_files = []
    source_path = Path(source_dir)

    for ext in ['*.yaml', '*.yml']:
        yaml_files.extend(source_path.glob(f"**/{ext}"))

    return [str(f) for f in yaml_files]


def detect_changes(
    source_dir: str,
    dest_dir: str,
    force: bool = False
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Detect which YAML files need syncing

    Returns:
        Tuple of (changed_files, summary_dict)
    """
    changed_files = []
    summary = {
        "new_files": [],
        "modified_files": [],
        "unchanged_files": []
    }

    yaml_files = find_yaml_files(source_dir)
    print(f"Found {len(yaml_files)} YAML files in source")

    for yaml_file in yaml_files:
        yaml_filename = os.path.basename(yaml_file)
        dest_file_path = os.path.join(dest_dir, yaml_filename)

        if not os.path.exists(dest_file_path):
            print(f"NEW: {yaml_filename}")
            changed_files.append(yaml_file)
            summary["new_files"].append(yaml_filename)
            continue

        if force:
            print(f"FORCE: {yaml_filename}")
            changed_files.append(yaml_file)
            summary["modified_files"].append(yaml_filename)
            continue

        source_mtime = os.path.getmtime(yaml_file)
        dest_mtime = os.path.getmtime(dest_file_path)

        if source_mtime > dest_mtime:
            print(f"MODIFIED: {yaml_filename} (source newer than destination)")
            changed_files.append(yaml_file)
            summary["modified_files"].append(yaml_filename)
        else:
            print(f"UNCHANGED: {yaml_filename}")
            summary["unchanged_files"].append(yaml_filename)

    return changed_files, summary


def create_summary_markdown(summary: Dict[str, List[str]]) -> str:
    """Create markdown summary of changes"""
    lines = []

    total_changes = len(summary["new_files"]) + len(summary["modified_files"])
    lines.append(f"**Total files to sync:** {total_changes}")
    lines.append("")

    if summary["new_files"]:
        lines.append(f"**New Files ({len(summary['new_files'])}):**")
        for f in summary["new_files"]:
            lines.append(f"- `{f}`")
        lines.append("")

    if summary["modified_files"]:
        lines.append(f"**Modified Files ({len(summary['modified_files'])}):**")
        for f in summary["modified_files"]:
            lines.append(f"- `{f}`")
        lines.append("")

    if summary["unchanged_files"]:
        lines.append(f"**Unchanged Files ({len(summary['unchanged_files'])}):**")
        lines.append(f"_{len(summary['unchanged_files'])} files are already up-to-date_")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Detect changed YAML files')
    parser.add_argument('--source', required=True, help='Source directory with YAML files')
    parser.add_argument('--dest', required=True, help='Destination directory with YAML files')
    parser.add_argument('--force', default='false', help='Force sync all files')

    args = parser.parse_args()
    force = args.force.lower() == 'true'

    changed_files, summary = detect_changes(args.source, args.dest, force=force)

    # Write changed files list
    with open('changed_files.txt', 'w') as f:
        for file_path in changed_files:
            f.write(f"{file_path}\n")

    # Write outputs for GitHub Actions
    changed_files_str = "\n".join(changed_files)
    output_file = os.environ.get('GITHUB_OUTPUT', '/dev/stdout')
    with open(output_file, 'a') as f:
        f.write(f"changed_files<<EOF\n{changed_files_str}\nEOF\n")

    summary_md = create_summary_markdown(summary)
    with open(output_file, 'a') as f:
        f.write(f"summary<<EOF\n{summary_md}\nEOF\n")

    print(f"\n{'='*60}")
    print(f"Detection complete: {len(changed_files)} files to sync")
    print(f"{'='*60}")

    sys.exit(0 if changed_files else 1)


if __name__ == "__main__":
    main()
