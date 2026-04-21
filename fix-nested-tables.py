#!/usr/bin/env python3
"""
fix-nested-tables.py

Fixes two categories of structural issues in queued Japanese MDX articles:

1. NESTED MARKDOWN TABLES
   When a markdown table row contains extra | pipe characters that include
   --- separator cells, the row holds a flattened nested table.  This script
   extracts those nested tables, converts them to inline HTML, and embeds
   them in the appropriate outer cell.  The outer table header and separator
   rows are trimmed back to the true outer column count.

2. JAPANESE CALLOUT TEXT NOT IN COMPONENT TAGS
   a. Malformed wrapping — a <Note>, <Warning>, or <Tip> tag opens at the
      start of a line that is actually a table row, and the matching closing
      tag appears at the end of a later table row.  The component tags are
      removed from those positions; the inline callout labels remaining in
      the cells are handled by (b).
   b. Unwrapped bold labels — **注記：**, **重要：**, **ヒント：** (and
      variants with the colon outside the bold span) appear inside a table
      cell but are not wrapped in a component.  Each label and its following
      text are wrapped in <Note>, <Warning>, or <Tip> respectively.
   c. Unwrapped plain labels — 注記：text or 重要：text appearing as plain
      text in a table cell (not in parentheses) are bolded and wrapped.

Usage:
    python3 fix-nested-tables.py           # modify files in place
    python3 fix-nested-tables.py --dry-run # report only, no writes
"""

import re
import sys
import subprocess
from pathlib import Path

REPO = Path(__file__).parent

# ─── callout label → (component_tag, canonical_label) ───────────────────────
CALLOUT_MAP = {
    '注記': ('Note',    '注記'),
    '重要': ('Warning', '重要'),
    'ヒント': ('Tip',   'ヒント'),
    '注意': ('Warning', '注意'),
    '警告': ('Warning', '警告'),
}

# All label keys joined for alternation
_ALL_LABELS = '|'.join(CALLOUT_MAP)

# ─── helpers ─────────────────────────────────────────────────────────────────

def get_queued_files():
    r = subprocess.run(
        ['git', 'diff', '--name-only'],
        capture_output=True, text=True, cwd=str(REPO)
    )
    return [f for f in r.stdout.strip().split('\n')
            if f.startswith('ja/s/article/')]


def parse_row(line):
    """Split a markdown table row into stripped cells (no leading/trailing '')."""
    row = line.strip()
    if row.startswith('|'):
        row = row[1:]
    if row.endswith('|'):
        row = row[:-1]
    return [c.strip() for c in row.split('|')]


def is_sep_cell(cell):
    return bool(re.match(r'^-+$', cell.strip()))


def outer_col_count(header_cells):
    """Count meaningful outer columns = (index of last non-empty header cell) + 1."""
    last = -1
    for i, c in enumerate(header_cells):
        if c:
            last = i
    return last + 1 if last >= 0 else 1


def is_table_like_line(line):
    """True if line is part of a markdown table (including malformed-wrapped rows)."""
    s = line.strip()
    if s.startswith('|'):
        return True
    # malformed: <Note/Warning/Tip>... | table content
    if re.match(r'^<(?:Note|Warning|Tip)>', s) and '|' in s:
        return True
    # closing tag at the end of a table row: | ... |</Tag>
    if re.search(r'\|</(?:Note|Warning|Tip)>\s*$', s):
        return True
    return False


def find_table_blocks(lines):
    """Return [(start, end), ...] index ranges for each markdown table block."""
    blocks = []
    i = 0
    while i < len(lines):
        if is_table_like_line(lines[i]):
            start = i
            while i < len(lines) and is_table_like_line(lines[i]):
                i += 1
            end = i
            # Must have at least header + separator
            if end - start >= 2:
                blocks.append((start, end))
        else:
            i += 1
    return blocks


# ─── 1. NESTED TABLE FIX ─────────────────────────────────────────────────────

def _parse_nested_from_extra(extra):
    """
    Given the extra cells from a row (everything beyond the outer columns),
    parse out the nested table.

    Returns (nested_header, nested_rows, M, pushed_outer) or
            (None, None, None, None) if no separator found.

    nested_header : list[str]  — column headers (may be empty strings)
    nested_rows   : list[list[str]]
    M             : int — nested column count
    pushed_outer  : list[str] — single-cell groups that are probably outer
                               column content displaced by the nested table
    """
    first_sep = next((i for i, c in enumerate(extra) if is_sep_cell(c)), None)
    if first_sep is None:
        return None, None, None, None

    # Consecutive seps → column count M
    sep_end = first_sep
    while sep_end < len(extra) and is_sep_cell(extra[sep_end]):
        sep_end += 1
    M = sep_end - first_sep

    # Header cells: non-empty cells before the separator
    before = [c for c in extra[:first_sep] if c]
    if len(before) >= M:
        nested_header = before[:M]
    else:
        nested_header = before + [''] * (M - len(before))

    # After separator: group non-empty cells
    nested_rows = []
    pushed_outer = []
    current = []
    for cell in extra[sep_end:]:
        if cell == '':
            if current:
                if len(current) == M:
                    nested_rows.append(current)
                elif len(current) == 1 and nested_rows:
                    # Single cell appearing after legitimate rows →
                    # probably an outer column that was displaced
                    pushed_outer.append(current[0])
                current = []
        else:
            current.append(cell)
    if current:
        if len(current) == M:
            nested_rows.append(current)
        elif len(current) == 1:
            pushed_outer.append(current[0])

    return nested_header, nested_rows, M, pushed_outer


def _build_html_table(header, rows):
    """Render an HTML table from header cells and data rows."""
    has_header = any(h for h in header)
    parts = ['<table>']
    if has_header:
        parts.append('<thead><tr>')
        parts += [f'<th>{h}</th>' for h in header]
        parts.append('</tr></thead>')
    parts.append('<tbody>')
    for row in rows:
        parts.append('<tr>')
        parts += [f'<td>{_wrap_callouts_in_text(c)}</td>' for c in row]
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)


def fix_nested_tables(table_lines):
    """
    Process one markdown table block.  Returns (new_lines, changed).
    """
    if len(table_lines) < 2:
        return table_lines, False

    # Determine outer column count from the header row
    # (header may be a plain | row or a malformed-wrapped row — use parse_row)
    header_cells = parse_row(table_lines[0])
    N = outer_col_count(header_cells)

    # Fast path: skip tables with no nested tables at all
    def _row_has_nested(line):
        cells = parse_row(line)
        return len(cells) > N and any(is_sep_cell(c) for c in cells[N:])

    if not any(_row_has_nested(l) for l in table_lines[2:]):
        return table_lines, False

    new_data = []
    changed = False

    for line in table_lines[2:]:
        cells = parse_row(line)

        # Simple row (no extra cells with ---)
        if len(cells) <= N or not any(is_sep_cell(c) for c in cells[N:]):
            row = (cells + [''] * N)[:N]
            new_data.append(row)
            continue

        outer = (cells[:N] + [''] * N)[:N]
        extra = cells[N:]

        nested_header, nested_rows, M, pushed = _parse_nested_from_extra(extra)

        if nested_header is None:
            new_data.append(outer)
            continue

        html = _build_html_table(nested_header, nested_rows)

        # Embed HTML in the last non-empty outer cell
        embed_idx = next(
            (i for i in range(N - 1, -1, -1) if outer[i]),
            N - 1
        )
        outer[embed_idx] = outer[embed_idx] + html

        # Place displaced outer-column content in the first empty slot after embed
        fill = embed_idx + 1
        for pushed_cell in pushed:
            while fill < N and outer[fill]:
                fill += 1
            if fill < N:
                outer[fill] = pushed_cell
                fill += 1

        new_data.append(outer)
        changed = True

    if not changed:
        return table_lines, False

    # Rebuild: trim header/separator to N columns, keep data rows
    hdr = (header_cells + [''] * N)[:N]
    widths = [max(3, len(h)) for h in hdr]

    def fmt(cells):
        padded = []
        for i, c in enumerate(cells[:N]):
            w = widths[i] if i < len(widths) else 3
            padded.append(c.ljust(w))
        return '| ' + ' | '.join(padded) + ' |'

    sep = '| ' + ' | '.join('-' * w for w in widths) + ' |'

    new_lines = [fmt(hdr), sep] + [fmt(r) for r in new_data]
    return new_lines, True


# ─── 2. CALLOUT WRAPPING ─────────────────────────────────────────────────────

# Matches bold callout labels — colon may be inside or outside the bold span
# Group 1 = label word; group 2 = separator style ('：**' or '**：')
_BOLD_LABEL_RE = re.compile(
    rf'\*\*({_ALL_LABELS})([：:]\*\*|\*\*[：:])'
)

# Matches plain (unbolded) callout labels NOT preceded by * or （
_PLAIN_LABEL_RE = re.compile(
    rf'(?<![*（])\b({_ALL_LABELS})[：:](?!\*\*)'
)


def _wrap_callouts_in_text(text):
    """
    Wrap all unprotected callout labels in *text* (a single cell or td content).

    Handles:
      **注記：**content  →  <Note>**注記：**content</Note>
      **注記**：content  →  <Note>**注記：**content</Note>
      注記：content      →  <Note>**注記：**content</Note>
        (skips （注記：…） parenthetical forms)

    Multiple callouts in one cell: each wraps up to the start of the next.
    """
    if not text:
        return text

    # Skip if any component tag already present (conservative: leave complex
    # cases for manual review)
    if re.search(r'<(?:Note|Warning|Tip)>', text):
        return text

    # --- Step 1: normalise **label**：text → **label：**text ----------------
    def _normalise_colon(m):
        label = m.group(1)
        style = m.group(2)          # either '：**' or '**：'
        if style.startswith('**'):  # '**：' means colon is outside bold
            return f'**{label}：**'
        return m.group(0)           # already '：**', leave as is

    text = _BOLD_LABEL_RE.sub(_normalise_colon, text)

    # --- Step 2: collect all callout start positions -------------------------
    # After normalisation every bold label looks like **label：**
    bold_re = re.compile(rf'\*\*({_ALL_LABELS})[：:]\*\*')
    plain_re = re.compile(rf'(?<![*（])\b({_ALL_LABELS})[：:](?!\*\*)')

    # Find all start positions with their label and whether they are bold
    spans = []
    for m in bold_re.finditer(text):
        spans.append((m.start(), m.end(), m.group(1), True))
    for m in plain_re.finditer(text):
        # Skip positions already covered by a bold match
        if not any(bs <= m.start() < be for bs, be, _, _ in spans):
            spans.append((m.start(), m.end(), m.group(1), False))

    if not spans:
        return text

    # Sort by position
    spans.sort(key=lambda x: x[0])

    parts = []
    prev = 0

    for i, (start, end, label, is_bold) in enumerate(spans):
        # Text before this callout
        parts.append(text[prev:start])

        # Content of the callout: from end of label to start of next or end
        if i + 1 < len(spans):
            content_end = spans[i + 1][0]
        else:
            content_end = len(text)

        content = text[end:content_end].rstrip()
        tag = CALLOUT_MAP[label][0]
        parts.append(f'<{tag}>**{label}：**{content}</{tag}>')

        prev = content_end

    parts.append(text[prev:])
    return ''.join(parts)


def fix_callouts_in_row(line):
    """
    Apply _wrap_callouts_in_text to each cell of a markdown table row.
    Returns (new_line, changed).
    """
    if not line.strip().startswith('|'):
        return line, False

    cells = parse_row(line)
    new_cells = [_wrap_callouts_in_text(c) for c in cells]

    if new_cells == cells:
        return line, False

    return '| ' + ' | '.join(new_cells) + ' |', True


# ─── 3. MALFORMED COMPONENT WRAPPING ─────────────────────────────────────────
#
# Pattern: <Warning>**重要：** | col | col |   ← start of wrapped section
#          | row |                              ← middle rows (no tag)
#          | row |</Warning>                   ← end of wrapped section
#
# Fix: remove the opening tag prefix; remove the closing tag suffix.
# After this the inline callout labels are handled by fix_callouts_in_row.

_MALFORMED_OPEN_RE = re.compile(r'^<(Note|Warning|Tip)>(.*?)\|')


def fix_malformed_wrapping(lines):
    """
    Scan all lines.  When a line starts with a component opening tag and also
    contains '|', remove the tag prefix.  Then find and remove the matching
    closing tag (which appears at the end of a later table row line).

    Returns (new_lines, changed).
    """
    new_lines = list(lines)
    changed = False

    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        m = _MALFORMED_OPEN_RE.match(line)
        if m:
            tag = m.group(1)
            close_tag = f'</{tag}>'
            # Remove everything before the first '|'
            pipe_pos = line.index('|', len(f'<{tag}>'))
            new_lines[i] = line[pipe_pos:]
            changed = True

            # Remove the matching closing tag (within the next ~50 lines)
            for j in range(i, min(i + 50, len(new_lines))):
                if close_tag in new_lines[j]:
                    new_lines[j] = new_lines[j].replace(close_tag, '').rstrip()
                    break
        i += 1

    return new_lines, changed


# ─── FILE PROCESSING ─────────────────────────────────────────────────────────

def process_file(filepath, dry_run=False):
    full = REPO / filepath
    try:
        content = full.read_text(encoding='utf-8')
    except Exception as e:
        print(f'  ERROR {filepath}: {e}')
        return False

    lines = content.split('\n')

    # Phase 1: remove malformed component-wrapping around table rows
    lines, mf_changed = fix_malformed_wrapping(lines)

    # Phase 2 & 3: process each table block
    nested_changed = False
    callout_changed = False

    for start, end in reversed(find_table_blocks(lines)):
        block = lines[start:end]

        # Fix nested tables first (so callout wrapping sees clean cells)
        block, nc = fix_nested_tables(block)
        if nc:
            nested_changed = True

        # Fix callout labels in every table row of the block
        new_block = []
        for bl in block:
            fixed, cc = fix_callouts_in_row(bl)
            new_block.append(fixed)
            if cc:
                callout_changed = True
        block = new_block

        lines[start:end] = block

    overall = mf_changed or nested_changed or callout_changed
    if overall:
        if not dry_run:
            full.write_text('\n'.join(lines), encoding='utf-8')
        reasons = []
        if nested_changed:
            reasons.append('nested tables')
        if callout_changed:
            reasons.append('callout wrapping')
        if mf_changed:
            reasons.append('malformed component tags')
        print(f'  FIXED ({", ".join(reasons)}): {filepath}')

    return overall


def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print('DRY RUN — no files will be modified\n')

    files = get_queued_files()
    print(f'Scanning {len(files)} queued Japanese articles...\n')

    fixed = 0
    for f in files:
        if process_file(f, dry_run=dry_run):
            fixed += 1

    print(f"\n{'Would fix' if dry_run else 'Fixed'} {fixed} of {len(files)} files.")


if __name__ == '__main__':
    main()
