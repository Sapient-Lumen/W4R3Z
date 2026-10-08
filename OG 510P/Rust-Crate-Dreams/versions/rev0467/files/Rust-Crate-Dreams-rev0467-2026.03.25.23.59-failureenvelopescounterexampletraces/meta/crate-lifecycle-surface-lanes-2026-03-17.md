# Crate lifecycle-surface lanes — 2026-03-17

This note keeps **P-0520 Crate Lifecycle Surface Pack Kit** from collapsing into generic “better graceful shutdown”, “better structured concurrency”, or “better async docs”.

## The lane

**P-0520** is the crate-authored, receiver-facing artifact layer for:

- named background-work components,
- cancel / abort / drop / join distinctions,
- shutdown and drain obligations,
- partial-progress / retry / race truth,
- and release-to-release lifecycle diffs.

It answers:

- “What background work might this crate start or keep alive?”
- “What happens if I drop the handle?”
- “Which methods are cancel-safe, partially-progressing, or abort-hostile?”
- “What must I flush, close, join, or drain before shutdown?”
- “How did that lifecycle support surface change across releases?”

## What it is not

### 1. Not runtime failure handoff

**P-0513** is about the bundle a crate hands another person *after* runtime failure.
**P-0520** is about steady-state and shutdown-path lifecycle truth before or around failure.

### 2. Not observability surfaces

**P-0518** is about emitted telemetry.
**P-0520** is about background work and stop semantics whether or not the crate emits telemetry.

### 3. Not authority surfaces

**P-0519** is about what host powers a crate may touch or assume.
**P-0520** is about what work the crate keeps alive and how that work is stopped, drained, or detached.

### 4. Not configuration scenarios

**P-0516** is about named setup recipes.
**P-0520** may import them, but it is specifically about lifecycle behavior after setup.

### 5. Not performance envelopes

**P-0517** is about workload posture and budgets.
**P-0520** is about cancellation, shutdown, and cleanup posture.

### 6. Not structured-concurrency substrate or runtimes

`task_scope`, `moro`, runtime task groups, and graceful-shutdown frameworks provide implementation substrate.
**P-0520** sits above them as the contract layer that says what one crate promises downstream users.

### 7. Not generic shutdown frameworks

`async_shutdown`, `tokio-graceful-shutdown`, and similar tools help implement lifecycle control in applications.
**P-0520** is broader and more product-facing: it declares one crate’s lifecycle promises and verifies them against fixtures.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **runtime failure handoff**,
2. **telemetry / observability**,
3. **authority / ambient powers**,
4. **setup/configuration scenarios**,
5. **receiver-facing lifecycle-surface contracts**,
6. **structured-concurrency or cancellation substrate**,
7. or **full shutdown/runtime orchestration frameworks**.

Do **not** let the archive quietly rephrase lifecycle-surface contracts as “better shutdown helpers”, “better Tokio docs”, or “another structured concurrency crate”.
