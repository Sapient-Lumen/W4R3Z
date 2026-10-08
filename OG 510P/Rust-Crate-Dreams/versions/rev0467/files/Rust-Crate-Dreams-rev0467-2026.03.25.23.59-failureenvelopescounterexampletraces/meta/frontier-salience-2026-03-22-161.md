# Frontier salience snapshot — 2026-03-22-161

This refresh keeps **P-0484 Toolchain & Target Support Contract Kit** firmly at the top and makes the reason more concrete: the remaining gap is not target installation, it is **support-evidence topology**.

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

## Why P-0484 strengthened again

Recent official signals all point toward the same missing layer:

- Rust’s challenge scan still names cross-compilation and `no_std` friction.
- The safety-critical write-up still asks for target-focused readiness truth that another team can audit.
- Cargo’s build-dir-layout-v2 call-for-testing says many projects rely on unspecified internal layout details.
- docs.rs target defaults and Rust-project target tiers can move without a project changing its own code.

That means a support-contract crate has more leverage than many narrower shipkits, because it helps other people interpret the whole platform promise honestly.

## Newly explicit sub-problems inside P-0484

### Artifact-route truth
How does a workflow actually discover its outputs?
Stable Cargo interfaces and brittle `target/` or build-dir spelunking should not be treated as equivalent.

### Host-target topology truth
Which parts of a “cross-target” lane are still host-only?
Build scripts, proc macros, runners, emulators, docs surfaces, and upload steps need explicit topology.

### Official-support drift truth
How do project claims react when target tiers or hosted-docs defaults change?
A project support class should not silently shadow official changes.

## Planning conclusion

For the next pass or two, prefer:

1. fully rounding out **P-0484**,
2. keeping **P-0121** and **P-0036** close behind,
3. and treating async/debug/plugin lanes as consumers of support-contract vocabulary where possible.

## Freshness anchors

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2025/05/26/demoting-i686-pc-windows-gnu/
- https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
