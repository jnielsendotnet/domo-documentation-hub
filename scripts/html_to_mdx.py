#!/usr/bin/env python3
"""
Converts Salesforce Knowledge HTML article bodies to Domo MDX format.

Handles:
  - Images:     width/height ≤ 40px → inline <img style> syntax (icon)
                larger or unsized   → <Frame>![alt](path)</Frame> (screenshot)
  - Links:      domo-support.domo.com/s/article/… → language-appropriate relative path
                  en_US → /s/article/…
                  ja    → /ja/s/article/…
                  de    → /de/s/article/…
                  fr    → /fr/s/article/…
                  es    → /es/s/article/…
  - Callouts:   **Note:**, **Important:**, **Warning:**, **Tip:** paragraphs
                → <Note>, <Warning>, <Tip> MDX components
  - FAQ:        ## FAQ/FAQs heading with bold-question / paragraph-answer pairs
                → <AccordionGroup>/<Accordion> components
  - Frontmatter: YAML ---title--- block added at the top

Content-level style rules from Domo-KB-Style-Guide.mdx that CANNOT be enforced
programmatically (e.g. imperative-mood headings, "select" not "click") are noted
in inline TODO comments when the pattern is detectable but left for human review
otherwise.

Usage as a module:
    from html_to_mdx import html_to_mdx
    mdx = html_to_mdx(html_body, title, image_local_map, language="en_US")

Usage from CLI (for testing a single article):
    python scripts/html_to_mdx.py input.html --title "My Article" [--language ja] [--image-map map.json]
"""

import re
import sys
import json
import argparse
from pathlib import Path

try:
    import markdownify
except ImportError:
    print("ERROR: markdownify required. Run: pip install markdownify")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Images with width OR height at/below this value (px) are treated as inline icons.
# Larger images (or images with no dimension attributes) are treated as screenshots.
INLINE_ICON_MAX_PX = 40

# Base URL for Salesforce-hosted Domo support articles (used to fix internal links)
SF_SUPPORT_BASE = "https://domo-support.domo.com/s/article/"

# Maps CSV language code → repo-relative article URL prefix
# Matches the directory structure: en_US → s/article, ja → ja/s/article, etc.
LANG_ARTICLE_PREFIX: dict[str, str] = {
    "en_US": "/s/article",
    "ja": "/ja/s/article",
    "de": "/de/s/article",
    "fr": "/fr/s/article",
    "es": "/es/s/article",
}

# Callout label → (MDX component name, bold label displayed inside component)
CALLOUT_MAP: dict[str, tuple[str, str]] = {
    "note": ("Note", "Note"),
    "important": ("Warning", "Important"),
    "warning": ("Warning", "Warning"),
    "caution": ("Warning", "Important"),
    "tip": ("Tip", "Tip"),
}


# ---------------------------------------------------------------------------
# Custom markdownify converter
# ---------------------------------------------------------------------------

class _DomoMDXConverter(markdownify.MarkdownConverter):
    """
    Extends markdownify.MarkdownConverter with Domo-specific behaviour:

    - <img>  →  placeholder string (restored after conversion via _restore_images)
    - <a>    →  internal Salesforce links rewritten to language-appropriate relative paths
    """

    def __init__(self, article_prefix: str = "/s/article", **kwargs):
        """
        Args:
            article_prefix: The repo-relative URL prefix for internal article links,
                            e.g. "/s/article" for English or "/ja/s/article" for Japanese.
        """
        super().__init__(**kwargs)
        self._article_prefix = article_prefix
        # Populated during conversion; key → {src, alt, width, height}
        self._images: dict[str, dict[str, str]] = {}

    def convert_img(self, el, text, parent_tags):
        """Replace each <img> with a unique placeholder and record its metadata."""
        key = f"__DOMO_IMG_{len(self._images)}__"
        self._images[key] = {
            "src": el.attrs.get("src", "") or "",
            "alt": (el.attrs.get("alt", "") or "").strip(),
            "width": str(el.attrs.get("width", "") or ""),
            "height": str(el.attrs.get("height", "") or ""),
        }
        # Extra newlines ensure the placeholder is on its own paragraph
        return f"\n\n{key}\n\n"

    def convert_a(self, el, text, parent_tags):
        """Rewrite internal Domo KB links to language-appropriate repo-relative paths."""
        href = (el.get("href") or "").strip()
        text = (text or "").strip()

        if not href:
            return text

        # Rewrite Salesforce support article links to repo-relative paths
        if SF_SUPPORT_BASE in href:
            slug = href.split(SF_SUPPORT_BASE, 1)[1]
            # Drop ?language=xx_XX and similar query params
            slug = re.sub(r"[?&]language=[^&\s]*", "", slug).strip("/")
            href = f"{self._article_prefix}/{slug}"

        if not text:
            text = href

        return f"[{text}]({href})"


# ---------------------------------------------------------------------------
# Image MDX helpers
# ---------------------------------------------------------------------------

def _is_inline_icon(width: str, height: str) -> bool:
    """
    Return True if either dimension indicates a small inline icon.
    Images with no dimension attributes default to screenshot treatment.
    """
    for val in (width, height):
        try:
            if int(val) <= INLINE_ICON_MAX_PX:
                return True
        except (ValueError, TypeError):
            pass
    return False


def _screenshot_mdx(alt: str, img_path: str) -> str:
    """Auto-sizing screenshot block using Mintlify's <Frame> component."""
    return f"<Frame>![{alt or 'Screenshot'}]({img_path})</Frame>"


def _inline_icon_mdx(alt: str, img_path: str, width: str, height: str) -> str:
    """Inline icon using raw <img> with Domo's standard inline style."""
    try:
        w = int(width)
    except (ValueError, TypeError):
        w = 20
    try:
        h = int(height)
    except (ValueError, TypeError):
        h = 20
    return (
        f'<img alt="{alt}" src="{img_path}" '
        f"style={{{{width: {w}, height: {h}, display: 'inline', "
        f"verticalAlign: 'start', margin: '0'}}}}/>"
    )


# ---------------------------------------------------------------------------
# Post-processing: image restoration
# ---------------------------------------------------------------------------

def _restore_images(
    text: str,
    image_registry: dict[str, dict[str, str]],
    image_local_map: dict[str, str],
) -> str:
    """
    Replace __DOMO_IMG_N__ placeholders with MDX image components.

    image_local_map maps Salesforce URL → local filename (e.g. '0EMVu000.jpg').
    Both raw (&) and HTML-encoded (&amp;) forms of the URL are tried.
    """
    for key, info in image_registry.items():
        src = info["src"]
        # Try both URL forms since BeautifulSoup decodes &amp; → & automatically
        local_name = image_local_map.get(src) or image_local_map.get(
            src.replace("&", "&amp;")
        )

        if local_name:
            img_path = f"/images/kb/{local_name}"
            if _is_inline_icon(info["width"], info["height"]):
                img_mdx = _inline_icon_mdx(
                    info["alt"], img_path, info["width"], info["height"]
                )
            else:
                img_mdx = _screenshot_mdx(info["alt"], img_path)
        else:
            # Image wasn't downloaded — leave a comment for manual follow-up
            img_mdx = f"\n<!-- TODO: embed image → {src} -->\n"

        text = text.replace(key, img_mdx)
    return text


# ---------------------------------------------------------------------------
# Post-processing: callout blocks
# ---------------------------------------------------------------------------

def _convert_callouts(text: str) -> str:
    """
    Convert bold-label callout paragraphs to MDX <Note>, <Warning>, <Tip> components.

    Matches patterns like:
        **Note:** Some information here.
        **Important:** Another note spanning
        multiple lines until a blank line.
    """

    def _replace(match: re.Match) -> str:
        raw_label = match.group(1)
        body = match.group(2).strip()
        component, display = CALLOUT_MAP.get(raw_label.lower(), ("Note", raw_label))
        return f"\n<{component}>**{display}:** {body}</{component}>\n"

    # Match **Label:** followed by the rest of the paragraph
    pattern = (
        r"\*\*(Note|Important|Warning|Caution|Tip):\*\*"  # bold label
        r"\s*"                                              # optional whitespace
        r"(.+?)"                                            # callout body (lazy)
        r"(?=\n\n|\n<|\Z)"                                  # until blank line, tag, or EOF
    )
    return re.sub(pattern, _replace, text, flags=re.IGNORECASE | re.DOTALL)


# ---------------------------------------------------------------------------
# Post-processing: FAQ → AccordionGroup
# ---------------------------------------------------------------------------

def _convert_faq(text: str) -> str:
    """
    Convert a FAQ section into Mintlify's <AccordionGroup>/<Accordion> components.

    Detects headings:  ## FAQ  |  ## FAQs  |  ## Frequently Asked Questions

    Handles two common Salesforce FAQ formats after markdownify conversion:

    Format A – standalone bold lines (most articles):
        **Question text here?**
        Answer paragraph here.

    Format B – numbered list items (connector articles):
        1. **Question text here?**
        Answer paragraph here.

        2. **Another question?**
        Another answer.

    Sections that don't match either pattern are left unchanged for manual review.
    """
    heading_re = re.compile(
        r"^(#{1,3})\s+(FAQ[s]?|Frequently Asked Questions)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    match = heading_re.search(text)
    if not match:
        return text

    faq_body_start = match.end()
    heading_level = len(match.group(1))

    # Find the start of the next section at the same or higher level
    next_section_re = re.compile(
        r"^#{1," + str(heading_level) + r"}\s+\S",
        re.MULTILINE,
    )
    next_match = next_section_re.search(text, faq_body_start + 1)
    faq_body_end = next_match.start() if next_match else len(text)
    faq_body = text[faq_body_start:faq_body_end]

    # --- Try Format B first: numbered list bold questions ---
    # Matches: "1. **Question?**\n\nAnswer..."
    numbered_qa_re = re.compile(
        r"\d+\.\s+\*\*(.+?)\*\*\s*\n+"     # N. **Question text**
        r"((?:(?!\d+\.\s+\*\*).)+?)"        # Answer (anything before next numbered item)
        r"(?=\s*\d+\.\s+\*\*|\s*\Z)",
        re.DOTALL,
    )
    qa_pairs = numbered_qa_re.findall(faq_body)

    # --- Try Format A: standalone bold-text questions ---
    if not qa_pairs:
        bold_qa_re = re.compile(
            r"\*\*(.+?)\*\*\s*\n+"             # **Question text**
            r"((?:(?!\*\*.+?\*\*).)+?)"        # Answer (anything before next bold block)
            r"(?=\s*\*\*|\s*\Z)",
            re.DOTALL,
        )
        qa_pairs = bold_qa_re.findall(faq_body)

    if not qa_pairs:
        # Can't detect Q&A structure — leave the section as-is for manual review
        return text

    # Build the AccordionGroup block
    parts = ["\n## FAQ\n\n<AccordionGroup>\n"]
    for question, answer in qa_pairs:
        q = question.strip()
        a = answer.strip()
        if q and a:
            safe_q = q.replace('"', "&quot;")
            parts.append(f'<Accordion title="{safe_q}">\n{a}\n</Accordion>\n')
    parts.append("\n</AccordionGroup>")

    accordion_block = "\n".join(parts)
    return text[: match.start()] + accordion_block + text[faq_body_end:]


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def html_to_mdx(
    html: str,
    title: str,
    image_local_map: dict[str, str],
    language: str = "en_US",
) -> str:
    """
    Convert a Salesforce Knowledge HTML body to a complete Domo MDX file.

    Args:
        html:             Raw HTML from the ARTICLE_BODY__C CSV column.
        title:            Article title (written into YAML frontmatter).
        image_local_map:  {salesforce_url: local_filename} mapping produced by
                          SalesforceImageDownloader.download_all().
        language:         CSV language code ("en_US", "ja", "de", "fr", "es").
                          Controls the article URL prefix used in internal links.

    Returns:
        Complete MDX string ready to write to the appropriate language directory.

    Notes:
        - Heading text is preserved from the source; manual review is needed to
          ensure imperative mood (e.g. "Connect X" not "Connecting X").
        - "click" → "select" substitution is not done automatically because the
          context varies; flag with TODO comments if needed.
        - FAQ detection works for the bold-Q/paragraph-A pattern. Unusual FAQ
          layouts are preserved verbatim for manual conversion.
    """
    article_prefix = LANG_ARTICLE_PREFIX.get(language, "/s/article")
    converter = _DomoMDXConverter(
        article_prefix=article_prefix,
        heading_style="ATX",        # Use ## syntax (not underline style)
        bullets="-",                # Unordered list marker
        strip=["script", "style"],  # Remove script/style tag content entirely
    )

    md = converter.convert(html)

    # Apply post-processing in dependency order
    md = _restore_images(md, converter._images, image_local_map)
    md = _convert_callouts(md)
    md = _convert_faq(md)

    # Normalise whitespace: collapse runs of 3+ blank lines to 2
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.strip()

    # Build complete MDX file with YAML frontmatter
    safe_title = title.replace('"', '\\"')
    return f'---\ntitle: "{safe_title}"\n---\n\n{md}\n'


# ---------------------------------------------------------------------------
# CLI entry point (for testing)
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Salesforce HTML file to Domo MDX (for testing)"
    )
    parser.add_argument("html_file", help="Path to input HTML file")
    parser.add_argument("--title", default="Untitled", help="Article title")
    parser.add_argument(
        "--language",
        default="en_US",
        choices=list(LANG_ARTICLE_PREFIX.keys()),
        help="Language code — controls internal link prefix (default: en_US)",
    )
    parser.add_argument(
        "--image-map",
        help="Path to JSON file mapping {salesforce_url: local_filename}",
    )
    parser.add_argument("--output", help="Output MDX file path (default: stdout)")
    args = parser.parse_args()

    with open(args.html_file, encoding="utf-8") as fh:
        html = fh.read()

    image_map: dict[str, str] = {}
    if args.image_map:
        with open(args.image_map, encoding="utf-8") as fh:
            image_map = json.load(fh)

    result = html_to_mdx(html, args.title, image_map, language=args.language)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(result)
        print(f"Written to {args.output}")
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
