#!/usr/bin/env python3
"""
Poll Paperclip for done issues in the Paperclip Issue tracker project and
auto-create GitHub PRs for them using create_pr_from_issue.py.
"""

import base64
import os
import requests
import subprocess
import sys

PAPERCLIP_BASE = "http://127.0.0.1:3100"
COMPANY_ID = "1a4b9747-f550-4169-bb87-c6a1ccd8e616"
PROJECT_ID = "3ebbb7b3-5c58-4581-8de3-4cbbdf524471"
REPO = "Dev2725/Levi"
GITHUB_TOKEN_B64 = os.environ.get("GITHUB_TOKEN_B64", "")


def get_headers():
    return {
        "Authorization": f"token {base64.b64decode(GITHUB_TOKEN_B64).decode()}",
        "Accept": "application/vnd.github+json",
    }


def get_done_issues():
    r = requests.get(f"{PAPERCLIP_BASE}/api/companies/{COMPANY_ID}/issues")
    r.raise_for_status()
    issues = r.json()
    done = [i for i in issues if i.get("status") == "done" and i.get("projectId") == PROJECT_ID]
    return done


def existing_pr(identifier):
    # Check GitHub for PRs with this identifier in title
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/pulls?state=all",
        headers=get_headers(),
    )
    if r.status_code != 200:
        print(f"[auto-pr] Warning: GitHub API returned {r.status_code}")
        return None
    for pr in r.json():
        if pr.get("title", "").startswith(f"{identifier}:"):
            return pr
    return None


def main():
    print("[auto-pr] Checking Paperclip for done issues...")
    done_issues = get_done_issues()
    print(f"[auto-pr] Found {len(done_issues)} done issue(s) in project")

    for issue in done_issues:
        identifier = issue.get("identifier")
        if not identifier:
            continue

        if existing_pr(identifier):
            print(f"[auto-pr] {identifier}: PR already exists, skipping")
            continue

        print(f"[auto-pr] Creating PR for {identifier}...")
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = base64.b64decode(GITHUB_TOKEN_B64).decode()
        result = subprocess.run(
            ["python3", "/home/gayathri_g/Levi/scripts/create_pr_from_issue.py", identifier],
            cwd="/home/gayathri_g/Levi",
            env=env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)


if __name__ == "__main__":
    main()
