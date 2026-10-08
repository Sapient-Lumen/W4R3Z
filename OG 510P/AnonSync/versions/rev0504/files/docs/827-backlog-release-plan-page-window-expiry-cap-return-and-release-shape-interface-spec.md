# Backlog release plan page — window expiry, cap return, and release-shape interface spec

## Purpose

The archive already has quiet-window, residual-activity, and resume-catch-up pages.
What it still lacked was one ordinary page for the question:

> when this quiet window ends or this subject is resumed, what cap returns, what backlog classes are waiting, and what release shape should the operator expect before claiming that catch-up is now predictable?

Current official Resilio docs make this seam concrete.
They still say empty schedule cells mean full bandwidth, that unchecked upload or download rules imply full bandwidth in that direction, and that priority and queue behavior have important caveats.
That is useful truth.
It should not remain split across scheduler and priority help.

## Core decision

AnonSync must expose one first-class **Backlog release plan** page whenever a subject, seat, or cohort is about to leave a quiet, throttled, or speed-zero posture.

The page exists to answer five things in one place:

1. which trigger is ending the quiet posture
2. what transfer cap actually returns next
3. which backlog classes are eligible to move first
4. what could make the first wave bursty or misleading
5. what sentence is honest before release actually happens

## Fixed page order

1. **Current release verdict**
2. **Release trigger and returned cap**
3. **Eligible backlog classes**
4. **Release-shape risks and exceptions**
5. **Actions and receipts**

### 1) Current release verdict

Show:

- `backlog_release_plan_page_id`
- scope (`seat`, `subject`, or `cohort`)
- current `release_class` (`scheduled-expiry`, `manual-resume`, `cap-widening`, `quiet-successor`, `unknown`)
- strongest honest summary
- current quiet posture and next transition time

The operator must be able to answer:

> what kind of release event is about to happen?

### 2) Release trigger and returned cap

Show:

- exact release trigger
- returned send cap
- returned receive cap
- whether `full bandwidth` is literal, inherited, or only the absence of a narrower rule
- whether local and LAN peers share the same returned cap or still differ
- whether release is immediate or staged

The operator must be able to answer:

> what bandwidth posture comes back the moment quiet ends?

### 3) Eligible backlog classes

Show buckets such as:

- blocked downloads that become eligible now
- blocked uploads that become eligible now
- queued work that remains capped or deprioritized
- residual non-byte events that already moved during quiet and therefore do not belong to the first byte wave
- no meaningful backlog expected

This section must make it ordinary to answer:

> what work is actually waiting to flood back, and what work is not part of that wave?

### 4) Release-shape risks and exceptions

This section is mandatory whenever any cap returns from zero or near-zero.
Show:

- whether authoritative order depends on a separate priority review
- queue-cap limits that keep some waiting files outside the active ordered set
- transfer-class exceptions, such as non-splittable work that may not obey strict priority
- queue-rebuild or error conditions that could reshuffle the first wave
- reasons that visible queue order may not be authoritative
- release-shape verdict (`gentle`, `moderate`, `bursty`, `order-provisional`, `unknown`)

The page must answer:

> how much trust should I place in my current story about the first catch-up wave?

### 5) Actions and receipts

Actions may include:

- `Release now`
- `Delay release`
- `Keep cap narrow for first wave`
- `Open backlog order review`
- `Open quiet window`
- `Open resume catch-up`

Receipts must record trigger, returned cap, release-shape verdict, and any surviving uncertainty.

## Public object

### Backlog release plan page

Fields:

- `backlog_release_plan_page_id`
- `scope_ref`
- `release_class`
- `current_quiet_posture`
- `release_trigger`
- `returned_send_cap`
- `returned_receive_cap`
- `eligible_backlog_rows[]`
- `release_shape_risk_rows[]`
- `release_shape_verdict`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. release class
3. returned cap
4. strongest release-shape warning
5. next action

Example:

```text
Project Alpha     scheduled-expiry     full send / full receive     order provisional beyond active queue     Open backlog order review
```

## Non-goals

This page does **not** promise that release will clear the backlog quickly or conflict-free.
It proves only the current **release trigger, returned cap, and release-shape truth**.
