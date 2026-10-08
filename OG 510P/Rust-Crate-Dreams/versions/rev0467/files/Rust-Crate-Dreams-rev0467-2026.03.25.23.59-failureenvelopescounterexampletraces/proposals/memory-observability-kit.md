---
id: P-0084
title: Memory Observability Kit — capture scopes, symbolization fidelity, allocator evidence, and regression gates
status: idea
domains: [devtools, profiling, memory, observability, performance, allocator, supportiveness]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://docs.rs/leaktracer/latest/leaktracer/
  - https://docs.rs/dhat/latest/dhat/
  - https://docs.rs/dhat/latest/dhat/struct.Profiler.html
  - https://docs.rs/tikv-jemalloc-ctl/latest/tikv_jemalloc_ctl/
  - https://docs.rs/jemalloc_pprof/latest/jemalloc_pprof/
---

# Problem

Rust can be “memory-hungry by default” in many real systems: fragmentation, unexplained RSS growth, and allocation hotspots are common operational pain points. Teams often stitch together allocators, profilers, and platform tools ad hoc, and the outputs don’t compose into a clean workflow: “capture → attribute → compare → regressions in CI → share with others”.

There are good point solutions (e.g. allocator-based tracing such as `leaktracer`, and platform approaches such as BPFtrace stack capture), but no cohesive *Rust-native* kit that makes memory investigation and regression testing routine.

Sources: official Rust survey/vision material plus current `leaktracer`, `dhat`, `tikv-jemalloc-ctl`, and `jemalloc_pprof` docs.

# Users & user stories

- **Backend/SRE**: “I need a memory regression gate in CI that fails PRs if p95 allocation or peak RSS jumps.”
- **Perf engineer**: “I want allocation flamegraphs with symbolized Rust frames and minimal setup.”
- **Library author**: “I want to ship an opt-in feature that makes it easy for users to produce a shareable memory report.”
- **Embedded/edge**: “I need to know worst-case allocation behavior and prove no leaks.”

# Prior art (and why it’s insufficient)

- **Allocator tracers** like `leaktracer`: very useful and plug-and-play, but typically focus on ‘who allocated’ rather than a full workflow including regression baselines and shareable artifacts. Sources: leaktracer repo + blog post.
- **General profilers** (`dhat`, allocator-native heap dumps, pprof-compatible tooling, etc.): powerful but fragmented and not “cargo-native”, often difficult to apply consistently across teams.
- **Allocator introspection / dump tooling** (`tikv-jemalloc-ctl`, `jemalloc_pprof`) is valuable substrate, but still not a shareable capture-and-regression workflow by itself.

# Design goals

1. **One-command capture**: `cargo mem capture --profile prod-like --seconds 30 --out report.memz`
2. **Multi-backend**: allocator-hook backend (portable), scoped heap-profiler imports, allocator-introspection/dump imports, and room for later platform-specific collectors.
3. **Actionable attribution**: allocation hotpaths, live allocations, size class histograms, fragmentation hints.
4. **Regression testing**: compare reports, produce diff summaries, and CI exit codes.
5. **Shareable artifact**: a single bundle (`.memz`) containing raw samples + symbol maps + metadata + rendered HTML/JSON summaries.
6. **Low-overhead modes**: sampling and “large alloc only” triggers.

# Non-goals

- Replacing all system profilers.
- Guaranteeing perfect call stacks without debug symbols.
- Being a GC (this is an observability kit).

# What it should hand other people

A real `0.1` in this lane should hand another engineer more than a raw profile file.
It should make it cheap to exchange:

- a **capture-scope policy**,
- a **symbolization-fidelity report**,
- a **backend-capability receipt**,
- a **regression-gate policy**,
- a **redaction profile**,
- a **memory-check report**,
- and a **memory diff**.

That is the smallest artifact layer that keeps “memory profile attached” from meaning five totally different things.

# Architecture & API sketch

**Crates:**
- `memobs-core`: artifact format, symbolization schema, diffing, report rendering.
- `memobs-alloc`: allocator shim (compatible with global allocator override); supports sampling.
- `memobs-ebpf`: optional Linux-only collector leveraging BPF tooling; integrates with frame pointers where available.
- `cargo-memobs`: CLI subcommand.

**Artifact format:**
- `meta.json` (env, git sha, rustc version, features)
- `samples.bin` (compact)
- `symbols/` (optional split DWARF mappings, build-ids)
- `report.html`, `report.json`

**API for libraries/apps:**
- `memobs::guard()` to start/stop capture with minimal invasiveness
- `memobs::mark("phase")` for phase-based breakdown

# Security / safety model

- Artifacts can contain path names and symbol info; provide redaction options (trim paths, hash paths).
- If eBPF backend used, require explicit enablement and document privilege needs.

# Maintenance & governance plan

- Keep default backend portable (allocator-based) and make eBPF optional.
- Provide stable artifact schema with versioning.
- Maintain a “known pitfalls” doc and a cookbook per platform.

# Milestones

1. MVP: allocator backend + artifact bundle + HTML summary + `cargo mem capture` and `cargo mem diff`.
2. Symbolization improvements and “top allocations” tables.
3. CI integration + GitHub Action.
4. Optional eBPF backend (Linux) and adapters for popular external tools.

# Open questions

- Best default sampling algorithm to balance overhead vs accuracy.
- How to provide accurate stacks across LTO/strip scenarios.
- How to keep the artifact small while retaining enough evidence.

# Sources

- https://github.com/veeso/leaktracer
- https://blog.veeso.dev/blog/en/leaktracer-a-rust-allocator-to-trace-memory-allocations/
- https://readyset.io/blog/tracing-large-memory-allocations-in-rust-with-bpftrace
- https://ohadravid.github.io/posts/2024-12-state-of-the-crates/
