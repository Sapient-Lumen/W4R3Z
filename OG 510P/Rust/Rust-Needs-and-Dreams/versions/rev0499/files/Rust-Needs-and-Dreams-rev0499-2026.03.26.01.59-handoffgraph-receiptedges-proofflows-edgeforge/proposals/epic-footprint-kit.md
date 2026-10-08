# Epic proposal: Footprint Kit

## Thesis
Rust already has strong point tools for artifact size and memory analysis.
The next high-leverage contribution is not another one-off “make it smaller” utility.
It is a **shared footprint contract** that turns budget declarations, measurement coverage, deltas, and caveats into durable engineering artifacts.

That would be a worthy ecosystem contribution because it helps:
- embedded teams review RAM/FLASH/stack constraints without burying truth in linker scripts and screenshots,
- Wasm teams compare retained-size regressions with feature/profile context,
- library and application teams gate native binary growth in CI with explicit reasons rather than vague “release got bigger” panic,
- release managers attach resource evidence to shipped artifacts,
- and maintainers connect codegen/monomorphization growth to real deployment budgets.

## Why now
The timing is stronger now because official Rust/Cargo work is making the resource problem more explicit:
- the 2025 State of Rust survey still lists resource usage — especially slow compile times and storage usage — among the biggest productivity problems;
- the 2024 survey already called out high disk usage of compiler artifacts;
- Cargo’s build-dir-layout goal explicitly ties its new layout to GC of target directories and a future cross-workspace shared build cache;
- Cargo build-analysis / `cargo report` work is making compile-workflow evidence more machine-usable;
- Cargo/build-std work explicitly names code-size-oriented standard-library builds as a real use case;
- and the ecosystem still relies on point tools like `cargo-bloat`, `twiggy`, `cargo-call-stack`, `cargo-binutils`, `dhat`, and allocator-specific profilers rather than a common review boundary.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://rustwasm.github.io/book/reference/code-size.html
- https://docs.rs/crate/cargo-bloat/latest/source/
- https://docs.rs/crate/cargo-call-stack/0.1.0
- https://doc.rust-lang.org/beta/unstable-book/compiler-flags/emit-stack-sizes.html
- https://docs.rs/dhat/latest/dhat/

## Proposed shape
Ship a narrowly scoped reference stack:
1. schemas for `footprint-budget/v0`, `footprint-measurement-report/v0`, `footprint-diff-report/v0`, `footprint-pack/v0`
2. adapters for Cargo profiles, `cargo-bloat`, `twiggy`, `cargo-call-stack`, `cargo-llvm-lines`, `cargo-binutils`, linker-map inputs, and optional runtime allocation profilers
3. explicit capability/coverage reporting for native vs Wasm vs embedded vs allocator-specific lanes
4. CI examples showing budget review across release binaries, firmware, and Wasm artifacts
5. guidance for attaching raw evidence without flattening incompatible tools into one fake metric

The winning version is boring, adapter-heavy, and explicit about platform limits.
It should make today's tools legible together rather than replacing them.

## Initial pilots
- one Cortex-M firmware with RAM/FLASH/stack budgets plus linker-layout evidence
- one Wasm package with retained-size diffing and export-surface-aware budget checks
- one CLI or service binary with native `.text` / symbol-growth gates in CI
- one workspace correlating monomorphization growth with release-size regressions before and after a dependency upgrade

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - distinguish section bytes, retained size, stack bounds, and allocation evidence
2. **v0.2 adapters**
   - normalize native / Wasm / embedded tool outputs
   - record unsupported or partial coverage honestly
3. **v0.3 cross-kit integration**
   - integrate with Config Set, Device Lab, Release Pipeline, and Migration artifacts
   - support baseline/diff workflows across releases and target profiles
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one deployment domain

## Success metrics
- Teams can review footprint changes as explicit budgeted dimensions rather than screenshots or local tables.
- Native, Wasm, and embedded evidence can travel in one pack without pretending they were measured the same way.
- Tool/platform limitations are visible instead of being hidden in maintainer memory.
- Release and migration reviews can point to durable footprint artifacts.
- Resource regressions become explainable deltas instead of generic “binary got bigger” anxiety.

## Archive fit
This proposal fills a real hole in the concise archive.
The repo already has strong proposals for performance, configuration selection, release evidence, device labs, migration, and cross-toolchain plumbing.
Footprint Kit adds the missing **resource-budget substrate** that ties those lanes back to concrete deployment constraints.


## Current archive decision
The next credible move is no longer “just make a better size tool.” It is to run Footprint Kit as the footprint half of a shared **Resource Evidence Stack** with Perf Labs, using a ranked pilot program that starts with compile/storage lanes and release-artifact lanes before widening to constrained targets, runtime allocation, and federated review. See [`../design/resource-evidence-pilot-program.md`](../design/resource-evidence-pilot-program.md).
