# Native build & build-script stack — incubation note (2026-03-08)

This note sharpens three adjacent proposals into one more buildable stack:

- **P-0046 buildscript-ux-kit**
- **P-0059 buildscript-testkit**
- **P-0058 native-deps-kit**

## Main judgment

This pass argues that the archive’s next worthwhile frontier to sharpen is a **native build / build-script support stack**.

The Rust ecosystem already has real substrate here:

- Cargo documents build-script directives, `links`, metadata handoff, override mechanisms, and rerun semantics.
- Cargo 1.84 added `cargo::error=MESSAGE`.
- `system-deps` already proves that declarative native requirements can live in manifest metadata.
- `vcpkg` already proves that Windows/MSVC-native probing can emit Cargo metadata.
- the Rust project has already explored sandboxed build scripts and explicitly calls out `-sys` crates as a first-class use case.

But that substrate is **not yet a boring workflow contract**.

Current official docs and live issues still point to the same gap:

- build scripts default to conservative reruns if authors do not narrow change detection,
- `OUT_DIR` persists across rebuilds and can surprise authors,
- warnings from non-path dependencies are often hidden unless the build fails or users opt into `-vv`,
- `cargo::error` exists but the presentation of failing build scripts is still noisy in practice,
- and Cargo still says after-the-fact rebuild diagnosis is not easy yet.

That makes the sharper missing value a stack of **reports, tests, and contracts** above existing build-script substrate.

## Why this is a real crate frontier

The missing value is not “replace Cargo build scripts”.

The missing value is to make native-build support boring enough that maintainers can hand another person a compact artifact answering:

- what native dependency contract was declared,
- what probe backends were attempted,
- what directives were emitted,
- what warnings or failures mattered,
- and whether behavior regressed between releases.

That is a support/review/testing seam, not just another wrapper crate.

## Stack members

### P-0046 buildscript-ux-kit

This is the **first** incubation target in this stack.

Why first:

- it helps all build scripts, not only native dependency probes,
- current official docs plus live issues show that presentation/noise problems remain unsolved,
- and it creates the typed directive and summary vocabulary that P-0059 and P-0058 can reuse.

Its first job is to emit one boring bundle:

- `buildscript-report.json`
- `buildscript-summary.txt`
- `policy-gate.report.json`
- `notes.md`

That gives other people a concise support artifact instead of “rerun with `-vv` and paste the whole log”.

### P-0059 buildscript-testkit

This should be the **second** incubation target.

Why second:

- the archive already has a strong case that build scripts are copied, fragile, and usually untested,
- but a stable normalized directive / summary vocabulary is easier to define after P-0046,
- and a fixture corpus becomes much more useful once reports can be compared in a shared shape.

Its first job is to make build scripts reviewable in CI with:

- `buildscript-run.report.json`
- `directives.normalized.json`
- `fixture-manifest.toml`
- `notes.md`

### P-0058 native-deps-kit

This should be the **third** incubation target, even though it may have the highest ultimate upside.

Why third:

- it spans multiple discovery ecosystems (`pkg-config`, `vcpkg`, vendored/source-build),
- it benefits from already having a report vocabulary and a test harness,
- and it can then focus on the real missing value: a **declarative native contract + doctor UX**, not just another probe helper.

Its first job is to emit:

- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `consumer-doctor.txt`

## Recommended incubation order

### First: P-0046

The best immediate crate in this frontier is the one that gives users a **human-scale explanation** of what the build script did and what action they should take.

### Second: P-0059

Once the archive has a stable normalized vocabulary for directives and failures, the next valuable move is to make those behaviors testable.

### Third: P-0058

Once reporting and fixture/testing vocabulary exist, the larger “boring native contract” crate can be designed with better constraints and less hand-wavy scope.

## What the first crate should provide other people

If the archive had to ship only one native-build-adjacent crate next, it should likely be **P-0046 buildscript-ux-kit**.

That crate should provide other people:

1. a short actionable failure summary,
2. a typed normalized build-script report,
3. a workspace-scoped policy gate for warnings/noise classes,
4. a redaction-aware support artifact that can travel with bug reports,
5. and a foundation vocabulary for later testing and native-contract crates.

That is a strong 0.1 because it helps end users, CI maintainers, IDEs, and maintainers immediately.

## Shared contract vocabulary the stack should converge on

Across all three crates, keep these ideas aligned:

- `observed_directive`
- `backend_attempt`
- `suggested_fix`
- `manual_review_required`
- `redaction_policy`
- `normalized_path_placeholder`
- `env_allowlist`
- `no_network_expected`
- `comparison_baseline`
- `bundle_schema_version`

If future passes rename these independently in each proposal, that is drift.

## Anti-patterns for this stack

- Do not treat `cargo::error` existing as proof that build-script UX is solved.
- Do not treat `system-deps` existing as proof that cross-platform native dependency management is already boring.
- Do not turn P-0059 into a full Cargo emulator.
- Do not let P-0058 become an attempt to replace OS package managers.
- Do not silently merge sandboxing, reporting, testing, and native contract work into one giant “build.rs improvement” blob.

## Repo implication

For the next few passes, the archive should prefer:

- fixture/schema stubs,
- report/receipt vocabulary,
- explicit incubation order,
- and sharper proposal planning for P-0046 / P-0059 / P-0058,

rather than adding more native-build-adjacent proposal count.

## Sources

- Cargo build scripts reference: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ (“Why is Cargo rebuilding my code?”): https://doc.rust-lang.org/cargo/faq.html
- Cargo unstable warnings config: https://doc.rust-lang.org/cargo/reference/unstable.html#warnings
- Cargo changelog (`cargo::error`, build-analysis, new build-dir layout): https://doc.rust-lang.org/cargo/CHANGELOG.html
- `system-deps` docs: https://docs.rs/system-deps/latest/system_deps/
- `vcpkg` docs: https://docs.rs/vcpkg/latest/vcpkg/
- `system-deps` standardization discussion: https://github.com/gdesmott/system-deps/issues/97
- Cargo issue #10159 (noisy build-script errors): https://github.com/rust-lang/cargo/issues/10159
- Cargo issue #15792 (still noisy build-script errors): https://github.com/rust-lang/cargo/issues/15792
- Rust project goal: sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
