#!/usr/bin/env python3
"""
Convert HTML tables in MDX articles to Markdown pipe tables.

Conversion rules:
  - Only top-level tables are converted; nested tables stay as HTML inside cells.
  - Tables whose cells use rowspan or colspan > 1 are skipped (kept as HTML).
  - Cell HTML is converted: <p> stripped, <b>→**, <a>→[text](url), entities decoded, etc.
  - Multiple <p> segments are joined with <br/> following the style-guide rules:
      plain→plain: <br/>  |  plain→callout: <br/>  |  callout→callout: (none)
  - Columns are space-padded so all pipe characters align vertically.
  - Pipe characters in cell content are escaped with a backslash.

Usage:
    python3 scripts/convert_html_tables.py [--dry-run] [--verbose] [files ...]

    With no files, processes every .mdx file under s/article/, s/topic/,
    de/, es/, fr/, and ja/. Files under portal/ are always skipped.
"""

import argparse
import glob
import html as _html
import re
import sys
from pathlib import Path


# ─── Low-level tag utilities ──────────────────────────────────────────────────

def find_tag_end(s: str, start: int) -> int:
    """Return the position *after* the '>' that closes the tag opening at s[start]='<'.

    Handles JSX attribute syntax such as style={{width: 20}} by tracking brace depth
    separately from HTML-attribute quotes.
    """
    i = start + 1
    brace_depth = 0
    in_dq = False  # inside "…"
    in_sq = False  # inside '…'
    while i < len(s):
        c = s[i]
        if brace_depth > 0:
            # Inside a JSX expression: only track { } to find the end
            if c == '{':
                brace_depth += 1
            elif c == '}':
                brace_depth -= 1
        elif in_dq:
            if c == '"':
                in_dq = False
        elif in_sq:
            if c == "'":
                in_sq = False
        elif c == '"':
            in_dq = True
        elif c == "'":
            in_sq = True
        elif c == '{':
            brace_depth += 1
        elif c == '}':
            brace_depth -= 1
        elif c == '>' and brace_depth == 0:
            return i + 1
        i += 1
    return len(s)  # no closing '>' found


def tag_info(s: str, pos: int):
    """Parse the tag at s[pos] and return (is_close, tag_name_lower, end_pos)."""
    end = find_tag_end(s, pos)
    inner = s[pos + 1: end - 1].strip()
    is_close = inner.startswith('/')
    if is_close:
        inner = inner[1:]
    name = re.split(r'[\s/]', inner)[0].lower() if inner.strip() else ''
    return is_close, name, end


# ─── Find top-level tables ────────────────────────────────────────────────────

def find_top_level_tables(content: str) -> list:
    """Return a list of (start, end) for each top-level <table>…</table> in content."""
    results = []
    i = 0
    while i < len(content):
        m = re.search(r'<table\b', content[i:], re.IGNORECASE)
        if not m:
            break
        start = i + m.start()
        depth = 0
        j = start
        found = False
        while j < len(content):
            lt = content.find('<', j)
            if lt == -1:
                break
            is_close, tname, tend = tag_info(content, lt)
            if tname == 'table':
                if not is_close:
                    depth += 1
                else:
                    depth -= 1
                    if depth == 0:
                        results.append((start, tend))
                        found = True
                        i = tend
                        break
            j = tend
        if not found:
            i = start + 7  # skip past '<table' and continue
    return results


def has_complex_spans(table_html: str) -> bool:
    """Return True if any cell uses rowspan or colspan > 1."""
    for m in re.finditer(r'(?:row|col)span=["\']?(\d+(?:\.\d+)?)["\']?',
                         table_html, re.IGNORECASE):
        try:
            if float(m.group(1)) > 1:
                return True
        except ValueError:
            pass
    return False


# ─── Parse table structure ────────────────────────────────────────────────────

def parse_table_rows(table_html: str) -> list:
    """Parse an HTML table into a list of rows.

    Returns:
        list of rows; each row is a list of (is_header: bool, inner_html: str).
    """
    rows = []

    # Skip past the outer opening <table …>
    lt0 = table_html.find('<')
    if lt0 == -1:
        return rows
    _, _, i = tag_info(table_html, lt0)

    depth = 1            # depth 1 = inside the outermost table
    current_cells: list = []
    in_cell = False
    cell_is_header = False
    cell_start = -1
    in_header_section = False

    while i < len(table_html):
        lt = table_html.find('<', i)
        if lt == -1:
            break

        is_close, tname, tend = tag_info(table_html, lt)

        # Track table nesting depth
        if tname == 'table':
            if not is_close:
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    # Reached the end of the outer table
                    if in_cell and cell_start >= 0:
                        current_cells.append((cell_is_header, table_html[cell_start:lt]))
                    if current_cells:
                        rows.append(current_cells)
                    break

        # Only process structural tags at depth 1 (direct children of outer table)
        if depth == 1:
            if not is_close:
                if tname == 'thead':
                    in_header_section = True
                elif tname == 'tbody':
                    in_header_section = False
                elif tname == 'tr':
                    current_cells = []
                elif tname in ('th', 'td'):
                    # Flush any accidentally open cell
                    if in_cell and cell_start >= 0:
                        current_cells.append((cell_is_header, table_html[cell_start:lt]))
                    in_cell = True
                    cell_is_header = (tname == 'th') or in_header_section
                    cell_start = tend
            else:
                if tname in ('thead', 'tbody'):
                    in_header_section = False
                elif tname == 'tr':
                    if in_cell and cell_start >= 0:
                        current_cells.append((cell_is_header, table_html[cell_start:lt]))
                        in_cell = False
                        cell_start = -1
                    if current_cells:
                        rows.append(current_cells)
                    current_cells = []
                elif tname in ('th', 'td'):
                    if in_cell and cell_start >= 0:
                        current_cells.append((cell_is_header, table_html[cell_start:lt]))
                    in_cell = False
                    cell_start = -1

        i = tend

    return rows


# ─── Cell content conversion ──────────────────────────────────────────────────

_CALLOUT_TAGS = {'note', 'warning', 'tip'}


def _is_callout(fragment: str) -> bool:
    """Return True if fragment starts with a <Note>, <Warning>, or <Tip> tag."""
    m = re.match(r'\s*<(\w+)', fragment)
    return bool(m and m.group(1).lower() in _CALLOUT_TAGS)


def _protect_images(text: str, store: list) -> str:
    """Replace <img> tags and <Frame>…</Frame> blocks with __IMG_N__ placeholders."""
    output = []
    i = 0
    while i < len(text):
        lt = text.find('<', i)
        if lt == -1:
            output.append(text[i:])
            break
        is_close, tname, tend = tag_info(text, lt)
        if not is_close and tname == 'img':
            output.append(text[i:lt])
            idx = len(store)
            store.append(text[lt:tend])
            output.append(f'__IMG_{idx}__')
            i = tend
        elif not is_close and tname == 'frame':
            depth = 0
            j = lt
            end_j = -1
            while j < len(text):
                lt2 = text.find('<', j)
                if lt2 == -1:
                    break
                ic2, tn2, te2 = tag_info(text, lt2)
                if tn2 == 'frame':
                    depth += (1 if not ic2 else -1)
                    if depth == 0:
                        end_j = te2
                        break
                j = te2
            if end_j > 0:
                output.append(text[i:lt])
                idx = len(store)
                store.append(text[lt:end_j])
                output.append(f'__IMG_{idx}__')
                i = end_j
            else:
                output.append(text[i:tend])
                i = tend
        else:
            output.append(text[i:tend])
            i = tend
    return ''.join(output)


def _protect_nested_tables(text: str, store: list) -> str:
    """Replace nested <table>…</table> blocks with __TABLE_N__ placeholders."""
    output = []
    i = 0
    while i < len(text):
        lt = text.find('<', i)
        if lt == -1:
            output.append(text[i:])
            break
        is_close, tname, tend = tag_info(text, lt)
        if tname == 'table' and not is_close:
            # Find matching </table>
            depth = 0
            j = lt
            end_j = -1
            while j < len(text):
                lt2 = text.find('<', j)
                if lt2 == -1:
                    break
                ic2, tn2, te2 = tag_info(text, lt2)
                if tn2 == 'table':
                    depth += (1 if not ic2 else -1)
                    if depth == 0:
                        end_j = te2
                        break
                j = te2
            if end_j > 0:
                output.append(text[i:lt])
                idx = len(store)
                store.append(text[lt:end_j])
                output.append(f'__TABLE_{idx}__')
                i = end_j
            else:
                output.append(text[i:tend])
                i = tend
        else:
            output.append(text[i:tend])
            i = tend
    return ''.join(output)


def _convert_lists(text: str) -> str:
    """Convert <ul>/<ol> + <li> to plain-text items joined by <br/>."""
    def _ul(m):
        items = re.findall(r'<li\b[^>]*>(.*?)</li>', m.group(1),
                           re.IGNORECASE | re.DOTALL)
        cleaned = []
        for item in items:
            c = re.sub(r'<[^>]+>', '', item).strip()
            if c:
                cleaned.append(c)
        return '<br/>'.join(cleaned)

    return re.sub(r'<[uo]l\b[^>]*>(.*?)</[uo]l>', _ul,
                  text, flags=re.IGNORECASE | re.DOTALL)


def _extract_paragraphs(text: str) -> list:
    """
    Split text into logical segments (paragraph contents, non-<p> text chunks).
    Returns a list of stripped strings.
    """
    parts = []
    remaining = text

    while True:
        m = re.search(r'<p\b[^>]*>(.*?)</p>', remaining,
                      re.IGNORECASE | re.DOTALL)
        if not m:
            tail = remaining.strip()
            if tail:
                parts.append(tail)
            break
        before = remaining[:m.start()].strip()
        if before:
            parts.append(before)
        inner = m.group(1).strip()
        if inner:
            parts.append(inner)
        remaining = remaining[m.end():]

    return parts


def _join_with_br_rules(parts: list) -> str:
    """Join content parts with <br/>, respecting callout rules."""
    if not parts:
        return ''
    result = [parts[0]]
    for i in range(1, len(parts)):
        prev = parts[i - 1]
        curr = parts[i]
        if _is_callout(prev) and _is_callout(curr):
            result.append(curr)       # no <br/> between two callouts
        else:
            result.append('<br/>' + curr)
    return ''.join(result)


def _convert_inline_html(text: str) -> str:
    """Convert inline HTML formatting to Markdown within a single text segment."""
    # Normalize <br> variants
    text = re.sub(r'<br\s*/?>', '<br/>', text, flags=re.IGNORECASE)

    # Code spans (before bold, to avoid double-wrapping)
    text = re.sub(
        r'<(?:code|span\s+class="mt-font-courier-new"|span\s+class="nowiki")[^>]*>'
        r'(.*?)'
        r'</(?:code|span)>',
        lambda m: f'`{m.group(1).strip()}`',
        text, flags=re.IGNORECASE | re.DOTALL
    )

    # Bold
    text = re.sub(
        r'<(?:b|strong)\b[^>]*>(.*?)</(?:b|strong)>',
        lambda m: f'**{m.group(1).strip()}**' if m.group(1).strip() else '',
        text, flags=re.IGNORECASE | re.DOTALL
    )

    # Italic
    text = re.sub(
        r'<(?:em|i)\b[^>]*>(.*?)</(?:em|i)>',
        lambda m: f'*{m.group(1).strip()}*' if m.group(1).strip() else '',
        text, flags=re.IGNORECASE | re.DOTALL
    )

    # Links — extract href; discard title attribute
    def _link(m):
        href_m = re.search(r'href=["\']([^"\']*)["\']', m.group(1))
        url = _html.unescape(href_m.group(1)) if href_m else '#'
        link_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        return f'[{link_text}]({url})' if link_text else url

    text = re.sub(r'<a\b([^>]*)>(.*?)</a>', _link,
                  text, flags=re.IGNORECASE | re.DOTALL)

    # Strip remaining <span> tags (keep content)
    text = re.sub(r'</?span\b[^>]*>', '', text, flags=re.IGNORECASE)

    # Strip remaining <div> wrappers (keep content) — e.g. info-box divs
    text = re.sub(r'</?div\b[^>]*>', '', text, flags=re.IGNORECASE)

    # Strip remaining tags we don't recognise (keep content)
    # Keep: <img>, <Frame>, <Note>, <Warning>, <Tip>, <br/>, __TABLE_N__
    def _strip_unknown(m):
        tag = re.split(r'[\s/]', m.group(1).strip('/'))[0].lower()
        keep = {'img', 'frame', 'note', 'warning', 'tip', 'br', 'codegroup'}
        if tag in keep or tag.startswith('accordion'):
            return m.group(0)
        return ''

    text = re.sub(r'<(/?\w[^>]*)>', _strip_unknown, text, flags=re.IGNORECASE)

    # Decode HTML entities
    text = _html.unescape(text)

    # Collapse interior whitespace (but preserve <br/> line-break markers)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()

    return text


def convert_cell(cell_html: str) -> str:
    """Convert the inner HTML of a <th>/<td> to MDX-compatible markdown inline text."""
    text = cell_html.strip()
    if not text:
        return ''

    # 1. Protect nested <table>…</table> blocks
    nested: list = []
    text = _protect_nested_tables(text, nested)

    # 2. Protect <img> tags and <Frame>…</Frame> blocks so they survive untouched
    images: list = []
    text = _protect_images(text, images)

    # 3. Flatten <ul>/<ol> lists into inline <br/>-separated items
    text = _convert_lists(text)

    # 4. Extract logical paragraphs and join with <br/> rules
    parts = _extract_paragraphs(text)
    if parts:
        # Convert inline HTML within each part first
        parts = [_convert_inline_html(p) for p in parts]
        parts = [p for p in parts if p]  # drop empty
        text = _join_with_br_rules(parts)
    else:
        text = _convert_inline_html(text)

    # 5. Collapse any remaining whitespace
    text = re.sub(r'[ \t]+', ' ', text).strip()

    # 6. Escape pipe characters that would break the markdown table
    #    Don't escape pipes that are already escaped or inside code spans
    def _escape_pipes(s: str) -> str:
        result = []
        in_code = False
        i = 0
        while i < len(s):
            c = s[i]
            if c == '`':
                in_code = not in_code
                result.append(c)
            elif c == '|' and not in_code:
                result.append('\\|')
            else:
                result.append(c)
            i += 1
        return ''.join(result)

    text = _escape_pipes(text)

    # 7. Restore image placeholders (after pipe-escaping, so image content is untouched)
    for idx, img_html in enumerate(images):
        text = text.replace(f'__IMG_{idx}__', img_html)

    # 8. Restore nested table placeholders
    for idx, tbl_html in enumerate(nested):
        text = text.replace(f'__TABLE_{idx}__', tbl_html)

    return text


# ─── Markdown table formatting ────────────────────────────────────────────────

def format_markdown_table(rows: list) -> str:
    """Format parsed rows as a padded Markdown pipe table.

    Args:
        rows: list of rows from parse_table_rows().
              Each row: list of (is_header: bool, inner_html: str).

    Returns:
        Markdown table string, or empty string if conversion is not possible.
    """
    if not rows:
        return ''

    # Convert all cell HTML to markdown text
    converted: list = []
    for row in rows:
        converted.append([(is_hdr, convert_cell(ch)) for is_hdr, ch in row])

    # Identify header row: first row that contains any th cells
    header_idx = next(
        (i for i, row in enumerate(converted) if any(h for h, _ in row)),
        0  # fall back to first row if no th found
    )

    headers = [cell for _, cell in converted[header_idx]]
    data_rows = [
        [cell for _, cell in row]
        for i, row in enumerate(converted)
        if i != header_idx
    ]

    # Determine column count
    num_cols = max(len(headers),
                   max((len(r) for r in data_rows), default=0),
                   1)

    def pad_to(lst, n):
        return lst + [''] * (n - len(lst))

    headers = pad_to(headers, num_cols)
    data_rows = [pad_to(r, num_cols) for r in data_rows]

    # Column widths: at least 3 characters (for '---')
    col_widths = [max(3, len(h)) for h in headers]
    for row in data_rows:
        for col, cell in enumerate(row[:num_cols]):
            col_widths[col] = max(col_widths[col], len(cell))

    def fmt_row(cells):
        padded = [cells[c].ljust(col_widths[c]) if c < len(cells)
                  else ' ' * col_widths[c]
                  for c in range(num_cols)]
        return '| ' + ' | '.join(padded) + ' |'

    def fmt_sep():
        return '| ' + ' | '.join('-' * w for w in col_widths) + ' |'

    lines = [fmt_row(headers), fmt_sep()]
    lines += [fmt_row(r) for r in data_rows]
    return '\n'.join(lines)


# ─── File processing ──────────────────────────────────────────────────────────

def convert_file(filepath: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Process one MDX file. Returns True if the file was (or would be) changed."""
    path = Path(filepath)

    # Never touch files under portal/
    try:
        rel = path.resolve().relative_to(Path.cwd().resolve())
        if rel.parts and rel.parts[0] == 'portal':
            return False
    except ValueError:
        pass

    try:
        content = path.read_text(encoding='utf-8')
    except OSError as exc:
        print(f'  SKIP {filepath}: {exc}', file=sys.stderr)
        return False

    original = content
    table_positions = find_top_level_tables(content)
    if not table_positions:
        return False

    replacements = []  # (start, end, markdown)
    counts = {'converted': 0, 'skipped_spans': 0, 'skipped_empty': 0, 'errors': 0}

    for start, end in table_positions:
        table_html = content[start:end]

        # Skip tables that are already inside a Markdown pipe-table row.
        # After a prior conversion pass, nested tables land inside lines like
        # "| cell content <table>…</table> |".  Those should stay as HTML.
        line_start = content.rfind('\n', 0, start) + 1
        line_prefix = content[line_start:start].lstrip()
        if line_prefix.startswith('|'):
            continue

        if has_complex_spans(table_html):
            counts['skipped_spans'] += 1
            continue

        rows = parse_table_rows(table_html)
        if not rows:
            counts['skipped_empty'] += 1
            continue

        try:
            markdown = format_markdown_table(rows)
        except Exception as exc:
            if verbose:
                print(f'  ERROR in {filepath}: {exc}')
            counts['errors'] += 1
            continue

        if not markdown:
            counts['skipped_empty'] += 1
            continue

        replacements.append((start, end, markdown))
        counts['converted'] += 1

    if not replacements:
        return False

    # Apply in reverse order so positions stay valid
    for start, end, markdown in reversed(replacements):
        content = content[:start] + markdown + content[end:]

    if content == original:
        return False

    if not dry_run:
        path.write_text(content, encoding='utf-8')

    if verbose:
        parts = [f'{counts["converted"]} converted']
        if counts['skipped_spans']:
            parts.append(f'{counts["skipped_spans"]} skipped (rowspan/colspan)')
        if counts['errors']:
            parts.append(f'{counts["errors"]} errors')
        print(f'  {filepath}: {", ".join(parts)}')

    return True


# ─── Entry point ─────────────────────────────────────────────────────────────

DEFAULT_DIRS = ['s/article', 's/topic', 'de', 'es', 'fr', 'ja']


def main():
    parser = argparse.ArgumentParser(
        description='Convert HTML tables in MDX articles to Markdown pipe tables.')
    parser.add_argument('files', nargs='*',
                        help='MDX files to process (default: all .mdx in repo directories)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without writing files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print per-file details')
    parser.add_argument('--dirs', default=None,
                        help='Comma-separated directories to scan (overrides default list)')
    args = parser.parse_args()

    # Collect files to process
    if args.files:
        files = list(args.files)
    else:
        dirs = args.dirs.split(',') if args.dirs else DEFAULT_DIRS
        files = []
        for d in dirs:
            files.extend(glob.glob(f'{d}/**/*.mdx', recursive=True))
        files.sort()

    if not files:
        print('No .mdx files found.')
        return

    changed = 0
    total = 0
    for f in files:
        total += 1
        if convert_file(f, dry_run=args.dry_run, verbose=args.verbose):
            changed += 1
            if not args.verbose:
                # Print a dot for progress without spamming
                print(f, flush=True)

    action = 'Would change' if args.dry_run else 'Changed'
    print(f'\n{action} {changed} / {total} files.')


if __name__ == '__main__':
    main()
