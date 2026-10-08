# Frontier salience refresh (2026-03-23, pass 228)

## Main judgment

The archive’s broad control-plane frontier still stands.
But the **practical build queue** should now explicitly include the native-build support stack as the next adoption amplifier after docs.rs parity and build-dir transition work.

## Practical queue now

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0472 Docs.rs Build Parity & Evidence Kit**
4. **P-0489 Cargo Build-Dir Consumer Transition Kit**
5. **P-0046 Buildscript UX Kit**
6. **P-0058 Native Deps Kit**
7. **P-0535 Dependency Lifecycle Transition Kit**
8. **P-0484 Toolchain & Target Support Contract Kit**
9. **P-0536 Crate Knowledge Pack Kit**
10. **P-0537 Compile Iteration Feedback Kit**

## Why P-0046 and P-0058 move up now

### They sit at a busy ecosystem seam

Official Rust signals keep converging on the same bottleneck:

- resource usage remains a major pain point,
- docs and support truth still matter a lot,
- Cargo is shifting build-dir assumptions,
- docs.rs is sandboxed, target-sensitive, and explicit about its limits,
- and safety-critical / mixed-language teams still need auditable interop and build evidence.

That makes build/native support more important than another niche runtime helper, service client, or convenience wrapper.

### The substrate is now real enough

This is no longer pure wishcasting.
The substrate exists:

- Cargo documents build-script directives and rerun behavior,
- docs.rs documents sandbox conditions and local/CI testing hooks,
- `system-deps` gives declarative metadata,
- `vcpkg` gives Windows/MSVC-native probing,
- crates.io has better trust surfaces than it used to,
- but the receiver-facing artifact layer is still missing.

### The product seam is distinct

The missing value is not “a better `pkg-config` wrapper”.
It is a support stack that gives:

- maintainers concise build failure bundles,
- CI and reviewers stable fixture outputs,
- downstream users native contract and probe receipts,
- and future tools a typed vocabulary for comparison and diagnosis.

## What should count as success here

For this frontier, a crate should now count as worthy only if it gives another person a compact answer to at least one of these:

- what happened in `build.rs`,
- whether build behavior drifted,
- what native support was promised,
- what backend was attempted,
- why the current machine or CI image failed,
- and what exact next action is reasonable.

## Sources

- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ (“Why is Cargo rebuilding my code?”) — https://doc.rust-lang.org/cargo/faq.html
- Cargo release notes (`OUT_DIR` build-time behavior change) — https://doc.rust-lang.org/beta/releases.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- system-deps docs — https://docs.rs/system-deps/latest/system_deps/
- `system-deps` standardization discussion — https://github.com/gdesmott/system-deps/issues/97
- vcpkg docs — https://docs.rs/vcpkg/latest/vcpkg/
