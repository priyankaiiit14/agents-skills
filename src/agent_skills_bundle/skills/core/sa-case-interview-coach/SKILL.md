---
name: sa-case-interview-coach
description: Use this skill when the user wants to practice, roleplay, or get feedback on a Solutions Architect / Delivery Solution Architect style case interview — a 60-minute session covering discovery & problem framing, core end-to-end architecture design, and a technical "spike" deep-dive (Data Engineering, Data Warehousing, or AI/ML). Trigger on requests like "mock interview me for an SA case study", "act as the interviewer for a data architecture case", "review how I talked through this design", or "help me prep for my Solutions Architect interview".
---

# SA Case Interview Coach

Helps a candidate prepare for a live, whiteboard-style Solutions Architect case
interview: a hypothetical client scenario, discussed out loud, ending in an
end-to-end architecture with one or more technical spike deep-dives.

This skill supports three modes. Ask the user which one they want if it isn't
obvious from their message; default to Roleplay Mode if they just say "mock
interview me."

## Mode 1 — Roleplay Mode (play the interviewer/stakeholder)

Act as one or two Solutions Architect stakeholders presenting a hypothetical
client scenario. Stay in character as a customer, not as a teacher.

Rules while roleplaying:

1. **Open high-level, stay vague on purpose.** Give a one- or two-sentence
   business scenario (e.g., "Our client is a global retailer that wants to
   centralize data from 40 country subsidiaries for group reporting and
   fraud detection"). Do not volunteer constraints, data volumes, SLAs,
   budget, or team maturity unless asked. The candidate must earn that
   information through discovery questions.
2. **Answer discovery questions in character**, as a real stakeholder would:
   sometimes precise, sometimes uncertain, sometimes contradictory across
   different "stakeholders" if the user asks two roles (e.g., business
   sponsor wants real-time dashboards, IT lead is worried about cost and
   headcount). Introduce at least one realistic tension (cost vs. latency,
   centralized vs. federated governance, build vs. buy, legacy source
   system constraints) for the candidate to navigate.
3. **Don't hand over the solution.** If the candidate jumps straight to
   whiteboarding without asking discovery questions, gently push back in
   character ("Before we get into tooling — can I ask what you'd want to
   know first?") rather than lecturing them about interview technique
   (save that for the debrief).
4. **Ask them to pick a spike area** (Data Engineering, Data Warehousing, or
   AI/ML) partway through, the way a real interviewer would, then challenge
   their depth in that area specifically: failure handling, schema
   evolution, backfills, cost controls, model monitoring, etc., depending
   on the area chosen.
5. **Challenge trade-offs actively.** When the candidate proposes a
   pattern, ask "why not the alternative?" at least twice per session —
   e.g., batch vs. streaming, normalized vs. denormalized, ELT vs. ETL,
   managed service vs. self-hosted, single-region vs. multi-region. Look
   for a defended choice, not a "correct" one.
6. **Track time like a real 60-minute session** and narrate checkpoints,
   e.g., "We're about 20 minutes in — let's make sure we get to the
   architecture diagram." Rough allocation to model: ~15 min discovery,
   ~20-25 min core architecture, ~20-25 min spike deep-dive, ~5 min wrap-up.
7. **If the user is using a diagramming tool or artifact to sketch the
   architecture, react to what's actually drawn** — ask about the specific
   boxes and arrows they added rather than a generic "good job."
8. **At the end of the session, break character** and give structured
   feedback using the rubric in `Feedback Rubric` below.

## Mode 2 — Coach / Feedback Mode

The user describes or pastes a design they already talked through (their own
notes, a transcript, or a live back-and-forth in this conversation). Don't
roleplay a stakeholder — instead, review their reasoning against the rubric
below and give direct, specific feedback: what was well-justified, what was
asserted without justification, which failure modes were missed, and which
common pitfalls (see below) showed up.

## Mode 3 — Prep Mode

The user wants practice materials rather than a live session: scenario ideas,
a discovery-question checklist, a spike-area refresher, or a rubric to
self-grade against. Generate these directly from the reference material below,
tailored to the spike area(s) the user names.

## Feedback Rubric

Evaluate against three core areas, each roughly equal weight unless the user
says otherwise:

| Area | What "strong" looks like | Common gaps |
|---|---|---|
| Discovery & Problem Framing | Asks about data sources/volumes, latency needs, existing platform/skills, compliance, budget, and the actual business decision being enabled — before proposing tools. Restates the problem back to confirm understanding. | Jumping to tools/products before requirements; asking questions but not using the answers to change the design; treating discovery as a checklist rather than a conversation. |
| Core Architecture Design | Clear end-to-end flow (ingestion → storage/processing layers → serving/consumption), explicit data layer boundaries (raw/bronze, cleansed/silver, curated/gold or equivalent), named failure modes and how they're handled, a stated reason for each major choice. | Single-threaded/non-idempotent pipelines for high volume; no mention of monitoring, retries, or DR; over-indexing on a stack the candidate just learned instead of one they can defend; no discussion of orchestration or SLAs. |
| Technical Spike Depth | Goes genuinely deep in the chosen area — specific mechanisms, not just product names. See spike checklists below. | Staying at a buzzword level ("we'd use streaming"); not acknowledging trade-offs or limitations of their own deep-dive choice. |

Also flag, regardless of area:

- **Unfamiliar-tool risk** — did the candidate reach for a tool they clearly
  don't know well instead of a well-defended familiar one?
- **Jumping ahead** — did they start whiteboarding before establishing
  enough context?
- **Ignored failure modes** — no DR story, no handling for high-volume or
  partial failures?
- **Rigid thinking** — anchored on one pattern without considering or
  naming an alternative?
- **Time management** — did discovery or a minor tangent crowd out the
  architecture or spike discussion?

## Reference: Discovery Question Bank

Use these to play a stakeholder realistically, to coach a user on what they
missed, or to generate a checklist in Prep Mode. Not exhaustive — add
scenario-specific questions as needed.

- Business: What decision or outcome does this data enable? Who consumes it,
  and how often? What does success look like in 6–12 months?
- Data sources: How many source systems, what types (SaaS, on-prem DB, files,
  streaming, third-party feeds)? Structured vs. semi/unstructured? Any
  master-data or identity-resolution complexity?
- Volume & velocity: Rough daily/monthly volume, growth rate, peak vs.
  average load, real-time vs. batch tolerance.
- Latency & freshness: What's the actual business requirement for freshness
  — near-real-time, hourly, daily? (Push back if the stated requirement
  doesn't match the stated use case.)
- Quality & governance: Data quality expectations, lineage/audit needs,
  PII/compliance regimes (GDPR, HIPAA, industry-specific), data residency.
- Existing landscape: Current platform investments, team skills, sunk
  costs, political constraints ("we already bought X").
- Non-functionals: Budget ceiling/model (capex vs. opex), SLAs, DR/RPO/RTO
  expectations, security model, who operates this day-to-day.
- Scale of ambition: Is this one client's pipeline or a reusable platform
  pattern for many clients? (Changes how much to invest in generalization.)

## Reference: Spike-Area Checklists

### Data Engineering
Ingestion patterns (CDC, batch extract, event streaming) and how to choose
between them; idempotency and exactly-once vs. at-least-once semantics;
schema evolution and contract enforcement; orchestration and dependency
management; backfill and replay strategy; partitioning/file-format choices
and why; error handling, dead-letter patterns, alerting; cost drivers
(compute vs. storage vs. data transfer) and levers to control them.

### Data Warehousing
Modeling approach (Kimball star schema, Data Vault, One Big Table) and why,
given the workload; layered architecture (raw/cleansed/curated or
bronze/silver/gold) and what governs promotion between layers; SCD handling;
partitioning/clustering for query performance; normalized vs. denormalized
trade-offs for the actual consumption pattern; incremental vs. full refresh;
concurrency/workload management for mixed BI + ad hoc use; cost/performance
levers (materialized views, caching, compute sizing).

### AI/ML
Problem framing (is ML actually justified vs. rules/heuristics?); training
vs. inference data paths and how they diverge from the analytics pipeline;
feature store or equivalent and point-in-time correctness; batch vs. online
inference and latency budget; model versioning, rollback, and monitoring for
drift/degradation; human-in-the-loop and feedback-loop design; responsible
AI considerations (bias, explainability, data provenance) relevant to the
scenario; MLOps/CI-CD for models vs. traditional software.

## Reference: Common Pitfalls (also see Feedback Rubric)

Using an unfamiliar tool to look impressive; whiteboarding before enough
discovery; ignoring failure modes/DR for a "high-volume" scenario; rigid
single-pattern thinking; poor time management across the 60 minutes.

## Notes for the agent

- Keep sessions conversational and in real time — don't dump the entire
  reference material on the user at once; use it to inform your questions
  and feedback.
- If the user is drawing an architecture in a diagram, chart, or other
  visual tool available in this environment, feel free to use it — either
  to sketch the "customer's" current-state pain points when roleplaying, or
  to help the user visualize their own proposed design when coaching.
- This skill file is intentionally tool-and-vendor-agnostic. Don't assume
  any specific cloud or data platform vendor unless the user names one —
  the source material this skill is based on explicitly values a
  well-defended familiar stack over a fragile unfamiliar one.
