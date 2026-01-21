#!/usr/bin/env python3
"""
Generate prioritized merge recommendations and human-readable report.
"""

import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"

def load_changes():
    """Load detected changes."""
    changes_file = OUTPUT_DIR / "changes_detected.json"

    if not changes_file.exists():
        print("ERROR: Changes file not found. Run detect_changes.py first.")
        exit(1)

    with open(changes_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def assign_priority(item, change_type):
    """Assign priority level based on file path and change type."""
    source_path = ''

    if change_type == 'new':
        source_path = item.get('source', {}).get('path', '').lower()
    else:
        source_path = item.get('source_path', '').lower()

    # CRITICAL: Core authentication, getting started, breaking changes
    critical_patterns = [
        'getting-started',
        'authentication',
        'api-authentication',
        'quickstart',
        'overview.md'
    ]

    # HIGH: Major new features
    high_patterns = [
        'advanced-forms',
        'app-catalyst',
        'local-development',
        'domo-publish-cicd'
    ]

    # MEDIUM: Tool updates, Pro Code Editor
    medium_patterns = [
        'da-cli',
        'domo.js',
        'pro-code-editor',
        'ai-service',
        'cli'
    ]

    # Check patterns
    for pattern in critical_patterns:
        if pattern in source_path:
            return 'critical'

    for pattern in high_patterns:
        if pattern in source_path:
            return 'high'

    for pattern in medium_patterns:
        if pattern in source_path:
            return 'medium'

    # Default priority based on change type
    if change_type == 'new':
        return 'high'  # New files are generally high priority
    elif change_type == 'major_update':
        return 'medium'
    else:
        return 'low'

def categorize_by_topic(source_path):
    """Categorize file by documentation topic."""
    path_lower = source_path.lower()

    if 'api-reference' in path_lower or 'api' in path_lower:
        return 'API Reference'
    elif 'forms' in path_lower:
        return 'Forms'
    elif 'app' in path_lower:
        return 'Apps'
    elif 'connector' in path_lower:
        return 'Connectors'
    elif 'embedded' in path_lower or 'embed' in path_lower:
        return 'Embedded Analytics'
    elif 'data-science' in path_lower:
        return 'Data Science'
    elif 'getting-started' in path_lower:
        return 'Getting Started'
    elif 'governance' in path_lower:
        return 'Governance'
    elif 'automate' in path_lower or 'workflow' in path_lower:
        return 'Automation'
    else:
        return 'Other'

def generate_recommendations(changes):
    """Generate prioritized merge recommendations."""
    print("\nGenerating merge recommendations...")

    recommendations = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }

    # Process new files
    for item in changes['changes']['new']:
        source = item.get('source', {})
        source_path = source.get('path', '')

        priority = assign_priority(item, 'new')
        topic = categorize_by_topic(source_path)

        recommendations[priority].append({
            'type': 'NEW',
            'priority': priority,
            'topic': topic,
            'source_path': source_path,
            'source_title': source.get('title', 'Untitled'),
            'added_date': item.get('added_date'),
            'commit_count': len(item.get('commits', [])),
            'action': 'Add new file to migrated repository',
            'dependencies': self_check_dependencies(source_path)
        })

    # Process major updates
    for item in changes['changes']['major_update']:
        source_path = item.get('source_path', '')
        priority = assign_priority(item, 'major_update')
        topic = categorize_by_topic(source_path)

        recommendations[priority].append({
            'type': 'MAJOR_UPDATE',
            'priority': priority,
            'topic': topic,
            'source_path': source_path,
            'migrated_path': item.get('migrated_path', ''),
            'stoplight_id': item.get('stoplight_id'),
            'reason': item.get('reason', ''),
            'commit_count': item.get('commit_count', 0),
            'latest_commit': item.get('latest_commit', {}),
            'action': 'Review and merge major content changes',
            'dependencies': []
        })

    # Process minor updates
    for item in changes['changes']['minor_update']:
        source_path = item.get('source_path', '')
        priority = assign_priority(item, 'minor_update')
        topic = categorize_by_topic(source_path)

        recommendations[priority].append({
            'type': 'MINOR_UPDATE',
            'priority': priority,
            'topic': topic,
            'source_path': source_path,
            'migrated_path': item.get('migrated_path', ''),
            'stoplight_id': item.get('stoplight_id'),
            'reason': item.get('reason', ''),
            'commit_count': item.get('commit_count', 0),
            'action': 'Merge minor content updates',
            'dependencies': []
        })

    # Process content differences (no git history but content differs)
    for item in changes['changes']['content_diff']:
        source_path = item.get('source_path', '')
        priority = 'low'  # Default to low priority for unexplained diffs
        topic = categorize_by_topic(source_path)

        recommendations[priority].append({
            'type': 'CONTENT_DIFF',
            'priority': priority,
            'topic': topic,
            'source_path': source_path,
            'migrated_path': item.get('migrated_path', ''),
            'stoplight_id': item.get('stoplight_id'),
            'reason': item.get('reason', ''),
            'action': 'Review content differences',
            'dependencies': []
        })

    return recommendations

def check_dependencies(source_path):
    """Check for image dependencies based on file path."""
    # This is a simplified check - in a full implementation,
    # you would parse the markdown and extract actual image references
    path_parts = Path(source_path).parts

    if 'Advanced-Forms' in path_parts:
        return ['advanced-form-*.png']
    elif 'App-Catalyst' in path_parts:
        return ['AC_*.png']
    elif 'Pro-Code' in path_parts:
        return ['pro.png', 'proxyId_location.png', 'thumbnail-procode.png']

    return []

def generate_markdown_report(recommendations, summary):
    """Generate human-readable markdown report."""
    report = []

    report.append("# Documentation Merge Report")
    report.append("")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Summary
    report.append("## Summary")
    report.append("")
    report.append(f"- **New files**: {summary['new_files']}")
    report.append(f"- **Major updates**: {summary['major_updates']}")
    report.append(f"- **Minor updates**: {summary['minor_updates']}")
    report.append(f"- **Content differences**: {summary['content_diff']}")
    report.append(f"- **Unchanged**: {summary['unchanged']}")
    report.append("")

    # Priority breakdown
    report.append("## Priority Breakdown")
    report.append("")
    for priority in ['critical', 'high', 'medium', 'low']:
        count = len(recommendations[priority])
        report.append(f"- **{priority.upper()}**: {count} files")
    report.append("")

    # Detailed recommendations by priority
    for priority in ['critical', 'high', 'medium', 'low']:
        items = recommendations[priority]
        if not items:
            continue

        report.append(f"## {priority.upper()} Priority ({len(items)} files)")
        report.append("")

        # Group by topic
        by_topic = {}
        for item in items:
            topic = item.get('topic', 'Other')
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(item)

        for topic, topic_items in sorted(by_topic.items()):
            report.append(f"### {topic}")
            report.append("")

            for item in topic_items:
                report.append(f"#### {item.get('type')} - {Path(item.get('source_path', '')).name}")
                report.append("")
                report.append(f"- **Source**: `{item.get('source_path', '')}`")

                if item.get('migrated_path'):
                    report.append(f"- **Migrated**: `{item.get('migrated_path', '')}`")

                if item.get('stoplight_id'):
                    report.append(f"- **Stoplight ID**: `{item.get('stoplight_id')}`")

                report.append(f"- **Action**: {item.get('action', '')}")

                if item.get('reason'):
                    report.append(f"- **Reason**: {item.get('reason', '')}")

                if item.get('commit_count', 0) > 0:
                    report.append(f"- **Commits**: {item.get('commit_count', 0)}")

                if item.get('latest_commit'):
                    commit = item['latest_commit']
                    report.append(f"- **Latest commit**: {commit.get('date', '')} - {commit.get('message', '')}")

                if item.get('dependencies'):
                    report.append(f"- **Dependencies**: {', '.join(item['dependencies'])}")

                report.append("")

        report.append("")

    return '\n'.join(report)

def self_check_dependencies(source_path):
    """Check for dependencies (simplified implementation)."""
    return check_dependencies(source_path)

def main():
    """Main execution."""
    print("=" * 60)
    print("Generating Merge Recommendations")
    print("=" * 60)

    # Load changes
    changes = load_changes()
    summary = changes['summary']

    # Generate recommendations
    recommendations = generate_recommendations(changes)

    # Count recommendations by priority
    priority_counts = {
        'critical': len(recommendations['critical']),
        'high': len(recommendations['high']),
        'medium': len(recommendations['medium']),
        'low': len(recommendations['low'])
    }

    # Build final output
    output = {
        'generated': datetime.now().isoformat(),
        'summary': {
            **summary,
            'priority_counts': priority_counts
        },
        'recommendations': recommendations
    }

    # Save JSON
    json_output = OUTPUT_DIR / "merge_recommendations.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nJSON recommendations saved to: {json_output}")

    # Generate markdown report
    markdown_content = generate_markdown_report(recommendations, summary)
    markdown_output = OUTPUT_DIR / "merge_report.md"
    with open(markdown_output, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Markdown report saved to: {markdown_output}")

    # Print summary
    print(f"\n" + "=" * 60)
    print("Merge Recommendations Summary")
    print("=" * 60)
    print(f"\nTotal items requiring action: {sum(priority_counts.values())}")
    print(f"\nBy priority:")
    for priority, count in priority_counts.items():
        print(f"  {priority.upper()}: {count}")

    print(f"\nBy change type:")
    print(f"  New files: {summary['new_files']}")
    print(f"  Major updates: {summary['major_updates']}")
    print(f"  Minor updates: {summary['minor_updates']}")
    print(f"  Content differences: {summary['content_diff']}")

    print(f"\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    print(f"\nReview the report at: {markdown_output}")
    print("Next steps:")
    print("1. Review the merge_report.md file")
    print("2. Start with CRITICAL priority items")
    print("3. Create a git branch for the merge")
    print("4. Proceed with content transformation and merging")

if __name__ == "__main__":
    main()
