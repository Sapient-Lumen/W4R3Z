# Desktop ShipKit — product plan (2026-03-19)

This note sharpens **P-0012 Desktop ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become “the one true desktop release platform.”
It should be a **small crate family plus CLI** that helps desktop teams publish one reviewable answer to:

- what release identity they actually shipped,
- what updater/channel topology they actually promised,
- whether store and direct-download routes diverge,
- and where the matching crash symbols or debug sidecars actually went.

The missing value is the **boring contract layer** above today’s release automation, packaging, updater, and signing substrate.

## What the crate should provide other people

For desktop maintainers, release engineers, support teams, and tooling authors, the crate should provide:

1. **One release identity receipt** instead of ad hoc release notes and CI assumptions.
2. **One update-channel contract** instead of “stable/beta/nightly” folklore.
3. **One crash-symbol handoff manifest** instead of after-the-fact hunting for `.pdb` or `.dSYM` outputs.
4. **One drift workflow** that explains what changed between releases.
5. **One compact support bundle** that can travel between maintainers and CI.

## Three first-class review objects

### 1. Release identity receipt

Named classes for `0.1` should focus on release truth such as:

- `artifact_family_declared`
- `direct_download_route_declared`
- `store_route_declared`
- `signing_status_declared`
- `notarization_status_declared`
- `manual_review_required`

This object should answer:

- which package families exist,
- which platforms/targets they correspond to,
- whether the route is store-only, direct-download-only, or mixed,
- and whether signing/notarization claims are actually present.

### 2. Update-channel contract

Named classes for `0.1` should focus on update truth such as:

- `channel_ring_declared`
- `full_artifact_family_declared`
- `delta_artifact_family_declared`
- `key_continuity_preserved`
- `store_vs_direct_manual_review`
- `rollback_policy_declared`

This object should answer:

- what rings/channels exist,
- which artifact families belong to each,
- whether key identity continued or rotated,
- and what rollback/pinning promise is in force.

### 3. Crash-symbol handoff manifest

Named classes for `0.1` should focus on diagnosability truth such as:

- `embedded_symbols_only`
- `split_sidecar_present`
- `sidecar_missing`
- `strip_reduces_debuggability`
- `upload_target_declared`
- `manual_review_required`

This object should answer:

- what symbol sidecars exist,
- whether they match shipped binaries,
- what `strip` / `split-debuginfo` posture was used,
- and where the support path is expected to fetch symbols.

## Recommended `0.1` command surface

### `cargo desktop-ship inspect`
Inspect a release output and emit:
- `release-identity.receipt.json`
- `desktop-ship.inspect.report.json`

### `cargo desktop-ship channels`
Inspect updater/config metadata and emit:
- `update-channel.contract.json`

### `cargo desktop-ship symbols`
Inspect symbol sidecars and emit:
- `crash-symbol-handoff.manifest.json`

### `cargo desktop-ship diff`
Compare two release bundles and emit:
- `desktop-ship-drift.diff.json`

### `cargo desktop-ship bundle`
Produce one compact `.desktopshipbundle.zip` containing reports, notes, and imported metadata.

## Recommended crate/workspace split

- `desktop_ship_model`
- `desktop_ship_import_dist`
- `desktop_ship_import_packager`
- `desktop_ship_import_tauri`
- `desktop_ship_symbols`
- `desktop_ship_bundle`
- `cargo-desktop-shipkit`

## `0.1` artifact set

Core artifacts should be:
- `desktop-ship.toml`
- `release-identity.receipt.json`
- `update-channel.contract.json`
- `crash-symbol-handoff.manifest.json`
- `desktop-ship.inspect.report.json`
- `desktop-ship-drift.diff.json`
- `notes.md`

## Discovery order

1. **Release import**
   - artifact inventory
   - target/package family
   - direct/store route
2. **Identity classification**
   - version/channel
   - signing/notarization posture
3. **Channel inspection**
   - rings
   - full vs delta families
   - key continuity
4. **Symbol inspection**
   - embedded vs split
   - sidecar mapping
   - upload/retention route
5. **Bundle export**
   - receipts
   - manifests
   - manual-review notes

## Ranking discipline

A good `0.1` should not treat “the app was packaged once” as the verdict.
It should keep separate:

- `release_identity_known`
- `channel_topology_known`
- `symbol_handoff_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- `dist` / `cargo-dist` release planning and manifest output
- `cargo-packager` / packager packaging and signing substrate
- Tauri bundling, signing, notarization, and updater signatures
- Rust/Cargo `strip` / `split-debuginfo` behavior
- optional self-update substrate such as Patchify

### Do not flatten into one fake verdict
- “the installer exists”
- “the artifact is signed”
- “the updater can verify an artifact”
- “the app store route exists”
- “the support team can actually diagnose crashes”

## Preferred proving grounds

- a Windows/MSVC release with NSIS or MSI installers and `.pdb` sidecars
- a macOS direct-download release where `.dmg`/`.app` distribution diverges from App Store posture
- a Linux mixed-format release (`.deb` + AppImage) where update/channel family drift is easy to miss
- a Tauri updater configuration where key continuity matters across releases

## Non-goals

- not a universal installer generator
- not a crash-reporting backend
- not an app-store submission automation suite
- not a general provenance or transparency framework

## MVP API sketch

```rust
pub fn inspect_release_identity(input: &ReleaseInput) -> Result<ReleaseIdentityReceipt>;
pub fn inspect_update_channels(input: &ChannelInput) -> Result<UpdateChannelContract>;
pub fn inspect_symbol_handoff(input: &SymbolInput) -> Result<CrashSymbolHandoffManifest>;
pub fn diff_release_bundles(old: &DesktopShipBundle, new: &DesktopShipBundle) -> Result<DesktopShipDiff>;
pub fn write_bundle(bundle: &DesktopShipBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Track cargo-dist, cargo-packager, and Tauri metadata/import drift explicitly.
- Preserve manual-review classes whenever store policy, notarization, or updater-key migration cannot be stated honestly.
- Keep the kit small and read-mostly.
- Compose with the archive’s debug-support/symbol-handoff work rather than fork it.

## Sources

- https://axodotdev.github.io/cargo-dist/book/
- https://docs.rs/cargo-packager/latest/cargo_packager/
- https://docs.crabnebula.dev/packager/
- https://v2.tauri.app/distribute/
- https://v2.tauri.app/plugin/updater/
- https://doc.rust-lang.org/rustc/codegen-options/index.html
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://github.com/danwilliams/patchify
