# Conflict evidence page: real counterpart, delete risk, and safe removal interface spec

## Purpose

The archive already has conflict-adjudication and inbox doctrine.
This document makes one narrower but ordinary page concrete.

The page exists to answer one operator question:

> what real object does this conflict-named entry correspond to, why is direct deletion unsafe, and what evidence supports the current winner/loser posture?

## Core decision

Every serious sync product must own one first-class **Conflict evidence** page.
That page is the semantic home of:

- conflict artifact identity
- live counterpart proof
- winner / loser basis
- delete risk disclosure
- safe removal / rename ladder
- receipts proving what was preserved

The product must not force the operator to infer all this from suffixes or folk wisdom.

## Fixed page order

1. conflict identity strip
2. counterpart map
3. winner / loser evidence
4. delete-risk review
5. safe resolution ladder
6. receipt promise

### 1) Conflict identity strip

Show:

- displayed conflict path
- original path family
- conflict kind (`name collision`, `case / unicode collision`, `unsupported-entry fallout`, `manual re-add echo`, `mixed`)
- current safety verdict (`inspect-first`, `compare-first`, `safe-rename-away`, `unsafe-delete`, `manual-adjudication-required`)

### 2) Counterpart map

Show a two-sided or multi-sided mapping between:

- conflict artifact on this seat
- live counterpart path(s) on other seats
- last known healthy candidate
- any archived predecessor related to the same object family

This section should answer `what real thing does this conflict artifact correspond to?`

### 3) Winner / loser evidence

Show:

- candidate rows
- byte/hash evidence where available
- chronology evidence where available
- portability or unsupported-entry evidence where relevant
- whether the product has a suggested healthy candidate or not

The page must make it obvious when the conflict exists because namespace renderings differ rather than content bytes alone.

### 4) Delete-risk review

This section must say plainly:

- whether deleting the conflict artifact would propagate wider deletion
- whether the artifact is merely an alternate rendering of live data
- whether the conflict object can be moved aside safely
- whether a local-only quarantine is available
- whether resolution requires preserving one candidate outside the subject first

The operator must never have to guess whether deletion is cosmetic cleanup or destructive mutation.

### 5) Safe resolution ladder

Allowed next actions:

- `open compare`
- `move healthy candidate aside`
- `rename for portability`
- `delete conflict after preserved copy proof`
- `quarantine local-only`
- `escalate to portability repair`
- `escalate to wider repair plan`

Each action preview must disclose:

- propagation scope
- history effect
- whether a preserved copy is mandatory first
- whether the product is acting on one candidate or the whole path family

### 6) Receipt promise

Show:

- what receipt will be issued
- which candidate was preserved
- which candidate was retired, renamed, or quarantined
- whether any residual risk remains on sibling seats

## Public objects

### Conflict evidence page

Fields:

- `conflict_evidence_page_id`
- `conflict_case_ref`
- `displayed_conflict_path`
- `counterpart_rows[]`
- `candidate_rows[]`
- `delete_risk_verdict`
- `safe_action_rows[]`
- `receipt_plan`

### Counterpart row

Fields:

- `counterpart_row_id`
- `seat_ref`
- `observed_path`
- `relationship_kind` (`same-object-different-render`, `content-divergent-counterpart`, `archived-predecessor`, `unknown`)
- `live_now`
- `proof_confidence`

### Delete risk verdict

Fields:

- `verdict_kind` (`unsafe-delete`, `safe-after-preserve`, `safe-local-quarantine`, `uncertain-inspect-first`)
- `reason_summary`
- `widest_possible_scope`
- `required_preconditions[]`

## Guardrails

The page must never:

- imply a conflict artifact is harmless trash solely because its name has `.Conflict`
- collapse counterpart proof into one vague `remote copy exists`
- offer direct delete before showing preserved-copy requirements
- hide wider propagation risk behind icon-only warnings

## Success criteria

The page is successful only when an operator can answer:

1. what real counterpart this conflict artifact belongs to
2. whether the product has enough evidence to suggest a healthy winner
3. why direct deletion is or is not safe
4. what sequence preserves data before cleanup
5. what receipt will later prove the cleanup was safe
