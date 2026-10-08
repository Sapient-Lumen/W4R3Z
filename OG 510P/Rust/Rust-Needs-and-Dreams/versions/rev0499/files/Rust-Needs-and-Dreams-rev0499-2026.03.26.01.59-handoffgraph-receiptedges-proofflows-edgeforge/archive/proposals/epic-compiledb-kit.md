# Epic Proposal: CompileDB Kit (cross-language IDE cohesion)

## One-sentence pitch
Make mixed Rust + native-code projects feel first-class by standardizing how Cargo builds emit compilation databases and by shipping shareable compiledb packs for IDEs and CI.

## Deliverables
- `cargo-compiledb` reference implementation
- Schemas:
  - `compiledb-pack/v0`
  - `compiledb-report/v0`
- build.rs integration:
  - helper crate for emitting fragments
  - optional compiler-wrapper mode
- deterministic merging + diff tool
- docs:
  - clangd setup
  - rust-analyzer integration for non-Cargo builds

## Why now
- The cc/build.rs ecosystem is actively requesting compile_commands emission for clangd, but lacks a standardized end-to-end solution.  
  https://github.com/rust-lang/cc-rs/issues/691
- rust-analyzer has non-Cargo workflows based on `rust-project.json`, but generation and diagnostics remain friction points.  
  https://github.com/rust-lang/rust-analyzer/issues/13446  
  https://github.com/rust-lang/rust-analyzer/issues/16377
- Cargo’s structured JSON messages can provide a reliable substrate for correlating builds with artifact generation.  
  https://github.com/rust-lang/cargo/issues/12864

## Milestones
1) v0: wrapper-based capture + merged compile_commands.json + pack schema
2) v0.2: build.rs helper crate + deterministic diff
3) v0.3: watch mode + rust-project.json generation hooks
4) v1: stable schemas + upstream proposals for cc-rs / Cargo hooks
