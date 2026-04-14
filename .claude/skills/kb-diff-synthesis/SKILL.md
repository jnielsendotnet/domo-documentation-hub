# SKILL: Diff and Synthesize Documentation Versions

## Overview
This skill compares two versions of a documentation file (old and new), identifies content differences, and produces a synthesized output that applies all updates from the new version while preserving HTML table formatting only where required (nested tables).

## Trigger Conditions
Use this skill when the user:
- Provides two versions of a documentation file and asks for a diff, synthesis, or both
- References an "old" and "new" version of a doc from a repository or version history
- Asks you to "apply changes" from one document to another
- Asks you to rewrite a doc "with updates from" another version

## Workflow

### Step 1 — Diff Analysis
When given two documents, perform a content-only diff. Structure your diff output as follows:

1. **Lead with identical content**: Briefly note what is unchanged (e.g. "The Prerequisites, Credentials Pane, and Troubleshooting sections are identical in content.") so the user knows what to expect.
2. **Group differences by type**, using clear headers:
   - **Title changes**
   - **Added content** (new sections, new fields, new reports, new notices)
   - **Removed content** (deprecated fields, removed reports, deleted sections)
   - **Renamed content** (fields or reports that have been renamed)
   - **Wording/description changes** (minor rewording, punctuation, numerals vs. words)
   - **Link changes** (absolute vs. relative URLs, changed destinations)
   - **Formatting-only changes** (HTML vs. Markdown tables, bullet style, heading level, FAQ structure) — note these but flag them as non-content
3. **Use comparison tables** where multiple items have changed, e.g. for report lists or endpoint tables:
   | Doc X (old) | Doc Y (new) |
   | --- | --- |
   | Old report name | New report name |
4. **Flag ambiguous cases** — e.g. if a screenshot appears to be a full-page image rather than an inline icon, note that it may need special handling. If a FAQ section uses plain headings or any format other than `<AccordionGroup>`, flag it as a formatting issue requiring correction in synthesis.

### Step 2 — Synthesis
When asked to synthesize the two documents into a new version:

1. **Use the new document as the base** for all content decisions.
2. **Apply all content updates from the new document**, including:
   - New or renamed reports/fields
   - Deprecated labels (e.g. appending "(Deprecated)" to report names)
   - New sections or notices (e.g. deprecation banners)
   - Updated field descriptions
   - Updated link paths (use the new document's relative paths, not the old document's absolute URLs)
   - Removed content (do not include items present only in the old document)
3. **Preserve non-table formatting conventions from the new document**, including:
   - Bullet point style (`-` not `*`)
   - Heading levels
   - Horizontal rules
   - `<Note>` or other MDX component usage
4. **Preserve image embeds** using the format and paths from the new document.
5. **Do not include** verbose `title` attributes on links unless present in the new document.
6. **Always convert FAQ sections to `<AccordionGroup>` format** (see FAQ Formatting below), regardless of what format either document uses.

## FAQ Formatting

FAQ sections must always use the `<AccordionGroup>` / `<Accordion>` component structure. This is a hard requirement — plain `####` headings, bold questions, or any other FAQ format must be converted during synthesis.

### Required structure:

```mdx
<AccordionGroup>

<Accordion title="Frequently asked question?">
Frequently asked answer.
</Accordion>

<Accordion title="Frequently asked question?">
Frequently asked answer.
</Accordion>

</AccordionGroup>
```

### Placement:
The FAQ section belongs at the bottom of the article, above only Troubleshoot or Related Articles (if present).

### Conversion rules:
- The question text goes in the `title` attribute of `<Accordion>`. Do not include a question mark in the component tag itself — put it inside the title string as normal punctuation.
- The answer content goes inside the `<Accordion>` body. Preserve all formatting (lists, code blocks, links, callouts) from the source answer.
- If either document uses `####` headings or bolded questions for FAQs, treat the heading/question text as the `title` and the following content as the body.
- If neither document has a FAQ section but one is being added, follow this structure from the start.
- During diffing: if one document uses `<AccordionGroup>` and the other does not, flag it as a formatting-only change and note it will be normalized to `<AccordionGroup>` in synthesis.

## Table Formatting Rules

**Default: use Markdown tables with evenly spaced pipe-bar columns.** Only use HTML for tables that contain a nested table inside them — and in that case, only the nested table itself needs to be written in HTML; the outer table may remain Markdown unless it too is nested inside another table.

### When to use Markdown (default)

All standard tables — reference tables, field/description tables, report lists without nesting — must be written as Markdown with aligned pipe-bar columns:

```markdown
| Column Header 1      | Column Header 2                        |
| -------------------- | -------------------------------------- |
| Row label            | Row description                        |
| Another label        | Another description                    |
```

Keep columns evenly spaced so the raw source is readable.

### When to use HTML (nested tables only)

If a table cell contains a nested table, write that nested table in HTML. The outer/parent table may stay in Markdown unless it is itself nested inside another table.

**Nested table written in HTML (inside a Markdown table cell):**

```markdown
| Field   | Details                                                                                                           |
| ------- | ----------------------------------------------------------------------------------------------------------------- |
| Report  | Select the report you want to run. The following reports are available:<br/><table border="1" cellpadding="1" cellspacing="1"><tbody><tr><td colspan="1" rowspan="1"><p>Report Name</p></td><td colspan="1" rowspan="1"><p>Description</p></td></tr></tbody></table> |
```

**Fully HTML table (only required when the outer table is itself nested):**

```html
<table border="1" cellpadding="1" cellspacing="1">
  <thead>
    <tr>
      <th colspan="1" rowspan="1"><p>Column Header 1</p></th>
      <th colspan="1" rowspan="1"><p>Column Header 2</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="1" rowspan="1"><p>Row label</p></td>
      <td colspan="1" rowspan="1"><p>Row description</p></td>
    </tr>
  </tbody>
</table>
```

### HTML table conventions (when HTML is required)
- Wrap all cell text content in `<p>` tags
- Use `<b>` for bold text inside cells (not Markdown `**`)
- Use `<a href="...">link text</a>` for links inside cells
- Use `<ul><li>...</li></ul>` for lists inside cells
- Use `<span class="mt-font-courier-new">...</span>` for inline code inside cells

### Info/metadata table (no header row, left column is bold label):
Use HTML only if this table contains a nested table. Otherwise, use Markdown. If HTML is needed:

```html
<table class="mt-responsive-table">
  <tbody>
    <tr>
      <td class="mt-noheading" colspan="1" rowspan="1"><p><b>Label</b></p></td>
      <td class="mt-noheading" colspan="1" rowspan="1"><p>Value</p></td>
    </tr>
  </tbody>
</table>
```

## Image Embed Handling

### Full-page screenshots (e.g. UI screenshots, diagrams):
Leave these as `<Frame>` tags:
```mdx
<Frame>![alt text](/images/kb/filename.png)</Frame>
```

### Inline icon images (small UI icons referenced mid-sentence):
Always use the inline `<img>` format exactly as written in the new document. Do not invent dimensions or styles — copy the tag from the new version verbatim. The expected format is:

```mdx
<img src="/images/kb/worksheets-icon-1.png" style={{width: 20, height: 20, display: 'inline', verticalAlign: 'start', margin: '0'}}/>
```

If the new document contains an inline image tag, copy it as-is, including the exact `src` path, `width`, `height`, and style values. Do not convert it to a `<Frame>` or any other format.

**How to tell the difference**: If the image is referenced inline within a sentence or table cell alongside text (e.g. "Click the <img/> icon"), use the inline format. If the image stands alone as a visual reference between paragraphs or steps, use `<Frame>`. If ambiguous, flag it for the user.

## Common Patterns and Edge Cases

### Deprecated items
When a report or feature is marked as deprecated in the new document, append **(Deprecated)** to its name in the output. Do not remove it — deprecated items are kept but labeled.

### New items added in the new document
Include all new reports, fields, sections, and notices from the new document. Do not omit them.

### Items removed in the new document
If something appears in the old document but not the new document, omit it from the synthesis output unless it is deprecated (in which case, keep it with the deprecated label).

### Link paths
Always use the relative paths from the new document (e.g. `/s/article/360042926274`) rather than the absolute URLs from the old document (e.g. `https://domo-support.domo.com/s/article/360042926274?language=en_US`).

### FAQ sections
- **Always output FAQs using `<AccordionGroup>` / `<Accordion>` components**, regardless of the format used in either source document. See FAQ Formatting above.
- If the new document removes content from a FAQ entry (e.g. an embedded video), omit that content from the synthesis.
- If both documents have FAQ content but structure it differently, merge all unique questions into a single `<AccordionGroup>`, applying all content updates from the new document.

### Deprecation banners
If the new document adds a top-level deprecation notice (e.g. `<Note>**Note:** **This KB has been deprecated.**</Note>`), include it immediately after the frontmatter, before the first section.

## Output Format

- Output the full synthesized document inside a single fenced code block tagged as `mdx`
- Do not add commentary inside the code block
- After the code block, add a brief note only if there are ambiguous cases the user should review (e.g. images that may need dimension adjustments, or content whose deprecation status is unclear)

## Example Invocations

**Diff only:**
> "Run a diff between these two documents."

**Synthesis only (after a prior diff):**
> "Now synthesize the two using the updates from Doc 2, keeping tables in HTML."

**Diff and synthesize in one step:**
> "Compare these two versions and give me a synthesized output applying all changes from the new version, with HTML tables."