#!/usr/bin/env python3
"""
Programmatic structural transforms for Japanese MDX articles.

Handles all rule-based transformations that do not require AI judgment:
  1. Remove TOC back-links
  2. Add missing InlineImage import (when English has it)
  3. Wrap plain Note / Warning / Tip callouts in MDX components
  4. Convert <Frame>![alt](ja/path)</Frame> → <Frame><img alt="" src="" style={{}}/></Frame>
     by matching filenames and copying dimensions from the English article
  5. Convert standalone inline-icon <img> tags → <InlineImage src="..."/>
     and inline them with adjacent text
  6. Convert FAQ #### headings → <AccordionGroup> / <Accordion> structure

Usage:
    python3 transform_ja_articles.py                        # all modified JA articles
    python3 transform_ja_articles.py --file 000005143.mdx   # single file
    python3 transform_ja_articles.py --dry-run              # preview only
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
EN_DIR = REPO_ROOT / "s" / "article"
JA_DIR = REPO_ROOT / "ja" / "s" / "article"

# ---------------------------------------------------------------------------
# TOC link patterns
# ---------------------------------------------------------------------------
_TOC_PATTERNS = [
    re.compile(r'\[#\w+\]\(#\w+\)\[このページのトップへ\]\(#\w+\)\s*\n?'),
    re.compile(r'\[#toc\]\(#toc\)\[.*?\]\(#toc\)\s*\n?'),
    re.compile(r'\[このページのトップへ\]\(#[\w]+\)\s*\n?'),
]

# ---------------------------------------------------------------------------
# Inline callout patterns (plain text → MDX component)
# ---------------------------------------------------------------------------
# Each tuple: (regex_to_find_label, component_tag)
_CALLOUT_PATTERNS = [
    (re.compile(r'(\*\*注記\*\*\*\*：\*\*|\*\*注記：\*\*|\*\*注 記：\*\*)'), 'Note'),
    (re.compile(r'(\*\*警告\*\*\*\*：\*\*|\*\*警告：\*\*)'), 'Warning'),
    (re.compile(r'(\*\*ヒント\*\*\*\*：\*\*|\*\*ヒント：\*\*)'), 'Tip'),
    (re.compile(r'(\*\*重要\*\*\*\*：\*\*|\*\*重要：\*\*)'), 'Warning'),
]

# Matches an entire standalone callout paragraph (everything up to blank line or EOF)
# Used to extract the full callout body after the label is detected.

# ---------------------------------------------------------------------------
# Image extraction helpers
# ---------------------------------------------------------------------------
# Match <Frame><img alt="..." src="..." style={{width: W, height: H}}/></Frame>
_EN_FRAME_IMG = re.compile(
    r'<Frame><img\s+alt="([^"]*?)"\s+src="([^"]+?)"(?:\s+style=\{\{([^}]*)\}\})?\s*/></Frame>',
    re.DOTALL,
)
# Match <Frame><img alt="..." src="..."/></Frame> without style
_EN_FRAME_IMG_NO_STYLE = re.compile(
    r'<Frame><img\s+alt="([^"]*?)"\s+src="([^"]+?)"\s*/></Frame>',
)
# Match <Frame>![alt](path)</Frame>
_JA_FRAME_MD = re.compile(r'<Frame>!\[([^\]]*)\]\(([^)]+)\)</Frame>')
# Match <InlineImage src="..."/> in English
_EN_INLINE = re.compile(r'<InlineImage\s+src="([^"]+)"\s*/>')
# Match standalone <img> icon tags in Japanese (display:inline, small size)
_JA_ICON_IMG = re.compile(
    r'<img\s+alt="([^"]*?)"\s+src="(/images/kb/ja/[^"]+?)"\s+style=\{\{width:\s*\d+,\s*height:\s*\d+,\s*display:\s*[\'"]inline[\'"].*?\}\}\s*/>'
)

# ---------------------------------------------------------------------------
# Short filename ID extractor (last component without extension)
# ---------------------------------------------------------------------------
def short_id(path_str: str) -> str:
    """Return basename without extension for path matching."""
    return Path(path_str).stem


# ---------------------------------------------------------------------------
# Parse English article image maps
# ---------------------------------------------------------------------------
def build_en_image_maps(en_content: str) -> tuple[dict, dict]:
    """
    Returns:
        frame_map:  short_id → (alt, full_style_string_or_None)
        inline_map: short_id → src_path
    """
    frame_map: dict[str, tuple[str, str | None]] = {}
    inline_map: dict[str, str] = {}

    for m in _EN_FRAME_IMG.finditer(en_content):
        alt, src, style = m.group(1), m.group(2), m.group(3)
        sid = short_id(src)
        frame_map[sid] = (alt, f"style={{{{{{style}}}}}}" if style else None)

    # also plain no-style frames
    for m in _EN_FRAME_IMG_NO_STYLE.finditer(en_content):
        alt, src = m.group(1), m.group(2)
        sid = short_id(src)
        if sid not in frame_map:
            frame_map[sid] = (alt, None)

    for m in _EN_INLINE.finditer(en_content):
        src = m.group(1)
        sid = short_id(src)
        inline_map[sid] = src

    return frame_map, inline_map


# ---------------------------------------------------------------------------
# Individual transformations
# ---------------------------------------------------------------------------
def remove_toc_links(content: str) -> str:
    for pat in _TOC_PATTERNS:
        content = pat.sub('', content)
    return content


def add_import_if_needed(content: str, en_content: str) -> str:
    """Add InlineImage import if English has it and Japanese doesn't."""
    import_line = 'import {InlineImage} from "/snippets/InlineImage.mdx";'
    if import_line in content:
        return content
    if import_line not in en_content and '<InlineImage' not in en_content:
        return content
    # Insert after closing --- of frontmatter
    parts = content.split('---', 2)
    if len(parts) >= 3:
        content = parts[0] + '---' + parts[1] + '---\n\n' + import_line + '\n' + parts[2]
    return content


def wrap_callouts(content: str) -> str:
    """Wrap plain-text Japanese callouts in Note/Warning/Tip components."""
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched_component = None
        for pat, component in _CALLOUT_PATTERNS:
            if pat.search(line):
                # Check it's not already inside a component
                stripped = line.strip()
                if not stripped.startswith('<Note') and not stripped.startswith('<Warning') and not stripped.startswith('<Tip'):
                    matched_component = component
                    break

        if matched_component:
            # Collect all lines of this callout paragraph (until blank line or EOF)
            callout_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() == '':
                    break
                callout_lines.append(next_line)
                j += 1
            callout_body = ''.join(callout_lines).rstrip('\n')
            result.append(f'<{matched_component}>{callout_body}</{matched_component}>\n')
            i = j
        else:
            result.append(line)
            i += 1
    return ''.join(result)


def convert_frame_images(content: str, frame_map: dict) -> str:
    """Convert <Frame>![alt](ja/path)</Frame> → <Frame><img .../></Frame>."""
    def replacer(m):
        ja_alt = m.group(1)
        ja_path = m.group(2)
        sid = short_id(ja_path)
        if sid in frame_map:
            en_alt, style_attr = frame_map[sid]
            # Keep Japanese alt if present, otherwise use English alt
            use_alt = ja_alt if ja_alt else en_alt
            if style_attr:
                return f'<Frame><img alt="{use_alt}" src="{ja_path}" {style_attr}/></Frame>'
            else:
                return f'<Frame><img alt="{use_alt}" src="{ja_path}"/></Frame>'
        # No match found — keep original but note it
        return m.group(0)

    return _JA_FRAME_MD.sub(replacer, content)


def convert_inline_icons(content: str, inline_map: dict) -> str:
    """
    Convert standalone <img> icon tags (display:inline) to <InlineImage>.
    Handles both:
      a) Icon on its own line between text — merge onto previous/next line
      b) Icon already inline — just swap tag
    """
    # First pass: swap tag syntax for icons that ARE inline already
    def swap_inline(m):
        ja_path = m.group(2)
        return f'<InlineImage src="{ja_path}" />'

    content = _JA_ICON_IMG.sub(swap_inline, content)

    # Second pass: collapse standalone <InlineImage> lines onto adjacent text
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # A line that is ONLY an InlineImage tag (possibly with leading spaces)
        if re.fullmatch(r'\s*<InlineImage\s+src="[^"]+"\s*/>\s*', line):
            inline_tag = stripped  # the <InlineImage .../> tag
            # Try to merge with previous non-blank line
            if result and result[-1].strip():
                prev = result[-1].rstrip('\n')
                result[-1] = prev + ' ' + inline_tag + '\n'
            else:
                # Merge with next non-blank line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_line = lines[j].lstrip()
                    result.append(inline_tag + ' ' + next_line)
                    # Skip any blank lines between
                    for k in range(i + 1, j + 1):
                        pass  # skip them
                    i = j + 1
                    continue
                else:
                    result.append(line)
        else:
            result.append(line)
        i += 1
    return ''.join(result)


def convert_faq_headings(content: str, en_content: str) -> str:
    """
    If English has <AccordionGroup> and Japanese has #### FAQ headings,
    convert the #### section to AccordionGroup/Accordion structure.
    """
    if '<AccordionGroup>' not in en_content:
        return content
    if '<AccordionGroup>' in content:
        return content  # already converted

    # Find the FAQ section in Japanese (#### headings after a ## or ### FAQ-like heading)
    # Pattern: find #### heading followed by content, repeated
    faq_section_pat = re.compile(
        r'(#{3,4}\s+(?:よくある質問|FAQ|ご質問|Q&A)[^\n]*\n)'
        r'((?:\n*####[^\n]+\n(?:[^#]|\n)*)+)',
        re.MULTILINE
    )

    def convert_faq(m):
        heading = m.group(1)
        body = m.group(2)
        # Split into individual Q&A pairs
        qa_items = re.split(r'\n(?=####)', body.strip())
        accordions = []
        for item in qa_items:
            item = item.strip()
            if not item:
                continue
            lines = item.splitlines()
            title_line = lines[0]
            title_match = re.match(r'####\s+(.+)', title_line)
            if not title_match:
                continue
            title = title_match.group(1).strip()
            answer = '\n'.join(lines[1:]).strip()
            accordions.append(
                f'<Accordion title="{title}">\n\n{answer}\n</Accordion>'
            )
        if not accordions:
            return m.group(0)
        group = '<AccordionGroup>\n\n' + '\n'.join(accordions) + '\n</AccordionGroup>'
        return heading + group

    content = faq_section_pat.sub(convert_faq, content)
    return content


# ---------------------------------------------------------------------------
# Main per-file function
# ---------------------------------------------------------------------------
def process_file(ja_path: Path, dry_run: bool) -> str:
    filename = ja_path.name
    en_path = EN_DIR / filename

    if not en_path.exists():
        return f'SKIP  {filename}  (no EN counterpart)'

    en_content = en_path.read_text(encoding='utf-8')
    ja_content = ja_path.read_text(encoding='utf-8')
    original = ja_content

    # Build image maps from English article
    frame_map, inline_map = build_en_image_maps(en_content)

    # Apply transformations
    ja_content = remove_toc_links(ja_content)
    ja_content = add_import_if_needed(ja_content, en_content)
    ja_content = wrap_callouts(ja_content)
    ja_content = convert_frame_images(ja_content, frame_map)
    if inline_map:
        ja_content = convert_inline_icons(ja_content, inline_map)
    ja_content = convert_faq_headings(ja_content, en_content)

    if ja_content == original:
        return f'SAME  {filename}'

    if dry_run:
        return f'DRY   {filename}  (changes detected)'

    ja_path.write_text(ja_content, encoding='utf-8')
    return f'OK    {filename}'


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------
def get_modified_ja_files() -> list[Path]:
    def git_diff(*args):
        r = subprocess.run(['git', 'diff', *args, '--name-only'],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        return r.stdout.strip().splitlines()
    lines = set(git_diff('--cached') + git_diff())
    return sorted(REPO_ROOT / p for p in lines
                  if p.startswith('ja/s/article/') and p.endswith('.mdx'))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--file', help='Process single file, e.g. 000005143.mdx')
    args = parser.parse_args()

    if args.file:
        files = [JA_DIR / args.file]
        if not files[0].exists():
            sys.exit(f'Not found: {files[0]}')
    else:
        files = get_modified_ja_files()
        if not files:
            sys.exit('No modified Japanese articles found.')

    print(f'{"DRY RUN — " if args.dry_run else ""}Processing {len(files)} file(s)\n')
    ok = same = skip = 0
    for f in files:
        msg = process_file(f, args.dry_run)
        print(msg)
        if msg.startswith('OK'):
            ok += 1
        elif msg.startswith('SAME'):
            same += 1
        else:
            skip += 1

    print(f'\nDone. {ok} updated, {same} unchanged, {skip} skipped/error.')


if __name__ == '__main__':
    main()
