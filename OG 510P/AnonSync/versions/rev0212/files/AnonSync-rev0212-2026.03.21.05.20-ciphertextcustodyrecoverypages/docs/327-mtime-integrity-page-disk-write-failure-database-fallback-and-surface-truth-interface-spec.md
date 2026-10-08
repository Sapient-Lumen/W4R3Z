# Mtime integrity page: disk write failure, database fallback, and surface truth interface spec

## Purpose

This page answers one ordinary question:

> when modification-time fidelity is weak, which timestamp is authoritative right now, which surfaces are reading disk versus database truth, and what behavior changes follow from that split?

The page exists because `file modified time`, `timestamp on disk`, and `timestamp known to the sync engine` are not always the same thing.

## Core decision

Every seat must render one first-class **Mtime integrity** page whenever timestamp assignment is weak, degraded, or deliberately bypassed.
That page owns:

- on-disk mtime write status
- database timestamp status
- divergence between the two
- affected product surfaces
- repair and verification ladder

The operator must not have to discover database-only timestamp truth from a hidden advanced preference description.

## Primary layout

The page always renders the same regions in the same order:

1. seat strip
2. write-integrity card
3. truth-divergence card
4. surface-impact card
5. remediation ladder
6. integrity receipts

### 1) Seat strip

Show:

- seat label
- affected subject or path scope
- current verdict: `mtime-faithful`, `mtime-write-failing`, `database-authoritative`, `timestamp-authority-ambiguous`
- one next honest action

### 2) Write-integrity card

This card publishes:

- whether mtime assignment to disk is succeeding
- current fallback posture
- last observed write error family if known
- whether retry is active, suppressed, or disabled

The operator must be able to answer: **is the engine still successfully writing authoritative mtimes to disk?**

### 3) Truth-divergence card

This card publishes:

- authoritative timestamp source right now: `disk`, `database`, `mixed`, `unknown`
- example paths where disk and engine truth diverge
- whether on-disk mtime is current-time noise or trustworthy evidence
- confidence grade for chronology decisions that still depend on mtime

The operator must be able to answer: **which timestamp should I trust right now?**

### 4) Surface-impact card

This card publishes:

- which surfaces read disk timestamps directly
- which surfaces read engine/database truth
- where a file browser view may disagree with product truth
- whether restore, reconcile, or chronology ranking are affected

The operator must be able to answer: **where will I see misleading time information if I leave this page?**

### 5) Remediation ladder

This card publishes:

- least-destructive fix rungs
- verification step after each rung
- whether fixing write permission, storage class, or provider semantics is likely to restore faithful disk mtimes
- whether the current database-only posture is acceptable temporarily or risky

The operator must be able to answer: **what smallest change would restore faithful on-disk timestamps, and how will I verify it?**

### 6) Integrity receipts

Receipts show:

- mtime write failures detected
- fallback policy changes
- repaired paths
- post-repair verification results

## Non-negotiable rules

### Rule 1 — disk and database truth must never silently collapse

If the engine knows a different timestamp than the filesystem shows, the page must say so directly.

### Rule 2 — file-browser disagreement is product truth, not user error

The product must publish when an external file browser will mislead the operator.

### Rule 3 — chronology confidence must degrade honestly

Weak mtime fidelity must lower chronology confidence rather than pretending ranking is normal.

## Honest outputs

The page may conclude:

- `On-disk mtime writes are failing; the sync engine is keeping authoritative time only in its own database.`
- `External file-browser timestamps are not trustworthy for chronology decisions on this seat right now.`
- `Database-only time authority is acceptable as a temporary operating posture, but restore and reconciliation reviews should stay guarded until disk fidelity is repaired.`

It may not collapse those outcomes into one generic `advanced setting enabled` label.
