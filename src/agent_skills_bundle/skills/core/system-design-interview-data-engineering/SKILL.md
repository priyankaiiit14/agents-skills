---
name: system-design-interview-data-engineering
description: Use this skill when preparing for or walking through a data engineering system design interview (e.g., 'design a data ingestion pipeline', 'design a real-time analytics platform', 'design a data warehouse for X', 'design a CDC pipeline'). Provides a repeatable 6-step framework — requirements gathering, pipeline design (batch vs. streaming, Lambda/Kappa/Lakehouse architecture, orchestration), data modeling (star/snowflake, medallion layers, SCD types), storage and file format (Parquet/Avro/Delta/Iceberg, partitioning/bucketing/clustering), data quality and observability, and scalability/backfills/idempotency. Do NOT use this for web-service, API, or general distributed-systems interview questions — use the general system design interview skill for those instead.

---

# Data Engineering System Design Interview Framework

A repeatable 6-step process for data pipeline / data platform system design interviews. This is a sibling to the general (web-service) system design framework — same *shape* of process, different *content*, because DE interviews are graded on data modeling, storage, and correctness rather than APIs and service architecture.

**Core mindset to state out loud early:** if you ask 10 senior data engineers to design the same ingestion pipeline, you'll get 10 valid architectures, each trading off cost, latency, complexity, or failure handling differently. There is rarely one "correct" answer — the interview is graded on whether you can *justify* your tradeoffs, not on whether you land on a specific tool.

---

## 1. Requirements Gathering (~5 min)

Ask before designing anything:
- **Who is the user/consumer of this data?** Analysts running BI queries? An ML model? A downstream operational system? This changes everything downstream (latency needs, schema shape, freshness).
- **What functionality is the pipeline supposed to offer?** What questions should the output data be able to answer?
- **What are the latency/freshness requirements?** Daily refresh? Hourly? Near-real-time? True streaming? This is the single highest-leverage question — it determines batch-vs-streaming, which determines almost every later decision.
- **What's the data volume?** MBs, GBs, TBs, PBs — and is it steady or bursty (e.g., end-of-month spikes, event-driven surges)?
- **What's the shape/variety of the source data?** Structured, semi-structured (JSON/logs), unstructured? Single source or many heterogeneous sources?

Draw the same in-scope/out-of-scope line as any system design interview — say explicitly what you're deferring.

---

## 2. Pipeline Design (~5-10 min)

- **How does data move from source to destination?** Walk the path end to end: source system(s) → ingestion → processing → storage → serving layer.
- **Batch vs. streaming** — pick based on the latency requirement from Step 1, and say so explicitly: *"Since freshness needs to be under a minute, I'll design this as streaming; if hourly were acceptable I'd default to batch for simplicity and cost."*
- **Architecture pattern** — pick one and justify it against the requirements, don't just name-drop:
  - **Lambda architecture** — separate batch and speed layers merged at query time; justify when you need both perfect historical accuracy *and* low-latency approximate results, but flag the cost of maintaining two codepaths.
  - **Kappa architecture** — everything as a single streaming pipeline (e.g., Kafka + stream processor), even for "batch-like" workloads (batch = replaying the log). Justify when you want a single codepath and infra dedicated to correctness.
  - **Lakehouse architecture** — unify a data lake with warehouse-like transactional/schema guarantees (Delta/Iceberg/Hudi on top of object storage). Justify when you want to avoid maintaining a separate warehouse and lake copy of the same data.
- **Orchestration tool** — name one (Airflow, Prefect, Dagster, Mage) and justify by the property that matters for this problem (DAG complexity, dynamic task generation, backfill ergonomics, observability), not by familiarity alone.

---

## 3. Data Modeling (~10 min)

This is the DE analogue of "core entities" in a service design interview, but far more load-bearing here — get this wrong and everything downstream (cost, query performance, correctness) suffers.

- **Schema choice** — star vs. snowflake schema. Star is usually the default answer (denormalized, fast for BI/analytics); justify snowflake only if storage cost or strict normalization actually matters more than query simplicity here.
- **Facts and dimensions** — define what the fact table(s) measure (the "events" — orders, clicks, transactions) and what dimensions describe them (user, product, time, geography).
- **Medallion layers, if using a lakehouse pattern:**
  - **Bronze** — raw, untransformed, as-ingested (append-only, for lineage/replay).
  - **Silver** — cleaned, deduplicated, conformed — *this is typically where your fact/dimension model actually lives.*
  - **Gold** — aggregated, business-metric-ready tables built on top of the silver-layer model, optimized for specific consumption patterns (a specific dashboard, a specific ML feature set).
  - State explicitly which layer your fact/dimension tables sit in and why (usually silver, with gold as derived aggregates) — interviewers listen for whether you know this distinction, not just the layer names.
- **Slowly Changing Dimensions (SCD)** — pick a type and justify it against the requirement:
  - **Type 1** — overwrite, no history kept. Use when historical accuracy of the dimension doesn't matter (e.g., correcting a typo in a name).
  - **Type 2** — new row per change, with effective-dated versions. Use when you need to preserve history for point-in-time correctness (e.g., "what was the customer's address when this order shipped").
  - **Type 3** — limited history via extra columns (e.g., `previous_value`). Rarely the right default; mention only if a bounded, small amount of change history is genuinely sufficient.

---

## 4. Storage and File Format (~5 min)

- **File format** — Parquet (columnar, great for analytics scans), Avro (row-based, better for write-heavy/schema-evolving streaming ingestion), Delta/Iceberg (transactional table formats on top of Parquet — ACID, time travel, schema evolution on a data lake). Default answer for most modern lakehouse designs: **Parquet under Delta or Iceberg** unless there's a specific reason (e.g., high write throughput of small records) to prefer Avro at the ingestion layer.
- **Storage optimization strategy** — this is a direct cost/performance lever, always worth naming explicitly:
  - **Partitioning** — split data by a low-cardinality, frequently-filtered column (commonly date) to prune scans.
  - **Bucketing** — hash-based grouping within partitions to optimize joins/aggregations on a specific high-cardinality key.
  - **Liquid clustering** (Databricks-specific) — dynamically reclusters data without rigid partition boundaries, avoiding the "wrong partition key chosen upfront" problem.
  - Say explicitly: *"This choice directly affects both query cost and query latency, so I'd pick partition keys based on the most common filter predicate from Step 1's access patterns."*

---

## 5. Data Quality and Observability (~5-10 min)

This is the DE analogue of "non-functional requirements → reliability" in service design, but framed around correctness of *data* rather than uptime of a *service*.

- **Data quality rules/checks** — schema validation, null/uniqueness constraints, referential integrity, freshness checks, volume anomaly detection (e.g., "today's row count is 90% lower than the 7-day average — something's wrong upstream").
- **Testing** — unit tests on transformation logic, and data-level tests (e.g., dbt tests, Great Expectations) that run as part of the pipeline itself.
- **Monitoring & alerting** — pipeline run success/failure, SLA breach detection (data not ready by the promised time), data drift or schema drift alerts.
- **SLAs** — state them explicitly (e.g., "gold tables must be refreshed by 6am daily") — this is what actually earns trust in the pipeline from downstream consumers, and it's a concrete thing an interviewer can push on.

---

## 6. Scalability, Backfills, and DataOps (~5-10 min)

This is the DE analogue of "handling surge/contention" in service design — the hard failure modes here are about reprocessing and consistency, not about locks and race conditions.

- **Scalability** — can this pipeline handle 10x current volume? Identify the actual bottleneck (a single-node transform step, a non-partitioned table, a serial DAG stage) rather than answering "add more servers" generically.
- **Graceful failure handling** — what happens when a source is late, malformed, or unavailable? Does the pipeline fail the whole run, skip-and-alert, or quarantine bad records for later reprocessing?
- **Backfills** — can you reprocess 3 months of historical data on demand? This requires: idempotent writes (see below), partition-level (not just full-table) reprocessing capability, and enough compute elasticity to not starve the regular pipeline schedule while backfilling.
- **Idempotency** — does running the same pipeline/task twice (e.g., after a retry) produce the same result rather than duplicating data? Concrete mechanisms to name:
  - Upserts/merge (rather than naive append) keyed on a natural or surrogate key.
  - Partition-overwrite semantics (rewrite the whole partition rather than appending to it) for batch jobs.
  - Deduplication keyed on an idempotency/event ID for streaming ingestion.
- **DataOps practices** — CI/CD for pipeline code, version-controlled schema migrations, environment parity (dev/staging/prod), and rollback strategy if a bad deploy corrupts a table.

---

## Quick Checklist to Run Through Live

- [ ] Established freshness/latency requirement before picking batch vs. streaming
- [ ] Named an architecture pattern (Lambda / Kappa / Lakehouse) and justified it against the requirements, not by default habit
- [ ] Picked an orchestration tool and justified by a specific property it offers
- [ ] Chose star vs. snowflake and justified it
- [ ] Placed fact/dimension tables in a specific medallion layer (usually silver) and explained why
- [ ] Chose an SCD type per dimension based on whether historical accuracy is actually needed
- [ ] Named a file format and a storage optimization strategy (partitioning/bucketing/clustering) tied to the actual access pattern
- [ ] Defined concrete data quality checks and at least one explicit SLA
- [ ] Addressed 10x scale by naming the actual bottleneck, not a generic "scale it up"
- [ ] Explained how backfills work and how idempotency is guaranteed (upsert/merge, partition overwrite, or dedup key)
- [ ] Explicitly called out what's out of scope
