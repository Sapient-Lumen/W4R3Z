---
id: P-0291
title: JPEG XL Conformance & Evidence Kit — decoder/encoder golden tests, fuzz corpus bundles, and reproducible divergence triage
status: idea
domains: [media, imaging, codecs, testing, fuzzing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://jpeg.org/jpegxl/
  - https://github.com/libjxl/libjxl
  - https://crates.io/crates/jxl-encoder
---

## What it should provide others

A **conformance + interop lab** for JPEG XL that lets Rust projects confidently ship encoding/decoding:
- Golden **decoder conformance** and feature-coverage matrices across implementations.
- Canonical “what differs?” reports for decoders/encoders (pixels, metadata, animation, HDR).
- Reproducible `*.jxlbundle.zip` artifacts for CI failures and bug reports.

JPEG XL is standardized as **ISO/IEC 18181** and has a widely used reference implementation (`libjxl`). The Rust ecosystem now includes **pure-Rust encoders** (e.g., `jxl-encoder`) and wrappers around reference libs; a shared conformance harness reduces fragmentation.

## Proposed crate/workspace shape

- `jxl-conform-ir` — canonical feature and result IR (decode/encode)
- `jxl-conform-runner` — runner that invokes multiple backends (native + pure Rust)
- `jxl-conform-diff` — pixel diff + metadata diff + tolerance profiles (lossy-aware)
- `jxl-conform-fuzz` — corpus/minimization helpers and crash bundling
- `jxl-conform-cli` — `run`, `matrix`, `diff`, `bundle`, `minimize`

### Bundle format: `*.jxlbundle.zip`

- `manifest.json` (backend versions, CPU features, build flags)
- `inputs/` (original jxl + sidecar expected outputs where relevant)
- `results/` (decoded pixels hashes, metadata extracts, encoder outputs)
- `diff/` (pixel diffs / histograms, metadata diffs, first divergence notes)
- `verdict.json` + `explain.md`

## MVP (4–8 weeks)

1. **Decode conformance harness**: run N decoders on a small curated corpus; emit matrix.
2. **Pixel+metadata diff**: deterministic outputs; tolerance profiles for lossy.
3. **Crash/corpus bundling**: single command to minimize and create a `jxlbundle.zip`.

## De-risk plan

- Start with **runner + IR + bundling**; do not “own” the codec—adapters invoke existing libs/crates.
- Use reference implementation as a baseline, but keep room for “allowed differences” profiles.

## Success metrics

- A decoder regression becomes a shareable `jxlbundle.zip` that anyone can replay.
- CI can gate merges on conformance deltas rather than ad-hoc image comparisons.
