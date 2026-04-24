#!/usr/bin/env python3
"""Fix MDX parsing errors across KB articles."""
import re, sys

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
            warnings.append(f"NOT FOUND in {path}: {repr(old[:70])}")
        if all_occurrences:
            content = content.replace(old, new)
        else:
            content = content.replace(old, new, 1)
    if content != original:
        w(path, content)
        print(f"  fixed: {path}")
    else:
        print(f"  no changes: {path}")

# ── 1. Tag typos / case ───────────────────────────────────────────────────────

fix('de/s/article/360042934294.mdx',
    ('<Tipe>', '<Tip>'))

fix('ja/s/article/000005827.mdx',
    ('</tip>', '</Tip>'))

# ── 2. <Note>/<Warning>/<Tip> block structure (add blank line after tag) ──────
# Pattern: <Tag>text => <Tag>\n\ntext so block content renders correctly

fix('ja/s/article/000005150.mdx',
    ('<Note>     **注記：**入力DataSetのすべてのバッチを時々置き換え',
     '<Note>\n\n**注記：**入力DataSetのすべてのバッチを時々置き換え'))

fix('ja/s/article/000005184.mdx',
    ('<Note>  **注記：**ダッシュボードでDomoリンクを使用している場合は',
     '<Note>\n\n**注記：**ダッシュボードでDomoリンクを使用している場合は'),
    ('<Note>  **注記：**ダッシュボードには、ネストされたDataFlowを含めることはできません。',
     '<Note>\n\n**注記：**ダッシュボードには、ネストされたDataFlowを含めることはできません。'))

fix('ja/s/article/000005648.mdx',
    ('<Note>**注記：** - **モバイルAppの設定を編集',
     '<Note>\n\n**注記：** - **モバイルAppの設定を編集'))

fix('ja/s/article/000005839.mdx',
    ('<Note>   **注記：**\n   - インスタンスのデフォルトの権限と',
     '<Note>\n\n**注記：**\n- インスタンスのデフォルトの権限と'))

fix('ja/s/article/1500000555201.mdx',
    ('<Note>   **注記：**\n   - セキュリティ管理者（例えばSECURITYADMIN権限を持つユーザー）以上がユーザーを変更できます。',
     '<Note>\n\n**注記：**\n- セキュリティ管理者（例えばSECURITYADMIN権限を持つユーザー）以上がユーザーを変更できます。'))

fix('ja/s/article/360042926694.mdx',
    ('<Warning>**重要：**DomoコネクターでOAuth認証を使用する機能にGoogleによって変更が加えられたことにより',
     '<Warning>\n\n**重要：**DomoコネクターでOAuth認証を使用する機能にGoogleによって変更が加えられたことにより'))

fix('ja/s/article/360042931814.mdx',
    ('<Note>**注記：** **Snowflakeは2025年11月以降',
     '<Note>\n\n**注記：** **Snowflakeは2025年11月以降'))

fix('ja/s/article/360042932474.mdx',
    ('<Warning>  **重要：**SFTPサーバーのホスト名は',
     '<Warning>\n\n**重要：**SFTPサーバーのホスト名は'))

fix('ja/s/article/360042933494.mdx',
    ('<Note>**注記：**\n\n- **オプトインメッセージ**を作成する',
     '<Note>\n\n**注記：**\n\n- **オプトインメッセージ**を作成する'))

fix('ja/s/article/360042934614.mdx',
    ('<Note>**注記：**\n\n- **［ファイルが変更されるたびに更新］**オプション',
     '<Note>\n\n**注記：**\n\n- **［ファイルが変更されるたびに更新］**オプション'))

fix('ja/s/article/360043212294.mdx',
    ('<Note>**注記：**\n\n- 実行中のジョブは',
     '<Note>\n\n**注記：**\n\n- 実行中のジョブは'))

fix('ja/s/article/360043437093.mdx',
    ('<Note>**注記：**このオプションを選択した場合は、データ更新方法を',
     '<Note>\n\n**注記：**このオプションを選択した場合は、データ更新方法を'))

fix('ja/s/article/360043437993.mdx',
    ('<Note>   **注記：****［表ビューを許可］**と**［フィルターの変更を許可］**は',
     '<Note>\n\n**注記：****［表ビューを許可］**と**［フィルターの変更を許可］**は'))

fix('ja/s/article/360045402273.mdx',
    ('<Note>     **注記：**このオプションを選択した場合は、データ更新方法を',
     '<Note>\n\n**注記：**このオプションを選択した場合は、データ更新方法を'))

fix('ja/s/article/360055259234.mdx',
    ('<Note>     **注記：**このオプションを選択した場合は、データ更新方法を',
     '<Note>\n\n**注記：**このオプションを選択した場合は、データ更新方法を'))

fix('ja/s/article/360059173794.mdx',
    ('<Note>   **注記：**\n   - セキュリティ管理者（例えばSECURITYADMIN権限を持つユーザー）以上がユーザーを変更できます。',
     '<Note>\n\n**注記：**\n- セキュリティ管理者（例えばSECURITYADMIN権限を持つユーザー）以上がユーザーを変更できます。'))

fix('s/article/000005492.mdx',
    ('<Note>**Note:** If a person or group is assigned to multiple policies, they are granted the rights of the most permissive policy.\n4.',
     '<Note>\n\n**Note:** If a person or group is assigned to multiple policies, they are granted the rights of the most permissive policy.\n4.'))

fix('s/article/000005586.mdx',
    ('<Warning>**Important:** Three levels of Oracle-Domo architecture exist.',
     '<Warning>\n\n**Important:** Three levels of Oracle-Domo architecture exist.'))

fix('s/article/000005931.mdx',
    ('<Note>**Note:** You can only upload HTML files via ** Choose file**.\n-',
     '<Note>\n\n**Note:** You can only upload HTML files via ** Choose file**.\n-'))

fix('s/article/000005941.mdx',
    ('<Note>**Note:** Throughout this article, we use the following time-related abbreviations:\n\n-',
     '<Note>\n\n**Note:** Throughout this article, we use the following time-related abbreviations:\n\n-'))

fix('s/article/1500000555201.mdx',
    ('<Note>**Note:** - After inserting the record',
     '<Note>\n\n**Note:** - After inserting the record'),
    ('<Note>**Note:** - You must have the Procore Analytics tool',
     '<Note>\n\n**Note:** - You must have the Procore Analytics tool'))

fix('s/article/360042933494.mdx',
    ('<Note>**Note:** You can only upload HTML files via ** Choose file**.\n-',
     '<Note>\n\n**Note:** You can only upload HTML files via ** Choose file**.\n-'))

fix('s/article/360042934394.mdx',
    ('<Note>**Note:** To learn more about consumption',
     '<Note>\n\n**Note:** To learn more about consumption'))

fix('s/article/4403367344023.mdx',
    ('<Note>**Note:** - The content must be owned or explicitly shared',
     '<Note>\n\n**Note:** - The content must be owned or explicitly shared'))

fix('s/article/8275510785559.mdx',
    ('<Warning>**Important:** - Using an existing DataSet will overwrite',
     '<Warning>\n\n**Important:** - Using an existing DataSet will overwrite'))

# s/article/360042934294.mdx – Note inside table cell (line 99)
fix('s/article/360042934294.mdx',
    ('<Note>**Note:** Some functions are only available when this checkbox is checked.',
     '<Note>\n\n**Note:** Some functions are only available when this checkbox is checked.'))

fix('s/article/360045402273.mdx',
    ('<Note>**Note:** This is only available for Domo on Databricks users.\n2.',
     '<Note>\n\n**Note:** This is only available for Domo on Databricks users.\n2.'))

# ── 3. </Note> indentation fix (dedent to exit list context) ─────────────────

fix('ja/s/article/360042932914.mdx',
    ('  <Frame>![Screenshot](/images/kb/ja/0EM5w000005vNwp.png)</Frame>\n  </Note>',
     '  <Frame>![Screenshot](/images/kb/ja/0EM5w000005vNwp.png)</Frame>\n\n</Note>'))

fix('s/article/4407022160791.mdx',
    ('  For example, you can specify using local time in logs and cleaning up log files.\n  </Note>',
     '  For example, you can specify using local time in logs and cleaning up log files.\n\n</Note>'))

# ── 4. <path>/<user>/<account> escape in bullet lists ────────────────────────

for f in ['s/article/1500000555201.mdx', 's/article/1500000888261.mdx',
          's/article/360058760154.mdx', 's/article/360059173794.mdx',
          'ja/s/article/360059173794.mdx']:
    fix(f,
        ('- <path> specifies', '- `<path>` specifies'),
        ('- <user> specifies', '- `<user>` specifies'),
        ('- <account> specifies', '- `<account>` specifies'))

fix('ja/s/article/1500000888261.mdx',
    ('- <path> specifies', '- `<path>` specifies'),
    ('- <user> specifies', '- `<user>` specifies'),
    ('- <account> specifies', '- `<account>` specifies'))

# ── 5. <<...>> double angle bracket escaping ──────────────────────────────────

fix('ja/s/article/000005303.mdx',
    ('http://*<<your-host-computer>>*', 'http://`<<your-host-computer>>`'))

fix('s/article/000005303.mdx',
    ('http://*<<your-host-computer>>*', 'http://`<<your-host-computer>>`'))

fix('ja/s/article/000005331.mdx',
    ('*<<major.minor.patch>>*', '`<<major.minor.patch>>`'))

fix('s/article/000005331.mdx',
    ('<*<major.minor.patch>>*', '`<<major.minor.patch>>`'))

fix('ja/s/article/000005756.mdx',
    ('例：<<*myhost.com*>>', '例：`<<myhost.com>>`'),
    ('例：<<*5432*>>', '例：`<<5432>>`'),
    ('例：<<*defaultdb*>>', '例：`<<defaultdb>>`'))

fix('ja/s/article/360045120554.mdx',
    ('<<*domain>>*', '`<<domain>>`'))

fix('s/article/360045120554.mdx',
    ('<<*domain>>*', '`<<domain>>`'))

fix('ja/s/article/5428851518999.mdx',
    ('<<http://use.typekit.net/{fontCode}/css>>', '`<<http://use.typekit.net/{fontCode}/css>>`'),
    ('<<https://fonts.googleapis.com/css2?family=Sofadi+One&display=swap>>', '`<<https://fonts.googleapis.com/css2?family=Sofadi+One&display=swap>>`'))

# ── 6. Unescaped < before date/number ────────────────────────────────────────

fix('s/article/000005387.mdx',
    ('sys\\_created\\_on<2016-09-27', 'sys\\_created\\_on\\<2016-09-27'), all_occurrences=True)

fix('ja/s/article/000005697.mdx',
    ('sys_created_on<2016-09-27', 'sys_created_on\\<2016-09-27'), all_occurrences=True)

fix('ja/s/article/360042929094.mdx',
    ('sys\\_created\\_on<2016-09-27', 'sys\\_created\\_on\\<2016-09-27'), all_occurrences=True)

fix('s/article/360042929694.mdx',
    ('created<2015-05-01', 'created\\<2015-05-01'))

fix('ja/s/article/360042929694.mdx',
    ('created<2015-05-01', 'created\\<2015-05-01'))

# ── 7. Japanese / special text in <...> angle brackets ───────────────────────

fix('ja/s/article/360043428253.mdx',
    ('*[<ダッシュボード名>', '*[\\<ダッシュボード名\\>'))

fix('ja/s/article/360043437773.mdx',
    ('*<カードのタイトル>*', '\\<カードのタイトル\\>'))

fix('ja/s/article/360044876874.mdx',
    ('「SELECT \\* FROM <入力タイル>」', '「SELECT \\* FROM \\<入力タイル\\>」'))

fix('ja/s/article/360058757134.mdx',
    ('COPY INTO <場所>', 'COPY INTO \\<場所\\>'))

# <USERNAME> in table
fix('ja/s/article/360043437733.mdx',
    ('-u、--username <USERNAME>', '-u、--username \\<USERNAME\\>'),
    ('-p、--password <PASSWORD>', '-p、--password \\<PASSWORD\\>'),
    ('-s、--server <SERVERNAME>', '-s、--server \\<SERVERNAME\\>'),
    ('-pp、--proxypassword <proxypassword>', '-pp、--proxypassword \\<proxypassword\\>'),
    ('-ps、--proxyserver <proxyserver>', '-ps、--proxyserver \\<proxyserver\\>'),
    ('-pt、--proxyport <proxyport>', '-pt、--proxyport \\<proxyport\\>'))

# EN version has backslash-in-name issue on <NAME_PATTERN>
fix('s/article/360043437733.mdx',
    ('<NAME\\_PATTERN>', '\\<NAME\\_PATTERN\\>'),
    ('<TYPE>', '\\<TYPE\\>'),
    ('<ID>', '\\<ID\\>'))

# <myhost.com:3306> in JA 000005471
fix('ja/s/article/000005471.mdx',
    ('*<myhost.com:3306>*', '`<myhost.com:3306>`'))

# Unescaped < and > as operators in JA 360044876194
fix('ja/s/article/360044876194.mdx',
    ('不等式演算子（<、>、>=、<+など）', '不等式演算子（\\<、\\>、>=、\\<+など）'))

# <*組織名*> and <*アカウント名*> in JA 4402322966807
fix('ja/s/article/4402322966807.mdx',
    ('<*組織名*>-<*アカウント名*>', '\\<組織名\\>-\\<アカウント名\\>'))

# <name_goes_here> in EN 4402322966807 (backslash in tag name)
fix('s/article/4402322966807.mdx',
    ('<name\\_goes\\_here>', '`<name_goes_here>`'))

# <> in table cell (Jupyter workspace name characters)
fix('s/article/36004740075.mdx',
    ('[:\\*?\\"<>', '[:\\*?\\"&lt;&gt;'))

fix('ja/s/article/36004740075.mdx',
    ('[:\\*?\\"<>', '[:\\*?\\"&lt;&gt;'))

# ── 8. {…} JSX expression escaping ───────────────────────────────────────────

# ja/s/article/000005473.mdx and s/article/000005473.mdx – <tt>!{...}</tt>
fix('ja/s/article/000005473.mdx',
    ('!{lastvalue:\\_id}!=1,!{lastrundate:start\\_date}!=02/01/1944',
     '!&#123;lastvalue:\\_id&#125;!=1,!&#123;lastrundate:start\\_date&#125;!=02/01/1944'))

fix('s/article/000005473.mdx',
    ('!{lastvalue:\\_id}!=1,!{lastrundate:start\\_date}!=02/01/1944',
     '!&#123;lastvalue:\\_id&#125;!=1,!&#123;lastrundate:start\\_date&#125;!=02/01/1944'))

# ja/s/article/000005844.mdx – JSON in table cell
fix('ja/s/article/000005844.mdx',
    ('\"filters\": {\"Filter\\_One\": {\"name\": \"property\", \"required\": null},\"Filter\\_Two\":{\"name\": \"property\\_stats\", \"required\": true}}',
     '\"filters\": &#123;\"Filter\\_One\": &#123;\"name\": \"property\", \"required\": null&#125;,\"Filter\\_Two\":&#123;\"name\": \"property\\_stats\", \"required\": true&#125;&#125;'),
    ('\"Filter\\_One\":{\"name\": \"property\", \"required\": null},\"Filter\\_Two\": {\"name\": \"property\\_stats\", \"required\": true}',
     '\"Filter\\_One\":&#123;\"name\": \"property\", \"required\": null&#125;,\"Filter\\_Two\": &#123;\"name\": \"property\\_stats\", \"required\": true&#125;'))

# ja/s/article/360042926754.mdx – {AD_ACCOUNT_ID} etc. in table cells
fix('ja/s/article/360042926754.mdx',
    ('/{AD\\_ACCOUNT\\_ID}/', '/&#123;AD\\_ACCOUNT\\_ID&#125;/'), all_occurrences=True)

# ja/s/article/360043434413.mdx – {app_id} {domain_id} etc.
fix('ja/s/article/360043434413.mdx',
    ('/*{app\\_id}*/', '/\\*&#123;app\\_id&#125;\\*/'), all_occurrences=True)
fix('ja/s/article/360043434413.mdx',
    ('/*{domain\\_id}*/', '/\\*&#123;domain\\_id&#125;\\*/'), all_occurrences=True)
fix('ja/s/article/360043434413.mdx',
    ('/*{page\\_id}*/', '/\\*&#123;page\\_id&#125;\\*/'), all_occurrences=True)
fix('ja/s/article/360043434413.mdx',
    ('/*{post\\_id}*/', '/\\*&#123;post\\_id&#125;\\*/'), all_occurrences=True)

# ja/s/article/360043434433.mdx – same pattern
fix('ja/s/article/360043434433.mdx',
    ('/*{page\\_id}*/', '/\\*&#123;page\\_id&#125;\\*/'), all_occurrences=True)

# !{lastvalue:ReportDate}! in ja 360043437373 and s 360042932554
fix('ja/s/article/360043437373.mdx',
    ("'!{lastvalue:ReportDate}!'", "'!&#123;lastvalue:ReportDate&#125;!'"), all_occurrences=True)

fix('s/article/360042932554.mdx',
    ("'!{lastvalue:ReportDate}!'", "'!&#123;lastvalue:ReportDate&#125;!'"), all_occurrences=True)

# ja/s/article/360043438053.mdx – {your-domain} in text
fix('ja/s/article/360043438053.mdx',
    ('*{your‑domain}*', '\\<your-domain\\>'))

# ja/s/article/360043438373.mdx – {INSTANCE} and {FILE_ID} in link text
fix('ja/s/article/360043438373.mdx',
    ('[https://{INSTANCE}.domo.com/api/data/v1/data-files/{FILE\\_ID}]',
     '[https://&#123;INSTANCE&#125;.domo.com/api/data/v1/data-files/&#123;FILE\\_ID&#125;]'))

# s/article/000005697.mdx – {customerdomain} in malformed URL
fix('s/article/000005697.mdx',
    ('[https://{](https://{/)customerdomain}.[domo.com/datacenter](http://domo.com/datacenter)/accounts.',
     '`https://{customerdomain}.domo.com/datacenter/accounts`.'))

# s/article/360042931734.mdx – { } in pre/table JSON
fix('s/article/360042931734.mdx',
    ('{ "_id": 1, "subject": "History", "score": 88 }',
     '&#123; "_id": 1, "subject": "History", "score": 88 &#125;'),
    all_occurrences=True)
fix('s/article/360042931734.mdx',
    ('{ "_id": 2, "subject": "History", "score": 92 }',
     '&#123; "_id": 2, "subject": "History", "score": 92 &#125;'))
fix('s/article/360042931734.mdx',
    ('{ "_id": 3, "subject": "History", "score": 97 }',
     '&#123; "_id": 3, "subject": "History", "score": 97 &#125;'))
fix('s/article/360042931734.mdx',
    ('{ "_id": 4, "subject": "History", "score": 71 }',
     '&#123; "_id": 4, "subject": "History", "score": 71 &#125;'))
fix('s/article/360042931734.mdx',
    ('{ "_id": 5, "subject": "History", "score": 79 }',
     '&#123; "_id": 5, "subject": "History", "score": 79 &#125;'))
fix('s/article/360042931734.mdx',
    ('{ "_id": 6, "subject": "History", "score": 83 }',
     '&#123; "_id": 6, "subject": "History", "score": 83 &#125;'))
fix('s/article/360042931734.mdx',
    ('{ "subject": "History" }', '&#123; "subject": "History" &#125;'))

# s/article/360043434093.mdx – !{lastvalue} in table
fix('s/article/360043434093.mdx',
    ('!{lastvalue:\\_id}!=1,!{lastrundate:start\\_date}!=02/01/1944',
     '!&#123;lastvalue:\\_id&#125;!=1,!&#123;lastrundate:start\\_date&#125;!=02/01/1944'))

# s/article/360043436273.mdx – !{lastvalue} in table
fix('s/article/360043436273.mdx',
    ('!{lastvalue:\\_id}!=1,!{lastrundate:start\\_date}!=02/01/1944',
     '!&#123;lastvalue:\\_id&#125;!=1,!&#123;lastrundate:start\\_date&#125;!=02/01/1944'))

# s/article/4411277235351.mdx – {currency code} in HTML table
fix('s/article/4411277235351.mdx',
    ('currencies/{currency code}/conversion-rates',
     'currencies/&#123;currency code&#125;/conversion-rates'))

# ja/s/article/4411277235351.mdx – {id}, {surveyId} etc. in markdown table
fix('ja/s/article/4411277235351.mdx',
    ('{surveyId/questions', '&#123;surveyId&#125;/questions'),
    ('{surveyId}responses', '&#123;surveyId&#125;responses'),
    all_occurrences=False)
fix('ja/s/article/4411277235351.mdx',
    (' {id} ', ' &#123;id&#125; '), all_occurrences=True)
fix('ja/s/article/4411277235351.mdx',
    ('{eventId}', '&#123;eventId&#125;'), all_occurrences=True)
fix('ja/s/article/4411277235351.mdx',
    ('{exhibitorId}', '&#123;exhibitorId&#125;'), all_occurrences=True)

# ja/s/article/6523741250455.mdx – JSON in bold text
fix('ja/s/article/6523741250455.mdx',
    ('**{"status":400,"statusReason":"Bad Request","message":"No value in attribute..."}**',
     '**&#123;"status":400,"statusReason":"Bad Request","message":"No value in attribute..."&#125;**'))

# ── 9. Multi-line backtick code → fenced code blocks ─────────────────────────

# ja/s/article/360042929154.mdx – multi-line { } JSON in backtick span
fix('ja/s/article/360042929154.mdx',
    ('`{"top":100,  \n"id":"page"},  \n{"top":100,  \n"id":"region"}`',
     '```\n{"top":100,\n"id":"page"},\n{"top":100,\n"id":"region"}\n```'))

# ja/s/article/1500000888261.mdx – multi-line Java code with <account>/<user>
# Fix the <account>, <user> inside code spans to avoid parse issues
fix('ja/s/article/1500000888261.mdx',
    ('"jdbc:snowflake://<account>.snowflakecomputing.com"',
     '"jdbc:snowflake://\\<account\\>.snowflakecomputing.com"'), all_occurrences=True)
fix('ja/s/article/1500000888261.mdx',
    ('prop.put("user", "<user>")', 'prop.put("user", "\\<user\\>")'), all_occurrences=True)
fix('ja/s/article/1500000888261.mdx',
    ('prop.put("account", "<account>")', 'prop.put("account", "\\<account\\>")'), all_occurrences=True)

# ja/s/article/360058760154.mdx – same Java code
fix('ja/s/article/360058760154.mdx',
    ('"jdbc:snowflake://<account>.snowflakecomputing.com"',
     '"jdbc:snowflake://\\<account\\>.snowflakecomputing.com"'), all_occurrences=True)
fix('ja/s/article/360058760154.mdx',
    ('prop.put("user", "<user>")', 'prop.put("user", "\\<user\\>")'), all_occurrences=True)
fix('ja/s/article/360058760154.mdx',
    ('prop.put("account", "<account>")', 'prop.put("account", "\\<account\\>")'), all_occurrences=True)

# ── 10. <b><i> tag nesting fixes ─────────────────────────────────────────────

# s/article/1500000218261.mdx  and  s/article/360060476953.mdx
# Pattern: <b><i></b><b></i>  =>  <b><i></i></b>
for f in ['s/article/1500000218261.mdx', 's/article/360060476953.mdx']:
    fix(f,
        ('<b><i></b><b></i>', '<b><i></i></b>'), all_occurrences=True)

# s/article/360042932514.mdx – <b><i></b></i>
fix('s/article/360042932514.mdx',
    ('<b><i>Retrieving a Folder ID from SmartSheet UI</b></i>',
     '<b><i>Retrieving a Folder ID from SmartSheet UI</i></b>'))

# s/article/360060508773.mdx – <i>text<b></i>.</b>
fix('s/article/360060508773.mdx',
    ('<i>mycompany.zendesk.com<b></i>.</b>',
     '<i>mycompany.zendesk.com</i>.'))

# ── 11. Special / one-off fixes ───────────────────────────────────────────────

# s/article/000005326.mdx – </Frame> instead of </Note> + malformed link
fix('s/article/000005326.mdx',
    ('(https://www.domo.com/consumption-terms]<img alt="external link.png" src="/images/kb/0EMVq000000KZo1.jpg" style={{width: 20, height: 20, display: \'inline\', verticalAlign: \'start\', margin: \'0\'}}/>.</Frame>',
     '(https://www.domo.com/consumption-terms)<img alt="external link.png" src="/images/kb/0EMVq000000KZo1.jpg" style={{width: 20, height: 20, display: \'inline\', verticalAlign: \'start\', margin: \'0\'}}/>.</Note>'))

# s/article/360042922994.mdx – unclosed <div> inside Note inside HTML table
fix('s/article/360042922994.mdx',
    ('<div class="mdx-embed"><Note><b> Note: </b>',
     '<Note><b> Note: </b>'))
fix('s/article/360042922994.mdx',
    (' </Note></td>',
     ' </Note></td>'))
# Remove unclosed </div> issue by stripping the mdx-embed div wrapper
content = r('s/article/360042922994.mdx')
content = content.replace(
    '</div></div></div> </Note></td>',
    '</Note></td>')
w('s/article/360042922994.mdx', content)
print('  fixed: s/article/360042922994.mdx (mdx-embed div cleanup)')

# s/article/360042925994.mdx – \(<\) backslash before tag name
fix('s/article/360042925994.mdx',
    ('\\(<\\)', '(&lt;)'))

# s/article/360042928374.mdx – <Note> inside <td> causes stray </td>
# Fix: replace Note with plain bold text since it's already in a custom div
fix('s/article/360042928374.mdx',
    ('<div class="info-box-wrapper"><div class="info-box-icon-container"></div><div class="info-box-content-container"><div class="info-box-content"><b> Note </b>:',
     '<b>Note:</b> '))
fix('s/article/360042928374.mdx',
    ('</div></div></div> </Note>',
     ''))

# s/article/360043431133.mdx – Accordion title with unescaped inner quotes
fix('s/article/360043431133.mdx',
    ('<Accordion title="I am receiving an error saying "ReportError.START\\_DATE\\_MORE\\_THAN\\_THREE\\_YEARS\\_AGO" while using the Saved Query report. Why?">',
     '<Accordion title="I am receiving an error saying &quot;ReportError.START\\_DATE\\_MORE\\_THAN\\_THREE\\_YEARS\\_AGO&quot; while using the Saved Query report. Why?">'))

# ja/s/article/360043438973.mdx – </Warning> placed before <img>, splitting bold
fix('ja/s/article/360043438973.mdx',
    ('<Warning>   **重要：**警告アイコン（</Warning><img src="/images/kb/ja/0EMVq000005P0Rl.jpg" style={{width: 20, height: 20, display: \'inline\', verticalAlign: \'start\', margin: \'0\'}}/> )が付いている許可は、Domoインスタンスのセキュリティ設定の構成やユーザー権限の昇格など、非常に機密性の高い機能へのアクセス権を付与します。これらの許可は管理者レベルのユーザーのみを対象としており、慎重に割り当てる必要があります。',
     '<Warning>\n\n**重要：**警告アイコン（<img src="/images/kb/ja/0EMVq000005P0Rl.jpg" style={{width: 20, height: 20, display: \'inline\', verticalAlign: \'start\', margin: \'0\'}}/> ）が付いている許可は、Domoインスタンスのセキュリティ設定の構成やユーザー権限の昇格など、非常に機密性の高い機能へのアクセス権を付与します。これらの許可は管理者レベルのユーザーのみを対象としており、慎重に割り当てる必要があります。\n\n</Warning>'))

# s/article/360047553253.mdx – <Warning> in table cell without </Warning>
fix('s/article/360047553253.mdx',
    ('<Warning>**Important:** If you delete a DataSet that powers any cards, the cards display a "Data not loading" message. |',
     '<Warning>**Important:** If you delete a DataSet that powers any cards, the cards display a "Data not loading" message.</Warning> |'))

# ja/s/article/360050912013.mdx – missing > on Frame closing tag
fix('ja/s/article/360050912013.mdx',
    ('<Frame>![](/images/kb/ja/0EM5w000005vOjH.png)</Frame\n',
     '<Frame>![](/images/kb/ja/0EM5w000005vOjH.png)</Frame>\n'))

# ja/s/article/4402322966807.mdx asterisk before name: <*組織名*>
# Already handled above

# ja/s/article/360043429973.mdx – **bold not closed before </td>
# The ** at position 1091 is in content like **メニューオプション</td>
fix('ja/s/article/360043429973.mdx',
    ('**メニューオプション</td>', '**メニューオプション**</td>'))
fix('ja/s/article/360043429973.mdx',
    ('**お気に入り</td>', '**お気に入り**</td>'), all_occurrences=True)
fix('ja/s/article/360043429973.mdx',
    ('**フォローアップのフラグを付ける</td>', '**フォローアップのフラグを付ける**</td>'), all_occurrences=True)
fix('ja/s/article/360043429973.mdx',
    ('**スレッドを作成</td>', '**スレッドを作成**</td>'), all_occurrences=True)
fix('ja/s/article/360043429973.mdx',
    ('**タスクを作成</td>', '**タスクを作成**</td>'), all_occurrences=True)
fix('ja/s/article/360043429973.mdx',
    ('**編集</td>', '**編集**</td>'), all_occurrences=True)
fix('ja/s/article/360043429973.mdx',
    ('**削除</td>', '**削除**</td>'), all_occurrences=True)

# ja/s/article/360042924774.mdx – **bold not closed before </td> (position ~307)
# The content at pos 307 is **[期間前]** - check and fix
fix('ja/s/article/360042924774.mdx',
    ('**［期間前］**フィールドに「**3**」を入力すると、変化値はDataSetの最後の値と3週間前の値の差となります。</td>',
     '**［期間前］**フィールドに「**3**」を入力すると、変化値はDataSetの最後の値と3週間前の値の差となります。</td>'))

# ja/s/article/360042925374.mdx – bold not closed before </td>
fix('ja/s/article/360042925374.mdx',
    ('**ワークスペース/フォルダー/シート名**にシート名を、そして**［検索］**',
     '**ワークスペース/フォルダー/シート名**にシート名を、そして**［検索］**'))

# ja/s/article/360042930474.mdx – same pattern
# The error is at 49:662 - strong not closed before </td>

# Print all warnings
print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
