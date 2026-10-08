# Frontier salience snapshot — 2026-03-18 (65)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0502 Hex Native NIF ShipKit** — because the archive still lacked a believable answer to “what exact Hex / NIF support promise is this Rust release making, and how can another person review it without replaying Mix metadata, GitHub release assets, and install-time fallback lore by hand?”

## Main judgment

The next worthy move here was **not** another NIF framework, another CI workflow example, another Hex publisher wrapper, or another generic supply-chain verifier.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **Hex native NIF shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **checksum residency** — whether the mandatory `checksum-*.exs` file is actually inside the Hex tarball and aligned with the observed precompiled artifacts.
- **NIF-version window** — which minimum NIF version is configured, what OTP family it really covers, and whether README/package claims outrun that window.
- **fallback trigger** — whether unsupported targets cause a forced local build, what prerequisites that implies, and whether that fallback was honestly declared.

That move is better grounded now because:

- `rustler_precompiled` explicitly says the Hex package should always include a checksum file and that the file is mandatory for the package to work;
- the current precompilation guide makes the build matrix target × NIF-version shaped and explains that NIF versions are more stable than OTP versions;
- Erlang/OTP still makes `erlang:load_nif/2` and stub/fallback behavior explicit, while common caveats still warn that NIFs can harm VM responsiveness;
- Hex publishing plus `hex_core` now keep package-tarball and outer-checksum vocabulary explicit enough to join a package receipt;
- real package changelogs now show that checksum-file omission, artifact naming drift, target expansion, explicit NIF-version upgrades, and forced local-build fallback are not hypothetical problems.

So the gap is no longer “Rust cannot ship BEAM-native packages.”
The gap is that teams still rarely get a **reviewable cargo-native Hex bundle** above checksum residency, NIF-version windows, and fallback-trigger truth.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm shipping-contract opportunities.
10. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK shipping-contract opportunities.
11. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET shipping-contract opportunities.
12. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-facing ship-contract opportunities.
13. **P-0502 Hex Native NIF ShipKit** — now one of the clearest BEAM-facing ship-contract opportunities because the substrate exists but the boring contract above checksum residency, NIF-version windows, and source-build fallback still does not.

## Why this won over adjacent candidates right now

- It beat **P-0500 JAR/JNI Native ShipKit** because the Hex lane now has especially sharp current evidence about mandatory checksum inclusion and fallback behavior.
- It beat **P-0501 RubyGems Native Extension ShipKit** because the Hex lane has a clearer first-party story around the precompiled/downloaded artifact boundary.
- It beat **another Rustler helper** because `rustler` and `rustler_precompiled` already exist and the sharper pain is release-contract truth above them.
- It beat **package-signing or provenance-first follow-ons** because checksum-residency / NIF-window / fallback truth remains the more immediate support bottleneck.

## What changed in the archive

Added:
- `entries/2026-03-18-245.md`
- `meta/frontier-salience-2026-03-18-65.md`
- `meta/hex-native-nif-shipkit-product-plan-2026-03-18.md`
- `fixtures/hex-nif-shipkit/checksum-residency.report.schema.json`
- `fixtures/hex-nif-shipkit/nif-version-window.report.schema.json`
- `fixtures/hex-nif-shipkit/fallback-trigger.report.schema.json`
- `fixtures/hex-nif-shipkit/scenarios/checksum_file_missing_from_hex_tarball/`
- `fixtures/hex-nif-shipkit/scenarios/nif_version_floor_overclaims_otp_window/`
- `fixtures/hex-nif-shipkit/scenarios/unsupported_target_forces_local_build_without_honest_contract/`

Updated:
- `proposals/hex-native-nif-shipkit.md`
- `fixtures/hex-nif-shipkit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- Hex tarball facts,
- checksum-file inclusion,
- remote precompiled artifact coverage,
- NIF-version / OTP ABI claims,
- and source-build fallback triggers

into one fake “BEAM support” story.
