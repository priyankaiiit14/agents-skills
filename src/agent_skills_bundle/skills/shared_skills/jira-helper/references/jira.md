# Jira Cloud Reference

## Access

Use the below Jira access path available in the runtime:

- Existing Jira MCP/API tool, preferred when present.
- If the Atlassian MCP server is configured but not authenticated, log in using the command for your agent runtime:
  - Claude Code: `claude mcp login atlassian`
  - Codex: `codex mcp login atlassian`
  - Other agents: use your agent's MCP login command.
  After logging in, complete the browser flow and restart your agent so the MCP tools are loaded.
Never print tokens. Never write credentials into the skill.

## API Endpoints

- Create issue: `POST /rest/api/3/issue`
- Search issues with JQL: `POST /rest/api/3/search/jql`
- Get issue: `GET /rest/api/3/issue/{issueIdOrKey}`
- Get create metadata: use Jira create metadata when available before creating issues with custom required fields.
- Transition issue: `POST /rest/api/3/issue/{issueIdOrKey}/transitions`
- Add comment: `POST /rest/api/3/issue/{issueIdOrKey}/comment`

Use Markdown as the source format for descriptions and comments whenever an MCP tool accepts `contentFormat: "markdown"`. Keep structured fields such as project, issue type, priority, labels, components, and parent/epic outside the Markdown body.

For direct Jira REST API calls, description and other multiline rich-text fields usually require Atlassian Document Format (ADF). Convert the Markdown body to the equivalent ADF shape before sending it.

Build the correct ADF shape depending on content:

Plain paragraph:
```json
{
  "type": "doc", "version": 1,
  "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "Plain text description" }] }
  ]
}
```

Bullet list (use for acceptance criteria, steps, etc.):
```json
{
  "type": "doc", "version": 1,
  "content": [
    {
      "type": "bulletList",
      "content": [
        { "type": "listItem", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Item one" }] }] },
        { "type": "listItem", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Item two" }] }] }
      ]
    }
  ]
}
```

Mixed paragraph + bullet list:
```json
{
  "type": "doc", "version": 1,
  "content": [
    { "type": "paragraph", "content": [{ "type": "text", "text": "Context sentence." }] },
    {
      "type": "bulletList",
      "content": [
        { "type": "listItem", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Criterion one" }] }] }
      ]
    }
  ]
}
```

When the description contains only plain text with no lists or headings, a single paragraph node is sufficient.

## Common JQL

My open tickets:

```jql
assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC
```

Open tickets assigned to a user:

```jql
assignee = "Display Name" AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Open tickets in projects:

```jql
project in (ABC, XYZ) AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Tickets in an epic, newer Jira parent model:

```jql
parent = ABC-123 AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Tickets in an epic, older Jira Software field:

```jql
"Epic Link" = ABC-123 AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Tickets on hold (stalled/waiting):

```jql
project = ABC AND status = "On Hold" ORDER BY updated ASC
```

To see why a ticket is on hold, fetch the issue and read its most recent comment:
`GET /rest/api/3/issue/{issueKey}/comment?orderBy=-created&maxResults=3`

Component work:

```jql
project = ABC AND component = "Backend" AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

Overdue tickets:

```jql
project = ABC AND due < now() AND statusCategory != Done ORDER BY due ASC
```

Open tickets in current sprint (scrum projects only):

```jql
project = ABC AND sprint in openSprints() AND statusCategory != Done ORDER BY priority DESC, updated DESC
```

My tickets in current sprint:

```jql
assignee = currentUser() AND sprint in openSprints() AND statusCategory != Done ORDER BY priority DESC
```

Recently stale tickets:

```jql
project = ABC AND statusCategory != Done AND updated <= -7d ORDER BY updated ASC
```

Created by current user:

```jql
reporter = currentUser() AND statusCategory != Done ORDER BY updated DESC
```

## Ticket Templates

Bug:

```markdown
## Context

Describe the bug, affected user or workflow, and observed impact.

## Environment

- Environment:
- Browser / client:
- Version / commit:

## Steps To Reproduce

1. First step.
2. Second step.
3. Third step.

## Expected Result

Describe what should happen.

## Actual Result

Describe what happens instead.

## Impact

- User or system impact.
- Frequency or severity, if known.

## Acceptance Criteria

- Reproduction steps are documented.
- Fix is verified in the affected environment.
- Regression coverage is added or existing coverage is updated.
```

Story:

```markdown
## User Story

As a user type, I want an action, so that a benefit is achieved.

## Context

Explain the requirement, customer problem, or business reason.

## Scope

- In scope item.
- Out of scope item, if useful.

## Acceptance Criteria

- Given a context, when an action happens, then an expected result occurs.
- Given another context, when another action happens, then another expected result occurs.

## Technical Notes

- Implementation detail, constraint, or affected system.

## Dependencies

- Blocks: None
- Blocked by: None
```

Task:

```markdown
## Context

Explain why this task is needed.

## Work Required

- Work item.
- Work item.

## Definition Of Done

- Required outcome.
- Validation or test result.

## Dependencies

- Blocks: None
- Blocked by: None
```

Spike:

```markdown
## Goal

Question or decision this spike must answer.

## Context

Relevant background and constraints.

## Time Box

- Target time box:

## Output

- Expected deliverable, doc, decision, or follow-up ticket.

## Definition Of Done

- Question is answered with evidence.
- Findings are documented with a link, comment, or follow-up ticket.
- Recommended next step is clear.
```

Manager summary format:

```markdown
Total open:
Blocked:
Overdue:
Unassigned:
By assignee:
By status:
Top risks:
```

## Result Fields

Prefer requesting these fields for summaries:

```text
key, summary, status, assignee, reporter, priority, duedate, components, labels, parent, updated
```
