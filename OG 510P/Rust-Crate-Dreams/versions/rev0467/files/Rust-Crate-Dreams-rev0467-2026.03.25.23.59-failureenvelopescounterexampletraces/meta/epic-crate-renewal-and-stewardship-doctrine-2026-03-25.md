# Epic crate renewal and stewardship doctrine — 2026-03-25

This note answers the practical question:

**What should a worthy crate provide other people *after* initial approval, so the result stays trustworthy without becoming a maintenance sink?**

## Core claim

A worthy crate should increasingly provide a **renewal contract**.
That contract sits above raw evidence, conformance claims, policy verdicts, and review packets.
It tells a downstream team:
- what must stay fresh,
- what can be cheaply rerun,
- what forces deeper review,
- who owns the queue,
- how long the result stays good,
- and how old decisions are retired without amnesia.

## What the crate should provide other people

### 1. A named renewal unit

The crate should say what gets renewed together.
Not every artifact should force a full rerun.
Examples of renewal units:
- one profile,
- one target/toolchain slice,
- one debugger tuple,
- one release boundary,
- one mirror/parity scope.

Without a named renewal unit, the archive risks producing giant approvals that are too expensive to maintain.

### 2. A freshness budget

The crate should ship a **freshness budget** that separates:
- cheap periodic checks,
- medium-cost replay slices,
- expensive human-review events,
- and explicit “do not auto-renew” conditions.

The point is not to predict exact labor hours.
The point is to make upkeep **bounded and reviewable**.

A good first schema family is:
- `renewal-program.json`
- `freshness-budget.json`
- `renewal-ticket.json`
- `renewal-ledger.jsonl`
- `stewardship-summary.md`
- `supersession-record.json`

### 3. A minimum rerun slice

A worthy crate should not force “rerun everything” for every trigger.
It should define the **minimum rerun slice** that can honestly answer the renewal question.

Examples:
- docs.rs metadata changed but not public API → rerun basis import + summary diff, not full corpus replay;
- alternate-registry posture changed → rerun parity and source-route checks first;
- new major release or semver-break warning → deeper review packet and human signoff;
- debugger version changed on one OS tuple → rerun only the affected tuple and corpus slice.

### 4. A stewardship queue and escalation path

The crate should provide a visible model for:
- what enters the renewal queue,
- which triggers are blocking,
- what can wait for a grace window,
- who may mark “manual review required”,
- and when the item escalates from cheap rerun to deeper review.

A worthy crate is not a full ticket system.
But it should expose queue-worthy objects with stable semantics.

### 5. A human stewardship summary

Most teams do not want to reread raw receipts.
The crate should provide a short human summary that says:
- what remains in good standing,
- what is due soon,
- what entered grace,
- what turned stale,
- and what was superseded or retired.

That summary is the bridge between tool output and sustainable operations.

### 6. Supersession and retirement rules

A worthy crate should tell users how to stop trusting an old result *cleanly*.
That means explicit transitions such as:
- `active`,
- `due-soon`,
- `due`,
- `grace`,
- `stale`,
- `superseded`,
- `retired`.

Old decisions should not merely disappear.
They should be superseded or retired with reason and replacement pointers.

### 7. A refusal boundary

The crate should refuse to pretend that all stale results are equally fixable.
It should explicitly refuse:
- auto-renewing across unknown public-boundary drift,
- carrying approvals across unreviewed alternate-registry changes,
- flattening prototype substrate changes into stable support meaning,
- or minting an “all good” status when only a subset was rerun.

## Release ladder

### Honest `0.1`
- one narrow receiver,
- one or two renewal units,
- one freshness budget vocabulary,
- one renewal queue object,
- one stewardship summary,
- explicit stale / grace / superseded states,
- no workflow-engine ambition.

### Honest `0.3`
- multiple renewal units,
- import of reviewed packets and continuity triggers,
- diff-aware rerun slices,
- stronger retirement / carry-forward records,
- profile overlays such as `ci-minimal`, `enterprise-offline`, `safety-case`.

### Honest `1.0`
- stable renewal semantics,
- stable cross-tool renewal packet shapes,
- stable human summary meanings,
- clear operator/escalation vocabulary,
- and narrow enough boundaries that organizations can wrap it in their own workflow.

## Package topology in practice

A renewal-worthy crate family will often want:
- one **CLI** for renew / due / stale / supersede operations,
- one **core library** for state transitions and trigger evaluation,
- one **schema crate** for renewal packet types,
- bounded **adapter crates** for docs.rs / crates.io / Cargo / local receipts,
- and one **scenario corpus** for renewal triggers and stale-state behavior.

This should stay a small suite, not a platform.

## Why this doctrine matters now

The official Rust substrate is getting more machine-usable, but it is still uneven and moving.
That means the archive should not only ask “can we produce a better packet?”
It should ask:

**can another team keep this packet alive at a cost they would actually accept?**

That is why renewal and stewardship now deserve to be first-class in the repo.
