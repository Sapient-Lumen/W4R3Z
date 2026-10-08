# Byte-class inventory page: payload, history, logs, and residual storage truth interface spec

## Purpose

This page answers:

> where exactly is local space going right now, which byte classes are payload versus retention versus service state, and which of them are reclaimable without lying about continuity cost?

The page exists because `storage used` is not one class of bytes.

## Core rule

Every seat and subject must expose one first-class **Byte-class inventory** page whenever space, cleanup, or retention is under review.
That page owns:

- byte classes
- current locality / owner
- retention role
- reclaimability and continuity cost
- last-observed measurement provenance

## Primary layout

The page always renders the same regions:

1. inventory summary
2. byte-class table
3. locality and owner card
4. continuity / retention meaning card
5. next review links

### 1) Inventory summary

Show:

- total local bytes attributable to product-managed classes
- current measurement freshness
- largest three classes
- strongest currently reclaimable class
- strongest currently non-reclaimable class

### 2) Byte-class table

Render one row per stable class such as:

- live materialized payload
- placeholder namespace / metadata
- retained history / archive / versions
- bounded-transfer receipts / download sinks / upload sinks
- logs / diagnostics / profiler / crash artifacts
- state-root database / identity / settings
- residual / orphaned / temp / in-flight bytes
- unknown / unclassified managed bytes

Each row must show:

- current bytes and percent of total
- locality / owner class
- reclaimability (`safe-first`, `reviewed`, `destructive`, `not-by-reclaim`, `unknown`)
- continuity role (`active payload`, `history`, `diagnostic`, `control-plane`, `residue`)
- strongest risk if removed

### 3) Locality and owner card

Show where each class principally lives:

- subject path
- state root
- service-owned root
- mobile sandbox
- bounded-transfer inbox
- hidden managed namespace
- unknown / mixed

The operator must be able to answer: **whose bytes are these, and where do they actually live?**

### 4) Continuity and retention meaning card

Explain per class:

- whether the class is required for active sync continuity
- whether it is optional but preserves recovery/history
- whether it is only diagnostic/support residue
- whether it represents abnormal leftovers that should usually be reclaimed first

### 5) Next review links

Link to:

- Space pressure
- Reclaim preview
- Reclaim receipt

## Honest outputs

This page may conclude:

- `archive dominates but is intentional history`
- `diagnostic residue dominates and is safe-first reclaimable`
- `state-root database is small but continuity-critical`
- `unknown managed bytes present; do not promise safe reclaim yet`

It may not flatten every row into `cache`, `data`, or `other`.

## Rules

### Rule 1 — payload and history must not merge

Live materialized bytes and retained history are different classes even when they share nearby paths.

### Rule 2 — service state must stay visible even when small

A small database or identity class may be continuity-critical.
It must not disappear merely because it is not the largest class.

### Rule 3 — unknown bytes are a first-class result

If the product cannot confidently classify some bytes, it must say so and keep them visible as `unknown managed bytes`.

### Rule 4 — reclaimability needs reason codes

Every reclaimability verdict must carry a reason such as:

- `safe-first residue`
- `requires retention weakening`
- `requires subject-membership change`
- `service continuity risk`
- `classification incomplete`

## Event language

Use explicit phrases such as:

- `archive is largest class; history role retained`
- `diagnostic residue exceeds payload on this seat`
- `state-root bytes small but control-plane critical`
- `unclassified managed bytes prevent automatic reclaim recommendation`

Avoid vague lines such as:

- `other data`
- `system files`
- `misc storage`

## Non-clone reason

Current official Resilio docs do reveal many real byte classes — placeholders, archive, app data, user data, logs, residual files, and storage-root state — but they reveal them across separate pages.
AnonSync should instead expose one Byte-class inventory page where payload, history, diagnostics, and residual state stay visibly distinct.
