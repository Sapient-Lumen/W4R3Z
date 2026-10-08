# Frontier salience snapshot — 2026-03-18 (67)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened another **shipping and adoption accelerator**:

- **P-0526 R Package Native ShipKit** — because the archive still lacked a believable answer to “what exact compiled R-package support promise is this Rust release making, and how can another person review it without replaying DESCRIPTION, NAMESPACE, wrappers, `src/entrypoint.c`, and CRAN install folklore by hand?”

## Main judgment

The next worthy move here was **not** another Rust↔R binding layer, another package skeleton generator, another generic `R CMD check` wrapper, or another broad CRAN automation suite.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **R-package native shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **registration posture** — whether the package has explicit native routine registration and `useDynLib(..., .registration = TRUE)`-style alignment or still hides wrapper/runtime ambiguity.
- **DLL load contract** — whether package name, library name, wrapper layer, `entrypoint.c`, and installed `libs/` artifacts still agree on how compiled code is loaded.
- **install posture** — whether ordinary users are realistically covered by CRAN binaries, require local compiled-code installation with Cargo/toolchains, or still sit behind a mixed/manual-review boundary.

That move is better grounded now because:

- `rextendr` already scaffolds the exact files ordinary maintainers are currently stitching together by hand;
- `extendr` already provides the Rust-side export/module substrate;
- current R manuals still make native routine registration, `useDynLib`, `library.dynam`, staged installation, and sub-architecture rules explicit;
- CRAN/base-R installation docs still distinguish binary-package intake from source-package installs that require compiled-code toolchains;
- and there are now many Rust-backed packages on CRAN, which proves the lane is no longer hypothetical.

So the gap is no longer “Rust cannot ship compiled R packages.”
The gap is that teams still rarely get a **reviewable cargo-native R-package bundle** above registration posture, DLL-load truth, and install-posture honesty.

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
13. **P-0502 Hex Native NIF ShipKit** — still one of the clearest BEAM-facing ship-contract opportunities.
14. **P-0500 JAR/JNI Native ShipKit** — still one of the clearest JVM-facing ship-contract opportunities.
15. **P-0526 R Package Native ShipKit** — now one of the clearest R/CRAN-facing ship-contract opportunities because the substrate exists but the boring contract above registration posture, DLL load contracts, and install posture still does not.

## Why this won over adjacent candidates right now

- It beat **P-0501 RubyGems Native Extension ShipKit** because the R lane now has especially sharp first-party packaging/load/install rules plus visible real-world Rust-on-CRAN adoption.
- It beat **another extendr/rextendr helper** because those already solve authoring/scaffolding; the sharper pain is release-contract truth above them.
- It beat **generic CRAN automation follow-ons** because registration/load/install honesty is the more immediate downstream support bottleneck.
- It beat **another binary-build helper** because the key missing value is not producing artifacts but explaining what support promise those artifacts actually make.

## What changed in the archive

Added:
- `entries/2026-03-18-247.md`
- `proposals/r-package-native-shipkit.md`
- `meta/frontier-salience-2026-03-18-67.md`
- `meta/r-package-native-shipkit-product-plan-2026-03-18.md`
- `fixtures/r-package-native-shipkit/registration-posture.report.schema.json`
- `fixtures/r-package-native-shipkit/dll-load-contract.report.schema.json`
- `fixtures/r-package-native-shipkit/install-posture.report.schema.json`
- `fixtures/r-package-native-shipkit/scenarios/usedynlib_registration_missing_after_wrapper_regeneration/`
- `fixtures/r-package-native-shipkit/scenarios/lib_name_drift_breaks_dll_load_alignment/`
- `fixtures/r-package-native-shipkit/scenarios/source_install_requires_cargo_but_posture_claims_boring_binary/`

Updated:
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

- wrapper generation,
- native routine registration,
- DLL/shared-object naming,
- binary/source installation posture,
- and one successful local install

into one fake “R support” story.
