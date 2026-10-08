# Crate observability-surface lanes — 2026-03-17

This note keeps **P-0518 Crate Observability Surface Pack Kit** from collapsing into generic “better telemetry”, “better tracing setup”, or “better observability tooling”.

## The lane

**P-0518** is the crate-authored, receiver-facing artifact layer for:

- named emitted signals,
- setup recipes,
- stability classes,
- cost and cardinality caveats,
- redaction and sensitivity boundaries,
- and release-to-release observability-surface diffs.

It answers:

- “What telemetry does this crate intentionally emit?”
- “Which names and fields are stable enough to build alerts or dashboards on?”
- “What feature flags or adapters do I need to see those signals?”
- “What might this signal surface cost or leak?”
- “How did the crate’s observability surface change across releases?”

## What it is not

### 1. Not task-first crate choice

**P-0509** helps users decide which crate to start with.
**P-0518** helps users operate a crate they already chose or are reviewing.

### 2. Not producer-side capability contracts

**P-0510** is about what a crate claims to support in general.
**P-0518** is about the emitted telemetry surface and its operational meaning.

### 3. Not shared interop profiles

**P-0511** defines reusable compatibility boundaries across crates.
**P-0518** may import those profiles, but it is not itself an interop contract.

### 4. Not compile-time guidance or runtime handoff

**P-0512** and **P-0513** are supportiveness lanes around failure and recovery.
**P-0518** is about what operators can observe before, during, and around runtime, not the bundle handed off after a failure is already being triaged.

### 5. Not upgrade, off-ramp, config-scenario, or performance packs

**P-0514**, **P-0515**, **P-0516**, and **P-0517** are about migration, leaving a crate, setup recipes, and performance posture.
**P-0518** may reference those lanes, but it is specifically about emitted signals and their meaning.

### 6. Not tracing/telemetry plumbing

`tracing`, `tracing-subscriber`, OpenTelemetry SDKs, exporters, and setup kits are the plumbing and wiring.
**P-0518** sits above them as the contract layer that says what signals matter and how trustworthy they are.

### 7. Not telemetry schema linting or semantic-convention governance

Schema-lint and semantic-convention tools help standardize names and keys.
**P-0518** is broader and more product-facing: it says which signals a crate intends to expose, not just whether the names were well chosen.

### 8. Not generic redaction policy tooling

Redaction policy crates can scrub sensitive data.
**P-0518** instead records which signal families are safe, sensitive, hashed, truncated, or manual-review territory for one crate’s intended surface.

### 9. Not full observability platforms

Collectors, vendor backends, dashboards, and org-wide governance systems are broader operational stacks.
**P-0518** is a portable crate-support artifact, not a platform replacement.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **general support/interop claims**,
3. **shared interop profiles**,
4. **compile-time guidance**,
5. **runtime handoff**,
6. **upgrade/off-ramp support**,
7. **configuration/setup scenarios**,
8. **performance envelopes**,
9. **observability-surface contracts**,
10. **telemetry plumbing / schema governance / redaction tooling**,
11. or **full observability platforms**.

Do **not** let the archive quietly rephrase observability-surface contracts as “better tracing setup”, “better OpenTelemetry support”, or “better dashboards”.
