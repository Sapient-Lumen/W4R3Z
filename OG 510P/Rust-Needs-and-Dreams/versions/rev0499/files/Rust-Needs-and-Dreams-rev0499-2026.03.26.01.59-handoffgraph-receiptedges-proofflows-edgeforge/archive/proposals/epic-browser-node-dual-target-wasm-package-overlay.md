# Epic proposal: Browser + Node dual-target Wasm package overlay

## Problem
The archive can already answer the browser-only package lane.
It still lacks a clear answer for the recurring harder case where a Rust-authored package wants **browser and Node** to both matter, but does **not** actually want to become:
- a browser app,
- a Node-native add-on,
- a worker-first runtime package,
- or a Wasm Component host story.

Current tooling makes this gap visible rather than hypothetical:
- `wasm-pack` exposes different build targets for bundlers, Node, direct browser import, and Deno;
- `wasm-bindgen` deployment docs still distinguish `web`, `nodejs`, and experimental Node ESM targets;
- `js-snippets` support is not uniform across those targets;
- and the `rustwasm` sunset means maintenance story and fallback strategy belong in the lane itself.

## Proposed contribution
Promote a bounded next-lane design for:

**browser + Node dual-target Wasm package overlay**

with:
- one design note that defines the project class and its truths;
- one gap note that makes the missing target/glue/test/maintenance boundary explicit;
- one future path toward a maintained default card **only after** the overlay can name an honest target matrix and test posture.

## Why this is worthy
This is worthy because it turns a recurring but under-specified package ambition into a **reviewable compatibility problem** instead of another vague “Rust compiles to JS/Wasm” narrative.

The value is not that it picks one universal runtime strategy.
The value is that it would let the ecosystem say, with receipts:
- what targets are actually claimed;
- which generated artifacts belong to each target;
- where browser and Node semantics diverge;
- what test evidence exists;
- and when a unified package is the wrong product shape.

## Intended output shape
A serious contribution here would likely standardize a family like:
- `dual-target-jswasm-profile/v0`
- `dual-target-glue-matrix/v0`
- `dual-target-capability-report/v0`
- `dual-target-test-pack/v0`
- `dual-target-release-pack/v0`

## Non-goals
- a universal package that claims parity across browser, Node, Deno, Bun, workers, and components;
- replacing `napi-rs` or Node-native add-on lanes;
- replacing the browser-only package default card;
- or pretending Wasm Components already obsolete the current JS target matrix.

## Current archive consequence
For now, this epic should be read as a **next public-lane candidate**, not an immediate maintained default card.
It outranks **raw custom Wasmtime embedder** and **durable internal library** as the next widening candidate because it solves a more recurring and more confused real-world adoption shape.
