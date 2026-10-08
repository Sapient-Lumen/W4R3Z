# Warning page: kind, current claim, and honest severity interface spec

## Purpose

The archive already has attention delivery and many typed review pages, but it still lacked one ordinary page for the simpler question:

> what exact kind of warning am I looking at right now, and how strong is its current claim?

This document defines the interface contract for one first-class **Warning page**.

## Core rule

Any warning strong enough to change trust, pacing, safety, or next-step choice must compile to one typed page that answers six things together:

1. warning kind
2. current claim under test
3. strongest honest severity
4. what still works normally
5. what evidence made the warning appear
6. whether the next move is inspect, wait, or intervene

The product must not let a toast, footer string, tray badge, or one-line row become the semantic home of the warning.

## Public object

### Warning page

Suggested fields:

- `warning_page_id`
- `warning_kind` (`observer-degraded`, `source-absent`, `hidden-work-delayed`, `state-corruption`, `chronology-invalid`, `merge-risk`, `identity-failed`, `capability-governance`, `unknown`)
- `claim_under_test`
- `severity` (`informational`, `degraded`, `blocked`, `dangerous-if-misread`, `requires-immediate-review`)
- `scope_ref`
- `evidence_rows[]`
- `still_works_rows[]`
- `unknown_rows[]`
- `next_step_posture` (`inspect-first`, `wait-first`, `repair-first`, `escalate-first`)
- `primary_action`
- `related_warning_refs[]`
- `generated_at`

### Evidence row

Suggested fields:

- `evidence_row_id`
- `evidence_kind` (`status-string`, `counterparty-list`, `warning-click-detail`, `measurement`, `recent-receipt`, `history-row`, `config-reading`, `unknown`)
- `summary`
- `freshness`
- `supports_claim` bool
- `supports_severity`

## Fixed page order

1. **Warning verdict**
   - warning kind
   - claim under test
   - honest severity
   - first safe next move

2. **Why this warning exists now**
   - strongest evidence rows
   - what changed recently
   - what uncertainty remains

3. **What still works**
   - unaffected scopes
   - degraded but not blocked scopes
   - work that is still allowed but slower / weaker / more uncertain

4. **How not to misread it**
   - common false equivalences
   - what this warning does *not* prove
   - whether acknowledgement or hiding changes only visibility

5. **Open next step**
   - inspect scope
   - open recovery rung
   - open warning history
   - escalate to deeper page family when needed

## Compact row contract

A dense warning row should preserve these labels in this order:

- `Kind`
- `Claim`
- `Severity`
- `Scope`
- `Next move`

Example:

```text
observer-degraded   file changes may be discovered only by rescan   degraded   subject-only on seat atlas   Review recovery rung
```

## Anti-goals

- no generic `warning` bucket when class is knowable
- no `critical` language when the product only knows `degraded`
- no hidden assumption that `blocked` means `nothing still works`
- no footer-only semantics for warnings with meaningful consequences

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving the page:

- what exact kind of warning this is
- what the product is currently claiming
- how strong that claim honestly is
- what still works despite the warning
- whether the first move is inspect, wait, repair, or escalate
