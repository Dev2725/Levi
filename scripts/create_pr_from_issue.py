#!/usr/bin/env python3
"""
Create a GitHub Pull Request from a Paperclip issue.

Usage:
    export GITHUB_TOKEN=ghp_xxx
    python3 scripts/create_pr_from_issue.py DEV-21

The script:
1. Reads the Paperclip issue
2. Creates a feature branch named feature/<identifier>
3. Commits any current repo changes
4. Pushes the branch to GitHub
5. Opens a PR with the issue title/body
6. Adds a comment linking back to Paperclip
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
GITHUB_USER = "Dev2725"
GIT_USER_NAME = "CTO Agent"
GIT_USER_EMAIL = "cto@devcorp.local"


def run(cmd, check=True, cwd=None):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result


def get_headers():
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def get_paperclip_issue(identifier: str):
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    for issue in r.json():
        if issue.get("identifier") == identifier:
            return issue
    raise ValueError(f"Issue {identifier} not found in Paperclip")


def clean_branch_name(identifier: str, title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", title.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"feature/{identifier}-{slug[:40]}"


def ensure_git_config(repo_path: str):
    try:
        run(f"git config user.name '{GIT_USER_NAME}'", cwd=repo_path)
        run(f"git config user.email '{GIT_USER_EMAIL}'", cwd=repo_path)
    except subprocess.CalledProcessError:
        pass


def create_pr(identifier: str):
    if "GITHUB_TOKEN" not in os.environ:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    issue = get_paperclip_issue(identifier)
    repo_path = "/home/gayathri_g/Levi"
    branch = clean_branch_name(identifier, issue.get("title"))

    ensure_git_config(repo_path)

    # Make sure we're on master with latest
    run("git checkout master", cwd=repo_path)
    run("git pull origin master", cwd=repo_path)

    # Create feature branch
    run(f"git checkout -b {branch}", cwd=repo_path)

    # Stage and commit any changes
    run("git add -A", cwd=repo_path)
    try:
        run(
            f"git commit -m 'feat({identifier}): {issue.get('title')}' -m '{issue.get('description') or 'No description'}'",
            cwd=repo_path,
        )
    except subprocess.CalledProcessError:
        print("No changes to commit, continuing...")

    # Push branch
    run(f"git push origin {branch}", cwd=repo_path)

    # Create PR
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/pulls",
        headers=get_headers(),
        json={
            "title": f"{identifier}: {issue.get('title')}",
            "head": branch,
            "base": "master",
            "body": (
                f"{issue.get('description') or 'No description'}\n\n"
                f"---\n"
                f"*Closes {identifier}*\n"
                f"- **Paperclip status:** {issue.get('status')}\n"
                f"- **Created by:** CTO agent via Paperclip"
            ),
        },
    )
    r.raise_for_status()
    pr = r.json()

    # Add comment
    requests.post(
        f"https://api.github.com/repos/{REPO}/issues/{pr['number']}/comments",
        headers=get_headers(),
        json={"body": f"This PR was created from Paperclip issue {identifier}."},
    )

    # Assign PR
    requests.patch(
        f"https://api.github.com/repos/{REPO}/issues/{pr['number']}",
        headers=get_headers(),
        json={"assignees": [GITHUB_USER]},
    )

    print(f"\n✅ Created PR #{pr['number']}: {pr.get('html_url')}")
    return pr


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <issue-identifier>")
        sys.exit(1)
    create_pr(sys.argv[1])
