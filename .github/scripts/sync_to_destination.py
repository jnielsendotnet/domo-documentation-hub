#!/usr/bin/env python3
"""
Sync YAML files from source to destination directory.

This script:
1. Reads the list of changed YAML files
2. Copies YAML files from source to destination
3. Maintains the same filenames
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List


def sync_files(
    source_dir: str,
    destination_dir: str,
    changed_list_file: str
) -> List[str]:
    """
    Sync YAML files to destination

    Args:
        source_dir: Directory containing source YAML files
        destination_dir: Destination directory for YAML files
        changed_list_file: File containing list of changed YAML files

    Returns:
        List of synced files
    """
    synced_files = []

    if not os.path.exists(changed_list_file):
        print(f"Changed list file not found: {changed_list_file}")
        return synced_files

    with open(changed_list_file, 'r') as f:
        changed_yaml_files = [line.strip() for line in f if line.strip()]

    print(f"Syncing {len(changed_yaml_files)} files...")

    os.makedirs(destination_dir, exist_ok=True)

    for yaml_file in changed_yaml_files:
        yaml_filename = os.path.basename(yaml_file)
        dest_path = os.path.join(destination_dir, yaml_filename)

        if not os.path.exists(yaml_file):
            print(f"WARNING: Source file not found: {yaml_file}")
            continue

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(yaml_file, dest_path)
        print(f"SYNCED: {yaml_file} -> {dest_path}")
        synced_files.append(dest_path)

    return synced_files


def main():
    parser = argparse.ArgumentParser(description='Sync YAML files to destination')
    parser.add_argument('--source', required=True, help='Source YAML directory')
    parser.add_argument('--destination', required=True, help='Destination directory for YAML files')
    parser.add_argument('--changed-list', required=True, help='File containing list of changed YAML files')

    args = parser.parse_args()

    synced_files = sync_files(args.source, args.destination, args.changed_list)

    print(f"\n{'='*60}")
    print(f"Sync complete: {len(synced_files)} file(s) synced")
    print(f"{'='*60}")

    for file in synced_files:
        print(f"  {file}")


if __name__ == "__main__":
    main()
