# Backlog release timeline page — quiet expiry, preemption, and queue-rebuild lineage interface spec

## Purpose

The archive already has quiet-break and catch-up pages.
What it still lacked was one ordinary timeline for the question:

> after quiet ended, which event actually shaped the release wave — expiry, manual resume, cap widening, higher-priority arrival, queue rebuild, or later aftershock?

Current official Resilio docs make this seam concrete.
They still say quiet windows can end into full bandwidth, higher-priority arrivals can suspend lower-priority downloads, and queue rebuilds can happen when the active queue changes.
That is useful truth.
It should not be reconstructed from vague history rows.

## Core decision

AnonSync must expose one first-class **Backlog release timeline** page whenever the operator needs to understand how a resumed catch-up wave evolved over time.

The page exists to answer five things in one place:

1. what release event opened the wave
2. what cap changes followed
3. what preemption or queue-rebuild events materially changed the order story
4. which events were first-wave causes versus later aftershocks
5. what statement about the backlog wave remains durable now

## Fixed page order

1. **Timeline verdict**
2. **Opening event cluster**
3. **Cap and order mutation sequence**
4. **Aftershocks and stabilizing evidence**
5. **Actions and receipts**

### 1) Timeline verdict

Show:

- `backlog_release_timeline_page_id`
- scope
- current `timeline_verdict` (`single-clean-release`, `release-with-preemption`, `release-with-rebuild`, `multi-wave-release`, `still-unsettled`, `unknown`)
- strongest honest summary
- current stabilization status

### 2) Opening event cluster

Show the earliest causally relevant events such as:

- quiet-window expiry
- manual resume
- cap widening
- release token acceptance
- source-return event

Each event row should show:

- exact time
- event type
- actor or authority class
- immediate effect on cap or eligibility
- whether it counts as the opening release event

### 3) Cap and order mutation sequence

Show later rows such as:

- priority basis becoming active
- higher-priority arrival suspending lower-priority work
- queue rebuild start and end
- visible-vs-actual order mismatch becoming relevant
- manual cap narrowing after initial flood concern

This section must make it ordinary to answer:

> which later events changed the simple story I first told myself about the release wave?

### 4) Aftershocks and stabilizing evidence

Show:

- later distortions that no longer define the main release story
- evidence that order has stabilized or remains provisional
- rows that narrowed or widened flood-risk language
- current strongest safe sentence and one forbidden stronger sentence

### 5) Actions and receipts

Actions may include:

- `Acknowledge stabilized release`
- `Open backlog order review`
- `Narrow cap now`
- `Re-enter quiet review`
- `Emit release receipt`

Receipts must preserve opening event, major reshapers, stabilization state, and claim boundary.

## Public object

### Backlog release timeline page

Fields:

- `backlog_release_timeline_page_id`
- `scope_ref`
- `timeline_verdict`
- `opening_event_rows[]`
- `mutation_rows[]`
- `aftershock_rows[]`
- `stabilization_verdict`
- `safe_sentence`
- `forbidden_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. timeline verdict
3. opening event
4. strongest reshaper
5. stabilization state

Example:

```text
Project Alpha     release-with-rebuild     scheduled-expiry at 18:00     queue rebuild after higher-priority arrival     still-unsettled
```

## Non-goals

This page does **not** replace current queue state, quiet state, or source sufficiency pages.
It proves only the **lineage of the release wave** and the strongest durable story about how it changed.
