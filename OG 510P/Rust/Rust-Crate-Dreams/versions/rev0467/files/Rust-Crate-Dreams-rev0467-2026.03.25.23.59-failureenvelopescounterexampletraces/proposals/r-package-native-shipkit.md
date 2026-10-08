---
id: P-0526
title: R Package Native ShipKit — registration posture, DLL load contracts, and install posture for Rust-backed packages
status: idea
domains: [r, cran, packaging, compiled-code, release, ci, tooling]
last_reviewed: 2026-03-18
evidence:
  - https://extendr.rs/rextendr/articles/package.html
  - https://extendr.github.io/extendr/extendr_api/macro.extendr_module.html
  - https://cran.r-project.org/doc/manuals/r-devel/R-exts.html
  - https://cran.r-project.org/doc/manuals/r-devel/R-ints.html
  - https://cran.r-project.org/doc/manuals/r-patched/packages/utils/refman/utils.html
  - https://cran.r-project.org/doc/manuals/r-devel/R-admin.html
  - https://github.com/nanxstats/r-rust-pkgs
---

# Problem

Rust already has real substrate for shipping compiled R packages.

- `extendr` provides the Rust-side authoring layer and exported-module surface for calling Rust from R.
- `rextendr` already scaffolds package structure, `src/entrypoint.c`, `src/Makevars`, `src/Makevars.win`, a Rust crate, and generated wrapper files for ordinary R-package development.
- CRAN and base R already have a real compiled-package story: native routine registration, `useDynLib(...)`, `library.dynam`, `R CMD INSTALL`, staged installation, sub-architecture rules, and binary-package distribution conventions.
- There are now many Rust-backed packages on CRAN, which proves the lane is no longer hypothetical.

But ordinary maintainers still lack one boring release/support artifact answering:

- whether native routines are registered explicitly or still rely on fuzzier dynamic lookup assumptions,
- whether the package’s `NAMESPACE`, wrapper layer, DLL/shared-object names, generated `entrypoint.c`, and installed `libs/` artifacts actually agree,
- whether installation posture is honestly “CRAN binary will usually cover users”, “source build with Cargo/toolchain required”, or “mixed/manual review required”,
- whether staged installation, temp-path assumptions, or local build requirements are being silently smuggled into the package,
- and how to explain “works on my machine” versus “boring for downstream users on Windows/macOS/Linux and current R series.”

So the missing crate is **not** another Rust↔R binding generator.
It is **not** another package skeletoner.
It is **not** another generic `R CMD check` wrapper.

The sharper missing crate is an **R package native shipkit**:
a cargo-adjacent crate that turns a Rust-backed R package release into a reviewable **registration-posture report, DLL-load-contract report, install-posture report, build-toolchain receipt, and support bundle**.

# What it provides

- `rpkg-shipkit.toml` — declares package name, Rust crate/lib name, expected DLL/shared-object base name, wrapper generation mode, install posture, system requirements, and support caveats.
- `native-registration.report.json` — classifies whether the package has explicit routine registration, `useDynLib(..., .registration = TRUE)` alignment, dynamic-symbol posture, and any obvious wrapper/export drift.
- `dll-load-contract.report.json` — records how the compiled code is expected to load (`useDynLib`, `.onLoad` + `library.dynam`, manual load edge cases), plus package/DLL/wrapper/lib-name alignment.
- `install-posture.report.json` — states whether the package is realistically `cran_binary_expected`, `source_build_required`, `mixed_binary_source`, or `manual_review_required`, including Cargo/toolchain and staged-install notes.
- `wrapper-surface.receipt.json` — records generated R wrappers, exported symbols, extendr-module expectations, and whether the wrapper surface matches the compiled module story.
- `build-toolchain.receipt.json` — records R version family, package metadata, Rust toolchain facts if available, system requirements, and build-entrypoint files observed.
- `support-risk.report.json` — rolls registration posture, load contract, and install posture into one conservative downstream support verdict.
- `cargo rpkg-ship inspect` — read package metadata, wrapper files, `src/entrypoint.c`, Makevars, NAMESPACE, and built artifacts.
- `cargo rpkg-ship check` — explain whether registration, load, and install claims agree.
- `cargo rpkg-ship diff <old> <new>` — compare support promises across package releases.
- `*.rpkgbundle.zip` — portable review/support artifact for release engineering and downstream diagnosis.

# What the crate should provide other people

1. **A boring answer to “what compiled R package do we actually ship?”** instead of folklore spread across DESCRIPTION, NAMESPACE, wrappers, `src/entrypoint.c`, and CI.
2. **An explicit registration posture** instead of assuming generated wrappers or one successful `.Call` prove the native surface is stable.
3. **A DLL load contract** that shows how the package actually finds and loads its compiled code.
4. **An honest install posture** that tells users whether they are likely getting CRAN binaries or a local compiled-code build path with Cargo/toolchain requirements.
5. **A diffable support bundle** that makes release drift visible when package names, library names, wrappers, or install promises change.

# Persona / who it’s for

- maintainers publishing Rust-backed R packages
- release engineers preparing CRAN-friendly source and binary releases
- teams exposing Rust libraries into R ecosystems for data science, geospatial, and scientific workflows
- support engineers diagnosing “package installs here but not there” failures
- downstream R users and platform engineers who need an honest compiled-code support statement before adoption

# Users & user stories

- **Package maintainer**: “Tell me whether our `NAMESPACE`, generated wrappers, `entrypoint.c`, and Rust lib name still agree.”
- **Release engineer**: “Give me one bundle that explains whether this release is registration-clean, load-clean, and honestly installable for ordinary CRAN users.”
- **Support engineer**: “Show me whether failure is about missing binaries, local Cargo/toolchain requirements, staged-install assumptions, or a load-name mismatch.”
- **Downstream user**: “Am I getting a boring binary package or a source build with compiled-code prerequisites?”

# Prior art (and why it’s insufficient)

- `extendr` already provides real authoring substrate for Rust-backed R APIs.
- `rextendr` already scaffolds package structure and developer workflows.
- Base R and CRAN already document native routine registration, `useDynLib`, `library.dynam`, staged installation, sub-architecture handling, and binary-package conventions.
- Existing R package-development tools can inspect some native-routine registration facts.

What remains missing is the **maintainer-facing coordination layer** that joins those surfaces into one reviewable statement:
“what compiled package contract did we actually ship, how is the DLL loaded, and how honest is the install posture for ordinary users?”

# Design goals

1. **Release-contract first** — the value is the shipping promise, not another binding API.
2. **R-package-native aware** — keep registration, wrapper generation, DLL loading, and install posture first-class.
3. **CRAN-reality aware** — reflect binary/source-install reality rather than pretending all users compile from source happily.
4. **Reviewable** — emit artifacts humans can inspect before publication.
5. **Conservative** — prefer `manual_review_required` over optimistic guesses when metadata and compiled artifacts drift.

# MVP surface

- Minimal types: `RpkgShipkitContract`, `RegistrationPostureReport`, `DllLoadContractReport`, `InstallPostureReport`, `WrapperSurfaceReceipt`, `BuildToolchainReceipt`, `SupportRiskReport`, `RpkgBundle`
- Minimal functions:
  - `capture_rpkg_shipkit_contract()`
  - `evaluate_registration_posture()`
  - `evaluate_dll_load_contract()`
  - `evaluate_install_posture()`
  - `capture_wrapper_surface_receipt()`
  - `capture_build_toolchain_receipt()`
  - `diff_rpkg_shipkits()`
- Feature flags:
  - `r-package`
  - `serde`
  - `naming-checks`
  - `build-receipts`

# Compatibility story

- Must remain useful for `extendr` / `rextendr` packages.
- Must remain useful for packages that load compiled code through classic `useDynLib` paths without extendr.
- Must distinguish **registration posture**, **DLL load contract**, and **install posture**, because those can drift independently.
- Should tolerate packages distributed beyond CRAN, while keeping CRAN/source/binary expectations explicit.
- Must not treat “compiled once locally” as evidence that downstream installation is boring.

# Conformance & fixtures

- one clean extendr/rextendr package with explicit registration and aligned wrapper/load names
- one package where crate/lib/package naming drift breaks `useDynLib` or wrapper assumptions
- one package where install posture really implies local Cargo/toolchain work
- one package where staged-install assumptions or temp-path assumptions need explicit review
- one package where generated wrappers are stale relative to the compiled Rust module
- goldens for `registration_contract_ok`, `registration_posture_review_required`, `dll_load_name_mismatch`, `source_build_required`, `mixed_binary_source`, and `manual_review_required`

# Path to boring stability

- Freeze the contract vocabulary before adding automation for submission or publishing.
- Start read-only: inspect package metadata, wrappers, generated entrypoints, and built artifacts.
- Keep install-posture classification conservative and explanation-heavy.
- Prefer release-review and support bundles over becoming another build orchestrator.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 5/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust-backed R package, capture its release posture, normalize registration/load/install facts, and emit one support bundle naming any registration, naming, or install-support gaps.

# De-risk plan

1. Start with one clean extendr package and one intentionally broken name/registration drift fixture.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate on packages that ship through CRAN-like source/binary flows before expanding to every alternate R repository.
4. Avoid becoming another binding generator, package template, or generic CRAN automation suite.

# Non-goals

- Not another Rust↔R binding generator.
- Not a replacement for `extendr`, `rextendr`, CRAN, or `R CMD check`.
- Not a promise that one successful local install means ordinary downstream users have a boring path.
- Not a generic R package manager or repository host.

# Architecture & API sketch

```rust
pub enum InstallPostureClass {
    CranBinaryExpected,
    SourceBuildRequired,
    MixedBinarySource,
    ManualReviewRequired,
}

pub fn capture_rpkg_shipkit_contract(root: &Path) -> Result<RpkgShipkitContract>;
pub fn evaluate_registration_posture(root: &Path, contract: &RpkgShipkitContract) -> Result<RegistrationPostureReport>;
pub fn evaluate_dll_load_contract(root: &Path, contract: &RpkgShipkitContract) -> Result<DllLoadContractReport>;
pub fn evaluate_install_posture(root: &Path, contract: &RpkgShipkitContract) -> Result<InstallPostureReport>;
pub fn write_bundle(bundle: &RpkgBundle, out: &Path) -> Result<()>;
```

Bundle draft: `rpkg-shipkit.toml`, `native-registration.report.json`, `dll-load-contract.report.json`, `install-posture.report.json`, `wrapper-surface.receipt.json`, `build-toolchain.receipt.json`, `support-risk.report.json`, `notes.md`.

# Security / safety model

- Treat package metadata, generated wrappers, build logs, and compiled artifacts as untrusted input.
- Support redaction of local paths, personal library trees, and CI-internal environment variables.
- Keep install-posture honesty separate from claims about code correctness or package safety.
- Never imply that “binary package exists for one OS/R series” means boring support for every user.

# Maintenance & governance plan

- Track CRAN/base-R changes to compiled-code packaging, binary distribution, staged installation, and registration guidance.
- Track `extendr` / `rextendr` only as substrate, not as the entire contract.
- Keep registration/load/install vocabulary intentionally small and explanation-heavy.
- Maintain fixtures for naming drift, stale wrappers, and source-build-required posture.

# Milestones

## 0.1
- contract file
- registration posture report
- DLL load contract report
- install posture report
- bundle + diff

## 0.2
- build-toolchain receipt
- wrapper-surface receipt
- richer staged-install and source-build explanations

## 0.3
- multi-release drift summaries
- optional imports from CRAN-like binary/source indexes
- polished markdown release-review output
