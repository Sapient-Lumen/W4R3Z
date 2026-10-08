---
id: P-0498
title: Node-API Package & Prebuild Contract Kit — npm prebuild matrices, loader receipts, and runtime-claim support bundles
status: idea
domains: [nodejs, npm, bindings, ffi, packaging, distribution, ci]
last_reviewed: 2026-03-18
evidence:
  - https://nodejs.org/api/addons.html
  - https://nodejs.org/api/n-api.html
  - https://nodejs.org/en/learn/modules/abi-stability
  - https://napi.rs/
  - https://napi.rs/docs/introduction/getting-started
  - https://napi.rs/docs/cli/build
  - https://napi.rs/blog/announce-v3
  - https://nodejs.org/api/packages.html
  - https://nodejs.org/api/cli.html
  - https://docs.npmjs.com/trusted-publishers/
  - https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/
---

# Problem

Rust already has serious substrate for shipping native JavaScript addons.

Node.js officially documents **Node-API** as the ABI-stable way to build native addons. The ecosystem also now has a mature Rust-side substrate in **napi-rs**: high-level bindings, generated TypeScript definitions, a project generator, a build CLI, and a support matrix that spans common operating systems, architectures, and libc variants.

That means the ecosystem is no longer mainly missing “some way to call Rust from Node”.

But ordinary maintainers still do not have one boring artifact that answers the practical release questions:

- which **Node-API version floor** a package actually promises,
- which prebuilt `.node` artifacts were published for which runtime/platform/libc tuples,
- whether the generated JS loader and package metadata really match those artifacts,
- whether the package is honestly **prebuild-first**, **local-build fallback**, or **WASM fallback**,
- and whether broader runtime claims around Bun or Deno exceed the artifacts and loader behavior actually shipped.

The missing crate is **not** another binding generator.

The missing crate is a **Node-API package & prebuild contract kit**: a crate and cargo-adjacent tool that turns “we ship a Rust addon to npm” into a portable **prebuild-coverage report, loader-route receipt, publish-identity report, and support-risk bundle**.

# What it provides

- `nodeapi-contract.toml` — declares package name, minimum Node-API version, supported runtimes (`node`, optional `bun`, optional `deno`), target triples/libc variants, local-build policy, optional WASM fallback policy, and expected loader strategy.
- `prebuild.manifest.json` — normalized list of produced `.node` artifacts, filenames, runtime tuples, Node-API level, checksum/digest metadata, and where each artifact is expected to live in the npm package.
- `loader.receipt.json` — records generated `index.js` / loader logic, platform-detection branches, fallback order, optional-package expectations, and TypeScript binding generation facts.
- `prebuild-coverage.report.json` — classifies the release as `fully_prebuilt`, `partial_prebuild_matrix`, `native_gap_hidden_by_local_build`, `wasm_only_fallback_for_named_tuple`, or `manual_review_required`.
- `loader-route.receipt.json` — records package `exports`, `node-addons` and `default` branches, generated loader order, local-build hooks, and native/WASM route decisions.
- `publish-identity.report.json` — records trusted-publisher posture, provenance expectations, and manual/token publish facts without pretending those settle runtime support.
- `runtime-support.report.json` — conservative join across artifact coverage, loader route, and named runtime claims.
- `addon-intake.report.json` — compact support bundle for one downstream environment: runtime family, runtime version, Node-API level, OS/arch/libc tuple, loader route, and why the published package should or should not work there.
- `cargo nodeapi-contract snapshot` — capture one package contract and one produced artifact set.
- `cargo nodeapi-contract doctor` — explain whether package metadata, generated loader code, and actual prebuilds agree.
- `cargo nodeapi-contract diff <old> <new>` — compare support promises across releases.
- `*.nodebundle.zip` — portable artifact for release review, npm publish rehearsal, support tickets, or downstream runtime-compatibility debugging.

# What the crate should provide other people

1. **A boring answer to “what runtimes and platforms does this addon actually support?”** instead of npm folklore and CI YAML archaeology.
2. **A prebuild manifest** that says exactly which native artifacts were published and which tuples are still missing.
3. **A loader-route receipt** that proves the JS shim people install is aligned with the native files they receive.
4. **A publish-identity report** that keeps trusted-publisher/provenance facts visible without confusing them for runtime support.
5. **A runtime-claim contract** that keeps Node, Bun, Deno, local-build fallback, and WASM fallback stories visibly distinct.
6. **A bridge** between Node-API’s ABI promise and the much messier reality of package-manager, loader, prebuild, and publish-identity workflows.

# Persona / who it’s for

- maintainers shipping Rust addons into npm workspaces and Node monoliths
- teams using napi-rs and wanting a reviewable publish contract
- release engineers building cross-platform prebuild matrices in CI
- support engineers diagnosing “works on macOS but not Alpine” or “works on Node but not Bun” issues
- downstream consumers who need a compact runtime compatibility statement

# Users & user stories

- **Addon maintainer**: “Show me whether our published npm package actually covers every tuple we claim in release notes.”
- **Release engineer**: “Give me one bundle that joins native artifacts, generated loader logic, Node-API version policy, and support verdicts.”
- **Support engineer**: “Tell me whether this failure is a missing prebuild, wrong libc family, Node-API floor mismatch, or a loader-name problem.”
- **Runtime adopter**: “Show whether the package really supports Bun or Deno, or whether that claim is only aspirational.”

# Prior art (and why it’s insufficient)

- Node.js already documents Node-API and ABI stability.
- `napi-rs` already provides a very strong Rust-side authoring and build experience.
- npm/yarn/pnpm plus CI actions can publish native artifacts.
- The archive already has **P-0482 SDK Release Promise Drift Kit** and **P-0487 Foreign SDK Consumer Doctor Kit**.

What remains missing is the **producer-side Node package contract** that answers: “what Node-API floor, which prebuilds, what loader branches, and how honest are our runtime claims?”

# Design goals

1. **Prebuild-coverage first** — the crate should speak in actually shipped native tuples, not only successful CI jobs.
2. **Loader-legible** — JS/package-level loader behavior must be reviewable.
3. **Publish-identity visible** — trusted-publisher and provenance posture must remain first-class.
4. **Fallback-honest** — prebuild, local-build, and WASM fallback stories must stay distinct.
5. **Ecosystem-neutral on package manager** — npm, pnpm, and yarn should all fit the same contract layer.

# MVP surface

- Minimal types: `NodeApiContract`, `PrebuildManifest`, `PrebuildCoverageReport`, `LoaderRouteReceipt`, `PublishIdentityReport`, `RuntimeSupportReport`, `AddonIntakeReport`, `NodeApiContractDiff`, `NodeBundle`
- Minimal functions:
  - `capture_nodeapi_contract()`
  - `collect_prebuild_manifest()`
  - `evaluate_prebuild_coverage()`
  - `capture_loader_route_receipt()`
  - `capture_publish_identity_report()`
  - `classify_runtime_support()`
  - `evaluate_addon_intake()`
  - `diff_nodeapi_contracts()`
- Feature flags:
  - `napi-rs`
  - `package-json`
  - `serde`
  - `typescript`
  - `markdown`

# Compatibility story

- Must remain useful whether the project uses napi-rs generators, a custom JS loader, or mixed native/WASM packaging.
- Must treat Node-API version floors as first-class support facts.
- Should work for prebuild-first packages, packages that permit local compilation, and packages that combine native and WASM targets.
- Must not silently conflate Node support with Bun or Deno compatibility claims.
- Should stay useful even when the native addon is only one package inside a larger monorepo.

# Conformance & fixtures

- one fixture with a clean Node-only prebuild matrix
- one fixture with glibc/musl coverage gaps hidden by local-build fallback
- one fixture with `node-addons` native routing plus `default` WASM fallback
- one fixture with trusted publishing/provenance present but Bun/Deno claims still exceeding what the contract can actually justify
- goldens for `fully_prebuilt`, `native_gap_hidden_by_local_build`, `node_addons_with_default_wasm_fallback`, and `trusted_publisher_with_provenance`

# Path to boring stability

- Freeze the contract and verdict vocabulary before trying to support every JS runtime edge case.
- Treat runtime claims beyond observed artifacts as explicit review items.
- Keep the first loader receipt simple and file/path oriented.
- Prefer package-review artifacts over any attempt to become a full npm publisher.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust→npm addon package, record its Node-API floor, enumerate its published `.node` artifacts, inspect its generated loader behavior, and emit a support bundle that names any runtime or prebuild gaps.

# De-risk plan

1. Start with Node.js and napi-rs packaging flows before broadening Bun/Deno claims.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate one clean multi-platform package and one intentionally broken prebuild matrix.
4. Avoid becoming a binding generator, npm registry client, or CI action collection.

# Non-goals

- Not another Node binding generator.
- Not a replacement for npm publishing tools or JS package managers.
- Not a runtime-specific polyfill layer.
- Not a promise that one package automatically works across every Node-compatible runtime.

# Architecture & API sketch

```rust
pub enum PrebuildCoverageClass {
    FullyPrebuilt,
    PartialPrebuildMatrix,
    NativeGapHiddenByLocalBuild,
    WasmOnlyFallbackForNamedTuple,
    ManualReviewRequired,
}

pub fn capture_nodeapi_contract(root: &Path) -> Result<NodeApiContract>;
pub fn collect_prebuild_manifest(root: &Path, contract: &NodeApiContract) -> Result<PrebuildManifest>;
pub fn evaluate_prebuild_coverage(contract: &NodeApiContract, manifest: &PrebuildManifest) -> PrebuildCoverageReport;
pub fn capture_loader_route_receipt(root: &Path) -> Result<LoaderRouteReceipt>;
pub fn capture_publish_identity_report(root: &Path) -> Result<PublishIdentityReport>;
pub fn classify_runtime_support(
    contract: &NodeApiContract,
    manifest: &PrebuildManifest,
    loader: &LoaderRouteReceipt,
    publish_identity: &PublishIdentityReport,
) -> RuntimeSupportReport;
```

Bundle draft: `nodeapi-contract.toml`, `prebuild.manifest.json`, `prebuild-coverage.report.json`, `loader-route.receipt.json`, `publish-identity.report.json`, `runtime-support.report.json`, `addon-intake.report.json`, `notes.md`.

# Security / safety model

- Treat local paths, CI secrets, package-manager tokens, and internal monorepo structure as redactable.
- Do not claim support for a runtime or tuple that the observed package artifacts do not justify.
- Make fallback-to-local-build posture explicit because it changes downstream trust and install experience.
- Record Node-API level and runtime-family assumptions visibly in every receipt.
- Keep publish identity visible because strong provenance is useful review context without being mistaken for compatibility evidence.

# Maintenance & governance plan

- Track Node-API version-matrix changes and napi-rs packaging conventions closely.
- Keep the contract vocabulary small and release-review focused.
- Maintain fixtures for common libc/arch/runtime mismatches.
- Add Bun/Deno-specific detail only when it sharpens package review instead of widening vague marketing claims.

# Milestones

## 0.1
- Node-API contract format
- prebuild manifest capture
- prebuild-coverage report export
- loader-route receipt export
- publish-identity report export
- support classification

## 0.2
- diff support
- downstream environment intake report
- redaction controls

## 0.3
- optional Bun/Deno claim adapters
- richer npm-package report templates
- monorepo workspace helpers

# Open questions

- What is the smallest runtime vocabulary that stays honest across Node, Bun, and Deno claims?
- Which loader behaviors can the crate infer mechanically versus requiring explicit contract annotations?
- How should the crate describe “works via local build” without letting that silently masquerade as shipped binary support?

# Sources

- Node.js C++ addons / Worker-support docs: https://nodejs.org/api/addons.html
- Node-API reference: https://nodejs.org/api/n-api.html
- Node ABI stability overview: https://nodejs.org/en/learn/modules/abi-stability
- Node package `node-addons` / `default` docs: https://nodejs.org/api/packages.html
- Node CLI and error docs for addon loading boundaries: https://nodejs.org/api/cli.html ; https://nodejs.org/api/errors.html
- npm trusted publishing docs: https://docs.npmjs.com/trusted-publishers/
- npm publish/provenance context docs: https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/
- napi-rs homepage and support matrix: https://napi.rs/
- napi-rs getting started: https://napi.rs/docs/introduction/getting-started
- napi-rs CLI build docs: https://napi.rs/docs/cli/build
- napi-rs v3 notes on broader runtime compatibility: https://napi.rs/blog/announce-v3
