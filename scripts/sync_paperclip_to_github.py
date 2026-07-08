#!/usr/bin/env python3
"""
Automatic sync from Paperclip to GitHub.

This script finds Paperclip issues that are not yet mirrored in GitHub,
creates matching GitHub issues, and assigns them to the configured user.

Usage:
    export GITHUB_TOKEN=ghp_...
    python3 scripts/sync_paperclip_to_github.py
"""

import os
import requests

# Configuration
PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
REPO = "Dev2725/Levi"
GITHUB_USER = "Dev2725"
LABELS = ["paperclip", "auto-sync"]


def get_paperclip_issues():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    return r.json()


def get_github_issues():
    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


def create_github_issue(issue, headers):
    body = (
        f"{issue.get('description') or 'No description'}\n\n"
        f"---\n"
        f"*Imported from Paperclip*\n"
        f"- **Status in Paperclip:** {issue.get('status')}\n"
        f"- **Original identifier:** {issue.get('identifier')}\n"
        f"- **Assigned to:** CTO agent"
    )
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/issues",
        headers=headers,
        json={
            "title": f"{issue.get('identifier')}: {issue.get('title')}",
            "body": body,
            "labels": LABELS,
        },
    )
    r.raise_for_status()
    return r.json()


def assign_and_comment(issue_number, headers):
    requests.patch(
        f"https://api.github.com/repos/{REPO}/issues/{issue_number}",
        headers=headers,
        json={"assignees": [GITHUB_USER]},
    ).raise_for_status()

    requests.post(
        f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments",
        headers=headers,
        json={"body": "Assigned to CTO agent in Paperclip."},
    ).raise_for_status()


def sync():
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        return

    headers = {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }

    paperclip_issues = get_paperclip_issues()
    github_issues = get_github_issues()

    # Build a set of identifiers already synced to GitHub
    synced = set()
    for ghi in github_issues:
        title = ghi.get("title", "")
        if title.startswith("DEV-"):
            synced.add(title.split(":")[0])

    created = 0
    for issue in paperclip_issues:
        identifier = issue.get("identifier")
        if identifier in synced:
            print(f"Skipping {identifier} (already synced)")
            continue

        gh_issue = create_github_issue(issue, headers)
        issue_number = gh_issue.get("number")
        assign_and_comment(issue_number, headers)

        print(f"Created GitHub issue #{issue_number} for {identifier}")
        created += 1

    print(f"\nSync complete: {created} new GitHub issue(s) created.")


if __name__ == "__main__":
    sync()
