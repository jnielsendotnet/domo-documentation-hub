#!/usr/bin/env python3
"""
Fix programmatic formatting errors in queued ja/s/article/ MDX files.

Fixes applied (in order):
  1. H1_IN_BODY         — convert body H1 headings to H2
  2. HEADING_SKIP       — promote headings that skip levels (run after H1 fix)
  3. IMG_OWN_LINE       — join inline-icon <img> on its own line to previous line
  4. IMG_IN_FRAME       — remove <Frame> wrapper from inline-icon <img> tags
  5. TABLE_UNPADDED_SEP — repad all table column widths
  6. CALLOUT_NO_BOLD    — prepend bold label to callouts missing one
  7. FAQ_NO_ACCORDION   — convert FAQ Q&A to <AccordionGroup> components
"""

import re
import subprocess
import sys

# ── Patterns ──────────────────────────────────────────────────────────────────

INLINE_IMG_RE    = re.compile(r"<img\b[^>]*display:\s*'inline'")
CALLOUT_OPEN_RE  = re.compile(r'<(Note|Warning|Tip)>')
CALLOUT_BOLD_RE  = re.compile(r'<(?:Note|Warning|Tip)>\s*\*\*')
HEADING_RE       = re.compile(r'^(#{1,6})(\s+.+)$')
FAQ_HEADING_RE   = re.compile(r'^(#{1,6})\s.*(FAQ|よくある質問)', re.IGNORECASE)
BOLD_Q_RE        = re.compile(r'^\*\*(.+)\*\*\s*$')
CODE_FENCE_RE    = re.compile(r'^```')

CALLOUT_LABELS = {
    'Note':    '**注記：**',
    'Warning': '**重要：**',
    'Tip':     '**ヒント：**',
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_queued_files():
    result = subprocess.run(["git", "status", "--short"],
                            capture_output=True, text=True, check=True)
    files = []
    for line in result.stdout.splitlines():
        path = line[3:].strip()
        if path.startswith("ja/s/article/") and path.endswith(".mdx"):
            files.append(path)
    return files

def frontmatter_end(lines):
    """Return index of first line after the closing --- of frontmatter."""
    if not lines or lines[0].strip() != '---':
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return i + 1
    return 0

# ── Fix 1: H1 in body ─────────────────────────────────────────────────────────

def fix_h1_in_body(lines):
    fm = frontmatter_end(lines)
    in_code = False
    out = []
    for i, line in enumerate(lines):
        if i < fm:
            out.append(line)
            continue
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
        if not in_code and re.match(r'^#\s+\S', line):
            line = '#' + line   # # → ##
        out.append(line)
    return out

# ── Fix 2: Heading skip ───────────────────────────────────────────────────────

def fix_heading_skip(lines):
    fm = frontmatter_end(lines)
    in_code = False
    cur = 0
    out = []
    for i, line in enumerate(lines):
        if i < fm:
            out.append(line)
            continue
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
        if not in_code:
            hm = HEADING_RE.match(line)
            if hm:
                level = len(hm.group(1))
                if cur > 0 and level > cur + 1:
                    level = cur + 1
                    line = '#' * level + hm.group(2)
                cur = level
        out.append(line)
    return out

# ── Fix 3: Inline <img> on its own line ───────────────────────────────────────

def fix_img_own_line(lines):
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<img ') and INLINE_IMG_RE.search(line):
            # Remove preceding blank lines, then join to previous non-blank line
            while out and not out[-1].strip():
                out.pop()
            if out:
                out[-1] = out[-1].rstrip() + stripped
            else:
                out.append(stripped)
        else:
            out.append(line)
    return out

# ── Fix 4: Inline <img> wrapped in <Frame> ────────────────────────────────────

def fix_img_in_frame(lines):
    PATTERN = re.compile(
        r"<Frame>(<img\b[^>]*display:\s*'inline'[^>]*/?>)</Frame>"
    )
    return [PATTERN.sub(r'\1', line) for line in lines]

# ── Fix 5: Table padding ──────────────────────────────────────────────────────

def _is_sep_cell(cell):
    return bool(re.match(r'^\s*:?-+:?\s*$', cell))

def _parse_cells(row):
    parts = row.split('|')
    return parts[1:-1]  # drop leading/trailing empty strings from outer pipes

def fix_table_padding(lines):
    out = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith('|'):
            out.append(lines[i])
            i += 1
            continue

        # Collect the table block
        block = []
        while i < len(lines) and lines[i].startswith('|'):
            block.append(lines[i])
            i += 1

        rows = [_parse_cells(l) for l in block]
        if not rows:
            out.extend(block)
            continue

        # Find separator row
        sep_idx = None
        for j, row in enumerate(rows):
            non_empty = [c for c in row if c.strip()]
            if non_empty and all(_is_sep_cell(c) for c in non_empty):
                sep_idx = j
                break

        if sep_idx is None:
            out.extend(block)
            continue

        # Compute max content width per column (excluding separator)
        num_cols = max(len(r) for r in rows)
        col_w = [0] * num_cols
        for j, row in enumerate(rows):
            if j == sep_idx:
                continue
            for k, cell in enumerate(row):
                if k < num_cols:
                    col_w[k] = max(col_w[k], len(cell.strip()))
        col_w = [max(w, 3) for w in col_w]   # minimum 3 dashes

        # Rebuild rows
        for j, row in enumerate(rows):
            cells = []
            for k in range(num_cols):
                raw = row[k].strip() if k < len(row) else ''
                if j == sep_idx:
                    cells.append('-' * col_w[k])
                else:
                    cells.append(raw.ljust(col_w[k]))
            out.append('| ' + ' | '.join(cells) + ' |')

    return out

# ── Fix 6: Callout missing bold label ─────────────────────────────────────────

def fix_callout_no_bold(lines):
    out = []
    for line in lines:
        if CALLOUT_OPEN_RE.search(line) and not CALLOUT_BOLD_RE.search(line):
            def add_label(m):
                tag   = m.group(1)
                label = CALLOUT_LABELS.get(tag, f'**{tag}:**')
                rest  = m.group(2)
                sep   = ' ' if rest.strip() else ''
                return f'<{tag}>{label}{sep}{rest.lstrip()}'
            # Match first callout without bold on this line
            line = re.sub(
                r'<(Note|Warning|Tip)>((?!\s*\*\*).*)',
                add_label, line, count=1
            )
        out.append(line)
    return out

# ── Fix 7: FAQ without AccordionGroup ─────────────────────────────────────────

def _parse_faq_block(block_lines):
    """
    Parse Q&A pairs from the body of a FAQ section.
    Returns list of (title_str, answer_lines) or [] if no pairs found.

    Recognises two question formats:
      - Any heading within the FAQ block that ends with ? or ？
      - A line that is entirely bold text:  **Question?**
    Sub-category headings (no trailing ? / ？) are silently dropped.
    """
    qa = []
    cur_q = None
    cur_a = []

    for line in block_lines:
        s = line.strip()

        hm = HEADING_RE.match(s)
        bm = BOLD_Q_RE.match(s)

        if hm:
            q_text = hm.group(2).strip().strip('*').strip()
            if not q_text.endswith(('?', '？')):
                # Sub-category label — save in-progress Q&A and skip this line
                if cur_q is not None:
                    qa.append((cur_q, list(cur_a)))
                    cur_q = None
                    cur_a = []
                continue
            if cur_q is not None:
                qa.append((cur_q, list(cur_a)))
            cur_q = q_text
            cur_a = []

        elif bm:
            q_text = bm.group(1).strip()
            if cur_q is not None:
                qa.append((cur_q, list(cur_a)))
            cur_q = q_text
            cur_a = []

        elif cur_q is not None:
            cur_a.append(line)

    if cur_q is not None:
        qa.append((cur_q, list(cur_a)))

    # Trim blank lines from each answer
    cleaned = []
    for q, a in qa:
        while a and not a[0].strip():
            a.pop(0)
        while a and not a[-1].strip():
            a.pop()
        cleaned.append((q, a))

    return cleaned


def fix_faq_no_accordion(lines):
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]
        faq_m = FAQ_HEADING_RE.match(line)

        if not faq_m:
            out.append(line)
            i += 1
            continue

        faq_level = len(faq_m.group(1))

        # Collect block until next heading at same or higher level
        j = i + 1
        while j < len(lines):
            hm = HEADING_RE.match(lines[j])
            if hm and len(hm.group(1)) <= faq_level:
                break
            j += 1

        block = lines[i + 1:j]

        # Skip if AccordionGroup already present
        if any('<AccordionGroup' in l for l in block):
            out.append(line)
            out.extend(block)
            i = j
            continue

        qa_pairs = _parse_faq_block(block)

        if not qa_pairs:
            # Can't convert — leave as-is
            out.append(line)
            out.extend(block)
            i = j
            continue

        # Emit converted FAQ section
        out.append(line)   # FAQ heading
        out.append('')
        out.append('<AccordionGroup>')

        for q_title, a_lines in qa_pairs:
            out.append('')
            out.append(f'<Accordion title="{q_title}">')
            out.extend(a_lines)
            out.append('</Accordion>')

        out.append('')
        out.append('</AccordionGroup>')

        i = j

    return out

# ── Orchestration ─────────────────────────────────────────────────────────────

FIXES = [
    ("H1_IN_BODY",         fix_h1_in_body),
    ("HEADING_SKIP",       fix_heading_skip),
    ("IMG_OWN_LINE",       fix_img_own_line),
    ("IMG_IN_FRAME",       fix_img_in_frame),
    ("TABLE_PADDING",      fix_table_padding),
    ("CALLOUT_NO_BOLD",    fix_callout_no_bold),
    ("FAQ_NO_ACCORDION",   fix_faq_no_accordion),
]

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    lines = original.split('\n')
    for _, fn in FIXES:
        lines = fn(lines)

    updated = '\n'.join(lines)
    if updated == original:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True


def main():
    files = get_queued_files()
    if not files:
        print("No queued ja/s/article/ files found.")
        sys.exit(0)

    fixed = 0
    for path in files:
        if process_file(path):
            print(f"  fixed: {path}")
            fixed += 1

    print(f"\nDone. Fixed {fixed}/{len(files)} file(s).")


if __name__ == "__main__":
    main()
