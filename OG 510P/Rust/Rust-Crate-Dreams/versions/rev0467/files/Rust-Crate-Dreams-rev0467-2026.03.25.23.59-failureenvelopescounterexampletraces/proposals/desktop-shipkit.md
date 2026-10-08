---
id: P-0012
title: Desktop ShipKit — release identity, update channels, and crash-symbol handoff for Rust apps
status: idea
domains: [desktop, distribution, release-engineering, signing, updates, support]
last_reviewed: 2026-03-19
evidence:
  - https://axodotdev.github.io/cargo-dist/book/
  - https://docs.rs/cargo-packager/latest/cargo_packager/
  - https://docs.crabnebula.dev/packager/
  - https://v2.tauri.app/distribute/
  - https://v2.tauri.app/plugin/updater/
  - https://doc.rust-lang.org/rustc/codegen-options/index.html
  - https://doc.rust-lang.org/cargo/reference/profiles.html
  - https://github.com/danwilliams/patchify
  - https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
---

# Problem

Rust desktop apps no longer suffer from a total lack of release tooling.
The substrate is real now:

- `dist` / `cargo-dist` already plans, builds, hosts, publishes, and announces releases, and emits machine-readable manifests.
- `cargo-packager` already packages executables into installers or app bundles for macOS, Windows, and Linux, and exposes signing-oriented APIs.
- Tauri’s current distribution docs explicitly treat platform bundling, signing, notarization, and updater signatures as first-class release concerns.
- Rust/Cargo debug-info behavior is platform-specific enough that symbol-sidecar handling still requires deliberate review instead of wishful thinking.
- There are also self-update libraries such as Patchify, which prove ongoing demand for “the app can update itself” workflows.

So the missing value is no longer simply “make installers from Rust.”
The sharper missing crate is the **boring release/update/support contract** above today’s packaging and updater substrate.

Teams still need one reviewable answer to questions like:

- what exact release identity did we publish,
- which artifacts belong to which update channel,
- what signing or notarization promises are actually in force,
- which store-vs-direct-download routes diverge,
- and where the crash symbols or debug sidecars went when support needs to diagnose a field failure.

That is the seam **Desktop ShipKit** should occupy.

# What it should provide

## 1) One release identity receipt

Other people should get a compact artifact that says, per release:

- app identifier,
- version and channel,
- target triples and package formats,
- direct-download versus store-distribution posture,
- signing/notarization state,
- and artifact provenance/import origins.

This should become `release-identity.receipt.json`.

## 2) One update-channel contract

The crate should make update routing reviewable instead of folklore.
It should record:

- stable/beta/nightly or internal ring layout,
- full versus delta artifact families,
- signing key / update identity continuity,
- rollback or pinning policy,
- and explicit “manual review required” zones when a project mixes store delivery with direct-download updates.

This should become `update-channel.contract.json`.

## 3) One crash-symbol handoff manifest

Desktop teams repeatedly discover too late that a release binary shipped but the matching symbols did not.
The crate should provide a manifest that records:

- whether symbols were embedded or split,
- what sidecars exist (`.pdb`, `.dSYM`, `.dwp`, etc.),
- whether stripping changed debugger usefulness,
- and where symbols were retained, uploaded, or intentionally omitted.

This should become `crash-symbol-handoff.manifest.json`.

## 4) One drift-aware support bundle

The crate should be able to bundle the release receipt, update contract, symbol manifest, and notes into one compact `desktopshipbundle.zip` so another maintainer can review a broken update or crash pipeline without spelunking half a CI system.

# Users & user stories

- **Rust desktop app maintainer**: “Tell me exactly what release promises we made on Windows, macOS, and Linux.”
- **Release engineer**: “Diff two releases and show me whether the channel topology, signing identity, or artifact families changed.”
- **Support engineer**: “A customer crashed on version X. Show me where the matching symbols and bundles are supposed to live.”
- **Security/review owner**: “Do not just say ‘signed’; tell me which artifacts were signed, which channel key was used, and where store-vs-direct divergence starts.”
- **Tooling author**: “I want to import manifests from cargo-dist, cargo-packager, or a Tauri build and normalize them into one reviewable report.”

# Prior art (and why it’s insufficient)

- **`dist` / `cargo-dist`** is strong release-engineering substrate with CI generation, installers, and machine-readable manifests, but it is broader release automation rather than a small contract-focused review layer.
- **`cargo-packager`** already packages and can sign outputs, but it is still primarily a packaging tool rather than a release/update/support contract that another team can diff and audit.
- **CrabNebula Packager docs** make cross-platform packaging and an updater flow concrete, but the lane still centers artifact production, not a normalized release promise for downstream review.
- **Tauri distribution and updater docs** make platform signing, notarization, update signatures, and store/direct distribution real, but they are framework-specific substrate, not a general Rust desktop release contract.
- **Patchify** proves there is still live appetite for self-updating Rust applications, but updater substrate alone does not answer release-identity or symbol-handoff questions.
- **Existing debug/support proposals in this archive** already cover symbol-sidecar and source-lookup posture more broadly; Desktop ShipKit should import those truths, not re-solve them.

# Design goals

1. **Import existing release tooling rather than replace it.**
2. **Keep release identity, update topology, and symbol handoff visibly separate.**
3. **Support direct-download desktop apps first**, with honest manual-review boundaries for app stores.
4. **Emit reviewable artifacts**, not just perform packaging side effects.
5. **Compose with debug/support contracts** instead of pretending desktop shipping owns all debugger concerns.
6. **Stay framework-neutral**: Tauri, egui, Slint, iced, winit-based apps, and plain CLI-with-GUI-shell apps should all be able to import it.
7. **Allow mixed-tool imports** from cargo-dist, cargo-packager, Tauri, or hand-rolled pipelines.

# Non-goals

- Replacing cargo-dist, cargo-packager, Tauri, or OS-native app-store tooling.
- Becoming a universal GUI framework.
- Solving crash reporting backend choice.
- Acting as a full software-distribution SaaS.
- Claiming that store delivery and direct-download updaters can always be unified without loss.

# Architecture & API sketch

## Suggested workspace split

- `desktop_ship_model`
  - core types for release identity, channel topology, and symbol handoff
- `desktop_ship_import_dist`
  - importers for `dist` / `cargo-dist` manifests
- `desktop_ship_import_packager`
  - importers for `cargo-packager` / packager metadata
- `desktop_ship_import_tauri`
  - importers for Tauri bundle/updater metadata
- `desktop_ship_symbols`
  - symbol-sidecar and strip/split-debuginfo inspection helpers
- `desktop_ship_bundle`
  - zip bundle writer / diff logic
- `cargo-desktop-shipkit`
  - cargo subcommand / CLI

## Core commands

- `cargo desktop-ship inspect`
  - emit `release-identity.receipt.json`
- `cargo desktop-ship channels`
  - emit `update-channel.contract.json`
- `cargo desktop-ship symbols`
  - emit `crash-symbol-handoff.manifest.json`
- `cargo desktop-ship diff`
  - compare two release/support bundles
- `cargo desktop-ship bundle`
  - produce `desktopshipbundle.zip`

## Draft API sketch

```rust
pub fn inspect_release_identity(input: &ReleaseInput) -> Result<ReleaseIdentityReceipt>;
pub fn inspect_update_channels(input: &ChannelInput) -> Result<UpdateChannelContract>;
pub fn inspect_symbol_handoff(input: &SymbolInput) -> Result<CrashSymbolHandoffManifest>;
pub fn diff_release_bundles(old: &DesktopShipBundle, new: &DesktopShipBundle) -> Result<DesktopShipDiff>;
pub fn write_bundle(bundle: &DesktopShipBundle, out: &Path) -> Result<()>;
```

# Security / safety model

- Never equate “artifact exists” with “artifact is signed, notarized, or updater-trusted.”
- Preserve a distinct field for signing identity continuity versus one-off successful signing.
- Keep store distribution, direct-download distribution, and self-update routes distinct.
- Treat symbol manifests and support bundles as potentially sensitive.
- Record when stripping or split-debuginfo choices reduce post-release diagnosability.

# Maintenance & governance plan

- Track cargo-dist, cargo-packager, and Tauri metadata evolution via importer modules rather than one giant parser.
- Keep app-store support explicitly narrower than direct-download support until honest workflows exist.
- Import the archive’s existing debug-support posture work instead of forking a second symbol-policy framework.
- Maintain a tiny fixture corpus that covers common desktop failure seams: channel drift, key rotation, missing symbols, and mixed-format release sets.

# Milestones

## 0.1
- normalize one cargo-dist release into `release-identity.receipt.json`
- import one cargo-packager layout
- inspect a symbol-sidecar set for one Windows/MSVC and one macOS release
- bundle one desktop support artifact

## 0.2
- updater-channel contract and signing-identity continuity checks
- Tauri updater import lane
- store-vs-direct-download manual-review classification

## 0.3
- diff tooling across releases
- delta/full artifact family classification
- symbol upload / retention handoff adapters

# Open questions

- How much store-specific metadata belongs in the `0.1` contract versus staying in manual-review notes?
- Should the kit model updater key rotation explicitly, or only record continuity/breakage?
- Which import shape is most stable for cargo-dist and packager ecosystems: config import, manifest import, or built-artifact inspection?
- How should Linux package families be normalized without pretending `.deb`, AppImage, RPM, and store/sandbox channels are interchangeable?

# Sources

See front matter links.
