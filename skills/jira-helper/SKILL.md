---
name: jira-helper
description: Create, draft, query, and summarize Jira Cloud tickets from conversations, notes, or user-provided files. Use when the user asks to create Jira issues, prepare Jira ticket drafts, parse a file into Jira tickets, route tickets to configured projects/epics, find open Jira work, query tickets by epic/project/assignee/reporter/component/label/status/priority/due date, summarize blockers or overdue tasks, or produce JQL for Jira tracking questions.
---

# Jira Helper

## Overview

Help users create and query Jira Cloud tickets without building a separate app. Keep workflows simple, explicit, and permission-aware.

Use the Jira details and reusable JQL patterns in `references/jira.md` when handling Jira API calls, JQL construction, ticket templates, or field mapping.

Use `references/project-routing.md` when the user wants configurable project, component, or epic routing, or when a team-provided config file is available.

## Jira Markdown Formatting

Use Markdown as the canonical format for Jira descriptions and comments. Keep Jira fields such as project, issue type, priority, assignee, components, labels, parent/epic, sprint, and story points as structured fields outside the description body.

When a Jira MCP tool accepts `contentFormat`, send description and comment bodies with `contentFormat: "markdown"`. When using Jira REST APIs directly, convert the same Markdown body to Atlassian Document Format (ADF) before sending it.

For Jira-rendered Markdown:

- Use `##` and `###` headings for sections.
- Use blank lines between headings, paragraphs, and lists.
- Use `-` bullets for unordered lists.
- Use `1.` numbered lists for ordered steps.
- Use `- [ ]` only when checkbox rendering is desired; otherwise use normal bullets.
- Use fenced code blocks for logs, JSON, stack traces, commands, or payloads.
- Do not use field-label lines like `Description:` or `Acceptance criteria:` inside the Jira body. Use headings such as `## Description` and `## Acceptance Criteria`.
- Do not include unresolved placeholders in the final Jira body. Use `Needs user input` only in drafts shown to the user.

## Operating Rules

- Do not create, transition, assign, comment on, or otherwise mutate Jira issues without explicit user approval.
- For ticket creation, always prepare a human-readable draft first and ask for confirmation before making the Jira API call.
- Before every create call, show all details that will be sent to Jira: project, issue type, summary, description, acceptance criteria, priority, assignee, component/s, labels, parent/epic, due date, links, and any custom fields.
- Treat confirmations such as "ok", "looks good", "confirm", "approved", or "create it" as approval only after the complete draft has been shown in the current conversation.
- Never create a ticket inside an epic/parent based only on a guess. If the epic/parent is inferred from routing config, show the matched rule and require explicit confirmation. If confidence is not high, ask the user to choose or provide the epic/parent before creating.
- For broad tracking queries that may scan team/project work, show the JQL before executing it.
- Prefer bounded JQL with project, assignee, reporter, epic, component, label, due date, or status constraints.
- For ticket creation, prefer Component/s over labels unless the user explicitly asks for labels or the Jira project requires labels.
- Do not invent required Jira fields. Ask for missing project, issue type, summary, description, priority, assignee, component/s, epic/parent, due date, acceptance criteria, or any Jira-required custom fields.
- Before creating a ticket, run a quick duplicate check: search for open tickets with similar keywords in the same project and show any close matches to the user. Skip this step only if the user explicitly says to proceed without checking.
- If the user gives rough notes, infer a reasonable draft from the notes and ask only the smallest set of missing questions needed to create the ticket safely. Correct spelling and grammar, clarify vague phrasing, add reasonable context from the routing/project/epic metadata, and preserve the user's intended scope.
- Add `###### created by agent` as the final line of every Jira description created by the agent. Do not use `# created by agent`, because it renders too large in Jira.
- Treat dependencies as Jira relationships, not description text. Use Jira linked work items for `blocks` and `blocked_by`; use Jira parent/subtask behavior for parent-child relationships when applicable. Do not add a "Dependencies: None" section to the Jira description.
- Show routing and duplicate-check details in the draft/review message before creation, but do not include routing or duplicate-check audit text in the Jira description.
- Include a `## Links` section in the Jira description only when actual supporting links are provided. Do not write `Links: None`.
- Render supporting links as named Markdown links, for example `- [Design doc](https://...)`, not as raw pasted URLs. When intake provides only a URL, infer a short useful title from the ticket context or ask for one if unclear.
- Do not store credentials in the skill. Use environment variables, an existing Jira MCP/API tool, or credentials already configured in the runtime.
- Respect Jira permissions. If Jira returns missing/forbidden results, explain that access is controlled by the authenticated user's Jira permissions.
- After creating or updating Jira issues, return concise results with the Jira key, direct browse link, status, assignee, priority, due date, and a short summary unless the user asks for more detail. The link should take the user directly to the issue in Jira.

## Ticket Creation

When the user asks to create a ticket:

1. Extract known fields from the request.
2. Ask only for missing required or risky fields.
3. Draft the ticket with summary, issue type, description, acceptance criteria, priority, component/s, assignee, epic/parent, linked work items, and project.
4. If the project, component, or epic/parent came from routing config, include the matched config rule in the draft.
5. Run a duplicate check, show any matches, then ask for explicit approval to create the issue (skip only if the user explicitly says so).
6. Create the issue through Jira only after approval.
7. Create approved Jira linked work items or parent-child relationships after issue creation when dependency fields are provided.
8. Return the created issue key and direct Jira browse link.
9. When creating from a local `requested_tickets` YAML entry, update that entry with `jira_key`, `jira_url`, and `creation_status: created` if the workspace file is writable.

Use this default draft shape. The "Jira Fields" section is for review and API fields; the "Jira Description" section is the exact Markdown body to send to Jira:

```markdown
## Jira Fields

| Field | Value |
| --- | --- |
| Project | Needs user input |
| Issue type | Task |
| Summary | Needs user input |
| Priority | Medium |
| Assignee | Unassigned |
| Component/s | None |
| Labels | None |
| Epic/Parent | None |
| Linked work items | None |
| Sprint | None |
| Story points | None |

## Jira Description

## Context

Short paragraph explaining the background, user impact, or reason for the ticket.

## Scope

- In scope item.
- Out of scope item, if useful.

## Acceptance Criteria

- Given a context, when an action happens, then an expected result occurs.
- Given a second context, when a second action happens, then another expected result occurs.

## Technical Notes

- Implementation note, constraint, affected file, or integration detail.

###### created by agent
```

Sprint and Story Points are optional Jira fields. Include them in the field table when the project's `workflow_type` is `scrum`. Omit them entirely when `workflow_type` is `kanban`. If the workflow type is unknown, ask the user once before drafting.

For "draft only" requests, stop after the draft and do not ask to create unless the user asks.

## Story Breakdown From Notes Or PRDs

When the user asks to turn notes, requirements, a PRD, or a planning document into Jira stories:

1. Read the provided content or file path. If no file is provided, use the notes in the conversation.
2. Identify features, bugs, technical tasks, spikes, dependencies, and acceptance criteria.
3. Produce small stories that can be independently reviewed and merged.
4. Preserve traceability by naming the source section, note, or requirement when available.
5. Output drafts in Markdown first. Do not create Jira issues until the user approves the full set.

Use this story draft format:

```markdown
## STORY-001: Story title

## Jira Fields

| Field | Value |
| --- | --- |
| Issue type | Story |
| Priority | Medium |
| Complexity | Small |
| Phase | Phase or milestone name |
| Component/s | None |
| Labels | None |
| Epic/Parent | None |
| Linked work items | None |

## Jira Description

## User Story

As a user type, I want an action, so that a benefit is achieved.

## Acceptance Criteria

- Given a context, when an action happens, then an expected result occurs.
- Given another context, when another action happens, then another expected result occurs.

## Technical Notes

- Relevant implementation detail.
- Files or systems likely to change, if known.

## Source

- Requirement, note, or PRD section used to derive this story.

###### created by agent
```

Order generated stories by dependency first, then phase, then priority. If a story looks larger than roughly one or two days of focused work, split it before presenting the draft.

## File-Based Ticket Intake

When the user provides a file with one or more requested tickets:

1. Read the file and identify candidate tickets by headings, bullets, tables, YAML/JSON objects, or repeated sections.
2. Produce a numbered draft for each candidate ticket. Do not create tickets during the first parsing pass.
3. Map fields only when the file or routing config supports them. Leave uncertain fields as `Needs user input`.
4. Treat rough wording as source notes, not final Jira copy: correct spelling/grammar, improve clarity, add concise context from routing metadata, and keep the user's intended meaning.
5. If many tickets are found, ask the user whether to create all, selected numbers, or revise the drafts.
6. Create only the explicitly approved tickets, and preserve the approved mapping between draft number and resulting Jira key.

For ambiguous files, summarize what was detected and ask for clarification instead of silently choosing issue boundaries or epics.

## Project And Epic Routing

Teams may maintain a config file that maps product/project names, components, labels, keywords, or request types to Jira projects and epics. Prefer a user-specified config path when provided; otherwise look for:

- `jira-routing.yml`
- `jira-routing.yaml`
- `.jira-routing.yml`
- `.jira-routing.yaml`

Do not treat `references/project-routing.md` as live routing config. It is a template and guidance file only.

For matching rules, workflow type handling (scrum vs kanban), and file intake shape, see `references/project-routing.md`. For a copyable starting point, use `assets/jira-routing.example.yml`.

When no routing file exists, do not block ticket drafting. Ask for the project, component/s, and epic/parent only when they are needed for a safe draft or create action.

When the user wants multiple tickets in different epics, help them create or confirm the routing file first. Ask for the Jira project key, each epic key, assignee, components, workflow type, and ticket notes before drafting create-ready Jira issues.

Routing files may include an optional `requested_tickets` section for rough ticket notes. Treat `requested_tickets` as draft input only: parse it, correct spelling and grammar, add concise inferred context, ask for missing required fields, show complete drafts, run duplicate checks, and require explicit approval before creating any Jira issues. In list fields, `[]` means no entries have been provided yet. Dependency fields may include `blocks`, `blocked_by`, `parent_of`, and `child_of`; apply these as Jira linked work items or parent-child relationships instead of writing them into the description.

Routing files may also include `initial_status` at the project, epic, or requested-ticket level. Use it only after showing the draft and getting approval, because status transitions mutate Jira. Prefer a board-visible status when the user has confirmed one; for example, if a board hides `To Do` but shows `Backlog`, use `initial_status: Backlog` for that route.

After creating issues from `requested_tickets`, mark each successfully created entry with `jira_key`, `jira_url`, and `creation_status: created`. If creation fails for one entry, record `creation_status: failed` and keep the error out of the Jira description unless the user asks to preserve it.

## Ticket Queries

When the user asks for open tickets, tickets in an epic, blockers, overdue work, or manager summaries:

1. Convert the request into bounded JQL.
2. Show the JQL first for broad team/project queries.
3. Execute the search if a Jira tool/API is available and the user has approved broad queries when needed.
4. Summarize results by the dimension the user asked for: assignee, epic, project, status, priority, due date, component, or blocker label.
5. Highlight missing owners, overdue work, blocked items, and stale tickets when relevant.

For individual queries such as "show my open tickets", execute directly if credentials/tools are available:

```jql
assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC
```

## Common Workflows

### Create Ticket

- Trigger examples: "create a Jira bug", "make a story for this", "file a ticket from these notes".
- Use Jira create metadata when available to validate required fields before creation.

### Prepare Draft

- Trigger examples: "draft a Jira ticket", "prepare but don't create", "turn this into a story".
- Produce a polished draft and stop.

### Find My Open Tickets

- Trigger examples: "show my open tickets", "what Jira tasks are assigned to me?"
- Use `assignee = currentUser()` unless the user names someone else.

### Show Tickets In Epic

- Trigger examples: "show open tickets under epic ABC-123", "summarize epic ABC-123".
- Query by parent/epic fields as appropriate for the Jira site. See `references/jira.md`.

### Summarize Stalled / On Hold Work

- Trigger examples: "what is on hold for the team?", "what tickets are stalled?", "why is ABC-123 blocked?"
- Query for status = "On Hold" within the project.
- For each result, fetch the most recent 2-3 comments and surface the reason if present.
- Show JQL before execution for broad team/project queries.

### List Overdue Tickets

- Trigger examples: "list overdue tickets", "what is past due in ABC?"
- Prefer project-bounded queries for team/project work.

## Update and Edit Tickets

When the user asks to update an existing ticket (change status, reassign, change priority, add a comment, update due date, or edit any field):

1. Identify the ticket key. If not provided, ask for it or search by summary.
2. Fetch the current ticket state and show relevant fields: key, status, assignee, priority, due date, last comment.
3. Apply the update only after explicit approval when the mutation is material.
4. Return the updated issue key and direct Jira browse link, plus the fields changed.
3. Show a clear summary of what will change:
   - Field updates: show `field: old value -> new value` for each change.
   - Status transition: show `status: Current Status -> Target Status` and confirm the transition is available.
   - Comment: show the full comment text before posting.
4. Require explicit approval before applying any mutation.
5. Apply the approved change and return the updated ticket key and a confirmation.

### Update Status

- Trigger examples: "mark ABC-123 as done", "move ABC-123 to In Progress", "transition ABC-123 to On Hold".
- Fetch available transitions first: `GET /rest/api/3/issue/{key}/transitions`.
- Show available statuses if the target is ambiguous.
- Use `POST /rest/api/3/issue/{key}/transitions` with the matched transition ID.

### Add Comment

- Trigger examples: "add a comment to ABC-123", "comment on ABC-123 saying ...", "update ABC-123 with this note".
- Show the full Markdown comment body for approval before posting.
- Use `contentFormat: "markdown"` when the Jira tool supports it. If using Jira REST directly, convert the Markdown comment body to ADF. See `references/jira.md`.

### Update Fields

- Trigger examples: "reassign ABC-123 to Jane", "change priority of ABC-123 to High", "set due date on ABC-123 to Friday".
- Show each change as `field: old -> new` and confirm before applying.
- Use `PUT /rest/api/3/issue/{key}` with only the fields being changed.

## Failure Handling

- If credentials are unavailable, provide the exact JQL or ticket payload and explain what environment/tooling is needed.
- If Jira rejects a create request, summarize field-level errors and ask for corrected values.
- If a query returns many results, summarize the first page and offer narrower filters.
- If epic fields differ by Jira configuration, try the site's supported parent/epic field and fall back to asking for the correct field name.
