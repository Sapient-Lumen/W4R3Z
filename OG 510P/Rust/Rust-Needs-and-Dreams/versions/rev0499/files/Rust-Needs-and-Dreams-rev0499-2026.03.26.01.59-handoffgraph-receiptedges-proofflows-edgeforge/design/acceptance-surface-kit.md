# Design: Acceptance Surface Kit (`cargo acceptsurf`, `acceptance-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **solver- and borrow-check-sensitive acceptance surfaces** in Rust: advanced trait obligations, higher-ranked bounds, lending patterns, local/send split traits, workaround formulations, nightly experiments, and compiler-lane migrations.

This should help answer questions like:
- which advanced patterns this crate intentionally supports,
- which examples are expected to compile versus fail,
- which outcomes were checked on stable/beta/nightly and which on experimental lanes like next-solver or Polonius,
- which workarounds are semantic equivalents versus lossy stopgaps,
- whether a change is a regression, an intentional newly-accepted case, or a known unsupported pattern,
- and what evidence backs those claims.

It should **not** replace `compiletest`, `trybuild`, `ui_test`, trait design work, or borrow-checker language design.
It should make acceptance truth reviewable and attachable.

## References (signals)
- The 2026 flagships explicitly aim to stabilize the next-generation trait solver and frame lending iterators / evolvable trait hierarchies as part of “unblocking dormant traits”.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 next-solver goal says the new solver is intended to fully replace the existing trait-system components, fix long-standing unsoundnesses, improve compile-times, and continue toward stabilization of `-Znext-solver=globally`; it also says more lints and rustdoc should move to the new solver.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- The 2025H2 Polonius goal says the nightly implementation should pass NLL problem case #3, accept lending iterators, be stabilizable, and include debugging / dump tooling for the analysis.
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- The evolving-traits goal is directly about trait-family transitions like `Deref: Receiver`, `Iterator: LendingIterator`, and local/send split families generated today with crates like `trait_variant`.
  https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- `compiletest` and the compiler UI test suites prove that large structured acceptance/regression inventories are tractable, but they are compiler-internal rather than a reusable ecosystem artifact boundary.
  https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
  https://rustc-dev-guide.rust-lang.org/tests/ui.html
- `trybuild` and `ui_test` prove libraries already need compile-pass / compile-fail harnesses, but those results usually stay local to one repo with no portable packaging or reason model.
  https://docs.rs/trybuild
  https://docs.rs/ui_test

## Design principles
1. **Separate acceptance from diagnostics.** “This compiles” and “this produces a nice error” are related but distinct surfaces.
2. **Compiler lanes are first-class.** Stable, beta, nightly, next-solver, Polonius, and future experimental lanes must remain distinguishable.
3. **Patterns deserve names.** The unit of review should be a named code-pattern family, not an opaque pile of `.rs` files.
4. **Workarounds are part of the contract.** Macro expansion tricks, boxed erasure, alternate bounds, and split-family adapters must be recorded honestly.
5. **Reason-coded outcomes beat snapshot mysticism.** A changed `.stderr` is not enough; the artifact should say whether the semantic outcome changed.
6. **Do not universalize edge cases.** v0 should support selective adoption for crates that live near these boundaries, not impose a compiler-regression culture on everyone.
7. **Evidence over vibes.** Pass/fail/xfail/regression/improvement claims need executable reports.

## Artifact family

### 1) `acceptance-subject/v0`
Top-level declaration of the subject under review.

Fields should include:
- subject id / version
- crate / workspace / module / feature family identity
- domain tags (`trait-family`, `borrow-pattern`, `lending`, `dyn-dispatch`, `local-send-split`, `opaque-return`, `other`)
- intended audience (`library`, `compiler-adjacent`, `macro`, `framework`, `experiment`)
- primary docs / issue links / RFC links
- linked profiles and packs

### 2) `pattern-catalog/v0`
Named pattern families whose acceptance matters.

Fields should include:
- pattern id
- short human name
- pattern class (`compile-pass`, `compile-fail`, `known-unsupported`, `future-lane`, `regression-guard`)
- representative fixture paths or embedded snippets
- semantic summary of what the pattern is testing
- related trait / borrow / lifetime / dyn / generator / pointer tags
- severity if behavior changes

Examples might include:
- HRTB normalization case
- lending-iterator borrow pattern
- local/send split trait expectation
- `dyn` async trait workaround case
- “accepted on next-solver, rejected on stable” exploratory case

### 3) `compiler-lane-profile/v0`
Describes the compiler lane used for checking.

Fields should include:
- toolchain channel / version / target triple
- lane kind (`stable`, `beta`, `nightly`, `next-solver`, `polonius`, `custom-flags`, `other`)
- relevant flags (`-Znext-solver=globally`, Polonius toggle, compare mode, edition, feature gates)
- whether rustdoc / lints / doctest contexts are involved
- normalization / bless posture
- comparability notes with other lanes

### 4) `acceptance-expectation-set/v0`
Declares expected outcomes for a set of patterns.

Fields should include:
- referenced patterns
- expected state per lane (`pass`, `fail`, `xfail`, `unstable-pass`, `unstable-fail`, `not-applicable`)
- reason classes (`borrow-check-limit`, `trait-solver-limit`, `object-safety-limit`, `workaround-required`, `known-unsound-old-lane`, `intentional-rejection`, `other`)
- whether diagnostics text is normative, advisory, or ignored
- migration notes / deprecation windows
- owner / review metadata

### 5) `workaround-profile/v0`
Describes alternate formulations that recover or approximate support.

Fields should include:
- workaround id
- source pattern ids and target supported pattern ids
- semantic status (`equivalent`, `approximate`, `lossy`, `ergonomic-only`, `performance-cost`, `other`)
- technique (`macro shim`, `trait split`, `boxing`, `erased dyn`, `extra bound`, `adapter type`, `cfg gate`, `nightly-only`, `other`)
- costs and caveats
- removal conditions if a future compiler lane makes it unnecessary

### 6) `acceptance-vector-set/v0`
Golden vectors for checking acceptance truth.

Fields should include:
- vector id
- referenced pattern ids
- lanes to exercise
- expected semantic outcome changes or invariants
- platform or edition requirements
- snapshot / normalization settings if relevant
- negative and unsupported cases

### 7) `acceptance-check-report/v0`
Records what actually happened.

Fields should include:
- subject and lanes checked
- vectors run / skipped
- observed pass/fail/xfail states
- changed reason classes
- snapshot drift notes if present
- attached stderr/stdout snapshots, minimized repros, or dump-tool output when relevant
- toolchain / platform / target details

### 8) `acceptance-diff-report/v0`
Explains changes between two acceptance states.

Fields should include:
- old/new subject or report references
- newly accepted patterns
- newly rejected patterns
- changed workaround requirements
- lane-specific deltas
- suspected compiler / crate / config causes
- migration guidance

### 9) `acceptance-pack/v0`
Bundle of the above plus human-facing docs, CI pointers, release notes, and issue links.

## CLI shape
`cargo acceptsurf` should be a thin orchestrator, not a new compiler test framework.

Potential commands:
- `cargo acceptsurf init` — scaffold an acceptance surface
- `cargo acceptsurf export` — emit subjects, pattern catalogs, and expectations
- `cargo acceptsurf check` — run vectors across selected lanes
- `cargo acceptsurf diff` — compare reports across versions / toolchains / flags
- `cargo acceptsurf bless` — update expected snapshots while preserving semantic reason metadata
- `cargo acceptsurf pack` — bundle an `acceptance-pack/v0`

The tool should prefer adapters to `trybuild`, `ui_test`, compiler UI tests, or custom scripts rather than replacing them.

## Initial targets
A first credible version should start where the seam is already undeniably real:
1. **Trait-solver pilot**
   - one crate or fixture set covering higher-ranked bounds, associated-type normalization, or return-position opaque bounds
   - stable vs nightly vs next-solver lane comparison
2. **Borrow-check / Polonius pilot**
   - one lending-iterator or NLL-problem-style case
   - stable/nightly/Polonius comparison
3. **Trait-family evolution pilot**
   - one `Deref` / `Receiver`-style or `Iterator` / `LendingIterator`-style conceptual split
   - one local/send split family using `trait_variant`-style workarounds
4. **Library-consumer pilot**
   - one advanced public crate publishes which patterns it supports and which remain intentionally unsupported

The kit should support both **promotion** (these patterns are part of our supported surface) and **deferral** (these patterns are experiments or release blockers, not promises yet).

## What good adoption looks like
A good v1 does not need to predict the final shape of every compiler transition.
It needs to prove that the ecosystem can publish honest acceptance truth.

Success would look like:
- one report that makes stable/nightly/experimental-lane acceptance differences obvious,
- workaround profiles that reveal when “supported” really means boxing, trait splitting, or macro indirection,
- diffs that separate semantic regressions from harmless snapshot churn,
- release notes and issue reports that attach one pack instead of many ad hoc test links,
- and future solver / borrow-check improvements landing into an ecosystem that already records what changed.

## Boundaries with other archive proposals
- **Compile Guidance Kit** owns diagnostic wording, lint catalogs, and fix/help surfaces; Acceptance Surface Kit owns whether patterns compile and under which lanes.
- **Trait Surface Kit** owns trait-family semantics and dyn posture; this kit owns cross-toolchain acceptance evidence for advanced trait patterns.
- **Lending Surface Kit** owns borrowing-aware sequence semantics; this kit owns whether borrowing-heavy patterns are accepted by current compiler lanes.
- **Spec Conformance Kit** owns spec references and executable conformance vectors; this kit owns pragmatic compiler-lane acceptance claims during active implementation evolution.
- **DocProof Kit** owns executable documentation; this kit owns semantic acceptance claims that may live underneath docs and examples.

## Failure modes to avoid
- turning stderr snapshots into the only source of truth;
- flattening stable/nightly/next-solver/Polonius into one fake compiler lane;
- treating every compile-fail example as a supported product surface;
- hiding workaround costs behind “works with helper crate” language;
- or pretending all acceptance drift is either a crate bug or a compiler bug when sometimes it is an intentional evolution.
