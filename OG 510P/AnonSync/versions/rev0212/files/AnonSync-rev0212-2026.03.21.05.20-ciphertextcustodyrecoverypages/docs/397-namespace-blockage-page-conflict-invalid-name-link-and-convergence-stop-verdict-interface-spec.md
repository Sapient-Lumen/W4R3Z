# Namespace blockage page: conflict, invalid name, unsupported entry, and convergence-stop verdict interface spec

## Purpose

The archive already has conflict, portability, and environment diagnosis doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> why is this path family not converging, and is the honest answer here `healthy but delayed`, `auto-repaired`, `conflicted`, `portability-blocked`, `unsupported`, or `share-stalling`?

## Core decision

Every serious sync product must own one first-class **Namespace blockage** page.
That page is the semantic home of:

- convergence verdict
- blockage class
- affected path family
- auto-repair disclosure
- unsupported-entry disclosure
- repair ladder
- receipts and proof

The product must not leave the real answer hiding in suffixes, warning rows, or error-linked articles.

## Fixed page order

The page always renders the same sections in the same order:

1. verdict strip
2. affected path family card
3. blockage-class card
4. auto-repair / rewrite card
5. safe repair ladder
6. proof and receipts
7. expert details drawer

### 1) Verdict strip

Show:

- subject
- acting seat
- current convergence verdict (`converging`, `delayed`, `auto-repaired`, `conflicted`, `portability-blocked`, `unsupported-entry`, `stalled-share`, `mixed`)
- strongest honest next action
- whether this is a live diagnosis, a replay, or a pinned prior receipt

The strip should answer `what kind of namespace problem is this, at the highest level?`

### 2) Affected path family card

Show:

- canonical displayed path family
- every observed rendering that matters (`raw seen name`, `portable rendering`, `conflict rendering`, `blocked rendering`)
- whether the issue affects one object, one directory cluster, or the whole subject
- whether the same problem is visible on one seat only or multiple seats

This card should answer `what exact paths are in play here?`

### 3) Blockage-class card

Show one or more typed classes:

- `case-fold collision`
- `unicode-normalization collision`
- `invalid symbol / reserved name`
- `path-too-long`
- `unsupported link / alias entry`
- `share tree cannot merge`
- `filesystem error / unreadable path`
- `auto-conflict emitted`
- `share-stalling policy`
- `mixed`

For each class, show:

- severity (`watch`, `guarded`, `high`, `blocked`)
- why the product chose that class
- whether the share can continue around the problem or is stalled by it

### 4) Auto-repair / rewrite card

Show clearly whether the product has already done any of the following:

- emitted `.Conflict` artifacts
- rewritten invalid symbols
- normalized unicode form
- suppressed conflict materialization because policy disabled it
- left the object untouched but blocked
- allowed the visible link entry while excluding its target material

This card must answer `what has the product already done to the path family before I intervene?`

### 5) Safe repair ladder

Render only honest next steps, ordered from least destructive to most consequential:

- `Inspect conflict evidence`
- `Inspect unsupported entry`
- `Normalize / rename for portability`
- `Split into separate subject`
- `Keep local-only`
- `Rebind / migrate target`
- `Open wider repair plan`
- `Unsafe to proceed without manual adjudication`

Every action preview must disclose:

- local-only versus multi-seat impact
- whether bytes move, remain, or become hidden
- whether history / receipts are preserved
- whether the action is reversible

### 6) Proof and receipts

Show:

- latest diagnosis receipt
- affected object count
- exact observations supporting the verdict
- prior repairs on the same path family
- whether the proof set is complete or sample-based

### 7) Expert details drawer

Include:

- target filesystem profile
- platform family limits
- policy toggles materially affecting diagnosis
- watcher / scan confidence where relevant
- raw object identifiers and prior names

## Public objects

### Namespace blockage page

Fields:

- `namespace_blockage_page_id`
- `subject_ref`
- `seat_ref`
- `current_verdict`
- `blockage_classes[]`
- `affected_path_rows[]`
- `auto_repair_rows[]`
- `repair_actions[]`
- `proof_rows[]`
- `receipt_refs[]`
- `next_honest_action`

### Affected path row

Fields:

- `path_row_id`
- `raw_name`
- `portable_rendering` nullable
- `conflict_rendering` nullable
- `location_scope` (`single-object`, `directory-cluster`, `subject-wide`)
- `seat_visibility_scope` (`local-only`, `multi-seat`, `unknown`)
- `current_material_state`

### Auto-repair row

Fields:

- `auto_repair_row_id`
- `repair_kind` (`conflict-emitted`, `symbol-rewritten`, `unicode-normalized`, `blocked-no-rewrite`, `link-target-excluded`, `policy-suppressed-conflict`)
- `applied`
- `repair_scope`
- `receipt_ref` nullable
- `reversible`

## Entry points

Launch this page from:

- subject warning badges
- conflict lists
- stalled-share status rows
- bind / adoption / migration reviews
- portability audit surfaces
- unsupported-entry detections

## Guardrails

The page must never:

- equate a `.Conflict` suffix with disposable junk
- treat unsupported links as though target material were automatically included
- hide share-stalling policy in expert-only settings
- collapse path collision, invalid name, and I/O unreadability into one vague `sync issue`
- offer a destructive fix before showing whether the product already rewrote or emitted alternates

## Success criteria

The page is successful only when an operator can answer, without leaving the page:

1. what exact path family is affected
2. which blockage class is actually present
3. whether the product already rewrote, conflicted, blocked, or excluded anything
4. whether the share can continue around the issue or is materially stalled
5. what the least-destructive honest next step is
