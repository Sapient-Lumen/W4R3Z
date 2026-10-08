---
id: P-0082
title: Realtime Audio Graph Standard Kit — real-time safe DSP graphs with a shared node model + conformance suite
status: idea
domains: [audio, realtime, dsp, media]
last_reviewed: 2026-03-04
evidence:
  - https://crates.io/crates/cpal
  - https://docs.rs/cpal
  - https://crates.io/crates/auxide
  - https://lib.rs/crates/pp-audiograph
---

## What it should provide others

A standard, dependable foundation to build:
- synths and audio effects,
- DAW-like processing chains,
- live audio tools,
- and audio plugins/hosts,

…without each team reinventing the “real-time audio graph” wheel.

The kit should give:

- a **real-time safe graph kernel** (no allocation on the audio thread),
- a **shared node model** (ports, buffers, parameter automation),
- hot-swapping graphs under real-time constraints,
- deterministic offline rendering (for tests, exports),
- and a conformance suite for “this graph is actually real-time safe.”

## Why this is missing / the pain

Rust has good building blocks for audio I/O (e.g., `cpal`), and emerging graph kernels exist, but:
- there is no widely adopted *standard* graph/node model,
- real-time safety constraints are easy to violate accidentally,
- and testing audio graphs for determinism and RT-safety is still niche.

A “standard kit” would let disparate crates interoperate (nodes, filters, generators) and give authors confidence they’re not shipping glitchy or unsafe real-time behavior.

## Core deliverables (MVP)

### 1) Graph kernel with RT-safety invariants
- explicit separation: control thread vs audio thread
- command queue for graph mutations (bounded, lock-free where possible)
- fixed-size buffer pools / arena allocation prepared ahead of time
- hard ban on allocations in the audio callback (with optional runtime checks in debug)

### 2) Node model + parameter automation
- audio-rate and control-rate ports
- parameter smoothing and automation lanes
- sample-accurate event scheduling (optional in MVP, but design for it)

### 3) Deterministic offline renderer
- same graph, same seed, same output bytes
- golden-output tests for nodes and entire graphs

### 4) Conformance suite
- stress tests for graph mutation while streaming
- “no allocation” checks (debug instrumentation)
- timing/jitter benchmarks (best effort; platform dependent)
- fixtures that plugin authors can run in CI

## Design: interoperability-first

### “Node ABI”
Not a Rust ABI — a *conceptual* ABI:
- node metadata schema (ports, params)
- stable serialization of graph topology (so graphs can be saved/loaded)
- optional dynamic plugin boundary: WASM nodes or serialized boundary nodes

### Layering
- `audiograph-core` (no-std friendly kernel primitives where possible)
- `audiograph-std` (threads, channels, file IO)
- `audiograph-cpal` adapter
- optional: `audiograph-wasm` node sandboxing

## Related work (and why it’s not enough)
- `cpal` solves cross-platform audio I/O, but does not define a DSP graph model.  
- Existing graph kernels show promise, but the missing piece is a common model + conformance suite that makes it easy to build interoperable node libraries and test real-time safety.

## Adoption plan
1. Ship the kernel + node traits + offline renderer.
2. Publish a small standard node pack (gain, mixer, biquad, oscillator).
3. Add conformance suite and CI recipes.
4. Encourage a “node ecosystem” (third-party nodes implementing the standard model).

## Sustainability hooks
- Keep the core minimal and stable.
- Put “extras” (file formats, GUIs, plugin hosts) in separate crates.
- Invest in conformance and golden fixtures to avoid regressions.
