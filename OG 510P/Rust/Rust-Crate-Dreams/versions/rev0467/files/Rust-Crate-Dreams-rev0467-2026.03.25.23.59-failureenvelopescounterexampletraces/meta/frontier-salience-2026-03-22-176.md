# Frontier salience refresh — 2026-03-22 (176)

## Main rerank for this pass

1. **P-0490 Cargo Lock Contention Witness Kit** — promoted because current Cargo and rust-analyzer substrate now makes contention truth more operational than folklore: roots, actor command lanes, wait windows, and mitigation cost are all explicit enough to bundle.
2. **P-0484 Toolchain & Target Support Contract Kit** — remains structurally important because support truth across targets still fragments across Cargo, docs.rs, CI, and project policy.
3. **P-0121 FFI Boundary & Bindings Conformance Kit** — remains central because interop still needs portable layout/error/ownership truth.
4. **P-0508 Cargo Build Script Delegation Kit** — remains high because build-time topology and override authority still matter across many other lanes.
5. **P-0469 Cargo Rebuild Explanation Kit** — remains high because rebuild causality and lock contention are adjacent but distinct receiver-facing questions.

## Why P-0490 moved up

Official Cargo and rust-analyzer docs now make build roots, actor command shapes, and lock-improvement efforts concrete enough that the sharper gap is no longer “tell me Cargo is slow.”
It is a crate that can tell another maintainer **which root claim is authoritative, which command lane ran, what wait was observed, and what the recommended workaround costs**.

## Guardrail

Do not add another Cargo/IDE pain crate unless it clearly explains why it is not better expressed as **P-0490** plus existing build-dir / rebuild / sandbox / delegation substrate.
