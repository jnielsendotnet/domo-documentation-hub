#!/usr/bin/env python3
"""
Domo KB Article Synthesis Script
Applies programmatic formatting fixes to modified/new MDX articles in s/article/

Transformations applied:
  1. Absolute domo-support URLs → relative /s/article/... paths
  2. Remove title="..." attributes from Markdown links
  3. Fix ****over-escaped bold**** → **bold**
  4. Fix missing space after closing **bold** (**text**word → **text** word)
  5. Convert * bullet points → - bullet points
  6. Convert standalone HTML tables → Markdown pipe tables
  7. Convert #### FAQ sections → <AccordionGroup>/<Accordion>
  8. Consolidate sequential `IP` inline spans → fenced code block
  9. Remove unused InlineImage imports
 10. Expand compressed list items inside <Note>/<Warning>/<Tip> tags

Usage:
  python3 synthesize_articles.py            # process all files
  python3 synthesize_articles.py --dry-run  # preview without writing
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
ARTICLE_DIR = REPO_ROOT / "s" / "article"

MODIFIED_FILES = [
    "1500000218261", "1500000555201", "1500000888261", "1500001012441",
    "1500002644442", "1500003419382", "1500009366622", "1500011338741",
    "360042932074",  "360042932114",  "360042932474",  "360042932514",
    "360042932554",  "360042932654",  "360042932914",  "360042933074",
    "360042933494",  "360042933734",  "360042933834",  "360042934014",
    "360042934234",  "360042934294",  "360042934334",  "360042934394",
    "360042934454",  "360042934494",  "360042934674",  "360043212294",
    "360043428113",  "360043428253",  "360043428293",  "360043428373",
    "360043428993",  "360043429773",  "360043429973",  "360043430513",
    "360043431133",  "360043431633",  "360043432813",  "360043432953",
    "360043432993",  "360043433033",  "360043433453",  "360043433653",
    "360043433813",  "360043434093",  "360043434413",  "360043434433",
    "360043435013",  "360043435113",  "360043436133",  "360043436273",
    "360043436313",  "360043436753",  "360043436873",  "360043437013",
    "360043437093",  "360043437373",  "360043437733",  "360043437773",
    "360043437793",  "360043437993",  "360043438433",  "360043442453",
    "360044258533",  "360044876094",  "360044876614",  "360044876874",
    "360045120554",  "360045402273",  "360047553253",  "360050912013",
    "360051709994",  "360052122394",  "360052884153",  "360055259234",
    "360056669354",  "360057013754",  "360057087393",  "360058713713",
    "360058716313",  "360058716453",  "360058757134",  "360058759794",
    "360058760154",  "360059173794",  "360060476953",  "360060508773",
    "360061691114",  "4402322966807", "4403367344023", "4406022964375",
    "4409512475927", "4411277235351", "4415839663639", "4423536836631",
    "5366610360983", "5563069185815", "7579340458903", "8275510785559",
    "9645646505111",
]

NEW_FILES = [
    "1500000196462", "360043437533", "360057028014", "4405291644311", "4407022160791",
]

ALL_FILES = MODIFIED_FILES + NEW_FILES


# ──────────────────────────────────────────────────────────────────────────────
# Utility: code-block-aware processing
# ──────────────────────────────────────────────────────────────────────────────

def split_prose_and_code(content: str):
    """
    Yield (segment_text, is_code_block) for each alternating prose/code region.
    Fenced code blocks (```...```) are marked is_code_block=True.
    """
    pattern = re.compile(r'(```[^\n]*\n.*?```)', re.DOTALL)
    last = 0
    for m in pattern.finditer(content):
        if m.start() > last:
            yield content[last:m.start()], False
        yield m.group(0), True
        last = m.end()
    if last < len(content):
        yield content[last:], False


def apply_to_prose(content: str, fn) -> str:
    """Apply fn only to non-fenced-code-block segments."""
    return "".join(fn(seg) if not is_code else seg
                   for seg, is_code in split_prose_and_code(content))


# ──────────────────────────────────────────────────────────────────────────────
# 1. Absolute → relative links
# ──────────────────────────────────────────────────────────────────────────────

_ABS_LINK_RE = re.compile(
    r'https://domo-support\.domo\.com(/s/article/[\w/-]+?)(?:\?[^")\s\]]*)?(?=["\s)\]])',
)

def fix_absolute_links(content: str) -> str:
    return apply_to_prose(content, lambda t: _ABS_LINK_RE.sub(r'\1', t))


# ──────────────────────────────────────────────────────────────────────────────
# 2. Remove title="..." from Markdown links
# ──────────────────────────────────────────────────────────────────────────────

_LINK_TITLE_RE = re.compile(r'(\[[^\]]*\]\()([^")\s][^)"]*?)\s+"[^"]*"(\))')

def remove_link_title_attrs(content: str) -> str:
    return apply_to_prose(content, lambda t: _LINK_TITLE_RE.sub(r'\1\2\3', t))


# ──────────────────────────────────────────────────────────────────────────────
# 3. Fix ****over-escaped bold****
# ──────────────────────────────────────────────────────────────────────────────

def fix_over_escaped_bold(content: str) -> str:
    def _fix(text: str) -> str:
        for n in (8, 6, 4):               # longest patterns first
            stars = r'\*' * n
            text = re.sub(rf'{stars}([^*\n]+?){stars}', r'**\1**', text)
        return text
    return apply_to_prose(content, _fix)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Fix missing space after **bold** closing marker
# ──────────────────────────────────────────────────────────────────────────────

_BOLD_SPACE_RE = re.compile(r'(\*\*[^*\n]+?\*\*)([A-Za-z(])')

def fix_bold_spacing(content: str) -> str:
    return apply_to_prose(content, lambda t: _BOLD_SPACE_RE.sub(r'\1 \2', t))


# ──────────────────────────────────────────────────────────────────────────────
# 5. Convert * bullet points to -
# ──────────────────────────────────────────────────────────────────────────────

def fix_bullets(content: str) -> str:
    def _fix(text: str) -> str:
        # Only convert line-start bullets; (?!\*) avoids touching ** bold markers
        return re.sub(r'^(\s*)\* (?!\*)', r'\1- ', text, flags=re.MULTILINE)
    return apply_to_prose(content, _fix)


# ──────────────────────────────────────────────────────────────────────────────
# 6. Convert standalone HTML tables → Markdown pipe tables
# ──────────────────────────────────────────────────────────────────────────────

def _html_cell_to_md(html: str) -> str:
    """Strip HTML from a table cell and return Markdown text."""
    t = html
    t = re.sub(r'<b\b[^>]*>(.*?)</b>',            r'**\1**',  t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'<i\b[^>]*>(.*?)</i>',             r'*\1*',    t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(
        r'<span[^>]+class="[^"]*mt-font-courier-new[^"]*"[^>]*>(.*?)</span>',
        r'`\1`', t, flags=re.DOTALL | re.IGNORECASE,
    )
    t = re.sub(r'<span[^>]*>(.*?)</span>',          r'\1',      t, flags=re.DOTALL | re.IGNORECASE)
    # Links: domo-support absolute → relative
    t = re.sub(
        r'<a\b[^>]*href="https://domo-support\.domo\.com(/s/article/[\w/-]+?)[^"]*"[^>]*>(.*?)</a>',
        r'[\2](\1)', t, flags=re.DOTALL | re.IGNORECASE,
    )
    t = re.sub(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'<p[^>]*>(.*?)</p>',               r'\1 ',     t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'<br\s*/?>',                        ' ',        t, flags=re.IGNORECASE)
    t = re.sub(r'<li[^>]*>(.*?)</li>',              r'- \1 ',   t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'<[uo]l[^>]*>(.*?)</[uo]l>',       r'\1',      t, flags=re.DOTALL | re.IGNORECASE)
    t = re.sub(r'<[^>]+>', '', t)
    t = (t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
          .replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')
          .replace('&ldquo;', '\u201c').replace('&rdquo;', '\u201d'))
    return re.sub(r'\s+', ' ', t).strip()


def _table_has_nested(html: str) -> bool:
    m = re.search(r'<table\b[^>]*>(.*)</table>', html, re.DOTALL | re.IGNORECASE)
    if not m:
        return False
    return bool(re.search(r'<table\b', m.group(1), re.IGNORECASE))


def _html_table_to_md(html: str) -> str | None:
    """Convert a non-nested HTML table to a Markdown pipe table. Returns None if unsafe."""
    if _table_has_nested(html):
        return None

    headers: list[str] = []
    rows: list[list[str]] = []

    thead_m = re.search(r'<thead\b[^>]*>(.*?)</thead>', html, re.DOTALL | re.IGNORECASE)
    if thead_m:
        headers = [
            _html_cell_to_md(m.group(1))
            for m in re.finditer(r'<t[hd]\b[^>]*>(.*?)</t[hd]>', thead_m.group(1),
                                 re.DOTALL | re.IGNORECASE)
        ]

    tbody_m = re.search(r'<tbody\b[^>]*>(.*?)</tbody>', html, re.DOTALL | re.IGNORECASE)
    if tbody_m:
        for row_m in re.finditer(r'<tr\b[^>]*>(.*?)</tr>', tbody_m.group(1),
                                  re.DOTALL | re.IGNORECASE):
            cells = [
                _html_cell_to_md(m.group(1))
                for m in re.finditer(r'<td\b[^>]*>(.*?)</td>', row_m.group(1),
                                     re.DOTALL | re.IGNORECASE)
            ]
            if cells:
                rows.append(cells)

    if not headers and rows:
        headers, rows = rows[0], rows[1:]

    if not headers:
        return None

    n = max(len(headers), max((len(r) for r in rows), default=0))
    headers = list(headers) + [''] * (n - len(headers))
    rows = [list(r) + [''] * (n - len(r)) for r in rows]

    def esc(s: str) -> str:
        return s.replace('|', r'\|')

    widths = [max(len(esc(h)), 3) for h in headers]
    for row in rows:
        for i, cell in enumerate(row[:n]):
            widths[i] = max(widths[i], len(esc(cell)))

    def pad(s: str, w: int) -> str:
        e = esc(s)
        return e + ' ' * (w - len(e))

    lines = [
        '| ' + ' | '.join(pad(h, widths[i]) for i, h in enumerate(headers)) + ' |',
        '| ' + ' | '.join('-' * w for w in widths) + ' |',
    ]
    for row in rows:
        lines.append('| ' + ' | '.join(pad(row[i] if i < n else '', widths[i]) for i in range(n)) + ' |')

    return '\n'.join(lines)


def _outermost_table_spans(text: str):
    """Yield (start, end) positions of outermost <table>…</table> in text."""
    depth = 0
    start = None
    i = 0
    while i < len(text):
        om = re.match(r'<table\b', text[i:], re.IGNORECASE)
        cm = re.match(r'</table\s*>', text[i:], re.IGNORECASE)
        if om:
            if depth == 0:
                start = i
            depth += 1
            i += om.end()
        elif cm:
            depth -= 1
            i += cm.end()
            if depth == 0 and start is not None:
                yield start, i
                start = None
        else:
            i += 1


def convert_html_tables(content: str) -> str:
    """Convert standalone (line-start) HTML tables to Markdown pipe tables."""
    def _process_prose(text: str) -> str:
        replacements = []
        for start, end in _outermost_table_spans(text):
            # Only convert tables that start at the beginning of a line
            line_start = text.rfind('\n', 0, start) + 1
            if text[line_start:start].strip():
                continue           # inline/nested table — leave it alone
            md = _html_table_to_md(text[start:end])
            if md:
                replacements.append((start, end, md))
        for s, e, md in reversed(replacements):
            text = text[:s] + md + text[e:]
        return text
    return apply_to_prose(content, _process_prose)


# ──────────────────────────────────────────────────────────────────────────────
# 7. Convert #### FAQ sections → <AccordionGroup>/<Accordion>
# ──────────────────────────────────────────────────────────────────────────────

_FAQ_SECTION_RE = re.compile(
    r'(##\s+(?:FAQ|FAQs|Frequently Asked Questions)[^\n]*\n)'
    r'((?:\n*####\s+[^\n]+\n(?:(?!####|##\s)[^\n]*\n)*)+)',
    re.IGNORECASE,
)
_QA_ITEM_RE = re.compile(r'####\s+([^\n]+)\n((?:(?!####)[^\n]*\n)*)', re.DOTALL)


def fix_faq_sections(content: str) -> str:
    """Convert #### FAQ question headings to <AccordionGroup>/<Accordion> components."""
    if '<AccordionGroup>' in content:
        return content     # Already converted

    def _convert(m: re.Match) -> str:
        header = m.group(1)
        body   = m.group(2)
        items  = []
        for qa in _QA_ITEM_RE.finditer(body):
            q = qa.group(1).strip()
            a = qa.group(2).strip()
            items.append(f'<Accordion title="{q}">\n{a}\n</Accordion>')
        if not items:
            return m.group(0)
        block = '\n\n'.join(items)
        return f'{header}\n<AccordionGroup>\n\n{block}\n\n</AccordionGroup>\n'

    return _FAQ_SECTION_RE.sub(_convert, content)


# ──────────────────────────────────────────────────────────────────────────────
# 8. Consolidate sequential inline `IP` code spans → fenced code block
# ──────────────────────────────────────────────────────────────────────────────

_IP_RE = re.compile(r'^\s*`(\d{1,3}(?:\.\d{1,3}){3})`\s*$')

def consolidate_ip_blocks(content: str) -> str:
    """
    Turn runs of standalone `IP` lines (possibly with blank lines between them)
    into a single fenced code block.
    """
    def _process(text: str) -> str:
        lines   = text.split('\n')
        out     = []
        i       = 0
        while i < len(lines):
            if _IP_RE.match(lines[i]):
                # Collect all IP lines in this run (blank lines allowed between)
                ip_vals = []
                j = i
                while j < len(lines):
                    if _IP_RE.match(lines[j]):
                        ip_vals.append(_IP_RE.match(lines[j]).group(1))
                        j += 1
                    elif lines[j].strip() == '':
                        # Peek ahead for another IP
                        k = j + 1
                        while k < len(lines) and lines[k].strip() == '':
                            k += 1
                        if k < len(lines) and _IP_RE.match(lines[k]):
                            j = k        # skip blanks, continue run
                        else:
                            break        # blanks followed by non-IP — end run
                    else:
                        break
                if len(ip_vals) >= 2:
                    out.append('```')
                    out.extend(ip_vals)
                    out.append('```')
                    i = j
                else:
                    out.append(lines[i])
                    i += 1
            else:
                out.append(lines[i])
                i += 1
        return '\n'.join(out)
    return apply_to_prose(content, _process)


# ──────────────────────────────────────────────────────────────────────────────
# 9. Remove unused InlineImage imports
# ──────────────────────────────────────────────────────────────────────────────

_IMPORT_INLINE_IMAGE_RE = re.compile(r'^import\s*\{InlineImage\}[^\n]*\n', re.MULTILINE)

def remove_unused_inline_image_import(content: str) -> str:
    """Remove `import {InlineImage}` when <InlineImage is not used in the file."""
    if '<InlineImage' not in content:
        content = _IMPORT_INLINE_IMAGE_RE.sub('', content)
    return content


# ──────────────────────────────────────────────────────────────────────────────
# 10. Expand compressed list items inside <Note>/<Warning>/<Tip> tags
# ──────────────────────────────────────────────────────────────────────────────

_CALLOUT_RE = re.compile(r'<(Note|Warning|Tip)>(.+?)</\1>', re.DOTALL | re.IGNORECASE)
_COMPRESSED_LIST_RE = re.compile(r'(?:\s{2,}|\n)(-\s|\d+\.\s)')


def fix_compressed_callouts(content: str) -> str:
    """
    When a Note/Warning/Tip tag contains list items compressed onto one line
    (multiple spaces + "- " or "1. " as separators), split them out below the tag.
    """
    def _fix(m: re.Match) -> str:
        tag   = m.group(1)
        inner = m.group(2)

        # Only trigger when multiple list-item starts appear separated by 2+ spaces
        if not _COMPRESSED_LIST_RE.search(inner):
            return m.group(0)

        # Split on the list-item separators (2+ spaces or newline + bullet/number)
        parts = re.split(r'\s{2,}(?=-\s|\d+\.\s)', inner.strip())
        if len(parts) < 2:
            return m.group(0)

        lead  = parts[0].strip()
        items = [p.strip() for p in parts[1:] if p.strip()]

        callout = f'<{tag}>{lead}</{tag}>' if lead else ''
        list_md = '\n'.join(items)
        return f'{callout}\n\n{list_md}'.lstrip('\n') if callout else list_md

    return apply_to_prose(content, lambda t: _CALLOUT_RE.sub(_fix, t))


# ──────────────────────────────────────────────────────────────────────────────
# 11. Merge standalone inline <img> icons with adjacent text
# ──────────────────────────────────────────────────────────────────────────────

_INLINE_IMG_ONLY_RE = re.compile(r'^\s*(<img\b[^>]*style=\{\{[^>]*/>\s*)$')
_IMG_BLOCK_LINE_RE  = re.compile(
    r'^\s*(?:#{1,6} |</?Frame\b|</?Note\b|</?Warning\b|</?Tip\b'
    r'|</?Accordion\b|</?AccordionGroup\b|```)'
)


def merge_standalone_inline_images(content: str) -> str:
    """
    An inline icon <img style={{...}}/> that sits alone on its own paragraph line
    should be joined with the surrounding text. This function detects that pattern
    and merges the img onto the same line as the adjacent text before and/or after it.

    Blank lines between the img and adjacent text are consumed in the merge.
    Does NOT merge with headings, <Frame>, <Note>, <Warning>, <Tip>, <Accordion>,
    code fences, or other standalone inline <img> lines.
    """
    lines = content.split('\n')
    n     = len(lines)

    # Track lines inside fenced code blocks — never touch those
    in_code: list[bool] = []
    inside  = False
    for line in lines:
        if line.strip().startswith('```'):
            inside = not inside
        in_code.append(inside)

    skip    : set[int]       = set()
    replace : dict[int, str] = {}

    for img_idx, line in enumerate(lines):
        if in_code[img_idx]:
            continue
        m = _INLINE_IMG_ONLY_RE.match(line)
        if not m:
            continue
        img_tag = m.group(1).strip()

        # Nearest preceding non-blank line
        pi = img_idx - 1
        while pi >= 0 and not lines[pi].strip():
            pi -= 1

        # Nearest following non-blank line
        ni = img_idx + 1
        while ni < n and not lines[ni].strip():
            ni += 1

        def _is_text(idx: int) -> bool:
            if idx < 0 or idx >= n:
                return False
            if in_code[idx]:
                return False
            ln = lines[idx]
            return (bool(ln.strip())
                    and not _IMG_BLOCK_LINE_RE.match(ln)
                    and not _INLINE_IMG_ONLY_RE.match(ln))

        has_prev = _is_text(pi)
        has_next = _is_text(ni)

        if has_prev and has_next:
            # prev … <blank lines> … img … <blank lines> … next  →  prev img next
            replace[pi] = lines[pi].rstrip() + ' ' + img_tag + ' ' + lines[ni].lstrip()
            for j in range(pi + 1, ni + 1):
                skip.add(j)
        elif has_prev:
            # prev … img  →  prev img
            replace[pi] = lines[pi].rstrip() + ' ' + img_tag
            for j in range(pi + 1, img_idx + 1):
                skip.add(j)
        elif has_next:
            # img … next  →  img next
            replace[img_idx] = img_tag + ' ' + lines[ni].lstrip()
            for j in range(img_idx + 1, ni + 1):
                skip.add(j)
        # else: no adjacent text — leave the img alone

    out = []
    for idx, line in enumerate(lines):
        if idx in skip:
            continue
        out.append(replace.get(idx, line))
    return '\n'.join(out)


# ──────────────────────────────────────────────────────────────────────────────
# 6b. Connector-article variant: every Markdown table → HTML
#     (swapped in for convert_html_tables when title contains "connector")
# ──────────────────────────────────────────────────────────────────────────────

def _is_connector_article(content: str) -> bool:
    """Return True when the frontmatter title contains the word 'connector'."""
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content[:500],
                  re.MULTILINE | re.IGNORECASE)
    return bool(m and re.search(r'\bconnector\b', m.group(1), re.IGNORECASE))


def _md_cell_to_html(cell: str) -> str:
    """Convert Markdown inline formatting inside a table cell to HTML."""
    t = cell.strip().replace(r'\|', '|')
    t = re.sub(r'\*\*(.+?)\*\*',                                   r'<b>\1</b>',    t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)',             r'<i>\1</i>',    t)
    t = re.sub(r'`([^`]+)`',
               r'<span class="mt-font-courier-new">\1</span>',      t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',                         r'<a href="\2">\1</a>', t)
    return t


def _parse_md_row(row: str) -> list[str]:
    parts = row.strip().split('|')
    return [p.strip() for p in parts[1:-1]]


_MD_TABLE_RE = re.compile(
    r'^([ \t]*\|[^\n]+\|\n)'            # header row
    r'([ \t]*\|[ \t]*[-:| \t]+\|\n)'    # separator row
    r'((?:[ \t]*\|[^\n]+\|[ \t]*\n?)*)',# data rows (0+)
    re.MULTILINE,
)


def _single_md_table_to_html(md: str) -> str:
    """Convert one Markdown pipe table to a connector-style HTML table."""
    lines = [l for l in md.strip().split('\n') if l.strip()]
    if len(lines) < 2:
        return md

    headers = _parse_md_row(lines[0])
    rows    = [_parse_md_row(l) for l in lines[2:] if l.strip()]

    def cell_tag(text: str, tag: str) -> str:
        return f'<{tag} colspan="1" rowspan="1"><p>{_md_cell_to_html(text)}</p></{tag}>'

    out = ['<table border="1" cellpadding="1" cellspacing="1">',
           '  <thead>', '    <tr>']
    for h in headers:
        out.append(f'      {cell_tag(h, "th")}')
    out += ['    </tr>', '  </thead>', '  <tbody>']
    for row in rows:
        row = list(row) + [''] * max(0, len(headers) - len(row))
        out.append('    <tr>')
        for cell in row[:len(headers)]:
            out.append(f'      {cell_tag(cell, "td")}')
        out.append('    </tr>')
    out += ['  </tbody>', '</table>']
    return '\n'.join(out)


def convert_markdown_tables_to_html(content: str) -> str:
    """
    Connector-article path: convert every Markdown pipe table to HTML.
    Tables whose cells already contain HTML tags (malformed nested tables)
    are left untouched — they need manual review.
    """
    def _replace(m: re.Match) -> str:
        md = m.group(0)
        if re.search(r'<[a-zA-Z]', md):   # hybrid/broken cell — skip
            return md
        return _single_md_table_to_html(md)
    return apply_to_prose(content, lambda t: _MD_TABLE_RE.sub(_replace, t))


# ──────────────────────────────────────────────────────────────────────────────
# 6c. Fix orphaned table rows after partial HTML conversion
#     (connector articles only — run before convert_markdown_tables_to_html)
# ──────────────────────────────────────────────────────────────────────────────

# Matches the block that appears right after a </table> when the programmatic
# converter failed on a <Warning>/<Note>/<Tip> inside a Markdown table cell:
#
#   \n+
#   [optional single-line description]          ← goes into the empty last TD
#   <Warning>callout text. |                    ← callout + end-of-cell pipe
#   | Field2 | Description2. |                 ← remaining pipe rows
#   ...
#   </Warning>
_ORPHAN_AFTER_TABLE_RE = re.compile(
    r'\n+'                                   # newlines after </table>
    r'(?:(?!<|[ \t]*\|)([^\n]+)\n)?'        # optional description line (1)
    r'<(Warning|Note|Tip)\b[^>]*>'           # opening callout tag (2)
    r'(.*?)'                                 # callout text up to end-of-cell pipe (3)
    r'\s*\|\s*\n'                            # end-of-cell pipe + newline
    r'((?:[ \t]*\|[^\n]*\n?)*)'             # remaining pipe rows (4)
    r'</(?:Warning|Note|Tip)>',              # closing callout tag
    re.DOTALL | re.IGNORECASE,
)

_EMPTY_TD_RE = re.compile(
    r'(<td\b[^>]*>)\s*(<p>\s*</p>)\s*(</td>)',
    re.IGNORECASE,
)


def fix_orphaned_table_rows(content: str) -> str:
    """
    Detect and repair the pattern produced when the programmatic converter
    failed to handle Domo callout tags inside Markdown table cells.

    Before:
      <table>…<td><p>Hostname</p></td><td><p></p></td></tr></tbody></table>
      Enter your SFTP server hostname.
      <Warning>Important: … |
      | Port | Enter your SFTP server port number. |
      …
      | Passphrase | Enter the passphrase … |</Warning>

    After:
      <table>…<td><p>Hostname</p></td><td><p>Enter your SFTP server hostname.</p></td></tr>
        <tr><td><p>Port</p></td><td><p>Enter your SFTP server port number.</p></td></tr>
        …
      </tbody></table>
      <Warning>Important: …</Warning>
    """
    def _process(text: str) -> str:
        spans = list(_outermost_table_spans(text))
        if not spans:
            return text

        replacements = []
        for tbl_start, tbl_end in spans:
            table_html = text[tbl_start:tbl_end]
            m = _ORPHAN_AFTER_TABLE_RE.match(text, tbl_end)
            if not m or m.start() != tbl_end:
                continue

            desc          = (m.group(1) or '').strip()
            tag           = m.group(2)
            callout_text  = m.group(3).strip()
            pipe_rows_raw = m.group(4) or ''

            new_table = table_html

            # Fill the last empty TD with the orphaned description
            if desc:
                td_matches = list(_EMPTY_TD_RE.finditer(new_table))
                if td_matches:
                    last = td_matches[-1]
                    new_table = (
                        new_table[:last.start()]
                        + f'{last.group(1)}<p>{desc}</p>{last.group(3)}'
                        + new_table[last.end():]
                    )

            # Parse remaining pipe rows and add as <tr> elements before </tbody>
            new_rows = []
            for row_line in pipe_rows_raw.split('\n'):
                row_line = row_line.strip()
                if not row_line or re.match(r'\|[-:| \t]+\|', row_line):
                    continue  # skip blank lines and separator rows
                cells = _parse_md_row(row_line)
                if not cells:
                    continue
                tr_html = '    <tr>\n'
                for cell in cells:
                    tr_html += (
                        f'      <td colspan="1" rowspan="1">'
                        f'<p>{_md_cell_to_html(cell)}</p></td>\n'
                    )
                tr_html += '    </tr>'
                new_rows.append(tr_html)

            if new_rows:
                tbody_m = re.search(r'</tbody>', new_table, re.IGNORECASE)
                if tbody_m:
                    ins = tbody_m.start()
                    new_table = (
                        new_table[:ins]
                        + '\n'.join(new_rows) + '\n'
                        + new_table[ins:]
                    )

            callout_block = f'\n<{tag}>{callout_text}</{tag}>' if callout_text else ''
            replacements.append((tbl_start, m.end(), new_table + callout_block))

        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]
        return text

    return apply_to_prose(content, _process)


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline
# ──────────────────────────────────────────────────────────────────────────────

TRANSFORMS: list[tuple[str, callable]] = [
    ("fix_absolute_links",                fix_absolute_links),
    ("remove_link_title_attrs",           remove_link_title_attrs),
    ("fix_over_escaped_bold",             fix_over_escaped_bold),
    ("fix_bold_spacing",                  fix_bold_spacing),
    ("fix_bullets",                       fix_bullets),
    ("convert_html_tables",               convert_html_tables),
    ("fix_faq_sections",                  fix_faq_sections),
    ("consolidate_ip_blocks",             consolidate_ip_blocks),
    ("remove_unused_inline_image_import", remove_unused_inline_image_import),
    ("fix_compressed_callouts",           fix_compressed_callouts),
    ("merge_standalone_inline_images",    merge_standalone_inline_images),
]


def process_file(filename: str, dry_run: bool = False) -> tuple[bool, list[str]]:
    """
    Apply all transforms to one file.
    Returns (changed: bool, applied_transforms: list[str]).

    Table strategy is title-aware:
      - Title contains "connector" → every Markdown table is converted to HTML
        (convert_html_tables is swapped for convert_markdown_tables_to_html)
      - Otherwise → standalone HTML tables are converted to Markdown (default)
    """
    path = ARTICLE_DIR / f"{filename}.mdx"
    if not path.exists():
        return False, ["FILE NOT FOUND"]

    original   = path.read_text(encoding='utf-8')
    content    = original
    applied    = []
    connector  = _is_connector_article(original)

    for name, fn in TRANSFORMS:
        if name == "convert_html_tables" and connector:
            # For connector articles: fix orphaned rows first, then convert MD→HTML
            for sub_name, sub_fn in [
                ("fix_orphaned_table_rows",       fix_orphaned_table_rows),
                ("convert_markdown_tables_to_html", convert_markdown_tables_to_html),
            ]:
                updated = sub_fn(content)
                if updated != content:
                    applied.append(sub_name)
                    content = updated
            continue

        updated = fn(content)
        if updated != content:
            applied.append(name)
            content = updated

    if content != original:
        if not dry_run:
            path.write_text(content, encoding='utf-8')
        return True, applied

    return False, []


def main() -> None:
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN — no files will be written\n")

    print(f"Repository : {REPO_ROOT}")
    print(f"Article dir: {ARTICLE_DIR}")
    print(f"Files      : {len(ALL_FILES)} ({len(MODIFIED_FILES)} modified + {len(NEW_FILES)} new)\n")

    changed_count  = 0
    skipped_count  = 0
    unchanged_count = 0

    for filename in ALL_FILES:
        changed, applied = process_file(filename, dry_run=dry_run)
        if "FILE NOT FOUND" in applied:
            print(f"  SKIP  {filename}.mdx")
            skipped_count += 1
        elif changed:
            verb = "WOULD UPDATE" if dry_run else "UPDATED"
            print(f"  ✓ {verb}  {filename}.mdx")
            print(f"           [{', '.join(applied)}]")
            changed_count += 1
        else:
            unchanged_count += 1
            # Suppress unchanged output unless verbose
            if '--verbose' in sys.argv:
                print(f"  —  {filename}.mdx  (unchanged)")

    print(f"\n{'─' * 60}")
    action = "Would update" if dry_run else "Updated"
    print(f"  {action}:  {changed_count}")
    print(f"  Unchanged: {unchanged_count}")
    if skipped_count:
        print(f"  Skipped:   {skipped_count}")
    print()


if __name__ == "__main__":
    main()
