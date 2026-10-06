# Toolchain bootstrap: Rust (and friends)

DeriveBSD’s implementation bias toward Rust creates a real bootstrap and trust problem: **rustc is self-hosting**.

This document defines how DeriveBSD treats the toolchain as a pinned, explainable input rather than a magical prerequisite.

## Problem statement

A typical rustc build uses a precompiled **stage0** compiler, then builds stage1/2. The stage0 binary is a trust anchor unless we can:

- bootstrap from simpler compilers, and/or
- verify the stage0 binary via reproducible builds / diverse double compilation.

See also: `docs/191-diverse-double-compiling-and-bootstrappable-toolchains.md`.

Optional wedge for C/C++ dependency mass:
- `docs/398-zig-toolchain-wedge-and-cross-compilation.md`

## Strategy

DeriveBSD supports three toolchain trust tiers.

### Tier 0: pinned vendor toolchain (bootstrap-only)

- Accept a pinned, signed stage0 toolchain **only to build the first self-hosted toolchain**.
- Require:
  - signature provenance
  - transparency inclusion (optional policy)
  - hash pinning in Lock

### Tier 1: self-hosted toolchain with reproducible verification

- Build rustc using tier0 stage0, then rebuild rustc using the freshly built compiler.
- Record:
  - `toolchain.buildrecord`
  - `toolchain.rebuild.diffoscope` (if differences)
  - `toolchain.stabilizers` (if used)

### Tier 2: bootstrappable chain

- Attempt a longer chain similar to systems that bootstrap Rust via alternate compilers (e.g., mrustc) and minimal C/C++ toolchains.
- This is expensive but reduces trust in opaque binaries.

## Policy knobs

- `toolchain.trustTier` (0/1/2)
- `toolchain.requiredWitnesses` (for Tier 1/2)
- `toolchain.allowedStage0Keys`

## Output artifacts

- `toolchain.bundle` is a first-class Artifact type (signed, attested, cached).
- Host and builder images MUST pin a toolchain bundle digest.

## Notes

This is intentionally pragmatic: DeriveBSD does not claim to solve “trusting trust” by default; it makes the trust boundary explicit, inspectable, and reducible.

Last updated: 2026-02-24
