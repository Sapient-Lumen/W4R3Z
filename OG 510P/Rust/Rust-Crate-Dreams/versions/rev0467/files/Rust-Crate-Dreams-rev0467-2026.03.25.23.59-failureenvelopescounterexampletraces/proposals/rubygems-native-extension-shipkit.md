---
id: P-0501
title: RubyGems Native Extension ShipKit — platform coverage, resolver routes, and extension residency for Rust-backed gems
status: idea
domains: [ruby, rubygems, ffi, packaging, release, interoperability, ci, tooling]
last_reviewed: 2026-03-18
evidence:
  - https://bundler.io/man/bundle-gem.1.html
  - https://guides.rubygems.org/specification-reference/
  - https://guides.rubygems.org/gems-with-extensions/
  - https://bundler.io/man/gemfile.5.html
  - https://bundler.io/man/bundle-cache.1.html
  - https://guides.rubygems.org/trusted-publishing/
  - https://guides.rubygems.org/command-reference/
  - https://github.com/rubygems/release-gem
  - https://github.com/oxidize-rb/rb-sys
  - https://docs.rs/magnus
  - https://oxidize-rb.org/docs/deployment/
---

# Problem

Rust already has real substrate for Ruby native extensions.

- Bundler now officially scaffolds Rust extensions with `bundle gem --ext=rust`, which means the substrate is no longer hypothetical or private folklore.
- RubyGems already has a real extension-install story plus platform-gem vocabulary through `spec.platform`, extension build hooks, and binary-gem naming rules.
- `rb-sys` exists specifically to make building Ruby native extensions in Rust easier and explicitly interoperates with existing Ruby native-extension toolchains.
- `magnus` gives a higher-level Rust authoring layer for Ruby extensions.
- oxidize.rb now documents the real “fat gem” distribution story for Rust-backed gems, which makes binary/source-build posture a first-class support seam.

But ordinary maintainers still do too much release work by folklore:

- deciding whether a gem is **source-build-at-install-time**, **platform-specific binary gem**, or a hybrid is still spread across README prose, CI YAML, and one-off scripts,
- Ruby implementation support (MRI, JRuby, TruffleRuby, “MRI only”, “MRI + source build only”) is often implied rather than reviewable,
- Bundler’s `platforms:` vocabulary is about Ruby implementations while `bundle lock --add-platform` is about OS/arch lockfile targets, so the actual resolver route is easy to overclaim,
- the final relationship between gemspec platform, packaged shared-library filenames, require stubs, copied extension files under `lib/`, and shipped artifacts is still easy to get subtly wrong,
- cross-build pipelines can produce many binary gems without one compact support artifact saying what was actually shipped,
- trusted publishing now makes release identity and CI publication posture more explicit, but Rust-backed gems still rarely record that as part of the release contract,
- and RubyGems’ own `gem rebuild` command makes release reproducibility relevant, but Rust-backed gems still rarely emit a clean build/rebuild receipt.

The sharper question is no longer “can Rust talk to Ruby?”

The sharper question is: **what gem(s) did we ship, for which Ruby implementations and platforms, with what build posture, and how honest is the support contract?**

The missing crate is not another Ruby binding layer.

The missing crate is a **shipkit** that turns Rust-backed Ruby gem releases into a boring, reviewable package contract: platform coverage, resolver routes, extension residency, build/load receipts, publish identity, and rebuild evidence.

# What it provides

- `rubygem-shipkit.toml` — declares release posture: source-built gem, binary gems, hybrid strategy, supported Ruby implementations, target platforms, Bundler/platform-lock expectations, and support caveats.
- `platform-coverage.report.json` — every produced `.gem` artifact with gem platform, Ruby version family, target triple, libc notes when relevant, checksum, and whether support is binary-gem, source-build, hybrid, or manual-review.
- `resolver-route.report.json` — explicit support posture for MRI / JRuby / TruffleRuby plus Bundler route facts: `platforms:` gating, lockfile target additions, `force_ruby_platform`, and where resolution still depends on source-build fallback.
- `extension-residency.report.json` — records gem require paths, extension filenames, packaged load locations, copied files under `lib/`, and whether the gem relies on install-time compilation or precompiled artifacts.
- `gem-build.receipt.json` — captures Ruby, RubyGems, Bundler, Cargo, `rb-sys`, `magnus`, and toolchain versions used to build the release.
- `publish-identity.receipt.json` — records whether publishing uses trusted publishing, traditional API keys, or manual local release posture, plus any review caveats.
- `rebuild.parity.json` — records whether a gem rebuild reproduces byte-identical or semantically equivalent artifacts, plus any drift explanations.
- `support-risk.report.json` — rolls platform coverage, Ruby-implementation support, source-build posture, and load contract into one downstream support verdict.
- `cargo rubygem-ship snapshot` — capture one release contract plus produced gem artifacts.
- `cargo rubygem-ship doctor` — explain whether gemspec platform, artifacts, build posture, and support claims agree.
- `cargo rubygem-ship diff <old> <new>` — compare support promises across gem releases.
- `*.rubygembundle.zip` — portable release-review and support artifact.

# What the crate should provide other people

1. **A boring answer to “what Ruby gem release did we actually ship?”** instead of CI archaeology.
2. **An explicit platform-coverage contract** that says which binary gems exist and where source-build fallback still applies.
3. **A resolver-route report** that says whether Bundler/RubyGems will actually take the route the README seems to imply.
4. **An extension-residency receipt** that proves gemspec platform, packaged extension files, copied `lib/` artifacts, and runtime load expectations agree.
5. **A publish-identity and rebuild evidence artifact** that helps maintainers, package reviewers, and downstream users trust what they installed.

# Persona / who it’s for

- maintainers publishing Rust-backed gems to RubyGems
- teams exposing Rust libraries into Ruby and Rails ecosystems
- release engineers producing multi-platform native gems
- support engineers diagnosing install/load failures
- downstream Ruby users who need an honest support statement before adopting a native gem

# Users & user stories

- **Gem maintainer**: “Show me whether our gemspec platform, built artifacts, and README support statement actually agree.”
- **Release engineer**: “Give me one bundle that joins Cargo output, RubyGems metadata, cross-build results, and Ruby implementation support.”
- **Support engineer**: “Tell me whether this failure is because we only shipped MRI gems, because source-build fallback is required, or because the packaged extension path/name is wrong.”
- **Downstream user**: “Show me whether this gem is a binary gem for my platform, an install-time build, or unsupported on my Ruby implementation.”

# Prior art (and why it’s insufficient)

- RubyGems already documents gems with extensions and platform-specific gems.
- RubyGems also documents `gem build`, `gem push`, and `gem rebuild`, which means build and rebuild facts are already part of the ecosystem’s official release story.
- Bundler already documents platform-lock and Ruby-implementation-oriented compatibility controls.
- RubyGems already documents trusted publishing, which means publish identity is now explicit enough to join the package contract.
- `rb-sys` and `magnus` already provide serious Rust-side authoring substrate.
- `rake-compiler`, `rake-compiler-dock`, and `cross-gem-action` already provide important build and cross-compilation substrate.
- Real projects also show both adoption and pain: some are publishing Rust-backed Ruby bindings, while others explicitly avoid repository publication because of operational overhead.

What remains missing is the **maintainer-facing coordination layer** that answers: “which gem platforms exist, which Ruby implementations are actually supported, does this release rely on source build or binary gems, and can we explain or reproduce what we shipped?”

# Design goals

1. **Release-contract first** — the core value is the shipping promise, not another extension authoring API.
2. **Platform-aware** — gem platforms and binary/source-build posture must be first-class facts.
3. **Resolver-aware** — Bundler Ruby-engine/platform controls, lockfile platform targets, and source-build fallback must stay visibly distinct.
4. **Residency-aware** — require stubs, copied extension files, packaged shared libraries, and runtime load expectations must remain checkable.
5. **Reviewable** — produce artifacts humans can inspect before publication.

# MVP surface

- Minimal types: `RubygemShipkitContract`, `PlatformCoverageReport`, `ResolverRouteReport`, `ExtensionResidencyReport`, `GemBuildReceipt`, `RebuildParityReport`, `SupportRiskReport`, `RubygemBundle`
- Minimal functions:
  - `capture_rubygem_shipkit_contract()`
  - `evaluate_platform_coverage()`
  - `evaluate_resolver_route()`
  - `capture_extension_residency_report()`
  - `capture_gem_build_receipt()`
  - `diff_rubygem_shipkits()`
- Feature flags:
  - `rubygems`
  - `cargo`
  - `serde`
  - `cross-build`
  - `rebuild-check`

# Compatibility story

- Must remain useful for classic install-time native extensions that compile during `gem install`.
- Must remain useful for binary gems whose platform is set explicitly in the gemspec.
- Must distinguish **Ruby implementation support**, **gem platform**, and **CPU/OS artifact target**, because those can drift independently.
- Should tolerate pure-Ruby or FFI fallbacks when projects choose mixed strategies, but must keep those support classes explicit.
- Must not treat “the extension compiled once in CI” as evidence that downstream installation is boring.

# Conformance & fixtures

- one clean MRI binary-gem matrix fixture
- one source-build-only fixture with no binary gems
- one hybrid fixture where some platforms use binary gems and others fall back to source build
- one fixture where Bundler platform/engine claims exceed the actual lockfile/platform route evidence
- one fixture where the shared library is built but copied/required under the wrong path or old name
- one fixture where publish identity or release recipe still requires explicit review
- goldens for `platform_contract_ok`, `fat_gem_gap`, `resolver_route_review_required`, `ruby_engine_claim_exceeds_route`, `extension_residency_mismatch`, `publish_identity_review_required`, and `manual_review_required`

# Path to boring stability

- Freeze the contract and verdict vocabulary before adding publication automation.
- Start with read-only inspection of gemspecs, built artifacts, lockfiles, and build receipts.
- Keep Ruby-implementation support conservative and explicit.
- Prefer package-review and support artifacts over becoming another build orchestrator.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 5/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust-backed gem project, capture its release posture, normalize the produced gem/platform matrix, classify Ruby-implementation support, record build/load receipts, and emit one support bundle that names any packaging or support gaps.

# De-risk plan

1. Start with one conventional MRI-only Rust gem and one intentionally broken support-claim fixture.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate on RubyGems publication and install-time build workflows before trying to support every alternate distribution channel.
4. Avoid becoming another binding generator, gem publisher, or generic Ruby packaging framework.

# Non-goals

- Not another Rust↔Ruby binding generator.
- Not a replacement for RubyGems, Bundler, or rake-compiler.
- Not a promise that JRuby and TruffleRuby support can be inferred automatically from MRI success.
- Not a generic Ruby package manager or Rails deployment platform.

# Architecture & API sketch

```rust
pub enum SupportRiskClass {
    PlatformContractOk,
    FatGemGap,
    ResolverRouteReviewRequired,
    RubyEngineClaimExceedsRoute,
    ExtensionResidencyMismatch,
    PublishIdentityReviewRequired,
    ManualReviewRequired,
}

pub fn capture_rubygem_shipkit_contract(root: &Path) -> Result<RubygemShipkitContract>;
pub fn evaluate_platform_coverage(root: &Path, contract: &RubygemShipkitContract) -> Result<PlatformCoverageReport>;
pub fn evaluate_resolver_route(root: &Path, contract: &RubygemShipkitContract) -> Result<ResolverRouteReport>;
pub fn capture_extension_residency_report(root: &Path) -> Result<ExtensionResidencyReport>;
pub fn capture_gem_build_receipt(root: &Path) -> Result<GemBuildReceipt>;
```

Bundle draft: `rubygem-shipkit.toml`, `gem-platform-matrix.json`, `ruby-vm-support.report.json`, `extension-load.receipt.json`, `gem-build.receipt.json`, `publish-identity.receipt.json`, `rebuild.parity.json`, `support-risk.report.json`, `notes.md`.

# Security / safety model

- Treat gemspecs, built gems, build logs, and packaged native artifacts as untrusted input.
- Support redaction of local paths, signing credentials, and internal CI coordinates.
- Keep Ruby-implementation support posture separate from claims about code safety or supply-chain trust.
- Never imply that “binary gem exists” means the gem is appropriate for every Ruby implementation or deployment model.

# Maintenance & governance plan

- Track RubyGems changes to platform matching, build/rebuild behavior, and metadata that affect native gems.
- Track `rb-sys`, `magnus`, and cross-build tooling only as substrate, not as the main contract.
- Keep Ruby-implementation vocabulary intentionally small and explanation-heavy.
- Maintain fixtures for binary-gem coverage gaps, source-build-only fallback, and implementation-support mismatches.

# Milestones

## 0.1
- contract file
- gem/platform matrix inspection
- build receipt
- initial support verdicts

## 0.2
- extension-load receipt
- rebuild parity report
- CI policy checks

## 0.3
- richer redaction
- support diffing across releases
- optional lightweight install smoke-check hooks

# Open questions

- What is the smallest useful vocabulary for Ruby implementation support without overfitting today’s MRI/JRuby/TruffleRuby details?
- Which rebuild facts matter most for reviewers: RubyGems version, Cargo.lock, binary-gem checksums, or all three?
- How much extension-load checking is useful before the crate drifts into a full runtime harness?
- How should hybrid “binary gems for some platforms, source build for others” strategies be represented so they stay honest?

# Sources

- Bundler `bundle gem` — https://bundler.io/man/bundle-gem.1.html
- Bundler Gemfile reference — https://bundler.io/man/gemfile.5.html
- Bundler bundle-cache reference — https://bundler.io/man/bundle-cache.1.html
- RubyGems specification reference — https://guides.rubygems.org/specification-reference/
- RubyGems guide: gems with extensions — https://guides.rubygems.org/gems-with-extensions/
- RubyGems trusted publishing — https://guides.rubygems.org/trusted-publishing/
- RubyGems command reference (`gem rebuild`) — https://guides.rubygems.org/command-reference/
- release-gem GitHub Action — https://github.com/rubygems/release-gem
- `rb-sys` — https://github.com/oxidize-rb/rb-sys
- `magnus` — https://docs.rs/magnus
- oxidize.rb deployment guide — https://oxidize-rb.org/docs/deployment/
