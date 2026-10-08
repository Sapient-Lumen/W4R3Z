# Capture-only ingest sink, retention floor, and disconnect semantics interface spec

## Purpose

The archive already had subject-kind migration, snapshot-send, and opaque-replica language.
What it still lacked was one explicit interface contract for a very common personal workflow that sync products often special-case poorly:

> when the user is not collaborating on a folder but simply wants a device to ingest captured material into a more durable sink, what page proves that this is a **capture-only ingest** relationship with its own retention promises, runtime caveats, and disconnect semantics?

Current official Resilio docs make this seam sharper than a generic `camera backup exists` note would.
They still present camera backup as an automatic backup flow from mobile devices to a desktop, NAS, or other high-storage device, say that deleting photos on the phone after sync leaves copies on the storage device, say that stopping/disconnecting backup leaves the pictures already present on both devices intact, note that iOS and Windows Phone require the app to remain open for real-time transfer, and still describe backup folders as `1.4` folders with Read Only keys because they are `for storage purposes only`.

That is useful functionality.
It is still not a clean public subject model.

## Core decision

AnonSync should make **capture-only ingest sink** a first-class subject kind.

A capture-only ingest relationship should declare, on one page:

- the source capture seat
- the sink or sinks
- whether the flow is append-only, reconcile-only, or ordinary bidirectional sync
- what retention floor applies after source-side deletion
- what runtime conditions are required for timely ingest on the source platform
- what disconnect means for already-arrived bytes and for future captures

If the operator still has to infer those truths from a mobile feature page and a legacy folder type, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- storage-only ingest is useful enough to deserve its own model, not a hidden exception
- retention after source-side deletion is a real contract and should be stated explicitly
- stopping/disconnecting an ingest flow has different consequences for existing bytes versus future captures
- source runtime limits such as `app must stay open` materially affect ingest truth
- sink selection across linked devices is part of the workflow and should be reviewable
- backup special-casing can still be implemented through a legacy folder class rather than a first-class subject kind
- the operator can still confuse `backup`, `read-only sync`, and `capture sink` even though their retention promises differ

AnonSync should therefore keep one stronger rule:

> capture-to-sink workflows must be modeled as first-class ingest subjects with explicit retention and disconnect truth.

## Fixed review order

Every non-trivial capture-ingest action should render the same sections in the same order:

1. **Ingest contract now**
2. **Source runtime and sink readiness**
3. **Retention and disconnect consequences**
4. **Receipt and continuity promise**

### 1) Ingest contract now

This section should show:

- source device and capture domain
- sink members and selected storage roots
- whether the relationship is `capture-only ingest`, `reconcile`, or `general sync`
- allowed source-side mutations after ingest
- whether sink-side edits can flow back at all

The operator must be able to answer: **what kind of relationship is this really?**

### 2) Source runtime and sink readiness

This section should show:

- whether the source platform supports background ingest reliably
- whether the app/process must remain open
- queue size and last successful ingest time
- sink capacity and write-readiness
- whether all selected sinks are online, deferred, or unavailable

The operator must be able to answer: **is capture likely to arrive promptly, and where?**

### 3) Retention and disconnect consequences

This section should show:

- the retention floor for already-arrived bytes
- what source-side deletion does after a file has safely landed
- what `pause`, `stop`, and `disconnect` mean for future captures versus stored copies
- whether disconnect leaves the current sink copy intact, quarantined, or removable by later cleanup

The operator must be able to answer: **what survives if I delete on the phone or stop the relationship?**

### 4) Receipt and continuity promise

This section should show:

- accepted source, sink, and retention settings
- runtime caveats acknowledged at apply time
- any current backlog
- whether disconnect preserved the existing sink bytes
- a replayable receipt for later audit

The operator must be able to answer: **what ingest promise did the system actually make?**

## States

Use a small stable vocabulary:

- `capture-ready`
- `capture-blocked-runtime`
- `sink-unavailable`
- `retention-floor-active`
- `ingest-disconnected-retained`
- `capture-backlog`

## Main surface

The source seat and sink subject should expose a **Capture ingest** card with:

- current ingest state
- backlog count/bytes
- sink count
- retention-floor badge
- a drill-in action: `Inspect capture ingest`

## Detailed surface

The detailed page should have five panes.

### Pane A — Contract summary

Shows:

- source
- sinks
- subject kind
- return-path policy
- retention floor

### Pane B — Runtime health

Shows:

- background capability
- foreground-required yes/no
- last active ingest time
- queue/backlog

### Pane C — Sink map

Per sink:

- path/root
- available space
- online state
- last write receipt

### Pane D — Exit and disconnect review

Actions:

- pause future capture
- disconnect but retain landed bytes
- migrate sink
- escalate to general sync/reconcile review

### Pane E — Receipts

Shows ingest creation, sink changes, disconnects, and retained-byte receipts.

## CLI parity

Minimum commands:

- `anonsync ingest show <subject>`
- `anonsync ingest sinks <subject>`
- `anonsync ingest disconnect <subject> --retain-landed`
- `anonsync ingest migrate-sink <subject> --to <member:path> --review <review-id>`

## Non-goals

This spec does **not** define:

- rich media curation
- album semantics
- content dedupe across unrelated capture subjects

It only defines how capture-to-sink workflows become first-class and reviewable.

## Acceptance criteria

A user can:

- create a capture-only ingest relationship without pretending it is ordinary collaboration
- inspect runtime caveats such as foreground-required operation before trusting timely ingest
- tell what survives after source-side deletion or disconnect
- distinguish ingest sinks from read-only replicas and general sync subjects
- prove afterward which sink held the bytes and under what retention promise
