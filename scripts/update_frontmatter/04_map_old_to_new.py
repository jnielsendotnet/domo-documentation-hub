#!/usr/bin/env python3
"""
Build a mapping from old article IDs (s/article/XXXXX) to new portal file paths.
"""
import json
import os
import re
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
OLD_ARTICLES_DIR = BASE_DIR / "s" / "article"
PORTAL_DIR = BASE_DIR / "portal"
OUTPUT_DIR = Path(__file__).parent / "output"

def extract_frontmatter(content):
    """Extract YAML frontmatter from MDX content."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        # Simple YAML parsing for title and permalink
        fm_dict = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                fm_dict[key.strip()] = value.strip().strip('"').strip("'")
        return fm_dict
    return {}

def scan_old_articles():
    """Scan old article files and extract their metadata."""
    print(f"Scanning old articles in {OLD_ARTICLES_DIR}...")
    old_articles = {}

    if not OLD_ARTICLES_DIR.exists():
        print(f"Warning: {OLD_ARTICLES_DIR} does not exist")
        return old_articles

    for mdx_file in OLD_ARTICLES_DIR.glob("*.mdx"):
        article_id = mdx_file.stem
        try:
            with open(mdx_file, 'r', encoding='utf-8') as f:
                content = f.read()
                fm = extract_frontmatter(content)
                if 'title' in fm:
                    old_articles[article_id] = {
                        'title': fm['title'],
                        'file': str(mdx_file.relative_to(BASE_DIR))
                    }
        except Exception as e:
            print(f"Error reading {mdx_file}: {e}")

    print(f"Found {len(old_articles)} old articles")
    return old_articles

def scan_portal_files():
    """Scan portal files and extract their metadata."""
    print(f"\nScanning portal files in {PORTAL_DIR}...")
    portal_files = {}

    if not PORTAL_DIR.exists():
        print(f"Warning: {PORTAL_DIR} does not exist")
        return portal_files

    for mdx_file in PORTAL_DIR.rglob("*.mdx"):
        try:
            with open(mdx_file, 'r', encoding='utf-8') as f:
                content = f.read()
                fm = extract_frontmatter(content)
                if 'title' in fm and 'permalink' in fm:
                    portal_files[mdx_file.stem] = {
                        'title': fm['title'],
                        'permalink': fm['permalink'],
                        'file': str(mdx_file.relative_to(BASE_DIR)),
                        'relative_path': f"portal/{mdx_file.relative_to(PORTAL_DIR)}"
                    }
        except Exception as e:
            print(f"Error reading {mdx_file}: {e}")

    print(f"Found {len(portal_files)} portal files")
    return portal_files

def find_old_article_refs_in_docs_json():
    """Find all old article references in docs.json."""
    docs_json_path = BASE_DIR / "docs.json"
    print(f"\nAnalyzing {docs_json_path}...")

    with open(docs_json_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all s/article/XXXXX references
    pattern = r'"s/article/(\d+)"'
    matches = re.findall(pattern, content)
    unique_refs = set(matches)

    print(f"Found {len(matches)} total references to {len(unique_refs)} unique old article IDs")
    return unique_refs

def build_mapping(old_articles, portal_files, referenced_ids):
    """Build mapping from old article IDs to new portal paths."""
    print("\nBuilding mapping...")
    mapping = {}
    unmapped = []

    for article_id in referenced_ids:
        if article_id in old_articles:
            old_title = old_articles[article_id]['title']
            # Try to find matching portal file by title
            found = False
            for portal_id, portal_info in portal_files.items():
                if portal_info['title'].lower() == old_title.lower():
                    mapping[article_id] = {
                        'old_title': old_title,
                        'new_path': portal_info['relative_path'].replace('.mdx', '').replace('portal/', ''),
                        'new_title': portal_info['title'],
                        'permalink': portal_info['permalink']
                    }
                    found = True
                    break

            if not found:
                unmapped.append({
                    'id': article_id,
                    'title': old_title
                })
        else:
            unmapped.append({
                'id': article_id,
                'title': 'NOT FOUND IN OLD ARTICLES'
            })

    print(f"Mapped {len(mapping)} article IDs")
    print(f"Unmapped: {len(unmapped)} article IDs")

    return mapping, unmapped

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Scan all files
    old_articles = scan_old_articles()
    portal_files = scan_portal_files()
    referenced_ids = find_old_article_refs_in_docs_json()

    # Build mapping
    mapping, unmapped = build_mapping(old_articles, portal_files, referenced_ids)

    # Save mapping
    mapping_file = OUTPUT_DIR / "old_to_new_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    print(f"\nMapping saved to {mapping_file}")

    # Save unmapped
    unmapped_file = OUTPUT_DIR / "unmapped_articles.json"
    with open(unmapped_file, 'w', encoding='utf-8') as f:
        json.dump(unmapped, f, indent=2)
    print(f"Unmapped articles saved to {unmapped_file}")

    # Create report
    report_file = OUTPUT_DIR / "mapping_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Old Article to New Portal Mapping Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total old article references in docs.json: {len(referenced_ids)}\n")
        f.write(f"Successfully mapped: {len(mapping)}\n")
        f.write(f"Unmapped: {len(unmapped)}\n\n")

        if mapping:
            f.write("\nMAPPED ARTICLES\n")
            f.write("-" * 70 + "\n")
            for article_id, info in sorted(mapping.items()):
                f.write(f"\n{article_id}\n")
                f.write(f"  Old: {info['old_title']}\n")
                f.write(f"  New: {info['new_path']}\n")
                f.write(f"  Title: {info['new_title']}\n")

        if unmapped:
            f.write("\n\nUNMAPPED ARTICLES\n")
            f.write("-" * 70 + "\n")
            for item in unmapped:
                f.write(f"\n{item['id']}: {item['title']}\n")

    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    main()
