# Epic proposal: Client Productization Stack

## Thesis
Rust does not most urgently need another GUI toolkit, shell, bridge generator, or app-template bundle.
It needs a **portable productization layer for real client applications**.

The serious ingredients already exist:
- Tauri 2 positions itself as a framework for all major desktop and mobile platforms, with explicit permissions, scopes, and capabilities attached to windows and webviews.
- Dioxus positions itself as a fullstack cross-platform app framework with an integrated CLI for hot reload, bundling, and development servers, but its own bundling docs still expose platform/package limits and native-platform-only build reality.
- Slint explicitly targets embedded, desktop, and mobile native GUI work.
- AccessKit provides shared accessibility infrastructure already integrated by multiple Rust UI projects.
- `cargo-mobile2` is candid that its maintenance is scoped primarily to the Tauri use case, which is exactly the kind of ecosystem signal that says “the higher product layer is still missing.”

## The worthy contribution
The worthy contribution here is a thin **Client Productization Stack** above the existing kits:
- **Client App Surface Kit**
- **A11yKit**
- **Localization Surface Kit**
- **Distribution Contract Stack**
- **Support Envelope + DocProof**
- optional imports from **Release Pipeline**, **Rollout Surface**, **Incident**, **Atlas**, and adjacent stacks

That stack should let maintainers publish and reviewers consume:
1. **app/package/capability truth** — what the app officially is, which shells and package identities it has, which bridges and permissions belong to it, and which lifecycle assumptions matter;
2. **support/docs truth** — what targets, runtime floors, docs surfaces, and caveats are actually promised;
3. **accessibility truth** — semantic UI evidence and a11y regressions that are more honest than screenshot tests;
4. **locale/runtime-data truth** — locales, catalogs, placeholders, fallback policy, and runtime-data assumptions;
5. **distribution/install truth** — what channel/store/direct bundle the user actually got, what verification ran, and what fallback path was taken;
6. **consumer handoff truth** — what release/support/incident/atlas/rollout consumers may conclude without redefining the product surface.

## Candidate artifact family
The stack should stay thin and linked rather than becoming a mega-schema. A plausible family is:
- `client-product-brief/v0`
- `client-support-brief/v0`
- `client-a11y-brief/v0`
- `client-locale-brief/v0`
- `client-install-brief/v0`
- `client-product-diff/v0`
- `client-product-pack/v0`

These artifacts should mostly reference lower-layer packs and checked attachments instead of replacing them.

## Reference CLI shape
- `cargo app product export`
  - emit `client-product-brief/v0` from imported app-surface / capability / lifecycle / package profiles
- `cargo app product support`
  - emit `client-support-brief/v0` from support-envelope / docproof imports
- `cargo app product a11y`
  - emit `client-a11y-brief/v0` from semantic snapshots/reports
- `cargo app product locale`
  - emit `client-locale-brief/v0` from locale/catalog/fallback/runtime-data imports
- `cargo app product install`
  - emit `client-install-brief/v0` from distribution/install receipts
- `cargo app product diff --against <ref|version|profile>`
  - emit `client-product-diff/v0`
- `cargo app product pack`
  - produce `client-product-pack/v0`

This should remain a **composition layer**, not a new framework, store portal, or deployment service.

## Why this is ecosystem-shaping
This contribution would help at least five important Rust client families at once:
- Tauri-style desktop/mobile/webview products with explicit capabilities and plugin permissions;
- Dioxus-style desktop/mobile/fullstack apps where build/bundle/deploy truth matters as much as UI code;
- Slint-style native apps spanning embedded, desktop, and mobile;
- bridge-heavy apps using UniFFI or `flutter_rust_bridge` where package/runtime truth differs from UI truth;
- support/release/install consumers that currently reconstruct app promises from manifests, issue threads, and IDE/project-file archaeology.

It also composes unusually well with atlas, guidance, and assistant-facing consumers because the 2025 State of Rust survey says online documentation remains the preferred canonical reference while agentic/editor usage keeps rising.

## Strong first proving grounds
1. **Tauri desktop/mobile lane**
   - prove app/package/capability/lifecycle truth on one real Tauri subject with permissions/capabilities kept explicit.
2. **Dioxus deploy/bundle lane**
   - prove bundle/package/support truth on one Dioxus desktop/mobile or native-fullstack subject, keeping package-type and cross-build limits honest.
3. **Slint native lane**
   - prove that native-UI support truth can travel separately from framework marketing or platform demos.
4. **Accessibility lane**
   - prove semantic UI evidence via AccessKit-backed snapshots/reports rather than screenshot theater.
5. **Install/support consumer lane**
   - prove release/distribution/install and support consumers can import the stack without redefining it.

## What this should not become
- not a universal GUI toolkit;
- not a universal mobile/desktop shell;
- not a store-publishing control plane;
- not a “best Rust app framework” chooser;
- not a fake “app readiness” score that flattens permissions, accessibility, locale support, installation, and docs into one badge.

## Success bar
This becomes worthy when a maintainer, release engineer, support engineer, or ecosystem guide can answer:
- what app/shell/package identities are official,
- what capabilities and lifecycle assumptions belong to that promise,
- what accessibility and localization truths were actually checked,
- what support/docs/runtime-floor claims were attached,
- what a user actually installed and from where,
- and what changed between versions or profiles,

without scraping Xcode/Gradle manifests, framework boilerplate, issue threads, or store notes.

## Read this with
- `gaps/client-app-surfaces-and-platform-behavior-contracts.md`
- `design/client-app-surface-kit.md`
- `design/client-productization-stack.md`
- `design/client-productization-pilot-program.md`
- `design/a11ykit-ui-testing.md`
- `design/localization-surface-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
