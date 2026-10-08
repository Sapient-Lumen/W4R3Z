# Runtime memory pressure, subject budget, and relief interface spec

## Purpose

The archive already has space pressure, work-phase visibility, and capacity-fit language.
What it still lacked was one explicit contract for another resource truth:

> when the runtime is short on memory, which subjects are causing it, what softer relief remains, and how does the product avoid turning one resource incident into full subject deletion and re-add ritual?

Current official Resilio docs make this seam painfully clear.
They still say the only way to make Sync use less RAM is to remove the biggest folders from Sync from all peers and share the folder again; that removal also deletes the database; and re-adding creates a new database and re-indexes the files while keeping only the current set of files.

That is practical support advice.
It is still not a good resource-relief contract.
Memory pressure is not the same thing as subject retirement.

AnonSync should therefore treat runtime memory pressure as one first-class budget surface with non-destructive relief before destructive subject reset.

## Core decision

Every seat must expose one **memory pressure ledger** that ties runtime memory consumption to concrete subject/index classes and to ordered relief options.
The product must separate at least five answers:

1. memory pressure source
2. current risk to the seat
3. reversible relief options
4. destructive relief options
5. continuity cost of each step

The product must never jump from `out of memory` to `remove the share and add it back` without first rendering what continuity is being thrown away.

## Fixed review order

Every memory-pressure case should render the same sections in the same order:

1. **Current memory pressure now**
2. **Top contributing subjects**
3. **Ordered relief ladder**
4. **Continuity receipt**

### 1) Current memory pressure now

This section should show:

- current memory pressure state (`healthy`, `elevated`, `critical`, `thrashing`, `recovering`)
- current pressure budget and observed usage
- whether the bottleneck is indexing, live transfer, metadata retention, or mixed work
- whether the seat is merely slow, at risk of crash, or already refusing new work

The operator must be able to answer: **how bad is it right now, and what class of work is causing it?**

### 2) Top contributing subjects

This section should rank the top subjects by live memory cost and show:

- subject label
- index/working-set contribution
- whether the load is durable or bursty
- whether the subject is currently active, idle-but-indexed, or partially detachable
- what local continuity artifacts depend on the current state

The operator must be able to answer: **which subjects are expensive, and what would be lost if I relieved them?**

### 3) Ordered relief ladder

The product should always present a relief ladder from least to most destructive, for example:

- slow scan or hashing concurrency
- suspend non-urgent subjects
- narrow local materialization or caches
- postpone history/verification classes
- split future intake across seats
- prepare subject sharding or migration
- rebuild local indexes only
- full subject detach/re-add

Every step must show:

- expected memory delta
- reversibility
- time cost
- continuity cost

The operator must be able to answer: **which softer moves remain before we cross into subject recreation?**

### 4) Continuity receipt

This section should show:

- action chosen
- memory delta target
- before/after continuity class
- whether any index lineage, history, or local proofs were intentionally discarded
- follow-up review references

The operator must be able to answer: **what later proves whether we relieved pressure safely or paid for it by resetting subject state?**

## Public objects

### `memory_pressure_ledger`

Fields:

- `memory_pressure_ledger_id`
- `seat_ref`
- `pressure_state`
- `budget_bytes`
- `observed_bytes`
- `pressure_classes[]`
- `top_subject_refs[]`
- `updated_at`

### `subject_memory_contribution`

Fields:

- `subject_memory_contribution_id`
- `subject_ref`
- `seat_ref`
- `estimated_bytes`
- `contribution_class` (`index`, `active-transfer`, `verification`, `history`, `mixed`)
- `burstiness`
- `reversible_relief_refs[]`
- `destructive_relief_refs[]`
- `generated_at`

### `memory_relief_plan`

Fields:

- `memory_relief_plan_id`
- `seat_ref`
- `target_delta_bytes`
- `ordered_steps[]`
- `strongest_step_class`
- `continuity_cost_summary`
- `created_at`

### `memory_relief_receipt`

Fields:

- `memory_relief_receipt_id`
- `seat_ref`
- `plan_ref`
- `applied_steps[]`
- `before_summary`
- `after_summary`
- `continuity_delta_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `memory healthy`
- `memory elevated · 2 subject indexes dominate`
- `memory critical · reversible relief still available`
- `memory critical · destructive subject reset would discard local index lineage`

## CLI shape

```text
anonsync memory status
anonsync memory top-subjects
anonsync memory relief plan --target 2GiB
anonsync memory relief apply <plan>
anonsync memory relief receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator gets an out-of-memory warning without seeing which subjects dominate working set
- the first honest step still looks like `remove and share again`
- destructive reset can happen without continuity cost and evidence loss being shown in the same review
- the product has space-pressure visibility but not memory-pressure visibility

## Non-clone reason

Resilio's current docs still route memory relief through full subject removal and re-add, with database deletion and re-index cost folded into the remedy.
AnonSync should instead publish subject memory budgets and an ordered relief ladder before any destructive reset.
