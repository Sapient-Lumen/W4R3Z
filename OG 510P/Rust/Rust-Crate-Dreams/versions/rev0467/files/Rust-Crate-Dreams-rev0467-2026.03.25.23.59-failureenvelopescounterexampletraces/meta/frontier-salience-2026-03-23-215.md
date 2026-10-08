# Frontier salience 215 — compile iteration now needs live-update outcome receipts and degraded-mode honesty

## Main judgment

The next worthwhile deepening for **P-0537 Compile Iteration Feedback Kit** is not another patch engine, watcher wrapper, or framework adapter.
It is a receiver-facing contract for **what actually happened when a live update attempt ran** and **what operating mode the process is honestly in afterward**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies compile time as a universal productivity tax and explicitly names hot reloading and faster linking as important mitigation routes.
- The 2025 compiler-performance survey still says current hot-patching systems remain limitation-heavy and not robust in the general case.
- `subsecond` now documents explicit patch-application failure variants and still keeps successful patch application separate from stale-call unwind/retry behavior.
- Chaud explicitly distinguishes unrecoverable errors from potentially recoverable degraded states via log levels.
- `hot-lib-reloader` explicitly documents combinations that can crash or corrupt behavior rather than merely “reload less well”.

## What the sharper crate should provide

A stronger **P-0537** should now publish:

- `live-update-outcome.report.json`
- `degraded-iteration-mode.report.json`
- doctor rules that reject fake “patchable means patched” and fake “reload event means healthy continuation” stories
- bundle inventory that keeps eligibility, outcome, degraded mode, and fallback planning distinct

## Boundary reminder

This is still **not** a new patch engine, not a process supervisor, and not a generic logger wrapper.
It is the support-contract layer that lets another engineer review:

- what update route was attempted,
- whether that attempt actually applied,
- whether old code likely remained in service,
- whether the process is now healthy, degraded, disabled, restart-only, or unknown,
- and when manual review is still the only honest answer.
