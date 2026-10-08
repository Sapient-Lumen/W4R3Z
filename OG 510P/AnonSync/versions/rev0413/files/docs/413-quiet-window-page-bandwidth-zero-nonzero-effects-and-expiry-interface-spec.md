# Quiet window page — bandwidth-zero, nonzero-effects, and expiry interface spec

## Purpose

`192` and `271` already established the semantic contract for pause and rate policy.
What this tranche still lacked was one denser ordinary page for the schedule-window question:

> if this subject or seat is in a quiet window right now, what exactly is zero, what still happens anyway, when does the window end, and what semantic residue survives during it?

Current official Resilio docs make this seam concrete.
They still say scheduled `Paused` makes upload and download speed zero, yet zero-sized files and deletions still sync, new files are still rescanned and indexed, and some peers may still upload to non-paused peers while not downloading.
That is useful truth.
It should not be a footnote.

## Core decision

AnonSync must expose one first-class **Quiet window** page whenever a schedule, temporary cap, or pause-like posture makes transfer look absent while some signal families still survive.

The page exists to answer five things in one place:

1. which motion classes are forced to zero
2. which nonzero effects still survive inside the window
3. whether the posture is manual, scheduled, inherited, or emergency
4. when the current window expires or rolls to the next window
5. what resume will and will not change

## Fixed page order

1. **Current quiet-window verdict**
2. **Signal matrix now**
3. **Origin and expiry**
4. **Surviving semantic effects**
5. **Resume and mutation actions**

### 1) Current quiet-window verdict

Show:

- `quiet_window_page_id`
- scope (`seat` or `subject`)
- current `quiet_window_class` (`none`, `manual-pause`, `scheduled-zero`, `throttled`, `inherited`, `emergency`, `unknown`)
- strongest honest summary
- time entered and next transition time

The operator must be able to answer:

> what kind of quiet posture is in force right now?

### 2) Signal matrix now

Show explicit rows for:

- outbound bytes
- inbound bytes
- deletions
- namespace/indexing
- announcement/publication
- peer-serving to already-eligible peers
- source-material fetch on this seat

Each row must render `allowed`, `blocked`, `limited`, or `unknown`, with policy owner.

The page must make it ordinary to answer:

> what exactly is still happening even though the window sounds quiet?

### 3) Origin and expiry

Show:

- policy origin (`manual`, `schedule`, `standing-seat-policy`, `subject-override`, `emergency-guard`)
- current window start
- current window end or reconsideration trigger
- next scheduled posture
- whether the posture repeats or is one-off

### 4) Surviving semantic effects

This section is mandatory whenever any transfer lane is zero or near-zero.
Show:

- whether delete waves still propagate
- whether local discovery/indexing still advances
- whether queue/backlog can still grow
- whether other peers may still observe this seat as serving or absent
- whether new change announcements can outpace future fetch once the window lifts

This section must not let `paused` imply semantic freeze if the truth is narrower.

### 5) Resume and mutation actions

Actions may include:

- `End window now`
- `Edit schedule`
- `Convert to stricter freeze review`
- `Open motion basis`
- `Open resume catch-up`
- `Keep current window`

Each action must preview surviving-effect deltas and observer deltas.

## Public object

### Quiet window page

Fields:

- `quiet_window_page_id`
- `scope_ref`
- `quiet_window_class`
- `origin_class`
- `signal_matrix_rows[]`
- `surviving_effect_rows[]`
- `entered_at`
- `expires_at` nullable
- `next_posture` nullable
- `repeat_rule` nullable
- `resume_preview`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. quiet class
3. dominant zeroed lane
4. strongest surviving effect
5. next transition

Example:

```text
Project Alpha     scheduled-zero     inbound/outbound bytes     deletions + indexing still alive     18:00 local
```

## Non-goals

This page does **not** prove freshness, route health, or bottleneck cause by itself.
It proves only the exact **quiet-window semantics** now in force.
