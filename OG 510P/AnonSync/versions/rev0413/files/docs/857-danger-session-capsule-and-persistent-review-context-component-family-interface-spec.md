# Danger session capsule and persistent review-context component family interface spec

## Purpose

The archive already has destructive review shell, loss matrix, salvage ladder, approval barrier, and local-web danger-surface pages.
What it still lacked was the persistent context object that keeps those pages tied together as one dangerous workflow instead of five adjacent screens.

This component family exists to answer:

> while I move between trust review, salvage export, destructive barrier, and receipt pages, what dangerous act is still in play, on what endpoint, with what freshness, and with what current rescue ceiling?

## Core decision

AnonSync must treat the **danger session capsule** and **persistent review-context rail** as reusable semantic components.
Any dangerous workflow that spans more than one page must keep these components alive.
No projection may make the operator recover dangerous context from browser history, page titles, or remembered earlier warnings.

## Component 1: Danger session capsule

The capsule is the compact always-visible summary.
It may be a sticky header, sticky footer, side badge, or pinned floating card depending on projection.
It must remain visible on:

- destructive review shell
- trust bootstrap review
- salvage export
- destructive approval barrier
- destructive execution ticket
- destructive receipt

### Required capsule fields

The capsule must preserve this order:

1. **endpoint watermark**
2. **acting seat**
3. **destructive action label**
4. **trust grade**
5. **basis freshness**
6. **at-risk work summary**
7. **best rescue rung**
8. **next required step**

### Allowed compact verdicts

The capsule may use bounded summary labels such as:

- `review only`
- `trust unlock required`
- `export recommended`
- `barrier ready`
- `ticket active`
- `stale re-review required`
- `receipt current`

It must not reduce the session to a generic `warning` or `danger` badge.

## Component 2: Persistent review-context rail

The rail is the expanded lineage/context region.
It may render as a side rail on wide layouts or a collapsible chronology strip on narrow ones.

### Required rail fields

The rail must preserve this order:

1. **current shell/ref**
2. **loss matrix ref**
3. **salvage ladder ref**
4. **trust review ref if any**
5. **salvage export receipt refs[]**
6. **current barrier ref**
7. **current execution ticket ref**
8. **latest destructive receipt ref**

### Interaction rules

- clicking any ref opens the owning page without changing the current action identity
- stale refs must be visibly stale rather than silently replaced
- superseded objects must remain inspectable from the rail
- rail order is chronological and semantic, not alphabetical

## Cross-component rules

The capsule and rail must cross-link.
The capsule should tell the operator what state the dangerous session is in now.
The rail should tell the operator why that state is honest and what prior reviewed objects support it.

## Narrow-width rule

A narrow layout may collapse the rail behind one disclosure.
It may not hide:

- action label
- trust grade
- basis freshness
- next required step

from the capsule itself.

## Copy rule

Forbidden capsule copy:

- `still dangerous`
- `warning active`
- `same session as before`

Allowed capsule copy:

- `trust unlock required before destructive approval`
- `basis stale after endpoint drift; re-review required`
- `export receipt exists; barrier review remains pending`

## Public objects

### Danger session capsule

Fields:

- `danger_session_capsule_id`
- `endpoint_ref`
- `acting_seat_ref`
- `destructive_action_ref`
- `transport_trust_grade`
- `basis_freshness_verdict`
- `at_risk_summary_rows[]`
- `best_rescue_rung`
- `next_required_step`
- `generated_at`

### Persistent review-context rail

Fields:

- `danger_review_context_rail_id`
- `danger_session_capsule_ref`
- `current_shell_ref`
- `loss_matrix_ref`
- `salvage_ladder_ref`
- `trust_review_ref`
- `salvage_export_receipt_refs[]`
- `approval_barrier_ref`
- `execution_ticket_ref`
- `latest_receipt_ref`
- `generated_at`
