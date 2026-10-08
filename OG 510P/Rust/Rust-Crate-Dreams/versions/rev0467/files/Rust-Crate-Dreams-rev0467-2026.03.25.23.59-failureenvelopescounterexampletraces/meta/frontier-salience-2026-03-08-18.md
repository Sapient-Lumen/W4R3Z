# Frontier salience scan — 2026-03-08 (eighteenth pass)

## Main judgment

This pass **did** add a new top-level proposal:

- **P-0504 Linker Lane Contract & Diagnosis Kit**

The repo already had strong ideas for toolchains, native deps, CPU baselines, and Cargo build explainability.
What it still lacked was a clean crate for the **linking layer itself**: one contract for intended linker lanes, one receipt for what actually happened, and one diagnosis/diff artifact for failures or lane switches.

That is a real missing seam rather than just another cross-compilation helper.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0504 Linker Lane Contract & Diagnosis Kit**
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0433 MC/DC Coverage Workbench Kit**
8. **P-0453 Safety Contract Consumer Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0046 buildscript-ux-kit**

## Why P-0504 is salient

Five current facts make this more than a speculative niche:

- The 2025 Rust compiler performance survey says the linking phase is a common complaint and explicitly points to faster linkers as a current direction.
- Cargo already documents target-specific linker and `rustflags` surfaces, so this is no longer a hidden implementation seam.
- Cargo also documents host/target flag-scope behavior that can make linker-related drift surprisingly confusing in mixed host/target builds.
- `rustc` now documents meaningful linker-lane substrate directly (`linker`, `link-self-contained`, `linker-features=+lld`).
- rustup and the ecosystem’s real tools (`cargo-zigbuild`, `cargo-xwin`, `xwin`, `cross`) together show that the missing value is now the **receipt/doctor/diff layer above the lanes**, not the existence of lanes themselves.

## What should happen next

The best next passes on this frontier should prefer:

1. tiny schema work for `linker-lane.manifest` and `link-diagnosis.report`,
2. scenario bundles for `host_flag_leakage`, `sdk_missing`, and `support_surface_changed`,
3. comparison planning between `system-default`, `self-contained-lld`, Zig, Windows-SDK, and containerized lanes,
4. and explicit boundary notes keeping linker-lane contracts distinct from broader toolchain support or native-dependency probing.

They should **not** drift into:

- another linker implementation,
- another universal cross-compilation orchestrator,
- or a giant benchmark suite with no support-grade artifact.

## Sources

- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo configuration: https://doc.rust-lang.org/cargo/reference/config.html
- `rustc` codegen options: https://doc.rust-lang.org/rustc/codegen-options/index.html
- rustup cross-compilation docs: https://rust-lang.github.io/rustup/cross-compilation.html
- `cargo-zigbuild`: https://github.com/rust-cross/cargo-zigbuild
- `cargo-xwin`: https://github.com/rust-cross/cargo-xwin
- `cross`: https://github.com/cross-rs/cross
- `xwin`: https://docs.rs/xwin/latest/xwin/
