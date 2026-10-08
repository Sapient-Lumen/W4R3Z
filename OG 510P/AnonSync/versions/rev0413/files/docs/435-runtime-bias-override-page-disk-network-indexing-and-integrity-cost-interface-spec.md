# Runtime bias override page — disk, network, indexing, and integrity cost interface spec

## Purpose

The archive already had bottleneck and host-cadence pages.
What it still lacked was one ordinary page for the simpler question:

> which hidden advanced settings are currently biasing runtime behavior toward lower disk pressure, higher network use, more aggressive indexing, or stronger integrity checks, and what exact side effects come with that choice?

Current official Resilio docs make this seam concrete.
They still keep important runtime-bias truth in low-level settings such as disk priority, per-job disk threads, prefer-network-over-disk operations, indexing-thread count, verification-after-download, and parallel indexing.
That is useful truth.
It should not remain buried in an advanced table.

## Core decision

AnonSync must expose one first-class **Runtime bias override** page whenever hidden settings materially change the disk/network/CPU balance, re-download risk, indexing aggressiveness, verification cost, or interruption penalty of current work.

The page exists to answer five things in one place:

1. what runtime bias posture is currently active
2. which hidden knobs are contributing to it
3. what observable benefits that posture targets
4. what side effects or risks it buys
5. which next action is safest

## Fixed page order

1. **Current bias verdict**
2. **Contributing override rows**
3. **Targeted benefit claims**
4. **Side-effect budget**
5. **Safe next actions**

### 1) Current bias verdict

Show:

- `runtime_bias_override_page_id`
- seat and optional subject in scope
- current `bias_verdict` (`default-balance`, `disk-gentle`, `disk-aggressive`, `network-preferring`, `indexing-aggressive`, `integrity-heavy`, `mixed-bias`, `unknown`)
- strongest honest summary
- last evaluated time

The operator must be able to answer:

> what hidden runtime posture is this seat currently optimized for?

### 2) Contributing override rows

At minimum render rows for relevant active settings such as:

- disk I/O priority
- per-job or pooled disk workers
- network-over-disk preference
- indexing thread count
- parallel indexing
- verify-after-download behavior
- direct-torrent / interruption tradeoff if active

Each row must say whether it affects `disk`, `network`, `cpu`, `latency`, `retry cost`, or `integrity confidence`.

### 3) Targeted benefit claims

For each active bias show the intended operational gain, for example:

- reduce device interference
- improve high-latency network-share throughput
- shorten initial indexing wall-clock time
- avoid expensive diff computation
- strengthen post-write verification confidence

The page must separate intended benefit from observed success.

### 4) Side-effect budget

Show the strongest side effects and risks, such as:

- slower sync speed
- heavier disk load
- higher CPU use
- more re-download on interruption
- higher contention across shares
- delayed visibility of work due to prioritization changes

This section must answer:

> what am I paying for this runtime bias right now?

### 5) Safe next actions

Actions may include:

- `Return to balanced runtime`
- `Open bottleneck cause`
- `Open host cadence`
- `Raise integrity confidence`
- `Reduce disk pressure`
- `Export runtime-bias receipt`

Each action must preview whether it changes targeted benefit, cost, or both.

## Public object

### Runtime bias override page

Fields:

- `runtime_bias_override_page_id`
- `seat_ref`
- `subject_ref` nullable
- `bias_verdict`
- `contributing_override_rows[]`
- `benefit_rows[]`
- `side_effect_rows[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. active bias
2. targeted benefit
3. strongest current cost
4. dominant affected resource
5. next safest action

Example:

```text
network-preferring diff policy     avoid local diff work     interrupted transfer may re-download whole file     network     Return to balanced runtime
```

## Non-goals

This page does **not** replace performance dashboards or full bottleneck proof.
It proves only **which hidden overrides are biasing runtime behavior, what they are trying to buy, and what cost that purchase carries**.
