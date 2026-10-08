---
id: P-0271
title: WebGPU CTS Triage & Evidence Kit (webgpubundle)
status: idea
domains: [graphics, webgpu, conformance, testing, interop]
last_reviewed: 2026-03-05
evidence:
  - https://gpuweb.github.io/cts/
  - https://gpuweb.github.io/cts/standalone/
  - https://www.w3.org/TR/webgpu/
  - https://www.w3.org/TR/WGSL/
  - https://crates.io/crates/wgpu
  - https://github.com/gfx-rs/wgpu-native
  - https://github.com/gpuweb/cts
---

## What it should provide others

A way to make **WebGPU implementation bugs reproducible across machines and backends** by turning CTS failures into shareable artifacts:

- minimal repro test selectors + environment fingerprint
- GPU/driver/backend metadata capture (Vulkan/Metal/D3D12/WebGPU)
- canonicalized failure output + shader source snapshots
- automatic bisection helpers for CTS revisions

The core deliverable is a portable `*.webgpubundle.zip` that can be attached to issues/CI logs.

## Why this is needed

The WebGPU Conformance Test Suite (CTS) is **normative** for conformance, and it’s huge; failures often depend on GPU model, driver version, and backend subtleties. The Rust ecosystem has strong building blocks (`wgpu`, `wgpu-native`) but lacks a *standard* way to package failures so they can be replayed and compared.

## Design sketch

### Workspace layout

- `webgpubundle` — bundle schema + redaction + IO
- `webgpu-cts-runner` — run CTS subsets (standalone runner embedding, WPT hooks optional)
- `webgpu-fingerprint` — normalized env capture:
  - adapter info, limits/features
  - driver + OS + backend
  - WebGPU/WGSL version pins
- `webgpu-diff` — canonical diff of failure sets across runs
- `webgpu-minimize` — minimize selector sets and test parameters (best-effort)

### Evidence bundle format: `*.webgpubundle.zip`

- `manifest.json` (cts revision, query selector(s), runtime flags)
- `env.json` (gpu/driver/backend fingerprint + wgpu version)
- `results.ndjson` (canonical pass/fail + error categories)
- `shaders/` (WGSL snapshots + compiled variants when available)
- `logs/` (sanitized stdout/stderr, validation messages)
- `repro.md` (copy/paste commands)

### MVP (4–6 weeks)

1. `webgpu-fingerprint` + deterministic `env.json`
2. `webgpu-cts-runner` to execute a selector and emit `results.ndjson`
3. `webgpubundle` writer/reader + simple `webgpu-diff`
4. CI example: run CTS smoke set and attach bundle

### Non-goals

- Not a new WebGPU implementation
- Not a full CTS fork; prefer pinning and referencing upstream

## Adoption plan

- Start as a toolchain crate that *wraps* `wgpu`/`wgpu-native` projects
- Provide GitHub Actions templates for “attach bundle on failure”
- Encourage upstream-friendly issue templates: “include bundle”
