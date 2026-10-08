# Frontier salience snapshot — 2026-03-22-163

This refresh keeps the support-contract frontier centered on toolchain, interop, MSRV, and dependency-lifecycle work, but promotes **P-0434 Sanitizer Profile & Evidence Kit** into the high-salience cluster.

## Ranked frontier after the latest scan

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0121 FFI Boundary & Bindings Conformance Kit**
3. **P-0036 MSRV Workspace Lab**
4. **P-0535 Dependency Lifecycle Transition Kit**
5. **P-0532 Async Runtime Assurance Profile Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0434 Sanitizer Profile & Evidence Kit**
8. **P-0503 Assurance Case Workbench Kit**
9. **P-0011 Crate Health Contract Kit**
10. **P-0017 Trust Lens**

## Why P-0434 enters the top cluster

Recent official signals make one missing layer unusually explicit:

- the 2026 goals slate still includes stabilization of **MemorySanitizer and ThreadSanitizer** plus precompiled instrumented standard libraries;
- the current sanitizer docs are now concrete about the sharp workflow seams: `--target`, `-Zbuild-std`, `external-clangrt`, and `llvm-symbolizer`;
- the March 2026 challenges post again says debugging and safety-critical tooling gaps remain meaningful friction.

That combination points toward a crate that helps teams publish **instrumentation scope**, **runtime-linkage truth**, **symbolization routes**, and **suppression policy** instead of one vague “sanitizers enabled” claim.

## Planning conclusion

For the next pass or two, prefer:

1. keeping **P-0484**, **P-0121**, **P-0036**, and **P-0535** in the lead cluster,
2. incubating **P-0434** as the debugging/safety-critical workflow lane for sanitizer receipts and handoff bundles,
3. and resisting the temptation to express sanitizer evidence as just another target-support or debugger-support note.

## Freshness anchors

- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
- https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
