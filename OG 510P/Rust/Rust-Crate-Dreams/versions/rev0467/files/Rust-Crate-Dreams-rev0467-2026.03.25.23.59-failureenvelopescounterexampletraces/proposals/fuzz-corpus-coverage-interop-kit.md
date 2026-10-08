---
id: P-0243
title: Fuzz Corpus & Coverage Interop Kit — portable corpora, minimization pipelines, and evidence bundles for cargo-fuzz and beyond
status: idea
domains: [security, testing, fuzzing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://rust-fuzz.github.io/book/cargo-fuzz.html
  - https://rust-fuzz.github.io/book/cargo-fuzz/tutorial.html
  - https://crates.io/crates/cargo-fuzz
---

## What it should provide others

A **standard way to package, exchange, minimize, and replay fuzz corpora** across teams and CI systems, without committing gigabytes of seeds or losing provenance.

The crate should provide:

- **Corpus bundle format**: `*.fuzzbundle.zip` containing
  - seeds (optional; can be remote-addressed)
  - coverage summaries
  - crash artifacts + minimized repro inputs
  - target metadata (features, sanitizers, rustc version)
  - provenance (where did these seeds come from?)
- **Adapters** for common engines:
  - `cargo-fuzz`/libFuzzer first
  - future: AFL++, honggfuzz, Jazzer-style harnesses
- **Minimization + curation pipeline**:
  - corpus minimization (coverage-preserving)
  - crash dedupe + bucketing
  - regression test extraction (`tests/regressions/*.bin`)

## Why this is still missing

`cargo-fuzz` is the recommended Rust fuzzing frontend and already supports workflows like corpus minimization (`cmin`) and coverage reports, but there is no shared, portable artifact standard for “this corpus + these crashes + this coverage + how to replay it.”

- cargo-fuzz is positioned as the recommended tool for fuzz testing Rust code. https://rust-fuzz.github.io/book/cargo-fuzz.html
- The Rust Fuzz Book documents corpus-first workflows and coverage generation. https://rust-fuzz.github.io/book/cargo-fuzz/coverage.html
- `cargo fuzz cmin` exists as a corpus minimization primitive. https://crates.io/crates/cargo-fuzz

## Design outline

### 1) Bundle spec

- `manifest.json`:
  - crate + target name
  - engine + version
  - compilation flags + sanitizers
  - corpus digest(s)
- `corpus/`:
  - seeds, optionally sharded
- `crashes/`:
  - minimized inputs + metadata (stack hash, sanitizer output)
- `coverage/`:
  - summary + optional raw profiles
- `replay/`:
  - one-command replay scripts (engine-specific)

### 2) Cargo UX

- `cargo fuzzbundle pack <target>`
- `cargo fuzzbundle cmin <target> --budget ...`
- `cargo fuzzbundle replay <bundle>`

### 3) Interop hooks

- P-0240 sandbox policies for fuzzing runs
- P-0242 reproducible builds for fuzz harness artifacts

## MVP (4–6 weeks)

1. `cargo-fuzz` adapter: pack/unpack/replay.
2. Corpus minimization wrapper + stable coverage summary.
3. Crash bucketing (stack hash + sanitizer class).
4. CI recipe: upload bundles per PR and on main.

## Long-term extensions

- standardized “seed provenance” formats (generators, grammars, harvested traffic)
- cross-engine corpus conversion where practical
- corpus quality scoring (coverage delta per byte)
