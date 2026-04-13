---
name: cleanup-localized-article
user-invocable: true
description: "clean up a localized KB article, fix broken image embeds, convert inline callouts to components, remove video sections, fix conversion artifacts"
argument-hint: "path(s) to localized article file(s), e.g. es/s/article/360042922994.mdx"
---

Clean up one or more localized KB articles that were programmatically converted from Salesforce. These articles typically have broken image embeds, inline callout formatting instead of Mintlify components, video sections that no longer render, and other conversion artifacts.

The user has provided: $ARGUMENTS

---

## Overview

Localized articles (under `de/`, `es/`, `fr/`, `ja/`) are converted from Salesforce and often arrive with a consistent set of structural problems. This skill applies a standard set of fixes to make them match Mintlify conventions.

A reference ("template") article is used to understand the intended structure before editing the target. The reference is typically a cleaner version of the same article in another locale.

---

## Step 1: Ask the user for file paths

Before doing anything else, use AskUserQuestion to ask:

1. **Which file should be used as the reference template?** (the clean version to model structure after)
2. **Which file should be edited?** (the article with conversion problems to fix)

If `$ARGUMENTS` was provided, pre-fill your question with paths parsed from it and ask the user to confirm or correct them rather than asking from scratch.

Once both paths are confirmed:
1. Verify both files exist.
2. Read the reference file first to understand the intended structure.
3. Read the target file in full.

---

## Step 2: Apply standard cleanup rules

Work through each rule below. Apply all that are relevant to the file — do not skip rules because the file "looks mostly clean."

### Rule 1 — Remove TODO image comments

Remove all `<!-- TODO: embed image -->` comments (including variants with `→`, `->`, or extra spaces). Also remove any blank lines immediately above and below the comment that exist solely as padding around it.

**Before:**
```
Haga clic en

<!-- TODO: embed image →  -->

**> Data Center**.
```
**After:**
```
Haga clic en **> Data Center**.
```

### Rule 2 — Remove broken inline images

Remove `<Frame>![...](...)</Frame>` blocks and `<img ... />` tags that are embedded *within* a sentence or step (i.e., they represent a UI icon or button, not a standalone screenshot). Merge the surrounding text into a single clean sentence.

Keep standalone `<Frame>` blocks that represent full screenshots on their own line — those are valid content.

**Before:**
```
haga clic en <img alt="gear.jpg" src="/images/kb/es/0EM5w.jpg" style={{...}}/> y seleccione **Ejecutar**.
```
**After:**
```
haga clic en y seleccione **Ejecutar**.
```

### Rule 3 — Convert inline callouts to Mintlify components

Replace inline bold callout patterns with the proper Mintlify component. Match regardless of language.

| Inline pattern | Component to use |
|---|---|
| `**Note:**`, `**Nota:**`, `**Notas:**`, `**Hinweis:**`, `**Hinweise:**`, `**注:**`, `**注意:**` | `<Note>` |
| `**Tip:**`, `**Consejo:**`, `**Tipp:**`, `**ヒント:**` | `<Tip>` |
| `**Important:**`, `**Importante:**`, `**Wichtig:**`, `**重要:**` | `<Warning>` |
| `**Warning:**`, `**Advertencia:**`, `**Warnung:**`, `**警告:**` | `<Warning>` |

Always bold the label inside the component (the existing bold formatting carries over).

**Before:**
```
**Nota:** Los DataSets de entrada ya *deben* existir en Domo.
```
**After:**
```
<Note>
**Nota:** Los DataSets de entrada ya *deben* existir en Domo.
</Note>
```

When the inline callout is a multi-sentence block, include the full block inside the component.

When a callout is already inside a `<Note>`, `<Tip>`, or `<Warning>` component, leave it alone.

### Rule 4 — Remove all video content

Remove any content related to training videos. This includes:

- Section headers that are video titles (e.g., `**Vídeo de aprendizaje: ...**`, `**Training video: ...**`, `**Schulungsvideo: ...**`)
- Descriptive sentences that introduce or reference a video (e.g., "Watch this video to learn...", "Vea este vídeo para...", "Folgen Sie dieser Übung...")
- `<Note>` or inline notes whose sole content is a statement that videos are only for Domo customers
- Part labels for multi-part video series (e.g., `**Part 1 of 3**`, `**Parte 1 de 2**`, `**Teil 1 von 4**`)
- Sentences mentioning Adobe Flash Player

After removing video content, also remove any blank lines left behind that create unwanted vertical gaps.

### Rule 5 — Fix run-on text from bad conversions

Some articles have lines where two separate paragraphs, sentences, or sections were merged onto a single line during conversion. Look for telltale signs:
- A sentence that ends and a new bold heading or sentence that begins without a line break
- A `**Nota:**` or other callout label that appears mid-sentence after unrelated content

Split these back into their correct separate elements.

**Before:**
```
**Nota:** Los vídeos de aprendizaje sobre productos solo están dirigidos a clientes de Domo.**Vídeo de aprendizaje: Información general**Vea este breve vídeo...
```
**After** (each element on its own line, then Rule 4 removes the video content):
```
<Note>
**Nota:** Los vídeos de aprendizaje sobre productos solo están dirigidos a clientes de Domo.
</Note>

**Vídeo de aprendizaje: Información general**

Vea este breve vídeo...
```

### Rule 6 — Fix conversion typos

Correct obvious character-level artifacts introduced by the conversion process. Common patterns:
- Stray closing brackets mid-word (e.g., `está]` → `están`, `clientes]` → `clientes`)
- Doubled punctuation
- Missing spaces between a closing `**` and the next word

Only fix what is clearly a conversion error, not a translation issue.

---

## Step 3: Execute and report

Apply all applicable rules using the Edit or Write tool. When the changes are extensive (many rules apply throughout a long file), a full rewrite with Write is cleaner than many small Edits.

After completing each file, report:
- Which rules were applied and how many instances of each were fixed
- Anything ambiguous that was left for the user to review
- Any structural differences noticed between the reference and the edited file that may warrant a separate review
