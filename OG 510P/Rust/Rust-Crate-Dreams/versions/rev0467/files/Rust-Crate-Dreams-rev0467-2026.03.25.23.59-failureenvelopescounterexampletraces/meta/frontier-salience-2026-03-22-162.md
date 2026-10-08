# Frontier salience snapshot — 2026-03-22-162

This refresh keeps **P-0484 Toolchain & Target Support Contract Kit** at the top, but introduces a new adjacent high-salience lane: **P-0535 Dependency Lifecycle Transition Kit**.

## Ranked frontier after the latest scan

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0121 FFI Boundary & Bindings Conformance Kit**
3. **P-0036 MSRV Workspace Lab**
4. **P-0535 Dependency Lifecycle Transition Kit**
5. **P-0532 Async Runtime Assurance Profile Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0081 Stable Plugin Host Kit**
8. **P-0002 Wasm Plugin Kit**
9. **P-0503 Assurance Case Workbench Kit**
10. **P-0017 Trust Lens**

## Why P-0535 enters the top cluster

Recent official signals make one missing layer unusually explicit:

- the safety-critical write-up directly asks for reusable **dependency lifecycle** patterns,
- the Vision Doc work argues for more **supportive interfaces** from crates,
- the 2025 State of Rust survey says online docs remain the preferred canonical reference,
- and crates.io now publishes stronger trust/support context that still stops short of local architectural placement truth.

That combination points toward a crate that helps teams say **where third-party crates are allowed, what seam contains them, and how they are expected to leave over time**.

## Planning conclusion

For the next pass or two, prefer:

1. keeping **P-0484**, **P-0121**, and **P-0036** in the lead cluster,
2. incubating **P-0535** as the new dependency-lifecycle / criticality / seam lane,
3. and reusing trust/MSRV/off-ramp vocabulary instead of duplicating it.

## Freshness anchors

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
