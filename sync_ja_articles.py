#!/usr/bin/env python3
"""
Sync Japanese MDX article formatting to match English counterparts.

For each modified Japanese article in ja/s/article/, this script:
  1. Applies fast regex fixes (image paths, TOC links).
  2. Calls the Claude API to align MDX structure (Note/Warning/Tip components,
     AccordionGroup/Accordion, code-block line breaks, inline images) while
     keeping all Japanese text intact.

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Usage:
    python sync_ja_articles.py                       # all modified JA articles
    python sync_ja_articles.py --dry-run             # preview, no writes
    python sync_ja_articles.py --file 000005303.mdx  # single file
    python sync_ja_articles.py --workers 3           # tune parallelism
    python sync_ja_articles.py --skip-claude         # quick fixes only (no API)
"""

import argparse
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("anthropic package not found. Run: pip install anthropic")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
EN_DIR = REPO_ROOT / "s" / "article"
JA_DIR = REPO_ROOT / "ja" / "s" / "article"
MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
SYNC_PROMPT = """\
You are a technical documentation editor. I have two versions of the same KB article:
1. ENGLISH — the authoritative source for structure, formatting, and MDX components.
2. JAPANESE — needs structural fixes to match the English version; Japanese text must stay in Japanese.

Apply ONLY the following changes to the Japanese article. Do not change anything else.

### Changes to apply

1. **Image embedding syntax**
   The Japanese article has its own image file paths (e.g. `/images/kb/ja/…`) that
   must NOT be changed — those point to localized screenshots and are correct as-is.
   What you must fix is HOW the image is embedded, to match the English article's
   embedding structure for the corresponding image:
   - If the English uses `<Frame>![alt text](/images/kb/…)</Frame>`, wrap the
     Japanese image in `<Frame>` the same way, keeping the Japanese path and
     any Japanese alt text.
   - If the English uses a bare `<img>` tag with style attributes (width, height,
     display, verticalAlign, margin), apply the same style attributes to the
     Japanese `<img>` tag, keeping the Japanese src path unchanged.
   - Never swap or replace a Japanese image path with an English one.

3. **Callout components**
   Convert plain-text Japanese callouts to proper Mintlify components:
   - `**注記：** …`  → `<Note>**注記：** …</Note>`
   - `**警告：** …`  → `<Warning>**警告：** …</Warning>`
   - `**ヒント：** …` → `<Tip>**ヒント：** …</Tip>`
   The content of the callout stays in Japanese. The opening label (`**注記：**` etc.)
   also stays in Japanese inside the component. Multi-line callouts: include all
   consecutive lines that are part of the same note/warning/tip.

4. **FAQ / Accordion sections**
   If the English article has `<AccordionGroup>` + `<Accordion title="…">` blocks and
   the Japanese article has the same Q&A content as plain text or a different structure,
   wrap the Japanese content in `<AccordionGroup>` + `<Accordion title="…">` tags,
   using the Japanese question text as the title. Keep all Japanese answer text.

5. **Code block formatting**
   If a code block in the Japanese article has multiple commands collapsed onto one
   line (missing newlines), restore line breaks to match the English version.
   Do not change the code content itself.

6. **TOC back-links** (already removed by pre-processing — included for completeness)
   Remove any `[#toc](#toc)[このページのトップへ](#toc)` patterns.

7. **Heading levels**
   If a heading in the Japanese article uses the wrong number of `#` characters
   compared to the corresponding English heading, fix the level. Do not change
   Japanese heading text.

### Critical rules
- **Never translate or rewrite any Japanese text.** Return Japanese exactly as-is.
- **Never change any image file path or src value in the Japanese article.** Only
  change the surrounding embedding syntax (tags, attributes) to match the English.
- **Never add, remove, or restructure content sections** beyond what is required
  by the changes above.
- **Return ONLY the corrected MDX.** No explanations, no surrounding code fences.

---

ENGLISH ARTICLE:
{en_content}

---

JAPANESE ARTICLE TO FIX:
{ja_content}

---

Return the corrected Japanese article:"""

# ---------------------------------------------------------------------------
# Quick regex fixes (no API needed)
# ---------------------------------------------------------------------------
_TOC_LINK = re.compile(r'\[#toc\]\(#toc\)\[.*?\]\(#toc\)\s*', re.DOTALL)


def apply_quick_fixes(content: str) -> str:
    """Apply cheap, deterministic regex fixes before calling the API."""
    # Remove TOC back-links — these never appear in English articles
    content = _TOC_LINK.sub('', content)
    return content


# ---------------------------------------------------------------------------
# Claude API call with simple retry
# ---------------------------------------------------------------------------
def call_claude(en_content: str, ja_content: str, client: anthropic.Anthropic,
                max_retries: int = 3) -> str:
    prompt = SYNC_PROMPT.format(en_content=en_content, ja_content=ja_content)
    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # Strip accidental markdown code fences Claude might add
            if text.startswith("```"):
                text = re.sub(r'^```[^\n]*\n', '', text)
                text = re.sub(r'\n```\s*$', '', text)
            return text
        except anthropic.RateLimitError:
            if attempt < max_retries:
                time.sleep(30 * attempt)
            else:
                raise
        except anthropic.APIStatusError as exc:
            if attempt < max_retries and exc.status_code >= 500:
                time.sleep(5 * attempt)
            else:
                raise
    raise RuntimeError("Unreachable")


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------
def process_file(ja_path: Path, client: anthropic.Anthropic | None,
                 dry_run: bool) -> str:
    """Process one Japanese article. Returns a one-line status string."""
    filename = ja_path.name
    en_path = EN_DIR / filename

    if not en_path.exists():
        return f"SKIP  {filename}  (no English counterpart found)"

    en_content = en_path.read_text(encoding="utf-8")
    ja_content = ja_path.read_text(encoding="utf-8")

    # Step 1: fast regex pass
    ja_fixed = apply_quick_fixes(ja_content)

    # Step 2: structural alignment via Claude (optional)
    if client is not None:
        ja_final = call_claude(en_content, ja_fixed, client)
    else:
        ja_final = ja_fixed

    if dry_run:
        changed = ja_final != ja_content
        return f"DRY   {filename}  ({'changes detected' if changed else 'no changes'})"

    if ja_final != ja_content:
        ja_path.write_text(ja_final, encoding="utf-8")
        return f"OK    {filename}"

    return f"SAME  {filename}  (no changes needed)"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------
def get_modified_ja_files() -> list[Path]:
    """Return paths of modified JA article files visible to git."""
    def git_diff(*args: str) -> list[str]:
        result = subprocess.run(
            ["git", "diff", *args, "--name-only"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        return result.stdout.strip().splitlines()

    lines = set(git_diff("--cached") + git_diff())
    return sorted(
        REPO_ROOT / p
        for p in lines
        if p.startswith("ja/s/article/") and p.endswith(".mdx")
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing files",
    )
    parser.add_argument(
        "--workers", type=int, default=5,
        help="Number of parallel API calls (default: 5)",
    )
    parser.add_argument(
        "--file",
        help="Process a single file by name, e.g. 000005303.mdx",
    )
    parser.add_argument(
        "--skip-claude", action="store_true",
        help="Apply quick regex fixes only; skip Claude API calls",
    )
    args = parser.parse_args()

    # Resolve file list
    if args.file:
        target = JA_DIR / args.file
        if not target.exists():
            sys.exit(f"File not found: {target}")
        files = [target]
    else:
        files = get_modified_ja_files()
        if not files:
            sys.exit("No modified Japanese articles found in git status.")

    # Set up Claude client (unless --skip-claude)
    client: anthropic.Anthropic | None = None
    if not args.skip_claude:
        client = anthropic.Anthropic()

    mode = "DRY RUN — " if args.dry_run else ""
    api_note = "regex fixes only" if args.skip_claude else f"Claude {MODEL}"
    print(f"{mode}Processing {len(files)} article(s) | {api_note} | {args.workers} worker(s)\n")

    counts = {"OK": 0, "SAME": 0, "DRY": 0, "SKIP": 0, "ERROR": 0}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(process_file, f, client, args.dry_run): f
            for f in files
        }
        for future in as_completed(futures):
            path = futures[future]
            try:
                msg = future.result()
                print(msg)
                key = msg.split()[0]
                counts[key] = counts.get(key, 0) + 1
            except Exception as exc:  # noqa: BLE001
                print(f"ERROR {path.name}: {exc}")
                counts["ERROR"] += 1

    print(
        f"\nDone. "
        f"{counts['OK']} updated, "
        f"{counts['SAME']} unchanged, "
        f"{counts['SKIP']} skipped, "
        f"{counts['DRY']} dry-run previewed, "
        f"{counts['ERROR']} errors."
    )


if __name__ == "__main__":
    main()
