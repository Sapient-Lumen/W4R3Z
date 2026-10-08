---
id: P-0100
title: Zero‑Copy Archive Safety Kit — rkyv‑style fast formats with portable safety gates, validation, and compatibility evidence
status: idea
domains: [data, performance, serialization, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/rkyv
  - https://github.com/rkyv/rkyv
  - https://curtislowder.com/blog/2025-08-10-sufficient-serialization/
needs:
  - zero-copy formats are powerful but hard to deploy safely and compatibly over time
---

# Problem
Zero‑copy deserialization (e.g., `rkyv`) is compelling for read-heavy systems, but teams struggle with:
- **Safety posture**: validation, bounds checks, and “what is safe to assume” boundaries
- **Compatibility posture**: how to evolve archived layouts and detect breakage early
- **Operational tooling**: benchmarking, corpus replay, and failure artifact capture

This slows adoption or leads to unsafe shortcuts.

# What it provides
- **A “safe deployment profile” for zero‑copy archives**
  - required validation gates (what must be checked before using bytes as data)
  - optional stricter profiles for hostile/untrusted inputs
- **Compatibility evidence + tooling**
  - `cargo zcar verify`: checks that new builds can read an archive corpus
  - `zcar-report.json`: perf + size + validation results + compat status
- **Archive corpus + minimization**
  - `zcar-corpus.zip`: historic archives + metadata + expected outcomes
  - “minimize failing archive” tool for quick bug bundles
- **Bench harness**
  - consistent microbench interface across formats (rkyv / bincode / postcard / etc.)
  - teaches teams to choose the right format for their workload (read-heavy vs write-heavy)

# MVP (4–6 weeks)
- corpus format + verifier
- rkyv integration module: generate + validate + replay corpus
- report emitter + a reference CI workflow

# Design notes
- **Not a competing serializer**: it’s a deployment & evidence kit
- **No magical schema evolution**: it surfaces incompatibilities early and makes them actionable
- **Portable by default**: avoid platform-specific assumptions unless explicitly enabled

# Testing & conformance
- corpus replay in CI
- fuzzing hooks for archive bytes (opt-in)
- Miri/loom-friendly “no UB in validation path” target (where practical)

# Related work
- rkyv provides the zero-copy mechanism and validation helpers; the missing piece is a standardized *operational* safety/compatibility envelope.
- Practical tradeoffs of serialization choices are discussed in community writeups comparing rkyv to other formats.
