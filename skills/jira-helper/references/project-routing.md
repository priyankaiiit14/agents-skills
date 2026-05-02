# Project Routing Reference

Use this reference when a team wants configurable Jira project, component, assignee, or epic routing.

## Recommended Config

Prefer YAML because it is readable in code review and easy for agents to parse.

```yaml
projects:
  shifu:
    jira_project: DSML
    default_components:
      - shifu
    aliases:
      - shifu
      - personalized pricing
    # workflow_type controls which optional fields appear in drafts.
    # Values: scrum | kanban
    # Omit or leave blank if unknown; the skill will ask the user.
    workflow_type: scrum         # scrum projects get Sprint + Story Points fields
    # story_points_field: story_points   # override if your Jira uses a custom field name
    epics:
      sagemaker_migration:
        key: DSML-3782
        aliases:
          - sagemaker
          - migration
          - emr
      martech_cohorts:
        key: DSML-5173
        aliases:
          - martech
          - cohort
    default_issue_type: Task

  platform:
    jira_project: PLAT
    default_components:
      - platform
    aliases:
      - platform
    workflow_type: kanban        # kanban projects omit Sprint and Story Points
    default_issue_type: Task
```

## Routing Rules

- Treat project keys, epic keys, parent keys, component names, and assignee display names as exact identifiers when present.
- Treat aliases and keywords as hints, not proof.
- If one rule clearly matches, draft the ticket with that project/component/epic and show the matched rule.
- If more than one rule matches, ask the user to choose before creating.
- If the epic is inferred, require explicit confirmation after showing the complete draft.
- If the user confirms only part of a draft, ask before creating any ticket with unresolved fields.

## Workflow Type Rules

When building the ticket draft, check the matched project's `workflow_type`:

- `scrum`: include **Sprint** and **Story Points** as optional fields in the draft. If the user did not provide values, ask before creating.
- `kanban`: omit Sprint and Story Points entirely from the draft.
- Not set / unknown: ask the user once: "Is this project scrum (sprints) or kanban?" Then apply the rule above. Do not ask again for subsequent tickets in the same session for the same project.

## File Intake Shape

Team ticket files may be Markdown, YAML, JSON, CSV, or plain text. Preserve ticket boundaries from headings, table rows, YAML/JSON objects, or clearly separated blocks. When boundaries are unclear, produce candidate drafts and ask the user to confirm the split before creating.
