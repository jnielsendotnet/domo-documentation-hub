#!/usr/bin/env python3
"""Fix remaining MDX parsing errors - follow-up to fix_mdx_errors.py."""

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

# ── 1. <Note>/<Warning> block structure (remaining cases) ────────────────────

# s/article/000005931.mdx – Note starts with inline content + list inside
fix('s/article/000005931.mdx',
    ('<Note>**Note:** - After inserting the record',
     '<Note>\n\n**Note:** - After inserting the record'))

# s/article/000005941.mdx – Note starts with inline content + list inside
fix('s/article/000005941.mdx',
    ('<Note>**Note:** - You must have the Procore Analytics tool',
     '<Note>\n\n**Note:** - You must have the Procore Analytics tool'))

# s/article/360042934394.mdx – Note starts with inline + has list
fix('s/article/360042934394.mdx',
    ('<Note>**Note:** Throughout this article, we use the following time-related abbreviations:',
     '<Note>\n\n**Note:** Throughout this article, we use the following time-related abbreviations:'))

# s/article/1500000555201.mdx – Note with RSA key followed by numbered list inside
fix('s/article/1500000555201.mdx',
    ('<Note>**Note:** For more information about the RSA\\_PUBLIC\\_KEY\\_2\\_FP property',
     '<Note>\n\n**Note:** For more information about the RSA\\_PUBLIC\\_KEY\\_2\\_FP property'))

# ja/s/article/360042931814.mdx – Note has non-breaking space (\xa0) after **注記：**
fix('ja/s/article/360042931814.mdx',
    ('<Note>**注記：**\xa0**Snowflake',
     '<Note>\n\n**注記：**\xa0**Snowflake'))

# ja/s/article/360043437093.mdx – same Snowflake Note pattern
fix('ja/s/article/360043437093.mdx',
    ('<Note>**注記：**\xa0**Snowflake',
     '<Note>\n\n**注記：**\xa0**Snowflake'))

# ja/s/article/1500000555201.mdx – Note with 3 spaces + content + numbered list inside
fix('ja/s/article/1500000555201.mdx',
    ('<Note>   **注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FP',
     '<Note>\n\n**注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FP'))

# ja/s/article/360043212294.mdx – Note starts with **注記：** then \n\n- list
fix('ja/s/article/360043212294.mdx',
    ('<Note>**注記：**\n\n- **［ファイルが変更されるたびに更新］**',
     '<Note>\n\n**注記：**\n\n- **［ファイルが変更されるたびに更新］**'))

# ja/s/article/360042934614.mdx – Note with many spaces + content + numbered list inside (case 1)
fix('ja/s/article/360042934614.mdx',
    ('<Note>         **注記：****［が次の範囲内：］**',
     '<Note>\n\n**注記：****［が次の範囲内：］**'))

# ja/s/article/360042934614.mdx – Note with 3 spaces + content + numbered list inside (case 2)
fix('ja/s/article/360042934614.mdx',
    ('<Note>   **注記：**ユーザーにルールが適用される',
     '<Note>\n\n**注記：**ユーザーにルールが適用される'))

# ja/s/article/360042933494.mdx – Note with 2 spaces + content + list inside
fix('ja/s/article/360042933494.mdx',
    ('<Note>  **注記：****［Choose file］**を使用してアップロードできるのは、HTMLファイルのみです。',
     '<Note>\n\n**注記：****［Choose file］**を使用してアップロードできるのは、HTMLファイルのみです。'))

# ── 2. Unescaped < in date operators ─────────────────────────────────────────

# ja/s/article/000005697.mdx – file uses backslash-escaped underscores
fix('ja/s/article/000005697.mdx',
    ('sys\\_created\\_on<2016-09-27', 'sys\\_created\\_on\\<2016-09-27'), all_occurrences=True)

# ── 3. Angle brackets around special tokens ───────────────────────────────────

# ja/s/article/360043428253.mdx – <ダッシュボード名> in italic link text
fix('ja/s/article/360043428253.mdx',
    ('*［<ダッシュボード名>を削除］*', '*［\\<ダッシュボード名\\>を削除］*'))

# ja/s/article/000005331.mdx – second occurrence of *<major.minor.patch>*
fix('ja/s/article/000005331.mdx',
    ('*<major.minor.patch>*', '*\\<major.minor.patch\\>*'))

# s/article/000005331.mdx – second occurrence of *<major.minor.patch>*
fix('s/article/000005331.mdx',
    ('*<major.minor.patch>*', '*\\<major.minor.patch\\>*'))

# s/article/360043437733.mdx – <PARAM> tokens in markdown table (EN version)
fix('s/article/360043437733.mdx',
    ('--username <USERNAME>', '--username \\<USERNAME\\>'),
    ('--password <PASSWORD>', '--password \\<PASSWORD\\>'),
    ('--server <SERVERNAME>', '--server \\<SERVERNAME\\>'),
    ('--token <TOKEN>', '--token \\<TOKEN\\>'),
    ('--dir <DIRECTORY>', '--dir \\<DIRECTORY\\>'),
    ('--data <FILENAME>', '--data \\<FILENAME\\>'),
    ('--temp-dir <TEMP>', '--temp-dir \\<TEMP\\>'),
    ('--query <QUERY>', '--query \\<QUERY\\>'),
    ('--queryfile <QUERYFILE>', '--queryfile \\<QUERYFILE\\>'),
    ('--exportfile <EXPORTNAME>', '--exportfile \\<EXPORTNAME\\>'),
    ('--id <ID>', '--id \\<ID\\>'),
    ('--entities <ENTITIES>', '--entities \\<ENTITIES\\>'),
    ('--filename <NAME>', '--filename \\<NAME\\>'),
    ('--limit <LIMIT>', '--limit \\<LIMIT\\>'),
    ('--offset <OFFSET>', '--offset \\<OFFSET\\>'),
    ('--term <TERM>', '--term \\<TERM\\>'))

# ja/s/article/360059173794.mdx – <path>, <user>, <account> in Japanese context
fix('ja/s/article/360059173794.mdx',
    ('- <path>は作成した', '- \\<path\\>は作成した'),
    ('- <user>はSnowflake', '- \\<user\\>はSnowflake'),
    ('- <account>はアカウント', '- \\<account\\>はアカウント'))

# ja/s/article/1500000888261.mdx – <path>, <user>, <account> in Japanese context
fix('ja/s/article/1500000888261.mdx',
    ('- <path>は作成した', '- \\<path\\>は作成した'),
    ('- <user>はSnowflake', '- \\<user\\>はSnowflake'),
    ('- <account>はアカウント', '- \\<account\\>はアカウント'))

# ja/s/article/1500000555201.mdx – same JA context (inside Note + numbered list)
fix('ja/s/article/1500000555201.mdx',
    ('- <path>は作成した', '- \\<path\\>は作成した'),
    ('- <user>はSnowflake', '- \\<user\\>はSnowflake'),
    ('- <account>はアカウント', '- \\<account\\>はアカウント'))

# ── 4. Curly brace escaping ───────────────────────────────────────────────────

# ja/s/article/000005844.mdx – JSON braces in markdown table
# File content uses \" (backslash+quote) and \_ (backslash+underscore)
fix('ja/s/article/000005844.mdx',
    ('\\"filters\\": {\\"Filter\\_One\\": {\\"name\\": \\"property\\", \\"required\\": null},\\"Filter\\_Two\\":{\\"name\\": \\"property\\_stats\\", \\"required\\": true}}',
     '\\"filters\\": &#123;\\"Filter\\_One\\": &#123;\\"name\\": \\"property\\", \\"required\\": null&#125;,\\"Filter\\_Two\\":&#123;\\"name\\": \\"property\\_stats\\", \\"required\\": true&#125;&#125;'),
    ('\\"Filter\\_One\\":{\\"name\\": \\"property\\", \\"required\\": null},\\"Filter\\_Two\\": {\\"name\\": \\"property\\_stats\\", \\"required\\": true}',
     '\\"Filter\\_One\\":&#123;\\"name\\": \\"property\\", \\"required\\": null&#125;,\\"Filter\\_Two\\": &#123;\\"name\\": \\"property\\_stats\\", \\"required\\": true&#125;'))

# ── 5. <datestamp> in log filenames ──────────────────────────────────────────

fix('ja/s/article/360043437373.mdx',
    ('Domo\\_Workbench\\_<datestamp>.logおよび Domo\\_Workbench\\_<Datestamp>\\_001\\_DomoWorkbench64.log',
     'Domo\\_Workbench\\_\\<datestamp\\>.logおよび Domo\\_Workbench\\_\\<Datestamp\\>\\_001\\_DomoWorkbench64.log'))

fix('s/article/360042932554.mdx',
    ('Domo\\_Workbench\\_<datestamp>.log and\xa0Domo\\_Workbench\\_<Datestamp>\\_001\\_DomoWorkbench64.log',
     'Domo\\_Workbench\\_\\<datestamp\\>.log and\xa0Domo\\_Workbench\\_\\<Datestamp\\>\\_001\\_DomoWorkbench64.log'))

# Print all warnings
print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
