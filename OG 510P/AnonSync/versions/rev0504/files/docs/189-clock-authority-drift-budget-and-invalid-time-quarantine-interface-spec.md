# Clock authority, drift budget, and invalid-time quarantine interface spec

## Purpose

The archive already had chronology, rename cost, byte-witness, and change-detection language.
What it still lacked was one explicit interface contract for a simpler but more corrosive lie:

> when the product says `latest`, `newer`, or even just shows an empty folder, what page proves whether time itself is trustworthy enough for chronology-dependent decisions?

Current official Resilio docs make this seam more concrete than an abstract `clock drift happens` warning would.
They still say file freshness is decided by comparing modification times after conversion to GMT, that any peer with invalid local time or timezone can exceed a 600-second tolerance and trigger an Invalid Time warning, and that mobile devices may show an empty file list while this is unresolved.
The same docs still treat correction mainly as an out-of-band system-time repair followed by a Sync restart.

That is candid support guidance.
It is still not a good public chronology contract.

## Core decision

AnonSync should make **clock authority** and **chronology confidence** first-class.

Every subject whose merge, overwrite, conflict, restore, or witness decisions depend on timestamps must always declare:

- the active clock-confidence class
- which peers are trusted as chronology participants
- the tolerated drift budget
- whether timezone uncertainty versus raw clock skew is the problem
- which recent decisions are now suspect because chronology confidence degraded
- what operator action would restore confidence

If an operator still has to infer chronology failure from an empty mobile list, a generic warning, or surprise `older wins` outcomes, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- chronology decisions can silently rely on peer clocks that the product does not continuously justify
- timezone misconfiguration is operationally equivalent to content-freshness ambiguity
- a bad clock can degrade visibility itself, not merely ordering confidence
- `latest wins` is unsafe language when clock confidence is impaired
- recovery guidance that lives outside the sync surface makes chronology feel incidental when it is actually foundational

AnonSync should therefore keep one stronger rule:

> chronology confidence, drift budget, and quorum trust must be shown as part of steady-state truth, not only after the system has already made a dubious freshness decision.

## Fixed review order

Every non-trivial time-related warning or chronology-sensitive mutation should render the same sections in the same order:

1. **Clock confidence now**
2. **Peer drift map**
3. **Affected chronology decisions**
4. **Repair and revalidation receipt**

### 1) Clock confidence now

This section should show:

- whether the subject is `trusted`, `guarded`, `quarantined`, or `clock-blind`
- the current allowed drift budget
- whether the problem is timezone labeling, raw wall-clock skew, monotonic rollback, or unknown
- whether freshness claims are still safe to honor automatically

The operator must be able to answer: **can I trust timestamp ordering right now?**

### 2) Peer drift map

This section should show:

- peers participating in chronology decisions
- each peer's observed drift from quorum
- timezone confidence
- last validated time sample
- whether the peer is allowed to publish chronology-affecting mutations while degraded

The operator must be able to answer: **which peer is distorting time truth, and by how much?**

### 3) Affected chronology decisions

This section should show:

- recent mutations whose ordering confidence is now suspect
- whether restores, conflict picks, or witness promotion should be held
- whether directory visibility is suppressed only as a safety posture or because state itself is unavailable
- whether existing receipts are still trustworthy

The operator must be able to answer: **what decisions should I distrust until time is fixed?**

### 4) Repair and revalidation receipt

This section should show only honest next actions, such as:

- `Revalidate timezone and wall clock`
- `Exclude peer from chronology decisions temporarily`
- `Hold overwrite/restore actions until revalidated`
- `Accept guarded mode with manual review`
- `Re-run chronology validation now`

The receipt must record both the repair and the post-repair confidence class.

## Public objects

### Clock confidence report

Fields:

- `clock_confidence_report_id`
- `subject_ref`
- `confidence_class` (`trusted`, `guarded`, `quarantined`, `clock-blind`)
- `drift_budget_seconds`
- `time_basis` (`wall-clock`, `wall-clock+timezone`, `mixed`, `unknown`)
- `participants[]`
- `suspect_decisions[]`
- `generated_at`

### Chronology quarantine review

Fields:

- `chronology_quarantine_review_id`
- `report_ref`
- `target_peers[]`
- `requested_action` (`repair-time`, `quarantine-peer`, `hold-chronology-actions`, `accept-guarded-mode`)
- `effects[]`
- `generated_at`
- `expires_at` nullable

### Clock revalidation receipt

Fields:

- `clock_revalidation_receipt_id`
- `review_ref`
- `validated_peers[]`
- `pre_confidence_class`
- `post_confidence_class`
- `suspect_decisions_cleared[]`
- `completed_at`

## Compact row contract

A truthful compact row should keep these facts in stable order:

1. subject or peer
2. clock confidence
3. worst drift
4. chronology effect
5. next honest action

Example:

```text
peer/laptop-east     quarantined     11m 42s drift     latest-write unsafe     Revalidate time and timezone
```

The product should not reduce that to `Invalid time` with no visible consequence model.

## CLI implications

A minimum public surface should include:

```text
anonsync clock show --subject <subject>
anonsync clock peers --subject <subject>
anonsync clock quarantine plan --peer <peer>
anonsync clock quarantine apply <chronology_quarantine_review_id>
anonsync clock revalidate run --peer <peer>
anonsync clock receipt show <clock_revalidation_receipt_id>
```

The CLI should let an operator prove whether timestamp ordering is safe before a merge, restore, or overwrite relies on it.
