#!/usr/bin/env python3
"""Fix patterns not matched in fix_mdx_errors3.py due to Japanese brackets, \xa0, or curly quotes."""

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

# ── Japanese-bracket patterns (use ［ ］ not [ ]) ─────────────────────────────

# ja/s/article/360042934614.mdx – **［保存］** with Japanese brackets
fix('ja/s/article/360042934614.mdx',
    ('**［保存］**を選択して変更を保持し、モーダルを閉じます。  </Note>',
     '**［保存］**を選択して変更を保持し、モーダルを閉じます。\n\n</Note>'))

# ja/s/article/360045402273.mdx – **［バッチでフィルター］** with Japanese brackets
fix('ja/s/article/360045402273.mdx',
    ('**［バッチでフィルター］**エリアが表示されます。  </Note>',
     '**［バッチでフィルター］**エリアが表示されます。\n\n</Note>'))

# ja/s/article/36004740075.mdx – **［他 <人数>人］** with Japanese brackets
fix('ja/s/article/36004740075.mdx',
    ('**［他 <人数>人］**を選択します。',
     '**［他 \\<人数\\>人］**を選択します。'))

# ja/s/article/360043429973.mdx – **［お気に入り］** and **［フォローアップのフラグを付ける］**
fix('ja/s/article/360043429973.mdx',
    ('**［お気に入り］**メニューオプション**</td>',
     '**［お気に入り］**メニューオプション</td>'),
    ('**［フォローアップのフラグを付ける］**メニューオプション**</td>',
     '**［フォローアップのフラグを付ける］**メニューオプション</td>'))

# ── Non-breaking space (\xa0) patterns ────────────────────────────────────────

# s/article/000005941.mdx – \xa0 between "level" and "access"
fix('s/article/000005941.mdx',
    ('Users must have *Admin-*level\xa0access to the Procore Analytics tool to generate an access token.</Note>',
     'Users must have *Admin-*level\xa0access to the Procore Analytics tool to generate an access token.\n\n</Note>'))

# s/article/1500000218261.mdx – stray </b> with \xa0 non-breaking space
fix('s/article/1500000218261.mdx',
    ('<b><i></i></b>End Date</b>\xa0to create a range',
     '<b><i></i></b>End Date\xa0to create a range'),
    ('<b><i></i></b>Start Date</b> to create a range',
     '<b><i></i></b>Start Date to create a range'),
    all_occurrences=True)

# s/article/360060476953.mdx – same stray </b> patterns with \xa0
fix('s/article/360060476953.mdx',
    ('<b><i></i></b>End Date</b>\xa0to create a range',
     '<b><i></i></b>End Date\xa0to create a range'),
    ('<b><i></i></b>Start Date</b> to create a range',
     '<b><i></i></b>Start Date to create a range'),
    all_occurrences=True)

# ── Curly-quote multi-line code span ──────────────────────────────────────────

# ja/s/article/360042929154.mdx – multi-line backtick span with Unicode curly quotes
# Content uses “ and ” (left/right double quotation marks)
_lq = '“'  # "
_rq = '”'  # "
fix('ja/s/article/360042929154.mdx',
    (f'`{{{_lq}top{_rq}:100,  \n{_lq}id{_rq}:{_lq}page{_rq}}},  \n{{{_lq}top{_rq}:100,  \n{_lq}id{_rq}:{_lq}region{_rq}}}`',
     f'`{{{_lq}top{_rq}:100, {_lq}id{_rq}:{_lq}page{_rq}}}, {{{_lq}top{_rq}:100, {_lq}id{_rq}:{_lq}region{_rq}}}`'))

# Print all warnings
print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
