# R Package Native ShipKit — product plan (2026-03-18)

This note sharpens **P-0526 R Package Native ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- whether native routines are explicitly registered and aligned with wrappers,
- how compiled code is expected to load inside the R package,
- whether package/lib/module names still agree,
- whether installation posture is really binary-friendly or source-build/toolchain-heavy,
- and whether the release story is boring enough for ordinary downstream users.

It should **not** try to become a replacement for `extendr`, `rextendr`, CRAN, or `R CMD check`.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For maintainers, release engineers, support reviewers, and downstream R users, the crate should provide:

1. **One compact support contract** instead of release truth spread across DESCRIPTION, NAMESPACE, wrapper files, `src/entrypoint.c`, Makevars, and CI.
2. **A registration-posture report** that states whether routine registration and wrapper/runtime alignment are explicit and reviewable.
3. **A DLL-load-contract report** that says how compiled code is actually located and loaded inside the package.
4. **An install-posture report** that says whether users are likely getting CRAN binaries, a source build with Cargo/toolchain work, or a mixed/manual-review situation.
5. **A diffable release bundle** that makes registration, naming, and install-support drift visible across releases.

## Three first-class review objects

### 1. Registration posture

This should stay separate from “the generated wrappers exist”.

Named classes for `0.1`:
- `registered_contract_ok`
- `registration_posture_review_required`
- `wrapper_export_drift`
- `manual_review_required`

This object should answer:
- whether native routines are registered explicitly,
- whether `useDynLib(..., .registration = TRUE)` or equivalent runtime expectations are aligned,
- whether wrappers appear to reference the expected symbols,
- and whether the package is still leaning on ambiguous runtime lookup assumptions.

### 2. DLL load contract

This should answer questions like:
- whether compiled code is loaded via `useDynLib`, `.onLoad` + `library.dynam`, or another explicit path,
- whether package name, DLL/shared-object base name, and wrapper layer still agree,
- whether `src/entrypoint.c` and the installed `libs/` layout match the claimed load story,
- and whether there is obvious drift after crate/lib/package renames.

### 3. Install posture

This should stop the product from treating “the package compiled once” as enough.
It should say explicitly:
- whether downstream users are realistically expected to receive CRAN binaries for major OS/R-series combinations,
- whether installation still implies local compiled-code toolchain work,
- whether Cargo/rustc are part of the installation contract,
- and whether staged-install or temp-path assumptions need explicit review.

## Recommended `0.1` command surface

### `cargo rpkg-ship inspect`
Read project facts from `DESCRIPTION`, `NAMESPACE`, generated wrappers, `src/entrypoint.c`, `src/Makevars*`, Cargo metadata, and built artifacts.
Emit early observations without pretending the release is valid yet.

### `cargo rpkg-ship check`
Run policy checks for:
- missing or ambiguous registration posture,
- wrapper/export drift,
- package/lib/module naming mismatches,
- missing or unclear DLL load paths,
- Cargo/toolchain-required install posture,
- staged-install/manual-review boundaries.

### `cargo rpkg-ship diff <old> <new>`
Compare release bundles and classify:
- `registration_posture_changed`
- `dll_load_contract_changed`
- `install_posture_changed`
- `wrapper_surface_changed`
- `toolchain_requirement_changed`
- `manual_review_boundary_changed`

### `cargo rpkg-ship bundle`
Produce one compact `.rpkgbundle.zip` containing normalized receipts plus a short summary.

## Recommended crate/workspace split

- `rpkg_ship_model`
  - shared types for policies, receipts, reports, and diffs
- `rpkg_ship_import`
  - R package metadata parsing, wrapper import, entrypoint inspection, artifact inventory import
- `rpkg_ship_check`
  - policy checking and conservative classification
- `rpkg_ship_render`
  - markdown summaries and zip bundle export
- `cargo-rpkg-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `rpkg_ship_cran_index`
- `rpkg_ship_extendr_import`
- `rpkg_ship_rextendr_import`

## `0.1` artifact set

Core artifacts should be:
- `rpkg-shipkit.toml`
- `native-registration.report.json`
- `dll-load-contract.report.json`
- `install-posture.report.json`
- `build-toolchain.receipt.json`
- `support-risk.report.json`
- `notes.md`

This pass says `0.1` also needs one sharper support artifact:
- `wrapper-surface.receipt.json`

That matters because the shipkit gets vague again if it only records package metadata and compiled artifacts without making clear whether the generated R wrapper surface still matches the compiled Rust module/export story.

## Discovery order

1. **Package metadata inspection**
   - DESCRIPTION
   - SystemRequirements
   - package name and R-version family
2. **Wrapper and entrypoint inspection**
   - `R/` wrapper files
   - `src/entrypoint.c`
   - `src/Makevars*`
   - Cargo lib name / crate name
3. **Registration-posture receipt**
   - native routine registration
   - wrapper symbol references
   - registration/manual-review boundaries
4. **DLL-load-contract receipt**
   - `useDynLib`
   - `.onLoad` / `library.dynam`
   - installed `libs/` expectations
   - name-alignment checks
5. **Install-posture receipt**
   - source vs binary posture
   - Cargo/toolchain requirement
   - staged-install review boundary
6. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “the package installs locally” as the verdict.
A good `0.1` should keep separate:
- `registration_contract_known`
- `dll_load_contract_known`
- `install_posture_honest`
- `wrapper_surface_known`
- `toolchain_requirement_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- base R / CRAN docs on registration and loading
- `R CMD INSTALL` staged-install and compiled-code rules
- CRAN binary/source package conventions
- `extendr` / `rextendr` scaffolding and module/export substrate
- lists/examples of Rust-backed packages already on CRAN

### Do not flatten into one fake verdict
- “wrappers were generated”
- “the package compiled once”
- “a DLL/shared object exists in `libs/`”
- “CRAN can produce binaries for some users”
- “the package works on my dev machine”

## Preferred proving grounds

- a clean `extendr` / `rextendr` package whose names, registration, wrappers, and install posture line up
- a package where `crate_name` / `lib_name` drift after a rename
- a package whose practical install posture still requires local Cargo/toolchain work
- a package whose staged-install assumptions or temp-path assumptions require explicit review

## Non-goals

- not another Rust↔R binding generator
- not a generic CRAN automation or submission bot
- not a replacement for `R CMD check`
- not a promise that one successful local install implies boring support for all users

## MVP API sketch

```rust
pub enum RegistrationPostureClass {
    RegisteredContractOk,
    RegistrationPostureReviewRequired,
    WrapperExportDrift,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_registration_posture(release: &ReleaseInspection) -> Result<RegistrationPostureReport>;
pub fn evaluate_dll_load_contract(release: &ReleaseInspection) -> Result<DllLoadContractReport>;
pub fn evaluate_install_posture(release: &ReleaseInspection) -> Result<InstallPostureReport>;
pub fn write_bundle(bundle: &RpkgBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow CRAN/base-R compiled-package guidance closely.
- Follow `extendr` / `rextendr` as substrate, not as the entire product.
- Preserve `manual review required` whenever the crate cannot safely infer registration, load, or install truth.
