# Backlog order review page — priority, caps, exceptions, and flood-risk interface spec

## Purpose

`284` already established download-queue truth.
What this tranche still lacked was one denser ordinary page for the post-quiet question:

> now that backlog release is imminent or active, what order is authoritative enough to rely on, what exceptions distort it, and how risky is it to talk as though the catch-up wave is neatly controlled?

Current official Resilio docs make this seam concrete.
They still say priority can come from share or global defaults, that only the active queue is prioritized up to 50,000 files, that some internal exceptions remain, that non-splittable transfers do not fully obey strict prioritization, and that the visible queue may still look alphabetical.
That is useful truth.
It should not be a memory test.

## Core decision

AnonSync must expose one first-class **Backlog order review** page whenever a resumed backlog is about to move or is already moving under a claimed order policy.

The page exists to answer five things in one place:

1. what order policy is currently in force
2. which source is authoritative for actual execution order
3. what cap or active-window limits narrow that order's jurisdiction
4. what exceptions or rebuilds make the order provisional
5. how strong a post-quiet catch-up sentence is still honest

## Fixed page order

1. **Current order verdict**
2. **Authoritative order source**
3. **Active-window and cap scope**
4. **Exceptions, rebuilds, and flood risk**
5. **Actions and receipts**

### 1) Current order verdict

Show:

- `backlog_order_review_page_id`
- scope
- current `order_verdict` (`natural`, `priority-active`, `priority-partial`, `order-provisional`, `rebuild-active`, `unknown`)
- strongest honest summary
- whether the current claim is inherited, pinned, or temporary

### 2) Authoritative order source

Show:

- actual order basis (`none`, `mtime-newer-first`, `mtime-older-first`, `size-larger-first`, `size-smaller-first`, `other-approved-basis`)
- policy origin (`standing-default`, `subject-override`, `temporary-review`, `implicit-natural-order`)
- whether visible list order is authoritative, cosmetic, or mixed
- whether the current order can be trusted for the next wave only or for the whole backlog

The operator must be able to answer:

> what order should I actually believe right now?

### 3) Active-window and cap scope

Show:

- active queue size or range where ordering is actually enforced
- waiting work outside that active set
- returned send/receive caps that still affect effective release order
- whether work outside the active set can leap in later and preempt

The operator must be able to answer:

> how much of the backlog is actually governed by the advertised order policy right now?

### 4) Exceptions, rebuilds, and flood risk

Show:

- current preemption behavior
- transfer classes that may refuse strict reprioritization
- queue rebuild triggers currently active or likely
- error, size-change, or policy-change conditions that can reshuffle execution order
- flood-risk verdict (`low`, `moderate`, `high`, `high but bounded`, `order-provisional`, `unknown`)
- strongest safe sentence and one forbidden stronger sentence

The page must answer:

> how neat or messy is this resumed catch-up wave really?

### 5) Actions and receipts

Actions may include:

- `Accept current order truth`
- `Open backlog release plan`
- `Narrow first-wave cap`
- `Pin explicit order`
- `Return to natural order`
- `Delay release until rebuild settles`

Receipts must record authoritative order, active-window limit, distortion factors, and flood-risk verdict.

## Public object

### Backlog order review page

Fields:

- `backlog_order_review_page_id`
- `scope_ref`
- `order_verdict`
- `authoritative_order_basis`
- `policy_origin`
- `visible_order_authority`
- `active_window_rows[]`
- `exception_rows[]`
- `flood_risk_verdict`
- `safe_sentence`
- `forbidden_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. order verdict
3. authoritative-order source
4. strongest distortion or risk
5. next action

Example:

```text
Media backlog     priority-partial     mtime-newer-first from subject override     visible list cosmetic; non-splittable exception active     Delay release until rebuild settles
```

## Non-goals

This page does **not** prove route health, source sufficiency, or chronology safety by itself.
It proves only current **post-quiet order truth and flood-risk honesty**.
