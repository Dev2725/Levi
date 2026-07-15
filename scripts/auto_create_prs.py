#!/usr/bin/env python3
"""
Auto-detect done Paperclip issues and create GitHub PRs for them.

Usage:
    export GITHUB_TOKEN=ghp_xxx
    python3 scripts/auto_create_prs.py
"""

import os
import subprocess
import sys

import requests

PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
REPO = "Dev2725/Levi"


def get_headers():
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def get_done_issues():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    return [i for i in r.json() if i.get("status") == "done"]


def get_existing_pr_identifiers():
    """Return set of identifiers that already have PRs (open or closed)."""
    identifiers = set()
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/pulls?state=all&per_page=100&page={page}",
            headers=get_headers(),
        )
        r.raise_for_status()
        prs = r.json()
        if not prs:
            break
        for pr in prs:
            title = pr.get("title", "")
            if ":" in title:
                ident = title.split(":", 1)[0].strip()
                identifiers.add(ident)
        page += 1
    return identifiers


def main():
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    done_issues = get_done_issues()
    existing = get_existing_pr_identifiers()

    new_issues = [i for i in done_issues if i["identifier"] not in existing]

    if not new_issues:
        print("No new done issues found.")
        return

    print(f"Found {len(new_issues)} new done issue(s): {', '.join(i['identifier'] for i in new_issues)}")

    created = []
    for issue in new_issues:
        identifier = issue["identifier"]
        print(f"\nCreating PR for {identifier}...")
        result = subprocess.run(
            [sys.executable, "/home/gayathri_g/Levi/scripts/create_pr_from_issue.py", identifier],
            cwd="/home/gayathri_g/Levi",
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode == 0:
            created.append(identifier)
        else:
            print(f"Failed to create PR for {identifier}", file=sys.stderr)

    if created:
        print(f"\n✅ Created PRs for: {', '.join(created)}")
    else:
        print("\nNo PRs were created.")


if __name__ == "__main__":
    main()
