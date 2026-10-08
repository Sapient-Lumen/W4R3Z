# Capability availability page — feature, seat, surface, and subject preconditions interface spec

## Purpose

The archive already had release-line, install-target, and entitlement-cliff guidance.
What it still lacked was one ordinary page for the simpler question:

> can this seat perform this capability here and now, on this surface, for this subject, and what exact missing ingredient blocks it if not?

Current official Resilio docs make this seam concrete.
They still repeat availability notes across Selective Sync, My Devices, User Management, single-file sharing, folder classes, and local-share pages.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Capability availability** page for every capability family that can materially differ by line, entitlement, host role, surface, or subject class.

The page exists to answer five things in one place:

1. what capability is being asked for
2. which seat, surface, and subject are in scope
3. whether the capability is currently available
4. which exact prerequisites are missing if not
5. which next action is least misleading

## Fixed page order

1. **Availability verdict**
2. **Seat / surface / subject basis**
3. **Missing prerequisites**
4. **Fallback and non-equivalence**
5. **Safe next actions**

### 1) Availability verdict

Show:

- `capability_availability_page_id`
- capability family
- seat and surface in scope
- subject in scope if applicable
- current `availability_verdict` (`available`, `available-with-review`, `blocked-by-line`, `blocked-by-entitlement`, `blocked-by-host-role`, `blocked-by-surface`, `blocked-by-subject-class`, `blocked-by-seat-rights`, `unknown`)
- strongest honest summary
- last evaluation time

The operator must be able to answer:

> can I do this here right now?

### 2) Seat / surface / subject basis

Show rows for:

- release line / edition family
- entitlement posture
- host role
- current UI surface
- subject family or folder class
- current seat right ceiling

Every row must show provenance and confidence.
The page must not let a missing button or remembered folklore impersonate the real basis.

### 3) Missing prerequisites

If the capability is not currently available, show the exact blockers in descending order of force:

- hard support block
- entitlement deficiency
- wrong surface
- wrong subject class
- insufficient seat rights
- currently missing runtime state

This section must answer:

> what exact condition must change before this capability becomes honest to offer?

### 4) Fallback and non-equivalence

Show:

- nearest weaker action that is truly available
- what that fallback does **not** preserve
- whether the fallback is only observational, local-only, or destructive
- whether leaving the current surface is required

The page must not imply that an approximate workaround is equivalent to the missing capability.

### 5) Safe next actions

Actions may include:

- `Open entitlement basis`
- `Open gated action`
- `Switch to eligible surface`
- `Open subject-class review`
- `Request stronger seat rights`
- `Accept unavailable state`

Each action must preview whether it changes capability truth or only changes context.

## Public object

### Capability availability page

Fields:

- `capability_availability_page_id`
- `capability_family`
- `seat_ref`
- `surface_ref`
- `subject_ref` nullable
- `availability_verdict`
- `basis_rows[]`
- `blocking_rules[]`
- `weaker_fallbacks[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. capability
2. seat / surface
3. strongest blocker or verdict
4. nearest honest fallback
5. next safest action

Example:

```text
On-the-fly permission edit     laptop-02 / web      blocked-by-subject-class     recreate grant epoch     Open gated action
```

## Non-goals

This page does **not** replace entitlement events, cohort cutover planning, or full grant-mutation review.
It proves only **whether a specific capability is genuinely available in this context right now**.
