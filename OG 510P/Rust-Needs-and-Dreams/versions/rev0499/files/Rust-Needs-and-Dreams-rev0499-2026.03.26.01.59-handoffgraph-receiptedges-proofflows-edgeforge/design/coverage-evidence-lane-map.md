# Design: Coverage Evidence lane map (LLVM baseline, nextest+doctest merge, external/FFI imports, Tarpaulin contrast, and future decision/MC/DC imports)

## Goal
Sharpen **Coverage Evidence Kit** so the archive stops treating “coverage support” as one bucket.
Rust already has real coverage lanes, and they differ materially in **criterion**, **engine/runtime assumptions**, **execution source**, **merge behavior**, **comparability**, and **what downstream reviewers may conclude**.

The archive should therefore keep coverage review grounded in a lane map instead of one flattened percentage.

## Signals from the current ecosystem
- Rust’s 2026 flagship roadmap explicitly puts **MC/DC coverage support** under **Safety-Critical Rust** and **better test tooling** under **Building blocks**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The January 2026 safety-critical adoption post says earlier MC/DC work stalled partly because of maintenance/ownership concerns, and says companies are now organizing around doing upstream MC/DC support the right way.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The rustc coverage chapter keeps the official LLVM source-based lane explicit: `-C instrument-coverage`, profiler runtime requirements, `LLVM_PROFILE_FILE`, raw `.profraw` files, `llvm-profdata merge`, `llvm-cov report/show`, and function / instantiation / line / region statistics.
  https://doc.rust-lang.org/rustc/instrument-coverage.html
- `cargo-llvm-cov` remains the strongest Cargo-native wrapper around that official lane and explicitly supports line/region coverage, optional branch coverage, `cargo test`, `cargo run`, `cargo nextest`, external tests, C/C++ coverage, proc-macro/UI coverage, and multiple report/export formats.
  https://github.com/taiki-e/cargo-llvm-cov
- nextest’s current docs still say doctest coverage must be merged separately because nextest does not currently support doctests.
  https://nexte.st/docs/integrations/test-coverage/
- Tarpaulin remains a real contrasting engine family, and its changelog now explicitly refuses delta coverage when run configuration changes would make comparisons meaningless.
  https://github.com/xd009642/tarpaulin
  https://docs.rs/crate/cargo-tarpaulin/latest/source/CHANGELOG.md

## The lanes

### 1) Official LLVM baseline lane
This is the baseline lane the archive should treat as the closest thing to “core coverage truth” today.

What defines it:
- rustc `-C instrument-coverage`
- profiler runtime requirements
- raw `.profraw` emission and explicit `.profdata` merge
- `llvm-cov report/show`
- ordinary rustc summary statistics: function, instantiation, line, region

What this lane is good for:
- a stable baseline review path for ordinary Rust crates
- first pilot lane for portable coverage packs
- grounding later merge/import lanes in one auditable native basis

What it must **not** silently become:
- branch/decision/MC/DC truth by implication
- “all tests” truth when doctests/examples/external binaries were not included
- a hosted-service percentage detached from the underlying execution and merge story

### 2) Cargo-native LLVM orchestration lane
This is the `cargo-llvm-cov` shaped lane above the rustc baseline.

What defines it:
- Cargo-shaped orchestration (`test`, `run`, `nextest`, `report`)
- explicit export formats (`json`, `lcov`, `cobertura`, Codecov custom JSON, text, html)
- optional branch coverage and optional doctest support on nightly paths
- proc-macro/UI coverage and workspace-aware orchestration

Why it deserves a separate lane:
- it is not merely rustc raw coverage; it is a higher-level orchestration surface
- it determines what got instrumented, how reports were generated, and what exports exist
- it can drive multiple execution families without becoming the same thing as those families

Design rule:
- preserve the **cargo-llvm-cov lane** as a named producer, not a transparent implementation detail

### 3) Split execution + merge lane (`nextest` + doctests + shard imports)
This is the first lane where the archive must force execution truth and merge provenance to stay explicit.

What defines it:
- multiple executions contributing to one reviewable result
- nextest-run workloads plus a separate doctest collection step
- optional shard or subset composition
- explicit merged-input provenance and caveats

Why it deserves a separate lane:
- nextest’s own docs say doctests must be merged separately
- one combined coverage percentage can otherwise hide that different execution surfaces were used
- the merge step becomes part of the truth, not CI plumbing trivia

Design rule:
- a merged result must cite each imported execution lane and preserve `comparable` / `advisory` / `not-comparable` posture explicitly

### 4) External / black-box / FFI import lane
This lane covers coverage that comes from outside the ordinary `cargo test` / `cargo run` / `cargo nextest` path.

What defines it:
- external harnesses or binaries
- black-box integration tests
- C/C++ coverage linked into Rust results
- imported runner-native recordings or external raw artifacts

Why it deserves a separate lane:
- this is where “coverage of the product” and “coverage of Rust crate tests” stop being the same sentence
- FFI/native code inclusion is valuable, but it changes what the result means
- imported execution and imported raw artifacts become first-class truth, not an invisible add-on

Design rule:
- preserve language/runtime boundary, import lossiness, and include/exclude policy explicitly instead of laundering all merged data into one Rust-only claim

### 5) Tarpaulin contrast lane
This lane exists so the archive never quietly treats unlike engines as interchangeable.

What defines it:
- a materially different engine/backend story than LLVM source-based coverage
- platform/backend differences that affect what is being measured and how
- explicit comparability limits when configuration changes matter

Why it deserves a separate lane:
- Tarpaulin remains useful precisely because it is not the same lane as `cargo-llvm-cov`
- a shared review layer should converge at the artifact/policy layer, not by pretending the engines are identical

Design rule:
- Tarpaulin results should be importable, reviewable, and gateable **without** becoming fake LLVM-equivalent evidence

### 6) Decision / MC/DC watch-and-import lane
This lane exists because the roadmap pressure is now real, but the ordinary coverage ecosystem is not there yet.

What defines it:
- future or imported decision/MC/DC criteria
- safety-critical consumers and case assembly
- explicit non-equivalence with line/region/branch outcomes

Why it deserves a separate lane:
- the 2026 roadmap says MC/DC support is a real flagship target
- the safety-critical writeup says the ownership/maintenance model matters just as much as the technical implementation
- ordinary line/region/branch coverage must not silently overclaim decision or MC/DC meaning

Design rule:
- until native decision/MC/DC support is real and adopted, this lane should be preserved as **watch-only** or **imported** rather than narrated as already solved by ordinary coverage tools

## Review rules that follow from the lane map
1. Keep **criterion identity** separate from **coverage percentage**.
2. Keep **execution truth** separate from **coverage aggregation**.
3. Keep **native/raw artifacts** separate from **portable review artifacts**.
4. Keep **engine identity** separate from **comparability claims**.
5. Keep **ordinary CI quality gates** separate from **safety-critical imports**.
6. Keep **Rust-only claims** separate from **Rust + FFI/native merged claims**.
7. Keep **watch-only future-facing criterion imports** separate from **directly measured criteria**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another replacement coverage engine,
- another hosted percentage service,
- another badge normalizer,
- or another CI snippet that hides merge/import details.

It is a thin `cargo cov` / `coverage-pack/v0` layer that can preserve:
- lane identity,
- criterion profiles,
- execution imports,
- merge reports,
- gate outcomes,
- and bounded downstream handoffs.

That means downstream reviewers can answer:
- *which lane produced this result?*
- *what criterion did it actually measure?*
- *what executions were merged?*
- *what was comparable and what was not?*
- *what may a safety-critical consumer conclude, and what must remain watch-only?*

## Immediate archive consequences
Read this together with:
- `design/coverage-evidence-kit.md`
- `design/coverage-evidence-pilot-program.md`
- `gaps/coverage-evidence-and-ci-review.md`
- `proposals/epic-coverage-evidence-kit.md`
- `design/test-execution-evidence-stack.md`
- `design/safety-evidence-kit.md`
- `design/safety-critical-evidence-stack.md`

The archive should now prefer **lane-aware coverage packs before one-number dashboards**.
