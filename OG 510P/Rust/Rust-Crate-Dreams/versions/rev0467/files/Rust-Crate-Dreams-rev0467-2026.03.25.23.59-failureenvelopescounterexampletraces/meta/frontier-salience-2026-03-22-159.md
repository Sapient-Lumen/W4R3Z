# Frontier salience snapshot — 2026-03-22-159

This pass deliberately chose a **broad rerank** instead of opening another narrow top-level lane.
The freshest official signals now make a handful of already-existing proposals stand out more sharply than the rest.

## Why the frontier moved

Four current signals matter most:

- the 2025 State of Rust survey still reports **resource usage** and **debugging** as major productivity problems;
- the March 2026 Rust challenges write-up explicitly calls out **no_std gaps**, **cross-compilation friction**, **GUI compile-time pain**, and **safety-critical tooling gaps**;
- the January 2026 safety-critical post explicitly asks for **target-focused readiness checklists**, **dependency lifecycle guidance**, **safety-case-friendly async runtime requirements**, and better **interop** tooling;
- and the 2026 program-management update moved Rust’s strategic framing toward **roadmaps** and **application areas** like **Cross-language interop** and **Safety-critical & regulated**.

That combination favors crates that make support, stability, interop, runtime posture, and reviewability legible.

## Ranked near-term frontier

### 1. **P-0484 Toolchain & Target Support Contract Kit**

Strongest day-to-day missing crate right now.
The official safety-critical guidance practically describes a missing artifact in plain language: a target-focused readiness checklist.
The March 2026 challenges post also reinforces cross-compilation and no-`std` support pain.
A worthy crate here should publish target-readiness, support-class, override-lineage, component-availability, exercise-scope, and prerequisite truth.

### 2. **P-0036 MSRV Workspace Lab**

Still extremely strong because Rust adoption in regulated and long-lived systems depends on stability windows, dependency drift control, and honest lockfile-authoring stories.
The missing value is not another “find the oldest compiler” searcher; it is a support contract for policy activation, command-family floors, and lockfile-authoring truth.

### 3. **P-0121 FFI Boundary & Bindings Conformance Kit**

Moved upward because 2026 strategy explicitly elevates cross-language interop, and the safety-critical post makes long-lived C/C++ interop a first-class Rust adoption story.
The worthy crate here is the evidence/conformance layer above generators and bridge crates.

### 4. **P-0532 Async Runtime Assurance Profile Kit**

Still one of the sharpest “epic crate” opportunities because the safety-critical post explicitly asks for safety-case-friendly async runtime requirements, while Tokio / Embassy / RTIC now expose enough real differences to classify honestly.

### 5. **P-0486 Debuggability Support Contract Kit**

The survey and debugging follow-up work keep this lane hot.
The worthy crate is not a debugger; it is the support contract for symbol sidecars, support posture, backend coverage, and release-bundle handoff.

### 6. **P-0035 cargo-build-insights**

Compile-time and storage pain remain official ecosystem problems, and GUI work especially suffers from slow edit/build loops.
The sharper missing layer is a historical comparison and drift-adjudication crate above Cargo build-analysis substrate.

### 7. **P-0483 Public API Readiness Bundle Kit**

Still high because library quality remains central to ecosystem health.
A worthy crate here helps maintainers publish one joined release-review answer instead of scattering semver, docs, cfg-availability, and waiver posture across tools and CI logs.

### 8. **P-0534 Service Readiness & Drain Contract Kit**

Very strong in production/backend settings because more Rust services now need explicit readiness/drain/in-flight fate stories rather than framework-specific folklore.

### 9. **P-0017 Trust Lens**

Still high because supply-chain trust, malicious-crate incidents, trusted-publishing posture, audit imports, and watch-channel gaps increasingly need one compact policy/evidence answer.

### 10. **P-0503 Assurance Case Workbench Kit**

Not the most common day-to-day pain, but one of the most strategically important frontiers for regulated adoption.
The ecosystem increasingly has evidence-producing substrate; it still lacks a boring review/import/export contract above it.

## High-value watch list outside the top ten

Keep these active so the archive preserves variety instead of collapsing into pure Cargo/support work:

- **P-0003 Array API** — scientific / ML / backend portability
- **P-0002 Wasm Plugin Kit** — sandboxed extensibility
- **P-0081 Stable Plugin Host Kit** — native plugin ecosystems
- **P-0224 OpenAPI 3.1 + JSON Schema 2020-12 Toolchain Kit** — API/data-contract toolchains
- **P-0101 Crash Artifact & Symbolication Workbench Kit** — incident support / desktop / ops
- **P-0527 LittleFS Native Adoption Kit** — embedded storage and power-cut evidence
- **P-0027 Text Input Kit** — GUI/product-engineering substrate
- **P-0485 Verification Campaign Workbench Kit** — formal methods and safety evidence

## Main conclusion

The archive’s strongest frontier is now **support-contract infrastructure**: crates that tell other people what is actually supported, what assumptions are in force, what evidence exists, and what changed.
That should not erase protocol, GUI, scientific, embedded, or assurance frontiers.
But it should change how the archive ranks them.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
