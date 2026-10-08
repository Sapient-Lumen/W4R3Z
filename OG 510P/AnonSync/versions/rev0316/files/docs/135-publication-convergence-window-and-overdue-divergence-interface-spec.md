# Publication convergence window and overdue-divergence interface spec

## Purpose

The archive now has:

- reviewed publication changes
- current subject × member publication truth
- durable mutation ledgers with observation-gap rows
- per-cell causality explanation
- future-arrival simulation for standing policy edits

What still remained under-specified was the temporal operator question that appears after a change is applied:

> for this specific pending gap, is the strongest honest verdict that the member is still within the expected convergence window, blocked by a prerequisite, overdue for fresh evidence, or impossible under the current winning policy state?

Without one explicit convergence object, the product will still recreate troubleshooting folklore in a friendlier costume.
`Applied` becomes `done`, `announced` becomes `they should have it`, and silence becomes either false comfort or vague panic.

This document defines the interface contract for honest convergence windows and overdue-divergence classification.

## Core rule

Every unresolved post-change observation gap must be renderable as one first-class **convergence window** object that states:

1. which reviewed mutation or arrival state is waiting to converge
2. what the strongest honest current verdict is
3. which evidence supports that verdict
4. which evidence is missing or stale
5. what the product must not claim yet

A convergence window is not a fake ETA card.
It is an honesty object for pending distributed state.

## Why this needs its own spec

Current Resilio docs still say synchronization starts immediately when change detection happens, while separate troubleshooting pages describe blocked trackers, relay fallback, and source-peer absence.
That is honest documentation.
But it still leaves the operator doing the synthesis.

AnonSync should refuse that synthesis burden.
A pending gap should not require reconstructing whether the system is merely waiting, missing a source, blocked by route policy, or stale because no one has observed the target recently enough.

## Public objects

### Convergence window

A durable inspection object for one unresolved post-change gap.

Suggested fields:

- `convergence_window_id`
- `subject_ref`
- `member_ref`
- `origin_kind` (`publication-mutation`, `arrival-claim`, `member-policy-apply`, `temporary-lease-expiry`, `withdrawal`, `superseding-mutation`)
- `origin_ref`
- `strongest_verdict` (`expected-delay`, `blocked-local-prerequisite`, `blocked-route-or-liveness`, `waiting-for-source`, `overdue-divergence`, `impossible-under-current-policy`, `superseded`)
- `expectation_class` (`ordinary`, `guarded`, `fragile`, `stale-evidence`)
- `supporting_evidence_refs[]`
- `missing_evidence_refs[]`
- `blocked_claims[]`
- `opened_at`
- `last_recomputed_at`

### Convergence evidence row

One fact that strengthens or weakens the current verdict.

Suggested fields:

- `convergence_evidence_row_id`
- `kind` (`announcement`, `member-receipt`, `liveness`, `route`, `source-availability`, `local-prerequisite`, `policy-eligibility`, `supersession`)
- `state` (`fresh-positive`, `fresh-negative`, `stale-positive`, `stale-negative`, `missing`)
- `summary`
- `source_ref` nullable
- `affects_verdict` boolean

### Overdue divergence ticket

A durable escalation object created when the strongest honest verdict becomes `overdue-divergence`.

Suggested fields:

- `overdue_divergence_ticket_id`
- `convergence_window_ref`
- `promoted_at`
- `promotion_reason`
- `recommended_review_ref` nullable
- `suppresses_auto-reannounce` boolean

### Convergence receipt

An exportable snapshot proving how the system classified the gap at one moment.

Suggested fields:

- `convergence_receipt_id`
- `convergence_window_ref`
- `generated_for_actor_ref`
- `created_at`
- `strongest_verdict`
- `evidence_hash`

## Fixed inspection order

Every convergence-window surface should preserve this order:

1. **Gap summary**
2. **Strongest honest verdict now**
3. **Fresh supporting evidence**
4. **Missing or stale evidence**
5. **What the product must not claim yet**
6. **Promotion and supersession truth**
7. **Next honest review boundary**

### 1) Gap summary

This section should state plainly:

- which `(subject, member)` outcome is pending
- which mutation, arrival, or expiry created the gap
- whether the gap concerns visibility, role, path readiness, byte availability, or withdrawal observation
- how long the current window has been open

### 2) Strongest honest verdict now

This is the center of the surface.
It should render exactly one current verdict, chosen from the stable vocabulary, with a short operator explanation such as:

- `expected-delay — announcement exists and member liveness is fresh, but no observation receipt yet`
- `blocked-local-prerequisite — member observed the subject, but role-first arrival review is still incomplete`
- `blocked-route-or-liveness — no fresh path or liveness evidence supports near-term observation`
- `waiting-for-source — publication is visible, but bytes cannot settle because no eligible source is currently online`
- `overdue-divergence — stronger evidence suggests the member should have observed the change by now`
- `impossible-under-current-policy — current policy now says this member should not converge to the pending target state`
- `superseded — a later mutation replaced the pending target before settlement completed`

### 3) Fresh supporting evidence

This section should keep the strongest recent facts adjacent, for example:

- member announced and reachable recently
- route probe succeeded recently
- source peer confirmed eligible and online
- member opened the new mutation or arrival review

### 4) Missing or stale evidence

This section should publish the weakest links plainly, for example:

- no recent liveness proof
- no eligible source currently online
- route evidence stale beyond the current confidence window
- local prerequisite still blocked on that member
- superseding policy change may have changed the target state

### 5) What the product must not claim yet

This section is mandatory.
Examples:

- expected-delay does not prove imminent convergence
- route freshness does not prove byte settlement
- observed policy mutation does not prove retained-byte cleanup
- no recent evidence does not prove failure by itself
- overdue-divergence does not prove malicious refusal or data loss

### 6) Promotion and supersession truth

This section should say whether the current window:

- is still in ordinary expectation
- promoted into overdue-divergence and why
- was cleared by later observation
- was replaced by a superseding mutation or policy change

### 7) Next honest review boundary

Examples:

- `Keep waiting`
- `Open wait-vs-intervene decision sheet`
- `Inspect route evidence`
- `Inspect source availability`
- `Open superseding mutation`
- `Export convergence receipt`

## Public rules

### Rule 1 — no fake ETAs

The product may classify expectation windows and confidence, but must not promise exact convergence times it cannot know.

### Rule 2 — silence is not one thing

A pending gap must distinguish missing announcement, route/liveness weakness, source absence, blocked local prerequisites, and policy impossibility.

### Rule 3 — overdue is evidence-based, not a timer alone

Promotion to `overdue-divergence` should require timer plus current evidence context, not just elapsed wall-clock time.

### Rule 4 — supersession remains visible

A later change may cancel the practical importance of a pending gap, but the original gap and its closure reason must remain inspectable.

### Rule 5 — convergence truth does not replace causality or recall

This surface explains pending distributed settlement.
It does not replace arrival causality explanation or retained-copy recall review.

## Dense row contract

A dense convergence row should preserve these labels in this order:

- `Cell`
- `Pending target`
- `Verdict now`
- `Fresh evidence`
- `Missing evidence`
- `What not proven`
- `Next`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one page:

- what exact state is still pending for this `(subject, member)` pair
- whether the strongest honest verdict is expected, blocked, overdue, impossible, or superseded
- which fresh evidence supports that verdict
- which evidence is missing or stale
- what the product still must not claim yet
- which review boundary or follow-up action is justified next
