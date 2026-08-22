# DSA pair-programming field guide

Use the sections relevant to the requested drill or warm-up.

## Discovery

Aim to establish:

- decision or customer outcome;
- row/event grain and stable identifiers;
- source shape, update pattern, and known bad data;
- expected volume, velocity, latency, and growth;
- correctness rules and acceptance checks;
- consumers, output shape, and operational constraints.

A strong transition into coding is: “I’ll state the assumptions we agreed on, create a tiny representative dataset with failure cases, and prove one end-to-end path before optimizing.”

## Synthetic data

Define the schema and invariants before generating rows. Include only edge cases that exercise stated requirements. Use a fixed seed when randomness is involved and keep a small deterministic fixture for debugging.

For scalable Spark examples, favor distributed construction such as SQL `range` or `spark.range` plus column expressions over building a large local Python collection. For small semantic fixtures, a short literal dataset can be clearer. Verify:

- schema and grain;
- row count and key uniqueness expectations;
- null, duplicate, and boundary-case counts;
- value ranges and referential assumptions;
- reproducibility of important cases.

## Building the solution

Use the fewest layers that make the current requirement clear. A useful notebook sequence is:

1. assumptions and expected result;
2. representative input;
3. transformation in small named stages;
4. checks after risky boundaries such as parsing, deduplication, and joins;
5. final result and reconciliation;
6. scale and production notes.

Do not introduce Bronze/Silver/Gold, streaming, orchestration, or a new abstraction unless the requirement justifies it. If persistence or a platform feature is unavailable, use DataFrames or temporary views and explain the production alternative.

## Debugging loop

Narrate: “I observe X. My leading hypothesis is Y because Z. I’ll run A; if Y is correct, I expect B.”

Reduce to a small reproducible input, inspect the actual schema and intermediate rows, and change one variable at a time. After the fix, re-run the failing case plus one normal case. Separate root cause from symptom and note whether the fix changes data semantics.

## Distributed reasoning

Be ready to explain, only as applicable:

- transformations are lazy until an action;
- narrow operations can stay within partitions, while joins, grouping, ordering, and repartitioning often shuffle;
- join strategy depends on size and statistics; broadcasting is useful only when the build side is safely small;
- skew can leave a few tasks slow even when average partition size looks healthy;
- `collect()` and large local objects move risk to the driver;
- caching helps reused expensive results, but costs memory and can be worse for one-pass data;
- streaming correctness depends on event time, watermarking, state, late-data policy, and idempotent outputs.

Pair each performance idea with evidence to inspect, such as the physical plan, stage/task metrics, partition counts, data distribution, or observed reuse.

## Auditing AI output

Before using generated code, ask:

1. Does this API exist in the current runtime and is it allowed here?
2. What schema, nullability, ordering, uniqueness, or timezone assumptions are hidden?
3. Is the business logic correct on normal and adversarial examples?
4. Is randomness seeded and is the result reproducible enough to debug?
5. Does it force data onto the driver or cause an avoidable shuffle?
6. Can I explain each line and the expected output?

When the AI is wrong, identify the precise failed assumption, correct the smallest necessary part, and validate the correction. This demonstrates stewardship better than discarding everything without analysis.

## Customer translation

Use this compact structure:

- **Goal:** what decision or user need the solution serves.
- **Flow:** how data changes from input to output in plain language.
- **Choice:** why the key implementation choice fits the current constraints.
- **Trust:** how correctness is checked and failures are surfaced.
- **Scale:** the first likely bottleneck and what evidence would trigger a change.

Avoid explaining a notebook cell-by-cell unless asked. Translate implementation details into reliability, cost, latency, and maintainability consequences.

## Ten-minute warm-up

1. Open the notebook environment and run one trivial SQL or Python cell.
2. Confirm the available compute and runtime rather than relying on remembered UI steps.
3. Generate a seeded dataset with one intentional null and duplicate.
4. Run a transformation and a reconciliation check.
5. Inspect an execution plan and narrate where a shuffle may occur.
6. Practice a 30-second customer summary.
