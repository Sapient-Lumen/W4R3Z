---
id: P-0527
title: LittleFS Native Adoption Kit — compatibility witnesses, async/blocking storage adapters, and power-cut evidence
status: idea
domains: [embedded, storage, filesystem, no_std, async, conformance]
last_reviewed: 2026-03-19
evidence:
  - https://github.com/littlefs-project/littlefs
  - https://docs.rs/crate/littlefs2/latest
  - https://github.com/trussed-dev/littlefs2-sys
  - https://github.com/littlefs-project/littlefs/issues/1112
  - https://docs.rs/littlefs-rust/latest/src/littlefs_rust/lib.rs.html
  - https://docs.rs/embedded-storage-async/latest/embedded_storage_async/
  - https://docs.rs/embassy-embedded-hal/latest/embassy_embedded_hal/
  - https://github.com/littlefs-project/littlefs/issues/143
---

# Problem

`littlefs` remains one of the most attractive embedded filesystems because it is explicitly designed for **power-loss resilience**, **dynamic wear leveling**, and **bounded RAM/ROM** on microcontrollers.
That makes it a natural target for Rust embedded work.

But the Rust story is still split across layers that do not yet add up to one boring default product:

- upstream `littlefs` is still the C reference implementation,
- `littlefs2` remains an idiomatic Rust API over a C backend,
- `littlefs2-sys` still carries C build/link surface and even says a permissively licensed replacement for `string.c` is welcome,
- and the newly published `littlefs-rust-core` / `littlefs-rust` pure-Rust port is exciting progress, but still looks more like a **feasibility breakthrough** than a finished ecosystem default.

At the same time, the Rust embedded world now has meaningful substrate for storage adapters:

- `embedded-storage-async` provides async storage traits,
- `embassy-embedded-hal` already offers flash utilities and simulated in-memory flash,
- and long-running user questions around async SPI / async flash with littlefs show that “just call the blocking filesystem” is not always an honest answer.

So the missing contribution is no longer simply “prove a pure-Rust littlefs is possible.”
The sharper missing crate is a **LittleFS native adoption kit** above the raw engine:

- compatibility witnesses,
- storage-adapter receipts,
- power-cut evidence,
- image/fixture tooling,
- and an honest async/blocking integration story.

# What it should provide

## 1) A boring Rust-first LittleFS product surface

Other people should get one opinionated path that answers:

- which engine implementation is being used,
- which on-disk littlefs version/profile it targets,
- whether it is blocking-only or async-integrated,
- and what exact flash/storage assumptions it makes.

That should work whether the engine is:

- the new pure-Rust `littlefs-rust-core`,
- a higher-level `littlefs-rust` wrapper,
- or (during migration) an FFI-backed compatibility backend.

The product should prefer native Rust where possible, but it should not hide the backend choice.

## 2) First-class storage adapters

The crate should provide adapters for:

- `embedded-storage` NOR-flash style backends,
- `embedded-storage-async` backends,
- host-side RAM/file test backends,
- and partitioned flash backends imported from Embassy-style utilities.

These adapters should emit a **storage-adapter receipt** that records:

- read/program/erase granularities,
- block-count and cache assumptions,
- bad-block policy,
- sync/yield behavior,
- and whether async is native, cooperative, or simulated.

## 3) Compatibility witnesses instead of “seems fine” claims

The crate should provide:

- image-format roundtrip checks,
- corpus-based mount/read/write/delete witnesses against known-good images,
- cross-checks against upstream littlefs behavior where practical,
- and migration witnesses for old/new image versions when relevant.

This should produce a compact `compatibility-witness.receipt.json`.

## 4) Power-cut and recovery evidence

Because littlefs is sold on power-loss resilience, the crate should not stop at API ergonomics.
It should provide a runner that can:

- inject failures between read/prog/erase/sync boundaries,
- remount after interruption,
- classify whether the last known good state survived,
- and emit a `powercut-run.report.json`.

## 5) Image tooling and support bundles

The product should include one CLI path to:

- create and inspect images,
- diff two images logically rather than byte-by-byte when possible,
- bundle compatibility and power-cut receipts,
- and hand another maintainer one compact `littlefsbundle.zip`.

# Users & user stories

- **Embedded Rust maintainer**: “I want a pure-Rust path that does not quietly depend on a C toolchain.”
- **Embassy application developer**: “Tell me whether this backend is really async-safe or merely wrapped blocking I/O.”
- **Firmware team**: “Show me a witness that the image I produce today still mounts and behaves like the reference path I trust.”
- **Security/reliability reviewer**: “Do not just tell me ‘power-loss safe’; give me a power-cut report and exact failure-injection scope.”
- **Tooling author**: “I want to create or inspect littlefs images on the host without re-implementing half the stack.”

# Prior art (and why it’s insufficient)

- **Upstream `littlefs`** is still the reference design and the normative source for format/behavior expectations, but it is C-first.
- **`littlefs2`** gives Rust users an idiomatic surface, but its own docs still describe a C backend and `littlefs2-sys` dependency.
- **`littlefs2-sys`** is useful and maintained, but it keeps C build/link reality in the picture and explicitly still carries a GPL-licensed `string.c` replacement surface asking for a permissive replacement.
- **`littlefs-rust-core` / `littlefs-rust`** newly prove that a no-C path is now real, but the reviewed public docs center a raw port plus a crate-specific `Storage` trait and `RamStorage` example, not yet a whole adoption/evidence workflow.
- **`littlefs2-pack`** helps with host-side image construction, but it also wraps the C library and is only one slice of the overall adoption story.
- **`embedded-storage-async`** and **Embassy flash utilities** provide important substrate, but not a LittleFS-specific compatibility/evidence contract.
- **Async SPI issue history** shows the underlying integration pain is real and long-lived, especially when “pretend synchronous” implies busy waiting or timing dishonesty.

# Design goals

1. **Backend honesty first** — native Rust, FFI-backed, blocking, async-cooperative, and simulated paths must remain distinguishable.
2. **On-disk compatibility before clever abstraction** — image truth matters more than API cleverness.
3. **no_std baseline** with optional `alloc` and host-side tooling layers.
4. **Reviewable artifacts** — compatibility, adapter, and power-cut receipts are first-class outputs.
5. **Import existing substrate** rather than rebuilding the world: embedded-storage, Embassy utilities, and the emerging pure-Rust port should all be usable.
6. **Async without lying** — if a backend is blocking under the hood, the receipt must say so.
7. **Host+target symmetry** — one team should be able to generate fixtures on a host and exercise them on-device.

# Non-goals

- Replacing every embedded filesystem.
- Becoming a generic VFS layer for all storage backends.
- Proving resilience against every flash chip or every power-failure model.
- Hiding the difference between upstream-behavior compatibility and Rust-native convenience extensions.
- Collapsing filesystem semantics, higher-level KV stores, OTA partitioning, and generic persistence policy into one crate.

# Architecture & API sketch

## Suggested workspace split

- `littlefs_engine_bridge`
  - imports an engine backend (`littlefs-rust-core` first when viable; FFI fallback optional)
- `littlefs_embedded_storage`
  - adapters for `embedded-storage`
- `littlefs_embedded_storage_async`
  - adapters for `embedded-storage-async`
- `littlefs_image`
  - host-side image create/inspect/diff helpers
- `littlefs_compat`
  - corpus import, upstream comparison, compatibility witnesses
- `littlefs_powercut`
  - failure injection and recovery classification
- `cargo-littlefs-kit`
  - CLI / cargo subcommand

## Core commands

- `cargo littlefs doctor`
  - emit `storage-adapter.receipt.json`
- `cargo littlefs compat`
  - emit `compatibility-witness.receipt.json`
- `cargo littlefs powercut`
  - emit `powercut-run.report.json`
- `cargo littlefs image pack|ls|diff`
  - host-side image workflows
- `cargo littlefs bundle`
  - produce `littlefsbundle.zip`

## Draft API sketch

```rust
pub fn inspect_storage_adapter(adapter: &AdapterConfig) -> Result<StorageAdapterReceipt>;
pub fn mount_with_backend<S>(storage: S, cfg: &FsConfig) -> Result<Filesystem<S>>;
pub fn witness_compatibility(case: &CompatCase) -> Result<CompatibilityWitnessReceipt>;
pub fn run_powercut_campaign(case: &PowercutCase) -> Result<PowercutRunReport>;
pub fn diff_images(old: &[u8], new: &[u8]) -> Result<ImageDiffReport>;
pub fn write_bundle(bundle: &LittleFsBundle, out: &Path) -> Result<()>;
```

# Security / safety model

- Never claim “power-loss safe” without recording the exact injection scope and campaign parameters.
- Treat host paths, image contents, and filenames as potentially sensitive when bundling artifacts.
- Keep backend-specific `unsafe` contained and auditable.
- Refuse to label cooperative or wrapped-blocking async paths as fully non-blocking.
- Record whether bad-block handling is exercised, assumed absent, or left to manual review.

# Maintenance & governance plan

- Keep format/profile compatibility separate from convenience APIs.
- Prefer importing upstream littlefs test/corpus material where licensing and mechanics allow.
- Track both the C reference and pure-Rust backend maturity, but avoid locking the proposal to only one implementation.
- Maintain a small fixture corpus that is meaningful for adoption: roundtrip, corruption handling, power-cut recovery, and async-yield honesty.

# Milestones

## 0.1
- `embedded-storage` adapter receipt
- host RAM/file backend
- image pack/list/diff
- first compatibility witness against a small known-good corpus

## 0.2
- `embedded-storage-async` adapter lane
- explicit cooperative-yield / wrapped-blocking classification
- first power-cut campaign runner

## 0.3
- optional upstream/reference cross-check runner
- migration/version witnesses
- compact `littlefsbundle.zip` support

# Open questions

- Should the long-term engine authority be a pure-Rust backend only, or should the kit permanently support multiple backends for witness generation?
- What is the cleanest honest async contract for flash backends that are operationally async but filesystem-semantically serialized?
- Which parts of power-cut simulation should be host-only, and which should be exercisable on real boards?
- How much logical diffing can be done without overstating semantic equivalence?

# Sources

See front matter links.
