# Warning page: class, scope, and safe sentence interface spec

## Purpose

Give one ordinary page that answers:

> what kind of warning is this, how serious is it, how wide is it, and what exact sentence is still safe to say right now?

This page exists because a warning row is often treated as self-explanatory when its true meaning may be transient load, chronology invalidation, source absence, continuity damage, or policy disablement.

## Core rule

Every durable warning must compile to a **warning record** with at least:

- warning class
- active scope / blast radius
- seriousness
- strongest safe sentence
- stronger forbidden sentence
- least-strong next rung
- current evidence and freshness

The UI may abbreviate the row, but it may not let the row outrun the record.

## Required sections

### 1) Warning now

Always show:

- warning title
- warning class (`transient-load`, `chronology-invalid`, `source-absent`, `continuity-damaged`, `storage-floor`, `bootstrap-failed`, `policy-disabled`, `unknown`)
- severity (`notice`, `degraded`, `blocked`, `unsafe-to-continue`, `unknown`)
- first seen / last seen / freshness of current evidence
- strongest safe sentence

Example safe sentences:

- `Work is delayed by local load; no continuity loss is proven.`
- `Chronology trust is invalid; winner claims are unsafe.`
- `This subject currently lacks a full byte source.`
- `Hidden control state for this subject is damaged; sync is suspended here.`

### 2) Scope and impact

Show which world is affected:

- item
- path group
- subject/share
- seat/runtime
- identity/control plane
- storage root / default-folder disk

Also show unaffected neighbors when known.

### 3) Evidence basis

List the proofs that gave the warning its current class:

- current detectors / warning codes
- observed facts
- last successful contradictory proof if any
- freshness of the evidence
- whether the warning is self-reported, inferred, or externally corroborated

### 4) Safe wording boundary

The product must publish:

- strongest safe sentence
- stronger forbidden sentence
- why the stronger sentence is unsafe

Examples:

- safe: `Synchronization for this subject is suspended on this seat.`
- forbidden: `All local bytes are damaged.`
- safe: `No full source peer is currently proven.`
- forbidden: `The file is permanently gone.`

### 5) Next honest actions

Offer typed actions rather than generic `Fix`:

- `Inspect blocker scope`
- `Open recovery rung`
- `Collect stronger evidence`
- `Acknowledge with note`
- `Export warning packet`

## Required row grammar

A compact row should read like:

- `Chronology invalid · subject+peer pair · winner claims blocked`
- `Transient load · seat-local · wait or inspect motion basis`
- `Continuity damage · subject-local · reconnect or rebuild after archive check`
- `Source absent · item set · restore source or preserve absence verdict`

## Data model

- `warning_id`
- `warning_code`
- `warning_class`
- `severity`
- `scope_kind`
- `scope_ref`
- `first_seen_at`
- `last_seen_at`
- `evidence_freshness`
- `safe_sentence`
- `forbidden_sentence`
- `least_strong_next_rung`
- `ack_state`
- `history_ref`

## Failure this page prevents

Without this page, operators are pushed into support-lore reasoning and generic dismiss/retry behavior while the true warning class and blast radius remain implicit.

AnonSync should instead keep warning class, scope, evidence, and safe wording adjacent.
