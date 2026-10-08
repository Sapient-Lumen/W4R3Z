---
id: P-0206
title: Wasm Component Contract & Conformance ShipKit (world locks, composition bundles, deterministic exercise receipts)
status: idea
domains: [wasm, interoperability, tooling, packaging, testing]
last_reviewed: 2026-03-18
evidence:
  - https://component-model.bytecodealliance.org/language-support/rust.html
  - https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
  - https://component-model.bytecodealliance.org/running-components/wasmtime.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip3.html
  - https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-xjhv-v822-pf94
---

# Problem

Wasm Components are becoming a real Rust deployment target, but the missing product is no longer “somehow build a component.”
The sharper missing layer is a **reviewable contract** for:

- **how** the component was produced,
- **what exact world/package/version boundary** it claims,
- **whether composition is actually closed**,
- and **how another person can run or replay** it.

Right now, teams still glue together native `cargo build --target=wasm32-wasip2`, transitional `cargo-component`, `wkg`, WAC, `wasm-tools`, and runtime CLIs in bespoke ways that are hard to inspect and harder to diff.

# What the crate provides (for other people)

## 1) Component contract bundle format
- `*.componentbundle.zip` containing:
  - the component `.wasm`,
  - WIT package(s),
  - world/interface metadata,
  - a tooling-lineage report,
  - a composition-closure report,
  - an exercise receipt,
  - and a short summary another person can review.

## 2) World-lock and version-truth API
- package/world/interface extraction and normalization,
- embedded import/export hashing,
- mismatch detection for cases where inferred or omitted package versions fail to line up,
- compact reports rather than giant raw metadata dumps.

## 3) Closure + exercise diagnostics
- distinguish:
  - fully bundled / closed components,
  - host-supplied-open components,
  - transitively open components,
  - and manual-review-required cases.
- capture exercise posture for:
  - `wasi:cli/run`,
  - `wasmtime run --invoke`,
  - or custom-host-required components.

## 4) “Explain” diagnostics
- On failure: produce a bundle that includes:
  - target/tooling lineage,
  - exact world/import/export view,
  - bundled-versus-open dependency status,
  - and the smallest exercise path that reproduced the issue.

# Architecture sketch

- `component-kit-model`: reports, receipts, diffs, bundle schema.
- `component-kit-import`: WIT/component metadata import and inspection.
- `component-kit-check`: lineage, world-lock, and closure classification.
- `component-kit-exercise`: deterministic exercise receipts on top of Wasmtime/custom-host adapters.
- `cargo-component-kit`: CLI wrapper for inspect/check/diff/pack flows.

# MVP (4–8 weeks)

1. Tooling-lineage import and reporting.
2. World-lock extraction and mismatch checks.
3. Composition-closure report.
4. Wasmtime-backed exercise receipt for a small set of runnable-component cases.
5. Deterministic `componentbundle.zip` writer/reader + diff.

# De-risking plan

- Start with **read-only capture and normalization**.
- Keep runtime exercise optional and conservative.
- Treat `cargo-component`, WAC, and native target flows as substrate to import, not replace.
- Keep `manual_review_required` as a first-class result whenever closure or version truth is not confidently known.
