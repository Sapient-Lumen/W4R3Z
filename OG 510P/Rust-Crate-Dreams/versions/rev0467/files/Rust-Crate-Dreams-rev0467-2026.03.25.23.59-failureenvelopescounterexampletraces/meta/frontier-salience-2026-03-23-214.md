# Frontier salience 214 — compile iteration now needs retirement boundaries and old-generation drain honesty

## Main judgment

The next worthwhile deepening for **P-0537 Compile Iteration Feedback Kit** is not another hotpatch engine, watcher wrapper, or framework adapter.
It is a receiver-facing contract for **when older code is expected to retire** and **whether pre-reload work has actually drained** after a reload event.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies compile time as a universal productivity tax and explicitly names hot reloading and faster linking as important mitigation routes.
- The 2025 compiler-performance survey still says incremental rebuilds remain painful and warns that current hot-patching systems still have real limitations and edge cases.
- `subsecond` now documents stack rewind to the “cleanest” hot entrypoint, stale-call unwind/retry behavior, and nested `call` boundaries that localize patch application.
- Chaud explicitly says old code can continue indefinitely if no hot entrypoint is called and that stored routes can keep older code alive.
- `hot-lib-reloader` exposes before/after reload events and explicit handoff hooks, which are useful boundaries without being full old-generation drain proofs.

## What the sharper crate should provide

A stronger **P-0537** should now publish:

- `retirement-boundary.report.json`
- `old-generation-drain.report.json`
- doctor rules that reject fake “reload complete means old code is gone” stories
- bundle inventory that keeps activation, generation, retirement, and drain completeness distinct

## Boundary reminder

This is still **not** a new patch engine, not a process supervisor, and not a general quiescence framework.
It is the support-contract layer that lets another engineer review:

- what route boundary is claimed to retire old code,
- whether that boundary is stack-scoped, entrypoint-scoped, library-scoped, or process-scoped,
- whether a reload event merely bracketed handoff,
- whether older callbacks/tasks/routes may still remain,
- and when manual review is still the only honest answer.
