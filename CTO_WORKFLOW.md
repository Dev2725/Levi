# CTO Agent Workflow

This document explains how the **CTO (Chief Technology Officer) agent** assigns work to other agents in the Paperclip system.

## Overview

The CTO agent is the senior technical leader in the Paperclip/Levi project. It is responsible for:

- Reviewing technical work
- Creating and assigning issues to other agents
- Delegating tasks based on agent capabilities
- Tracking progress and ensuring completion

## How the CTO Agent Works

### 1. Creating Issues

The CTO agent can create new issues in Paperclip through the API or user interface. Each issue includes:

- A clear title
- A description of the work
- A status (e.g., `todo`, `in_progress`, `done`)
- An assignee agent

### 2. Assigning Issues to Other Agents

To assign an issue to another agent, the CTO agent updates the issue's `assigneeAgentId` field. For example:

```http
PATCH /api/issues/{issue_id}
{
  "assigneeAgentId": "agent-uuid-here"
}
```

The CTO should choose agents based on:

- Their role (e.g., engineer, designer, tester)
- Their current status (`idle` is preferred)
- Their capabilities

### 3. Agents Receiving Tasks

Once an issue is assigned, the agent:

- Receives the task in its queue
- Updates the issue status to `in_progress`
- Performs the work
- Updates the issue status to `done` when complete

### 4. Tracking Progress

The CTO agent can monitor progress by:

- Checking issue statuses
- Reading agent activity logs
- Reviewing completed work
- Reassigning blocked issues to other agents

### 5. Delegation Examples

| Task Type | Delegate To | Reason |
|-----------|-------------|--------|
| Code changes | Software engineer agent | Has coding capabilities |
| UI design | Designer agent | Has design skills |
| Testing | QA agent | Has testing capabilities |
| Documentation | Technical writer agent | Has writing skills |

## Sync with GitHub

Issues created in Paperclip can also be mirrored in GitHub for visibility:

| Platform | Assignee | Status |
|----------|----------|--------|
| Paperclip | CTO / other agents | `todo`, `in_progress`, `done` |
| GitHub | Dev2725 (human user) | `open`, `closed` |

## Best Practices

1. **Keep agents idle before assignment** — check agent status first.
2. **Use clear titles and descriptions** — helps agents understand the task.
3. **Set realistic statuses** — don't mark `done` until work is verified.
4. **Reassign blocked issues** — don't let tasks get stuck.
5. **Document decisions** — add comments to issues when needed.

## Related

- Paperclip UI: http://127.0.0.1:3100
- GitHub Issues: https://github.com/Dev2725/Levi/issues
