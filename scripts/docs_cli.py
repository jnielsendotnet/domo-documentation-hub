#!/usr/bin/env python3
"""
Domo Documentation Hub CLI

Extensible command-line tool for documentation management tasks.
New subcommands are added by creating a module in scripts/commands/
that exposes register(subparsers) and run(args) functions.

Usage:
    python scripts/docs_cli.py --help
    python scripts/docs_cli.py export --help
"""

import argparse
import sys

from commands import export_structure


def main():
    parser = argparse.ArgumentParser(
        description="Domo Documentation Hub CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register subcommands
    export_structure.register(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to the subcommand's run function
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
