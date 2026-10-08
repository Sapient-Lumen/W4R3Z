# Frontier salience 216 — compile iteration now needs coverage-scope receipts and claim-ceiling honesty

## Main judgment

The next worthwhile deepening for **P-0537 Compile Iteration Feedback Kit** is not another hotpatch engine, watcher wrapper, or framework adapter.
It is a receiver-facing contract for **what is actually under the live-update regime** and **where support claims must stop**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies compile time as a universal productivity tax and explicitly names hot reloading and faster linking as important mitigation routes.
- Dioxus now documents three separate hot-reload families and keeps experimental Rust hotpatch tip-crate-only.
- `subsecond` keeps patch scope and route-local anchors explicit instead of promising whole-workspace coverage.
- Chaud updates `#[chaud::hot]` functions and also documents that its macros are no-ops unless the relevant feature is enabled.
- `hot-lib-reloader` makes the reload surface depend on a wrapped dylib interface and documented exported-function limitations.
- `bevy_simple_subsecond_system` explicitly constrains coverage to annotated / preexisting routes and excludes common workspace layouts.

## What the sharper crate should provide

A stronger **P-0537** should now publish:

- `coverage-scope.receipt.json`
- `coverage-ceiling.report.json`
- doctor rules that reject fake “successful reload somewhere means broad support” stories
- bundle inventory that keeps coverage scope and claim ceilings distinct from activation, generation, outcome, and drain

## Boundary reminder

This is still **not** a new patch engine, not a build orchestrator, and not a framework-only convenience wrapper.
It is the support-contract layer that lets another engineer review:

- what surfaces were actually covered,
- whether coverage depended on annotations, wrappers, or specific launch-time routes,
- where support claims stop,
- and when manual review is still the only honest answer.
