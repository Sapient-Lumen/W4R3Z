---
id: P-0436
title: Target-Dir Lease & Shared Cache Coordination Kit — lease manifests, GC receipts, and safer cache sharing above Cargo’s evolving build-dir model
status: idea
domains: [cargo, build, ci, workspace, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://github.com/mozilla/sccache
---

# Problem

Cargo’s build cache and target-dir story is good enough to function but still rough enough that many teams treat it as a semi-sacred black box.

The official Cargo build-dir-layout goal names exactly the problems users feel today:

- coarse locking,
- hard-to-cache internals,
- target-directory sprawl,
- poor GC behavior,
- and awkward shared-cache behavior across workspaces and tools like rust-analyzer.

Cargo’s own docs also make clear that parts of the build-dir layout are internal and subject to change, while the usual user-facing knobs (`CARGO_TARGET_DIR`, `CARGO_BUILD_BUILD_DIR`, wrappers such as `sccache`) do not by themselves provide a portable coordination story.

That means the missing crate is not “replace Cargo caching.”

The missing crate is a **coordination layer** that helps humans and tools reason about cache residency, leases, cleanup, and shared target-dir policies without scraping internals blindly.

# What it provides

- `target-lease.toml` — describes who is allowed to use a shared target/build dir, for which workspace/toolchain/profile/target tuple, and with what retention policy.
- `cache.receipt.json` — records actual cache roots, wrappers, toolchain hashes, workspace identity, and build-dir mode.
- `gc.receipt.json` — records what cleanup happened, why, and what leases were honored or expired.
- `cache-advice.md` — human-readable explanation of target-dir sharing, risks, and suggested policy changes.
- `cargo cache-lease doctor` — explains whether a given config is safe to share, likely to contend, or likely to over-clean.
- `cargo cache-lease gc` — lease-aware cleanup that avoids the usual “just nuke target” habit.
- `cargo cache-lease snapshot` — writes receipts that make CI cache behavior reviewable.

# What the crate should provide other people

1. **A reviewable policy layer** for shared target and build directories.
2. **Lease-aware cleanup** so teams stop relying on blind `cargo clean` or ad hoc deletion scripts.
3. **Receipts for CI and local developer machines** that explain what cache roots and wrappers were active.
4. **A safer bridge** between Cargo target dirs, build dirs, wrappers like `sccache`, and future Cargo build-unit work.
5. **Practical explanations** of cache contention and sharing assumptions.

# Persona / who it’s for

- CI/build engineers
- monorepo and workspace maintainers
- developers juggling multiple local workspaces
- tool authors integrating with Cargo’s build directories

# Users & user stories

- **Workspace maintainer**: “Use a shared target dir without accidentally making cleanup or contention worse.”
- **CI engineer**: “See one receipt for what cache roots, wrappers, and workspace IDs were actually involved in this build.”
- **Developer**: “Explain why this build is contending with rust-analyzer or another Cargo process.”
- **Tool author**: “Coordinate around user-visible policy and receipts instead of scraping internals.”

# Prior art (and why it’s insufficient)

- Cargo documents the target/build dir knobs and explicitly treats much of the layout as internal.
- The Cargo project is actively working on finer-grained build-dir units and shared cache improvements.
- `sccache` is excellent as a compiler wrapper and shared compilation cache, but it is not a workspace lease or GC policy layer.

What remains missing is a **lease/receipt/cleanup layer** that is honest about Cargo internals while still helping users coordinate safely.

# Design goals

1. **Respect Cargo boundaries** — do not depend on unstable internal layout beyond what the crate can observe conservatively.
2. **Lease-first** — shared cache use should be deliberate and reviewable.
3. **GC without fear** — cleanup must be explainable and avoid surprising deletions.
4. **Wrapper-aware** — record how `RUSTC_WRAPPER` and workspace wrappers affect cache behavior.
5. **Future-friendly** — adapt as Cargo introduces finer-grained units and user-wide cache support.

# MVP surface

- Minimal types: `TargetLease`, `CacheReceipt`, `GcReceipt`, `CacheDoctorReport`, `WorkspaceIdentity`
- Minimal functions:
  - `discover_cache_roots()`
  - `write_receipt()`
  - `diagnose_sharing()`
  - `acquire_lease()`
  - `gc_with_leases()`
  - `summarize_contention()`
- Feature flags:
  - `serde`
  - `sccache`
  - `ci`
  - `rust-analyzer`
  - `fs-events`

# Compatibility story

- Works with today’s target-dir and build-dir knobs.
- Records wrappers such as `sccache` without trying to replace them.
- Can stay conservative where Cargo layout details are internal.
- Should evolve to understand future build-dir units rather than pretending the old layout is permanent.

# Conformance & fixtures

- Fixtures for one workspace, many workspaces, shared target dir, separate build dir, wrapper/no-wrapper, and simulated contention.
- Goldens for doctor findings such as “likely global clean blast radius” and “lease mismatch across workspaces.”
- Cleanup fixtures ensuring that lease-aware GC removes only expected material.
- Receipts from local and CI-like environments.

# Path to boring stability

- Stabilize the lease and receipt formats before adding too much automation.
- Keep deletion behavior conservative and reversible where possible.
- Prefer diagnosis and receipts over intrusive active coordination at first.
- Expand into richer contention observation only after the artifact model feels trustworthy.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that discover active cache roots, emit a receipt, explain sharing risks, and perform conservative lease-aware cleanup for shared target directories.

# De-risk plan

1. Start as a diagnosis and receipt tool.
2. Add leases and cleanup only where the crate can stay conservative.
3. Model `sccache` and wrapper context explicitly but lightly.
4. Track Cargo build-dir-layout work so schema assumptions stay modest.

# Non-goals

- Not a replacement for Cargo’s cache implementation.
- Not a distributed build cache service.
- Not a promise to understand every internal Cargo artifact.
- Not a performance profiler.

# Architecture & API sketch

```rust
pub struct CacheReceipt {
    pub workspace: WorkspaceIdentity,
    pub target_dir: std::path::PathBuf,
    pub build_dir: Option<std::path::PathBuf>,
    pub wrappers: Vec<WrapperInfo>,
    pub leases: Vec<TargetLease>,
}

pub fn discover_cache_roots(cx: &RunContext) -> Result<CacheReceipt>;
pub fn diagnose_sharing(receipt: &CacheReceipt) -> Result<CacheDoctorReport>;
pub fn gc_with_leases(receipt: &CacheReceipt, policy: &GcPolicy) -> Result<GcReceipt>;
```

Bundle draft: `target-lease.toml`, `cache.receipt.json`, `gc.receipt.json`, `cache-advice.md`, `notes.md`.

# Security / safety model

- Avoid deleting content without an explicit lease/policy decision.
- Record path roots and wrapper context precisely.
- Permit path redaction in exported receipts.
- Distinguish observed facts from inferred advice.

# Maintenance & governance plan

- Track Cargo build-dir-layout evolution and user-wide-cache efforts.
- Keep internal-layout assumptions minimal and easy to revise.
- Maintain a compact doctor-finding taxonomy.
- Prefer stable environment and config surfaces over fragile path heuristics.

# Milestones

## 0.1
- receipt writer
- doctor checks
- conservative lease format

## 0.2
- lease-aware GC
- wrapper-aware cache summaries
- CI export recipes

## 1.0
- stable schemas
- richer workspace coordination
- integration with newer Cargo cache units where possible

# Open questions

- What is the smallest useful lease model that still prevents common cleanup mistakes?
- How much contention diagnosis can be done without platform-specific process inspection?
- Should the crate model wrapper cache roots as first-class leases or only as receipt metadata initially?

# Sources

- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- `sccache`: https://github.com/mozilla/sccache
