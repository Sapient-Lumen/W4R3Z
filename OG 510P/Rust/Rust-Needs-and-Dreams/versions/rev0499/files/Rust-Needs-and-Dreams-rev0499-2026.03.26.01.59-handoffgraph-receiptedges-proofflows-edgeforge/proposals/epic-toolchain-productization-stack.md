> rev0448 note: this proposal is now the implementation companion to `design/toolchain-productization-execution-blueprint-2026Q1.md`, which makes the primary shape explicit as **reference layer + report/pack command + profile/acceptance corpus**.

# Epic Proposal: Toolchain Productization Stack (`cargo toolchaincheck` + `toolchain-product-pack/v0`)

> rev0412 note: this proposal is now the implementation companion to `design/toolchain-productization-contract-2026Q1.md`.

## Why this is worthy
Rust’s ecosystem increasingly asks teams to treat compiler / stdlib / target / sanitizer variants like long-lived product inputs:
- `build-std` is being pushed toward a stabilizable MVP;
- rustup still models toolchains, components, targets, and overrides as distinct surfaces;
- custom targets explicitly require compiler pinning;
- cross compilation often needs linkers / SDKs beyond target stdlib installation;
- sanitizer stabilization now depends on precompiled and instrumented standard libraries;
- Rust for Linux and CPython-like adopters need repeatable std/core and platform-support stories.

But the ecosystem still has no single honest handoff for **toolchain-as-product truth**. [`design/toolchain-productization-lane-map.md`](../design/toolchain-productization-lane-map.md) is now the companion rule for keeping stock rustup, build-std, reusable sysroot packs, compiler-pinned custom targets, activation/host-target split rules, instrumented runtime families, and external handoff distinct.

That means reviewers, CI systems, firmware teams, release pipelines, and safety/security consumers still have to reconstruct the answer from:
- rustup local state;
- `rust-toolchain.toml` files;
- Cargo config snippets;
- target JSON files;
- `-Z build-std` invocations;
- linker/SDK environment setup;
- sanitizer flags and CI jobs;
- and ad hoc cache directories.

The missing contribution is a thin portable layer above those pieces, not another replacement for them.

## Proposal
Define a **Toolchain Productization Stack** with:
- a reference aggregation CLI, `cargo toolchaincheck`;
- a thin linked bundle, `toolchain-product-pack/v0`;
- imported evidence from:
  - `toolchain-pack/v0`
  - `sysroot-pack/v0`
  - `sysroot-activation/v0`
  - optional `sanitize-pack/v0`
  - optional support / release / firmware / safety imports
- stable diff and observation artifacts:
  - `toolchain-product-envelope/v0`
  - `toolchain-product-observation-report/v0`
  - `toolchain-product-diff-report/v0`

## Reference CLI shape
- `cargo toolchaincheck export`
  - emit `toolchain-product-envelope/v0` for one selected target/profile subject
- `cargo toolchaincheck observe`
  - emit `toolchain-product-observation-report/v0` from imported provisioning / sysroot / activation / runtime-analysis inputs
- `cargo toolchaincheck diff --against <ref|pack|path>`
  - emit `toolchain-product-diff-report/v0`
- `cargo toolchaincheck pack`
  - produce `toolchain-product-pack/v0`
- `cargo toolchaincheck verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace rustup, Cargo, cross/zigbuild/xwin, or sanitizer engines.

## What `toolchain-product-pack/v0` should contain
- `manifest.json`
- `toolchain-product-envelope.json`
- `toolchain-product-observation-report.json`
- optional `toolchain-product-diff-report.json`
- imported `toolchain-pack` pointer or embedded attachment
- imported `sysroot-pack` and activation attachments
- optional imported `sanitize-pack` attachments
- optional support / release / firmware / safety import pointers
- checksums, provenance, and generator identity

## Design principles
- **Toolchain as product, not just local machine state.**
- **Thin imports over new truth engines.**
- **Provisioning, stdlib identity, activation, and runtime-analysis remain distinct truths.**
- **Activation and reuse must be attachable, not inferred from directory state.**
- **Sanitizer / mitigation results must preserve their runtime and stdlib provenance.**
- **Diff toolchain drift, not only version strings.**

## Early implementation order
1. instrumented-stdlib pack
2. hardened / ABI-modifying pack
3. custom-target / tier-3 pack
4. shared-cache / CI reuse lane
5. external-build-system handoff lane

## Non-goals
- another `build-std` convenience wrapper;
- a universal cross-compilation manager;
- replacing rustup or Cargo upstream workflows;
- a fake “custom toolchain works” score;
- collapsing sanitizer evidence into provisioning evidence.

## Success bar
This becomes worthy when a team can answer:
- which compiler / linker / SDK / target stdlib they actually used;
- which stdlib profile family was built and why;
- how the workspace or CI selected and reused that toolchain;
- what runtime-analysis or mitigation lane actually ran;
- and what changed between two toolchain variants,

without scraping machine-local state or reverse-engineering shell history.

## Read this with
- `gaps/toolchain-variants-sysroots-cross-builds-and-sanitizer-support-contracts.md`
- `design/toolchain-productization-lane-map.md`
- `design/toolchain-productization-stack.md`
- `design/toolchain-productization-pilot-program.md`
- `design/cross-toolchain-kit.md`
- `design/sysroot-pack-kit.md`
- `design/sanitizer-battery-kit.md`
