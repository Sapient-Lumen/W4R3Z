---
id: P-0491
title: Debugger Visualizer Compatibility Kit — NatVis/GDB conformance receipts, backend-support matrices, and embed-vs-external diagnosis bundles
status: idea
domains: [debugging, devtools, gdb, natvis, lldb, ci]
last_reviewed: 2026-03-22
evidence:
  - https://doc.rust-lang.org/reference/attributes/debugger.html
  - https://rustc-dev-guide.rust-lang.org/debuginfo/debugger-visualizers.html
  - https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  - https://rustc-dev-guide.rust-lang.org/debuginfo/intro.html
  - https://lldb.llvm.org/use/variable.html
  - https://lldb.llvm.org/use/lldbdap.html
  - https://learn.microsoft.com/en-us/visualstudio/debugger/create-custom-views-of-native-objects?view=visualstudio
  - https://sourceware.org/gdb/current/onlinedocs/gdb.html/Writing-a-Pretty_002dPrinter.html
  - https://rustc-dev-guide.rust-lang.org/tests/compiletest.html
---

# Problem

Rust now has enough real debugger-visualizer substrate that this proposal should stop sounding like “some day we should automate debuggers better.”

The upstream story is already concrete:

- `#[debugger_visualizer]` is a stable language feature,
- the Rust reference documents two first-class asset families: **NatVis** and **GDB pretty-printer scripts**,
- NatVis embedding is explicitly limited to `-windows-msvc` targets,
- and the same reference explicitly warns that embedded GDB pretty printers are **not auto-loaded by default** unless the binary or directory is trusted via GDB’s auto-load safe-path configuration.
- LLDB’s official formatter model is command/script driven rather than a Rust-embedded visualizer lane, which makes an explicit `external_formatter_route` policy lane honest rather than apologetic.

That means ordinary maintainers still cannot answer several release-review questions cleanly:

- which debugger/backend combinations are intended to work,
- which ones are unsupported **by design** versus merely untested,
- whether a failure came from the asset, the debugger’s safe-path/autoload policy, or broader debuginfo posture,
- whether a backend only works through an external-formatter/manual-install route,
- whether a backend drifted because the embed/activation route changed rather than the asset itself,
- and how the visualizer story changed between two releases.

The archive already has adjacent ideas:

- **P-0486 Debuggability Support Contract Kit** is about the broad support posture / sidecar / debuginfo story,
- **P-0493 Source Path Hygiene & Debug Source Kit** is about source lookup and remapping,
- **P-0083 Debugger UX Kit** is about broader formatter-pack/doctor ambition.

What remains missing is a narrower **compatibility and conformance layer for visualizer assets themselves**.

# What it provides

- `visualizer-policy.toml` — intended debugger families, supported target triples, expected probe lanes, safe-path assumptions, and explicit unsupported-by-design declarations.
- `visualizer-assets.manifest.json` — embedded assets, external companion assets, attachment points, hashes, and provenance.
- `backend-matrix.receipt.json` — debugger/backend attempts with verdicts like `supported`, `unsupported_by_design`, `safe_path_blocked`, `asset_failed`, `backend_failed`, or `manual_review_required`.
- `activation-route.receipt.json` — how a visualizer was expected to become active for a backend lane, including safe-path and external-script realities.
- `formatter-origin.receipt.json` — which asset, wrapper, or debugger-local formatter setup is actually the effective origin for that lane.
- `render-golden.report.json` — normalized expected-vs-observed rendering for a small set of fixture values.
- `embed-vs-external.report.json` — which backends use embedded assets, which require an external formatter route, and which remain manual-review-only.
- `probe-surface.receipt.json` — which debugger surface, version, OS class, and delivery route were actually observed.
- `comparison-basis.receipt.json` — whether two visualizer observations are comparable, partially comparable, or not honestly comparable.
- `visualizer-support-bundle.manifest.json` — portable bundle that keeps policy, assets, activation route, formatter origin, probe surface, comparison basis, backend verdicts, and drift separate.
- `visualizer-drift.diff.json` — release-to-release or toolchain-to-toolchain compatibility changes.
- `cargo visualizer-compat capture` — capture manifests and policy context from a project.
- `cargo visualizer-compat probe` — run a conservative probe against configured debuggers and goldens.
- `cargo visualizer-compat diff <old> <new>` — compare two compatibility bundles.
- `*.vizcompat.zip` — portable review/support artifact.

# What the crate should provide other people

1. **A stable vocabulary** for what a crate’s visualizer assets are actually trying to support.
2. **A compact compatibility bundle** instead of debugger screenshots, tribal knowledge, and “works on my debugger” claims.
3. **An honest safe-path/autoload lane** so GDB policy failures are not misreported as broken assets.
4. **An activation-route receipt** so GDB safe-path refusal, toolchain support scripts, and manual command routes stop being flattened into generic asset failure.
5. **A formatter-origin receipt** so a crate can say whether the effective visualization came from its own asset, a toolchain wrapper, or debugger-local configuration.
6. **A probe-surface receipt** so backends, frontends, delivery containers, and host-version assumptions stop being implicit.
7. **A comparison-basis receipt** so two visualizer observations are not over-read as equivalent when they came from different debugger surfaces.
8. **A conservative embed-vs-external distinction** so maintainers can say when a backend needs external formatter setup rather than pretending parity exists.
9. **A diffable release-review surface** for debugger regressions that are otherwise easy to miss.

# Persona / who it’s for

- library and application maintainers shipping Rust artifacts with debugger visualization support
- release engineers who want debugger regressions caught in CI
- teams supporting Windows/MSVC plus GDB-heavy workflows
- debugger-tooling authors who need a machine-readable compatibility artifact

# Users & user stories

- **Maintainer**: “Show me whether our embedded NatVis and GDB assets still work after the toolchain or debugger upgrade.”
- **Reviewer**: “Tell me whether this release changed the visualizer story or only the broader symbol/debuginfo story.”
- **Support engineer**: “Was this a broken asset, an untrusted GDB auto-load path, an unsupported backend, or a broader debug-support problem?”
- **Tool author**: “I need one matrix that says which backends are supported by embedded assets and which require external/manual setup.”

# Prior art (and why it’s insufficient)

- The Rust reference documents `#[debugger_visualizer]`, but that is a language surface, not a review artifact.
- GDB documents auto-load safe-path rules, but that is debugger policy substrate, not a crate-maintainer receipt.
- Rust release notes establish that debugger visualizers are mainstream substrate now, but do not give maintainers a backend matrix or drift story.
- LLDB documents summary/synthetic/data formatter workflows, but that is external-formatter substrate, not a Rust-embedded compatibility receipt.
- Existing formatter packs and debugger doctors focus on installation or broader debugging ergonomics, not on **release-reviewing the visualizer assets a crate already ships**.

What remains missing is a **visualizer compatibility receipt** that says what assets exist, which backends they target, what rendered correctly, what required trust/config, and how that changed.

# Design goals

1. **Visualizer-first** — focus on visualizer assets and their concrete outcomes, not the whole debugger platform.
2. **Backend-explicit** — make unsupported-by-design and external-only lanes first-class.
3. **Safe-path-aware** — distinguish GDB policy refusal from a bad pretty-printer asset.
4. **Surface-explicit** — keep CLI, DAP, IDE, wrapper, and delivery-route facts visible.
5. **Golden-friendly** — a small set of rendered values should be comparable in CI.
6. **Adjacent-but-separate** — integrate with P-0486/P-0493 vocabulary without collapsing into them.
7. **Honest uncertainty** — keep `manual_review_required` whenever probing or normalization would be brittle.

# MVP surface

- Minimal types: `VisualizerPolicy`, `VisualizerAssetManifest`, `BackendMatrixReceipt`, `RenderGoldenReport`, `EmbedVsExternalReport`, `VisualizerDrift`, `VisualizerCompatBundle`
- Minimal functions:
  - `capture_visualizer_assets()`
  - `probe_backend_matrix()`
  - `compare_render_goldens()`
  - `classify_embed_vs_external()`
  - `diff_visualizer_receipts()`
- Feature flags:
  - `natvis`
  - `gdb`
  - `external-backends`
  - `serde`
  - `markdown`

# Compatibility story

- Must understand embedded NatVis and GDB-script assets from stable Rust source.
- Must record that NatVis embedding is only documented for `-windows-msvc` targets.
- Must record when GDB support is blocked by auto-load/safe-path policy instead of silently calling the asset broken.
- Must keep explicit room for `external_formatter_route` because LLDB-style formatter support is real substrate even when Rust-embedded assets are not the delivery vehicle.
- Should import broad support facts from a P-0486-style receipt when available, but should still stand alone.
- Should model non-reference backends conservatively as `external_formatter_route`, `unsupported_by_design`, or `manual_review_required` unless better evidence exists.

# Conformance & fixtures

- fixture crate with embedded NatVis on `x86_64-pc-windows-msvc`
- fixture crate with embedded GDB pretty-printer script where safe-path setup is missing
- fixture crate where backend policy intentionally routes one debugger family through an external formatter lane
- fixture where debuginfo exists but the visualizer asset is malformed or missing
- goldens for `supported`, `unsupported_by_design`, `safe_path_blocked`, `asset_failed`, `backend_failed`, and `manual_review_required`

# Path to boring stability

- Freeze the backend verdict vocabulary before adding many backend adapters.
- Start with asset discovery + small conformance probing + diff.
- Keep render goldens tiny and value-oriented.
- Treat non-reference backends as explicit external/manual lanes first.
- Treat safe-path/autoload facts as first-class evidence, not as a debugging footnote.

# 2026-03-22 artifact-completeness addendum

The next credible implementation step for **P-0491** is no longer “probe more backends”.
It is to keep five additional truths reviewable:

1. **activation route** — embedded autoload, safe-path refusal, toolchain wrapper, debugger-local config, manual commands, or unsupported-by-design;
2. **formatter origin** — whether the effective formatter came from a repo-embedded asset, a repo-shipped external script, a toolchain support launcher such as `rust-lldb`, or debugger-local configuration;
3. **probe surface** — which debugger family, frontend surface, version, OS class, and delivery container were actually observed;
4. **comparison basis** — whether two observations are honestly comparable or only partially comparable because the frontend surface, delivery route, or formatter origin changed;
5. **portable bundle completeness** — one shareable bundle that keeps policy, asset inventory, route receipts, origin receipts, probe-surface receipts, comparison-basis receipts, backend verdicts, and drift separate.

That matters because backend support is no longer one-dimensional.
A crate can ship an embedded NatVis asset, ship an embedded GDB script, rely on toolchain support scripts for LLDB-family workflows, and still need a conservative statement about which route is authoritative for each lane.

The worthy crate contribution here is therefore not just “visualizers compile”.
It is a crate that gives another engineer a **small, auditable packet** answering:
- what asset exists,
- how it was supposed to load,
- what actually provided the formatter behavior,
- and which backend verdict changed between releases.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A library and cargo subcommand that read embedded visualizer assets, record backend intent, probe a small debugger/backend matrix with normalized render goldens, and export a diffable receipt that shows whether a release still supports the intended debugger families.

# De-risk plan

1. Start with NatVis and GDB, because those are the backends explicitly documented by the language feature.
2. Model GDB safe-path refusal as its own verdict lane.
3. Keep external-backend support explicit and conservative instead of forcing fake parity.
4. Normalize only a small set of common value renderings at first.
5. Separate visualizer failures from broader symbol/debuginfo/source failures whenever possible.

# Non-goals

- Not a full debugger pretty-printer pack.
- Not a replacement for GDB/LLDB/VS integrations.
- Not a whole debuggability support contract.
- Not a promise that every debugger can be batch-probed uniformly across all platforms.
- Not an excuse to invent support claims for backends the Rust feature docs do not cover.

# Architecture & API sketch

```rust
pub enum BackendVerdict {
    Supported,
    UnsupportedByDesign,
    SafePathBlocked,
    AssetFailed,
    BackendFailed,
    ManualReviewRequired,
}

pub fn capture_visualizer_assets(root: &Path) -> Result<VisualizerAssetManifest>;
pub fn probe_backend_matrix(manifest: &VisualizerAssetManifest, policy: &VisualizerPolicy) -> Result<BackendMatrixReceipt>;
pub fn capture_probe_surface(policy: &VisualizerPolicy, backend: BackendLane) -> Result<ProbeSurfaceReceipt>;
pub fn compare_probe_surfaces(lhs: &ProbeSurfaceReceipt, rhs: &ProbeSurfaceReceipt) -> ComparisonBasisReceipt;
pub fn classify_embed_vs_external(matrix: &BackendMatrixReceipt) -> EmbedVsExternalReport;
pub fn diff_visualizer_receipts(old: &BackendMatrixReceipt, new: &BackendMatrixReceipt) -> VisualizerDrift;
```

Bundle draft: `visualizer-policy.toml`, `visualizer-assets.manifest.json`, `activation-route.receipt.json`, `formatter-origin.receipt.json`, `probe-surface.receipt.json`, `comparison-basis.receipt.json`, `backend-matrix.receipt.json`, `render-golden.report.json`, `embed-vs-external.report.json`, `visualizer-drift.diff.json`, `notes.md`.

# Security / safety model

- Treat debugger scripts and debugger batch execution as untrusted-input surfaces.
- Support offline replay of captured outputs where direct probing is not acceptable.
- Distinguish observed render outcomes from inferred support claims.
- Permit redaction of local paths or proprietary type names in exported bundles.
- Treat GDB safe-path bypasses and auto-load trust changes as explicit, auditable facts.

# Maintenance & governance plan

- Track Rust reference changes around `#[debugger_visualizer]`.
- Track GDB auto-load/safe-path behavior that affects embedded pretty-printer loading.
- Maintain a small compatibility matrix of debugger/backend versions used for conformance.
- Keep fixture corpora tiny and regression-focused.

# Why now

This got sharper, not fuzzier:

- debugger visualizers are stable substrate,
- the official Rust docs now make two awkward compatibility truths explicit (NatVis is MSVC-only; embedded GDB printers are not auto-loaded by default),
- and the 2026 Rust debugging survey shows that backend quality, visualizers, async debugging, and evaluation ergonomics are active project concerns.

So the worthy contribution is no longer “better debugger tooling” in the abstract.
It is the first boring **visualizer compatibility receipt** that another maintainer can review.

# Sources

- Rust reference: `#[debugger_visualizer]`. https://doc.rust-lang.org/reference/attributes/debugger.html
- GDB manual: auto-load safe path. https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
- Rust release notes (stabilization / mainstream substrate). https://doc.rust-lang.org/beta/releases.html
- Rust debugging survey 2026. https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- LLDB variable formatting / formatter model. https://lldb.llvm.org/use/variable.html
