---
id: P-0151
title: SIMD Kernel Suite & Verification Kit
status: idea
domains: [performance, simd, compiler, numeric, multimedia, ml, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://doc.rust-lang.org/std/simd/index.html
  - https://github.com/rust-lang/portable-simd
  - https://doc.rust-lang.org/std/simd/index.html#what-is-portable
---

# Problem

Rust’s **portable SIMD** API (`std::simd`) exists but remains **nightly-only and experimental** today. That creates a recurring ecosystem gap:

- Many crates re-implement similar kernels (hashing, parsing, DSP, image ops, ML primitives) with ad-hoc intrinsics.
- Verification is weak: correctness across architectures and lane counts is hard.
- Performance regressions go unnoticed because benchmarks aren’t standardized.

We’re missing a **shared kernel library + verification harness** that can be used both *now* (via stable fallbacks + optional nightly acceleration) and later as portable SIMD stabilizes.

# What it should provide

## 1) A curated, reusable kernel catalog (with stable fallbacks)

Kernels that appear everywhere:

- bytes/UTF-8 scanning (find, classify, whitespace)
- base64 / hex decode
- checksum / hashing primitives (non-crypto fast hash building blocks)
- image kernels (RGBA swizzle, alpha blend, convolution)
- audio/DSP kernels (biquad, FIR blocks)
- ML primitives (GEMM microkernels, activation blocks, layernorm)

Each kernel has:
- Pure stable scalar baseline
- Optional architecture-specialized fast path (x86_64/arm64/wasm simd)
- Optional `portable_simd` fast path (nightly feature gate)

## 2) A correctness & portability harness

- Property tests + fuzzing harness per kernel
- Cross-arch corpus replay (“golden inputs” + “golden outputs”)
- Differential testing: scalar vs simd outputs must match bit-for-bit (or within explicit eps)
- A `kernel-report.json` for CI and regressions

## 3) Benchmark standardization

- A uniform benchmark driver (`criterion`-based) with:
  - input distributions specified in JSON
  - warmup protocols standardized
- Output `bench-report.json` with normalized metrics

## 4) Adoption-first API design

A small, stable API surface:

- `kernel::X::run(input, output, params)` in `no_std`-friendly shapes
- Feature flags:
  - `simd-portable` (nightly)
  - `simd-x86`, `simd-neon`, `simd-wasm`
- A capability query function so downstream crates can log which backend is active.

# MVP scope (2–4 weeks)

- Pick 3 kernels with big wins and clear semantics:
  1) `find_byte`/`find_any_of`
  2) `hex_decode`
  3) `rgba_swizzle`
- Implement scalar baseline + one specialized backend (x86 or neon)
- Add harness:
  - fuzz + corpus replay
  - `kernel-report.json`

# v1 scope (2–3 months)

- Expand to 10–15 kernels across domains
- Add “portable simd” implementations behind `portable_simd` feature gate
- CI matrix:
  - x86_64 + aarch64 + wasm32 (where possible)
- Publish “kernel cookbook” docs for downstreams

# Why it’s worthy

This is the *library* that prevents the ecosystem from fragmenting into dozens of half-verified SIMD code paths. It provides shared, audited kernels that downstream crates can depend on, and it supports Rust itself by stress-testing portable SIMD semantics and performance as it moves toward stabilization.
