# Project Routing Reference

Use this reference when a team wants configurable Jira project, component, assignee, or epic routing.

## How To Use

Create one routing file at the root of the project where the agent is working:

- `jira-routing.yml`
- `jira-routing.yaml`
- `.jira-routing.yml`
- `.jira-routing.yaml`

Use this file only for non-secret routing metadata. Do not put Jira tokens, passwords, API keys, or private credentials in it.

Minimum useful fields:

- `jira_project`: Jira project key, such as `DSML`.
- `default_components`: components to apply when a rule matches.
- `aliases`: product, team, feature, or keyword hints that help match user requests.
- `workflow_type`: `scrum` or `kanban`; controls whether Sprint and Story Points appear in drafts.
- `default_issue_type`: fallback issue type when the user does not specify one.
- `default_assignee`: optional assignee hint. Use `currentUser()` when the tickets should be assigned to the authenticated Jira user, or provide a display name/account ID when known.
- `initial_status`: optional status to transition created issues into after creation and approval, such as `Backlog`, when that status is known to be visible on the team's board.
- `epics`: optional mapping of known epics or parents by key and aliases.
- `requested_tickets`: optional intake queue for drafts. This is useful when the user wants to keep routing and rough ticket notes in one YAML file. Treat this section as draft input only, not approval to create issues. Rough notes should be polished before drafting: correct spelling and grammar, clarify wording, add concise inferred context from routing metadata, and preserve the user's intended scope.

Use `assets/jira-routing.example.yml` as the copyable starter file. Copy it to the project root as `jira-routing.yml`, then replace placeholder project keys, epic keys, components, aliases, workflow type, and assignee.

When the user wants several tickets routed to different epics, ask setup questions first and help them create the routing file before drafting or creating tickets. Ask only for missing values:

- Jira project key: are all tickets in the same project?
- Epic keys or parent keys for each area.
- Component/s for each area, if components should differ.
- Assignee: `currentUser()`, a display name such as `Priyanka Mishra`, or a Jira account ID.
- Workflow type: scrum or kanban.
- Initial board-visible status, if the default Jira status does not appear on the team's board.
- Default issue type and priority.
- Ticket summaries or rough notes for each requested ticket.

If the routing file includes `requested_tickets`, preserve those entries while drafting. Each ticket should include at least `route`, `issue_type`, `summary`, and enough context or acceptance criteria to create a useful Jira description. Missing fields should be asked one at a time. In list fields, `[]` means no entries have been provided yet; users can leave it as-is or replace it with indented list items.

`initial_status` may be set on the project, epic route, or individual requested ticket. When present, show the planned transition in the draft, create the issue only after approval, then transition it to that status if Jira offers a valid transition. Use this for board visibility only when the team has confirmed the status appears on the board.

After a ticket is created from `requested_tickets`, update the entry in the routing file with:

- `jira_key`: created issue key.
- `jira_url`: direct Jira browse URL.
- `creation_status`: `created` or `failed`.

Supported dependency fields:

- `blocks`: issues this ticket blocks.
- `blocked_by`: issues blocking this ticket.
- `parent_of`: issues that should be children of this ticket.
- `child_of`: issue this ticket should be a child of, when it is not already represented by the routed epic/parent.

Dependency fields are for Jira relationships only. Do not render them as a "Dependencies" section in the Jira description, and never write empty dependency values such as "Blocks: None" into the description. After the ticket is created and approved dependency values exist, create Jira linked work items or parent-child relationships:

- `blocks`: create a Blocks link where this ticket blocks the listed issue.
- `blocked_by`: create a Blocks link where the listed issue blocks this ticket.
- `child_of`: set the parent when the relationship is a Jira parent/subtask relationship and it is not already represented by the routed epic/parent.
- `parent_of`: create or attach child/subtask work only when the user has explicitly approved the child issue relationship.

Use `links` for supporting docs, PRDs, design notes, dashboards, or runbooks that should appear in the Jira description. Prefer objects with `title` and `url` so the Jira description can render named Markdown links. If `links` is empty, omit the Links section from the description. If a link is provided as a raw string, infer a short label and render it as `[label](url)` rather than displaying the raw URL.

Example:

```yaml
requested_tickets:
  - route: stackforge
    jira_key: null
    jira_url: null
    creation_status: draft
    issue_type: Task
    summary: Short imperative title
    priority: Medium
    context: Why this work matters or what problem it solves.
    scope: []
    acceptance_criteria:
      - Given a context, when an action happens, then an expected result occurs.
    technical_notes: []
    dependencies:
      blocks: []
      blocked_by: []
      parent_of: []
      child_of: []
    links:
      - title: Supporting design doc
        url: https://example.com/design-doc
```

If the user says something like "create three tickets: one in Segmentation, one in Jarvis, one in Stackforge, assigned to me", first draft a routing config with placeholders for the missing epic keys. Then ask the user to fill or confirm those values before creating tickets.

After the routing file is confirmed, map each ticket by matching its topic to the configured epic aliases. Show the matched route in every draft:

```markdown
Routing rule used:
- Project: PROJ via `projects.data_platform`
- Epic/Parent: PROJ-111 via `epics.segmentation`
- Assignee: currentUser()
```

## Routing Rules

- Treat project keys, epic keys, parent keys, component names, and assignee display names as exact identifiers when present.
- Treat aliases and keywords as hints, not proof.
- If one rule clearly matches, draft the ticket with that project/component/epic and show the matched rule.
- If more than one rule matches, ask the user to choose before creating.
- If the epic is inferred, require explicit confirmation after showing the complete draft.
- If the user confirms only part of a draft, ask before creating any ticket with unresolved fields.
- If the routing file contains placeholder keys such as `PROJ-111`, do not create tickets until the user replaces or confirms the real Jira keys.

## Workflow Type Rules

When building the ticket draft, check the matched project's `workflow_type`:

- `scrum`: include **Sprint** and **Story Points** as optional fields in the draft. If the user did not provide values, ask before creating.
- `kanban`: omit Sprint and Story Points entirely from the draft.
- Not set / unknown: ask the user once: "Is this project scrum (sprints) or kanban?" Then apply the rule above. Do not ask again for subsequent tickets in the same session for the same project.

## File Intake Shape

Team ticket files may be Markdown, YAML, JSON, CSV, or plain text. Preserve ticket boundaries from headings, table rows, YAML/JSON objects, or clearly separated blocks. When boundaries are unclear, produce candidate drafts and ask the user to confirm the split before creating.
