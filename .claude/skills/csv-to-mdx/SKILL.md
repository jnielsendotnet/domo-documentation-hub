---
name: csv-to-mdx
user-invocable: true
description: "review converted MDX article, audit programmatic conversion output, check batch CSV to MDX output, validate Salesforce article conversion, post-conversion review"
argument-hint: "path to an MDX file or article title to review"
---

Review and audit an MDX article produced by the Salesforce-to-Domo programmatic conversion pipeline (`scripts/html_to_mdx.py`). Identify anything the script cannot fix automatically and provide a corrected version.

The user will provide: $ARGUMENTS

---

## Pipeline Overview

The full programmatic conversion runs in this order:

1. **CSV extraction** — `update_kb_articles.py` reads `ARTICLE_BODY__C` (HTML), `TITLE`, `URLNAME`, `LANGUAGE`, and `PUBLISHSTATUS` from the Salesforce CSV export.
2. **Pre-processing** — `_strip_toc_elements()` removes ToC jump-link lists and "Back/Return to top" navigation before the HTML is converted.
3. **markdownify conversion** — `_DomoMDXConverter` converts HTML to Markdown with image placeholders, rewriting internal Salesforce URLs to language-appropriate repo-relative paths.
4. **Image restoration** — `_restore_images()` replaces placeholders with either `<Frame>` screenshot blocks or inline `<img>` icon syntax, based on image dimensions and HTML context.
5. **Callout conversion** — `_convert_callouts()` converts `**Note:**`, `**Important:**`, `**Warning:**`, `**Tip:**` paragraphs to `<Note>`, `<Warning>`, `<Tip>` components.
6. **FAQ conversion** — `_convert_faq()` converts FAQ sections to `<AccordionGroup>`/`<Accordion>` components.
7. **Artifact cleanup** — strips `— | —` Salesforce divider artifacts and collapses excess blank lines.
8. **Frontmatter** — wraps the result in a `---\ntitle: "..."\n---` YAML block.

---

## Formatting Rules (from New-Article-Template.mdx)

Apply these exact MDX patterns wherever the corresponding element appears.

**Screenshots**
```mdx
<Frame>![alt text describing the screenshot](/images/kb/image-name.png)</Frame>
```
- Wrapping in `<Frame>` is required — it auto-sizes the image to the content column width.
- Alt text must describe what the screenshot shows, not just "screenshot."

**Inline icons**
```mdx
<img alt="alt text" src="/images/kb/icon-name.png" style={{width: 20, height: 20, display: 'inline', verticalAlign: 'start', margin: '0'}}/>
```
- Use for small icons embedded mid-sentence (≤ 40px in either dimension).
- `display: 'inline'` and `verticalAlign: 'start'` keep the icon aligned with surrounding text.

**Callout components** (always bold the label inside)
```mdx
<Note>**Note:** Text here.</Note>
<Warning>**Important:** Text here.</Warning>
<Tip>**Tip:** Text here.</Tip>
```

**FAQ section**
```mdx
## FAQ

<AccordionGroup>

<Accordion title="Question text here?">
Answer text here.
</Accordion>

</AccordionGroup>
```
- FAQ goes at the bottom of the article, above Troubleshooting if it exists.
- One `<Accordion>` per question/answer pair.

**Frontmatter**
```mdx
---
title: "Article Title Here"
---
```

---

## Style Rules

### A — Enforced programmatically by `html_to_mdx.py`

These are already handled and should be correct in any script output:

| Rule | What the script does |
|------|---------------------|
| No table of contents | `_strip_toc_elements()` removes jump-link `<ul>`/`<ol>` lists before conversion |
| No "Back/Return to top" links | `_strip_toc_elements()` removes these anchor links and their parent paragraphs |
| No `— \| —` divider artifacts | Stripped with `re.sub(r"\n*—\s*\|\s*—\n*", "\n\n", md)` |
| Callout blocks use MDX components | `_convert_callouts()` converts bold-label paragraphs |
| FAQs use AccordionGroup | `_convert_faq()` converts FAQ sections |
| Internal links are repo-relative | `convert_a()` rewrites `domo-support.domo.com/s/article/…` links |
| Screenshots wrapped in `<Frame>` | `_restore_images()` wraps large/standalone images |
| Inline icons use `<img style>` | `_restore_images()` uses dimension + context signals |
| YAML frontmatter added | `html_to_mdx()` wraps output in `---\ntitle: "..."\n---` |

### B — Requiring human review after conversion

The script cannot reliably fix these. Review every converted article for:

**Voice and headings**
- [ ] All headings use the **imperative mood** — never the gerund. **Correct:** "Connect a DataSet" **Incorrect:** "Connecting a DataSet"
- [ ] "select" not "click" (except right-click, left-click, double-click)
- [ ] Present tense throughout ("This opens the panel" not "This will open the panel")
- [ ] Active voice — no passive voice unless the actor is genuinely unknown
- [ ] No exclamation points
- [ ] Numbers below 10 are spelled out

**Word choices to fix manually**
- [ ] `whitelist` → `allowlist`, `blacklist` → `blocklist`
- [ ] `utilize` / `utilizes` / `utilizing` → `use`
- [ ] `once` used as a causal connector → `after` ("After you save" not "Once you save")
- [ ] No Latin abbreviations (`i.e.`, `e.g.`, `etc.`) — use "such as," "as in," or a list

**Punctuation and formatting**
- [ ] No spaces around em-dashes: `tools—such as these—work` not `tools — such as these — work`
- [ ] Oxford comma in lists of three or more
- [ ] Bold static UI elements (`**Save**`, `**Admin** > **Security**`)
- [ ] No bold on the `>` in navigation paths

**Domo terminology (capitalize exactly)**

| Correct | Never use |
|---------|-----------|
| DataSet | Dataset, dataset |
| DataFlow | Dataflow |
| DataFusion | Data Fusion |
| Magic ETL | magic ETL |
| Beast Mode | Beastmode, beast mode |
| AppDB | App DB, appDB |
| Dashboard | Page, Domo story |
| Dashboard Filters | Page Filters |
| Data Center | data center |
| Alerts Center | alerts center |
| Drill Path / drill into | Drilldown |
| Visualization Card | KPI card |
| Doc Card | image card |
| Community Forums | Dojo |

**Article structure**
- [ ] Intro → Required Grants → Access Feature → CRUD tasks (Create/Review/Update/Delete, include only those that apply) → FAQ
- [ ] Any `<!-- TODO: embed image → ... -->` comments left by the script must be resolved manually (image wasn't downloaded)
- [ ] FAQ items that didn't match the bold-Q/paragraph-A or numbered-list patterns are left verbatim and need manual `<AccordionGroup>` conversion

---

## Review Procedure

When invoked, do the following:

1. **Read the file** at the path provided in `$ARGUMENTS`. If a title is given instead, find the file with `grep -r "title:.*<title>" s/article/`.
2. **Scan for human-review items** from Section B above.
3. **Check image placeholders** — search for `<!-- TODO: embed image` comments and flag them.
4. **Check for leftover Salesforce artifacts** — any remaining `— | —`, bare Salesforce URLs, or raw HTML tags that markdownify didn't convert.
5. **Apply fixes** to items from Section B that are clearly wrong (e.g., incorrect Domo terminology, `whitelist` → `allowlist`).
6. **List items requiring editorial judgment** (e.g., gerund headings, passive-voice sentences) with line numbers so the user can decide.
7. **Write the corrected file** and report what was changed vs. what needs the user's review.
