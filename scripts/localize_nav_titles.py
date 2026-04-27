#!/usr/bin/env python3
"""
Localize tab, group, and sub-group titles in docs.json for each non-English language section.

Translations are applied only to strings present in the TRANSLATIONS map;
untranslated strings (e.g., product names, year labels) are left as-is.

Usage:
    python3 scripts/localize_nav_titles.py [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path

DOCS_JSON = Path(__file__).parent.parent / "docs.json"

# fmt: off
TRANSLATIONS: dict[str, dict[str, str]] = {
    "fr": {
        "Release Notes":                   "Notes de version",
        "Knowledge Base":                  "Base de connaissances",
        "Archived Feature Release Notes":  "Notes de version des fonctionnalités archivées",
    },
    "de": {
        "Release Notes":                   "Versionshinweise",
        "Knowledge Base":                  "Wissensdatenbank",
        "Archived Feature Release Notes":  "Archivierte Versionshinweise zu Funktionen",
    },
    "es": {
        "Release Notes":                   "Notas de la versión",
        "Knowledge Base":                  "Base de conocimientos",
        "Archived Feature Release Notes":  "Notas de la versión de funciones archivadas",
    },
}
# fmt: on


def translate_node(node: object, lang_map: dict[str, str]) -> object:
    """Recursively translate 'tab' and 'group' title strings in a nav node."""
    if isinstance(node, dict):
        return {
            key: (
                lang_map.get(value, value)
                if key in ("tab", "group") and isinstance(value, str)
                else translate_node(value, lang_map)
            )
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [translate_node(item, lang_map) for item in node]
    return node


def collect_changes(
    node: object, lang_map: dict[str, str], path: str = ""
) -> list[tuple[str, str, str]]:
    """Return list of (path, old_title, new_title) for all titles that would change."""
    changes = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("tab", "group") and isinstance(value, str):
                translated = lang_map.get(value, value)
                if translated != value:
                    changes.append((f"{path}.{key}", value, translated))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    changes.extend(
                        collect_changes(item, lang_map, f"{path}.{key}[{i}]")
                    )
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changes without writing to docs.json",
    )
    args = parser.parse_args()

    with DOCS_JSON.open(encoding="utf-8") as f:
        data = json.load(f)

    languages: list[dict] = data["navigation"]["languages"]
    total_changes = 0

    for lang in languages:
        lang_code = lang["language"]
        lang_map = TRANSLATIONS.get(lang_code)
        if not lang_map:
            continue

        tabs = lang.get("tabs", [])
        changes = []
        for i, tab in enumerate(tabs):
            changes.extend(collect_changes(tab, lang_map, f"[{lang_code}].tabs[{i}]"))

        if changes:
            print(f"\n{lang_code}:")
            for path, old, new in changes:
                print(f"  {old!r:45s} → {new!r}")
            total_changes += len(changes)

        if not args.dry_run:
            lang["tabs"] = [translate_node(tab, lang_map) for tab in tabs]

    if total_changes == 0:
        print("Nothing to translate — all titles already localized.")
        return

    if args.dry_run:
        print(f"\nDry run: {total_changes} title(s) would be updated. "
              "Re-run without --dry-run to apply.")
        return

    with DOCS_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nApplied {total_changes} translation(s) to docs.json.")


if __name__ == "__main__":
    main()
