# Paperclip PR Workflow

This repository uses a semi-automatic workflow to generate GitHub Pull Requests from Paperclip issues.

## How it works

1. Create an issue in the **Paperclip Issue tracker** project.
2. Assign the issue to the **CTO** agent (configured as a Hermes agent).
3. Mark the issue as `done` when the work is complete.
4. Run the PR creation script:
   ```bash
   export GITHUB_TOKEN=***   python3 scripts/create_pr_from_issue.py DEV-XX
   ```
5. The script will:
   - Verify the issue belongs to the **Paperclip Issue tracker** project
   - Create a feature branch
   - Commit relevant changes
   - Push the branch to GitHub
   - Open a Pull Request

## Project scoping

Only issues assigned to the **Paperclip Issue tracker** project will be processed. If an issue is in a different project, the script will ask for confirmation before continuing.

## Configuration

Update the following constants in `scripts/create_pr_from_issue.py` if your setup changes:

- `PAPERCLIP_BASE` — local Paperclip API URL
- `COMPANY_ID` — your Paperclip company ID
- `PROJECT_ID` — the Paperclip Issue tracker project ID
- `REPO` — your GitHub repository (e.g., `Dev2725/Levi`)
- `GITHUB_USER` — your GitHub username

## Future improvements

- Convert this into a fully automatic webhook or cron job so PRs are created instantly when an issue is marked `done`.
- Add support for closing the linked Paperclip issue when the PR is merged.
