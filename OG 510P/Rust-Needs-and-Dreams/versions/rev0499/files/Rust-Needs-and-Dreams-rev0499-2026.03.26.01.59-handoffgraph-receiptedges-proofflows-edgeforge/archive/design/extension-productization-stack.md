# Design: Extension Productization Stack (Plugin Surface + Runtime Capability + Wasm Component + Host Package + Distribution Contract + Support Envelope)

## Goal
Turn Rust extension-enabled products into a **portable productization stack** instead of leaving each host to publish its extension story as a tangle of protocol versions, plugin manifests, permission files, gallery/install rules, runtime assumptions, SDK caveats, and README folklore.

The stack should **not** replace plugin runtimes, extension SDKs, galleries, registry protocols, or package managers.
It should make them compose better and make supported extension behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust host extensions?” They say the missing problem is **what a Rust extension host can honestly claim to support**:
- Rust’s 2026 flagships explicitly include **Wasm Components**, which means typed, component-shaped extension runtimes are becoming more mainstream in the language/toolchain itself;
- the official component-model Rust guide now says `wasm32-wasip2` is a first-class target in the toolchain, native Cargo can build components directly, `cargo-component` is in the process of being deprecated for the simple path, and `wit-bindgen` is still needed for custom-WIT bindings; `cargo-component` itself now explicitly says plain `cargo` + `wasm32-wasip2` works for WASI-only lanes while custom-WIT lanes still need `cargo-component`;
- the WIT spec says WIT packages are the basis of sharing types and definitions in an ecosystem of components, which is exactly the kind of stable boundary extension ecosystems want;
- Zed extensions are Git repositories with an `extension.toml` manifest, can provide languages/debuggers/themes/snippets/slash commands/MCP servers, and compile procedural Rust parts to WebAssembly; Zed also gives users an explicit extension-capability system with constrainable operations like `process:exec`;
- Nushell plugins are separately installed units speaking a **versioned** protocol, and the docs are explicit that when Nushell is updated, registered plugins need to be updated too;
- Tauri plugins are first-class product units made of a Cargo crate and optional NPM / Android / iOS packages, can hook lifecycle and expose commands, and are governed by named permissions and capabilities; Tauri’s current plugin docs and plugin-permission examples go further and state that potentially dangerous plugin commands/scopes are blocked by default until enabled in capabilities configuration;
- Extism treats a plug-in system as a host-defined interface, gives plug-ins a manifest that describes the plugin plus runtime constraints, allows hosts to inject host functions as explicit capability surfaces, and exposes the runtime as both a Rust crate and a C API.

Together, those signals argue that the missing contribution is **not** another plugin SDK, gallery wrapper, or runtime-specific convenience layer. It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Plugin Surface: declared extension points, lifecycle, runtime kinds, and compatibility posture
Plugin Surface owns the **declared extension boundary** for a host:
- host identity and extension-point identities,
- lifecycle hooks and event points,
- runtime kinds (`wasm-component`, `extism-wasm`, `native-stable-abi`, `protocol-exec`, framework-native, etc.),
- plugin manifests and compatibility ranges,
- and checked host↔extension flows.

This layer answers questions like:
- “Which extension points are official?”
- “Which runtime kinds are real, experimental, or internal-only?”
- “What host/plugin compatibility claims were actually checked?”

Design rule: **host extension-point identity must not collapse into crate names, binary names, or symbol names alone**.

### 2) Runtime Capability: what extensions may do, under what grants, with what scope
Extension hosts stop being honest the moment capability posture is hidden.
This layer covers:
- available versus granted capabilities,
- permission identifiers and scope selectors,
- host-function imports or command privileges,
- user/app/runtime grant sources,
- denied-by-default or restricted operations,
- and per-window/per-plugin/per-host policy where relevant.

This layer answers questions like:
- “What powers can an extension ask for?”
- “What is granted by default versus activated later?”
- “Which capability names or shapes changed across host versions?”

Design rule: **capability posture is part of the product contract, not only the security implementation**.

### 3) Wasm/native/protocol runtime truth: imports, packaging lanes, and host embedding reality
Real extension ecosystems now span materially different runtime lanes:
- versioned executable protocols (like Nushell plugins),
- WebAssembly/plugin systems (like Extism),
- WIT/component-shaped embeddings,
- framework-native/mobile plugin lanes (like Tauri),
- and native ABI/plugin lanes where they exist.

This layer covers:
- runtime kind and embedding mode,
- host requirements/imports,
- protocol or WIT/package identity,
- package/runtime layout differences,
- and raw attached artifacts preserving lane-specific truth.

This layer answers questions like:
- “Is this extension a separate executable, a Wasm/component bundle, a native artifact, or a host-mobile package family?”
- “Which imports, protocols, or package identities determine compatibility?”
- “What part of the extension story depends on the host runtime rather than only the extension package?”

Design rule: **extension stacks must preserve runtime-lane truth instead of flattening executable, Wasm, component, native, and mobile extension lanes into one fake model**.

### 4) Host Package + Consumer Install + Update Continuity: install, update, downgrade, gallery, and shipped-artifact truth
Extension ecosystems rarely fail only at runtime. They fail at acquisition and upgrade:
- gallery identity and package source,
- Git-repo or registry-package posture,
- install/override/dev-extension workflows,
- update versus downgrade rules,
- package metadata and shipped artifact families,
- and compatibility between host version, extension package version, and runtime lane.

This layer answers questions like:
- “What gets installed where?”
- “How does the host discover, register, or override an extension?”
- “What happens on host update, plugin update, or downgrade?”

Design rule: **package/install/lifecycle truth must not disappear into gallery UI or CLI behavior**.

### 5) Support Envelope + DocProof: public promise, checked examples, and support posture
Extension ecosystems accumulate lore fast:
- which host/runtime/platform combinations are officially supported,
- which capabilities are public or experimental,
- which docs/examples were actually checked,
- which extension lanes are community-only or host-maintainer-supported,
- and which upgrade/migration paths are real.

This layer answers questions like:
- “What extension story is actually supported?”
- “Which docs and setup guides were checked?”
- “What can support/release/policy consumers safely conclude?”

Design rule: **one extension demo, one gallery page, or one SDK example is not the support contract**.

### 6) Downstream consumers
The stack becomes ecosystem-shaping when real consumers can import it honestly:
- **release/support** consumers can answer what extension surfaces and update paths a shipped host actually promised;
- **gallery/install/policy** consumers can reason about package source, capability activation, and compatibility without scraping prose;
- **atlas/learning** consumers can compare serious Rust extension lanes without pretending one runtime has already won;
- **incident/debug** consumers can preserve host/plugin/runtime/capability context when extension problems happen.

Design rule: **consumers import selected extension-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust plugin platform.”
It is a portable boring stack with clear boundaries:

1. **host and extension identity first**
   - prove stable host identity, extension-point identity, extension package identity, and runtime-lane identity on one real host;
2. **capability and permission truth second**
   - make available/granted/denied/scope-bounded capability posture diffable and reviewable;
3. **runtime-lane attachments third**
   - preserve protocol/Wasm/component/native/mobile truths as imports rather than re-inventing them;
4. **install/update/downgrade truth fourth**
   - prove gallery/install/override/update receipts exist above extension manifests;
5. **support/docs and consumer imports fifth**
   - prove public support claims, checked docs, and release/support/policy/atlas consumers can import the artifacts without re-deriving them.

An eventual aggregate artifact may exist, but it should be a **thin pack of linked artifacts**, not a mega-schema that erases plugin surface, capability posture, runtime-lane truth, package/install truth, and support truth. The explicit proposal-layer candidate is now [`proposals/epic-extension-productization-stack.md`](../proposals/epic-extension-productization-stack.md): a thin `cargo extensioncheck` / `extension-product-pack/v0` layer above those imported truths rather than a new universal extension framework or hosted marketplace.

## Ranked first execution lanes
1. **single-host Wasm extension lane**
   - best first exporter because it proves host identity, extension packaging, and runtime-lane truth without immediately requiring multi-language or native ABI complexity.
2. **capability-gated host lane**
   - proves that extension capability/permission posture is part of the product boundary rather than hidden config.
3. **versioned protocol-executable lane**
   - proves host/plugin version compatibility and update posture can be captured honestly.
4. **gallery/install/update lane**
   - proves package/install/override/downgrade truth matters as much as runtime truth.
5. **mixed-runtime host lane**
   - proves extension ecosystems can carry multiple runtime/package families without collapsing them into one fake abstraction.

## Non-goals
- one universal plugin SDK;
- one marketplace or gallery service;
- another “plugins in Rust with Wasm” wrapper that ignores package/update/support truth;
- flattening host/plugin surface, capability truth, runtime truth, install truth, and support truth into one fake “extension support” badge;
- pretending editor, shell, desktop-app, embedded-host, agent-host, and mobile-extension ecosystems are the same.

## Archive implications
- The archive should now treat **Plugin Surface + Runtime Capability + Wasm Component + Host Package + Distribution Contract + Support Envelope** as a coupled **Extension Productization Stack** in frontier discussions.
- The direct proposal-layer candidate is [`proposals/epic-extension-productization-stack.md`](../proposals/epic-extension-productization-stack.md), which should stay deliberately thin and import lower-layer truths instead of replacing them.
- Future revisions should prefer **host identity/version truth, extension package/install/lifecycle truth, capability/permission activation, runtime-kind compatibility truth, and support/docs truth** over another plugin SDK, gallery wrapper, marketplace scraper, or Wasm-only convenience layer.
- This stack should stay adjacent to, but distinct from, **Polyglot Productization** (mixed-language package/binding truth), **CLI Productization** (tool/runtime/install truth), and **Agent Productization** (workflow/model/retrieval/runtime truth).

## Read this together with
- `design/plugin-surface-kit.md`
- `design/runtime-capability-kit.md`
- `design/wasm-component-kit.md`
- `design/host-package-kit.md`
- `design/distribution-contract-stack.md`
- `design/consumer-install-kit.md`
- `design/update-continuity-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `proposals/epic-extension-productization-stack.md`
