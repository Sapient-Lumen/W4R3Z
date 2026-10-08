# Design: CompileDB Kit (`cargo compiledb`, compiledb-pack/v0)

## Goal
Unify IDE/tooling integration for Rust projects with native code by:
- standardizing how build scripts emit C/C++ compilation commands,
- producing deterministic `compile_commands.json`,
- optionally producing `rust-project.json` for non-Cargo integrations,
- bundling everything into a portable `compiledb-pack/v0`.

## References (signals)
- cc-rs compile_commands request: https://github.com/rust-lang/cc-rs/issues/691
- cc-rs merging complexity: https://github.com/rust-lang/cc-rs/issues/497
- rust-analyzer configuration + rust-project.json workflow: https://rust-analyzer.github.io/book/configuration
- rust-analyzer non-Cargo integration discussion: https://github.com/rust-lang/rust-analyzer/issues/13446 ; https://github.com/rust-lang/rust-analyzer/issues/16377
- cargo JSON build messages: https://github.com/rust-lang/cargo/issues/12864

## Core UX
### `cargo compiledb build`
- Runs a build (or piggybacks on one) and emits a merged `compile_commands.json`.
- For each build script that compiles C/C++:
  - capture the exact compiler invocation, args, include paths, defines, working directory.
- Ensure deterministic output ordering and normalization:
  - normalize paths
  - stable sorting by (crate, file, target)

### `cargo compiledb watch`
- Rebuild on changes and update the compilation database for editor loops.

### `cargo compiledb pack`
- Produce `compiledb-pack/v0`:
  - `compile_commands.json`
  - optional `rust-project.json` (or generation instructions)
  - toolchain + target triple + profile
  - cargo metadata snapshot hash
  - environment allowlist hash

### `cargo compiledb diff <A> <B>`
- Diff two packs:
  - new include paths/defines
  - changed compiler flags (e.g., -fPIC, -O levels)
  - new native files introduced

## Implementation model
### Build-script capture hook
Preferred: a small helper crate used by build scripts:
- `compiledb_emit::cc(CommandLike)` wraps `cc::Build` or raw `Command`
- writes per-crate fragments into `$OUT_DIR/compiledb-fragment.json`

Alternative: intercept compiler wrappers:
- set `CC=compiledb-wrapper` for build scripts,
- wrapper logs invocations and forwards to real compiler.

### Merge
- Collect all fragment files across target dir.
- Merge into one JSON array conforming to the Compilation Database spec.
- Emit to workspace root (or `.compiledb/`) with symlink option.

### Rust side alignment
- Record Cargo build graph:
  - workspace members, resolved profiles, features, target selection.
- Optionally generate `rust-project.json` for non-Cargo build systems via a discoverConfig command (rust-analyzer supports invoking a command to obtain config).

## Integration points
- Feature Kit: attach feature-report to explain why native flags changed (feature-dependent build.rs).
- Cross Toolchain Kit: include sysroot/toolchain provenance for cross builds.
- Safety Evidence: treat new native code as a review trigger.

## Evaluation plan
- Pilot on:
  - crates using bindgen + cc
  - embedded projects (C HAL code)
  - GUI projects with native deps
- UX bar:
  - “clangd works out of the box for the C bits, without manual CMake.”
