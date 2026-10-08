# Linker-lane upstream fit — 2026-03-08

## Main judgment

This frontier now has enough official substrate and enough real lane-specific tools that the missing value is **not another linker wrapper**.

The missing value is the **contract / receipt / diagnosis / diff layer** above them.

## Current substrate we should treat as real

- Cargo already documents target-specific `linker` and `rustflags` configuration.
- Cargo also documents that without `--target`, `build.rustflags` can affect host builds such as build scripts and proc macros.
- `rustc` already documents linker-lane knobs like `-C linker`, `-C link-self-contained`, and `-C linker-features=+lld`.
- rustup explicitly says cross-compilation typically still needs extra tools, especially a linker.
- The Rust compiler performance survey now explicitly names link time as a common complaint and notes a move toward faster linkers by default.

## Prior art that should not be ignored

- `cargo-zigbuild` for Zig-backed linking lanes
- `cargo-xwin` / `xwin` for Windows MSVC-from-non-Windows lanes
- `cross` for containerized cross-compilation lanes

These are not evidence that the problem is solved.
They are evidence that **lane-specific execution exists**, so the new crate should sit **above** that level.

## Planning rule

When a future pass touches this frontier, it must state explicitly whether the missing value is:

1. a **new linker or wrapper lane**,
2. a **project support contract for which lane is intended**,
3. a **doctor/receipt layer for what happened on one machine**,
4. or a **diff layer for switching lanes deliberately**.

For this archive, the best current move is (2)–(4), not (1).

## Adjacent boundaries to keep sharp

- **P-0484 Toolchain & Target Support Contract Kit** is broader support posture.
- **P-0058 native-deps-kit** is native dependency probing and fallback behavior.
- **P-0504** should stay on **linker lane choice, diagnosis, and diffable support risk**.

## Sources

- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- `rustc` codegen options: https://doc.rust-lang.org/rustc/codegen-options/index.html
- rustup cross-compilation docs: https://rust-lang.github.io/rustup/cross-compilation.html
- `cargo-zigbuild`: https://github.com/rust-cross/cargo-zigbuild
- `cargo-xwin`: https://github.com/rust-cross/cargo-xwin
- `cross`: https://github.com/cross-rs/cross
- `xwin`: https://docs.rs/xwin/latest/xwin/
