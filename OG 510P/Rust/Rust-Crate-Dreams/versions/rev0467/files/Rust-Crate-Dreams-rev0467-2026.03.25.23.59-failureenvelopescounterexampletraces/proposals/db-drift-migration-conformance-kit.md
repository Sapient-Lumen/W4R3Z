---
id: P-0111
title: DB Drift & Migration Conformance Kit — standardized schema drift detection, migration replay, and CI artifacts for Rust DB stacks
status: idea
domains: [database, tooling, reliability, testing, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/sqlx/latest/sqlx/macro.migrate.html
  - https://github.com/launchbadge/sqlx/issues/1105
  - https://users.rust-lang.org/t/how-to-deal-with-sqlx-migrate-and-schema-that-already-exists/123292
needs:
  - “schema drift” and “already exists” realities make migration workflows brittle for teams adopting Rust DB tooling
  - sqlx/diesel/sea-orm each have partial solutions; none provide a shared artifact + conformance story
  - CI needs deterministic, reviewable outputs (“what changed?”, “is this safe?”, “can we replay from scratch?”)
---

# Problem

Migrations are easy until they aren’t:
- environments that already have schema/data
- manual hotfixes causing drift
- feature branches racing and reordering migrations
- teams need deterministic replay and clear diffs in PRs

Rust has good pieces, but lacks a **standard workflow + artifact format**.

# What it provides

## 1) A migration replay and drift check runner

`cargo dbkit` subcommands:
- `cargo dbkit plan` — computes a deterministic migration plan and writes an artifact
- `cargo dbkit replay` — applies migrations to ephemeral DBs (docker/local/embedded)
- `cargo dbkit drift` — compares expected vs actual schema (and emits guidance)

Backends:
- sqlx migrations (`Migrator`, `sqlx migrate`)
- diesel migrations
- sea-orm migrations

## 2) A portable CI artifact format

`*.dbkit.zip`
- `plan.json` (ordered migrations, checksums, backend, features)
- `schema_expected.sql` (normalized output)
- `schema_actual.sql` (from target env)
- `diff.patch` (stable formatting)
- `replay.log` + `error.json` (machine-readable failure)

## 3) Policy knobs teams actually need

- “allow existing schema if empty” vs “must be pristine”
- baseline snapshots (import starting schema once, then migrate forward)
- per-environment guardrails (prod forbids destructive statements unless approved)

# MVP

- sqlx-only backend first (since `migrate!` exists and is common)
- deterministic schema normalize/diff for Postgres + Sqlite
- `dbkit.zip` artifact + GitHub Actions example

# v1

- diesel + sea-orm adapters
- “baseline snapshot” workflow (for adopting migrations into an existing DB)
- conformance corpus:
  - “already exists” adoption path
  - reorder/race scenarios
  - destructive migrations behind explicit approvals

# Why this is epic

It turns migrations into a **reviewable supply chain**:
every PR ships an artifact proving what will happen to the schema and whether drift exists.
