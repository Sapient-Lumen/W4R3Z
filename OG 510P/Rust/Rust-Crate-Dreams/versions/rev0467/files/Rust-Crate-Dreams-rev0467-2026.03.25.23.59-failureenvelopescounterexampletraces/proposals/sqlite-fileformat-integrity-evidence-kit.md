---
id: P-0281
title: SQLite File-Format + Integrity Interop & Evidence Kit — canonical dumps, page-level diffs, and corruption triage bundles
status: idea
domains: [databases, storage, forensics, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://sqlite.org/fileformat.html
  - https://crates.io/crates/rusqlite
  - https://crates.io/crates/sqlite-parser-nom
  - https://crates.io/crates/sqlite_wasm_reader
---
## What it should provide others

A **bundle-first toolkit** for working with SQLite databases as *artifacts*:
- deterministic inspection
- stable diffs (schema + content + page-level)
- corruption triage that produces shareable, privacy-safe repro bundles

The gap is not another SQL layer; it is a standardized way to answer:
- “What changed in this DB file between builds?”
- “Is this file valid SQLite, and if not, what’s the minimal failing segment?”
- “Can we reproduce the corruption / locking issue with a minimal fixture?”

## Why now (ecosystem gap)

SQLite is the lingua franca embedded database, but Rust teams often end up with bespoke scripts for:
- migrating / diffing DB state in tests
- debugging on-disk corruption issues from embedded/edge deployments
- producing minimal repros (especially when the DB contains sensitive user data)

SQLite’s on-disk format is stable and documented; that makes it an ideal target for canonicalization + evidence bundles.

## Proposed crate shape (workspace)

- `sqlitekit-core` — file-format primitives, page model, stable identifiers
- `sqlitekit-inspect` — `sqlitekit inspect foo.sqlite` → JSON/NDJSON outputs (no execution needed)
- `sqlitekit-canon` — deterministic “canonical dump” format (schema + content) for diffs
- `sqlitekit-diff` — semantic diff (schema changes, row changes, page deltas)
- `sqlitekit-triage` — corruption triage + minimization (binary chopping to smallest failing db)
- `sqlitekit-bundle` — `*.sqlitebundle.zip` schema + redaction + signing hooks
- `cargo-sqlitekit` — CLI + CI integration

### Canonicalization strategy (practical)

Prefer layered outputs:
1. **Schema IR** (tables, indexes, triggers) extracted via parsing/inspection
2. **Content IR** (ordered, typed row sets per table) where feasible
3. **Page map IR** (page types + btree topology fingerprints) for low-level diffs

This lets users choose tradeoffs:
- “diff only schema”
- “diff schema + rows for specific tables”
- “diff page layout” for forensics and corruption debugging

## Minimum lovable MVP (4–8 weeks)

1. `sqlitekit-inspect` producing stable JSON for:
   - header, page size, freelist, schema summary
2. `sqlitekit-canon` canonical schema dump + deterministic row export for a selected table list
3. `sqlitekit-bundle` with redaction presets (strip large TEXT/BLOB, keep hashes) + `sqlitekit-diff`

Deliverable: `sqlitekit diff before.sqlite after.sqlite --tables users,sessions --out change.sqlitebundle.zip`.

## De-risk plan

- Start with **read-only** inspection and canonical dumps; avoid implementing a full SQLite engine.
- Use existing crates for SQL grammar parsing where useful; keep the on-disk parser minimal and format-driven.
- Provide “hash-only” redaction modes so sensitive values never leave CI.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 5 (DB artifacts appear everywhere)
- Sustainability: 4
- Differentiation: 4 (canonical dumps + minimization + evidence bundles)
