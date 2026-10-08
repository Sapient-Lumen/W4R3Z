# Frontier salience 212 — compile iteration now needs activation-boundary and stale-code-residency honesty

## Main judgment

The next worthwhile deepening for **P-0537 Compile Iteration Feedback Kit** is not another watcher wrapper, dev server, or “instant reload” demo.
It is a receiver-facing contract for **when new code actually becomes active** and **what old code may still continue to run or remain reachable after a reload event**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies compile time as a universal productivity tax and explicitly names hot reloading and faster linking as high-leverage mitigations.
- The current **Relink don’t Rebuild** goal still shows that “small change” and “fast path” are not yet the same thing upstream.
- Dioxus hot-reload docs now give a clear multi-surface model, but they still do not export a neutral activation/continuity bundle.
- `subsecond` documents globals/statics/thread-local caveats and struct-layout limits sharply enough that “patch route exists” is not a sufficient story.
- `chaud` explicitly documents entrypoint-gated activation and continued old-code execution via function pointers or trait objects.
- `hot-lib-reloader` explicitly documents reload events, serialization/deserialization handoff, global-state reinitialization, and `TypeId` identity drift.

## What the sharper crate should provide

A stronger **P-0537** should now publish:

- `activation-boundary.report.json`
- `stale-code-risk.report.json`
- doctor rules that reject fake “reloaded means immediately active everywhere” stories
- bundle inventory that keeps patch route, continuity class, activation boundary, and stale-code residency distinct

## Boundary reminder

This is still **not** a new hotpatch engine, not a watcher, not a framework-specific runtime shim, and not a replacement for Dioxus/Subsecond/Chaud/hot-lib-reloader.
It is the support-contract layer that lets another engineer review:

- when fresh code becomes reachable,
- whether old frames or stored call routes can still hit old code,
- whether continuity came from persistence vs explicit handoff,
- whether restart is still the only honest takeover path,
- and when manual review is still required.
