# Frontier salience 213 — compile iteration now needs code-generation witnesses and mixed-generation honesty

## Main judgment

The next worthwhile deepening for **P-0537 Compile Iteration Feedback Kit** is not another hotpatch engine, watcher wrapper, or framework adapter.
It is a receiver-facing contract for **which code generation a route is actually running now** and **whether mixed-generation execution is still possible after a reload event**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies compile time as a universal productivity tax and explicitly names hot reloading and faster linking as important mitigation routes.
- The 2025 compiler-performance survey still says incremental rebuilds remain painful and warns that hot-patching systems still have meaningful edge cases and limitations.
- `subsecond` now documents a jump-table model, nested call boundaries, thread-local caveats, re-instancing pressure, and the absence of true pointer versioning.
- Chaud still documents entrypoint-gated activation plus indefinite survival of old code through function pointers and trait objects.
- `hot-lib-reloader` exposes reload events and load counters, which makes generation naming possible without yet proving route-level generation coverage.

## What the sharper crate should provide

A stronger **P-0537** should now publish:

- `generation-witness.report.json`
- `mixed-generation-risk.report.json`
- doctor rules that reject fake “the new build is live everywhere now” stories
- bundle inventory that keeps generation identity, activation boundary, continuity, and stale-code reachability distinct

## Boundary reminder

This is still **not** a new hotpatch engine, not a watcher, not a framework-specific runtime shim, and not a substitute for Dioxus/Subsecond/Chaud/hot-lib-reloader.
It is the support-contract layer that lets another engineer review:

- what generation witness exists,
- how precise that witness actually is,
- whether different routes may still execute different generations,
- whether a “latest pointer” or load counter was over-read as a stronger proof,
- and when manual review is still the only honest answer.
