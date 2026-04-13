#!/usr/bin/env python3
"""
Batch-runs the cleanup-localized-article Claude skill for all modified
es/ and fr/ KB articles, using their German (de/) counterparts as templates.

Reads the list of modified files from git (both staged and unstaged vs HEAD),
finds each file's de/ counterpart, and runs:
    claude -p "cleanup-localized-article template: de/... target: es/..."

Files with no de/ counterpart are skipped and reported.

Usage:
    python3 cleanup_localized_batch.py             # process all
    python3 cleanup_localized_batch.py --dry-run   # preview only, no edits
    python3 cleanup_localized_batch.py --locale es # restrict to one locale
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SUPPORTED_LOCALES = ("es", "fr")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_modified_articles(locales: tuple[str, ...]) -> list[str]:
    """Return sorted list of modified es/fr article paths relative to repo root."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=REPO_ROOT, check=True,
    )
    paths = []
    for line in result.stdout.splitlines():
        line = line.strip()
        parts = line.split("/")
        if (
            len(parts) >= 4
            and parts[0] in locales
            and parts[1] == "s"
            and parts[2] == "article"
            and line.endswith(".mdx")
        ):
            paths.append(line)
    return sorted(set(paths))


def get_de_counterpart(filepath: str) -> str | None:
    """Return the de/ counterpart path if it exists on disk, else None."""
    parts = filepath.split("/")
    parts[0] = "de"
    de_path = "/".join(parts)
    return de_path if (REPO_ROOT / de_path).exists() else None


# ---------------------------------------------------------------------------
# Skill runner
# ---------------------------------------------------------------------------

def run_cleanup(template_path: str, target_path: str, dry_run: bool) -> int:
    """
    Invoke the cleanup-localized-article skill via the Claude Code CLI.
    Returns the subprocess exit code (0 = success).
    """
    prompt = (
        "Use the cleanup-localized-article skill. "
        "The paths are already confirmed — skip the confirmation question "
        "and proceed directly to cleanup. "
        f"Template: {template_path}, target: {target_path}"
    )

    if dry_run:
        print(f"    [DRY RUN] claude -p \"{prompt[:100]}...\"")
        return 0

    result = subprocess.run(
        ["claude", "--dangerously-skip-permissions", "-p", prompt],
        cwd=REPO_ROOT,
    )
    return result.returncode


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch-clean localized KB articles using the cleanup-localized-article skill."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without invoking Claude.",
    )
    parser.add_argument(
        "--locale",
        choices=SUPPORTED_LOCALES,
        default=None,
        help="Restrict to a single locale (default: all supported locales).",
    )
    args = parser.parse_args()

    locales = (args.locale,) if args.locale else SUPPORTED_LOCALES
    articles = get_modified_articles(locales)

    if not articles:
        print("No modified es/ or fr/ articles found in the working tree.")
        return 0

    # Pre-flight: resolve counterparts and print plan
    plan: list[tuple[str, str | None]] = [
        (article, get_de_counterpart(article)) for article in articles
    ]

    print(f"Found {len(articles)} modified article(s):\n")
    for article, de_path in plan:
        marker = f"  template → {de_path}" if de_path else "  [SKIP — no de/ counterpart found]"
        print(f"  {article}")
        print(marker)
    print()

    if args.dry_run:
        print("Dry-run mode: no files will be changed.\n")

    # Process
    counts = {"done": 0, "skipped": 0, "failed": 0}
    failed_files: list[str] = []

    for article, de_path in plan:
        if de_path is None:
            print(f"[SKIP]  {article}")
            counts["skipped"] += 1
            continue

        print(f"[START] {article}")
        rc = run_cleanup(de_path, article, dry_run=args.dry_run)

        if rc == 0:
            print(f"[DONE]  {article}\n")
            counts["done"] += 1
        else:
            print(f"[FAIL]  {article} — exit code {rc}\n")
            counts["failed"] += 1
            failed_files.append(article)

    # Summary
    print("─" * 50)
    print("Summary")
    print(f"  Processed : {counts['done']}")
    print(f"  Skipped   : {counts['skipped']}")
    print(f"  Failed    : {counts['failed']}")
    if failed_files:
        print("\nFailed:")
        for f in failed_files:
            print(f"  {f}")

    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
