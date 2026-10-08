# Transfer staging, partial artifacts, and finalize visibility interface spec

## Purpose

The archive already had byte-witness, ghost-announcement, and commit-barrier language.
What it still lacked was one explicit interface contract for a simpler but equally common operator question:

> when bytes are in flight but not yet safely present, what page proves whether the object is still staged, finalized, abandoned, or stuck, and what cleanup is safe?

Current official Resilio docs make this seam much sharper than a generic `downloads can fail` warning would.
They still describe `.!sync` files inside the hidden `.sync` folder as files that are being synced at the moment and say that when download completes the file is renamed to its proper name and moved into place.
Their troubleshooting docs also still say partially downloaded files can remain on the receiving device, that a restart may resume them, and that if syncing still does not resume the operator should delete the stuck `.!sync` files and restart again.

That is practical repair advice.
It is still not a good public transfer-finality contract.

## Core decision

AnonSync should make **staging** and **finalization** first-class.

Every subject that can receive bytes must expose, per object and in aggregate:

- whether bytes are announced only, staged partially, verified and ready, or finalized in place
- where staged bytes currently live
- what conditions must be met before finalization
- whether cleanup is reversible, retryable, or destructive
- what residue remains after an interrupted transfer

If a user still has to inspect hidden directories for temp artifacts and guess whether deletion is safe, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal six truths AnonSync should not clone:

- partial-transfer truth can still live mainly in a hidden service directory
- visible namespace truth and staged-byte truth are still separate but weakly surfaced
- finalization still depends on an implicit rename/move boundary rather than one explicit state model
- interrupted transfers can leave residue that the operator is asked to clean manually
- the repair path still depends on trial actions like restart, then manual deletion, then restart again
- `file exists` and `file is finalized` remain different truths but can be hard to distinguish publicly

AnonSync should therefore keep one stronger rule:

> transfer staging must be visible as state, evidence, and repairability, not only as hidden temp artifacts.

## Fixed review order

Every non-trivial transfer-staging incident should render the same sections in the same order:

1. **Object state now**
2. **Finalize gate and blockers**
3. **Residue and cleanup safety**
4. **Receipt and replay promise**

### 1) Object state now

This section should show:

- whether the object is `announced`, `staging`, `verifying`, `finalized`, `stalled`, or `abandoned`
- staged byte count and expected total if known
- current source witnesses
- whether the visible namespace entry is a placeholder, a staged temp object, or the finalized object

The operator must be able to answer: **what exactly exists right now?**

### 2) Finalize gate and blockers

This section should show:

- checksum/hash verification state
- last successfully received range/piece
- any blocker such as no source, no space, path error, permission failure, or policy hold
- the exact conditions under which the object will be renamed or promoted into place

The operator must be able to answer: **what is preventing finalization?**

### 3) Residue and cleanup safety

This section should show:

- whether staged residue can be resumed safely
- whether deleting the residue only discards incomplete local bytes or also affects shared state
- whether a retry will resume from checkpoint, restart from zero, or remain blocked
- whether the residue is hidden implementation state or operator-visible retained cache

The operator must be able to answer: **is it safe to clean this up, and what do I lose if I do?**

### 4) Receipt and replay promise

This section should show:

- the final object state after repair/apply
- whether any staged residue was discarded
- whether the retry resumed or restarted
- the witness set used for the eventual finalized object
- a replayable event trail

The operator must be able to answer: **what happened to the staged bytes, and how did we reach finality?**

## States

Use a small stable vocabulary:

- `announced only`
- `staging`
- `verifying`
- `finalized`
- `stalled resumable`
- `stalled cleanup-optional`
- `abandoned residue`

## Main surface

The subject workspace should expose a **Transfer finality** card with:

- count of staged objects
- count of stalled objects
- count of cleanup-optional residues
- a drill-in action: `Inspect staged transfers`

## Detailed surface

The detailed page should have five panes.

### Pane A — Staged object table

Columns:

- object
- state
- staged bytes
- witness count
- blocker
- cleanup safety

### Pane B — Finalize gate

Shows per object:

- verification status
- last piece received
- rename/promote readiness
- filesystem/space/policy blockers

### Pane C — Repair actions

Actions:

- resume
- retry from start
- discard staged residue locally
- quarantine residue for manual inspection

Each action must clearly state whether shared state changes.

### Pane D — Aggregate health

Shows:

- total staged bytes
- stalled duration distribution
- common blocker classes
- whether the subject is making progress or merely accumulating residue

### Pane E — Receipts

Shows prior resume/discard/finalize events.

## CLI parity

Minimum commands:

- `anonsync transfers show <subject>`
- `anonsync transfers inspect <subject> --object <id>`
- `anonsync transfers resume <subject> --object <id>`
- `anonsync transfers discard-residue <subject> --object <id> --review <review-id>`

## Non-goals

This spec does **not** define:

- transport-route choice
- scheduling/prioritization policy
- long-term archival of failed transfer residue

It only defines how partial transfer state becomes visible and safely repairable.

## Acceptance criteria

A user can:

- distinguish staged bytes from finalized bytes without browsing hidden directories
- see what must happen before a staged object becomes final
- tell whether cleanup is local-only and resumable or destructive to progress
- repair a stalled transfer from GUI or CLI using the same state vocabulary
- prove afterward whether the object resumed, restarted, finalized, or had residue discarded
