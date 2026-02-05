#!/usr/bin/env python3
"""
Create individual pull requests for each synced YAML file.

This script:
1. Reads the list of changed YAML files
2. For each file:
   - Checks if an open PR already exists (skip if so)
   - Creates a new branch
   - Copies the YAML to destination
   - Commits the changes
   - Creates a PR
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class PRCreator:
    """Handles creation of individual PRs for YAML files"""

    def __init__(
        self,
        changed_files_list: str,
        source_dir: str,
        dest_dir: str,
        base_branch: str = "main",
        pr_branch_prefix: str = "openapi-sync",
        repo: str = None
    ):
        self.changed_files_list = changed_files_list
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.base_branch = base_branch
        self.pr_branch_prefix = pr_branch_prefix
        self.repo = repo

        self.processed = 0
        self.failed = 0
        self.skipped = 0

    def run_command(self, cmd: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command"""
        try:
            return subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr if e.stderr else e.stdout}")
            raise

    def git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command"""
        return self.run_command(["git"] + args, check=check)

    def gh_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a gh (GitHub CLI) command"""
        return self.run_command(["gh"] + args, check=check)

    def check_pr_exists(self, branch_name: str) -> Optional[int]:
        """Check if an open PR exists for the given branch"""
        try:
            result = self.gh_command([
                "pr", "list",
                "--state", "open",
                "--head", branch_name,
                "--json", "number",
                "--jq", ".[0].number"
            ], check=False)

            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip())
            return None
        except (ValueError, subprocess.CalledProcessError):
            return None

    def create_or_checkout_branch(self, branch_name: str) -> bool:
        """Create or checkout a branch"""
        try:
            self.git_command(["fetch", "origin"], check=False)
            self.git_command(["checkout", "-f", self.base_branch], check=False)

            local_branches = self.git_command(["branch", "--list", branch_name], check=False)
            branch_exists_locally = branch_name in local_branches.stdout

            result = self.git_command(["ls-remote", "--heads", "origin", branch_name], check=False)
            branch_exists_remotely = bool(result.stdout.strip())

            if branch_exists_remotely:
                if branch_exists_locally:
                    self.git_command(["branch", "-D", branch_name], check=False)
                self.git_command(["checkout", "-f", "-b", branch_name, f"origin/{branch_name}"])
            else:
                self.git_command(["checkout", "-b", branch_name])

            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create/checkout branch: {e}")
            return False

    def sync_file(self, yaml_file: str) -> Optional[str]:
        """Copy YAML file to destination"""
        try:
            yaml_filename = os.path.basename(yaml_file)
            dest_path = os.path.join(self.dest_dir, yaml_filename)

            if not os.path.exists(yaml_file):
                print(f"Source file not found: {yaml_file}")
                return None

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(yaml_file, dest_path)
            print(f"Synced: {yaml_file} -> {dest_path}")

            return dest_path
        except Exception as e:
            print(f"Sync failed: {e}")
            return None

    def stage_and_commit(self, yaml_file: str, file_name: str, dest_path: str) -> bool:
        """Stage changes and commit"""
        try:
            self.git_command(["add", dest_path])

            result = self.git_command(["diff", "--cached", "--name-only"], check=False)
            if not result.stdout.strip():
                print(f"No changes to commit for {file_name}")
                return False

            self.git_command(["config", "user.name", "github-actions[bot]"])
            self.git_command(["config", "user.email", "github-actions[bot]@users.noreply.github.com"])

            self.git_command([
                "commit",
                "-m", f"docs: Update OpenAPI spec {file_name}",
                "-m", f"Synced from source repository",
                "-m", f"Destination: {dest_path}"
            ])

            return True
        except subprocess.CalledProcessError as e:
            print(f"Commit failed: {e}")
            return False

    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote"""
        try:
            self.git_command(["push", "-f", "origin", branch_name])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Push failed: {e}")
            return False

    def create_pr(self, branch_name: str, file_name: str, dest_path: str) -> Optional[str]:
        """Create a pull request"""
        try:
            pr_body = f"""## OpenAPI Specification Update

This PR syncs an updated OpenAPI specification from the source repository.

### File Details
- **File:** `{file_name}`
- **Destination:** `{dest_path}`

### Changes
- Updated OpenAPI YAML specification
- Navigation will be updated automatically via TOC generator

---
This PR was created automatically by the OpenAPI sync workflow.
"""

            cmd = [
                "pr", "create",
                "--title", f"docs: Update OpenAPI spec {file_name}",
                "--body", pr_body,
                "--head", branch_name,
                "--base", self.base_branch
            ]

            if self.repo:
                cmd.extend(["--repo", self.repo])

            result = self.gh_command(cmd, check=False)

            if result.returncode == 0 and result.stdout.strip().startswith("https://"):
                return result.stdout.strip()
            else:
                print(f"PR creation failed: {result.stderr if result.stderr else result.stdout}")
                return None
        except subprocess.CalledProcessError as e:
            print(f"PR creation failed: {e}")
            return None

    def return_to_base_branch(self):
        """Return to base branch"""
        try:
            self.git_command(["checkout", self.base_branch], check=False)
        except subprocess.CalledProcessError:
            pass

    def process_file(self, yaml_file: str) -> bool:
        """Process a single file"""
        file_name = os.path.basename(yaml_file)
        file_base = Path(file_name).stem
        branch_name = f"{self.pr_branch_prefix}/{file_base}"

        print("---")
        print(f"Processing: {file_name}")
        print(f"Branch: {branch_name}")

        pr_number = self.check_pr_exists(branch_name)
        if pr_number:
            print(f"Skipping - PR #{pr_number} already exists")
            self.skipped += 1
            return True

        if not self.create_or_checkout_branch(branch_name):
            self.failed += 1
            self.return_to_base_branch()
            return False

        dest_path = self.sync_file(yaml_file)
        if not dest_path:
            self.failed += 1
            self.return_to_base_branch()
            return False

        if not self.stage_and_commit(yaml_file, file_name, dest_path):
            self.return_to_base_branch()
            return True

        if not self.push_branch(branch_name):
            self.failed += 1
            self.return_to_base_branch()
            return False

        pr_url = self.create_pr(branch_name, file_name, dest_path)
        if pr_url:
            print(f"Created PR: {pr_url}")
            self.processed += 1
        else:
            self.failed += 1

        self.return_to_base_branch()
        return pr_url is not None

    def process_all_files(self) -> Dict[str, int]:
        """Process all files in the changed files list"""
        print("Creating individual PRs for YAML files...")

        if not os.path.exists(self.changed_files_list):
            print(f"Changed files list not found: {self.changed_files_list}")
            sys.exit(1)

        with open(self.changed_files_list, 'r') as f:
            files = [line.strip() for line in f if line.strip()]

        if not files:
            print("No files to process")
            return {"processed": 0, "failed": 0, "skipped": 0, "total": 0}

        for yaml_file in files:
            self.process_file(yaml_file)

        print("")
        print(f"Summary:")
        print(f"  Total: {len(files)}")
        print(f"  Processed: {self.processed}")
        print(f"  Skipped: {self.skipped}")
        print(f"  Failed: {self.failed}")

        return {
            "processed": self.processed,
            "failed": self.failed,
            "skipped": self.skipped,
            "total": len(files)
        }


def main():
    parser = argparse.ArgumentParser(description='Create individual PRs for YAML files')
    parser.add_argument('--changed-list', required=True, help='File containing list of changed YAML files')
    parser.add_argument('--source-dir', required=True, help='Source directory with YAML files')
    parser.add_argument('--dest-dir', required=True, help='Destination directory for YAML files')
    parser.add_argument('--base-branch', default='main', help='Base branch (default: main)')
    parser.add_argument('--pr-branch-prefix', default='openapi-sync', help='Branch prefix (default: openapi-sync)')
    parser.add_argument('--repo', default=None, help='GitHub repository (owner/repo)')

    args = parser.parse_args()

    creator = PRCreator(
        changed_files_list=args.changed_list,
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        base_branch=args.base_branch,
        pr_branch_prefix=args.pr_branch_prefix,
        repo=args.repo
    )

    results = creator.process_all_files()

    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
