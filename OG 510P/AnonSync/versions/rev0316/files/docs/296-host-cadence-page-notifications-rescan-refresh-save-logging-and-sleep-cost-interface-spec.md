# Host cadence page — notifications, rescan, refresh, save, logging, and sleep-cost interface spec

## Purpose

The archive already has change-detection coverage, contention, memory pressure, and battery-saver work.
What it still lacked was one ordinary page for the host-level question administrators eventually face:

> why is this host active or quiet right now, which background cadences are running, what freshness did they buy, and what wake or disk cost do they still impose?

This page exists so cadence truth does not hide in advanced settings and troubleshooting recipes.

## Core rule

Cadence is a public freshness contract.
The product must separate at least:

- notification coverage
- periodic rescan cadence
- helper-refresh cadence
- settings-save cadence
- logging/profiling cadence
- observed wake/sleep cost

If the operator still has to infer host quietness from one rescan interval and one sleepy disk complaint, the page is not explicit enough.

## Fixed review order

Every serious host-cadence page should render the same sections in the same order:

1. **Current cadence verdict**
2. **Detection and refresh matrix**
3. **Wakefulness and freshness tradeoffs**
4. **Quiet-host review actions**
5. **Receipts and audit trail**

### 1) Current cadence verdict

This section should answer:

- whether the host is `responsive`, `guarded`, `quiet-biased`, `rescan-heavy`, `watcher-degraded`, or `sleep-hostile`
- whether the posture is host-wide or dominated by one subject
- whether any setting is temporary or emergency-grade

The operator must be able to answer: **what cadence posture is this host currently in?**

### 2) Detection and refresh matrix

Rows should include:

- filesystem notification coverage
- periodic rescan interval
- helper/bootstrap refresh interval
- settings-save cadence
- log/profiler activity
- manual rescan availability

For each row show:

- current setting
- effective source
- primary benefit
- primary cost
- degraded consequences if narrowed further

The operator must be able to answer: **what background loops are running, and why?**

### 3) Wakefulness and freshness tradeoffs

This section should show:

- whether the host is staying awake because of peer demand, local scans, logging, or verification work
- whether disabled notifications or watcher exhaustion are forcing slower freshness
- whether quieting changes create `manual-rescan required`, `periodic-only freshness`, or `reduced helper freshness` states
- whether disk sleep or low-churn goals are being met or defeated

The operator must be able to answer: **what exact cost did my quieting or acceleration posture buy me?**

### 4) Quiet-host review actions

This section should offer reviewed actions such as:

- lengthen rescan interval
- shorten rescan interval
- lower logging/profiling intensity
- increase watcher coverage
- reduce helper refresh frequency
- restore balanced cadence

Every action preview must show:

- freshness effect
- wake/sleep effect
- diagnostic/visibility effect
- reversibility

The operator must be able to answer: **how do I make this host quieter or fresher without guessing?**

### 5) Receipts and audit trail

This section should show:

- cadence-change receipts
- temporary quiet-host expiry
- watcher-pressure acknowledgments
- quiet-host versus freshness tradeoff reviews

The operator must be able to answer: **what proof explains why this host was intentionally quieter or intentionally fresher?**

## States

Use a small stable vocabulary:

- `responsive`
- `balanced`
- `quiet-biased`
- `rescan-heavy`
- `watcher-degraded`
- `sleep-hostile`

## Main surface

A compact **Host cadence** card should show:

- current cadence verdict
- strongest freshness penalty if any
- strongest wakefulness source if any
- primary action: `Inspect host cadence`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- host / seat
- cadence verdict
- strongest freshness penalty
- strongest wake source
- primary action

### Pane B — Detection and refresh matrix

Columns:

- loop
- current value
- source
- benefit
- cost
- warning

### Pane C — Wakefulness and freshness

Rows may include:

- watcher exhaustion forcing periodic-only freshness
- quiet-host intervals still defeated by peer demand
- logging preventing disk sleep
- helper refresh reduced below normal
- manual rescan now required for some targets

### Pane D — Reviewed actions

Shows preview cards with explicit before/after consequences.

### Pane E — Receipts

Shows:

- cadence change receipt
- watcher-limit acknowledgment
- quiet-host review receipt

## CLI parity

Minimum commands:

- `anonsync cadence show`
- `anonsync cadence show --seat <seat>`
- `anonsync cadence preview --rescan 1800 --helper-refresh 7200 --logging low`
- `anonsync cadence preview --watchers repair`
- `anonsync cadence receipt <receipt-id>`

## Acceptance criteria

A user can:

- see all meaningful background cadences in one place
- tell why a host is awake, sleepy, or stale
- preview quiet-host changes and their freshness cost before commit
- prove later which cadence tradeoff was chosen and why
