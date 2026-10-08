# Hidden work, phase ledger, and honest progress interface spec

## Purpose

The archive already had activity-phase, settle-barrier, and transfer-finality language.
What it still lacked was one explicit contract for a more basic operator question:

> when the system is busy but visible progress is thin, what page proves whether it is scanning, hashing, merging, deduplicating, reading, writing, or genuinely stuck?

Current official Resilio docs make this seam sharper than a generic spinner or `working` badge would.
They still describe an error state that says some internal tasks are taking time to complete and explicitly admit that many important operations are hidden from the user.
They then enumerate scanning files, hashing file, checking file blocks, copying local file blocks for deduplication, merging folder tree, reading file from disk, transferring, and writing file to disk.
They also say this can recover automatically, but that the same symptom can mean resource pressure, a huge workset, or a retrying merge.

That is candid implementation guidance.
It is still not a good public work-progress contract.

## Core decision

AnonSync should make **work phases** first-class.

Every subject needs one visible phase ledger that declares:

- which work classes are active now
- which objects are blocked behind them
- whether the phase is forward progress, retried progress, or no-progress waiting
- which resource class is the bottleneck
- what proof will show that the phase actually completed

If an operator still has to infer system truth from disk usage, vague warnings, and elapsed time, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- important work still hides behind a generic `internal tasks` warning
- several different states with very different remedies can look identical from outside
- hashing, deduplication, merge retry, and ordinary transfer are not the same promise
- a receiving peer may be spending real time verifying or reusing local material long before bytes visibly move over the network
- the product still treats `recovering automatically` and `please contact support` as adjacent without a public proof ladder between them
- operators can still mistake CPU/disk-heavy local verification for a transport stall

AnonSync should therefore keep one stronger rule:

> progress must publish the phase plan, the bottleneck, and the next proof point, not merely a busy state.

## Fixed review order

Every non-trivial work-progress incident should render the same sections in the same order:

1. **Phase ledger now**
2. **Blocked outputs and next proof point**
3. **Bottleneck and retry truth**
4. **Receipt and replay promise**

### 1) Phase ledger now

This section should show:

- active phases: `scan`, `hash`, `check-blocks`, `reuse-local-blocks`, `merge-tree`, `read-source`, `transfer`, `write-target`, `verify-final`, `idle`
- whether each phase is running, queued, retried, or waiting
- subject-local versus cross-subject scope
- object counts and byte estimates behind each phase
- the oldest item waiting in that phase

The operator must be able to answer: **what work is actually happening right now?**

### 2) Blocked outputs and next proof point

This section should show:

- which visible outcomes are waiting on the current phase
- whether the next expected proof is a tree-merge receipt, a local-block witness, a verified write, or a finalized object
- estimated work class, not fake time promises
- whether any object can finish while others remain behind

The operator must be able to answer: **what visible result is this work trying to unlock?**

### 3) Bottleneck and retry truth

This section should show:

- dominant bottleneck class: `disk`, `cpu`, `network`, `metadata-churn`, `permission`, `space`, `clock`, `policy`, `unknown`
- whether the phase is monotonic progress, bounded retry, or unbounded waiting
- last successful checkpoint
- whether the system expects self-recovery or now requires operator review

The operator must be able to answer: **is the system progressing, retrying honestly, or merely stuck?**

### 4) Receipt and replay promise

This section should show:

- the phase sequence that actually ran
- which proofs were emitted at the end of each high-signal phase
- whether any phase was abandoned or replayed
- the durable event trail for CLI/API parity

The operator must be able to answer: **what work really happened, and what evidence proves it completed?**

## Main surface

The subject workspace should expose a **Work phases** card with:

- strongest active phase
- bottleneck badge
- count of retrying items
- count of visible objects blocked behind local work
- a drill-in action: `Inspect work ledger`

## Detailed surface

The detailed page should have five panes.

### Pane A — Phase timeline

Rows:

- phase
- scope
- running/queued/retrying state
- objects waiting
- oldest age
- next proof point

### Pane B — Output blockers

For each blocked visible outcome:

- object or subject
- blocked by phase
- last successful checkpoint
- next honest action

### Pane C — Bottleneck classifier

Shows:

- dominant resource class
- saturation indicators
- whether the condition is expected for workload shape
- whether review is required now

### Pane D — Recovery ladder

Actions:

- wait for bounded self-recovery
- narrow workload / split subject
- raise host budget
- re-run review for policy or path blocker
- escalate with evidence bundle

### Pane E — Receipts

Shows prior phase-completion and retry receipts.

## CLI parity

Minimum commands:

- `anonsync work show <subject>`
- `anonsync work inspect <subject> --object <id>`
- `anonsync work bottleneck <subject>`
- `anonsync work receipt show <receipt-id>`

## Non-goals

This spec does **not** define:

- scheduler policy
- bandwidth budgeting
- final transfer semantics for partial artifacts
- exact host telemetry collection internals
