# Frontier salience refresh — 2026-03-22 (175)

## Main rerank for this pass

1. **P-0431 Public Dependency Boundary Kit** — promoted because current Rust/Cargo direction now makes public/private dependency stabilization concrete enough that the missing crate is a reviewable boundary contract, not another lint wrapper.
2. **P-0484 Toolchain & Target Support Contract Kit** — remains structurally important because support truth across targets still fragments across Cargo, docs.rs, CI, and project policy.
3. **P-0121 FFI Boundary & Bindings Conformance Kit** — remains central because interop still needs portable layout/error/ownership truth.
4. **P-0120 Unsafe Contract Auditor Kit** — remains central because unsafe obligations increasingly have official contract/documentation substrate.
5. **P-0508 Cargo Build Script Delegation Kit** — remains high because build-time topology and override authority still matter across many other lanes.

## Why P-0431 moved up

Official Rust goals now explicitly target stabilization of public/private dependencies, Cargo already ships more user-facing unstable surface for them, and rustdoc-based public API tooling is mature enough to support an imported-evidence layer.
The sharper gap is therefore a crate that can tell another maintainer **what was declared, what is effectively public, how it escaped, what evidence supports the verdict, and what to do next**.

## Guardrail

Do not add another public-API analyzer unless it clearly explains why it is not better expressed as **P-0431** plus existing public-API/semver substrate.
