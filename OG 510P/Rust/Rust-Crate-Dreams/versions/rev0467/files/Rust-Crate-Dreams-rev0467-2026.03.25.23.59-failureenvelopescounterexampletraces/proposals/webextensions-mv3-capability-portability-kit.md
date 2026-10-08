---
id: P-0399
title: WebExtensions MV3 Capability Portability Kit — manifest locks, permission/API coverage diffs, and cross-browser evidence bundles
status: idea
domains: [web, browser, wasm, tooling, portability, validation, security]
last_reviewed: 2026-03-06
evidence:
  - https://w3c.github.io/webextensions/specification/
  - https://www.w3.org/community/webextensions/
  - https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Build_a_cross_browser_extension
  - https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Chrome_incompatibilities
  - https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3
  - https://docs.rs/web-extensions-sys/latest/i686-pc-windows-msvc/web_extensions_sys/
---

# Problem

Browser-extension portability is no longer a purely ad hoc problem. The WebExtensions Community Group has an active common-core specification effort, the major browsers have adopted Manifest V3, and the compatibility story is better than it used to be — but still not boring. In practice, extension authors still hit real drift around permissions, API availability, service-worker behavior, declarative rules, and store/runtime differences.

Rust already has some substrate here. `web-extensions-sys` and `web-extensions` provide bindings for extension APIs in a WASM-friendly direction, but they are explicitly Chrome-oriented today. The painful failures still happen at the seam between:

- **what a manifest declares and what a browser/runtime/store actually accepts**,
- **the common-core WebExtensions model and browser-specific API or permission differences**,
- **Chrome-centric MV3 assumptions and Firefox/Safari divergence**,
- **generated bindings and the real capability matrix a given extension depends on**,
- and **debugging that still happens through store upload attempts, browser consoles, and tribal knowledge.**

The missing Rust contribution is not another extension framework. It is a **portability kit** for manifest locks, capability matrices, permission/API coverage diffs, and evidence bundles that survive handoff.

# What it provides

- `webext.lock` — pins manifest version, required permissions, optional permissions, host permissions, background model, and declared API surface.
- `capability-matrix` — explicit browser/runtime matrix for APIs, events, permission semantics, and migration notes.
- `manifest-diff` — semantic comparison of two manifests or two browser-targeted packaging variants.
- `probe-receipt` — optional runtime/static-analysis receipt describing which APIs were used, declared, denied, or unsupported.
- `cargo webext-portability` — emits `*.webextbundle.zip` with locks, coverage, findings, and notes.

# What the crate should provide other people

1. **A boring portability receipt for cross-browser extension work**.
2. **Semantic manifest diffs** instead of line-by-line JSON comparison.
3. **Permission/API coverage matrices** tied to real target browsers.
4. **A way to pin what a Rust/WASM extension actually relies on**.
5. **A safer path to MV3 migration and multi-browser release hygiene.**

# Persona / who it’s for

- Rust/WASM extension authors
- Teams shipping one extension to multiple browser ecosystems
- QA/release engineers validating manifest/API portability
- Maintainers of Rust bindings and browser-facing SDK layers

# Users & user stories

- **Extension author**: “Show me whether the portability bug is the manifest, permissions, service-worker model, or missing API support.”
- **Release engineer**: “Compare our Chrome-targeted and Firefox-targeted packages semantically, not just textually.”
- **Binding maintainer**: “Pin which subset of APIs my Rust crate actually covers and where it is Chrome-only.”
- **Security reviewer**: “See a compact receipt of requested permissions, optional permissions, and unsupported APIs.”

# Prior art (and why it’s insufficient)

- The WECG is building the common-core specification surface.
- MDN and browser-vendor docs explain compatibility and migration.
- Rust has early bindings for Chrome-oriented WebExtension APIs.

What Rust still lacks is an **evidence-grade coordination layer** for semantic manifest diffs, target matrices, permission/API coverage, and release-ready portability receipts.

# Design goals

1. **Browser-matrix explicit** — compatibility cannot be implied.
2. **Manifest semantics first** — compare meaning, not raw JSON formatting.
3. **Static-first, runtime-optional** — useful before full browser harness integration.
4. **Rust/WASM friendly** — align with the actual Rust extension substrate.
5. **Store/runtime honest** — separate browser runtime behavior from packaging/store acceptance.

# MVP surface

- Minimal types: `WebExtLock`, `CapabilityMatrix`, `ManifestFinding`, `ProbeReceipt`, `WebExtBundle`
- Minimal functions:
  - `load_manifest()`
  - `diff_manifests()`
  - `build_capability_matrix()`
  - `write_bundle()`
- Feature flags:
  - `mv3`
  - `static-analysis`
  - `runtime-probes`
  - `chrome`
  - `firefox`
  - `safari`

# Compatibility story

- Starts as a manifest and API-usage workbench, even before deep runtime adapters exist.
- Can consume Rust-generated manifests, hand-written manifests, or multiple target variants.
- Keeps browser-specific findings namespaced and explicit.
- Can integrate later with `web-extensions(-sys)`, `wasm-bindgen`, and automated browser harnesses.

# Conformance & fixtures

- Goldens for manifest migrations, permission changes, host-permission narrowing, service-worker/background differences, and API-coverage drift.
- Tiny fixtures for browser-specific incompatibilities and unsupported APIs.
- Public mini-corpus of MV3-targeted extension examples.
- Optional runtime probe fixtures that record denied or unavailable APIs.

# Path to boring stability

- Stabilize the lockfile, semantic manifest diff, and capability matrix schema first.
- Start with static analysis and browser matrices before runtime probes.
- Keep browser-specific overlays versioned and clearly separated.
- Resist scope creep into becoming a full extension framework or store deployer.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A Rust library and CLI that pin extension assumptions, compute semantic manifest diffs, generate browser capability matrices, and emit compact `*.webextbundle.zip` artifacts.

# De-risk plan

1. Start with MV3 manifest semantics and static browser matrices.
2. Keep runtime probes optional and adapter-based.
3. Use small, public extension examples as goldens.
4. Treat browser/store differences as overlays, not one blended “compatibility score.”

# Non-goals

- Not an extension framework.
- Not a browser automation framework.
- Not a store deployment pipeline.
- Not a general web build system.

# Architecture & API sketch

```rust
pub struct WebExtLock {
    pub manifest_version: u8,
    pub required_permissions: Vec<String>,
    pub optional_permissions: Vec<String>,
    pub target_browsers: Vec<String>,
}

pub fn load_manifest(path: &std::path::Path) -> Result<WebExtLock>;
pub fn diff_manifests(a: &WebExtLock, b: &WebExtLock) -> Vec<ManifestFinding>;
pub fn build_capability_matrix(lock: &WebExtLock) -> CapabilityMatrix;
```

Bundle draft: `webext.lock`, `manifest.json`, `capability-matrix.json`, `findings.json`, `notes.md`.

# Security / safety model

- Make requested permissions and host permissions first-class findings.
- Support redaction of internal IDs, endpoints, or packaging metadata.
- Separate static claims from runtime-proven behavior.
- Keep bundle scope tight enough for code review and release gating.

# Maintenance & governance plan

- Keep the core about locks, diffs, matrices, and receipts.
- Version browser overlays explicitly as compatibility changes land.
- Publish a tiny public corpus of cross-browser extension fixtures.
- Avoid drifting into whole-app scaffolding.

# Milestones

## 0.1
- `webext.lock`
- semantic manifest diff
- browser capability matrix

## 0.2
- API-usage analysis
- runtime probe adapters
- public MV3 fixture corpus

## 1.0
- stable `*.webextbundle.zip`
- documented compatibility policy for browser overlays
- CI-friendly gating outputs

# Open questions

- Which browser compatibility data sources should be treated as normative versus informational?
- How much runtime probing is needed before the tool becomes materially more useful than static analysis?
- How should store-upload findings be modeled without binding the core to one vendor workflow?

# Sources

- WebExtensions specification draft: https://w3c.github.io/webextensions/specification/
- W3C WebExtensions Community Group: https://www.w3.org/community/webextensions/
- MDN cross-browser extension guide: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Build_a_cross_browser_extension
- MDN Chrome incompatibilities: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Chrome_incompatibilities
- Chrome Manifest V3 overview: https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3
- `web-extensions-sys`: https://docs.rs/web-extensions-sys/latest/i686-pc-windows-msvc/web_extensions_sys/
