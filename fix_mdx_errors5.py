#!/usr/bin/env python3
"""Fix remaining 24 MDX parsing errors (round 5)."""

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
    """Replace **text** with <b>text</b> on specific lines (bold-in-td fix)."""
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

# ── Group A: Note/Warning/Tip opening/closing ─────────────────────────────────

# ja/s/article/000005184.mdx – second Note block, closing </Note> inline
fix('ja/s/article/000005184.mdx',
    ('データソースがDataSetビューまたはDataFusionではない。</Note>',
     'データソースがDataSetビューまたはDataFusionではない。\n\n</Note>'))

# ja/s/article/1500000555201.mdx – closing </Note> inline
fix('ja/s/article/1500000555201.mdx',
    ('サンプルコードは以下のとおりです。</Note>',
     'サンプルコードは以下のとおりです。\n\n</Note>'))

# ja/s/article/360042934614.mdx – closing </Note> inline (trailing two spaces)
fix('ja/s/article/360042934614.mdx',
    ('ポリシーエディターを閉じることができます。  </Note>',
     'ポリシーエディターを閉じることができます。\n\n</Note>'))

# ja/s/article/360059173794.mdx – opening <Note> has content on same line
fix('ja/s/article/360059173794.mdx',
    ('<Note>   **注記：**RSA',
     '<Note>\n\n**注記：**RSA'))

# ja/s/article/4402322966807.mdx – both opening and closing inline
fix('ja/s/article/4402322966807.mdx',
    ('<Note>  **注記：**このデータベース内の',
     '<Note>\n\n**注記：**このデータベース内の'),
    ('る必要がある場合があります。</Note>',
     'る必要がある場合があります。\n\n</Note>'))

# s/article/000005941.mdx – second Note block: both opening and closing inline
fix('s/article/000005941.mdx',
    ('<Note>**Note:** It is recommended',
     '<Note>\n\n**Note:** It is recommended'),
    ('may cause issues with your token.</Note>',
     'may cause issues with your token.\n\n</Note>'))

# s/article/360042933494.mdx – opening and closing inline
fix('s/article/360042933494.mdx',
    ('<Note>**Note:** - For a Bi-weekly schedule',
     '<Note>\n\n**Note:** - For a Bi-weekly schedule'),
    ('Wednesday in July.</Note>',
     'Wednesday in July.\n\n</Note>'))

# s/article/360045120554.mdx – Tip: opening and closing inline
fix('s/article/360045120554.mdx',
    ('<Tip>**Tip:** You can use the description',
     '<Tip>\n\n**Tip:** You can use the description'),
    ('becomes the subscription owner.</Tip>',
     'becomes the subscription owner.\n\n</Tip>'))

# s/article/360045402273.mdx – opening inline only
fix('s/article/360045402273.mdx',
    ('<Note>**Note:** This is only an intermediate calculation',
     '<Note>\n\n**Note:** This is only an intermediate calculation'))

# s/article/36004740075.mdx – Warning: opening inline only
fix('s/article/36004740075.mdx',
    ('<Warning>**Important:** - Simultaneous editing',
     '<Warning>\n\n**Important:** - Simultaneous editing'))

# ── Group B: Brace/angle escaping ─────────────────────────────────────────────

# ja/s/article/360042926754.mdx – {AD_SET_ID}, {CAMPAIGN_GROUP_ID}, {USER_ID}
fix('ja/s/article/360042926754.mdx',
    ('/{AD\\_SET\\_ID}/insights',
     '/&#123;AD\\_SET\\_ID&#125;/insights'),
    ('/{CAMPAIGN\\_GROUP\\_ID}/insights',
     '/&#123;CAMPAIGN\\_GROUP\\_ID&#125;/insights'),
    ('/{USER\\_ID}',
     '/&#123;USER\\_ID&#125;'),
    all_occurrences=True)

# ja/s/article/360043434413.mdx – /*{page_id}* at line 102
fix('ja/s/article/360043434413.mdx',
    ('/*{page\\_id}*',
     '/\\*&#123;page\\_id&#125;\\*'),
    all_occurrences=True)

# ja/s/article/360043437733.mdx – <TYPE> in markdown table
fix('ja/s/article/360043437733.mdx',
    ('--owner-id <TYPE>',
     '--owner-id \\<TYPE\\>'))

# ── Group D: HTML structure ────────────────────────────────────────────────────

# s/article/360042928374.mdx – <b>Note:</b> at start of <td> content
fix('s/article/360042928374.mdx',
    ('<b>Note:</b> There might be',
     '**Note:** There might be'))

# s/article/360042931734.mdx – <p><pre> invalid nesting (aggregate query block)
fix('s/article/360042931734.mdx',
    ('<p><pre>[',
     '<pre>['),
    (']</pre></p>',
     ']</pre>'))

# s/article/360043434093.mdx – wrong nesting <b><i>text</b></i>
fix('s/article/360043434093.mdx',
    ('<b><i>rules</b></i>',
     '<b><i>rules</i></b>'),
    ('<b><i>rulesJson</b></i>',
     '<b><i>rulesJson</i></b>'),
    ('<b><i>excludeRules</b></i>',
     '<b><i>excludeRules</i></b>'))

# ── Group E: **bold** inside <td> → <b>bold</b> ──────────────────────────────

fix_td_bold('ja/s/article/360042924774.mdx', 49)
fix_td_bold('ja/s/article/360042925374.mdx', 29)
fix_td_bold('ja/s/article/360042930474.mdx', 49)
fix_td_bold('ja/s/article/360043429973.mdx', 151)
fix_td_bold('ja/s/article/360043434433.mdx', 52)

# ── Group C: Java multi-line backtick spans → fenced code block ───────────────

JAVA_CODE = (
    'import java.util.Properties;\n'
    'import java.sql.Connection;\n'
    'import java.sql.Statement;\n'
    'import java.sql.ResultSet;\n'
    'import java.sql.DriverManager;\n'
    'import java.io.File;\n'
    'import java.io.FileInputStream;\n'
    'import java.io.DataInputStream;\n'
    'import java.util.Base64;\n'
    'import java.security.spec.PKCS8EncodedKeySpec;\n'
    'import java.security.KeyFactory;\n'
    'import java.security.PrivateKey;\n'
    'import javax.crypto.EncryptedPrivateKeyInfo;\n'
    'import javax.crypto.SecretKeyFactory;\n'
    'import javax.crypto.spec.PBEKeySpec;\n'
    '\n'
    'public class TestJdbc\n'
    '{\n'
    'public static void main(String[] args)\n'
    'throws Exception\n'
    '{\n'
    'File f = new File("<path>/rsa_key.p8");\n'
    'FileInputStream fis = new FileInputStream(f);\n'
    'DataInputStream dis = new DataInputStream(fis);\n'
    'byte[] keyBytes = new byte[(int) f.length()];\n'
    'dis.readFully(keyBytes);\n'
    'dis.close();\n'
    '\n'
    'String encrypted = new String(keyBytes);\n'
    'String passphrase = System.getenv("PRIVATE_KEY_PASSPHRASE");\n'
    'encrypted = encrypted.replace("-----BEGIN ENCRYPTED PRIVATE KEY-----", "");\n'
    'encrypted = encrypted.replace("-----END ENCRYPTED PRIVATE KEY-----", "");\n'
    'EncryptedPrivateKeyInfo pkInfo = new EncryptedPrivateKeyInfo(Base64.getMimeDecoder().decode(encrypted));\n'
    'PBEKeySpec keySpec = new PBEKeySpec(passphrase.toCharArray());\n'
    'SecretKeyFactory pbeKeyFactory = SecretKeyFactory.getInstance(pkInfo.getAlgName());\n'
    'PKCS8EncodedKeySpec encodedKeySpec = pkInfo.getKeySpec(pbeKeyFactory.generateSecret(keySpec));\n'
    'KeyFactory keyFactory = KeyFactory.getInstance("RSA");\n'
    'PrivateKey encryptedPrivateKey = keyFactory.generatePrivate(encodedKeySpec);\n'
    '\n'
    'String url = "jdbc:snowflake://<account>.snowflakecomputing.com";\n'
    'Properties prop = new Properties();\n'
    'prop.put("user", "<user>");\n'
    'prop.put("account", "<account>");\n'
    'prop.put("privateKey", encryptedPrivateKey);\n'
    '\n'
    'Connection conn = DriverManager.getConnection(url, prop);\n'
    'Statement stat = conn.createStatement();\n'
    'ResultSet res = stat.executeQuery("select 1");\n'
    'res.next();\n'
    'System.out.println(res.getString(1));\n'
    'conn.close();\n'
    '}\n'
    '}'
)
JAVA_BLOCK = f'```java\n{JAVA_CODE}\n```'

def fix_java_spans(path):
    content = r(path)
    start_marker = '     `import java.util.Properties;'
    end_marker = '      }`'
    si = content.find(start_marker)
    ei = content.find(end_marker, si)
    if si == -1 or ei == -1:
        warnings.append(f"NOT FOUND java span markers in {path}")
        return
    ei += len(end_marker)
    new_content = content[:si] + JAVA_BLOCK + content[ei:]
    w(path, new_content)
    print(f"  fixed: {path}")

fix_java_spans('ja/s/article/1500000888261.mdx')
fix_java_spans('ja/s/article/360058760154.mdx')

# ── Summary ───────────────────────────────────────────────────────────────────

print()
if warnings:
    print('WARNINGS (patterns not found):')
    for w_ in warnings:
        print(f'  {w_}')
else:
    print('All patterns found and applied.')
