# Python Wheel ABI & Free-Threading ShipKit — product plan (2026-03-18)

This note sharpens **P-0466 Python Wheel ABI & Free-Threading ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which interpreters and wheel tags they actually built,
- which ABI target class the release is claiming,
- whether the extension is declaring free-threaded support or opting out,
- what repair or packaging steps changed the artifact,
- which wheel families are upload-ready versus review-only,
- and whether future `abi3t` / wheel-variant work affects the release policy.

It should **not** try to become a replacement for PyO3, maturin, cibuildwheel, auditwheel, delocate, or package indexes.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For maintainers, release engineers, and reviewers, the crate should provide:

1. **One compact compatibility contract** instead of compatibility folklore spread across CI YAML, `pyproject.toml`, Cargo features, and issue threads.
2. **An ABI target report** that states whether the release is version-specific, `abi3`, split free-threaded, or on an `abi3t` horizon.
3. **A thread-support declaration** that keeps `gil_used`, free-threading opt-in/opt-out, and manual-review boundaries visible.
4. **A wheel matrix artifact** with exact tags, interpreter families, platform tags, and upload intent.
5. **A repair receipt** that records if auditwheel/delocate-like steps changed the wheel.
6. **A variant-horizon report** that explicitly says whether accepted future surfaces like `abi3t` and wheel variants are out-of-scope, planned, or already gated.
7. **A diffable release bundle** another person can review without rerunning CI.
8. **A conservative summary** for downstream users explaining what can be installed directly versus what still needs source builds or manual review.

## Three first-class review objects

### 1. ABI target class
This should stay separate from “whatever wheel tags happened to fall out of CI.”

Named classes for `0.1`:
- `version_specific`
- `abi3`
- `split_free_threaded`
- `abi3t_horizon`
- `manual_review_required`

### 2. Thread-support declaration
This should answer questions like:
- is the module explicitly declaring GIL-disabled safety?
- is it opting out with `gil_used = true`?
- are there `#[pyclass]` or `unsafe` hotspots still requiring human audit?
- does the release claim thread-safety, or only loadability?

### 3. Variant horizon
This should stop the product from hard-coding today’s tag vocabulary forever.
It should say explicitly:
- whether `abi3t` is out-of-scope, blocked on tooling, or planned,
- whether wheel-variant evolution matters to this package,
- and whether the current bundle is intentionally limited to classic wheel tags.

## Recommended `0.1` command surface

### `cargo pyext-ship inspect`
Read project facts from `Cargo.toml`, `pyproject.toml`, PyO3 features/config, and built wheels if present.
Emit early observations without pretending the release is valid yet.

### `cargo pyext-ship matrix`
Import wheel artifacts from `target/wheels`, maturin outputs, or CI outputs and normalize them into:
- `wheel-matrix.json`
- `abi-target.report.json`
- `interpreter-matrix.json`

### `cargo pyext-ship check`
Run policy checks for:
- `abi3` versus version-specific mismatch,
- free-threaded split-wheel requirements,
- thread-support declaration gaps,
- upload-unsafe wheels,
- missing repair receipts,
- and variant-horizon/manual-review warnings.

### `cargo pyext-ship diff <old> <new>`
Compare release bundles and classify:
- `abi_target_changed`
- `thread_support_changed`
- `wheel_family_added_or_removed`
- `repair_step_changed`
- `upload_scope_changed`
- `variant_horizon_changed`
- `manual_review_boundary_changed`

### `cargo pyext-ship bundle`
Produce one compact `.pywheelbundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `pyext_ship_model`
  - shared types for policies, matrices, receipts, and diffs
- `pyext_ship_import`
  - project inspection and wheel metadata parsing
- `pyext_ship_check`
  - policy checking and conservative classification
- `pyext_ship_render`
  - markdown summaries and zip bundle export
- `cargo-pyext-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `pyext_ship_maturin`
- `pyext_ship_cibuildwheel`
- `pyext_ship_repair`

## `0.1` artifact set

Core artifacts should be:
- `pyext-policy.toml`
- `interpreter-matrix.json`
- `wheel-matrix.json`
- `repair.receipt.json`
- `release.receipt.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `abi-target.report.json`
- `thread-support.report.json`
- `variant-horizon.report.json`

Those matter because the shipkit gets vague again if it only records “a wheel exists” without making clear:
- what compatibility class was intended,
- whether free-threaded support was declared or merely load-tested,
- and whether accepted future packaging surfaces should still stay manual-review-only.

## Discovery order

1. **Project inspection**
   - PyO3 features
   - `pyproject.toml`
   - maturin backend posture
   - built wheel inventory
2. **ABI classification**
   - version-specific vs `abi3`
   - split free-threaded policy
   - `abi3t` horizon flag
3. **Thread-support declaration**
   - `gil_used`
   - free-threaded support claim
   - manual-review hotspots
4. **Wheel matrix normalization**
   - python tags
   - abi tags
   - platform tags
   - upload intent
5. **Repair / publication checks**
   - repair receipts
   - reproducibility notes
   - policy mismatches
6. **Variant horizon check**
   - accepted but not yet implemented future surfaces
   - “do not silently overclaim” notes
7. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “wheel built successfully” as the verdict.
A good `0.1` should keep separate:
- `build_succeeded`
- `abi_target_classified`
- `thread_support_declared`
- `repair_receipt_present`
- `upload_scope_clear`
- `future_surface_out_of_scope`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- PyO3 `abi3` and free-threading configuration
- maturin wheel outputs and changelog reality
- cibuildwheel selector behavior
- Python’s stable-ABI and free-threading docs
- accepted `abi3t` / wheel-variant work

### Do not flatten into one fake verdict
- “can compile”
- “can load”
- “declared thread-safe”
- “`abi3` today”
- “`abi3t` tomorrow”
- “upload-ready”

## Preferred proving grounds

- a project shipping ordinary `abi3` wheels for CPython plus separate `cp314t` wheels
- a project that deliberately opts out of free-threaded safety with `gil_used = true`
- a project that wants to track `abi3t` but must keep it policy-only until tooling catches up
- a project where repair/bundling changes wheel contents after the raw build

## Non-goals

- not a replacement for PyO3 or maturin
- not a package index client
- not a universal FFI framework
- not a promise that accepted future packaging PEPs are already usable everywhere
- not a silent “best possible” uploader for every Python backend

## MVP API sketch

```rust
pub enum AbiTargetClass {
    VersionSpecific,
    Abi3,
    SplitFreeThreaded,
    Abi3tHorizon,
    ManualReviewRequired,
}

pub fn inspect_project(root: &Path) -> Result<ProjectInspection>;
pub fn collect_wheel_matrix(root: &Path) -> Result<Vec<WheelReceipt>>;
pub fn classify_abi_target(project: &ProjectInspection, wheels: &[WheelReceipt]) -> AbiTargetClass;
pub fn evaluate_thread_support(project: &ProjectInspection) -> Result<ThreadSupportReport>;
pub fn evaluate_variant_horizon(project: &ProjectInspection) -> Result<VariantHorizonReport>;
pub fn write_bundle(bundle: &PyWheelBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow PyO3 free-threading guidance closely.
- Follow Python extension-build guidance for stable ABI versus free-threaded splits.
- Track maturin and cibuildwheel packaging-policy changes.
- Keep `abi3t` support policy-aware before it is automation-aware.
- Preserve “manual review required” whenever the crate cannot safely infer thread-safety or future compatibility policy.
