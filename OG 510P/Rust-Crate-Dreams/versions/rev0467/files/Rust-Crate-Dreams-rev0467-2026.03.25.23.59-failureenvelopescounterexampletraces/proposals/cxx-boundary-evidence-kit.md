---
id: P-0441
title: C++ Boundary Evidence Kit — toolchain/header receipts, ownership matrices, and replayable boundary tests across cxx, autocxx, bindgen, and cbindgen
status: idea
domains: [ffi, c++, build, tooling, safety, interop, ci]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
  - https://cxx.rs/
  - https://google.github.io/autocxx/
  - https://github.com/rust-lang/rust-bindgen
  - https://github.com/mozilla/cbindgen
  - https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
---

# Problem

Rust/C++ interop is one of the most strategically important seams in the ecosystem, and it is not one problem.

Different projects lean on different substrates:

- `cxx` for a safer shared regime,
- `autocxx` for header-driven safe automation,
- `bindgen` for raw generated bindings,
- `cbindgen` for Rust-to-C/C++ header generation,
- and increasingly, language work around in-place initialization because C++ object construction and move semantics do not line up neatly with Rust’s defaults.

The Rust project is explicitly mapping the C++/Rust interop problem space because the seam is broad, important, and not close to “solved.”

What teams still repeatedly lack is not proof that bindings can be generated.

They lack a **portable boundary artifact** that records:

- which headers/macros/compilers were used,
- which ownership/lifetime/exceptions model was assumed,
- which constructors/moves/pinning expectations applied,
- which adapter stack (`cxx`, `autocxx`, `bindgen`, `cbindgen`) was in play,
- and which boundary tests actually passed.

The missing crate is not another binding generator.

The missing crate is a **boundary evidence and replay kit** for mixed Rust/C++ edges.

# What it provides

- `cxx-boundary.toml` — declares headers, include paths, macro defines, compiler families, adapter stack, ownership policy, exception policy, and move/pinning assumptions.
- `boundary.receipt.json` — exact toolchain/header/config information used for one boundary build/test run.
- `ownership-matrix.json` — records how values cross the boundary: by value, borrowed, pointer/handle, unique/shared ownership, pinned/in-place construction, opaque type, exception boundary.
- `boundary.findings.json` — structured results from boundary probes and test scenarios.
- `cxxbundle.zip` — receipts, generated artifacts, minimized repros, compile/link logs, and scenario results.
- `cargo cxx-boundary check` — builds and runs declared boundary scenarios.
- `cargo cxx-boundary explain` — tells a human which assumptions the boundary is relying on and where caveats remain.

# What the crate should provide other people

1. **A boring artifact** for Rust/C++ boundary assumptions and results.
2. **A shared ownership/lifetime vocabulary** across multiple interop stacks.
3. **Replayable mixed-language bug bundles** for CI and maintainers.
4. **A migration aid** when moving between `bindgen`, `autocxx`, `cxx`, or generated C ABI surfaces.
5. **A narrow safety review aid** for one of Rust adoption’s most important seams.

# Persona / who it’s for

- teams incrementally adopting Rust into C++ codebases
- maintainers of Rust crates exposing C++-consumable surfaces
- build/CI engineers for mixed-language projects
- reviewers of ownership-sensitive FFI boundaries

# Users & user stories

- **Interop maintainer**: “Show exactly which headers/macros/toolchains produced this boundary and whether the tests passed.”
- **Reviewer**: “Tell me whether this boundary is assuming pinned construction, opaque handles, exceptions off, or shared ownership.”
- **Migration owner**: “Compare a `bindgen` path and an `autocxx`/`cxx` path using the same boundary scenarios.”
- **Bug reporter**: “Package one boundary replay bundle instead of a vague build failure description.”

# Prior art (and why it’s insufficient)

- `cxx` provides a safer interoperability model, but not a portable evidence bundle across the wider Rust/C++ boundary lifecycle.
- `autocxx` automates large parts of the problem, but still leaves teams to manage scenario coverage and boundary receipts.
- `bindgen` and `cbindgen` are powerful generators, but they are not a shared ownership/pinning/exception evidence layer.
- The Rust project’s interop and in-place-init goals identify the problem space and future substrate, but not the day-to-day artifact other teams can adopt now.

What remains missing is a **receipt/matrix/replay layer** above the existing tools.

# Design goals

1. **Boundary-first** — focus on the seam, not on replacing generators.
2. **Ownership-explicit** — make transfer and aliasing assumptions first-class.
3. **Header/toolchain provenance** — mixed-language failures are often configuration failures.
4. **Scenario-oriented** — real boundary examples beat abstract claims.
5. **Adapter-neutral** — treat `cxx`, `autocxx`, `bindgen`, and `cbindgen` as boundary inputs, not competing religions.

# MVP surface

- Minimal types: `BoundaryManifest`, `BoundaryReceipt`, `OwnershipMatrix`, `BoundaryScenario`, `BoundaryFinding`
- Minimal functions:
  - `capture_boundary_receipt()`
  - `run_boundary_scenarios()`
  - `compare_adapter_paths()`
  - `write_findings()`
  - `bundle_boundary_results()`
- Feature flags:
  - `cxx`
  - `autocxx`
  - `bindgen`
  - `cbindgen`
  - `serde`

# Compatibility story

- Works above existing C++ interop crates and build systems.
- Can model a boundary that uses more than one tool path.
- Supports partial coverage and caveated outcomes.
- Should integrate with ordinary Cargo and external CMake/Bazel/etc. flows via receipts rather than deep build-system replacement.

# Conformance & fixtures

- Fixtures for string/vector/opaque-handle boundaries, callback/lifetime cases, exception-disabled boundaries, ownership transfer, move-sensitive C++ types, and pinned/in-place construction scenarios.
- Goldens for `safe shared regime`, `opaque fallback`, `header mismatch`, `toolchain mismatch`, and `constructor/pinning caveat` outcomes.
- Adapter comparison fixtures using the same boundary scenario across two tool paths.
- Replay bundles suitable for filing mixed-language interop bugs.

# Path to boring stability

- Stabilize `cxx-boundary.toml`, `boundary.receipt.json`, and `ownership-matrix.json` first.
- Keep the ownership vocabulary small and explicit.
- Treat partial support as normal and reviewable.
- Add richer scenario packs only after the core receipts are trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A crate and cargo subcommand that record header/toolchain/adapter assumptions for one Rust/C++ boundary, run a few boundary scenarios, and export a replay bundle showing what was actually tested and under which ownership/pinning policy.

# De-risk plan

1. Start with small scenario fixtures and one or two adapter paths.
2. Keep exception and ownership policy vocabularies narrow.
3. Treat generated-artifact capture and replay as the core value, not ambitious automation.
4. Add in-place-init/pinning scenarios as caveated extensions until the substrate is clearer.

# Non-goals

- Not a new binding generator.
- Not a full C++ ABI model checker.
- Not a build-system replacement.
- Not a guarantee that all Rust/C++ interop problems are captured by scenario tests.

# Architecture & API sketch

```rust
pub struct BoundaryReceipt {
    pub manifest: BoundaryManifest,
    pub toolchains: Vec<ToolchainInfo>,
    pub ownership: OwnershipMatrix,
    pub findings: Vec<BoundaryFinding>,
    pub caveats: Vec<String>,
}

pub fn capture_boundary_receipt(manifest: &BoundaryManifest) -> Result<BoundaryReceipt>;
pub fn run_boundary_scenarios(receipt: &mut BoundaryReceipt, scenarios: &[BoundaryScenario]) -> Result<()>;
pub fn bundle_boundary_results(receipt: &BoundaryReceipt, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `cxx-boundary.toml`, `boundary.receipt.json`, `ownership-matrix.json`, `boundary.findings.json`, `generated/`, `repro/`, `notes.md`.

# Security / safety model

- Preserve exact compiler/header/macro provenance.
- Never hide unsupported ownership or exception cases behind a “pass.”
- Support path and symbol redaction in shared bundles.
- Keep generated artifacts and logs attached to every replayable bundle.

# Maintenance & governance plan

- Maintain a small shared scenario corpus that reflects common boundary pain.
- Version the ownership vocabulary conservatively.
- Keep adapter-specific logic as thin modules.
- Publish examples for incremental adoption into existing C++ repositories.

# Milestones

## 0.1
- manifest + receipt format
- a few boundary scenarios
- replay bundle export

## 0.2
- adapter comparison mode
- richer ownership matrix
- constructor/pinning caveat modeling

## 1.0
- stable receipt schemas
- CI/report adapters
- broader scenario corpus

# Open questions

- What is the smallest ownership vocabulary that still helps reviewers?
- Should exception and panic-boundary modeling be one shared concept or two separate layers?
- Which generated artifacts belong inside the bundle versus referenced externally?

# Sources

- C++/Rust interop problem space mapping: https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- `cxx`: https://cxx.rs/
- `autocxx`: https://google.github.io/autocxx/
- `bindgen`: https://github.com/rust-lang/rust-bindgen
- `cbindgen`: https://github.com/mozilla/cbindgen
- In-place initialization goal: https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
