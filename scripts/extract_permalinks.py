#!/usr/bin/env python3
"""
Permalink to File Path Mapping Generator

Extracts permalink values from MDX file frontmatter in the /portal directory
and generates a JSON file mapping permalinks to their corresponding file paths.
"""

import re
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Set
from collections import defaultdict


class PermalinkExtractor:
    """Extracts permalinks from MDX files and generates redirect mappings."""

    def __init__(self, portal_dir: Path, exclude_archived: bool = True):
        self.portal_dir = portal_dir
        self.exclude_archived = exclude_archived
        self.redirects: List[Dict[str, str]] = []
        self.stats = {
            'total_files': 0,
            'files_with_permalinks': 0,
            'files_without_permalinks': 0,
            'skipped_same_source_destination': 0,
            'skipped_duplicate_source': 0,
            'skipped_archived': 0,
            'errors': 0
        }
        self.errors: List[str] = []
        self.skipped_files: List[str] = []
        self.permalink_map: Dict[str, List[str]] = defaultdict(list)
        self.source_map: Dict[str, Dict[str, str]] = {}  # Track source -> {destination, file_path}
        self.duplicate_resolutions: List[Dict] = []  # Track how duplicates were resolved

    def extract_permalink_from_frontmatter(self, content: str) -> Optional[str]:
        """
        Extract permalink value from YAML frontmatter.

        Args:
            content: File content string

        Returns:
            Permalink value without quotes, or None if not found
        """
        # Extract frontmatter block
        frontmatter_pattern = r'^---\s*\n(.*?)\n---'
        frontmatter_match = re.match(frontmatter_pattern, content, re.DOTALL)

        if not frontmatter_match:
            return None

        yaml_content = frontmatter_match.group(1)

        # Extract permalink (handles with/without quotes, stops at newline)
        permalink_pattern = r"permalink:\s*['\"]?([^'\"\n]+)['\"]?"
        permalink_match = re.search(permalink_pattern, yaml_content)

        if permalink_match:
            permalink = permalink_match.group(1).strip()
            return permalink if permalink else None

        return None

    def get_destination_path(self, file_path: Path) -> str:
        """
        Convert file path to destination path format.

        Args:
            file_path: Absolute path to MDX file

        Returns:
            Destination path without .mdx extension, relative to project root
        """
        # Get path relative to portal_dir's parent (project root)
        relative_path = file_path.relative_to(self.portal_dir.parent)

        # Remove .mdx extension
        path_without_ext = relative_path.with_suffix('')

        # Convert to string with forward slashes and prepend /
        return '/' + str(path_without_ext).replace('\\', '/')

    def should_skip_file(self, file_path: Path) -> bool:
        """
        Check if file should be skipped.

        Args:
            file_path: Path to check

        Returns:
            True if file should be skipped
        """
        if self.exclude_archived and '_archived' in file_path.parts:
            return True
        return False

    def process_file(self, file_path: Path) -> None:
        """
        Process a single MDX file.

        Args:
            file_path: Path to MDX file
        """
        self.stats['total_files'] += 1

        # Check if should skip
        if self.should_skip_file(file_path):
            self.stats['skipped_archived'] += 1
            self.skipped_files.append(str(file_path))
            return

        try:
            # Read file with UTF-8 encoding
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1
                content = file_path.read_text(encoding='latin-1')

            # Extract permalink
            permalink = self.extract_permalink_from_frontmatter(content)

            if permalink:
                # Create redirect entry
                source = f"/portal/{permalink}"
                destination = self.get_destination_path(file_path)

                # Track for duplicate detection
                self.permalink_map[permalink].append(str(file_path))

                # Skip if source and destination are the same
                if source == destination:
                    self.stats['skipped_same_source_destination'] += 1
                    return

                # Check if we already have this source
                if source in self.source_map:
                    existing = self.source_map[source]
                    existing_dest = existing['destination']
                    existing_path = existing['file_path']

                    # Prefer the destination with more path depth (more organized)
                    current_depth = destination.count('/')
                    existing_depth = existing_dest.count('/')

                    if current_depth > existing_depth:
                        # Replace existing with current (more organized)
                        # Find and remove the old redirect
                        self.redirects = [
                            r for r in self.redirects
                            if not (r['source'] == source and r['destination'] == existing_dest)
                        ]

                        # Add the new one
                        redirect_entry = {
                            "source": source,
                            "destination": destination
                        }
                        self.redirects.append(redirect_entry)
                        self.source_map[source] = {
                            'destination': destination,
                            'file_path': str(file_path)
                        }

                        # Track the resolution
                        self.duplicate_resolutions.append({
                            'permalink': permalink,
                            'source': source,
                            'chosen_destination': destination,
                            'chosen_file': str(file_path),
                            'rejected_destination': existing_dest,
                            'rejected_file': existing_path,
                            'reason': 'More organized path (deeper hierarchy)'
                        })

                        self.stats['files_with_permalinks'] += 1
                        self.stats['skipped_duplicate_source'] += 1
                    else:
                        # Skip current, keep existing
                        self.stats['skipped_duplicate_source'] += 1
                        self.skipped_files.append(f"{str(file_path)} (duplicate source: {source})")

                        # Track the resolution
                        self.duplicate_resolutions.append({
                            'permalink': permalink,
                            'source': source,
                            'chosen_destination': existing_dest,
                            'chosen_file': existing_path,
                            'rejected_destination': destination,
                            'rejected_file': str(file_path),
                            'reason': 'Kept first (equally or more organized)'
                        })
                else:
                    # First time seeing this source, add it
                    redirect_entry = {
                        "source": source,
                        "destination": destination
                    }
                    self.redirects.append(redirect_entry)
                    self.source_map[source] = {
                        'destination': destination,
                        'file_path': str(file_path)
                    }
                    self.stats['files_with_permalinks'] += 1
            else:
                self.stats['files_without_permalinks'] += 1
                self.skipped_files.append(str(file_path))

        except Exception as e:
            self.stats['errors'] += 1
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")

    def process_all_files(self) -> None:
        """Process all MDX files in the portal directory."""
        print(f"Searching for MDX files in {self.portal_dir}...")

        # Find all .mdx files recursively
        mdx_files = list(self.portal_dir.rglob("*.mdx"))
        print(f"Found {len(mdx_files)} MDX files")

        print("Processing MDX files...")
        for file_path in mdx_files:
            self.process_file(file_path)

    def validate_results(self) -> None:
        """Validate extracted results and report issues."""
        print("Validating results...")

        # Check for duplicate sources (should not happen after deduplication)
        source_counts = defaultdict(int)
        for redirect in self.redirects:
            source_counts[redirect['source']] += 1

        duplicate_sources = {
            source: count
            for source, count in source_counts.items()
            if count > 1
        }

        if duplicate_sources:
            print("\n❌ ERROR: Duplicate sources found in redirects:")
            for source, count in duplicate_sources.items():
                print(f"  - Source '{source}' appears {count} times")
        else:
            print("✓ All redirect sources are unique")

        # Check for duplicate permalinks in source files (informational)
        duplicates = {
            permalink: files
            for permalink, files in self.permalink_map.items()
            if len(files) > 1
        }

        if duplicates:
            print(f"\nℹ️  Note: {len(duplicates)} permalinks found in multiple files (resolved by preferring organized paths)")

        # Check for empty permalinks (shouldn't happen but safety check)
        empty_permalinks = [
            r for r in self.redirects
            if not r['source'].replace('/portal/', '').strip()
        ]

        if empty_permalinks:
            print(f"\n⚠️  WARNING: {len(empty_permalinks)} empty permalinks found")

    def write_output(self, output_path: Path) -> None:
        """
        Write redirects to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_data = {
            "redirects": self.redirects
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nWrote {len(self.redirects)} redirects to {output_path}")

    def write_duplicates_report(self, report_path: Path) -> None:
        """
        Write duplicate permalinks report to file.

        Args:
            report_path: Path to output report file
        """
        if not self.duplicate_resolutions:
            return

        # Group by permalink
        duplicates_by_permalink = defaultdict(list)
        for resolution in self.duplicate_resolutions:
            duplicates_by_permalink[resolution['permalink']].append(resolution)

        # Also check permalink_map for all files with each permalink
        report_data = {
            "summary": {
                "total_duplicate_permalinks": len(duplicates_by_permalink),
                "total_files_affected": sum(len(files) for files in self.permalink_map.values() if len(files) > 1)
            },
            "duplicates": []
        }

        for permalink, files in self.permalink_map.items():
            if len(files) > 1:
                # Find which one was chosen
                chosen_info = self.source_map.get(f"/portal/{permalink}")

                duplicate_entry = {
                    "permalink": permalink,
                    "source": f"/portal/{permalink}",
                    "files_with_this_permalink": files,
                    "chosen_destination": chosen_info['destination'] if chosen_info else None,
                    "chosen_file": chosen_info['file_path'] if chosen_info else None
                }

                report_data["duplicates"].append(duplicate_entry)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"Wrote duplicate permalinks report to {report_path}")

    def print_report(self) -> None:
        """Print summary report."""
        print("\n" + "=" * 50)
        print("Permalink Extraction Report")
        print("=" * 50)
        print(f"Total MDX files found: {self.stats['total_files']}")
        print(f"Files with redirects: {self.stats['files_with_permalinks']}")
        print(f"Files without permalinks: {self.stats['files_without_permalinks']}")
        print(f"Skipped (source = destination): {self.stats['skipped_same_source_destination']}")
        print(f"Skipped (duplicate source): {self.stats['skipped_duplicate_source']}")
        print(f"Archived files skipped: {self.stats['skipped_archived']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract permalinks from MDX files and generate redirect mappings'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='redirects.json',
        help='Output JSON file path (default: redirects.json)'
    )
    parser.add_argument(
        '--exclude-archived',
        action='store_true',
        default=True,
        help='Exclude files in _archived directories (default: True)'
    )
    parser.add_argument(
        '--include-archived',
        dest='exclude_archived',
        action='store_false',
        help='Include files in _archived directories'
    )
    parser.add_argument(
        '--portal-dir',
        type=str,
        default='portal',
        help='Portal directory path (default: portal)'
    )

    args = parser.parse_args()

    # Get portal directory path
    portal_dir = Path(args.portal_dir)

    if not portal_dir.exists():
        print(f"❌ Error: Portal directory not found: {portal_dir}")
        return 1

    if not portal_dir.is_dir():
        print(f"❌ Error: Not a directory: {portal_dir}")
        return 1

    # Create extractor and process files
    extractor = PermalinkExtractor(portal_dir, args.exclude_archived)
    extractor.process_all_files()
    extractor.validate_results()

    # Write output
    output_path = Path(args.output)
    extractor.write_output(output_path)

    # Write duplicates report if there are any
    if extractor.duplicate_resolutions or any(len(files) > 1 for files in extractor.permalink_map.values()):
        duplicates_report_path = output_path.parent / 'duplicates_report.json'
        extractor.write_duplicates_report(duplicates_report_path)

    # Print report
    extractor.print_report()

    return 0


if __name__ == '__main__':
    exit(main())
