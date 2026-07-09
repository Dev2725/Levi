#!/usr/bin/env python3
"""
Automatic bidirectional sync from Paperclip to GitHub.

This script mirrors Paperclip issues to GitHub. For each Paperclip issue:
- If no matching GitHub issue exists, create one.
- If a matching GitHub issue exists, update title/body/labels and state to
  reflect the Paperclip issue status.

Usage:
    export GITHUB_TOKEN=ghp_xxx
    python3 scripts/sync_paperclip_to_github.py
"""

import os
import re
import requests

# Configuration
PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
REPO = "Dev2725/Levi"
GITHUB_USER = "Dev2725"
OPEN_LABELS = ["paperclip", "auto-sync"]
DONE_LABELS = ["paperclip", "auto-sync", "done"]


def get_headers():
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def get_paperclip_issues():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    return r.json()


def get_github_issues():
    headers = get_headers()
    issues = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={page}",
            headers=headers,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        issues.extend(batch)
        page += 1
    return issues


def extract_identifier(title: str) -> str | None:
    match = re.match(r"^(DEV-\d+):?", title)
    return match.group(1) if match else None


def build_body(issue: dict) -> str:
    return (
        f"{issue.get('description') or 'No description'}\n\n"
        f"---\n"
        f"*Imported from Paperclip*\n"
        f"- **Status in Paperclip:** {issue.get('status')}\n"
        f"- **Original identifier:** {issue.get('identifier')}\n"
        f"- **Assigned to:** CTO agent"
    )


def create_github_issue(issue: dict) -> dict:
    headers = get_headers()
    labels = DONE_LABELS if issue.get("status") == "done" else OPEN_LABELS
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/issues",
        headers=headers,
        json={
            "title": f"{issue.get('identifier')}: {issue.get('title')}",
            "body": build_body(issue),
            "labels": labels,
        },
    )
    r.raise_for_status()
    return r.json()


def update_github_issue(gh_issue: dict, issue: dict) -> dict:
    headers = get_headers()
    labels = DONE_LABELS if issue.get("status") == "done" else OPEN_LABELS
    state = "closed" if issue.get("status") == "done" else "open"

    r = requests.patch(
        f"https://api.github.com/repos/{REPO}/issues/{gh_issue['number']}",
        headers=headers,
        json={
            "title": f"{issue.get('identifier')}: {issue.get('title')}",
            "body": build_body(issue),
            "labels": labels,
            "state": state,
        },
    )
    r.raise_for_status()
    return r.json()


def assign_and_comment(issue_number: int, created: bool) -> None:
    headers = get_headers()
    requests.patch(
        f"https://api.github.com/repos/{REPO}/issues/{issue_number}",
        headers=headers,
        json={"assignees": [GITHUB_USER]},
    ).raise_for_status()

    if created:
        requests.post(
            f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments",
            headers=headers,
            json={"body": "Assigned to CTO agent in Paperclip."},
        ).raise_for_status()


def sync() -> None:
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        return

    paperclip_issues = get_paperclip_issues()
    github_issues = get_github_issues()

    gh_by_identifier = {}
    for ghi in github_issues:
        identifier = extract_identifier(ghi.get("title", ""))
        if identifier:
            gh_by_identifier[identifier] = ghi

    created_count = 0
    updated_count = 0

    for issue in paperclip_issues:
        identifier = issue.get("identifier")
        if not identifier:
            continue

        gh_issue = gh_by_identifier.get(identifier)

        if not gh_issue:
            gh_issue = create_github_issue(issue)
            issue_number = gh_issue.get("number")
            assign_and_comment(issue_number, created=True)
            print(f"Created GitHub issue #{issue_number} for {identifier}")
            created_count += 1
        else:
            gh_issue = update_github_issue(gh_issue, issue)
            issue_number = gh_issue.get("number")
            print(f"Updated GitHub issue #{issue_number} for {identifier}")
            updated_count += 1

    print(f"\nSync complete: {created_count} created, {updated_count} updated.")


if __name__ == "__main__":
    sync()
