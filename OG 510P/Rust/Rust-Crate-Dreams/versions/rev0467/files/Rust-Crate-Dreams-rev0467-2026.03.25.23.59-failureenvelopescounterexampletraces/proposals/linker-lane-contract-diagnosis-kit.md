---
id: P-0504
title: Linker Lane Contract & Diagnosis Kit — per-target linker receipts, lane-switch diffs, and cross-link support bundles
status: idea
domains: [cargo, linking, cross-compilation, build-performance, ci, release, toolchains]
last_reviewed: 2026-03-08
evidence:
  - https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/rustc/codegen-options/index.html
  - https://rust-lang.github.io/rustup/cross-compilation.html
  - https://github.com/rust-cross/cargo-zigbuild
  - https://github.com/rust-cross/cargo-xwin
  - https://github.com/cross-rs/cross
  - https://docs.rs/xwin/latest/xwin/
---

# Problem

Rust’s linking layer is becoming both **more important** and **more complicated**.

The 2025 Rust compiler performance survey explicitly says the **linking phase is too slow** and notes that Rust is trying to switch common targets to faster linkers by default. At the same time, the official docs make it clear that the user-facing linker story is now spread across several real configuration surfaces:

- Cargo target-specific `linker` and `rustflags` config,
- `rustc` codegen options like `-C linker`, `-C link-self-contained`, and `-C linker-features=+lld`,
- rustup target installation that still often requires **extra non-Rust tools**, especially a linker,
- and an ecosystem of practical lane-specific tools such as `cargo-zigbuild`, `cargo-xwin`, `xwin`, and `cross`.

That means Rust no longer lacks *ways to link*.

What it still lacks is a **boring, reviewable, portable artifact** that says:

- which linker lane was actually used,
- what host/target assumptions that lane depended on,
- whether a switch from one lane to another is safe or risky,
- whether a failure came from a missing linker, missing SDK/sysroot, flag-scope mistake, or path/search mismatch,
- and whether a project’s release/support story implicitly depends on one linker lane without admitting it.

The missing crate is **not** another linker.
It is **not** another cross-compilation wrapper.
It is **not** a benchmark lab pretending to solve compiler performance.

The missing crate is a **linker lane contract and diagnosis kit** above today’s substrate and above existing lane-specific tools.

# Sharper reading after the latest Rust docs and ecosystem signals

Several current facts make this proposal much sharper than a vague “linking is hard” complaint:

1. The Rust project now treats linker performance as a visible ecosystem problem, not as obscure tooling trivia.
2. Cargo documents target-specific linker configuration and the precedence of target-specific `rustflags` versus global `RUSTFLAGS`.
3. Cargo’s docs also explicitly warn that without `--target`, `build.rustflags` apply to **host builds too**, including build scripts and proc macros, which means linker-related flags and support bugs can easily leak into the wrong compilation lane.
4. `rustc` now documents meaningful linker-lane substrate directly: self-contained linker control and explicit `lld` lane selection.
5. rustup still documents that adding a Rust target is often not enough because cross-compilation typically still needs a linker or SDK outside Rust itself.
6. The ecosystem already has credible lane-specific helpers (`cargo-zigbuild`, `cargo-xwin`, `xwin`, `cross`), which is exactly why the missing value has moved upward into **comparison, diagnosis, and support receipts**.

So the worthy contribution here is no longer “invent a new way to call a linker.”

It is:

- one contract for intended linker lanes,
- one receipt for what actually happened,
- one diagnosis for why it failed or drifted,
- and one diff for switching lanes deliberately.

# What it provides

- `linker-policy.toml` — declares preferred, allowed, and disallowed linker lanes per target/profile (`system-default`, `self-contained-lld`, `explicit-lld`, `zig-driver`, `xwin-sdk`, `containerized-cross`, `custom-wrapper`, `manual-review-required`).
- `linker-lane.manifest.json` — normalized view of one target’s configured linker lane: Cargo config sources, env overrides, `rustflags`, `link-self-contained` posture, linker feature toggles, host/target split, and known external prerequisites.
- `link-attempt.receipt.json` — one observed linking attempt with command provenance, selected driver/binary, SDK/sysroot hints, search-path facts, and normalized verdict.
- `link-diagnosis.report.json` — structured diagnosis categories such as `linker_not_found`, `sdk_missing`, `sysroot_missing`, `driver_flag_scope_mismatch`, `host_flag_leakage`, `search_path_mismatch`, `crt_or_runtime_mismatch`, `lane_unsupported_here`, and `manual_review_required`.
- `lane-switch.diff.json` — compares two lanes or two revisions and classifies `same_semantics`, `perf_only_shift`, `support_surface_changed`, `external_dependency_added`, `fallback_removed`, `manual_review_required`.
- `support-risk.report.json` — summarizes whether the project’s release or CI story depends on undocumented external tools, specific SDK versions, or one-off host assumptions.
- `cargo linker-lane capture` — emit one linker lane bundle for a target/profile.
- `cargo linker-lane doctor` — explain why the current lane is failing or fragile.
- `cargo linker-lane diff <old> <new>` — compare lane receipts across revisions, targets, or CI environments.
- `*.linkbundle.zip` — portable support artifact for release reviews, CI failures, cross-compilation bug reports, and “should we switch linker lanes?” decisions.

# What the crate should provide other people

1. **One honest linker support contract** instead of scattered Cargo config, CI env vars, wrapper scripts, and tribal knowledge.
2. **A reviewable diagnosis artifact** for linker failures that is sharper than “link step failed”.
3. **A safe lane-switch diff** for teams experimenting with `lld`, self-contained linking, Zig-based linking, or Windows SDK packaging.
4. **A bridge layer** across rustup, Cargo config, `rustc` flags, and lane-specific tools like `cargo-zigbuild`, `cargo-xwin`, and `cross`.
5. **A reusable library API** for release tools, CI helpers, and support tooling that should not scrape raw linker commands or shell logs.

# Persona / who it’s for

- release engineers and CI owners
- maintainers of cross-platform CLI/desktop/server crates
- embedded and systems teams with custom linkers or target specs
- tool authors building release or cross-compilation workflows
- support engineers debugging “target added, but link still fails” reports

# Users & user stories

- **Release engineer**: “Tell me whether switching this Linux target to the `lld` lane changed performance only, or also changed our external-tool assumptions.”
- **Cross-platform maintainer**: “Capture one bundle showing why macOS/Windows/Linux cross-linking succeeds in CI but fails on contributor machines.”
- **Contributor**: “Explain whether I am missing a linker, a sysroot/SDK, or just have the wrong target-specific config.”
- **Security/repro reviewer**: “Show whether this build relied on the system linker, a self-contained linker, a wrapped toolchain, or a containerized lane.”
- **Tool author**: “Reuse a stable diagnosis schema instead of inventing yet another parser for Cargo config, rustflags, and wrapper-specific logs.”

# Prior art (and why it’s insufficient)

- Cargo already documents target-specific linker and `rustflags` configuration, but it does not turn that into one support-grade contract or diff.
- `rustc` already documents `link-self-contained`, `linker`, and `linker-features`, but these are primitive knobs, not a diagnosis/report layer.
- rustup documents that cross-compilation often needs extra tools, particularly a linker, but rustup is not a cross-link doctor.
- `cargo-zigbuild` provides a strong Zig-based linker lane, especially for easier cross-compilation and glibc targeting, but it is intentionally one lane rather than a general lane contract.
- `cargo-xwin` and `xwin` provide a strong Windows MSVC lane from non-Windows hosts, but they are specialized tooling and do not provide a generic lane-diff/support-risk artifact.
- `cross` provides containerized cross-compilation/testing lanes, but it is not a linker-lane explanation or support-contract crate.

What remains missing is the **lane contract / receipt / diagnosis / diff layer** above these tools.

# Design goals

1. **Lane-explicit** — always name which linker lane is being discussed.
2. **Diagnosis-first** — failures should classify into a small, reviewable vocabulary.
3. **Host/target honest** — separate host-tooling facts from target-linking facts.
4. **Diff-friendly** — linker-lane changes must be reviewable across time.
5. **Adapter-based** — integrate with existing tools rather than competing with them.
6. **Performance-aware, not benchmark-first** — timing can be attached, but the core value is the support artifact.

# MVP surface

- Minimal types: `LinkerPolicy`, `LinkerLaneManifest`, `LinkAttemptReceipt`, `LinkDiagnosisReport`, `LaneSwitchDiff`, `SupportRiskReport`, `LinkBundle`
- Minimal functions:
  - `capture_lane_manifest()`
  - `capture_attempt_receipt()`
  - `diagnose_attempt()`
  - `diff_lanes()`
  - `summarize_support_risk()`
- Feature flags:
  - `cargo-config`
  - `rustflags`
  - `serde`
  - `timings`
  - `markdown`

# Compatibility story

- Starts as a read-mostly crate above existing Cargo/rustc/linker tooling.
- Must preserve whether a fact came from Cargo config, environment, wrapper command, `rustc` flags, or external tool metadata.
- Should work with ordinary Cargo, `cargo-zigbuild`, `cargo-xwin`, and `cross` through adapters or captured receipts.
- Must remain honest when it cannot see the real linker binary behind a wrapper.
- Should avoid assuming one “best” linker lane across targets.

# Conformance & fixtures

- one Linux fixture showing `system-default` versus `self-contained-lld` lane comparison
- one fixture where `build.rustflags` leak into host tools because `--target` scoping was not explicit
- one Windows-from-Linux fixture using an `xwin` / `cargo-xwin` style lane
- one Zig lane fixture with glibc-version suffix expectations
- one containerized `cross`-style lane fixture where the build works only inside the container environment
- goldens for `linker_not_found`, `sdk_missing`, `sysroot_missing`, `host_flag_leakage`, `support_surface_changed`, and `manual_review_required`

# Path to boring stability

- Freeze the lane vocabulary before expanding adapter count.
- Keep diagnosis categories small and reviewer-friendly.
- Treat wrapper-specific details as provenance, not as the schema’s primary truth.
- Prefer one portable bundle over a giant live benchmarking system.
- Make `manual_review_required` a normal output, not a failure of the crate.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A crate and cargo subcommand that capture one target’s configured/observed linker lane, classify why a link failed or drifted, and emit one portable `*.linkbundle.zip` another person can review without recreating the whole machine.

# De-risk plan

1. Start with read-only lane capture and diagnosis for a few common lanes.
2. Keep performance timing optional and secondary.
3. Validate on one Linux target, one Windows cross lane, and one wrapper/container lane.
4. Treat unresolved wrapper opacity as an explicit caveat rather than a reason to overfit the design.

# Non-goals

- Not a new linker implementation.
- Not a replacement for `cross`, `cargo-zigbuild`, `cargo-xwin`, or `xwin`.
- Not a universal cross-compilation orchestrator.
- Not a benchmark suite pretending to solve link-time performance by itself.
- Not a guarantee that all target-specific linker behavior can be inferred perfectly.

# Architecture & API sketch

```rust
pub enum LinkerLaneKind {
    SystemDefault,
    SelfContainedLld,
    ExplicitLld,
    ZigDriver,
    XwinSdk,
    ContainerizedCross,
    CustomWrapper,
    ManualReviewRequired,
}

pub fn capture_lane_manifest(root: &Path, target: &str) -> Result<LinkerLaneManifest>;
pub fn capture_attempt_receipt(invocation: &ObservedInvocation) -> Result<LinkAttemptReceipt>;
pub fn diagnose_attempt(receipt: &LinkAttemptReceipt, policy: &LinkerPolicy) -> LinkDiagnosisReport;
pub fn diff_lanes(old: &LinkBundle, new: &LinkBundle) -> LaneSwitchDiff;
```

Bundle draft: `linker-policy.toml`, `linker-lane.manifest.json`, `link-attempt.receipt.json`, `link-diagnosis.report.json`, `lane-switch.diff.json`, `support-risk.report.json`, `notes.md`.

# Security / safety model

- Treat wrapper commands, env vars, and shell output as untrusted input.
- Support redaction of local paths, internal SDK roots, and proprietary wrapper names.
- Preserve which facts are observed versus inferred.
- Never silently equate “build succeeded once” with “support contract is stable.”

# Maintenance & governance plan

- Track Rust/Cargo linker-lane substrate changes, especially around default `lld` behavior and self-contained linking.
- Version the lane and diagnosis vocabularies separately from adapters.
- Maintain fixtures that cover both performance-motivated lane switching and cross-compilation support failures.
- Publish guidance for when a lane diff should block release versus require manual review.

# Milestones

## 0.1
- lane manifest capture
- one-attempt receipt
- diagnosis report
- portable link bundle export

## 0.2
- lane-switch diffs
- support-risk summaries
- adapter receipts for `cargo-zigbuild`, `cargo-xwin`, and `cross`

## 1.0
- stable bundle schema
- curated fixture corpus across major lane families
- optional timing attachments and CI adapters

# Adjacent archive relationship

- **P-0484 Toolchain & Target Support Contract Kit** should answer: *what toolchains, components, and targets do we support?*
- **P-0058 native-deps-kit** should answer: *how do native dependencies and probes behave?*
- **P-0497 CPU Baseline & Runtime Dispatch Contract Kit** should answer: *what hardware/runtime-dispatch promises do we make?*
- **P-0504** should answer: *which linker lane did we actually rely on, how did it drift, and what changed when we switched?*

If a future pass tries to merge all of that into one “cross-platform build doctor”, that is probably a repo regression.

# Open questions

- What is the smallest durable linker-lane vocabulary that still distinguishes real operational choices?
- How much wrapper-specific data belongs in the core receipt versus optional adapter attachments?
- Should lane-switch diffs classify performance-only changes separately from support-surface changes in the MVP, or later?
- Which early targets best stress the design: Linux GNU, Windows MSVC-from-Linux, Android, or Apple cross-lanes?

# Sources

- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo configuration (`target.<triple>.linker`, `rustflags`): https://doc.rust-lang.org/cargo/reference/config.html
- `rustc` codegen options (`link-self-contained`, `linker`, `linker-features`): https://doc.rust-lang.org/rustc/codegen-options/index.html
- rustup cross-compilation docs: https://rust-lang.github.io/rustup/cross-compilation.html
- `cargo-zigbuild`: https://github.com/rust-cross/cargo-zigbuild
- `cargo-xwin`: https://github.com/rust-cross/cargo-xwin
- `xwin`: https://docs.rs/xwin/latest/xwin/
- `cross`: https://github.com/cross-rs/cross
