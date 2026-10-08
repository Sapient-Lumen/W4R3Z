---
id: P-0057
title: run-record-kit — standard run recording artifacts (events + outputs + metadata) for CI replay and analysis
status: idea
domains: [testing, ci, tooling, observability]
last_reviewed: 2026-03-01
evidence:
  - https://nexte.st/docs/design/architecture/recording-runs/
  - https://nexte.st/docs/features/record-replay-rerun/
---

# Problem
When CI fails, developers want a **portable artifact** they can replay locally: event stream, test outputs, environment metadata, and enough structure to enable tooling (search, diff, partial reruns). cargo-nextest has a sophisticated run recording design, but other tools (chaos testing, benchmark harnesses, build analyzers) lack a shared format and library.

# Users & user stories
- CI: “Attach a run artifact to a job; developer downloads and replays it.”
- Tool author: “I want to emit structured run records without inventing a file format.”
- Debugger: “Jump to the first failing test, see context, and reproduce deterministically.”

# Prior art (and why it’s insufficient)
- nextest implements recording internally; the approach is reusable but not standardized.
- Ad hoc logs are not replayable or queryable.

# Design goals
- A versioned **run-record container format** and Rust library.
- Append-only event stream + indexed stdout/stderr chunks.
- Redaction hooks (secrets, paths).
- Optional compatibility with NDJSON event streams (pairs well with cargo-event-stream).

# Non-goals
- A new test runner; this is a substrate.

# Architecture & API sketch
- Container layout (directory or tar.zst):
  - `manifest.json` (tool, args, schema_version, timestamps)
  - `events.ndjson.zst` (append-only typed events)
  - `stdout/` and `stderr/` chunk files + `index.json`
- Library:
  - `Recorder` (write events + outputs)
  - `Reader` (stream events, seek outputs)
- CLI helpers:
  - `run-record inspect`
  - `run-record export (human report)`

# Security / safety model
- Redaction is first-class: allowlist env vars; mask known secret patterns.
- No execution on “replay” unless tool opts in (format should support analysis without execution).

# Maintenance & governance plan
- Tight semver on schema; explicit upgrade tooling.
- Fixture corpus: tiny recordings for compatibility tests.

# Milestones
- 0.1: schema v0 + recorder/reader + basic inspect CLI.
- 0.2: indexing + chunking + redaction policy packs.
- 0.3: integration examples: nextest plugin, chaos-lab, build-insights.

# Open questions
- Whether to standardize event vocabulary across tools vs allow custom event namespaces.
- Best compression and random-access strategy.

# Sources
See front matter links.
