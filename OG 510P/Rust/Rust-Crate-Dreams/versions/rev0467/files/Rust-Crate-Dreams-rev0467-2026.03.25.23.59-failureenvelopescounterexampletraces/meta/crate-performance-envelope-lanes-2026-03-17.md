# Crate performance-envelope lanes — 2026-03-17

This note keeps **P-0517 Crate Performance Envelope Pack Kit** from collapsing into generic “better benchmarking” or generic “better performance tooling”.

## The lane

**P-0517** is the crate-authored, receiver-facing artifact layer for:

- named workload scenarios,
- metric choice,
- confidence / noise classes,
- checked reproduction recipes,
- representative budgets,
- and release-to-release performance-envelope diffs.

It answers:

- “What performance posture does this crate actually support?”
- “Which workload and metric should I trust?”
- “Which numbers are CI-reliable versus manually reviewable?”
- “How did this crate’s performance contract change across releases?”

## What it is not

### 1. Not task-first crate choice

**P-0509** helps users decide which crate to start with for a task.
**P-0517** helps users understand the performance tradeoff surface of a crate they already chose or are reviewing.

### 2. Not producer-side capability contracts

**P-0510** is about what a crate claims to support in general.
**P-0517** is about workload-specific performance posture and measurement honesty.

### 3. Not shared interop profiles

**P-0511** defines reusable compatibility boundaries across crates.
**P-0517** may reference those profiles, but it is not itself an interop contract.

### 4. Not configuration-scenario packs

**P-0516** explains how to instantiate a crate for a named scenario.
**P-0517** explains what performance tradeoff that scenario actually yields and under what measurement assumptions.

### 5. Not compile-time guidance or runtime handoff

**P-0512** and **P-0513** are supportiveness lanes around failure and recovery.
**P-0517** is about pre-failure performance expectations and reproducible measurement posture.

### 6. Not upgrade packs or off-ramp packs

**P-0514** and **P-0515** help users move between versions or away from a crate.
**P-0517** may help diff performance changes across versions, but it is not a migration or successor artifact by itself.

### 7. Not generic benchmark frameworks

Criterion, Iai-Callgrind, Divan, libtest benches, and related tools run measurements.
**P-0517** sits above them as the contract layer that chooses named scenarios, metrics, and confidence boundaries.

### 8. Not profiling evidence bundles

Profiling bundles capture raw or normalized evidence for investigation.
**P-0517** is narrower and more product-facing: it explains what a crate means to promise about performance and how to check it conservatively.

### 9. Not hosted performance CI services

CodSpeed-class services help execute or compare benchmarks in CI.
**P-0517** can import from them, but it is not a SaaS replacement or runner.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **general support/interop claims**,
3. **shared interop profiles**,
4. **configuration/setup scenarios**,
5. **performance-envelope contracts**,
6. **compile-time guidance**,
7. **runtime handoff**,
8. **upgrade/off-ramp support**,
9. **generic benchmark/profiling tools**,
10. or **hosted CI perf services**.

Do **not** let the archive quietly rephrase performance envelopes as “better benchmark charts”, “better profiling”, or “better config scenarios with numbers attached”.
