# Cargo script workbench frontier — 2026-03-22

## Main judgment

**P-0435 Cargo Script Workbench Kit** now deserves the archive’s newer artifact-rich treatment.

The upstream direction is finally explicit enough that the missing crate is not another script runner.
It is a reviewable support bundle for:

1. **frontmatter authority**,
2. **discovery scope**,
3. **invocation interpretation**,
4. **cache residency**,
5. **export lineage**.

## Why this frontier sharpened

- the Cargo script goal frames single-file packages as an important workflow for bug reports, educational material, prototypes, and tiny utilities;
- Cargo’s unstable docs now define frontmatter, defaulted/inferred fields, disallowed manifest fields, hashed default target-dir behavior, and lockfile placement;
- Cargo also documents manifest-command behavior for `cargo <path>`, including different config-root and verbosity semantics from `cargo run --manifest-path <path>`;
- Cargo 1.94’s development notes say cargo script is intentionally starting with workspace auto-discovery disabled while broader workspace/config discovery remains unsettled;
- the stabilization path also names rustfmt, rust-analyzer, lexer, and diagnostics work, which means support truth is wider than one command invocation.

Taken together, that means the receiver-facing value is now a crate that can say **what Cargo inferred**, **what it deliberately did not discover**, **how it interpreted the invocation**, and **what a downstream maintainer would need to do to export or reproduce the result safely**.

## Best next implementation stance

The next implementation pass should freeze a small vocabulary before adding any orchestration:

- frontmatter-authority classes,
- discovery-scope classes,
- invocation-interpretation classes,
- cache-residency classes,
- export-lineage classes.

The crate should stay explanation-first and provenance-first.
