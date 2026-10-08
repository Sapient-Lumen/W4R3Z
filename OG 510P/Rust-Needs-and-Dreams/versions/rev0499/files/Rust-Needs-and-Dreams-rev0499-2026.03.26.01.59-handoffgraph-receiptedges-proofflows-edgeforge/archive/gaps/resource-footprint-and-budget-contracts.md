# Gap: resource footprint and budget contracts

## What is missing
Rust has many ways to tune and inspect produced artifacts, but it still lacks a **shared footprint contract**.

Today there is no standard way to describe, exchange, and diff:
- which resource dimensions matter for a crate or binary (`.text`, `.rodata`, `.data`, `.bss`, Wasm bytes, stack, heap/allocation behavior, startup-related runtime profile),
- which target / profile / feature / allocator / linker assumptions those numbers depend on,
- which measurements came from static analysis versus runtime profiling,
- and which changes are acceptable regressions versus hard budget violations.

That missing layer matters because Rust's deployment story spans embedded, Wasm, CLI tools, desktop apps, services, plugins, and constrained devices.
The same crate often cares about very different resource limits across those environments, yet the evidence still lives in one-off CI scripts, linker map files, screenshots, local notes, and tool-specific output formats.

Sources:
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/beta/unstable-book/compiler-flags/emit-stack-sizes.html
- https://docs.rs/crate/cargo-bloat/latest/source/
- https://rustwasm.github.io/book/reference/code-size.html
- https://rustwasm.github.io/book/reference/tools.html
- https://docs.rs/crate/cargo-call-stack/0.1.0
- https://docs.rs/crate/cargo-llvm-lines/latest
- https://docs.rs/dhat/latest/dhat/
- https://docs.rs/crate/cargo-binutils/latest
- https://docs.rust-embedded.org/book/unsorted/speed-vs-size.html
- https://docs.rust-embedded.org/embedonomicon/memory-layout.html
- https://raw.githubusercontent.com/rust-lang/surveys/main/surveys/2024-annual-survey/report/annual-survey-2024-report.pdf

## The current seam is awkward
Rust already has real footprint tooling and knobs:
- Cargo profiles expose `opt-level`, `lto`, `strip`, `panic`, `incremental`, and `codegen-units`;
- `cargo-bloat` shows which symbols occupy executable space;
- `twiggy` analyzes retained Wasm size and why code is retained;
- `cargo-call-stack` computes whole-program stack usage when LLVM stack-size metadata is available;
- `cargo-llvm-lines` exposes monomorphization/codegen growth that often drives both compile-time and binary-size pain;
- `cargo-binutils` and linker outputs expose section and object-level views;
- `dhat` and jemalloc profiling expose runtime allocation behavior;
- embedded runtime/linker setups explicitly encode memory-region and stack placement constraints.

But each tool answers a different question, on different targets, with different limits:
- `twiggy` is Wasm-specific;
- `cargo-bloat` focuses on ELF / Mach-O style native binaries;
- `emit-stack-sizes` is an unstable compiler flag and LLVM only emits the metadata for ELF object formats;
- allocation profilers depend on particular allocators or instrumentation styles;
- linker-map interpretation is highly target- and toolchain-specific.

So the problem is not that Rust has no footprint tools.
The problem is that there is no durable way to say:
- “these are the budgeted resource dimensions for this artifact,”
- “these target/profile/feature slices were actually measured,”
- “these numbers came from static stack analysis, these from runtime allocation sampling,”
- or “this release grew 11% in `.text` but stayed within the agreed envelope.”

Sources:
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/beta/unstable-book/compiler-flags/emit-stack-sizes.html
- https://docs.rs/crate/cargo-bloat/latest/source/
- https://rustwasm.github.io/book/reference/code-size.html
- https://docs.rs/crate/cargo-call-stack/0.1.0
- https://docs.rs/crate/cargo-llvm-lines/latest
- https://docs.rs/dhat/latest/dhat/
- https://docs.rs/crate/cargo-binutils/latest
- https://docs.rust-embedded.org/embedonomicon/memory-layout.html

## Why this matters
This gap is broader than microcontroller tuning.
It affects:
1. **embedded Rust** — section placement, RAM/FLASH splits, stack placement, and zero-cost overflow defenses are first-order deployment constraints;
2. **Wasm** — Rust's own Wasm guidance says size profiling should guide shrinking efforts, and points people to `twiggy` for call-graph-driven size analysis;
3. **native binaries** — profile settings and symbol-level bloat tools exist, but teams still lack one reviewable artifact for release-size budgets;
4. **compile-time pressure** — monomorphization growth and codegen duplication show up in `cargo-llvm-lines`, but are rarely connected back to explicit artifact budgets;
5. **runtime memory use** — heap profilers and allocator-specific introspection exist, but not as a portable lane that can travel through CI/review/release evidence;
6. **ecosystem adoption** — the 2024 survey explicitly named large binary size of compiled artifacts as a pain point, which means resource footprint is not a niche embedded-only concern.

Sources:
- https://docs.rust-embedded.org/embedonomicon/memory-layout.html
- https://docs.rust-embedded.org/book/unsorted/speed-vs-size.html
- https://rustwasm.github.io/book/reference/code-size.html
- https://docs.rs/crate/cargo-llvm-lines/latest
- https://docs.rs/dhat/latest/dhat/
- https://raw.githubusercontent.com/rust-lang/surveys/main/surveys/2024-annual-survey/report/annual-survey-2024-report.pdf

## What “good” looks like
A worthy contribution here is **not** “one universal size tool.”
It is a shared footprint boundary:
- one `footprint-budget/v0` describing which resource dimensions matter, on which targets/profiles/features, and what the allowed envelopes are;
- one `footprint-measurement-report/v0` recording what tools ran, which measurements are static versus runtime, and which resource dimensions are covered or unsupported;
- one `footprint-diff-report/v0` summarizing regressions/improvements between baselines with explicit reason codes;
- and one `footprint-pack/v0` bundle for CI, PR review, release engineering, embedded bring-up, and downstream archaeology.

That would let Cargo profile choices, linker/map outputs, symbol bloat analysis, Wasm retained-size analysis, stack analysis, and allocation profiling participate in one reviewable story instead of staying as disconnected local rituals.
