# Design: Cross Toolchain Kit (`cargo crosskit`, toolchain-pack/v0)

## Goal
Make cross compilation and packaging predictable by defining:
- a reference CLI (`cargo crosskit`) that provisions target toolchains/sysroots,
- a portable report and bundle format (`toolchain-report/v0`, `toolchain-pack/v0`),
- adapters to reuse the best existing tools (cross, zigbuild, xwin) instead of reinventing them.

## References (signals)
- rustup cross compilation docs: https://rust-lang.github.io/rustup/cross-compilation.html
- cross: https://github.com/cross-rs/cross
- cargo-zigbuild: https://github.com/rust-cross/cargo-zigbuild ; https://crates.io/crates/cargo-zigbuild
- cargo-xwin: https://github.com/rust-cross/cargo-xwin
- “bundle zig-cc in rustup” discussion: https://internals.rust-lang.org/t/bundle-zig-cc-in-rustup-by-default/22096

## Core UX: `cargo crosskit`
- `cargo crosskit prepare --target <triple>`  
  Ensure everything needed exists:
  - rust target stdlib (`rustup target add`)
  - C toolchain/linker
  - sysroot/SDK (managed or referenced)
- `cargo crosskit build --target <triple>`  
  Build using a selected backend:
  - `backend = cross` (containerized)
  - `backend = zig` (zig as linker)
  - `backend = xwin` (Windows MSVC sysroot)
  - `backend = native` (host toolchain, if available)
- `cargo crosskit doctor --target <triple>`  
  Explain configuration:
  - which linker and sysroot are used
  - how `cc` will find it (env vars, cargo config)
  - common failure patterns and fixes
- `cargo crosskit report`  
  Emit `toolchain-report/v0` (no secrets)
- `cargo crosskit pack`  
  Bundle report + pinned toolchain metadata into `toolchain-pack/v0` for CI reproduction.

## Configuration handoff (critical)
Expose a stable “toolchain environment contract”:
- `CROSSKIT_CC`, `CROSSKIT_CXX`, `CROSSKIT_AR`, `CROSSKIT_RANLIB`
- `CROSSKIT_SYSROOT`
- `CROSSKIT_LINKER`
- `CARGO_TARGET_<TRIPLE>_LINKER` (set by generated `.cargo/config.toml`)
This is designed so `cc-rs` and build scripts can consistently pick up the right toolchain.

## Artifact: `toolchain-report/v0`
- session metadata (workspace hash, git sha optional, toolchain versions)
- target triple and selected backend
- sysroot/SDK identifiers and provenance pointers
- compiler/linker identifiers and paths
- generated Cargo config snippets (redacted)
- reason codes for failures:
  - `MISSING_SYSROOT`
  - `SDK_LICENSE_BLOCK` (e.g., macOS SDK constraints)
  - `CC_CRATE_NOT_PICKING_UP_TOOLCHAIN`
  - `LINKER_MISMATCH`
  - `UNSUPPORTED_TARGET_BACKEND`

## Integration points
- Release Pipeline Kit: emit `toolchain-pack/v0` as part of release evidence.
- Cargo Report Kit: associate build sessions with toolchain packs for perf diffing.
- Credentials Kit: ensure no SDK keys leak; record sourcing without secrets.

## Evaluation plan
- Pilots across target classes:
  - musl static Linux
  - Windows MSVC from Linux
  - macOS universal2 from Linux (where legally possible)
  - Android NDK builds
- Success criteria:
  - “prepare + build” works with minimal config for common crates
  - doctor output leads to actionable fixes within one screen.
