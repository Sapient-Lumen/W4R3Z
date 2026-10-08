# Gap: Coverage evidence, criterion truth, and CI review are still too fragmented

## Summary
Rust has credible coverage primitives and several strong tools, but ordinary teams still piece together their own workflow for **criterion choice, instrumentation choice, doctest/example handling, cross-run merging, CI policy, and artifact publishing**.

The result is a familiar failure mode: coverage either becomes a vanity percentage in one hosted service, or it becomes too bespoke and brittle to trust. Just as importantly, unlike lanes keep getting flattened into one fake coverage story: rustc/LLVM baseline coverage, Cargo-native orchestration, nextest+doctest merges, external/FFI imports, Tarpaulin contrast, and future decision/MC/DC imports are all real but too easy to narrate as one number. The ecosystem has working parts, but not yet a **Cargo-native, criterion-aware evidence layer** with an explicit lane map for coverage claims and review.

## Why now
- Rust has a stable compiler flag for source-based coverage: `-C instrument-coverage`.
  https://doc.rust-lang.org/rustc/codegen-options/index.html#instrument-coverage
- Rust’s 2026 flagship roadmap now makes coverage criteria strategically visible again: **Safety-Critical Rust** includes implementing **MC/DC coverage support**, and **Building blocks** includes **better test tooling**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The January 2026 safety-critical adoption writeup says industry participants are organizing around upstream MC/DC support rather than treating it as a forever-external requirement.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The official coverage workflow is already real, but it still exposes rough edges and low-level mechanics (profiler runtime requirements, `profraw` / `profdata`, doc-test-specific flags, and report assembly).
  https://doc.rust-lang.org/rustc/instrument-coverage.html
- `cargo-llvm-cov` has emerged as the strongest Cargo-native wrapper around the official source-based flow and already supports line/region/branch-style reporting, `cargo test` / `cargo run` / `cargo nextest`, external tests, C/C++ coverage merging, and multiple export formats.
  https://github.com/taiki-e/cargo-llvm-cov
- nextest’s own coverage docs explicitly say doctest coverage must be merged separately, which makes execution-import truth and merge provenance first-class concerns instead of CI trivia.
  https://nexte.st/docs/integrations/test-coverage/
- Tarpaulin remains valuable, but its model is materially different: its README still says the default Linux backend is `ptrace` on `x86_64`, while macOS and Windows default to LLVM instrumentation. Its 0.35.0 changelog also says delta coverage should not be reported when run-configuration changes would make the comparison meaningless.
  https://github.com/xd009642/tarpaulin
  https://docs.rs/crate/cargo-tarpaulin/latest/source/CHANGELOG.md

## Concrete missing pieces
1. **Versioned coverage manifests**
   - what targets count (`lib`, bins, examples, doctests, benches, integration tests)
   - engine choice and merge strategy
   - include / exclude policy
2. **Explicit criterion profiles**
   - ordinary line / region / branch posture
   - decision / MC/DC watch or import posture
   - direct measurement vs imported or future-facing claims
3. **Portable coverage evidence artifacts**
   - which tool produced the result
   - which execution produced the result
   - criterion and coverage-model posture
   - toolchain / target / profile metadata
   - merged-input provenance
4. **CI review semantics**
   - global minimums are not enough
   - per-path / per-target / changed-code gates should be first-class
   - `fail`, `warn`, `informational`, `inconclusive`, and `not-comparable` all need explicit meaning
5. **Cross-run composition**
   - native tests + nextest + external harnesses + examples + doctests + linked C/C++ should compose into one reviewable pack
6. **Honest comparability**
   - distinguish “same engine, same criterion, comparable” from “merged across unlike runs, interpret carefully”

## Lane-map consequence
- Read this gap together with `design/coverage-evidence-lane-map.md`. The missing contribution is not another universal percentage surface, but a lane-aware layer that keeps **official LLVM baseline**, **Cargo-native orchestration**, **split merge lanes**, **external/FFI imports**, **Tarpaulin contrast**, and **future decision/MC/DC imports** reviewable as separate truths.

## Desired properties
- Converge existing tools instead of replacing them.
- Preserve criterion and execution provenance so reviewers can see *what* was measured and *how* it was produced.
- Treat doctests/examples/external tests as first-class citizens, not footnotes.
- Make merged coverage reviewable and diffable in CI.
- Prefer portable artifacts over screenshots and opaque hosted percentages.

## Distinction from nearby archive entries
- **Perf Labs** standardizes runtime performance evidence; this kit standardizes **coverage evidence and CI policy**.
- **FuzzPack Kit** standardizes fuzz corpora/crash artifacts; this kit standardizes **criterion-aware coverage review artifacts** across test styles.
- **Safety Evidence Kit** unifies unsafe/audit/formal evidence; this kit supplies criterion-aware coverage inputs that Safety Evidence can ingest rather than replace.
- **Test Execution Evidence Stack** standardizes run subject and execution imports; this kit must import that truth rather than quietly redefining what ran.
