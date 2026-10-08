---
id: P-0141
title: WebGPU CTS Interop & Triage Kit — run, minimize, and report conformance failures from Rust
status: idea
domains: [gpu, graphics, conformance, testing, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://gpuweb.github.io/cts/
  - https://github.com/gfx-rs/wgpu/discussions/1611
  - https://crates.io/crates/wgpu
  - https://lib.rs/crates/deno_webgpu
needs:
  - Make it straightforward to run WebGPU CTS (and subsets) from Rust CI and local workflows.
  - Turn massive CTS output into actionable, minimized, stable failure artifacts.
  - Provide a common “interop vocabulary” so implementations can compare results fairly.
risks:
  - CTS size/runtime cost; needs smart selection, sharding, caching, and minimization.
  - Cross-driver nondeterminism; must record environment fingerprints and retries.
  - Keeping up with CTS updates while preserving reproducibility of reports.
---

## Problem

The WebGPU Conformance Test Suite (CTS) is normative: implementations must pass it to be considered WebGPU-conformant.  
Source: https://gpuweb.github.io/cts/

Rust projects (notably `wgpu`) explicitly point to CTS as a major defense and discuss how to run it in CI (e.g., via Deno tooling).  
Sources: https://github.com/gfx-rs/wgpu/discussions/1611 , https://crates.io/crates/wgpu

But the current state for Rust developers is fragmented: bespoke runners, hard-to-triage failures, and difficulty sharing minimized repros across OS/GPU/driver matrices.

## What this crate should provide

A **runner + triage workbench** for WebGPU CTS focused on Rust implementers and downstreams:

1. **`cargo webgpu-cts run`**
   - Fetch/pin CTS version, run selected queries (selectors), shard and parallelize.
   - Backends: wgpu-native, Dawn (optional), browser (optional, via headless).
   - Output a stable `cts-report.json` for CI systems.

2. **`cargo webgpu-cts triage`**
   - Normalize failures (error categories), cluster similar failures, summarize deltas.
   - Produces `*.ctsfail.zip` bundles:
     - selector list, environment fingerprint (adapter, driver, OS), logs, screenshots if relevant
     - minimized subset if possible (bisect selectors; heuristic minimization)

3. **`cargo webgpu-cts compare`**
   - Compare two runs (commits, drivers, platforms) and report regression sets.

4. **Interop hooks**
   - Export/import results in a common format so multiple implementations can exchange data.

## Users & user stories

- **GPU backend maintainer**: “Run CTS shards in CI, and get one minimized bundle per root-cause.”
- **App developer**: “Know whether a bug is my shader vs the implementation by checking CTS equivalence.”
- **Driver/OS matrix owner**: “Track which failures are driver-specific vs implementation-specific.”

## Prior art (and why it’s insufficient)

- **CTS itself** defines behavior, but not a cargo-native operational workflow.  
  Source: https://gpuweb.github.io/cts/
- **wgpu discussions** highlight the need and some routes (Deno runner), but it’s not packaged as a reusable workbench.  
  Source: https://github.com/gfx-rs/wgpu/discussions/1611
- **`deno_webgpu`** indicates CTS-driven testing, but is ecosystem-specific rather than a general Rust tool.  
  Source: https://lib.rs/crates/deno_webgpu

## MVP plan (3–5 weeks)

- Minimal runner:
  - Pin CTS version (git SHA), run selectors via a JS runner (Node/Deno)
  - Capture stable JSON report + logs
  - Create `*.ctsfail.zip` bundles for failures
- Implement basic sharding strategy (by test file / selector hash).
- Provide GitHub Actions example with caching of CTS checkout and node_modules.

## v1 plan (8–12 weeks)

- Minimization:
  - Selector bisection + flaky-test detection (retry policy)
  - Environment fingerprinting: GPU adapter/driver, limits/features, OS/build
- Visualization:
  - HTML summary (generated from report.json) with drilldown links
- “Interop mode”:
  - Compare against a reference (e.g., prior known-good snapshot) and produce diffs.

## Conformance & testing

- Self-tests: run a tiny curated CTS subset in CI on software adapters.
- Golden fixtures:
  - Simulated reports to ensure stable JSON schema and clustering logic.
- Repro capture:
  - Optional record of shader modules and pipeline descriptors for triage (privacy-conscious).

## Adoption strategy

- Keep runtime dependencies (Node/Deno) optional; provide clear install checks.
- Ship as `cargo-webgpu-cts` + a library crate for report parsing and minimization heuristics.
