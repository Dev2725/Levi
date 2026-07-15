#!/usr/bin/env python3
"""
Auto-detect done issues in Paperclip and create GitHub PRs for them.

Usage:
    export GITHUB_TOKEN=ghp_xxx
    python3 scripts/auto_create_prs.py
"""

import os
import re
import subprocess
import sys

import requests

# Configuration
PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
REPO = "Dev2725/Levi"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_PR_SCRIPT = os.path.join(SCRIPT_DIR, "create_pr_from_issue.py")


def get_headers():
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def get_paperclip_issues():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    return r.json()


def get_github_prs():
    headers = get_headers()
    prs = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/pulls?state=all&per_page=100&page={page}",
            headers=headers,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        prs.extend(batch)
        page += 1
    return prs


def extract_identifier_from_pr(title: str) -> str | None:
    match = re.match(r"^(DEV-\d+):?", title)
    return match.group(1) if match else None


def main():
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    issues = get_paperclip_issues()
    prs = get_github_prs()

    done_issues = [i for i in issues if i.get("status") == "done"]
    existing_pr_identifiers = set()
    for pr in prs:
        ident = extract_identifier_from_pr(pr.get("title", ""))
        if ident:
            existing_pr_identifiers.add(ident)

    to_create = [i for i in done_issues if i.get("identifier") not in existing_pr_identifiers]

    if not to_create:
        print("No new done issues found.")
        return

    print(f"Found {len(to_create)} done issue(s) without PRs:")
    for issue in to_create:
        print(f"  {issue.get('identifier')}: {issue.get('title')}")

    created = []
    for issue in to_create:
        identifier = issue.get("identifier")
        print(f"\nCreating PR for {identifier}...")
        try:
            result = subprocess.run(
                [sys.executable, CREATE_PR_SCRIPT, identifier],
                capture_output=True,
                text=True,
                check=True,
            )
            print(result.stdout)
            # Extract PR URL from output
            match = re.search(r"https://github\.com/[^\s]+/pull/\d+", result.stdout)
            if match:
                created.append((identifier, match.group(0)))
        except subprocess.CalledProcessError as e:
            print(f"Error creating PR for {identifier}: {e.stderr}", file=sys.stderr)

    if created:
        print("\n=== Created PRs ===")
        for identifier, url in created:
            print(f"{identifier}: {url}")
    else:
        print("\nNo PRs were created.")


if __name__ == "__main__":
    main()
