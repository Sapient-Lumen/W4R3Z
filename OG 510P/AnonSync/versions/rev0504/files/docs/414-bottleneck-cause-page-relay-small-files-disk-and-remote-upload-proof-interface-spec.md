# Bottleneck cause page — relay, small files, disk, and remote-upload proof interface spec

## Purpose

The archive already has graphs, queue views, and route pages.
What it still lacked was one ordinary page for the more causal question:

> if transfer is slow right now, what is the strongest proved bottleneck class, what evidence supports it, and what repair changes only that cause instead of widening everything at once?

Current official Resilio docs make this seam concrete.
They still say slowness can come from many small files, relay use, remote-upload asymmetry, low-capacity networking hardware, security software delay, or disk-priority settings, while hidden internal work can also consume time before visible transfer.
That is useful truth.
It should not remain a troubleshooting list.

## Core decision

AnonSync must expose one first-class **Bottleneck cause** page whenever a subject, peer pair, or seat is materially below expected transfer or catch-up rate.

The page exists to answer five things in one place:

1. what bottleneck class is strongest right now
2. what evidence supports that claim and what remains merely plausible
3. whether the bottleneck is route, remote source, local disk, workload shape, or host interference
4. what least-widening repair changes that cause specifically
5. what evidence is still missing before a stronger claim is honest

## Fixed page order

1. **Current bottleneck verdict**
2. **Candidate stack**
3. **Evidence sufficiency**
4. **Least-widening repair ladder**
5. **Receipts and retest plan**

### 1) Current bottleneck verdict

Show:

- `bottleneck_cause_page_id`
- scope (`seat`, `subject`, or `peer-pair`)
- current `bottleneck_verdict` (`relay-penalty`, `remote-upload-ceiling`, `local-disk`, `many-small-files`, `host-interference`, `hidden-work`, `mixed`, `insufficient-evidence`, `unknown`)
- strongest honest summary
- confidence grade

### 2) Candidate stack

List candidate rows in descending strength.
Typical rows:

- active relay or indirect path
- slow source peer upload ceiling
- local disk write or hash pressure
- many-small-files / metadata-heavy workload
- host security or external-writer delay
- source absence masquerading as slowness
- temporary hidden work before transfer

Each row shows `proved`, `plausible`, `rejected`, or `not yet measured`.

### 3) Evidence sufficiency

Show:

- route class and relay truth
- peer upload/download asymmetry proof
- disk/cpu pressure proof
- queue depth and workload-shape proof
- source-availability proof
- graph/window sufficiency verdict

The operator must be able to answer:

> what evidence makes the current bottleneck claim stronger than a guess?

### 4) Least-widening repair ladder

Actions may include:

- `Wait for hidden work to clear`
- `Open peer route`
- `Repair direct path`
- `Reclassify as source absence`
- `Lift disk-priority guard`
- `Reduce competing workload`
- `Keep current posture`

Each repair rung must preview the likely bottleneck delta and its non-effects.

### 5) Receipts and retest plan

Show:

- last rate or latency window used for this claim
- last repair attempt touching this scope
- next comparison window and success threshold
- what counterexample would downgrade the verdict

## Public object

### Bottleneck cause page

Fields:

- `bottleneck_cause_page_id`
- `scope_ref`
- `bottleneck_verdict`
- `confidence_grade` (`strong`, `moderate`, `weak`, `insufficient`)
- `candidate_rows[]`
- `evidence_rows[]`
- `repair_ladder[]`
- `retest_plan`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. bottleneck verdict
3. strongest evidence
4. least-widening repair
5. confidence grade

Example:

```text
Laptop ↔ NAS     remote-upload-ceiling     source upload 4 MB/s cap     keep route, change source-side cap     moderate
```

## Non-goals

This page does **not** prove global system health or subject freshness by itself.
It proves only the current strongest **bottleneck cause** claim and its evidence basis.
