#!/usr/bin/env python3
"""
Create a GitHub Pull Request from a Paperclip issue.

Usage:
    export GITHUB_TOKEN=***    python3 scripts/create_pr_from_issue.py DEV-23

The script:
1. Reads the Paperclip issue
2. Verifies the issue belongs to the 'Paperclip Issue tracker' project
3. Creates a feature branch named feature/<identifier>
4. Commits relevant files (scripts and docs)
5. Pushes the branch to GitHub
6. Opens a PR with the issue title/body
7. Adds a comment linking back to Paperclip
"""

import os
import re
import subprocess
import sys

import requests

# Configuration
PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
PROJECT_ID = "3ebbb7b3-5c58-4581-8de3-4cbbdf524471"  # Paperclip Issue tracker
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


def get_project_name():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/projects/{PROJECT_ID}")
    if r.status_code == 200:
        return r.json().get("name", "Unknown")
    return "Unknown"


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
    project_name = get_project_name()

    # Verify project belongs to Paperclip Issue tracker
    print(f"Project validation: expecting '{project_name}' (id={PROJECT_ID})")
    if issue.get("projectId") != PROJECT_ID:
        print(f"Warning: {identifier} is not in project '{project_name}'.")
        print(f"Current projectId: {issue.get('projectId')}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)
    else:
        print(f"✅ {identifier} is correctly assigned to project '{project_name}'.")

    ensure_git_config(repo_path)

    # Make sure we're on master with latest
    run("git checkout master", cwd=repo_path)
    run("git pull origin master", cwd=repo_path)

    # Create feature branch
    run(f"git checkout -b {branch}", cwd=repo_path)

    # Stage and commit relevant files (avoid extra files)
    files_to_stage = ["scripts/create_pr_from_issue.py", "doc/PAPERCLIP_PR_WORKFLOW.md"]
    for f in files_to_stage:
        if os.path.exists(os.path.join(repo_path, f)):
            run(f"git add {f}", cwd=repo_path)
    try:
        title = issue.get('title', '').replace("'", '"')
        description = (issue.get('description') or 'No description').replace("'", '"')
        run(
            f"git commit -m 'feat({identifier}): {title}' -m '{description}'",
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
                f"- **Project:** {project_name}\n"
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
        json={"body": f"This PR was created from Paperclip issue {identifier} in project '{project_name}'."},
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
