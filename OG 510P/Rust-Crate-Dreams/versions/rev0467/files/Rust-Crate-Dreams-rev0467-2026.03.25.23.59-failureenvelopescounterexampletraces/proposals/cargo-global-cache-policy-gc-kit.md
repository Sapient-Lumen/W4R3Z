---
id: P-0480
title: Cargo Global Cache Policy & GC Receipt Kit — cache inventories, dry-run cleanup plans, exemption ledgers, and cleanup receipts
status: idea
domains: [cargo, cache, storage, ci, build-performance, devtools]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/guide/cargo-home.html
  - https://doc.rust-lang.org/cargo/reference/build-cache.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  - https://crates.io/crates/cargo-cache
---

# Problem

Rust teams have complained for years about resource usage, and the 2025 State of Rust survey still reports **slow compile times and storage usage** as a major productivity problem.

Cargo finally has real global-cache garbage-collection substrate:

- automatic garbage collection for global caches was stabilized in Rust 1.88,
- `cache.auto-clean-frequency` is a real stable configuration surface,
- nightly Cargo documents manual `cargo clean gc -Zgc` controls for age and size,
- and Cargo’s cache-locking model is now explicit enough that cache mutation can be coordinated conservatively.

That is meaningful progress, but it still does **not** give ordinary teams a boring workflow for questions like:

- what is actually taking space in this developer or CI cache,
- which caches are safe to let Cargo evict and which ones should be kept warm,
- what would a cleanup do *before* we do it,
- how should shared runners or devcontainers adopt GC settings without surprising users,
- and how do we compare cache policy and cleanup outcomes across toolchain changes?

Today the workflow is still mostly:

- look at `du` output,
- maybe install `cargo-cache`,
- maybe let Cargo auto-clean opportunistically,
- maybe run nightly GC commands by hand,
- and maybe rediscover a month later that the space budget, retention rules, and exemptions were never written down.

The missing crate is not another ad hoc deleter.

The missing crate is a **Cargo global cache policy & GC receipt kit**: a Cargo-adjacent crate that turns Cargo-home cache management into a durable **inventory, dry-run cleanup plan, exemption ledger, and diffable cleanup receipt**.

# What it provides

- `cache-policy.toml` — desired retention and budget policy, including environment class (`developer-laptop`, `shared-ci`, `ephemeral-container`), age/size thresholds, and “do not evict” exemptions.
- `cache-inventory.json` — normalized inventory of Cargo-home caches: registry sources, crate archives, indexes, git db/checkouts, last-access buckets when observable, and size summaries.
- `gc-plan.json` — dry-run plan classifying entries as `keep`, `eligible-auto-gc`, `eligible-manual-gc`, `exempt`, `needs-review`, or `toolchain-compat-risk`.
- `cache-surface.receipt.json` — records whether the plan concerns Cargo-home global caches, target-dir final artifacts, build-dir intermediates, or a future cache surface.
- `recovery-obligation.report.json` — classifies what an eviction means: local recreation, redownload, plugin fetch, or manual review.
- `cache-exemptions.toml` — explicit keep-warm rules for unusual situations like slow links, alternate registries, or old toolchain interoperability.
- `gc.receipt.json` — records the exact Cargo/toolchain/config context, the policy used, and what cleanup was performed or proposed.
- `cache-diff.json` — compare two inventories or receipts to classify `grew`, `shrunk`, `new-class`, `policy-changed`, `exemption-added`, and `unexpected-regrowth`.
- `cargo cache-policy scan` — collect one inventory without mutating anything.
- `cargo cache-policy plan` — compute a dry-run cleanup and explain which rule made each entry eligible or exempt.
- `cargo cache-policy diff <old> <new>` — compare two inventories or cleanup receipts.
- `cargo cache-policy doctor` — flag suspicious mixed-toolchain situations, disabled auto-clean, or policy/runtime mismatches.
- `*.cargocache.zip` — portable support artifact for CI runners, devcontainers, and “why is Cargo using 40 GiB here?” tickets.

# What the crate should provide other people

1. **A boring inventory** of Cargo-home storage, not just a raw directory-size dump.
2. **A dry-run review surface** before any cleanup happens.
3. **A policy-and-exemption layer** so organizations can be explicit about warm-cache tradeoffs.
4. **A recovery-obligation report** so “space reclaimed” does not hide who later pays rebuild or redownload cost.
5. **A cache-surface receipt** so Cargo-home GC, target-dir cleanup, and future user-wide caches do not get flattened together.
6. **A diffable receipt** for comparing cache behavior across toolchain, config, and environment changes.
7. **A bridge** between Cargo’s growing GC substrate and ordinary storage hygiene.

# Persona / who it’s for

- developers on laptops or small SSDs
- CI/platform engineers running shared Cargo caches
- maintainers of devcontainers, remote builders, or ephemeral build farms
- teams that need to explain storage budgets without resorting to shell folklore

# Users & user stories

- **Developer**: “Tell me what in my Cargo home is safe to clean, what will likely be re-downloaded, and what should stay.”
- **CI owner**: “Give me a policy file and dry-run receipt before I change cache retention on shared runners.”
- **Release/platform engineer**: “Compare cache growth before and after a toolchain upgrade or policy rollout.”
- **Support engineer**: “Attach one redacted artifact showing cache classes, settings, and why auto-clean did or did not run.”

# Prior art (and why it’s insufficient)

- Cargo now has stable automatic global-cache garbage collection, but that is still mostly a built-in maintenance behavior, not a human review artifact.
- Nightly `cargo clean gc -Zgc` offers real age/size controls, but it is still a command surface, not a durable inventory/policy/receipt workflow.
- `cargo-cache` is useful for sizing and selective cleanup, proving demand, but it is not aligned to Cargo’s newer GC policy vocabulary and does not provide a durable policy/diff/receipt layer.
- `cargo-sweep` is valuable for `target/` cleanup, but that is a different surface from Cargo-home registry/git cache governance.

What remains missing is a **policy + dry-run + receipt layer** above Cargo’s cache-management substrate.

# Design goals

1. **Policy-first** — make retention and exemptions reviewable before deletion.
2. **Cargo-grounded** — use Cargo’s own cache classes and terminology wherever possible.
3. **Dry-run by default** — no surprising deletions.
4. **Storage honest** — distinguish “space can be recovered” from “space can be recovered without likely redownload pain.”
5. **Recovery explicit** — keep rebuild, redownload, plugin-fetch, and unknown recovery classes separate.
6. **Surface honest** — keep Cargo-home GC distinct from target/build-dir housekeeping and future user-wide caches.
7. **Mixed-environment aware** — make old-toolchain and offline-heavy caveats explicit.

# MVP surface

- Minimal types: `CachePolicy`, `CacheInventory`, `GcPlan`, `CacheExemption`, `GcReceipt`, `CacheDiff`, `CacheBundle`
- Minimal functions:
  - `scan_cache_inventory()`
  - `build_gc_plan()`
  - `diff_cache_receipts()`
  - `write_cache_bundle()`
  - `doctor_cache_policy()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `nightly-gc`
  - `ci`

# Compatibility story

- Works on stable Cargo first for inventory, policy explanation, and auto-clean configuration analysis.
- Integrates with nightly manual GC controls when available, but should still be useful without them.
- Must preserve mixed-toolchain caveats because Cargo’s own docs warn that older versions may interact differently with access tracking and cache cleanup.
- Should remain useful even if Cargo later stabilizes more manual GC controls, because reviewable policy and receipts still live above raw deletion commands.

# Conformance & fixtures

- One fixture for a small developer cache with a few registry sources and crate archives.
- One fixture for a shared CI cache with large git db/checkouts and explicit exemptions.
- One fixture where offline-heavy policy keeps redownload-only entries longer than locally recreatable ones.
- One fixture where target-dir cleanup is explicitly kept separate from Cargo-home GC.
- One fixture where future user-wide build-cache/plugin recovery remains manual-review-only.
- One fixture where auto-clean is effectively disabled or misconfigured.
- One fixture where mixed old/new Cargo use requires a `toolchain-compat-risk` warning.
- Goldens for `eligible-auto-gc`, `eligible-manual-gc`, `exempt`, `needs-review`, `unexpected-regrowth`, and explicit recovery classes.

# Path to boring stability

- Stabilize inventory and plan vocabulary before supporting real mutation.
- Keep the first version focused on scanning, planning, diffing, and support bundles.
- Treat actual deletion as optional and conservative.
- Prefer explicit `unknown_access_age` or `compatibility_risk` markers over fake precision.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that scan Cargo-home caches, compute a dry-run cleanup plan from a small policy file, explain every keep/delete classification, and emit a diffable support bundle.

# De-risk plan

1. Start with scan/plan/diff/doctor before supporting any cleanup execution.
2. Keep the first policy vocabulary tiny: budgets, age thresholds, and exemptions.
3. Validate on one laptop workflow and one shared CI runner workflow.
4. Treat access-age and mixed-toolchain caveats as first-class output, not footnotes.

# Non-goals

- Not a replacement for Cargo’s built-in automatic garbage collection.
- Not a generic disk cleaner for `target/` trees or unrelated caches.
- Not a remote cache server.
- Not a promise that storage optimization never hurts rebuild/download latency.

# Architecture & API sketch

```rust
pub struct CacheInventory {
    pub cargo_home: std::path::PathBuf,
    pub classes: Vec<CacheClassSummary>,
    pub total_bytes: u64,
}

pub fn scan_cache_inventory(cargo_home: &std::path::Path) -> Result<CacheInventory>;
pub fn build_gc_plan(inv: &CacheInventory, policy: &CachePolicy) -> Result<GcPlan>;
pub fn diff_cache_receipts(old: &GcReceipt, new: &GcReceipt) -> CacheDiff;
```

Bundle draft: `cache-policy.toml`, `cache-inventory.json`, `gc-plan.json`, `cache-surface.receipt.json`, `recovery-obligation.report.json`, `cache-exemptions.toml`, `gc.receipt.json`, `cache-diff.json`, `notes.md`.

# Security / safety model

- Never delete by default.
- Treat local paths, private registry URLs, and user-specific directory details as sensitive in exported bundles.
- Record whether a plan depends on nightly-only GC controls.
- Never imply that an entry is safe to remove if the evidence is incomplete.

# Maintenance & governance plan

- Track Cargo GC stabilization, config changes, and cache-class evolution closely.
- Keep schemas compact and versioned.
- Maintain fixtures for laptops, CI, alternate registries, and mixed-toolchain caveats.
- Prefer compatibility shims over reinterpreting Cargo’s cache model.

# Milestones

## 0.1
- scan inventory
- policy parser
- dry-run plan

## 0.2
- diff receipts
- support bundle export
- doctor warnings for mixed-toolchain and config drift

## 1.0
- stable bundle schema
- curated CI/devcontainer fixtures
- optional conservative cleanup integration

# Open questions

- What is the smallest useful policy vocabulary that still captures real-world CI and laptop tradeoffs?
- How much access-age detail is reliably observable without overpromising precision?
- Which exemption classes deserve first-class fields versus free-form notes?

# Sources

- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo changelog (automatic global-cache GC stabilized in 1.88): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo configuration reference (`cache.auto-clean-frequency`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`gc` / manual controls): https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-cache`: https://crates.io/crates/cargo-cache
