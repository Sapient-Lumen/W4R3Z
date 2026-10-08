---
id: P-0231
title: OpenXR CTS Triage & Evidence Kit
status: idea
domains: [xr, graphics, conformance, testing, interop, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://registry.khronos.org/OpenXR/conformance/cts_usage.html
  - https://github.com/KhronosGroup/OpenXR-CTS
  - https://github.com/KhronosGroup/OpenXR-CTS/releases
  - https://github.com/Ralith/openxrs
---

# Problem

OpenXR runtimes live or die on **conformance**. Khronos provides an OpenXR Conformance Test Suite (CTS), but day-to-day engineering still lacks:

- a portable, *shareable* artifact for “this CTS failure”,
- stable canonicalization for logs, traces, and runtime/environment metadata,
- bisect-friendly “what changed” diffs between CTS runs,
- a clean bridge from Rust OpenXR projects (apps, runtimes, layers) into CTS triage.

CTS is primarily aimed at the adopter process and runtime developers; the Rust ecosystem needs a crate that turns CTS output into **reproducible evidence bundles** that can be shared across vendors and CI systems. citeturn0search1turn0search4

# What it provides

1. `openxr-cts-kit` workspace:
   - `openxr-cts-runner`: hermetic runner wrapper (pin CTS version, collect system metadata).
   - `openxr-cts-parse`: structured parsers for CTS outputs + normalization.
   - `openxr-cts-evidence`: bundle format + redaction + diffing.
   - `openxr-cts-matrix`: extension/support matrix derived from runtime manifests and CTS probes.

2. Evidence bundle format: `*.xrbundle.zip`
   - `manifest.json` (CTS version tag, runtime build SHA, loader/runtime details)
   - `env.json` (GPU/driver/OS, compositor, XR device, enabled extensions)
   - `results.json` (structured test results with stable IDs)
   - `logs/` (canonicalized logs)
   - optional `captures/` (API call summaries, not raw sensitive traces by default)

3. CLI:
   - `xrcapture run` — run CTS and emit a bundle
   - `xrcapture diff` — semantic diff between bundles
   - `xrcapture explain` — highlight likely root causes (extension mismatch, env deltas, timing)

# Design notes

## Pinning and provenance

CTS releases move quickly (Khronos publishes tagged releases). The kit should treat the CTS version as part of the artifact identity, and store enough provenance to reproduce the run. citeturn0search19

## Rust-first integration

Rust already has OpenXR bindings (`openxrs`, `openxr`), but CTS triage is still bespoke. Provide helpers to:

- launch runtimes/layers with known env vars,
- capture extension manifests and loader info,
- map CTS test names → extension/features coverage. citeturn1search1turn1search13

# Minimum lovable MVP (4–8 weeks)

1. Run wrapper + bundle creation:
   - pin CTS git tag/release
   - collect `env.json` + `results.json`
2. `diff`:
   - result-level diff with stable IDs
3. Two integration paths:
   - “runtime under test” (loader points to runtime)
   - “app under test” (for regression testing of layers/app behavior)

# De-risk plan

- Start with parsing/normalizing CTS outputs (no runtime hooks).
- Validate across two CTS versions to ensure stable IDs.
- Keep privacy defaults conservative (no raw GPU dumps; opt-in capture plugins).

# Scorecard (0–5)

- Impact: 3 (XR-focused, but high value where needed)
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4 (evidence bundles + semantic diffs for CTS runs)

# Prior art / adjacent

- Khronos OpenXR CTS usage docs and repository. citeturn0search1turn0search4
- CTS release tags (good anchor for pinning). citeturn0search19
