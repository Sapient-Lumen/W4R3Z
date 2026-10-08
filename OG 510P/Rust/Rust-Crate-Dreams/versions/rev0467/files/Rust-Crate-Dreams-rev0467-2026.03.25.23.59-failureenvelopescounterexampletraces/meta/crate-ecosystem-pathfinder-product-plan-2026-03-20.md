# Crate ecosystem pathfinder product plan — 2026-03-20

This note exists to sharpen **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** into a more implementation-ready product.
The archive already had good material for:

- task fit,
- role coverage,
- interop fit,
- starter-set readiness,
- lock-in cost,
- scope split,
- evidence origin,
- and freshness windows.

What it still lacked was one boring receiver-facing story for **decision aging** after a team has already frozen a starter set.

## Main product shift

A credible pathfinder should now provide not just a **freezeable decision pack**, but a **freezeable-and-reviewable decision pack**.

That means the product must answer three more questions:

1. **Which later events force review?**
2. **How long may the frozen decision age quietly?**
3. **What is the current watch state of the frozen answer?**

## Why this became more urgent

Three ecosystem realities now make the gap sharper:

1. **Faster-moving registry/security/support substrate**
   - crates.io has a Security tab, trusted-publishing-only mode, and `pubtime` in the index,
   - malicious-crate routine notifications now primarily flow through RustSec advisories and RSS,
   - maintainer support/health posture is increasingly a mutable, reviewable signal rather than a release-bound badge.

2. **Visible support posture can shift without local choice changing**
   - docs.rs default-target changes proved that a crate’s visible support story can move even when a team’s starter-set lock stays frozen.

3. **Frozen decisions are increasingly reused downstream**
   - once teams, educators, platform groups, or templates commit a starter-set lock, the choice starts living in docs, ADRs, scaffolding, and policy.
   - at that point, “we once reviewed it” is no longer enough.

## What the crate should provide other people now

In addition to ranked choice and freeze readiness, the crate should provide:

1. **A revisit-trigger policy**
   - which event classes reopen review,
   - which ones merely mark `review_due`,
   - which ones fully mark `invalidated`,
   - and which signals are advisory only.

2. **A freeze-horizon policy**
   - soft review cadence,
   - maximum lock age,
   - and lane-specific overrides for especially fast-moving areas.

3. **A decision-watch report**
   - current state: `steady`, `review_due`, `invalidated`, `superseded`, `manual_review_required`,
   - fired triggers,
   - last reviewed timestamp,
   - next review due,
   - and exact evidence refs that changed the watch state.

4. **A no-silent-replacement guarantee**
   - the watch layer should not quietly replace one starter set with another,
   - only raise review state and explain why.

## First-class artifacts for this pass

### `revisit-trigger.policy.json`

This should describe what counts as a material event for one frozen starter set.

Suggested `0.1` trigger classes:

- `rustsec_advisory`
- `malicious_crate_notice`
- `health_contract_changed`
- `docs_surface_changed`
- `major_release_after_cooldown`
- `task_constraint_changed`
- `manual_review_requested`

Each trigger should be able to map to one of:

- `inform_only`
- `review_due`
- `invalidate_until_reviewed`

### `freeze-horizon.policy.json`

This should answer the time-based question that freshness windows do not:

- how many days until routine review is due,
- how many days until the lock is too old to present as freshly reviewed,
- which event classes shorten those windows.

### `decision-watch.report.json`

This is the joined state report for a frozen decision.

Suggested core fields:

- `starter_set`
- `watch_state`
- `last_reviewed_at`
- `next_review_due_at`
- `trigger_events`
- `evidence_refs`
- `notes`

## Minimal workflow shape

1. `cargo pathfinder freeze`
   - emits the starter-set lock and the watch-related policies.
2. `cargo pathfinder watch`
   - imports updated advisory/support/docs signals.
3. `cargo pathfinder doctor`
   - renders why the watch state changed.
4. `cargo pathfinder diff`
   - compares old and new decision/watch bundles.
5. `cargo pathfinder supersede`
   - optionally records that a newer reviewed decision replaces the old one.

## Distinctions the implementation must keep explicit

### Freshness windows are not revisit triggers

- **freshness window**: “is this signal too fresh to freeze into the decision right now?”
- **revisit trigger**: “a frozen decision already exists; does this new signal reopen review?”

### Review due is not invalidated

- `review_due` means the decision should be re-checked.
- `invalidated` means the recommendation should no longer pretend to be currently approved.

### Fired trigger is not automatic replacement

A RustSec advisory, malicious-crate notice, or health/support shift may invalidate a decision.
That does **not** mean the product should silently bless a replacement crate without human review.

### Superseded is not stale-by-default

A decision may be old but still `steady` if the policy permits it and no trigger fired.
It becomes `superseded` only when a newer reviewed decision explicitly replaces it.

## Two implementation-ready fixture families

### 1. `rustsec_or_malicious_crate_signal_invalidates_frozen_decision`

Goal: prove that security/malware triggers can invalidate a frozen answer without pretending the replacement is automatically chosen.

### 2. `docs_surface_shift_triggers_review_without_forcing_auto_replacement`

Goal: prove that docs/support visibility shifts can make a frozen answer `review_due` while keeping task fit and replacement choice as human decisions.

## Recommended `0.2` success bar

`0.2` is good enough when a maintainer can:

1. freeze one starter-set decision,
2. declare which events reopen review,
3. declare how long the lock may age quietly,
4. run one watch command later,
5. get an explicit watch state instead of a silent stale lock,
6. and avoid automatic crate replacement without human approval.

That is already enough to make frozen crate-choice artifacts feel alive rather than archival.


## 2026-03-23 addendum — freeze timebox and as-of replay

The next implementation-ready layer for **P-0509** is not another ranking model.
It is a portable answer to:

1. what evidence window the frozen decision relied on,
2. what facts were still cooling or still invisible then,
3. and how later replay compares with the current ecosystem without pretending replacement is automatic.

Promote these artifacts next:

- `decision-timebox.receipt.json`
- `as-of-replay.report.json`

And keep these truths separate:

- current public visibility versus freeze-time basis,
- docs-surface drift versus task-fit drift,
- fresh-release enthusiasm versus cooldown-cleared evidence,
- and replay evidence versus replacement authority.


## 2026-03-23 addendum — explicit exclusion and candidate re-entry

The next implementation-ready layer for **P-0509** is not another ranking signal.
It is a portable answer to:

1. why a plausible candidate was excluded,
2. whether that exclusion was reversible,
3. what evidence would reopen consideration,
4. and which public-surface changes are *not* enough.

Promote these artifacts next:

- `candidate-elimination.receipt.json`
- `candidate-reentry.policy.json`

And keep these truths separate:

- runner-up status versus hard exclusion,
- re-entry versus replacement,
- visibility drift versus solved task-fit gaps,
- and popularity/search order versus decision authority.
