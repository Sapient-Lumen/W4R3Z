# Frontier salience snapshot — 2026-03-19 (72)

This pass did **not** add another GUI framework, another updater crate, or another packaging backend.
It sharpened a neglected but highly leverageable adoption lane:

- **P-0012 Desktop ShipKit** — because Rust now has meaningful desktop release substrate, but still lacks one boring contract for release identity, update channels, and crash-symbol handoff.

## Main judgment

The next worthy move here was **not** another packager and **not** another updater library.
Those already exist as substrate.

The sharper missing layer is the **desktop release/update/support contract** above today’s substrate, especially once three more facts are kept explicit:

- **release identity truth** — what artifacts, routes, and signing/notarization posture the release actually claims;
- **update channel truth** — what stable/beta/nightly or internal-ring topology actually exists and whether key continuity holds;
- **crash symbol truth** — whether the shipped binaries still have a usable post-release support path via embedded or split symbols.

That move is better grounded now because:

- `dist` / `cargo-dist` already plans, builds, hosts, publishes, and announces releases, and emits machine-readable manifests;
- `cargo-packager` already packages and signs outputs for major desktop OS families;
- Tauri’s current distribution docs make code signing, notarization, store/direct routes, and updater signatures explicitly first-class;
- and Rust/Cargo debug-info behavior is still platform-specific enough that symbol handoff is not safely inferable from “the build succeeded.”

So the gap is no longer “Rust cannot ship desktop apps.”
The gap is that teams still rarely get a **reviewable desktop release promise** above the substrate.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
8. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
9. **P-0012 Desktop ShipKit** — now promoted as a stronger Band B shipping candidate because the missing value is no longer “make installers somehow,” but a release/update/support contract above existing tooling.
10. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
11. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
12. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
13. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.
14. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK contract opportunities.
15. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET contract opportunities.
16. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-native contract opportunities.

## Why this won over adjacent candidates right now

- It beat a broader **desktop packager rewrite** because cargo-dist, cargo-packager, and Tauri already prove packaging substrate exists.
- It beat a narrower **self-updater** lane because updater capability alone does not answer release-identity or symbol-handoff questions.
- It beat another **foreign-package shipping** pass because the archive needed another strong desktop/product adoption candidate outside the recent mobile/language-package cluster.

## What changed in the archive

Added:
- `entries/2026-03-19-252.md`
- `meta/frontier-salience-2026-03-19-72.md`
- `meta/desktop-shipkit-product-plan-2026-03-19.md`
- `meta/desktop-shipkit-lane-boundaries-2026-03-19.md`
- `fixtures/desktop-shipkit/release-identity.receipt.schema.json`
- `fixtures/desktop-shipkit/update-channel.contract.schema.json`
- `fixtures/desktop-shipkit/crash-symbol-handoff.manifest.schema.json`
- `fixtures/desktop-shipkit/scenarios/windows_signed_installer_update_key_rotated_without_migration/`
- `fixtures/desktop-shipkit/scenarios/macos_direct_download_release_missing_dsym_handoff/`
- `fixtures/desktop-shipkit/scenarios/linux_mixed_format_release_channel_drift/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/desktop-shipkit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `fixtures/desktop-shipkit/README.md`

## What this pass deliberately did not do

It did **not** collapse:

- package production,
- signing/notarization identity,
- update-channel topology,
- symbol/debug-sidecar handoff,
- and crash-reporting backend choice

into one fake “desktop shipping support” story.
