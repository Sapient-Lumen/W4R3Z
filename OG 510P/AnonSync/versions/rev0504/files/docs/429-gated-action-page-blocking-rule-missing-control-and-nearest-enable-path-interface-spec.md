# Gated action page — blocking rule, missing control, and nearest enable path interface spec

## Purpose

The archive already had several destructive-review and subject-class pages.
What it still lacked was one ordinary page for the simpler question:

> why is this action missing, disabled, or absent on this page right now, and what exact rule is doing the blocking?

Current official Resilio docs make this seam concrete.
They still spread action availability across version notes, Pro-vs-Free comparisons, folder-class differences, surface-specific limitations, and troubleshooting pages about lost licenses or unsupported server seats.
That is useful truth.
It should not remain an interpretive exercise.

## Core decision

AnonSync must expose one first-class **Gated action** page whenever an action of consequence is missing, disabled, downgraded, or replaced by a weaker fallback.

The page exists to answer five things in one place:

1. what action the operator expected
2. whether the action is truly blocked or merely unavailable on this surface
3. which exact gate rules caused the result
4. what the nearest enable path is
5. which shortcuts are unsafe or deceptive

## Fixed page order

1. **Requested action verdict**
2. **Gate stack**
3. **Nearest enable path**
4. **Unsafe shortcuts and false equivalences**
5. **Safe next actions**

### 1) Requested action verdict

Show:

- `gated_action_page_id`
- requested action
- origin surface
- seat and subject scope
- current `gate_verdict` (`available-here`, `available-elsewhere`, `blocked-by-rule`, `missing-because-weaker-surface`, `hidden-because-unsafe`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> is this action really unavailable, or am I just on the wrong surface or wrong subject?

### 2) Gate stack

Show the active rules in descending order of force:

- release-line gate
- entitlement gate
- host-role gate
- current-surface gate
- subject-class gate
- seat-rights gate
- current runtime-state gate

Every gate row must say whether it is `hard`, `soft`, or `contextual`, and whether changing context would remove it.

### 3) Nearest enable path

Show the shortest honest sequence that would make the action available, for example:

- move to a richer surface
- upgrade release line
- restore entitlement
- switch to an eligible subject class
- obtain stronger seat rights
- wait for runtime state to settle

The page must distinguish `one-step enable` from `requires new epoch or recreation`.

### 4) Unsafe shortcuts and false equivalences

Show:

- tempting fallback that is not actually equivalent
- whether the missing action would widen rights, change chronology, or mutate subject class
- whether hidden controls were removed for safety rather than simplicity

The page must not reduce all blocked actions to `upgrade to unlock`.

### 5) Safe next actions

Actions may include:

- `Open capability availability`
- `Open entitlement basis`
- `Open subject-class chooser`
- `Switch surface`
- `Request stronger rights`
- `Accept action unavailable`

Each action must preview which gate it addresses.

## Public object

### Gated action page

Fields:

- `gated_action_page_id`
- `requested_action`
- `origin_surface_ref`
- `seat_ref`
- `subject_ref` nullable
- `gate_verdict`
- `gate_rows[]`
- `nearest_enable_path[]`
- `unsafe_shortcuts[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. action
2. origin surface
3. strongest gate
4. nearest enable path
5. next safest action

Example:

```text
Edit member rights     browser summary pane     blocked-by-subject-class     recreate as advanced-governed subject     Open subject-class chooser
```

## Non-goals

This page does **not** replace entitlement ownership, install-target support, or full migration review.
It proves only **why an expected action is absent or gated in the current context**.
