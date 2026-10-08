# Gap: “Just Works” Cross Compilation (sysroots, C toolchains, and consistent UX)

## Summary
Rust can target many platforms via `rustup target add`, but in practice cross-compilation remains
frictionful for real projects because you also need:
- a C toolchain/linker that matches the target,
- sysroots/SDKs (musl, Android NDK, macOS SDK, Windows MSVC import libs),
- consistent configuration for `cc`-using crates and build scripts.

The ecosystem has powerful third-party tools (`cross`, `cargo-zigbuild`, `cargo-xwin`) and active
discussion about bundling a C compiler (e.g., Zig) with rustup, but there is no **unified, policyable,
explainable** story for most teams.

This gap is about standardizing a *workflow layer* and *artifact/report layer* so cross-compilation is:
- predictable,
- debuggable (“why does linking fail?”),
- reproducible and cacheable.

## Ecosystem signals
- rustup documents cross-compilation as “install targets via `rustup target add`”, but does not solve C toolchains/sysroots.  
  https://rust-lang.github.io/rustup/cross-compilation.html
- `cross` provides “zero setup” cross compilation and cross testing using containerized toolchains.  
  https://github.com/cross-rs/cross
- `cargo-zigbuild` uses Zig as a linker for easier cross compilation and even offers a macOS universal2 pseudo-target.  
  https://github.com/rust-cross/cargo-zigbuild  
  https://crates.io/crates/cargo-zigbuild
- `cargo-xwin` eases cross compiling to Windows MSVC targets by managing a sysroot.  
  https://github.com/rust-cross/cargo-xwin
- Community proposal to bundle `zig-cc` in rustup by default, to improve cross compilation and build script C compilation.  
  https://internals.rust-lang.org/t/bundle-zig-cc-in-rustup-by-default/22096

## What “good” looks like
- A single command to “prepare” a target toolchain + sysroot for common targets.
- Clear configuration handoff to `cc` crates and build scripts.
- Portable reports that explain:
  - what sysroot/toolchain was used,
  - what linker flags were selected,
  - what failed and why.
