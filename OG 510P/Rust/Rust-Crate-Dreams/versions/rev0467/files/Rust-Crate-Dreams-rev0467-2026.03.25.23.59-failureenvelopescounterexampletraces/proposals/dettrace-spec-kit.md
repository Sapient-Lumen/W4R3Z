---
id: P-0239
title: Determinism Trace & Cassette Spec Kit — a shared artifact format + adapters for async record/replay tooling
status: idea
domains: [testing, async, determinism, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/crate/frankenlab/
  - https://github.com/synoet/sturgeon
  - https://lib.rs/crates/frankenlab
---

## What it should provide others

A **stable, versioned “determinism trace” spec** plus Rust libraries/tools that let different deterministic-testing approaches **interoperate**.

This crate should give users:

- **A cassette format** for deterministic recordings (task scheduling decisions, virtual time, external events).
- **Adapters** for emerging tools (Tokio-first): import/export recordings so teams can share repros even if they don’t share the same harness.
- **Canonicalization + diff** for recordings (CI can compare “same seed” runs deterministically).
- **Redaction primitives** for traces (strip secrets, URLs, tokens; keep structural repro power).
- **Viewing + triage**: a small TUI/HTML report generator to inspect minimized schedules.

## Why this is still missing

Deterministic testing is moving from “research trick” to “production practice,” but the ecosystem is currently **tool-siloed**.

- FrankenLab positions itself as a deterministic record/replay/minimization harness for async Rust. A spec layer would let the *artifact* live longer than any single harness. (See: FrankenLab docs.)
- Sturgeon records async streams with timing information and replays them; it’s evidence that different “record/replay slices” are valuable but not standardized. (See: sturgeon repo.)

## Design outline

### 1) A minimal, composable event model

Focus on what multiple tools can agree on:

- **Schedule decisions**: which runnable task was polled next (or equivalent).
- **Virtual time events**: timers set/fired.
- **External inputs**: user-defined, typed “inbox events” (bytes, JSON, structured).
- **Optional channels**: IO readiness, RNG reads, network cassettes (via references).

### 2) Bundle format

A deterministic artifact should be shareable and diffable:

- `trace.det.jsonl.zst` — append-only event stream.
- `meta.json` — versioning + tool provenance.
- `attachments/` — optional linked evidence (pcap, http cassette, logs).

Recommended packaging: `*.dettracebundle.zip`.

### 3) Canonicalization rules

- Stable ordering and normalization for time, task ids, and attachments.
- A “lossy canonical mode” for diffs (remove nondeterministic metadata).

### 4) Adapter surface

Provide a trait-based interface:

- `Recorder`: emits canonical events.
- `Replayer`: feeds events back.
- `Minimizer`: shrinks traces while preserving failure.

## Minimum lovable MVP (4–8 weeks)

1. Spec v0.1 + reference implementation (`dettrace-core`).
2. CLI: `dettrace validate|canon|diff|inspect`.
3. Adapter prototype for *one* harness (Tokio test harness or FrankenLab-compatible import/export).
4. Basic redaction policy presets.

## De-risk plan

- Start by supporting *only* virtual time + schedule choices + user events.
- Treat IO/network as attachments to avoid overcommitting early.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (artifact standardization + adapters)
