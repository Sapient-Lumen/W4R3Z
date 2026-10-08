# Epic Proposal: Cross Toolchain Kit (cargo crosskit)

## One-sentence pitch
Make Rust cross compilation predictable by standardizing how toolchains/sysroots are provisioned, configured for build scripts, and reported for CI reproduction.

## Deliverables
- `cargo-crosskit` reference implementation
- Schemas:
  - `toolchain-report/v0`
  - `toolchain-pack/v0`
- Backends/adapters:
  - cross-rs/cross adapter
  - cargo-zigbuild adapter
  - cargo-xwin adapter
- Target recipes:
  - musl, Android, Windows MSVC, macOS universal2 guidance
- Doctor + corpus:
  - common linker/sysroot failures with fixes
  - regression tests for config handoff to `cc` crates

## Why now
- Third-party tools have made major strides (`cross`, `cargo-zigbuild`, `cargo-xwin`), but users still face fragmented UX and inconsistent reporting.  
  https://github.com/cross-rs/cross  
  https://github.com/rust-cross/cargo-zigbuild  
  https://github.com/rust-cross/cargo-xwin
- There is active community appetite to improve the base toolchain story (e.g., bundling Zig in rustup), suggesting the time is ripe for a workflow standard that can later fold upstream.  
  https://internals.rust-lang.org/t/bundle-zig-cc-in-rustup-by-default/22096

## Non-goals
- Replacing cross/zigbuild/xwin
- Shipping proprietary SDKs
- Solving legal distribution constraints (we surface them clearly)

## Milestones
1) v0: prepare + doctor + report schema, zig backend
2) v0.2: cross backend adapter + CI templates
3) v0.3: xwin backend + sysroot provenance pointers
4) v1: stable schemas + upstream integration proposal
