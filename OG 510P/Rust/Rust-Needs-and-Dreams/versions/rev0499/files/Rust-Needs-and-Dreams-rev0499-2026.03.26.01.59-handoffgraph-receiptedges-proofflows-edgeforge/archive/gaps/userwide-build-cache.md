# Gap: Build State Topology, Locking, and Reuse Truth

## Summary
Rust has plenty of *ways* to make builds faster, but it still lacks a first-class, reviewable model of **which cache lane is actually in play**. Workspace-local Cargo state, rust-analyzer private target dirs, shared `CARGO_TARGET_DIR` folklore, Cargo-native user-wide caching, compiler-wrapper caches like `sccache`, container-layer caching via `cargo-chef`, and coarse CI blob exchange are all materially different stories.

It also still lacks a first-class, reviewable model of **build state** itself:
- which artifacts are intermediate vs final,
- which build units can be locked independently,
- which directories are safe to share across tools and workspaces,
- which reuse decisions are valid, blocked, stale, or merely heuristic,
- and which workarounds are duplicating state just to avoid contention.

Today, users mostly encounter this territory as folklore:
- “try a separate target directory for rust-analyzer,”
- “set up sccache,”
- “use a shared `CARGO_TARGET_DIR` carefully,”
- “clean the target dir if things get weird,”
- “CI cache blobs help sometimes.”

That is not a durable ecosystem substrate.
The missing contribution is not just another cache backend.
The missing contribution is a **portable build-state contract** that makes layout, locking, reuse eligibility, garbage collection, and exchange policies inspectable.

## Why this matters now
Cargo is no longer treating build-cache structure as an implementation detail.
Upstream work is explicitly converging on:
- a reworked build-dir layout with smaller self-contained units,
- finer-grained locking,
- a first-class user-wide cache,
- and plugin-based read/write cache sources.

That means one of the ecosystem’s highest-leverage opportunities is to define the **review boundary** over that future before every tool, IDE, CI system, and wrapper invents its own private model.

## Ecosystem signals
- The accepted/project-goal work on **Rework Cargo Build Dir Layout** says the current build cache is not easily broken into smaller units, so Cargo often locks the entire build cache; it explicitly calls out `cargo check` vs rust-analyzer contention and names finer-grained caching/locking plus a first-class user-wide cache as the “shiny future.”  
  Source: Rust Project Goals — Rework Cargo Build Dir Layout. https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The Cargo 1.93 development-cycle update says Cargo is exploring a **finer-grained locking scheme** as a user-facing deliverable on top of the build-dir layout work; it also explains the split between a build dir for intermediate artifacts and an artifacts dir for final artifacts.  
  Source: Inside Rust — This development-cycle in Cargo 1.93. https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The Cargo Book now documents **both** `target-dir` and `build-dir`, and explicitly distinguishes final artifacts from intermediate build artifacts. That is a major sign that Cargo’s build-state topology is becoming a public-facing concept.  
  Source: Cargo Book — Build Cache. https://doc.rust-lang.org/cargo/reference/build-cache.html
- rust-analyzer documents `cargo.targetDir` as a way to use a rust-analyzer-specific target directory to avoid lock contention, but at the cost of duplicated build artifacts. That is a direct proof that the ecosystem currently pays for missing shared semantics with duplicated state.  
  Source: rust-analyzer book — Configuration. https://rust-analyzer.github.io/book/configuration
- The earlier user-wide cache goal already framed cross-workspace reuse, reduced disk usage, and more precise cross-job caching as core needs, which means the current build-dir-layout effort is not a niche cleanup but a strategic precursor to wider cache reuse.  
  Source: Rust Project Goals — User-wide build cache. https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

## What is missing
Rust still lacks a standard way to answer questions like:
- “What exact build-state units exist for this workspace and toolchain?”
- “Which ones are lock-compatible for parallel operations?”
- “Which units are shareable across workspaces, CI jobs, or editor sessions?”
- “Why did rust-analyzer duplicate this build instead of reusing it?”
- “Which part of the build state is safe to garbage-collect?”
- “What policy caused this cache import/export/reuse decision?”

Without that layer, even good upstream work risks surfacing as:
- new hidden caches,
- new lock behaviors users cannot inspect,
- new CI integrations that move opaque blobs around,
- and more tooling divergence over what “share the build cache” actually means.

## What “good” looks like
A worthy contribution here would give Rust a shared, inspectable language for build state:
1. **layout truth** — build dirs, artifact dirs, unit identities, and path classes are explicit.
2. **locking truth** — lock domains and conflict classes are visible instead of inferred from “blocking waiting for file lock”.
3. **reuse truth** — a cache hit/miss or “duplicated by policy” decision is explained with reason codes.
4. **exchange truth** — local, user-wide, editor-owned, and CI/remote cache lanes are modeled explicitly.
5. **retention truth** — GC policies attach to units and evidence rather than only to raw directories.

## Contribution shape
The strongest version is **not** “yet another remote cache service.”
It is a reviewable artifact family and reference tool that can sit above Cargo’s evolving layout and below editor/CI/cache integrations.

In other words: Rust needs a **Build State / Cache Topology Kit** more than it needs one more cache daemon.

## Lane-map consequence
Future build-cache revisions should read this gap together with [`design/build-cache-lane-map.md`](../design/build-cache-lane-map.md) and [`design/build-cache-pilot-program.md`](../design/build-cache-pilot-program.md). The missing contribution is not one more universal cache layer; it is a portable boundary that keeps Cargo-native workspace state, editor-private duplication, Cargo-native user-wide reuse, wrapper caches, container layers, and CI/plugin exchange distinct enough to compare honestly.
