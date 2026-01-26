#!/usr/bin/env python3
"""
Generate AI-powered sidebar title recommendations.

This script uses Claude API to analyze H1 titles and determine if shorter
sidebar titles would be appropriate for navigation.

Requires:
- ANTHROPIC_API_KEY environment variable
- pip install anthropic

Output:
- sidebar_title_recommendations.json: AI suggestions for all files
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import time


def load_analysis() -> List[Dict]:
    """Load the title analysis from Phase 1."""
    analysis_path = Path('scripts/update_frontmatter/output/title_analysis.json')

    if not analysis_path.exists():
        raise FileNotFoundError(
            f"Analysis file not found at {analysis_path}. "
            "Please run analyze_titles.py first."
        )

    with open(analysis_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def determine_parent_context(filepath: str) -> str:
    """
    Extract parent directory structure for context.

    Example:
        portal/Apps/App-Framework/Guides/manifest.mdx
        -> "Apps > App Framework > Guides"
    """
    path = Path(filepath)
    parts = path.parts

    # Skip 'portal' and filename
    if 'portal' in parts:
        start_idx = parts.index('portal') + 1
    else:
        start_idx = 0

    context_parts = parts[start_idx:-1]  # Exclude filename

    # Convert kebab-case to Title Case
    formatted_parts = []
    for part in context_parts:
        # Convert App-Framework to App Framework
        formatted = part.replace('-', ' ').replace('_', ' ')
        # Title case
        formatted = ' '.join(word.capitalize() for word in formatted.split())
        formatted_parts.append(formatted)

    return ' > '.join(formatted_parts)


def generate_sidebar_title_with_claude(title: str, context: str, h1_title: Optional[str] = None) -> Dict:
    """
    Use Claude API to determine if a shorter sidebar title is needed.

    Returns:
        Dict with keys: needs_sidebar_title, sidebar_title, reasoning
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package not found. Install with: pip install anthropic"
        )

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Get your API key from https://console.anthropic.com/"
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Determine which title to use (prefer H1 if it exists and differs)
    display_title = h1_title if h1_title else title

    prompt = f"""Given this documentation page title and context, determine if a shorter sidebar title is needed for navigation.

Title: "{display_title}"
File Path Context: {context}

Consider:
1. Is the title longer than ~40 characters?
2. Does the hierarchy provide context that makes parts of the title redundant?
3. Would a shorter version maintain clarity while fitting better in navigation?
4. Are there well-known acronyms or abbreviations that would be appropriate?
5. Is the title already concise and clear?

Guidelines:
- Only recommend a sidebar title if it's meaningfully shorter AND maintains clarity
- Remove redundant words implied by the navigation hierarchy
- Keep it under 30 characters if possible
- Preserve key technical terms and proper nouns
- Use well-known acronyms (API, CLI, SDK, etc.)
- If the title is already concise (under 30 chars), recommend null

Respond with JSON only (no other text):
{{"needs_sidebar_title": true/false, "sidebar_title": "..." or null, "reasoning": "..."}}"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        response_text = response.content[0].text.strip()

        # Handle markdown code blocks if present
        if response_text.startswith('```'):
            # Extract JSON from code block
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])  # Remove first and last lines

        result = json.loads(response_text)
        return result

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return {
            'needs_sidebar_title': False,
            'sidebar_title': None,
            'reasoning': f'Error: {str(e)}',
            'error': True
        }


def batch_generate(files: List[Dict], rate_limit_delay: float = 0.5) -> Dict:
    """
    Generate sidebar title recommendations for all files.

    Args:
        files: List of file analysis data
        rate_limit_delay: Seconds to wait between API calls (default 0.5s)

    Returns:
        Dict mapping filepath to recommendation
    """
    recommendations = {}
    total = len(files)

    print(f"Generating sidebar title recommendations for {total} files...")
    print("This will take some time due to API rate limits.\n")

    for i, file_data in enumerate(files, 1):
        filepath = file_data['relative_path']

        # Skip files with errors
        if not file_data.get('has_frontmatter'):
            print(f"[{i}/{total}] Skipping {filepath} (no frontmatter)")
            continue

        # Get the title (prefer H1 if it exists and differs)
        current_title = file_data['frontmatter']['title']
        h1_title = file_data['h1'].get('text') if file_data['h1']['exists'] else None

        # Skip if no meaningful title
        if not current_title and not h1_title:
            print(f"[{i}/{total}] Skipping {filepath} (no title)")
            continue

        # Determine context
        context = determine_parent_context(filepath)

        # Show progress
        display_title = h1_title if h1_title else current_title
        print(f"[{i}/{total}] Analyzing: {display_title[:50]}...")

        # Call Claude API
        recommendation = generate_sidebar_title_with_claude(
            current_title,
            context,
            h1_title
        )

        recommendations[filepath] = {
            'current_title': current_title,
            'h1_title': h1_title,
            'context': context,
            'recommendation': recommendation
        }

        # Rate limiting
        if i < total:
            time.sleep(rate_limit_delay)

    return recommendations


def save_recommendations(recommendations: Dict, output_path: Path):
    """Save recommendations to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved recommendations to {output_path}")

    # Print summary statistics
    total = len(recommendations)
    with_sidebar = sum(1 for r in recommendations.values()
                      if r['recommendation'].get('needs_sidebar_title'))
    errors = sum(1 for r in recommendations.values()
                if r['recommendation'].get('error'))

    print(f"\nSUMMARY:")
    print(f"  Total files analyzed: {total}")
    print(f"  Sidebar titles recommended: {with_sidebar}")
    print(f"  Errors: {errors}")


def main():
    """Main execution function."""
    import sys

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("\nTo use this script:")
        print("1. Get your API key from https://console.anthropic.com/")
        print("2. Set the environment variable:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        print("3. Run this script again")
        sys.exit(1)

    # Load analysis
    print("Loading title analysis from Phase 1...")
    try:
        files = load_analysis()
        print(f"✓ Loaded analysis for {len(files)} files\n")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Filter to files that need recommendations (have frontmatter and title)
    files_to_process = [
        f for f in files
        if f.get('has_frontmatter') and
        (f.get('frontmatter', {}).get('title') or
         (f.get('h1', {}).get('exists') and f.get('h1', {}).get('text')))
    ]

    print(f"Processing {len(files_to_process)} files with valid titles...\n")

    # Generate recommendations
    recommendations = batch_generate(files_to_process)

    # Save results
    output_dir = Path('scripts/update_frontmatter/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'sidebar_title_recommendations.json'

    save_recommendations(recommendations, output_path)

    print("\n✓ Sidebar title generation complete!")
    print("\nNext steps:")
    print("1. Review sidebar_title_recommendations.json")
    print("2. Run migrate_titles.py to apply the changes")


if __name__ == '__main__':
    main()
