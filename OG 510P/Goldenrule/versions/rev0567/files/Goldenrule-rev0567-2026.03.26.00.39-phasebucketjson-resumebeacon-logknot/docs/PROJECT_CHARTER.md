# Concord Project Charter

## Purpose

Concord is a research lab for discovering and stress-testing reciprocal strategies under explicit definitions.
The output is not "a narrative." The output is reproducible evidence artifacts.

## What We Are Trying To Accomplish

1. Build a deterministic experimental engine for repeated social dilemmas.
2. Use formal analysis where tractable (closed-form or numerically robust certificates).
3. Run large experiment programs safely (AFK, kill/resume, no orphan compute).
4. Keep claims tied to frozen definitions and versioned evidence.

## System Split (Hard Boundary)

### Rust (`crates/gr_engine`)

Rust owns:
- deterministic simulation semantics,
- schema-typed artifacts and stable hashing,
- world/strategy execution with bounded behavior,
- formal math solvers and verification-friendly certificates,
- low-level diff/shrink/probe primitives.

Rust does not own:
- workflow orchestration UX,
- queue supervision dashboards,
- long-running mission scheduling policies.

### Python (`grlab`)

Python owns:
- experiment/task orchestration,
- durable queueing and AFK safety loops,
- search policy loops and mission control,
- report generation and operator ergonomics.

Python does not redefine:
- simulation truth semantics,
- scoring equations already defined in Rust artifacts.

## Evidence Discipline

Every comparative claim must be scoped by:
- definition hashes,
- engine version,
- world/strategy identifiers,
- run artifacts.

No "best strategy" claim is valid without its failure envelope and definition context.

## Design Constraints

1. Determinism first.
2. Provenance first.
3. Diffability and shrinkability first.
4. Small, testable bricks over broad rewrites.

## Non-Goals

- No grand moral authority claims.
- No hidden thresholds in code when a spec artifact should define them.
- No one-off "hero run" that cannot be reproduced from artifacts.

## Immediate Priority

1. Keep core docs operational and truthful.
2. Keep core CLI and engine behavior testable.
3. Move mathematically meaningful logic into explicit modules with tests.
