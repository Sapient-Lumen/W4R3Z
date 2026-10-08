# Epic Proposal: FFI Boundary Kit (`cargo ffi`)

## One-sentence pitch
Turn Rust↔C/C++ integration from a pile of tool-specific conventions into a reviewable release surface with manifests, generated artifacts, diff reports, and downstream-friendly packs.

## Deliverables
- `cargo-ffi` reference implementation
- Schemas:
  - `ffi-manifest/v0`
  - `ffi-pack/v0`
  - `ffi-report/v0`
- Adapters/integrations:
  - bindgen
  - cbindgen
  - cxx / autocxx metadata hooks where feasible
  - CMake/Corrosion packaging notes
- Corpus:
  - representative C ABI crate
  - representative bindgen consumer
  - representative C++ bridge example
- Docs:
  - ownership contract checklist
  - native toolchain troubleshooting
  - release workflow for boundary diffs

## Why now (signals)
- Rust’s safety-critical work says interop is part of the safety story, not a side quest.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The project-goals repo now has an explicit C++/Rust interop problem-mapping effort.
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- Existing tools are valuable, but they do not yet standardize the release boundary itself.
  https://rust-lang.github.io/rust-bindgen/ ; https://github.com/mozilla/cbindgen ; https://google.github.io/autocxx/

## Non-goals
- A stable general-purpose Rust ABI
- Solving every C++ language interop problem in v0
- Replacing bindgen/cbindgen/cxx/autocxx

## Milestones
1) v0: manifest + pack + verify/diff flows for C ABI crates and bindgen consumers
2) v0.2: richer breakage classification + Corrosion/CMake integration examples
3) v1: broader C++ bridge coverage + policy hooks for regulated environments

## Execution posture
- Execute this as part of the ranked native-edge pilot program in [`design/native-edge-pilot-program.md`](../design/native-edge-pilot-program.md), starting with C ABI export lanes before broader C++ bridge / external-build-system lanes.
- Position this as a companion evidence substrate to active interop work, not as a bid to settle every language-level interop question in one crate.
