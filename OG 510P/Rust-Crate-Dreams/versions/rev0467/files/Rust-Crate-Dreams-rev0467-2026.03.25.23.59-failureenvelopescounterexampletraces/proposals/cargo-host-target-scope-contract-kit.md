---
id: P-0505
title: Cargo Host/Target Scope Contract Kit — config-scope receipts, mixed-build diffs, and host-target diagnosis
status: idea
domains: [cargo, build-config, cross-compilation, proc-macros, rustdoc, ci, devtools]
last_reviewed: 2026-03-08
evidence:
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://github.com/rust-lang/cargo/issues/14046
  - https://github.com/rust-lang/docs.rs/issues/1580
---

# Problem

Cargo’s build world is not one thing.
It is a **mixed world** containing:

- target artifacts,
- host-only artifacts such as build scripts and proc macros,
- rustdoc/rustc command families that do not always obey the same configuration surfaces,
- and cases where host triple and target triple are equal even though the *intended support lane* is not.

The official docs now make this concrete enough to stop hand-waving.
Cargo documents that `build.rustflags` and `RUSTFLAGS` apply to **all** compiler invocations when no `--target` is used, including build scripts and proc macros.
But when `--target` is used, those flags only apply to the target and not to host-built artifacts.
Cargo’s unstable docs then introduce `target-applies-to-host` and `[host]` config because the legacy behavior is confusing and because users need a way to configure host artifacts differently from target artifacts.
The Cargo internals docs go further and say that the host-artifact behavior is **counterintuitive**, yet kept for backwards compatibility, and that the same rule shape also applies to rustdoc flags.

This means the gap is no longer “Rust has no configuration knobs.”
The gap is that maintainers, tool authors, CI owners, and downstream integrators still lack one boring artifact that says:

- which config was *intended* for host artifacts,
- which config was *intended* for target artifacts,
- what actually applied on this build,
- whether changing `--target`, `build.target`, or nightly host-config changed behavior materially,
- and whether a failure or drift came from linker choice, target support posture, compile-time-deps/tool-only mode, or simply **config scope changing under your feet**.

The worthy crate is not another linker wrapper.
It is not another cross-compilation frontend.
It is not a full sandbox runner.
It is a **host/target scope contract and diagnosis kit** above Cargo’s existing config substrate.

# Sharper reading after the latest Cargo docs and ecosystem signals

Several current facts make this proposal much sharper than a vague “cross builds are confusing” complaint:

1. Cargo’s configuration docs now state explicit precedence and scope rules for `build.rustflags` / `RUSTFLAGS`, including the host-vs-target split around `--target`.
2. Cargo’s unstable docs now expose `target-applies-to-host` and `[host]`, which means the project has acknowledged this seam and is experimenting with a more explicit model rather than hiding it as implementation detail.
3. Cargo’s own internal docs say the host-artifact behavior is counterintuitive and that the same rule family also applies to rustdoc flags.
4. The user-wide build cache goal and sandboxed build-script goal both explicitly depend on host/target artifact sharing or separation, which proves this is not a trivia edge-case but real substrate.
5. Official issue trackers already show concrete maintainers being surprised by `RUSTFLAGS` behavior for build scripts and by rustdoc/build-script scope mismatches on docs.rs.

So the contribution that now looks worthy is:

- one contract for intended host/target config scope,
- one receipt for what was actually observed,
- one diagnosis for why scope drifted or split,
- and one diff for comparing mixed-build behavior across revisions, commands, or environments.

# Main judgment after the 2026-03-08 implementation pass

The proposal is now strong enough to treat as an **implementation-shaping** frontier, not just an idea sketch.

Three facts make the crate sharper than before:

- Cargo’s stable config docs already document the scope split for `build.rustflags` / `RUSTFLAGS` when `--target` is or is not present.
- Cargo’s unstable docs and tracking issues still show `target-applies-to-host` and `[host]` as open, baking surfaces rather than settled defaults.
- Cargo’s internal docs now make the surprising part explicit: for host-only artifacts when `--target` is provided, only `host.*.rustflags` is respected, and that behavior is described as **counterintuitive** but preserved for backwards compatibility; the same rule family also applies to rustdoc flags.

That combination means the missing value is not documentation alone.
It is the **portable receipt and diff layer** that freezes one mixed-build incident into something reviewable.

# What it provides

- `scope-policy.toml` — declares intended scope for `rustflags`, `rustdocflags`, linkers, runners, target selection, nightly-only host-config use, and manual-review zones.
- `scope-snapshot.manifest.json` — normalized view of relevant inputs: `build.*`, `target.*`, `host.*`, `--target`, `build.target`, env vars, and config provenance.
- `scope-observation.receipt.json` — observed mixed-build facts: host artifact kinds, target artifact kinds, relevant rustc/rustdoc invocations, which config families appeared to apply, and whether each fact came from config parsing, command capture, or imported logs.
- `scope-diagnosis.report.json` — structured verdicts such as `flags_leak_to_host`, `host_flags_missing`, `host_config_ignored`, `rustdoc_buildscript_scope_split`, `same_triple_scope_ambiguous`, `nightly_host_config_required`, and `manual_review_required`.
- `scope-diff.report.json` — compares two manifests/receipts and classifies `scope_equivalent`, `target_only_shift`, `host_only_shift`, `mixed_shift`, `nightly_dependency_added`, `same_triple_lane_changed`, and `manual_review_required`.
- `support-hints.md` — contributor/reviewer-facing explanation of what to change: add explicit `--target`, adopt `[host]`, split config, or stop relying on legacy implicit scope.
- `cargo scope-contract capture` — emit one portable mixed-build scope bundle.
- `cargo scope-contract doctor` — explain why the current Cargo/rustdoc behavior is surprising or fragile.
- `cargo scope-contract diff <old> <new>` — compare behavior across two revisions, commands, or CI environments.
- `*.scopebundle.zip` — portable artifact for CI failures, docs.rs bug reports, build-script/proc-macro support tickets, and release reviews.

# What the crate should provide other people

1. **One honest scope contract** instead of shell-history archaeology across Cargo config files, env vars, and CI steps.
2. **A reproducible bug-report bundle** for “why did my build script/proc macro/rustdoc invocation stop seeing this flag?”
3. **A migration helper** for moving from legacy implicit target-applies-to-host behavior toward explicit host/target config where needed.
4. **A shared vocabulary** for scope failures so tools can say more than “works locally, fails with `--target`.”
5. **A reusable library API** for IDEs, CI wrappers, docs builders, and release tooling that should not have to reverse-engineer Cargo scope rules ad hoc.

# Persona / who it’s for

- maintainers with build scripts, proc macros, unusual rustdoc needs, or cross-target support
- CI owners debugging why one command shape differs from another
- tool authors integrating Cargo in editors, wrappers, or docs builders
- support engineers triaging “flag present here, missing there” build reports
- downstream packagers working with same-triple-but-different-support environments

# Users & user stories

- **Workspace maintainer**: “Tell me whether `RUSTFLAGS` hit the build script only because I forgot to pass `--target`.”
- **Cross-build CI owner**: “Compare this stable build and this nightly host-config build and tell me what actually changed.”
- **Docs builder maintainer**: “Explain whether our rustdoc cfgs were seen by rustdoc only or also by the build script.”
- **Tool author**: “Reuse a stable schema for scope facts instead of encoding Cargo’s host/target rules in every wrapper.”
- **Reviewer**: “Tell me whether this patch merely reorganized config or silently changed what host tools compile with.”

# Prior art (and why it’s insufficient)

- Cargo’s configuration docs explain precedence and some scope behavior, but they do not emit a portable contract or receipt.
- Cargo’s unstable `host-config` / `target-applies-to-host` docs expose better substrate, but not a support-grade diff or diagnosis artifact.
- Cargo internals docs clarify behavior, including counterintuitive host-artifact rules, but that is not a maintainer-facing workflow.
- The user-wide cache and sandboxed build-script goals prove the host/target split matters, but they are not day-to-day diagnosis tools.
- Official Cargo/docs.rs issues show the pain is real, but issue threads are not reusable support bundles.
- Adjacent archive proposals already cover tool-only compile surfaces, linker lanes, and broader target support posture.

What remains missing is the **scope contract / observation / diagnosis / diff layer** above those ingredients.

# Design goals

1. **Scope-explicit** — always say whether a fact is about host artifacts, target artifacts, rustdoc, or mixed builds.
2. **Observed-vs-intended honest** — preserve the difference between declared policy and observed behavior.
3. **Unstable-aware without depending on it** — provide value on stable Cargo while clearly recording when nightly host-config features are in play.
4. **Diff-first** — scope changes should be reviewable across revisions and command shapes.
5. **Small diagnosis vocabulary** — enough to be useful, not so broad that every mismatch becomes bespoke.
6. **Adjacent-stack friendly** — compose with linker-lane, compile-time-deps, and toolchain-support bundles instead of absorbing them.

# MVP surface

- Minimal types: `ScopePolicy`, `ScopeSnapshotManifest`, `ScopeObservationReceipt`, `ScopeDiagnosisReport`, `ScopeDiffReport`, `ScopeBundle`
- Minimal functions:
  - `capture_scope_snapshot()`
  - `capture_scope_receipt()`
  - `diagnose_scope()`
  - `diff_scope_bundles()`
  - `generate_support_hints()`
- Feature flags:
  - `cargo-config`
  - `rustdoc`
  - `serde`
  - `markdown`

# Compatibility story

- Starts as a read-mostly crate above Cargo’s documented config surfaces.
- Must work on stable by capturing current behavior, even when the project is *not* using nightly `host-config`.
- Must record whether facts came from config files, env vars, command-line shape, rustdoc invocation style, or nightly-only config.
- Should stay useful even if `target-applies-to-host` changes default later, because teams will still need before/after drift artifacts.
- Must remain useful when host and target triples are equal but the intended support lane is still different.

# Conformance & fixtures

- one fixture where `RUSTFLAGS` / `build.rustflags` leak into build scripts because no explicit `--target` was used
- one fixture where adding `--target <host-triple>` changes host-tool behavior unexpectedly
- one nightly fixture using `target-applies-to-host = false` with explicit `[host]` config
- one rustdoc fixture where `build.rustdocflags` and build-script cfg behavior split in a docs-builder-like workflow
- one same-triple fixture where host and target look equal but config scope still deserves manual review
- goldens for `flags_leak_to_host`, `host_flags_missing`, `host_config_ignored`, `rustdoc_buildscript_scope_split`, `same_triple_scope_ambiguous`, `nightly_host_config_required`, and `same_triple_lane_changed`

Current implementation-shaping target:
- freeze `scope-observation.receipt.json` and `scope-diff.report.json` next to the existing manifest / diagnosis schemas
- prove the model on three small scenario bundles before inventing adapters or autofix logic

# Path to boring stability

- Freeze a small scope vocabulary before adding many adapters.
- Start with capture/doctor/diff rather than config mutation or auto-fixes.
- Treat nightly-only facts as explicit provenance rather than hidden complexity.
- Make `manual_review_required` a first-class success case, not a schema failure.
- Prefer portable scope bundles over raw command-log scraping.
- Keep **same-triple-but-different-lane** as a first-class diagnosis so host-equals-target string comparisons do not erase real support differences.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A crate and cargo subcommand that capture one mixed-build command’s intended and observed host/target scope, classify why behavior changed, and emit one portable `*.scopebundle.zip` another person can review without re-deriving Cargo’s scoping rules.

# De-risk plan

1. Start with read-only capture for stable Cargo config and command shapes.
2. Add nightly `host-config` parsing as explicit optional provenance.
3. Validate first on build-script/proc-macro fixtures and one rustdoc/docs-builder fixture.
4. Keep linker-lane and compile-time-deps integration as references, not required dependencies.

# Non-goals

- Not another linker wrapper or linker-lane chooser.
- Not a replacement for **P-0494 Cargo Compile-Time-Deps Workflow Kit**.
- Not a sandbox runner for build scripts or proc macros.
- Not a general Cargo config generator or formatter.
- Not a docs.rs clone or rustdoc wrapper platform.

# Architecture & API sketch

```rust
pub enum ScopeVerdict {
    Ok,
    FlagsLeakToHost,
    HostFlagsMissing,
    HostConfigIgnored,
    RustdocBuildscriptScopeSplit,
    SameTripleScopeAmbiguous,
    NightlyHostConfigRequired,
    ManualReviewRequired,
}

pub fn capture_scope_snapshot(root: &Path) -> Result<ScopeSnapshotManifest>;
pub fn capture_scope_receipt(observed: &ObservedBuild) -> Result<ScopeObservationReceipt>;
pub fn diagnose_scope(policy: &ScopePolicy, receipt: &ScopeObservationReceipt) -> ScopeDiagnosisReport;
pub fn diff_scope_bundles(old: &ScopeBundle, new: &ScopeBundle) -> ScopeDiffReport;
```

Bundle draft: `scope-policy.toml`, `scope-snapshot.manifest.json`, `scope-observation.receipt.json`, `scope-diagnosis.report.json`, `scope-diff.report.json`, `support-hints.md`, `notes.md`.

# Security / safety model

- Treat config files, env vars, rustc/rustdoc command lines, and wrapper logs as untrusted input.
- Support redaction of local paths, private cfg names, proprietary runners, and secret-bearing env vars.
- Preserve which facts are observed versus inferred.
- Never imply that equal host/target triples mean equal support or equal scope safety.

# Maintenance & governance plan

- Track Cargo config docs, unstable host-config behavior, and any default changes to `target-applies-to-host`.
- Keep the diagnosis vocabulary versioned and small.
- Maintain fixtures covering build-script, proc-macro, rustdoc, same-triple, and nightly-host-config scenarios.
- Publish guidance for when a scope diff should block release versus require manual review.

# Milestones

## 0.1
- scope snapshot capture
- observed mixed-build receipt
- diagnosis report
- portable scope bundle export

## 0.2
- scope diffs
- support hints
- nightly host-config provenance support

## 1.0
- stable schemas
- adapters for docs builders / editor wrappers
- curated fixture corpus for build-script, proc-macro, rustdoc, and same-triple cases

# Open questions

- What is the smallest durable vocabulary for host/target/rustdoc scope mismatches?
- How much raw command-line capture is worth preserving once the normalized receipt exists?
- Which integrations matter first: docs builders, editor wrappers, or release CI?

# Sources

- https://doc.rust-lang.org/cargo/reference/config.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://doc.rust-lang.org/cargo/CHANGELOG.html
- https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
- https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://github.com/rust-lang/cargo/issues/14046
- https://github.com/rust-lang/docs.rs/issues/1580
