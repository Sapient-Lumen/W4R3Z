---
id: P-0502
title: Hex Native NIF ShipKit — checksum residency, NIF-version windows, and fallback-trigger receipts for Rust-backed BEAM packages
status: idea
domains: [elixir, erlang, beam, hex, nif, packaging, release, ci, interoperability, tooling]
last_reviewed: 2026-03-18
evidence:
  - https://docs.rs/crate/rustler/latest
  - https://hexdocs.pm/rustler_precompiled/
  - https://hexdocs.pm/rustler_precompiled/precompilation_guide.html
  - https://www.erlang.org/doc/system/nif.html
  - https://www.erlang.org/doc/system/commoncaveats.html
  - https://hex.pm/docs/publish
  - https://hexdocs.pm/hex_core/hex_tarball.html
  - https://hexdocs.pm/rustler/changelog.html
  - https://hexdocs.pm/mjml/changelog.html
  - https://hexdocs.pm/pcap_file_ex/0.1.5/changelog.html
---

# Problem

Rust already has real substrate for Elixir/Erlang NIFs and for shipping BEAM packages.

- `rustler` is a mature Rust-side bridge for writing Erlang NIFs safely.
- `rustler_precompiled` is explicit maintainer-facing substrate for downloading precompiled NIFs with checksums.
- Hex already has a real package-build and package-publish story built around package tarballs and checksums.
- Erlang/OTP already has explicit runtime native-loading behavior via `erlang:load_nif/2`, plus explicit warnings about VM responsiveness and long-running NIFs.
- Real packages now use this stack in production, including projects that add or drop specific precompiled targets, pin NIF versions, fix checksum-file inclusion, correct artifact naming, or force local builds when a target is unsupported.

But the maintainer-facing shipping contract is still too implicit.

Today, ordinary teams still piece together release truth from:

- `mix.exs` package metadata,
- Hex tarball contents and outer checksums,
- `checksum-*.exs` file generation and inclusion,
- `rustler_precompiled` module configuration,
- NIF-version feature choices and OTP support statements,
- `priv/native` naming and loader paths,
- CI target matrices,
- and README notes about “compile from source if this fails”.

That creates a support problem:

- a package may claim “no Rust toolchain needed” while the mandatory checksum file is not actually inside the Hex tarball,
- the checked-in checksum file may drift from the precompiled asset set or artifact naming that CI produced,
- the chosen minimum NIF version may not match the OTP window the README or package metadata implies,
- unsupported targets may silently fall back to local compilation without one compact support receipt,
- Hex tarball and remote-asset facts may drift apart,
- and the loader may expect one NIF base name while the precompiled asset naming follows another convention.

The sharper question is no longer “can Rust talk to the BEAM?”

The sharper question is: **what Hex package did we actually publish, which checksum file and precompiled assets does it truly carry, what NIF-version/OTP window does it honestly support, when do we fall back to source builds, and how can another maintainer review that without replaying CI and issue threads?**

The missing crate is not another NIF wrapper.

The missing crate is a **shipkit** that turns Rust-backed Hex releases into one boring, reviewable package contract: Hex tarball receipt, checksum-residency report, NIF-version-window report, fallback-trigger report, loader behavior, and downstream support verdicts.

# What it provides

- `hex-nif-shipkit.toml` — declares release posture: package tarball facts, remote precompiled posture, supported OTP / Elixir versions, supported targets, fallback-to-source rules, NIF naming, and support caveats.
- `hex-package.receipt.json` — records package name/version, tarball filename, outer checksum, included files, package metadata, and compressed/uncompressed size posture.
- `nif-precompiled.matrix.json` — every precompiled NIF artifact the project claims, with target triple, libc notes when relevant, checksum entry presence, NIF version, remote URL origin, and publish intent.
- `beam-loader.receipt.json` — records expected NIF module/base name, `priv` path assumptions, `erlang:load_nif` / RustlerPrecompiled loader posture, and whether local or remote loading is expected.
- `checksum-residency.report.json` — checks whether the generated checksum file is present in the Hex package, matches the asset matrix, and is sufficient for install-time verification.
- `nif-version-window.report.json` — records the chosen minimum NIF version, compatible OTP window, feature configuration, and whether support claims exceed the declared/runtime-compatible NIF surface.
- `fallback-trigger.report.json` — records when precompiled download should work, when unsupported targets force a local build, what toolchain prerequisites are assumed, and whether the fallback story is honest.
- `support-risk.report.json` — rolls checksum discipline, asset coverage, loader naming, fallback posture, and version support into one support verdict.
- `cargo hex-nif-ship inspect` — capture one release contract plus package/precompiled facts.
- `cargo hex-nif-ship check` — explain whether Hex tarball, checksum file, remote assets, NIF-version window, loader expectations, and fallback rules agree.
- `cargo hex-nif-ship diff <old> <new>` — compare support promises across package releases.
- `*.hexnifbundle.zip` — portable release-review and support artifact.

# What the crate should provide other people

1. **A boring answer to “what Hex package release did we actually ship?”** instead of Mix/CI archaeology.
2. **A checksum-residency receipt** that proves the mandatory checksum file is actually inside the Hex package and covers the assets users will download.
3. **A NIF-version/OTP-window report** that states which ABI window is really supported, instead of vague “supports OTP 22+” folklore.
4. **An explicit fallback-trigger report** that says when a user gets a precompiled NIF, when they fall back to source build, and what that build requires.
5. **A package/load contract** joining Hex tarball, remote assets, loader naming, and support posture into one reviewable bundle.

# Persona / who it’s for

- maintainers publishing Rust-backed Elixir or Erlang packages to Hex
- teams adopting `rustler` / `rustler_precompiled`
- release engineers producing multi-platform NIF assets
- support engineers diagnosing “works on one machine, compiles on another, downloads on a third” failures
- downstream BEAM users who want an honest support contract before adopting a native package

# Users & user stories

- **Package maintainer**: “Show me whether our Hex tarball, checksum file, remote assets, NIF version choice, and loader expectations actually agree.”
- **Release engineer**: “Give me one bundle that joins Mix package metadata, Hex tarball facts, Rust artifacts, NIF target coverage, and fallback rules.”
- **Support engineer**: “Tell me whether this failure is a missing precompiled asset, a checksum file missing from the package, a NIF-version mismatch, or an unsupported-target local-build fallback.”
- **Downstream user**: “Show whether I will download a precompiled NIF, compile from source, or fall into manual-review territory.”

# Prior art (and why it’s insufficient)

- `rustler` already gives serious Rust-side NIF authoring substrate.
- `rustler_precompiled` already makes precompiled NIF downloads and checksum verification possible.
- Erlang/OTP already documents NIF loading and caveats clearly enough that loader behavior is not a mystery surface.
- Hex already documents package building and publishing, and Hex Core exposes package-tarball checksum vocabulary.
- Real packages such as `mjml` and `pcap_file_ex` show live adoption of `rustler_precompiled`, target additions/drops, checksum workflows, local-build fallback, and artifact-naming fixes.

What remains missing is the **producer-side coordination layer** that answers: “which assets exist, is the checksum file really in the package, what NIF-version window are we promising, when do we force a local build, how will the BEAM load the NIF, and what support risk does that create?”

# Design goals

1. **Release-contract first** — the core value is the shipping promise, not another NIF authoring DSL.
2. **Checksum-residency explicit** — having a checksum file in CI or git is not the same as shipping it inside the Hex package.
3. **NIF-window honest** — minimum NIF version and OTP support claims must stay reviewable together.
4. **Fallback-explicit** — source-build escape hatches must be named, not implied.
5. **Loader-legible** — `erlang:load_nif`, `priv/native`, and RustlerPrecompiled download/load behavior must remain visibly distinct.
6. **Package-aware** — Hex tarball receipt and package-size posture are first-class facts.

# MVP surface

- Minimal types: `HexNifShipkitContract`, `HexPackageReceipt`, `NifPrecompiledMatrix`, `BeamLoaderReceipt`, `ChecksumResidencyReport`, `NifVersionWindowReport`, `FallbackTriggerReport`, `SupportRiskReport`, `HexNifBundle`
- Minimal functions:
  - `capture_hex_nif_shipkit_contract()`
  - `capture_hex_package_receipt()`
  - `collect_nif_precompiled_matrix()`
  - `capture_beam_loader_receipt()`
  - `evaluate_checksum_residency()`
  - `evaluate_nif_version_window()`
  - `evaluate_fallback_triggers()`
  - `diff_hex_nif_shipkits()`
- Feature flags:
  - `hex`
  - `mix`
  - `rustler`
  - `precompiled`
  - `serde`

# Compatibility story

- Must remain useful for packages that always compile from source and do not use remote precompiled assets.
- Must remain useful for packages that rely heavily on `rustler_precompiled` and checked-in checksum files.
- Must distinguish **Hex package tarball**, **remote NIF asset set**, **checksum residency**, **NIF-version window**, and **runtime loader expectations**, because those can drift independently.
- Should tolerate Elixir-favored projects that still support Erlang use, but must not overclaim BEAM-language portability automatically.
- Must not treat “one CI build succeeded” as evidence that downstream installation is boring.

# Conformance & fixtures

- one clean Hex package with aligned tarball receipt, checksum file, and precompiled NIF matrix
- one package where the checksum file exists in CI but is missing from the published Hex tarball
- one package where NIF-version / OTP support claims exceed the configured minimum ABI window
- one package where unsupported targets silently force a local build without an honest support statement
- one package where loader expects one NIF base name or `priv` path but assets use another naming/layout
- goldens for `checksum_residency_ok`, `checksum_file_missing_from_tarball`, `nif_version_window_honest`, `nif_window_claim_exceeds_features`, `fallback_contract_honest`, `unsupported_target_forces_local_build`, and `manual_review_required`

# Path to boring stability

- Freeze the contract and verdict vocabulary before adding every BEAM release nuance.
- Start with read-only inspection of package metadata, checksum state, loader expectations, produced artifacts, and support claims.
- Keep OTP / Elixir support reporting conservative.
- Prefer package-review artifacts over becoming a Hex publisher, release bot, or NIF build farm.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 5/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust-backed Hex package, record the Hex tarball receipt, inspect the precompiled-NIF matrix and checksum-residency posture, capture loader expectations, classify NIF-version support and fallback triggers, and emit one support bundle that names any shipping gaps.

# De-risk plan

1. Start with one clean `rustler_precompiled` package and one intentionally broken checksum/tarball scenario.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate first on Elixir-facing packages using Hex publishing, then generalize carefully to Erlang-first layouts if needed.
4. Avoid becoming another NIF framework, CI action bundle, or Hex publishing wrapper.

# Non-goals

- Not another NIF binding generator.
- Not a replacement for Hex, Mix, or release-pipeline tooling.
- Not a promise that every runtime crash or scheduler problem can be inferred statically.
- Not a full validator of BEAM VM safety, dirty-scheduler correctness, or NIF performance behavior.

# Architecture & API sketch

```rust
pub enum SupportRiskClass {
    ChecksumResidencyOk,
    ChecksumFileMissingFromTarball,
    NifVersionWindowHonest,
    NifWindowClaimExceedsFeatures,
    FallbackContractHonest,
    UnsupportedTargetForcesLocalBuild,
    ManualReviewRequired,
}

pub fn capture_hex_nif_shipkit_contract(root: &Path) -> Result<HexNifShipkitContract>;
pub fn capture_hex_package_receipt(root: &Path) -> Result<HexPackageReceipt>;
pub fn collect_nif_precompiled_matrix(root: &Path, contract: &HexNifShipkitContract) -> Result<NifPrecompiledMatrix>;
pub fn capture_beam_loader_receipt(root: &Path) -> Result<BeamLoaderReceipt>;
pub fn evaluate_checksum_residency(release: &HexNifRelease) -> Result<ChecksumResidencyReport>;
pub fn evaluate_nif_version_window(release: &HexNifRelease) -> Result<NifVersionWindowReport>;
pub fn evaluate_fallback_triggers(release: &HexNifRelease) -> Result<FallbackTriggerReport>;
```

Bundle draft: `hex-nif-shipkit.toml`, `hex-package.receipt.json`, `nif-precompiled.matrix.json`, `beam-loader.receipt.json`, `checksum-residency.report.json`, `nif-version-window.report.json`, `fallback-trigger.report.json`, `support-risk.report.json`, `notes.md`.

# Security / safety model

- Treat Hex packages, Mix metadata, `checksum.exs`, remote release assets, and built NIFs as untrusted input.
- Support redaction of private URLs, local file paths, and CI internals.
- Keep checksum reporting separate from broader claims about trustworthiness or supply-chain sufficiency.
- Never imply that “precompiled asset exists” means the NIF is safe for every BEAM deployment.

# Maintenance & governance plan

- Track Hex package metadata/build/publish changes and any package-tarball checksum vocabulary changes.
- Track `rustler` / `rustler_precompiled` only as substrate, not as the main contract itself.
- Track OTP/Elixir support-window changes that materially affect compatibility reporting.
- Maintain fixtures for checksum residency drift, NIF-window drift, target coverage gaps, loader drift, and source-build fallback instead of mirroring every project’s CI layout.

# Milestones

## 0.1
- contract file
- Hex tarball receipt
- precompiled matrix
- checksum-residency report
- initial support verdicts

## 0.2
- NIF-version-window report
- fallback-trigger report
- loader receipt
- diffing across releases

## 0.3
- package-size posture
- richer redaction
- optional lightweight asset-fetch verification hooks

# Open questions

- Which OTP / Elixir support facts are stable enough to record without overfitting to one package’s CI matrix?
- Should remote-asset verification stay read-only in the MVP or optionally fetch and verify checksums?
- How much loader inspection is useful before the crate drifts into runtime execution or full NIF testing?
- Where should the boundary sit between producer-side Hex package contracts and consumer-side support diagnosis handled by P-0487?
