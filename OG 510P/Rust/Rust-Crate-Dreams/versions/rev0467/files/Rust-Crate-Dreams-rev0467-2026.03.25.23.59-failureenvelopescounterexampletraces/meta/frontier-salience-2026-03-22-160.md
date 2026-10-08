# Frontier salience snapshot — 2026-03-22-160

This refresh moves **cross-language interop** from “important supporting theme” to one of the archive’s clearest top-level support-contract clusters.

## Ranked frontier after the latest scan

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0121 FFI Boundary & Bindings Conformance Kit**
3. **P-0036 MSRV Workspace Lab**
4. **P-0532 Async Runtime Assurance Profile Kit**
5. **P-0486 Debuggability Support Contract Kit**
6. **P-0081 Stable Plugin Host Kit**
7. **P-0002 Wasm Plugin Kit**
8. **P-0101 Crash Artifact & Symbolication Workbench Kit**
9. **P-0503 Assurance Case Workbench Kit**
10. **P-0017 Trust Lens**

## Why P-0121 moved up

Fresh official Rust framing now makes the interop lane harder to treat as optional:

- the Rust project is explicitly organizing around **Cross-language interop** as an application area;
- the safety-critical Rust write-up explicitly treats C/C++ interop as part of the safety story;
- and current bridge families make it clear that the remaining gap is not “can Rust talk to other languages?” but “can another team review what the boundary really means?”

That makes **P-0121** more leverage-heavy than many narrower shipkits.

## Clustered reading of the frontier

### Support-contract core
- **P-0484** toolchain/target support
- **P-0121** FFI boundary conformance
- **P-0036** MSRV workspace lab
- **P-0486** debuggability support

### Runtime / operations / assurance
- **P-0532** async runtime assurance
- **P-0101** crash symbolication
- **P-0503** assurance case workbench
- **P-0017** trust lens

### Interop / extensibility stack
- **P-0121** FFI boundary conformance
- **P-0081** stable plugin host
- **P-0002** Wasm plugin kit

## Planning conclusion

For the next few passes, prefer:

1. deepening **P-0484** and **P-0121**,
2. keeping **P-0036 / P-0532 / P-0486** close behind,
3. and treating plugin / shipkit work as adjacent layers that should reuse the boundary-contract vocabulary instead of re-inventing it.

## Freshness anchors

- 2025 State of Rust survey — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- program-management update — https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- safety-critical Rust — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- `cxx` docs — https://cxx.rs/
- UniFFI docs — https://mozilla.github.io/uniffi-rs/
- Diplomat book — https://rust-diplomat.github.io/book/
- component model docs — https://component-model.bytecodealliance.org/
