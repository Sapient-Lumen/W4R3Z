# Gap: Cross-language Compilation Database + IDE Cohesion (CompileDB Kit)

## Summary
Rust projects that include **C/C++ (or other) build steps** often lose IDE and tooling quality:
- clangd and other C tooling want `compile_commands.json`,
- Rust tooling wants Cargo metadata (or `rust-project.json` for non-Cargo builds),
- `build.rs` + `cc` crates can generate complex per-target C flags that aren't surfaced.

The ecosystem has *pieces*, but no standard, adoption-ready workflow that:
1) emits a unified compilation database for native code built by `build.rs`,
2) ties that to Rust target selection and workspace profiles,
3) produces stable, shareable artifacts for CI and review.

## Ecosystem signals
- The `cc` crate has open issues requesting an option to emit `compile_commands.json` for clangd from `build.rs`.  
  https://github.com/rust-lang/cc-rs/issues/691
- Related discussions highlight the complexity: multiple build scripts need to merge into a single JSON compilation database.  
  https://github.com/rust-lang/cc-rs/issues/497
- rust-analyzer relies on Cargo by default; for non-Cargo projects it uses `rust-project.json`, and there are multiple issues about smoother generation and “cargo check style” diagnostics in non-Cargo builds.  
  https://rust-analyzer.github.io/book/configuration  
  https://github.com/rust-lang/rust-analyzer/issues/13446  
  https://github.com/rust-lang/rust-analyzer/issues/16377
- Cargo exposes structured JSON build events (`--message-format json`) that can be used to correlate builds with artifact generation.  
  https://github.com/rust-lang/cargo/issues/12864

## What “good” looks like
- `cargo compiledb` that produces:
  - `compile_commands.json` for C/C++ built via build scripts,
  - `rust-project.json` (or a pointer) for IDEs when needed,
  - a portable report artifact with enough metadata to reproduce.
- A merge strategy that is deterministic across platforms and workspaces.
