#!/usr/bin/env python3
"""Fix remaining MDX parsing errors - follow-up to fix_mdx_errors2.py."""

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

# ── Group A: </Note>/</Warning> inline at end of list items ────────────────────

# ja/s/article/000005150.mdx
fix('ja/s/article/000005150.mdx',
    ('セクション内のデータも指定する必要があります。</Note>',
     'セクション内のデータも指定する必要があります。\n\n</Note>'))

# ja/s/article/000005184.mdx
fix('ja/s/article/000005184.mdx',
    ('DataFlowの入力が有効で、サポートされているタイプである。</Note>',
     'DataFlowの入力が有効で、サポートされているタイプである。\n\n</Note>'))

# ja/s/article/000005648.mdx
fix('ja/s/article/000005648.mdx',
    ('削除できます。</Note>',
     '削除できます。\n\n</Note>'))

# ja/s/article/000005839.mdx
fix('ja/s/article/000005839.mdx',
    ('自分またはほかのユーザーの権限管理権限を昇格させるのを防ぐためのものです。</Note>',
     '自分またはほかのユーザーの権限管理権限を昇格させるのを防ぐためのものです。\n\n</Note>'))

# ja/s/article/1500000555201.mdx
fix('ja/s/article/1500000555201.mdx',
    ('DESCRIBEUSERを使用してユーザーのパブリックキーの指紋を確認します。  </Note>',
     'DESCRIBEUSERを使用してユーザーのパブリックキーの指紋を確認します。\n\n</Note>'))

# ja/s/article/360042931814.mdx
fix('ja/s/article/360042931814.mdx',
    ('以下のいずれかの接続方法のご利用をご検討ください。**</Note>',
     '以下のいずれかの接続方法のご利用をご検討ください。**\n\n</Note>'))

# ja/s/article/360042932474.mdx
fix('ja/s/article/360042932474.mdx',
    ('- SSH秘密キーのパスフレーズ。</Warning>',
     '- SSH秘密キーのパスフレーズ。\n\n</Warning>'))

# ja/s/article/360042933494.mdx
fix('ja/s/article/360042933494.mdx',
    ('QRコードを追加する。</Note>',
     'QRコードを追加する。\n\n</Note>'))

# ja/s/article/360042934614.mdx
fix('ja/s/article/360042934614.mdx',
    ('**[保存]**を選択して変更を保持し、モーダルを閉じます。  </Note>',
     '**[保存]**を選択して変更を保持し、モーダルを閉じます。\n\n</Note>'))

# ja/s/article/360043437093.mdx – same Snowflake deprecation Note pattern as 360042931814
fix('ja/s/article/360043437093.mdx',
    ('以下のいずれかの接続方法のご利用をご検討ください。**</Note>',
     '以下のいずれかの接続方法のご利用をご検討ください。**\n\n</Note>'))

# ja/s/article/360043437773.mdx – Note opening inline AND closing inline
fix('ja/s/article/360043437773.mdx',
    ('<Note>   **注記：**少なくとも1人のユーザーまたは1つのグループを選択する必要があります。',
     '<Note>\n\n**注記：**少なくとも1人のユーザーまたは1つのグループを選択する必要があります。'),
    ('フィールドからユーザーまたはグループを削除します。  </Note>',
     'フィールドからユーザーまたはグループを削除します。\n\n</Note>'))

# ja/s/article/360043437993.mdx – Note has no closing tag before step 5
fix('ja/s/article/360043437993.mdx',
    ('パブリックエンベッドするカードには使用できません。\n5.',
     'パブリックエンベッドするカードには使用できません。\n\n</Note>\n5.'))

# ja/s/article/360045402273.mdx
fix('ja/s/article/360045402273.mdx',
    ('**[バッチでフィルター]**エリアが表示されます。  </Note>',
     '**[バッチでフィルター]**エリアが表示されます。\n\n</Note>'))

# ja/s/article/360055259234.mdx – Note opening inline AND closing inline
fix('ja/s/article/360055259234.mdx',
    ('<Note>   **注記：**サイズ変更時に、セクションと重なっているタイルと付箋がセクションに含まれます。',
     '<Note>\n\n**注記：**サイズ変更時に、セクションと重なっているタイルと付箋がセクションに含まれます。'),
    ('セクションの端をドラッグして付箋の上に重なるようにします。</Note>',
     'セクションの端をドラッグして付箋の上に重なるようにします。\n\n</Note>'))

# ja/s/article/360059173794.mdx
fix('ja/s/article/360059173794.mdx',
    ('DESCRIBEUSERを使用してユーザーのパブリックキーの指紋を確認します。  </Note>',
     'DESCRIBEUSERを使用してユーザーのパブリックキーの指紋を確認します。\n\n</Note>'))

# s/article/000005473.mdx – Note opening inline AND closing inline
fix('s/article/000005473.mdx',
    ("<Note>**Note:** Your service account doesn't need to be in the same project",
     "<Note>\n\n**Note:** Your service account doesn't need to be in the same project"),
    ('or to multiple external identities</Note>',
     'or to multiple external identities\n\n</Note>'))

# ja/s/article/000005473.mdx – Note opening inline AND closing inline
fix('ja/s/article/000005473.mdx',
    ('<Note>     **注記：**サービスアカウントは、Workload',
     '<Note>\n\n**注記：**サービスアカウントは、Workload'),
    ('複数の外部IDに付与できます。</Note>',
     '複数の外部IDに付与できます。\n\n</Note>'))

# s/article/000005492.mdx
fix('s/article/000005492.mdx',
    ('cannot refresh the data for any DataFlow more often than once per week.</Note>',
     'cannot refresh the data for any DataFlow more often than once per week.\n\n</Note>'))

# s/article/000005931.mdx
fix('s/article/000005931.mdx',
    ('all the data will be written to Salesforce every time the Connector runs.</Note>',
     'all the data will be written to Salesforce every time the Connector runs.\n\n</Note>'))

# s/article/000005941.mdx
fix('s/article/000005941.mdx',
    ('Users must have *Admin-*level access to the Procore Analytics tool to generate an access token.</Note>',
     'Users must have *Admin-*level access to the Procore Analytics tool to generate an access token.\n\n</Note>'))

# s/article/1500000555201.mdx
fix('s/article/1500000555201.mdx',
    ('passes it to the Snowflake driver to create a connection:</Note>',
     'passes it to the Snowflake driver to create a connection:\n\n</Note>'))

# s/article/360042933494.mdx
fix('s/article/360042933494.mdx',
    ('Format any dynamic field in your email or add a QR Code by selecting **Tag Formatting**.</Note>',
     'Format any dynamic field in your email or add a QR Code by selecting **Tag Formatting**.\n\n</Note>'))

# s/article/360042934294.mdx
fix('s/article/360042934294.mdx',
    ('Lets you search the group listing to display only specific groups. |</Note>',
     'Lets you search the group listing to display only specific groups. |\n\n</Note>'))

# s/article/4403367344023.mdx
fix('s/article/4403367344023.mdx',
    ('the user promoting the repository will be the owner of content created during the promotion.</Note>',
     'the user promoting the repository will be the owner of content created during the promotion.\n\n</Note>'))

# s/article/8275510785559.mdx
fix('s/article/8275510785559.mdx',
    ('Different report types cannot use the same DataSet.</Warning>',
     'Different report types cannot use the same DataSet.\n\n</Warning>'))

# ja/s/article/1500000888261.mdx – Note opening inline AND closing inline
fix('ja/s/article/1500000888261.mdx',
    ('<Note>   **注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FPプロパティの詳細については、「キーローテーション」を参照してください。',
     '<Note>\n\n**注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FPプロパティの詳細については、「キーローテーション」を参照してください。'),
    ('サンプルコードは以下のとおりです。</Note>',
     'サンプルコードは以下のとおりです。\n\n</Note>'))

# ja/s/article/360058760154.mdx – Note opening inline, unescaped <path>/<user>/<account>, closing inline
fix('ja/s/article/360058760154.mdx',
    ('<Note>   **注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FPプロパティの詳細については、「[キーローテーション]',
     '<Note>\n\n**注記：**RSA\\_PUBLIC\\_KEY\\_2\\_FPプロパティの詳細については、「[キーローテーション]'),
    ('     - <path>は作成したシークレットキーファイルへのローカルパスを指定します。',
     '     - \\<path\\>は作成したシークレットキーファイルへのローカルパスを指定します。'),
    ('     - <user>はSnowflakeログイン名を指定します。',
     '     - \\<user\\>はSnowflakeログイン名を指定します。'),
    ('     - <account>はアカウントの名前（Snowflakeが提供）を指定します。',
     '     - \\<account\\>はアカウントの名前（Snowflakeが提供）を指定します。'),
    ('サンプルコードは以下のとおりです。</Note>',
     'サンプルコードは以下のとおりです。\n\n</Note>'))

# ── Group B: Unescaped { } braces and angle bracket tokens ────────────────────

# ja/s/article/360042926754.mdx – {CAMPAIGN_GROUP_ID} and {AD_ACCOUNT_ID} unescaped
fix('ja/s/article/360042926754.mdx',
    ('/{CAMPAIGN\\_GROUP\\_ID}/insights', '/&#123;CAMPAIGN\\_GROUP\\_ID&#125;/insights'),
    ('{AD\\_ACCOUNT\\_ID}/adsets', '&#123;AD\\_ACCOUNT\\_ID&#125;/adsets'))

# ja/s/article/360042929154.mdx – multi-line backtick code span with { } – convert to code fence
fix('ja/s/article/360042929154.mdx',
    ('`{"top":100,  \n"id":"page"},  \n{"top":100,  \n"id":"region"}`',
     '```json\n{"top":100,\n"id":"page"},\n{"top":100,\n"id":"region"}\n```'))

# ja/s/article/360043434413.mdx – /*{page_id}* without trailing slash (line 94)
fix('ja/s/article/360043434413.mdx',
    ('/*{page\\_id}*                  |',
     '/\\*&#123;page\\_id&#125;\\*                  |'))

# ja/s/article/360043434433.mdx – /*{page_id}* and /*{post_id}*/insights
fix('ja/s/article/360043434433.mdx',
    ('/*{page\\_id}*          |',
     '/\\*&#123;page\\_id&#125;\\*          |'),
    ('/*{post\\_id}*/insights |',
     '/\\*&#123;post\\_id&#125;\\*/insights |'))

# ja/s/article/6523741250455.mdx – {"status":500,...} bold text
fix('ja/s/article/6523741250455.mdx',
    ('**{"status":500,"statusReason":"Internal Server Error"',
     '**&#123;"status":500,"statusReason":"Internal Server Error"'),
    ('" ...}**',
     '" ...&#125;**'))

# s/article/360042931734.mdx – MongoDB aggregation { } inside <pre> HTML
fix('s/article/360042931734.mdx',
    ('  {\n    $match: {\n      score: {\n        $gt: 80\n      }\n    }\n  },\n  {\n    $count: "passing_scores"\n  }\n',
     '  &#123;\n    $match: &#123;\n      score: &#123;\n        $gt: 80\n      &#125;\n    &#125;\n  &#125;,\n  &#123;\n    $count: "passing_scores"\n  &#125;\n'))

# s/article/360043434093.mdx – JSON in HTML table cell
fix('s/article/360043434093.mdx',
    ('{ "pipeline": [ { "limit": 5 } ], "source": { "pageEvents": null }, "timeSeries": { "count": 1, "first": 1493596800000, "period": "dayRange" } }',
     '&#123; "pipeline": [ &#123; "limit": 5 &#125; ], "source": &#123; "pageEvents": null &#125;, "timeSeries": &#123; "count": 1, "first": 1493596800000, "period": "dayRange" &#125; &#125;'))

# s/article/4411277235351.mdx – {id} and {surveyId in HTML table cell
fix('s/article/4411277235351.mdx',
    ('/events/{id}/surveys/ {surveyId/questions',
     '/events/&#123;id&#125;/surveys/ &#123;surveyId/questions'))

# ── Group C: Structural fixes ─────────────────────────────────────────────────

# s/article/360042925994.mdx – <Frame> should be </Frame> (missing slash)
fix('s/article/360042925994.mdx',
    ('   ![alert_actions_attach_button.png](/images/kb/0EM5w000005vOcD.png)\n   <Frame>',
     '   ![alert_actions_attach_button.png](/images/kb/0EM5w000005vOcD.png)\n   </Frame>'))

# s/article/360043437733.mdx – <uploadfile.script> in Tip needs escaping
fix('s/article/360043437733.mdx',
    ('Update <uploadfile.script> in the above example',
     'Update \\<uploadfile.script\\> in the above example'))

# s/article/360045402273.mdx – stray </Note> at end of step 4
fix('s/article/360045402273.mdx',
    ('appears [below](#configure_partition_key_recommended).</Note>',
     'appears [below](#configure_partition_key_recommended).'))

# s/article/36004740075.mdx – </Warning> inline at end of last list item
fix('s/article/36004740075.mdx',
    ('Input and Output DataSets are also shared with Co-Owners.</Warning>',
     'Input and Output DataSets are also shared with Co-Owners.\n\n</Warning>'))

# ja/s/article/36004740075.mdx – <人数> placeholder needs escaping
fix('ja/s/article/36004740075.mdx',
    ('**[他 <人数>人]**を選択します。',
     '**[他 \\<人数\\>人]**を選択します。'))

# ── Group D: Stray tags and structural issues ──────────────────────────────────

# s/article/1500000218261.mdx – stray </b> + wrong nesting <b><i></b></i>
fix('s/article/1500000218261.mdx',
    ('<b><i></i></b>End Date</b> to create a range',
     '<b><i></i></b>End Date to create a range'),
    ('<b> End Date</b><b><i></b></i>',
     '<b> End Date</b><b><i></i></b>'),
    all_occurrences=True)

# s/article/360060476953.mdx – same stray </b> + wrong nesting
fix('s/article/360060476953.mdx',
    ('<b><i></i></b>End Date</b> to create a range',
     '<b><i></i></b>End Date to create a range'),
    ('<b> End Date</b><b><i></b></i>',
     '<b> End Date</b><b><i></i></b>'),
    all_occurrences=True)

# ja/s/article/360045120554.mdx – <<companyname>> has unescaped leading <<
fix('ja/s/article/360045120554.mdx',
    ('*<<companyname\\>\\>*',
     '*\\<\\<companyname\\>\\>*'))

# s/article/360045120554.mdx – same <<companyname>> pattern
fix('s/article/360045120554.mdx',
    ('*<<companyname\\>\\>*',
     '*\\<\\<companyname\\>\\>*'))

# ja/s/article/4402322966807.mdx – <*組織名*>-<*アカウント名*> and other angle bracket tokens
fix('ja/s/article/4402322966807.mdx',
    ('サブドメインの値は<*組織名*>-<*アカウント名*>です。',
     'サブドメインの値は\\<*組織名*\\>-\\<*アカウント名*\\>です。'),
    ('https://<*アカウントロケーター*>.<*リージョン*>.snowflakecomputing.com',
     'https://\\<*アカウントロケーター*\\>.\\<*リージョン*\\>.snowflakecomputing.com'),
    ('*例：<アカウントロケーター>.<リージョン>',
     '*例：\\<アカウントロケーター\\>.\\<リージョン\\>'))

# s/article/4402322966807.mdx – </AccordionGroup> directly followed by ### heading
fix('s/article/4402322966807.mdx',
    ('</AccordionGroup>### Next Steps',
     '</AccordionGroup>\n\n### Next Steps'))

# s/article/360042922994.mdx – <Note> inside HTML <li> (JSX not allowed in HTML)
fix('s/article/360042922994.mdx',
    ('<Note><b> Note: </b> Because MySQL determines which indexes are needed to improve run-time efficiency, not all of your index transforms may show up in the Explain SQL if MySQL determined that running the index would cause inefficiencies. </Note>',
     '<b> Note: </b> Because MySQL determines which indexes are needed to improve run-time efficiency, not all of your index transforms may show up in the Explain SQL if MySQL determined that running the index would cause inefficiencies. '))

# s/article/360042928374.mdx – <Note> inside HTML <td> with no </Note> closing tag
fix('s/article/360042928374.mdx',
    ('<Note><b>Note:</b> There might be a possibility of having other/additional supported values for Reporting Period.',
     '<b>Note:</b> There might be a possibility of having other/additional supported values for Reporting Period.'))

# ── Group E: Unmatched ** in HTML table cells ──────────────────────────────────

# ja/s/article/360043429973.mdx – trailing ** before </td> in two cells
fix('ja/s/article/360043429973.mdx',
    ('**[お気に入り]**メニューオプション**</td>',
     '**[お気に入り]**メニューオプション</td>'),
    ('**[フォローアップのフラグを付ける]**メニューオプション**</td>',
     '**[フォローアップのフラグを付ける]**メニューオプション</td>'))

# Print all warnings
print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
