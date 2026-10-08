# Compile iteration feedback product plan — 2026-03-22

This note sharpens **P-0537 Compile Iteration Feedback Kit** into a buildable product plan.

## Why this lane is worthy now

Fresh official signals align unusually well:

- the March 2026 Rust challenges write-up treats compile times as the universal productivity tax and explicitly calls out GUI iteration pain;
- the same note points at hot reloading and faster linking as high-leverage mitigations;
- the 2025 compiler-performance survey says small-change rebuild workflows are still painful;
- and upstream linker/relink work is real enough that downstream teams now need a stable review contract above it.

The sharper missing value is therefore not “make Rust magically fast”.
It is a crate that helps another engineer inspect **which edit paths are live-update-capable, which are only link-speed improvements, what state continuity is being claimed, and what restart path remains necessary**.

## Product thesis

The crate should become the boring support layer above:

- watchers and command-loop tools,
- linker selection and faster-link routes,
- framework-local hot reload,
- runtime hotpatch engines,
- and future upstream relink/reuse improvements.

Its job is to freeze those moving parts into a compact set of reviewable receipts.

## MVP artifact order

1. `iteration-profile.toml`
2. `edit-event.receipt.json`
3. `patch-eligibility.report.json`
4. `linker-route.receipt.json`
5. `state-continuity.contract.json`
6. `fallback-restart.plan.json`
7. `latency-budget.report.json`
8. `iteration-support-bundle.manifest.json`

## First useful scenarios

1. UI-only markup reload with no Rust-code rebuild.
2. faster-linker route that improves latency but does not imply patchability.
3. runtime hotpatch path with preserved function code but limited state continuity.
4. layout/global/constructor drift that requires restart fallback.
5. bundle export that keeps patch truth, linker truth, and state truth separate.

## Receiver-facing promise

A good bundle from this lane should let another engineer answer five questions fast:

1. What changed?
2. What reload or patch route was actually used?
3. What state was preserved, reset, or left undefined?
4. Did the loop meet the declared latency budget?
5. What restart plan remains when patching is not safe?

## Things this product should resist

- becoming only a watcher wrapper;
- becoming only a linker benchmark runner;
- becoming only a framework-local hot reload adapter;
- pretending restart-free feedback is always possible;
- or flattening every faster-feedback route into one fake “hot reload” verdict.
