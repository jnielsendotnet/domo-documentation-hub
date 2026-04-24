#!/usr/bin/env python3
"""Fix 11 remaining MDX parsing errors (round 6)."""

import re

def r(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def w(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

warnings = []

def fix(path, *pairs, all_occurrences=False):
    content = r(path)
    original = content
    for old, new in pairs:
        if old not in content:
            warnings.append(f"NOT FOUND in {path}: {repr(old[:80])}")
        if all_occurrences:
            content = content.replace(old, new)
        else:
            content = content.replace(old, new, 1)
    if content != original:
        w(path, content)
        print(f"  fixed: {path}")
    else:
        print(f"  no changes: {path}")

def fix_td_bold(path, *line_nums):
    """Replace **text** with <b>text</b> on specific lines."""
    lines = r(path).split('\n')
    changed = False
    for ln in line_nums:
        old = lines[ln - 1]
        new = re.sub(r'\*\*([^*\n]+)\*\*', r'<b>\1</b>', old)
        if old != new:
            lines[ln - 1] = new
            changed = True
        else:
            warnings.append(f"No bold found on line {ln}: {path}")
    if changed:
        w(path, '\n'.join(lines))
        print(f"  fixed: {path}")
    else:
        print(f"  no changes: {path}")

# ── Note opening/closing inline ───────────────────────────────────────────────

# ja/s/article/1500000888261.mdx – <Note> opening inline + closing inline
fix('ja/s/article/1500000888261.mdx',
    ('<Note>   **注記：**',
     '<Note>\n\n**注記：**'),
    ('確認します。  </Note>',
     '確認します。\n\n</Note>'))

# ja/s/article/360058760154.mdx – <Note> opening inline only
fix('ja/s/article/360058760154.mdx',
    ('<Note>   **注記：**',
     '<Note>\n\n**注記：**'))

# s/article/360045402273.mdx – </Note> closing inline
fix('s/article/360045402273.mdx',
    ('this query:</Note>',
     'this query:\n\n</Note>'))

# s/article/360042933494.mdx – stray <Note> with no content before </Accordion>
fix('s/article/360042933494.mdx',
    ('<Note>\n</Accordion>',
     '</Accordion>'))

# ── **bold** inside <td> ──────────────────────────────────────────────────────

# ja/s/article/360043434413.mdx – line 44 has **[アカウント]** etc inside <td>
fix_td_bold('ja/s/article/360043434413.mdx', 44)

# ── Angle bracket escaping ────────────────────────────────────────────────────

# ja/s/article/360043437733.mdx – <uploadfile.script> inside **bold** at line 322
fix('ja/s/article/360043437733.mdx',
    ('の例の<uploadfile.script>は、自分のスクリプトファイルの名前に変更してください。',
     'の例の\\<uploadfile.script\\>は、自分のスクリプトファイルの名前に変更してください。'))

# ja/s/article/4402322966807.mdx – <アカウント> inside *emphasis* at line 303
fix('ja/s/article/4402322966807.mdx',
    ('Snowflake <アカウント>',
     'Snowflake \\<アカウント\\>'))

# ── Self-closing <img> fix ────────────────────────────────────────────────────

# ja/s/article/360042925374.mdx – <img> not self-closed inside <div> on line 36
fix('ja/s/article/360042925374.mdx',
    ('bruce.png?origin=mt-web">',
     'bruce.png?origin=mt-web"/>'))

# ── HTML structure fixes ──────────────────────────────────────────────────────

# s/article/360042928374.mdx – orphaned </td></tr> after Note text; add <table> opening
fix('s/article/360042928374.mdx',
    ('**Note:** There might be a possibility of having other/additional supported values for Reporting Period. Contact Sage Intacct for other possible Reporting Duration values for filtering the data. </td></tr><tr><td',
     '<table><tbody><tr><td colspan="2"><b>Note:</b> There might be a possibility of having other/additional supported values for Reporting Period. Contact Sage Intacct for other possible Reporting Duration values for filtering the data.</td></tr><tr><td'))

# s/article/360042931734.mdx – <p><pre>subject: History</pre></p> inline nesting
fix('s/article/360042931734.mdx',
    ('<p><pre>&#123; "subject": "History" &#125;</pre></p>',
     '<pre>&#123; "subject": "History" &#125;</pre>'))

# s/article/360042922994.mdx – unclosed <li> and table at end of line 128
fix('s/article/360042922994.mdx',
    ('running the index would cause inefficiencies. \n',
     'running the index would cause inefficiencies.</li></ul></ul></td></tr></tbody></table>\n'))

# Print all warnings
print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
