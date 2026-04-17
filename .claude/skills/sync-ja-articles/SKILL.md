---
name: sync-ja-articles
description: Diff each queued Japanese article in ja/s/article/ against its English counterpart in s/article/ and apply all necessary formatting, MDX component, and image-embedding fixes while keeping Japanese text intact.
---

# Sync Japanese Articles to English Structure

## What this skill does

For every modified Japanese article queued in `ja/s/article/`, compare it to the matching English article in `s/article/` (same filename) and apply structural fixes so the MDX formatting, components, and image-embedding syntax match the English version — while leaving all Japanese text completely unchanged.

## Step-by-step instructions

### Step 1 — Build the file list

Run the following to get the list of modified Japanese articles:

```bash
git diff --name-only --cached; git diff --name-only
```

Filter results to lines matching `ja/s/article/*.mdx`. Deduplicate. This is your working list.

Use TodoWrite to create one task per file so you can track progress across the full batch.

### Step 2 — Process each file

For each Japanese article in the list:

1. **Read** the English article at `s/article/<filename>`.
2. **Read** the Japanese article at `ja/s/article/<filename>`.
3. **Diff and fix** (see rules below).
4. **Write** the corrected content back to the Japanese file using the Edit tool.
5. Mark the TodoWrite task complete.

Work through the list sequentially. Do not skip files.

---

## Fix rules

Apply every rule below. Do not make any other changes.

### 1. Remove TOC back-links
Delete any line containing `[#toc](#toc)` (e.g. `[#toc](#toc)[このページのトップへ](#toc)`). These never appear in English articles.

### 2. Image embedding syntax — PATHS MUST NOT CHANGE
The Japanese article has its own image paths (e.g. `/images/kb/ja/0EM5w.jpg`). These are correct localized screenshots — **never change the src/path values**.

Fix only the *embedding syntax* to match the English:
- If the English wraps the corresponding image in `<Frame>![alt](/images/kb/…)</Frame>`, wrap the Japanese image the same way: `<Frame>![Japanese alt text](/images/kb/ja/…)</Frame>`. Keep the Japanese `src` path and any Japanese alt text.
- If the English uses a bare `<img>` tag with style attributes (width, height, display, verticalAlign, margin), apply those same style attribute values to the Japanese `<img>` tag, keeping the Japanese `src` path unchanged.
- If the Japanese article is missing a `<Frame>` wrapper that the English has, add it. If it has an extra wrapper the English doesn't, remove it.

### 3. Callout components
Convert plain-text Japanese callouts to proper Mintlify components. The label and body text stay in Japanese inside the component.

| Plain text pattern | Component to use |
|--------------------|-----------------|
| `**注記：** …` or `**注記****：** …` | `<Note>**注記：** …</Note>` |
| `**警告：** …` | `<Warning>**警告：** …</Warning>` |
| `**ヒント：** …` | `<Tip>**ヒント：** …</Tip>` |

Multi-line callouts: include all consecutive lines belonging to the same callout inside the single component tag.

If the English uses `<Note>`, `<Warning>`, or `<Tip>` and the Japanese already has the correct component, leave it alone.

### 4. AccordionGroup / FAQ sections
If the English article has an `<AccordionGroup>` + `<Accordion title="…">` block and the Japanese article renders the same Q&A as plain text or a flat list, wrap the Japanese content in `<AccordionGroup>` + `<Accordion title="…">` tags. Use the Japanese question text as the `title` attribute value. Keep all Japanese answer text inside the accordion body.

### 5. Code block formatting
If a code block in the Japanese article has multiple commands collapsed onto a single line (missing newlines between commands), restore the line breaks to match the English version's code block. Do not change the command content itself.

### 6. Heading levels
If a heading uses the wrong number of `#` characters compared to the structurally equivalent heading in the English article, correct the level. Do not change the Japanese heading text.

### 7. Frontmatter
Leave all frontmatter values (including the Japanese `title`) exactly as they are.

---

## Critical rules — read before editing any file

- **Never translate, reword, or alter any Japanese text.** Every Japanese character must be returned exactly as found.
- **Never change any image `src` or file path.** Only fix embedding syntax (wrappers and attributes).
- **Never add or remove content sections** (headings, paragraphs, tables) beyond what the rules above require.
- **Do not "improve" or reformat content** beyond the rules above — even if something looks off, leave it unless it matches one of the fix rules.
- After editing each file, do a quick sanity check: confirm the Japanese text is intact and no image paths were changed.
