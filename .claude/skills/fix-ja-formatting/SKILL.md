---
name: fix-ja-formatting
description: Compare queued Japanese articles in ja/s/article/ against their English counterparts in s/article/ and fix structural formatting issues — inline image placement, Frame vs. InlineImage mismatches, callout component wrapping, and redundant blank lines — while leaving all Japanese text and image paths untouched.
user-invocable: true
argument-hint: "optional: path(s) to specific Japanese article file(s), e.g. ja/s/article/000005143.mdx. Omit to process all queued articles."
---

# Fix Japanese Article Formatting

## What this skill does

For each target Japanese article in `ja/s/article/`, read it alongside the structurally correct English counterpart in `s/article/` (same filename). Identify formatting discrepancies, then apply surgical fixes.

The English version is the authority on **structure and layout**: which images are inline vs. standalone screenshots, where inline images sit relative to surrounding text, how callouts are wrapped, and how much vertical whitespace separates elements.

The Japanese version is the authority on **content**: all Japanese text stays exactly as-is, and all image `src` paths are correct localized paths that must never change.

The user has provided: $ARGUMENTS

---

## Step 1 — Build the file list

**If `$ARGUMENTS` was provided**, parse it for one or more `ja/s/article/*.mdx` paths. Verify each file exists.

**If no arguments were provided**, run:

```bash
git diff --name-only HEAD -- 'ja/s/article/*.mdx'; git diff --name-only --cached -- 'ja/s/article/*.mdx'
```

Deduplicate the combined output. This is your working list.

Use TodoWrite to create one task per file.

---

## Step 2 — Diff and fix each file

For each file in the list:

1. Read the English article at `s/article/<filename>`.
2. Read the Japanese article at `ja/s/article/<filename>`.
3. Perform a **structural diff** (see Diff Analysis below).
4. Apply all applicable fixes (see Fix Rules below).
5. Write the corrected content back using Edit or Write.
6. Mark the TodoWrite task complete.

Work through the list sequentially.

---

## Diff Analysis

Before editing, mentally map the structure of both articles paragraph by paragraph. Flag each of the following discrepancies — these are the only categories you will fix:

### Category A — Inline image placement
An inline image is one that appears **within a sentence, list item, or step** — not standing alone between paragraphs. Determine which each is by looking at the English:

- If the English embeds an image inline (using `<InlineImage src="..." />` within a line of text), that image is **inline**.
- If the English puts a `<Frame>` or `<Frame><img .../></Frame>` on its own line between paragraphs or steps, that image is a **standalone screenshot**.

Flag any place where the Japanese article has the wrong treatment for the image type.

### Category B — InlineImage broken off from surrounding text
The Japanese article may have a correct `<InlineImage>` component but placed on a **separate line** from the text it belongs to. The result is a line break mid-sentence, between the step number and the step text, or between a list bullet and its continuation.

Flag every instance where an `<InlineImage>` sits on its own line when the English has it inline within the same line as surrounding text.

### Category C — Callout components
Flag any callout (`**注記：**`, `**警告：**`, `**重要：**`, `**ヒント：**`, `**注意：**`) that is plain bold text but whose English counterpart is wrapped in `<Note>`, `<Warning>`, or `<Tip>`.

Also flag the reverse: if the Japanese is missing a closing `</Note>` / `</Warning>` / `</Tip>` tag, or has stray blank lines inside a callout that break the component.

### Category D — Redundant blank lines
Flag sequences of multiple blank lines (2+) between adjacent elements where the English has one blank line or no gap. Also flag trailing whitespace-only lines (lines containing only spaces) that are artifacts of conversion.

---

## Fix Rules

Apply every applicable rule. Do not make any other changes.

### Rule 1 — Fix Frame vs. InlineImage mismatches

**Scenario A: Japanese uses `<Frame>` for an image the English treats as inline.**

Convert each `<Frame>![alt](ja-path)</Frame>` to `<InlineImage src="ja-path" />`. Keep the Japanese `src` path exactly. Place the `<InlineImage>` on the same line as the surrounding text it belongs to (see Rule 2). Remove blank lines that were padding around the `<Frame>` block.

**Scenario B: Japanese uses `<InlineImage>` for an image the English treats as a standalone screenshot.**

Convert `<InlineImage src="ja-path" />` to `<Frame>![alt text](ja-path)</Frame>` on its own line. Keep the Japanese `src` path. Use the alt text from the English `<img>` tag if available, otherwise leave the brackets empty.

**Scenario C: Japanese `<Frame>` uses `![alt](path)` syntax and English `<Frame>` uses `<img>` with style attributes.**

Leave the Japanese `<Frame>![alt](ja-path)</Frame>` syntax unchanged. Do not attempt to add width/height style attributes from the English — those reference English image dimensions.

### Rule 2 — Merge inline images back into their text

When an `<InlineImage>` is on its own line but the English has it inline, merge it onto the correct line. The English article shows exactly where each inline image sits relative to the text.

**Before (Japanese — broken across lines):**
```
3. Domoツールバーで

<InlineImage src="/images/kb/ja/0EM5w000006u9Z1.jpg" /> **［検索］**を選択します。
```

**After (Japanese — fixed):**
```
3. Domoツールバーで <InlineImage src="/images/kb/ja/0EM5w000006u9Z1.jpg" /> **［検索］**を選択します。
```

Apply the same principle to list items, parenthetical insertions, and sentence-internal image references. The blank line above and below the orphaned `<InlineImage>` should be removed after the merge.

When a sentence is split across multiple lines because an `<InlineImage>` broke it, rejoin all parts into a single line.

**Before:**
```
ツールバーで**［Domo］**を選択（または、

<InlineImage src="/images/kb/ja/0EMVq000000liVR.jpg" /> **［その他］**>**［Domo］**を選択）し、メニューを表示します。
```

**After:**
```
ツールバーで**［Domo］**を選択（または、<InlineImage src="/images/kb/ja/0EMVq000000liVR.jpg" /> **［その他］**>**［Domo］**を選択）し、メニューを表示します。
```

### Rule 3 — Wrap callouts in Mintlify components

Replace inline bold callout patterns with the proper Mintlify component. Match the component type to what the English uses at the same location.

| Japanese inline pattern | Component |
|---|---|
| `**注記：**` or `**注記****：**` | `<Note>` |
| `**注意：**` or `**重要：**` | `<Warning>` |
| `**警告：**` | `<Warning>` |
| `**ヒント：**` | `<Tip>` |

Always bold the label inside the component. Multi-line callouts: include all consecutive lines belonging to the same callout inside a single component.

**Before:**
```
**注記：**コンテンツの受信者がDomoアドインを持っていない場合は…
```

**After:**
```
<Note>**注記：**コンテンツの受信者がDomoアドインを持っていない場合は…</Note>
```

If the callout spans multiple lines, keep the same multiline block structure the English uses:

```
<Note>
**注記：** …Japanese text…

More Japanese text continuing the note.
</Note>
```

### Rule 4 — Remove redundant blank lines

Remove extra blank lines between adjacent elements where the English has one blank line or none. Also remove lines that contain only whitespace (spaces or tabs but no other characters).

**Before:**
```
<Frame>![app1.png](/images/kb/ja/0EM5w000006vSPQ.jpg)</Frame>

     

<Frame>![app2.png](/images/kb/ja/0EM5w000006vSKL.jpg)</Frame>
```

**After** (once converted to InlineImage, now on one line — or if remaining as Frame blocks, remove the whitespace-only line between them):
```
<InlineImage src="/images/kb/ja/0EM5w000006vSPQ.jpg" /> <InlineImage src="/images/kb/ja/0EM5w000006vSKL.jpg" />
```

Do not collapse intentional blank lines that separate sections or steps. Match the English article's spacing pattern.

---

## Critical rules — read before editing any file

- **Never translate, reword, or alter any Japanese text.** Every Japanese character must be returned exactly as found.
- **Never change any image `src` path.** The Japanese image paths (e.g. `/images/kb/ja/0EM5w…`) are correct — only the embedding syntax and placement are fixed.
- **Never add or remove content sections** beyond what the rules above require.
- **Do not apply fixes from `sync-ja-articles`** (TOC back-links, heading levels, code block formatting, etc.) unless they are also explicitly listed in the Fix Rules above. This skill is focused solely on image placement, callout wrapping, and blank-line cleanup.
- **Do not remove or alter `import` statements** at the top of the file.

---

## Step 3 — Report

After completing each file, briefly report:

- Which categories of issues were found (A / B / C / D)
- How many instances of each were fixed
- Any edge cases left for the user to review (e.g. an image that is ambiguously inline vs. standalone, or a callout whose type was unclear)
