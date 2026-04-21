#!/usr/bin/env python3
"""Check queued ja/s/article/ MDX files for formatting errors per Domo KB style guide."""

import re
import subprocess
import sys

# ── Patterns ──────────────────────────────────────────────────────────────────
FRONTMATTER_RE   = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TITLE_RE         = re.compile(r'^title\s*:', re.MULTILINE)
HEADING_RE       = re.compile(r'^(#{1,6})\s+\S')
CODE_FENCE_RE    = re.compile(r'^```')
INLINE_TAG_RE    = re.compile(r'<InlineImage')
INLINE_IMPORT_RE = re.compile(r'import\s+\{InlineImage\}')
CALLOUT_OPEN_RE  = re.compile(r'<(Note|Warning|Tip)>')
CALLOUT_BOLD_RE  = re.compile(r'<(?:Note|Warning|Tip)>\s*\*\*')
# Inline-style img (20×20 icon) anywhere on a line
INLINE_IMG_RE    = re.compile(r"<img\b[^>]*display:\s*'inline'")
FRAME_HEADING_RE = re.compile(r'^#{1,6}\s+.*<Frame')
FAQ_HEADING_RE   = re.compile(r'^#{1,6}\s.*(FAQ|よくある質問)', re.IGNORECASE)
ACCORDION_RE     = re.compile(r'<AccordionGroup')
FRAME_WRAP_RE    = re.compile(r'<Frame>.*<img\b[^>]*display:\s*\'inline\'')

def get_queued_files():
    result = subprocess.run(["git", "status", "--short"],
                            capture_output=True, text=True, check=True)
    files = []
    for line in result.stdout.splitlines():
        path = line[3:].strip()
        if path.startswith("ja/s/article/") and path.endswith(".mdx"):
            files.append(path)
    return files

def is_unpadded_table_sep(line):
    """True if the line is a Markdown table separator row with any cell using ≤3 dashes."""
    if not line.startswith('|'):
        return False
    cells = [c.strip() for c in line.split('|')[1:-1]]
    if not cells or not all(re.match(r'^:?-+:?$', c) for c in cells if c):
        return False
    return any(re.match(r'^:?-{1,3}:?$', c) for c in cells if c)

def check_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []
    lines  = content.split('\n')

    # ── Frontmatter ──
    fm_match = FRONTMATTER_RE.match(content)
    fm_text  = fm_match.group(1) if fm_match else ""
    body_start = content[:fm_match.end()].count('\n') + 1 if fm_match else 1

    if not TITLE_RE.search(fm_text):
        errors.append((1, "NO_TITLE", "Frontmatter missing `title` field"))

    in_code          = False
    cur_heading_lvl  = 0
    has_faq          = False
    has_accordion    = False

    for lineno, line in enumerate(lines, 1):
        if lineno < body_start:
            continue

        # Track fenced code blocks
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()

        # ── H1 in body ──
        if re.match(r'^#\s+\S', line):
            errors.append((lineno, "H1_IN_BODY",
                f"`{stripped[:60]}`"))

        # ── Heading hierarchy ──
        hm = HEADING_RE.match(line)
        if hm:
            lvl = len(hm.group(1))
            if cur_heading_lvl > 0 and lvl > cur_heading_lvl + 1:
                errors.append((lineno, "HEADING_SKIP",
                    f"H{cur_heading_lvl}→H{lvl}: `{stripped[:55]}`"))
            cur_heading_lvl = lvl

        # ── Leftover <InlineImage> tag ──
        if INLINE_TAG_RE.search(line):
            errors.append((lineno, "LEFTOVER_INLINE_IMAGE_TAG",
                "`<InlineImage>` tag not yet converted"))

        # ── Leftover import statement ──
        if INLINE_IMPORT_RE.search(line):
            errors.append((lineno, "LEFTOVER_IMPORT",
                "InlineImage import statement still present"))

        # ── Callout without bold label ──
        co = CALLOUT_OPEN_RE.search(line)
        if co and not CALLOUT_BOLD_RE.search(line):
            errors.append((lineno, "CALLOUT_NO_BOLD",
                f"`<{co.group(1)}>` missing bold label (e.g. `**注記：**`)"))

        # ── Inline <img> on its own line (not inline with text) ──
        if INLINE_IMG_RE.search(line) and stripped.startswith('<img '):
            errors.append((lineno, "IMG_OWN_LINE",
                "Inline icon `<img>` is on its own line; should be inline with text"))

        # ── Inline <img> wrapped in <Frame> ──
        if FRAME_WRAP_RE.search(line):
            errors.append((lineno, "IMG_IN_FRAME",
                "Inline icon `<img>` is wrapped in `<Frame>` (remove the Frame)"))

        # ── Unpadded table separator ──
        if is_unpadded_table_sep(line):
            errors.append((lineno, "TABLE_UNPADDED_SEP",
                f"Separator uses short dashes: `{stripped[:55]}`"))

        # ── <Frame> embedded inside a heading ──
        if FRAME_HEADING_RE.match(line):
            errors.append((lineno, "FRAME_IN_HEADING",
                f"`<Frame>` embedded in heading: `{stripped[:55]}`"))

        # ── FAQ heading / AccordionGroup presence ──
        if FAQ_HEADING_RE.match(line):
            has_faq = True
        if ACCORDION_RE.search(line):
            has_accordion = True

    # ── File-level: FAQ without AccordionGroup ──
    if has_faq and not has_accordion:
        errors.append((None, "FAQ_NO_ACCORDION",
            "FAQ heading present but no `<AccordionGroup>` found in file"))

    return errors


def main():
    files = get_queued_files()
    if not files:
        print("No queued ja/s/article/ files found.")
        sys.exit(0)

    all_errors = []
    for path in files:
        filename = path.replace("ja/s/article/", "")
        for lineno, etype, detail in check_file(path):
            all_errors.append((filename, str(lineno) if lineno else "—", etype, detail))

    if not all_errors:
        print("No formatting errors found in queued files.")
        return

    headers = ["File", "Line", "Error", "Detail"]
    col_widths = [
        max(len(headers[i]), max(len(str(row[i])) for row in all_errors))
        for i in range(len(headers))
    ]

    def fmt(cells):
        return "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(cells)) + " |"

    print(fmt(headers))
    print("| " + " | ".join("-" * w for w in col_widths) + " |")
    for row in all_errors:
        print(fmt(row))

    files_affected = len(set(r[0] for r in all_errors))
    print(f"\n{len(all_errors)} error(s) across {files_affected} file(s).")


if __name__ == "__main__":
    main()
