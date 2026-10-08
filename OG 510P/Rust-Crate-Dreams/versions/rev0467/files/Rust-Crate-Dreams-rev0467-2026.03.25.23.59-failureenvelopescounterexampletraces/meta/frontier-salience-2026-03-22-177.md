# Frontier salience refresh — 2026-03-22 (177)

## Main rerank for this pass

1. **P-0435 Cargo Script Workbench Kit** — promoted because current Cargo substrate now makes single-file package truth more operational than folklore: frontmatter authority, discovery scope, invocation semantics, cache residency, and export lineage are all explicit enough to bundle.
2. **P-0490 Cargo Lock Contention Witness Kit** — remains structurally important because Cargo/rust-analyzer shared-root waiting still needs reviewable evidence.
3. **P-0484 Toolchain & Target Support Contract Kit** — remains structurally important because support truth across targets still fragments across Cargo, docs.rs, CI, and project policy.
4. **P-0508 Cargo Build Script Delegation Kit** — remains high because build-time topology and override authority still matter across many other lanes.
5. **P-0469 Cargo Rebuild Explanation Kit** — remains high because rebuild causality and session-based build analysis still need receiver-facing interpretation.

## Why P-0435 moved up

Official Cargo and Rust sources now make single-file package semantics explicit enough that the sharper gap is no longer “run this `.rs` file with dependencies.”
It is a crate that can tell another maintainer **which manifest bits were inferred, which discovery rules applied, what invocation semantics Cargo used, where cache/lock state lived, and how to export the script without losing provenance**.

## Guardrail

Do not add another script/reproducer crate unless it clearly explains why it is not better expressed as **P-0435** plus existing build-dir / contention / workspace-boundary substrate.
