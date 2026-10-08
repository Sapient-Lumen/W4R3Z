# Staged Build Plan

This plan follows the specs’ priorities: determinism, AFK safety, definition clarity, and “micro-lab” ergonomics.

## Stage 1 — Minimal deterministic lab core (done)

**Goal:** run small, crisp, reproducible IPD experiments that produce stable artifacts.

Delivered:
- `gr_engine` (Rust): deterministic IPD match simulation; built-in + memory-one strategies; JSON task input; atomic artifact writes.
- Engine traces separate intended/executed/observed actions; artifacts record derived seed streams for reproduction.
- `grlab` (Python): minimal runner that enumerates match tasks, executes them, and supports resume by skipping existing artifacts.

## Stage 2 — Probes, suites, and definition clarity

**Goal:** make “tests are artifacts” real and easy.

Implemented (foundation):
- Probe registry + probe suite specs and runner (`gr-engine run-probe-suite`).
- Metamorphic check registry + suite runner (`gr-engine run-metamorphic`, `gr-engine run-metamorphic-suite`).
- Shrinking/minimization for failing probes (`gr-engine shrink-probe-*`).
- Definition snapshots + definition diffs (`gr-engine snapshot`, `gr-engine diff-snapshots`, `gr-engine diff-snapshot-artifacts`).
- Result drift diffs as artifacts (probe/probe-suite/metamorphic/metamorphic-suite/scorecard/scorecard-suite/snapshot-run).
- Scorecard + scorecard suite execution (minimal confidence banner + gating).

## Stage 3 — AFK worker model + durable queue

**Goal:** meet the “AFK runner contract” under kill/resume with zero orphan compute.

Implemented (foundation):
- SQLite-backed durable queue + leasing/heartbeats/reconcile (`grlab queue-*`, `grlab watch`).
- Multi-worker queue execution with killable process groups (`grlab queue-work --workers N`, `grlab afk`).
- Retry/backoff + max attempts + per-task timeouts.
- Artifact indexing into SQLite and DB-backed reporting (`grlab queue-index`, `grlab report --use-db`).
- Definition hashes in manifests + definition diffs between runs (`grlab defdiff`).

In progress (foundation brick):
- SQLite-backed task queue helpers + CLI (`grlab queue-init`, `grlab queue-import`, `grlab queue-status`, `grlab queue-work`, `grlab queue-reconcile`, `grlab queue-list`, `grlab watch`).
- Multi-worker queue execution + lease heartbeats (`grlab queue-work --workers N`, `grlab afk`).
- Retry/backoff + max-attempts + timeouts for robust AFK behavior (no silent orphan compute).
- Artifact indexing (SQLite) to support fast reporting and future content-addressed storage.

## Stage 4 — Search & optimization loops

**Goal:** Pareto-front exploration under explicit scorecards + adversarial probe growth.

Planned:
- Parameter sweeps (memory-one), evolutionary search, and minimal adversarial coevolution.
- Failure mining → shrink → “probe promotion”.

## Stage 5 — Institutions + richer worlds

**Goal:** partner choice, reputation, apology/repair channels, and realism modules without losing epistemic control.

Planned:
- Modular institutions in `WorldSpec`.
- Holdout suite management.
- Redaction/export pipeline for dual-use-sensitive artifacts.
