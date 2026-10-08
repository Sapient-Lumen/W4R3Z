# Integrity rebuild, reindex, and subject repair ladder interface spec

## Purpose

The archive already had hidden-state repair, reconnect, and continuity language.
What it still lacked was one explicit contract for a harsher operator moment:

> when the system says the local share database is damaged, service files are missing, trees cannot merge, or syncing has been abandoned, what page proves the safest repair ladder and blast radius before the user starts removing and re-adding things?

Current official Resilio docs make this seam sharper than a generic `repair sync` button would.
They still say database error repair starts with restart, then disconnect/reconnect the share to recreate only the local database, and then escalates to removing and re-adding the folder across peers if the problem persists.
They still say missing or corrupted `.sync` service files suspend synchronization and the documented fix is to remove the share, delete `.sync`, and add it back.
They still say some no-sync cases reduce to `devices cannot merge folder trees` and again recommend re-adding the folder, and they still say filesystem errors can cause syncing to be abandoned entirely.

That is practical support lore.
It is still not a good public integrity-repair contract.

## Core decision

AnonSync should make **repair ladders** first-class.

Every integrity incident must classify:

- what layer is damaged: local index, local witness cache, subject identity, namespace merge state, path bind, or real bytes
- what the least-destructive repair is
- what evidence will be lost by each stronger step
- whether continuity of the subject identity can be preserved
- which peers or subjects are in scope for the repair

If the operator still learns the blast radius only after choosing `remove and add again`, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- multiple integrity failures still collapse into restart, reconnect, or re-add ritual
- `recreate local database` and `create a new synchronization instance` are materially different actions but can appear adjacent
- deleting hidden service state can also discard local archive/history context unless separately protected
- merge failure, database failure, and path ambiguity can still share the same support move even though their causes differ
- filesystem errors can suspend syncing without a public proof ladder that distinguishes transient from structural damage
- the user can still be asked to widen the repair from one peer to all peers before the interface proves why
- continuity of subject identity can still be lost as collateral damage of implementation repair

AnonSync should therefore keep one stronger rule:

> every repair step must publish its layer, blast radius, evidence loss, and continuity effect before it can be applied.

## Fixed review order

Every non-trivial integrity incident should render the same sections in the same order:

1. **Fault classification now**
2. **Least-destructive repair ladder**
3. **Evidence and continuity impact**
4. **Receipt and replay promise**

### 1) Fault classification now

This section should show:

- damaged layer: `local-index`, `service-state`, `merge-state`, `path-bind`, `filesystem-health`, `byte-integrity`, `identity-root`, `unknown`
- subject scope and peer scope
- whether syncing is degraded, suspended, or abandoned
- strongest evidence for the diagnosis

The operator must be able to answer: **what is actually broken?**

### 2) Least-destructive repair ladder

This section should show ordered candidate steps such as:

- restart runtime only
- rescan/reindex without rebinding
- rebuild local index while preserving subject identity
- repair path bind while preserving local bytes
- rotate or recreate local service state
- reconstruct subject from surviving witnesses

Each step must declare:

- affected scope
- reversibility
- continuity class
- prerequisite backups or receipts

The operator must be able to answer: **what is the safest next repair, and what stronger steps remain if it fails?**

### 3) Evidence and continuity impact

This section should show:

- archive/history/cache/receipt evidence at risk
- whether local subject identity survives
- whether peers will see a continuity-preserving repair or a new subject incarnation
- whether any local bytes must be quarantined before stronger repair

The operator must be able to answer: **what proof or continuity will I lose if I take this step?**

### 4) Receipt and replay promise

This section should show:

- chosen repair step
- resulting subject continuity status
- evidence preserved, discarded, or relocated
- whether escalation to the next step is still permitted or now unnecessary
- the durable repair receipt

The operator must be able to answer: **what repair was actually performed, and what identity/evidence survived?**

## Main surface

The subject workspace should expose an **Integrity repair** card with:

- fault class
- current sync posture
- safest available step
- strongest escalation step if needed
- a drill-in action: `Review repair ladder`

## Detailed surface

The detailed page should have five panes.

### Pane A — Fault classifier

Columns:

- symptom
- diagnosed layer
- confidence
- subject scope
- peer scope

### Pane B — Repair ladder

Rows:

- step
- layer touched
- reversibility
- evidence loss risk
- continuity impact

### Pane C — Preservation set

Shows:

- bytes to preserve first
- state to snapshot first
- receipts/history to seal first
- quarantines required before rebuild

### Pane D — Escalation guardrails

Actions:

- run local repair
- preserve evidence only
- widen scope to peer group review
- abort and escalate externally

### Pane E — Receipts

Shows prior repair attempts and resulting continuity class.

## CLI parity

Minimum commands:

- `anonsync repair classify <subject>`
- `anonsync repair ladder <subject>`
- `anonsync repair apply <subject> --step <step-id> --review <review-id>`
- `anonsync repair receipt show <receipt-id>`

## Non-goals

This spec does **not** define:

- low-level database formats
- filesystem scrubbing internals
- external support bundle contents
- transport retry logic unrelated to integrity repair
