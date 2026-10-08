# Epic proposal: Extension Productization Stack (`cargo extensioncheck`, `extension-product-pack/v0`)

## One-line thesis
Build a thin stack-level Rust companion layer for **extension-enabled products** that links **host/plugin surface truth**, **runtime-kind and capability truth**, **package/install/lifecycle truth**, and **support/docs truth** into one portable review boundary without collapsing editors, shells, desktop-apps, agent hosts, and Wasm/component lanes into one fake “supports extensions” badge.

## Why this is now worth doing
Rust has real extension lanes now, but they still live in different planes:
- Rust’s 2026 flagship slate explicitly includes **Wasm Components**, which makes typed extension/runtime lanes a live ecosystem frontier rather than a niche side path.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The current Rust/component-model guidance says Rust has first-class component support via `wasm32-wasip2`; older `cargo-component` workflows are in the process of being deprecated for the simple native-Cargo path; and `cargo-component` itself now explicitly says plain `cargo` + `wasm32-wasip2` works for WASI-only lanes while custom-WIT lanes still need `cargo-component`. That means the extension/runtime picture is getting richer rather than converging to one tool.
  https://component-model.bytecodealliance.org/language-support/rust.html
  https://github.com/bytecodealliance/cargo-component
- Zed extensions are Git repositories with an `extension.toml` manifest and can provide languages, debuggers, themes, snippets, slash commands, and MCP servers; Zed also exposes a real capability system where users can restrict operations such as `process:exec`.
  https://zed.dev/docs/extensions/developing-extensions
  https://zed.dev/docs/extensions/capabilities
- Nushell plugins are separately installed units speaking a **versioned** `nu-plugin` protocol, and the docs explicitly warn that when Nushell is updated, registered plugins need to be updated too.
  https://www.nushell.sh/book/plugins.html
- Tauri plugins are product families made of a Cargo crate plus optional NPM / Android / iOS packages, and its plugin docs/security docs explicitly say potentially dangerous plugin commands and scopes are blocked by default until enabled through capabilities/permissions configuration.
  https://v2.tauri.app/develop/plugins/
  https://v2.tauri.app/plugin/os-info/
- Extism treats the plugin system itself as a host-defined interface; its manifest describes the plugin plus runtime constraints; and its runtime/host-function docs make host injection and cross-language embedding explicit.
  https://extism.org/docs/concepts/manifest/
  https://extism.org/docs/concepts/runtime-apis/
  https://extism.org/docs/concepts/host-functions/
- WIT packages are explicitly the basis of sharing types and definitions in an ecosystem of components, which is exactly the sort of stable package/interface boundary extension ecosystems want to import rather than re-invent.
  https://component-model.bytecodealliance.org/design/packages.html
  https://github.com/WebAssembly/component-model/blob/main/design/mvp/WIT.md

What is still missing is the **stack-level boundary that says one extension-enabled product subject was reviewed with these imported truths, these runtime lanes, these capability defaults, these install/update paths, these caveats, and this bounded handoff to consumers**.

## Working name
- CLI: `cargo extensioncheck`
- primary artifact: `extension-product-pack/v0`

## Scope
### This epic should own
- extension-product subject identity
- imported plugin-surface / runtime-capability / component / host-package / distribution / support attachments
- diffable review points across host versions, plugin versions, runtime lanes, and install/update paths
- bounded release / support / gallery / policy / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- creating one universal plugin SDK
- registry hosting or extension-gallery services
- replacing Zed/Nushell/Tauri/Extism/component tooling
- declaring one runtime lane the winner
- inventing one universal permission language
- a one-number extension-readiness score

## Candidate artifact family
### `extension-product-brief/v0`
Why the product exists, intended consumer set, host family, runtime lanes in scope, freshness budget, and review status.

### `extension-product-subject/v0`
The exact host version/build, extension-point family, extension package identities, runtime-lane identities, and comparison base.

### `extension-product-pack/v0`
The portable review bundle linking:
- imported `plugin-pack` attachments
- imported `cap-pack` attachments
- imported `component-pack` / `hostpkg-pack` / protocol/native runtime attachments as applicable
- imported install/override receipts plus update/downgrade continuity receipts
- imported support/docs/check receipts
- local notes, waivers, and caveats
- integrity metadata

### `extension-product-diff/v0`
What changed between two review points, with separate sections for host surface, runtime lanes, capability posture, package/install/update posture, and bounded downstream conclusions.

### `extension-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support review
- gallery / extension-ops review
- policy / security review
- atlas / adoption review
- assistant/editor rendering

## Recommended rollout
1. single-host Wasm extension lane
2. capability-attached review lane
3. versioned protocol-executable lane
4. gallery / install / override / downgrade lane
5. mixed-runtime or multi-package lane
6. bounded consumer handoff lane

This should be driven by [`design/extension-productization-pilot-program.md`](../design/extension-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a better plugin manifest,
- a nicer extension gallery,
- a nicer permissions UI,
- a better component wrapper,
- or a better host-specific SDK.

An epic contribution here instead gives Rust one **portable extension-product contract** above those lanes.
That is strategically different because it can:
- make release/support/gallery/policy reviews share the same subject and evidence boundary;
- let host-specific SDKs stay specialized without pretending they define the whole product;
- keep host identity, plugin package identity, runtime lane, capability activation, install receipts, update continuity, and support claims distinct but linked;
- and give atlas/assistant consumers a bounded surface to import instead of re-scraping docs, manifests, capability files, and issue threads.

## Design principles
- **No fake one-runtime winner.**
- **Imported runtime truth stays imported.**
- **Host identity is not plugin package identity.**
- **Capability defaults do not replace install truth.**
- **Install receipts do not replace support truth.**
- **Partial lane coverage is explicit.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact extension-enabled product subject,”
- “these are the host/plugin/runtime lanes we actually support,”
- “these are the capabilities available, granted, denied, or user-activated,”
- “these are the package/install/update/downgrade facts we imported,”
- “these are the docs/support checks and caveats,”
- “this is what changed from the prior review,”
- and “this is what release/support/policy/atlas consumers may safely conclude,”

without inventing a bespoke extension-support schema for every repository.

## Read this with
- `gaps/extension-hosts-galleries-capabilities-and-support-contracts.md`
- `design/extension-productization-stack.md`
- `design/extension-productization-pilot-program.md`
- `design/plugin-surface-kit.md`
- `design/runtime-capability-kit.md`
- `design/wasm-component-kit.md`
- `design/host-package-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
