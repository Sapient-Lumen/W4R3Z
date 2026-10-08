## Execution addendum (rev0449)
For questions about **what the archive's repeated support-envelope seam should actually ship once “target/platform support matters” is no longer enough**, read `design/support-envelope-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the broader **Compatibility Claims** band is unchanged;
- this revision says more explicitly what **Support Envelope** should become in theory and practice;
- **Support Envelope** should now be understood as **reference layer + report/pack command + observation/diff corpus**;
- **Acceptance Surface** and imported debugger tuple truth remain adjacent owners rather than substitutes;
- and future support-envelope work should prove subject truth, lane truth, provisioning/runtime-floor truth, observed evidence, drift, and bounded consumer handoffs before widening into support badges, cross-build wrappers, or matrix portals.

# Design: Support Envelope Kit (`cargo support`, `support-pack/v0`)

## Goal
Define a portable contract for declaring, checking, diffing, and reviewing Rust platform-support claims across **development hosts, source-build targets, released artifacts, docs surfaces, and runtime floors**.

This should **not** replace Cargo target selection, rustc target tiers, docs.rs, cross-compilation wrappers, or hosted compatibility labs.
It should make them compose better and make support claims reviewable.

## Why this is higher leverage than another cross-build tool
Rust already has serious target/provisioning tools.
What it still lacks is the boring but strategic layer that says:
- *what exactly is claimed*,
- *for which lane* (dev host, source build, release artifact, docs),
- *with what runtime floor*,
- *validated by what evidence strength*,
- *using which provisioning backend or std/sysroot story*,
- and *how that support changed*.

That is why this kit belongs closer to the steering shortlist than it did originally.
A strong support contract would feed Release Pipeline, Trust Signals, Ecosystem Atlas, Cross Toolchain, Sysroot Pack, Config Set, Device Lab, DocProof, and future crates.io/docs.rs presentation layers without trying to absorb them.

## References (signals)
- rustc platform support distinguishes plain targets from targets with host tools and includes platform notes like minimum OS / kernel / glibc floors for several mainstream targets.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- The target-tier policy makes host-tool support a distinct review surface and notes that tier guarantees vary materially.
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- docs.rs metadata already lets crate authors set `default-target`, `targets`, and `additional-targets`, while the docs.rs build docs say `#[cfg(docsrs)]` only applies to the final rustdoc invocation and not to dependencies or workspace members.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- docs.rs changed its default target list in October 2025, proving that docs target choice is an ecosystem-facing support signal, not just a rendering detail.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo’s `supported-targets` RFC is active and the Cargo 1.86 cycle explicitly reviewed the supported-platforms proposal.
  https://github.com/rust-lang/rfcs/pull/3759
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- cargo-deny already requires callers to name the targets that actually matter for policy checks.
  https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- the Rust 2024 edition guide plus Cargo’s resolver/MSRV docs show that source-build posture can vary by toolchain lane because resolver `3` is Rust-version aware and workspace members can influence chosen dependency versions.
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
  https://doc.rust-lang.org/cargo/reference/resolver.html
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- `build-std` and custom targets prove that source-build support can be real even when prebuilt std or official target support is absent.
  https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
  https://doc.rust-lang.org/rustc/targets/custom.html
- `cross`, `cargo-zigbuild`, and `cargo-xwin` show the ecosystem already has serious provisioning lanes, including glibc-version targeting caveats and offline SDK/CRT caching.
  https://github.com/cross-rs/cross
  https://github.com/rust-cross/cargo-zigbuild
  https://github.com/rust-cross/cargo-xwin
- Rust release notes continue to show target promotions/demotions, which means support drift is normal and reviewable diff artifacts matter.
  https://doc.rust-lang.org/beta/releases.html


## Why this now belongs in a compatibility-claims stack
Support Envelope Kit was already strong on its own, but current official Rust signals make it clearer that it is part of a larger missing substrate: **compatibility claims**.

Three things changed the posture:
- the safety-critical adoption writeup says teams need to map target tiers and upgrades to something they can responsibly bet on for a product lifetime, not just to upstream policy language;
- the debugging survey makes it explicit that “support” can vary by debugger family/version and operating system even when the code compiles and runs;
- release notes continue to promote or demote targets, which means support drift is not theoretical and needs diffable artifacts.

That means Support Envelope Kit should increasingly be framed as the platform-facing half of a broader compatibility-claims band, alongside Acceptance Surface Kit as the advanced-pattern / compiler-lane half.

Additional signals:
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Why this now needs its own pilot program
The archive already has a shared [`compatibility-claims` pilot](./compatibility-claims-pilot-program.md), but Support Envelope now deserves its own execution layer because the support half has become more operationally dense than the archive previously captured.

What changed:
- target tiers and mainstream target notes keep shifting, so support drift is not theoretical;
- docs.rs target defaults changed, which proves docs surfaces are part of the public support story;
- the 2025 State of Rust survey says online docs remain canonical while editor/agentic tooling rises, so hidden docs-target choices matter more;
- Cargo’s `cargo check` policy draws a real line between quick feedback and the stable guarantee attached to `cargo build`, which means some support lanes need explicit build/package/run evidence rather than a green `check`.

That means the strongest next move is not just “Compatibility Claims” in the abstract. It is a **Support Envelope pilot program** that proves a few high-value support lanes can be declared, observed, diffed, and consumed honestly before the archive widens the schema surface.

See also: [`design/support-envelope-pilot-program.md`](./support-envelope-pilot-program.md).

## Lane-map consequence
Support Envelope should now be read through [`design/compatibility-claims-lane-map.md`](./compatibility-claims-lane-map.md):
- **dev-host**, **source-build**, **release-artifact**, **docs-surface**, and **runtime-floor** claims should stay separate even when one project exports all of them;
- resolver/MSRV-sensitive source-build posture must not be flattened into one generic “builds from source” sentence; and
- docs.rs surfaces must not be allowed to silently stand in for ordinary local or CI build truth.

## Core artifact family

### 1) `support-envelope/v0`
The declared support contract for a crate, workspace, release candidate, or published release.

Required ideas:
- subject identity (`crate`, `workspace`, `release`, `binary artifact`, optional `variant`)
- support lanes:
  - `dev-host`
  - `source-build`
  - `release-artifact`
  - `docs-surface`
- target selector (`triple`, `cfg`, or named lane)
- support status (`official`, `supported`, `best-effort`, `experimental`, `docs-only`, `deprecated`, `unsupported`)
- required provisioning posture:
  - `native-rustup`
  - `cross`
  - `zigbuild`
  - `xwin`
  - `custom-sysroot`
  - `build-std`
  - `custom-target-json`
  - `other`
- host-tools posture where relevant:
  - `cargo`
  - `rustc`
  - optional `clippy`, `rustfmt`, `rustdoc`, `rust-analyzer-friendly`
- runtime-floor linkage (to one or more `runtime-floor-report/v0` entries)
- docs surface posture (import or align with `support-docs-profile/v0` where used):
  - docs.rs `default-target`
  - docs.rs `targets`
  - docs.rs `additional-targets`
  - whether docs targets are `representative`, `compatibility-probe`, or `convenience-only`
- validation policy target (`check`, `compile-only`, `test`, `build`, `package`, `run-smoke`, `field-validation`, `manual-review`)
- attachment policy for CI, release, and docs publication

Design rule: **the declared support contract must make lane identity explicit**.
A project must not be able to hide “compile-only via zigbuild on CI” behind the same entry as “we ship and support this binary for end users”.

### 2) `runtime-floor-report/v0`
Portable runtime-floor facts attached to one or more support entries.

Should record:
- target / lane / artifact identity
- minimum OS version when known
- minimum kernel version when known
- minimum libc / CRT / SDK / ABI baseline when known
- CPU-feature assumptions when known
- external runtime assumptions (system library family, container/image expectation, emulator/runner requirement, etc.)
- evidence source:
  - explicit maintainer declaration
  - rustc target notes
  - toolchain wrapper setting
  - symbol/version scan
  - package metadata
  - manual review
- confidence level (`declared`, `derived`, `observed`, `partial`, `unknown`)
- reason codes such as:
  - `glibc-floor-declared`
  - `glibc-floor-observed`
  - `sdk-floor-declared`
  - `kernel-floor-unknown`
  - `cpu-feature-assumed`
  - `custom-target-floor-opaque`

This is the missing answer to “what runtime environment does this target claim *actually* depend on?”

### 3) `support-observation-report/v0`
Machine-readable evidence for what support lanes were actually checked.

Should record:
- linked `support-envelope/v0`
- toolchain/provisioning backend used (`cargo`, `cross`, `zigbuild`, `xwin`, `build-std`, custom)
- whether the lane was native-host, cross-build, packaged artifact, docs build, or run/smoke execution
- command lanes used (`check`, `build`, `test`, `doc`, `package`, `run-smoke`, `integration`, `device-run`, `wine-run`, etc.)
- evidence strength per lane (`compiled`, `tested`, `packaged`, `smoked`, `field-observed`, `not-run`)
- observed mismatches between declared and observed support
- host-tool availability findings where relevant
- attached runtime-floor evidence (symbol scans, image/base metadata, SDK cache provenance, probe output)
- raw attachment pointers (CI exports, docs.rs metadata, release manifest snippets, `readelf` / `objdump` / `otool` / `dumpbin`, package manifests, runner logs)
- reason codes such as:
  - `host-tools-unavailable`
  - `cross-only-lane`
  - `docs-target-only`
  - `runtime-floor-unverified`
  - `glibc-floor-ambiguous`
  - `sdk-floor-ambiguous`
  - `target-feature-unchecked`
  - `package-produced`
  - `package-not-produced`
  - `run-lane-missing`
  - `ci-matrix-gap`
  - `custom-target-source-build-only`

This is the artifact that turns support claims from prose into evidence.
It should be governed by an explicit `support-evidence-policy/v0` in serious pilots, rather than inheriting evidence expectations from ad hoc CI habits.

### 4) `support-diff-report/v0`
A diff artifact for comparing two support contracts or a declared contract versus observed evidence.

Should support:
- baseline identity and comparison mode
- added / removed / narrowed / widened support lanes
- new or removed runtime floors
- higher/lower minimum OS/libc/SDK/kernel floors
- docs-surface changes
- validation-strength changes (`tested` → `compile-only`, `experimental` → `supported`, etc.)
- release-artifact changes (ship/no-ship)
- reason codes such as:
  - `lane-added`
  - `lane-removed`
  - `runtime-floor-raised`
  - `runtime-floor-lowered`
  - `docs-default-target-changed`
  - `release-artifact-removed`
  - `source-build-only-now`
  - `validation-strength-reduced`
  - `validation-strength-increased`
  - `target-tier-context-changed`
- `docs-profile-changed`
- verdicts (`pass`, `warn`, `fail`, `inconclusive`)

A good diff report reviews **support drift**, not just matrix churn.

### 5) `support-waiver/v0`
Optional artifact for time-bounded exceptions.

Use cases:
- temporary docs-target mismatch during migration
- release artifact delayed for one target
- known runtime-floor ambiguity awaiting investigation
- target broken only on nightly / beta / one provisioning backend
- target retained for source-build users while binaries are temporarily paused

Required ideas:
- scope
- reason
- owner
- expiry / review date
- linked observation/diff evidence

### 6) `support-pack/v0`
Bundle format containing:
- `support-envelope/v0`
- zero or more `runtime-floor-report/v0`
- one or more `support-observation-report/v0`
- optional `support-diff-report/v0`
- optional `support-waiver/v0`
- raw attachments and rendered summaries

This is the unit that should travel through CI, docs hosting, release review, crates.io/discoverability adapters, policy checks, and later archaeology.

## Reference UX
- `cargo support init`
- `cargo support check`
- `cargo support diff`
- `cargo support docsrs`
- `cargo support runtime`
- `cargo support pack`

`cargo support` should begin as an **adapter / explainer / packer**, not as a universal compatibility oracle.

## Default policy
- **Separate dev-host, source-build, release-artifact, and docs lanes.**
- **Record runtime floors explicitly** instead of burying them in issues or release notes.
- **Preserve raw source truth** from manifests, docs.rs metadata, CI exports, package metadata, and probe outputs.
- **Distinguish declared support from observed support.**
- **Allow partial evidence honestly** (`compile-only`, `packaged`, `smoke-run`, etc.) rather than flattening them into one badge.
- **Treat target triples as necessary but insufficient.**

## What the kit should provide to others
- **Cross Toolchain Kit / Sysroot Pack Kit:** consume explicit support contracts after provisioning toolchains or std/sysroot variants.
- **Build Cache Kit / Semantic Context Kit:** attach lane identity so caches and semantic outputs are not misread as universal support.
- **Config Set Kit:** map bounded CI matrices back to the official support contract.
- **DocProof Kit:** attach docs-target truth and landing-page assumptions to support claims.
- **Release Pipeline Kit / Signed Binaries Kit / SBOM Evidence Kit:** attach per-artifact support facts and runtime floors to shipped deliverables.
- **Trust Signals Kit / Policy Kit / Ecosystem Atlas Kit:** consume support evidence and support drift without scraping READMEs.
- **Lifecycle Ledger Kit:** record deprecations, narrowed support windows, and successor lanes explicitly.
- **Device Lab Kit / Wasm Component Kit / Client App Surface Kit:** attach domain-specific validation evidence to a shared platform-support substrate.

## Overlap boundaries
- **Not Cross Toolchain Kit:** that kit provisions toolchains/sysroots/runners; this kit records claims and evidence about supported surfaces.
- **Not Sysroot Pack Kit / build-std stabilization:** those own std/sysroot production; this kit records when such lanes are part of the support contract.
- **Not DocProof Kit:** that kit verifies learning/documentation surfaces; this kit records how docs targets relate to support claims.
- **Not rustc target tiers:** target tiers are Rust-project guarantees; this kit is for crate/workspace/release support promises layered on top.
- **Not a hosted badge service:** the value is the portable artifact family and review workflow.

## Hard problems (explicitly scoped)
1. **Support is multi-plane, not one list**
   - dev host, source build, release artifact, docs surface, and runtime floor are distinct.

2. **Runtime floors are messy and sometimes partially knowable**
   - glibc/SDK/kernel/min-OS/CPU-feature assumptions vary by target and provisioning backend.
   - v0 should allow partial evidence and explicit uncertainty.

3. **Validation strength is uneven**
   - compile-only, package-only, docs-only, smoke-run, and field validation are not the same thing.

4. **Upstream Cargo may absorb part of the declaration story**
   - `supported-targets` may eventually cover manifest declaration.
   - this kit should therefore focus on reusable artifacts, evidence, diffs, and composition.

5. **Provisioning and support interact but are not identical**
   - “can be built with zigbuild/xwin/build-std/custom-target-json” is not identical to “officially supported for end users”.

6. **Rust’s own platform map changes over time**
   - promotions, demotions, and docs.rs default-target shifts make diff/report lanes strategically important.

## Minimal adoption path
1. Publish schemas for `support-envelope/v0`, `runtime-floor-report/v0`, and `support-observation-report/v0`.
2. Ship `cargo support docsrs` and `cargo support check` first.
3. Ingest docs.rs metadata, explicit target declarations, CI target matrices, and release-artifact manifests.
4. Add adapters for `cross`, `cargo-zigbuild`, `cargo-xwin`, `build-std`, and simple runtime-floor probes.
5. Add diff/report workflows and waiver support.
6. Pilot crates.io/docs.rs/release-note rendering and ecosystem-atlas consumption later, only after artifact quality is good enough.

## What a worthy contribution would look like in practice
A worthy contribution here would probably be:
- a schema crate + validator,
- a Cargo subcommand that produces support packs from real projects,
- adapters for docs.rs / CI / release artifacts / provisioning tools,
- enough runtime-floor capture to make glibc/min-OS/SDK claims reviewable,
- and at least three pilots from materially different domains (CLI app, library with docs.rs customization, cross-built binary project, embedded/custom-target project).

That is “epic” in the good sense: boring infrastructure that turns one of the ecosystem’s fuzzier trust surfaces into something projects can actually review, publish, diff, and consume.
