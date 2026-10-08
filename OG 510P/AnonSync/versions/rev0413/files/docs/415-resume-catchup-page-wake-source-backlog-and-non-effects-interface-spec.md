# Resume catch-up page — wake, source, backlog, and non-effects interface spec

## Purpose

The archive already has background delivery, suspended-seat, and freshness pages.
What it still lacked was one ordinary page for the post-quiet question:

> when this seat wakes, regains source peers, exits a quiet window, or returns from runtime absence, what exactly will catch up, what risks stay, and what definitely will not change just because we resumed?

Current official Resilio docs make this seam concrete.
They still say Android Auto Sleep wakes on interval, iOS lacks background sync, restarting can trigger re-index, source devices must actually be online, and some warned files may still remain unavailable because no peer retains full bytes anymore.
That is useful truth.
It should not remain split across power, background, and warning pages.

## Core decision

AnonSync must expose one first-class **Resume catch-up** page whenever a subject or seat is about to re-enter active participation after sleep, stop, quiet window, forbidden network, or source-return gap.

The page exists to answer five things in one place:

1. what exact event is driving resume
2. what backlog classes should catch up next
3. what source/runtime preconditions still must be true
4. what replay, overwrite, or ghost-risk remains
5. what will definitely *not* be fixed merely by resume

## Fixed page order

1. **Current resume verdict**
2. **Resume trigger and prerequisites**
3. **Expected catch-up set**
4. **Residual risks and non-effects**
5. **Actions and receipts**

### 1) Current resume verdict

Show:

- `resume_catchup_page_id`
- scope (`seat` or `subject`)
- current `resume_class` (`wake-interval`, `manual-resume`, `runtime-restart`, `source-return`, `network-return`, `none`, `unknown`)
- strongest honest summary
- most recent absence interval and next wake if scheduled

### 2) Resume trigger and prerequisites

Show:

- exact trigger that caused or will cause resume
- whether full source peers are currently present
- whether route eligibility already exists
- whether runtime presence is stable or merely momentary
- whether re-index / re-hash / requeue is expected before transfer

The operator must be able to answer:

> what must already be true before catch-up can honestly begin?

### 3) Expected catch-up set

Show buckets such as:

- pending announcements likely to land now
- locally detected but unpublished changes likely to publish now
- downloads that were policy-suppressed and now become eligible
- no catch-up expected because the quiet period accumulated nothing
- catch-up impossible because no live full source exists

### 4) Residual risks and non-effects

This section must explicitly call out:

- overwrite or chronology risk from offline local edits
- ghost-file / announced-but-no-source risk
- route or source absence that resume does not solve
- policy limits that remain in force after wake
- observer or disclosure posture that resume alone does not change

The page must answer:

> what will still remain false even after we resume?

### 5) Actions and receipts

Actions may include:

- `Resume now`
- `Wait for next wake`
- `Verify source peers`
- `Open motion basis`
- `Open bottleneck cause`
- `Repair route`
- `Run reviewed rescan`

Receipts must record the trigger, resulting motion class, and any residual risk kept open.

## Public object

### Resume catch-up page

Fields:

- `resume_catchup_page_id`
- `scope_ref`
- `resume_class`
- `absence_interval`
- `next_wake_at` nullable
- `prerequisite_rows[]`
- `expected_catchup_rows[]`
- `residual_risk_rows[]`
- `non_effect_rows[]`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. resume class
3. catch-up expectation
4. strongest residual risk
5. next action

Example:

```text
Mobile seat     wake-interval     queued announcements should publish     source may still be absent for two files     Verify source peers
```

## Non-goals

This page does **not** guarantee that resumed work will finish quickly or conflict-free.
It proves only the current **resume and catch-up truth**, including what resume definitely does not solve.
