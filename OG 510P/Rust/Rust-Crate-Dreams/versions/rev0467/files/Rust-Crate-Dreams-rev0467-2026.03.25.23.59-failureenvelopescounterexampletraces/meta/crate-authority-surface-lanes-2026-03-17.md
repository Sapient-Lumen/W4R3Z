# Crate authority-surface lanes — 2026-03-17

This note keeps **P-0519 Crate Authority Surface Pack Kit** from collapsing into generic “better sandboxing”, “better capability APIs”, or “better static authority linting”.

## The lane

**P-0519** is the crate-authored, receiver-facing artifact layer for:

- named ambient authority kinds,
- scenario/profile boundaries,
- determinism posture,
- capability-injection truth,
- sandbox/offline recipes,
- and release-to-release authority diffs.

It answers:

- “What host powers might this crate actually exercise or assume?”
- “Which dependencies are ambient-only versus injectable?”
- “Can this crate run in an offline, deterministic, or sandbox-ready profile?”
- “Which profile still reads env vars, touches `$HOME`, writes temp files, or needs network egress?”
- “How did that authority surface change across releases?”

## What it is not

### 1. Not task-first crate choice

**P-0509** helps users decide which crate to start with.
**P-0519** helps users review or constrain a crate they already chose or are considering.

### 2. Not producer-side capability contracts

**P-0510** is about what a crate claims to support in general.
**P-0519** is specifically about ambient powers, determinism posture, and injection/sandbox recipes.

### 3. Not configuration scenarios

**P-0516** is about named setup/configuration recipes.
**P-0519** may import them, but it is about authority boundaries and host dependence, not generic setup shape.

### 4. Not observability surfaces

**P-0518** is about emitted telemetry.
**P-0519** is about what the crate may touch or assume from the host whether or not it emits telemetry.

### 5. Not compile-time sandbox policy

**P-0107** and adjacent build-sandbox work are about Cargo’s compile-time execution surfaces.
**P-0519** is about the chosen crate’s receiver-facing runtime/library authority surface.

### 6. Not capability-based replacement libraries

`ambient-authority`, `cap-std`, and related crates provide APIs and building blocks.
**P-0519** sits above them as the contract layer that says what one crate actually requires and how to verify narrower profiles.

### 7. Not generic static authority linting

A static scanner can say “this source seems to import env or fs.”
**P-0519** is broader and more product-facing: it declares intended profiles, injection points, and recipes, not just suspicious imports.

### 8. Not full sandbox runtimes or org policy platforms

Containers, seccomp/Landlock wrappers, capability hosts, and org policy engines are broader operational systems.
**P-0519** is a portable crate-support artifact, not a platform replacement.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **general support/interop claims**,
3. **configuration/setup scenarios**,
4. **observability-surface contracts**,
5. **receiver-facing authority-surface contracts**,
6. **compile-time sandbox policy**,
7. **capability-based runtime substrate**,
8. **static authority scanning**,
9. or **full sandbox/runtime host platforms**.

Do **not** let the archive quietly rephrase authority-surface contracts as “better sandboxing”, “better cap-std docs”, or “another security linter”.
