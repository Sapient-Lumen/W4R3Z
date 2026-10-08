---
id: P-0466
title: Python Extension Compatibility Contract ShipKit — ABI target classes, thread-support declarations, and variant-aware release bundles for PyO3 + maturin
status: idea
domains: [python, ffi, packaging, release, interoperability, ci, tooling]
last_reviewed: 2026-03-18
evidence:
  - https://pyo3.rs/v0.28.2/building-and-distribution
  - https://pyo3.rs/v0.28.2/building-and-distribution/multiple-python-versions
  - https://pyo3.rs/v0.28.2/free-threading
  - https://docs.python.org/3/howto/free-threading-extensions.html
  - https://docs.python.org/3/whatsnew/3.14.html
  - https://www.maturin.rs/changelog.html
  - https://github.com/PyO3/maturin/issues/3064
  - https://cibuildwheel.pypa.io/en/stable/options/
  - https://peps.python.org/pep-0803/
  - https://peps.python.org/pep-0825/
---

# Problem

Rust already has serious Python substrate. PyO3 documents a real build-and-distribution story, maturin can build and publish wheels across major platforms, and `abi3` remains a genuine compatibility target for ordinary CPython releases. PyO3 also now treats free-threaded support as a first-class surface rather than an odd experimental corner. citeturn324357view5turn377112view1

But ordinary teams still do too much release work by hand:

- choosing between version-specific wheels and `abi3` policy is still a per-project judgment call,
- free-threaded CPython created a second compatibility axis that is **not** the same as the old Stable ABI story,
- current tooling can produce wheels without making the project’s exact compatibility promise easy to review,
- accepted future work like `abi3t` and wheel variants means today’s packaging assumptions are still moving,
- and downstream reviewers still lack one compact artifact answering “what exactly are we promising users, and what is still manual-review territory?”

Python’s own docs make the seam sharper now:

- Python 3.14 says free-threaded Python is officially supported, not merely experimental; citeturn404209view3
- but the extension HOWTO still says the free-threaded build does **not currently** support the Limited C API or stable ABI, so separate wheels are still required today; citeturn790458view1
- PyO3’s current guide says modules can explicitly opt out of free-threaded support with `gil_used = true`, and since 0.28 the default assumption is thread-safe unless the crate says otherwise; citeturn377112view1turn790458view2
- maturin already has concrete free-threading support and recent policy changes, but it still has open March 2026 work for `abi3.abi3t` wheels; citeturn324357view2turn596666view1
- and accepted Python packaging work now includes both **PEP 803 (`abi3t`)** and **wheel variants**, so a serious shipkit should make future-compatibility posture explicit instead of pretending the current tag world is permanent. citeturn404209view2turn790458view0turn404209view0

The missing crate is not another binding generator and not a new package uploader.

The missing crate is a **shipkit** that turns PyO3 + maturin output into a reviewable compatibility contract: ABI target class, interpreter matrix, wheel tags, repair steps, free-threading declarations, and future-surface posture.

# What it provides

- `pyext-policy.toml` — declares intended compatibility policy, publication scope, and review boundaries.
- `interpreter-matrix.json` — CPython / PyPy / GraalPy / free-threaded matrix with supported versions and unsupported combinations.
- `wheel-matrix.json` — every built wheel with target triple, tag set, checksum, and upload intent.
- `abi-target.report.json` — explicit classification of `version_specific`, `abi3`, split free-threaded, or `abi3t`-horizon posture.
- `thread-support.report.json` — `gil_used` posture, PyO3 free-threading declaration, and manual-review hotspots.
- `repair.receipt.json` — auditwheel/delocate-style repair steps, bundled libraries, and unresolved caveats.
- `variant-horizon.report.json` — whether `abi3t` and wheel-variant evolution are out-of-scope, planned, implemented, or blocked on tooling.
- `release.receipt.json` — exact Cargo, PyO3, maturin, Python, and platform-toolchain versions used for a release.
- `cargo pyext-ship inspect` — inventory project policy and PyO3/maturin posture.
- `cargo pyext-ship matrix` — import and normalize a wheel matrix from local or CI artifacts.
- `cargo pyext-ship verify` — check policy mismatches, free-threading caveats, and overclaims.
- `cargo pyext-ship diff` — classify changes between releases.
- `*.pywheelbundle.zip` — portable bundle for review, CI, or release signoff.

# What the crate should provide other people

1. **A boring release contract** for Python wheels built from Rust.
2. **A machine-readable ABI target class** instead of tribal knowledge about `abi3`, version-specific wheels, and free-threaded splits.
3. **A clean thread-support declaration** that does not confuse “loads on a free-threaded interpreter” with “is safe without a GIL.”
4. **A matrix artifact** reviewers can inspect without re-running a whole release pipeline.
5. **A variant-horizon report** that keeps accepted future surfaces visible without overclaiming present support.
6. **A path for CI and package publishing tools** to exchange the same compatibility story.

# Persona / who it’s for

- maintainers shipping Rust-backed Python packages
- SDK teams exposing Rust functionality into Python ecosystems
- release engineers and CI maintainers
- reviewers who need to sign off on cross-platform Python releases
- downstream integrators who need a compact support promise

# Users & user stories

- **PyO3 maintainer**: “Tell me whether this crate should be `abi3`, version-specific, or split across free-threaded wheels.”
- **Release engineer**: “Show me every wheel we built, what tag it carries, and whether any repair step changed the artifact.”
- **Reviewer**: “Explain whether this extension declares free-threaded safety or opts out with `gil_used = true`.”
- **Downstream integrator**: “Give me one receipt that says which interpreters and platforms are actually supported right now.”
- **Future-proofing owner**: “Tell me whether `abi3t` is deliberately out-of-scope, blocked on tooling, or planned.”

# Prior art (and why it’s insufficient)

- PyO3 explains how to build and distribute Rust-backed Python modules, including multiple-version support and free-threaded guidance. citeturn324357view5turn377112view1
- maturin is the best current boring build/publish substrate for many Rust-Python projects. citeturn324357view2
- cibuildwheel already handles large wheel matrices, including free-threaded selectors. citeturn324357view3turn790458view4
- Python documents both the Stable ABI story and the fact that free-threaded extension builds currently need a separate path. citeturn790458view1
- Python has accepted `abi3t` and wheel-variant work, but tool support and ordinary release practice are still catching up. citeturn404209view2turn790458view0turn404209view0

What remains missing is a **maintainer-facing coordination layer**: the thing that collects ABI class, wheel tags, thread-support declarations, repair steps, interpreter coverage, and future-surface posture into a single reviewable artifact.

# Design goals

1. **Policy-first** — force the crate to say what compatibility promise it is making.
2. **Threading-honest** — never flatten “free-threaded support” into mere loadability.
3. **Matrix-aware** — wheel families must be first-class, not hidden inside CI logs.
4. **Future-aware** — keep `abi3t` / wheel-variant posture explicit without pretending those surfaces are already solved.
5. **Packager-neutral** — work with maturin-first flows without hard-coding a single CI vendor.
6. **Reviewable** — produce outputs humans can sign off on before upload.

# MVP surface

- Minimal types: `PyExtPolicy`, `InterpreterMatrix`, `WheelReceipt`, `AbiTargetReport`, `ThreadSupportReport`, `RepairReceipt`, `VariantHorizonReport`, `PyWheelBundle`
- Minimal functions:
  - `inspect_project()`
  - `collect_wheel_matrix()`
  - `classify_abi_target()`
  - `evaluate_thread_support()`
  - `evaluate_variant_horizon()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `maturin`
  - `repair`
  - `free-threading`

# Compatibility story

- Must be useful for classic CPython wheels even when free-threading is out of scope.
- Must remain useful as `abi3t` / wheel-variant tooling evolves, because the policy/receipt layer still matters.
- Should tolerate projects using PyO3 directly or through maturin.
- Should preserve “manual review required” whenever the crate cannot infer thread-safety or wheel policy safely.
- Must keep “can build”, “can load”, and “declares free-threaded safety” distinct.

# Conformance & fixtures

- One version-specific CPython-only extension fixture.
- One `abi3` fixture spanning multiple CPython versions.
- One split release fixture with `abi3` plus `cp314t` wheels.
- One `gil_used = true` fixture showing free-threaded opt-out.
- One `abi3t` horizon fixture that is policy-aware but tooling-blocked.
- Goldens for `abi3`, `version_specific`, `split_free_threaded`, `gil_required_opt_out`, `abi3t_horizon`, and `manual_review_required`.

# Path to boring stability

- Stabilize the policy and receipt vocabulary before adding upload automation.
- Start with inspection + matrix normalization + bundle export.
- Treat thread-support declarations and future-surface posture as evidence, not magic.
- Add publication helpers only after the review artifact is trusted.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that inspect a PyO3 project, classify its ABI target class, normalize the built wheel matrix, surface thread-support declarations, keep `abi3t` / variant posture explicit, and export one shareable release bundle.

# De-risk plan

1. Start with read-only inspection and bundle export.
2. Focus on CPython + PyO3 + maturin first.
3. Treat free-threading as explicit split-policy evidence, not a silent extension of `abi3`.
4. Keep `abi3t` and wheel variants as future-aware policy surfaces before they become full automation surfaces.

# Non-goals

- Not a replacement for PyO3 or maturin.
- Not a new Python package index client.
- Not a promise that `abi3`, free-threaded support, and `abi3t` are interchangeable.
- Not a generic FFI abstraction layer for all languages.
- Not a silent uploader that hides compatibility-policy questions.

# Architecture & API sketch

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

Bundle draft: `pyext-policy.toml`, `interpreter-matrix.json`, `wheel-matrix.json`, `abi-target.report.json`, `thread-support.report.json`, `repair.receipt.json`, `variant-horizon.report.json`, `release.receipt.json`, `notes.md`.

# Security / safety model

- Never claim wheel compatibility that packaging metadata cannot justify.
- Never claim free-threaded safety merely because a wheel loads.
- Record exact Python, Cargo, PyO3, maturin, and repair-tool versions used.
- Preserve explicit manual-review zones for thread-safety, native dependency repair, and future-surface posture.
- Support redaction of environment-specific paths and credentials in release notes/bundles.

# Maintenance / stewardship questions

- Track PyO3, maturin, cibuildwheel, `abi3t`, and wheel-variant guidance closely.
- Maintain fixtures for `abi3`, version-specific, split free-threaded, and future-aware-but-blocked releases.
- Publish guidance for interpreting thread-support declarations conservatively.
- Keep diff output stable enough for CI and human review.

# Keywords

- PyO3
- maturin
- cibuildwheel
- abi3
- abi3t
- free-threading
- wheel matrix
- compatibility contract
- release bundle

# Open questions

- Which repair facts matter most for reviewers: bundled libs, stripped symbols, manylinux policy, or all three?
- How much thread-support posture can be inferred automatically versus requiring maintainer annotation?
- How should the bundle express “planned when tooling ready” without encouraging overclaims?

# Sources

- PyO3 building and distribution: https://pyo3.rs/v0.28.2/building-and-distribution
- PyO3 multiple Python versions / `abi3`: https://pyo3.rs/v0.28.2/building-and-distribution/multiple-python-versions
- PyO3 free-threading guide: https://pyo3.rs/v0.28.2/free-threading
- Python free-threaded extension HOWTO: https://docs.python.org/3/howto/free-threading-extensions.html
- What’s new in Python 3.14: https://docs.python.org/3/whatsnew/3.14.html
- maturin changelog: https://www.maturin.rs/changelog.html
- maturin issue 3064 (`abi3.abi3t` work): https://github.com/PyO3/maturin/issues/3064
- cibuildwheel options: https://cibuildwheel.pypa.io/en/stable/options/
- PEP 803: https://peps.python.org/pep-0803/
- PEP 825: https://peps.python.org/pep-0825/
