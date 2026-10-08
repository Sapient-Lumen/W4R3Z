# Doctest runtool profile route/basis plan — 2026-03-22

Purpose: sharpen **P-0481 Doctest Runtool Profile Kit** into a more implementation-ready support-contract lane.

The missing crate here should not try to become a full emulator manager.
It should become the boring layer that gives another maintainer an honest answer to these questions:

1. **What selected the effective runner?**
2. **What target lane and support class was being claimed?**
3. **Which ignore policy was in force?**
4. **What compile/run path assumptions applied?**
5. **What exact portable bundle should travel in CI or support handoff?**

## Why this is timely now

Current official docs make the substrate unusually concrete:

- rustdoc’s current CLI docs define `--test-runtool` / `--test-runtool-arg` precisely enough that wrapper provenance is first-class;
- Cargo’s config docs keep target runners and environment overrides first-class and define runner precedence;
- Cargo’s `cargo test` docs still keep both the execution-model caveat and the compile-vs-run working-directory split explicit;
- release notes keep cross-target doctests and target-specific ignore attrs official;
- and Rust-for-Linux still demonstrates why special-environment doctests matter in practice.

## What version 0.1 should provide other people

### 1. `runner-route.receipt`

A compact receipt that states, conservatively:

- route kind (`explicit_rustdoc_runtool`, `cargo_target_triple_runner`, `cargo_target_cfg_runner`, `environment_runner_override`, `direct_no_runner`, `manual_review_required`),
- wrapper program and args,
- precedence notes,
- where the route was declared (CLI/config/env/import),
- and what remained unknown.

### 2. `execution-basis.receipt`

A companion receipt that states:

- target triple and support class (`target_run_via_runner`, `compile_only`, `ignored_by_target_policy`, `manual_review_required`),
- compile invocation directory basis,
- runtime working-directory basis,
- ignore-target annotations and rationale refs,
- and adjacent imported receipts (for example from **P-0455**).

### 3. `doctest-runtool-support-bundle.manifest`

A portable bundle manifest that enumerates:

- the declared runtool policy,
- route receipt,
- execution-basis receipt,
- target matrix,
- ignore audit,
- run results,
- and optional imports such as extraction/support receipts from **P-0455**.

## What 0.1 should not try to do

- not a VM lifecycle manager,
- not a general-purpose test scheduler,
- not a docs.rs reproducer,
- not a replacement for rustdoc extraction JSON,
- not a coverage or debt dashboard,
- and not a magical tool that claims all green target lanes are equivalent.

## Suggested CLI surface

- `cargo doctest-profile route` — emit the effective runner-route receipt without executing doctests.
- `cargo doctest-profile basis` — emit execution-basis receipts for selected targets.
- `cargo doctest-profile run` — execute one configured lane and emit route/basis/results together.
- `cargo doctest-profile bundle` — collect a portable support bundle.
- `cargo doctest-profile diff` — compare route/basis drift across receipts.

## Tiny MVP data model

```rust
pub struct RunnerRouteReceipt {
    pub target: String,
    pub route_kind: RouteKind,
    pub wrapper_program: Option<String>,
    pub wrapper_args: Vec<String>,
    pub declared_by: Vec<DeclarationSource>,
    pub manual_review_required: bool,
}

pub struct ExecutionBasisReceipt {
    pub target: String,
    pub support_class: SupportClass,
    pub compile_directory_basis: DirectoryBasis,
    pub run_directory_basis: DirectoryBasis,
    pub ignore_annotations: Vec<IgnoreAnnotation>,
    pub imports: Vec<ImportedReceiptRef>,
}
```

## Distinct from adjacent lanes

- **P-0455** owns extraction-basis, rewrite-lineage, grouping, and example-support truth.
- **P-0472** owns docs.rs hosted parity.
- **P-0476** owns documentation-example coverage / debt review.
- **P-0481** should own route provenance and execution basis above the official runner substrate.

## Best next fixture slices

1. Cargo target-runner route is not the same as explicit rustdoc `--test-runtool`.
2. Target-specific ignore policy plus package-root run directory is part of execution basis, not just decoration.
3. Portable bundle keeps route, basis, results, and imports separate.

## Sources

- rustdoc command-line arguments — https://doc.rust-lang.org/rustdoc/command-line-arguments.html
- Cargo unstable features (`doctest-xcompile`) — https://doc.rust-lang.org/cargo/reference/unstable.html#doctest-xcompile
- Rust release notes — https://doc.rust-lang.org/beta/releases.html
- Cargo configuration — https://doc.rust-lang.org/cargo/reference/config.html
- Cargo test docs — https://doc.rust-lang.org/cargo/commands/cargo-test.html
- Rust for Linux tooling goal — https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- rustdoc unstable features (`--persist-doctests`) — https://doc.rust-lang.org/rustdoc/unstable-features.html#--persist-doctests-persist-doctest-executables-after-running
