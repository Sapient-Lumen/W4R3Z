# Reclaim preview page: freed bytes, non-effects, and retention cost interface spec

## Purpose

This page answers:

> if I apply this reclaim action, what bytes should disappear, what truths should remain unchanged, what retention or continuity posture will weaken, and what prerequisites or blockers still stand in the way?

The page exists because `clear`, `cleanup`, `free space`, and `remove local files` are not honest enough by themselves.

## Core rule

Every reclaim action stronger than a purely automatic temp-file trim must compile to one first-class **Reclaim preview** page before apply.
That page owns:

- exact target classes
- expected byte delta
- explicit non-effects
- continuity / retention costs
- prerequisites and blockers

## Primary layout

The page always renders the same regions:

1. proposed reclaim verdict
2. target-and-delta card
3. non-effects card
4. continuity / retention cost card
5. prerequisites, blockers, and apply receipt target

### 1) Proposed reclaim verdict

Show:

- action label
- strongest honest one-line summary
- expected bytes freed
- safety class: `safe-first`, `reviewed`, `destructive`, `unknown-outcome`
- one recommended apply posture

### 2) Target and delta card

Show exactly which classes are in scope, such as:

- residual temp bytes
- diagnostic logs
- materialized payload copies
- transfer receipts
- archive/history classes
- service-state residues

For each class show:

- expected bytes freed
- whether estimate is exact or approximate
- locality / owner
- whether any bytes in the class are intentionally preserved

### 3) Non-effects card

Show what the action does **not** do, for example:

- does not delete replicated payload on other peers
- does not remove subject membership
- does not clear transfer history rows
- does not weaken archive retention
- does not erase crash artifacts
- does not reclaim hidden state-root bytes

This card is mandatory.

### 4) Continuity and retention cost card

Show:

- whether future re-download or rematerialization is required
- whether restore/history posture gets weaker
- whether diagnostics/support evidence becomes less available
- whether any later recipe is needed to regain the previous posture

### 5) Prerequisites, blockers, and receipt target

Show:

- required posture changes before apply
- missing proofs or missing live sources
- unknowns that prevent honest estimates
- the receipt page that will verify observed outcome after apply

## Honest outputs

This page may conclude:

- `safe-first residual trim; no continuity weakening expected`
- `local payload eviction; later rematerialization depends on surviving source`
- `archive reduction; restore window will narrow`
- `outcome uncertain; measurement incomplete`

It may not compress all of these into `cleanup will free space`.

## Rules

### Rule 1 — reclaimed bytes and weakened truths must stay adjacent

Never say only how many bytes may be freed.
Always say what operator guarantees become weaker, if any.

### Rule 2 — non-effects are part of the contract

An omitted non-effect line is treated as an incomplete preview.

### Rule 3 — unknown estimates must remain typed

Use typed uncertainty such as:

- `exact`
- `best-effort estimate`
- `cannot estimate until measurement refresh`
- `blocked by unclassified bytes`

### Rule 4 — broader delete verbs may not hide inside reclaim previews

If the action would actually remove replicated payload or sever subject relationships, the preview must say so directly and should usually redirect to a different mutation review family.

## Event language

Use explicit phrases such as:

- `preview shows 3.2 GiB residual trim; no history weakening`
- `preview shows 11.4 GiB payload eviction; subject membership preserved`
- `preview shows 6.8 GiB archive reduction; restore window shortened from 30 days to 7 days`
- `preview blocked by unknown service-state bytes`

Avoid vague lines such as:

- `cleanup may affect app performance`
- `files can be restored later`
- `may remove some cached data`

## Non-clone reason

Current official Resilio docs do provide practical cleanup and space-saving verbs, but they still leave operators to infer blast radius and non-effects from whichever article they found.
AnonSync should instead expose one Reclaim preview page where expected freed bytes, non-effects, and retention cost stay visible together before apply.
