# Losing-version fate page — archive, branch, export, and live-path protection interface spec

## Purpose

A winner review is incomplete if the losing version disappears into vague reassurance.
This page owns the next question:

> before I let this candidate lose the live path, where exactly will it survive, how discoverable and recoverable will it be, and what replay risk remains later?

This page exists so `placed in Archive` never substitutes for a real loser-preservation grammar.

## Core decision

Whenever a same-path loser could be overwritten, displaced from the live path, or demoted to history, the product must offer one first-class **Losing-version fate** page before final apply.

## Fixed page order

1. **Threatened loser strip**
2. **Preservation channels**
3. **Recoverability and horizon**
4. **Replay and reactivation risk**
5. **Chosen loser fate**
6. **Receipt promise**

### 1) Threatened loser strip

Show:

- losing candidate label
- current location/seat
- current risk (`overwrite`, `archive-only`, `branch`, `export`, `quarantine`, `blocked`)
- strongest safe sentence

### 2) Preservation channels

Offer only typed options such as:

- `Archive with reviewed access path`
- `Branch beside live path`
- `Detached export copy`
- `Quarantine and hold replay`
- `No extra preservation beyond existing history`

Each option must show:

- where the loser will live
- whether it stays inside product governance or becomes an outside artifact
- whether it remains visible from ordinary recovery surfaces

### 3) Recoverability and horizon

For each option show:

- recoverability class (`easy`, `guarded`, `hard`, `unknown`)
- access path
- retention horizon if known
- whether authorship/provenance remains visible or requires another surface

### 4) Replay and reactivation risk

Show:

- whether restoring this loser later could replay outward automatically
- whether the loser might be re-archived on later rescan
- whether the current runtime/watch state is sufficient for clean restore
- whether a detached copy is safer than a live restore

The operator should be able to answer: **if I need this loser later, what exactly happens when I bring it back?**

### 5) Chosen loser fate

After selection, show one plain-language commitment sentence, for example:

- `The losing version will be branched before live overwrite proceeds.`
- `The losing version will survive only in Archive; later replay remains guarded.`
- `A detached export will be created; the product will not auto-replay it.`

### 6) Receipt promise

The resulting receipt must prove:

- loser identity
- loser-preservation shape chosen
- access/recoverability posture
- stronger sentence rejected

## Public object

### `losing_version_fate_review`

Fields:

- `losing_version_fate_review_id`
- `subject_ref`
- `canonical_path`
- `losing_candidate_ref`
- `risk_posture`
- `preservation_channels[]`
- `chosen_channel`
- `recoverability_class`
- `retention_horizon`
- `replay_risk_posture`
- `generated_at`

## Result

A good losing-version fate page prevents five failures:

- `archived` becoming the only remembered fact
- discoverability and retention remaining implicit
- loser provenance being lost even when bytes survive
- restore/replay risk being discovered only after a later recovery attempt
- later audits losing proof that loser-preservation options were reviewed before overwrite
