# Design: Plugin Surface Kit (`cargo plugincheck`, `plugin-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported plugin/extension surface: extension-point identities, lifecycle hooks, runtime kind, host capabilities, plugin manifests, compatibility posture, checked host↔plugin flows, and evidence that the declared extension boundary still matches the shipped host and plugin artifacts.

This should **not** replace `libloading`, `abi_stable`, `stabby`, Extism, Tauri plugins, the WebAssembly Component Model, or framework-specific SDKs.
It should make them compose better and make support claims reviewable.

## References (signals)
- The Rust Reference is explicit that the native `Rust` ABI offers no stability guarantees, which is a foundational reason native plugin systems need explicit boundary tooling instead of wishful thinking.
  https://doc.rust-lang.org/reference/items/external-blocks.html
- `libloading` already exposes a safer cross-platform interface to dynamic libraries but deliberately does not hide all platform differences.
  https://docs.rs/libloading
- `abi_stable` already supports ffi-safe trait objects, extensible prefix types, and load-time layout checking for semver-compatible changes.
  https://docs.rs/abi_stable
- `stabby` is another serious stable-ABI lane focused on stable binary interfaces for shared libraries.
  https://docs.rs/stabby
- Extism explicitly frames a plug-in system as an interface your application defines, and its manifest is a description of the plug-in plus runtime constraints.
  https://extism.org/docs/concepts/plug-in-system/
  https://extism.org/docs/concepts/manifest/
- Tauri plugins are first-class extension units that can hook lifecycle, expose Rust code, and bridge to Kotlin or Swift on mobile.
  https://v2.tauri.app/develop/plugins/
- The WebAssembly Component Model exists for interoperable Wasm libraries, applications, and environments, which makes it an important runtime lane for plugin ecosystems.
  https://component-model.bytecodealliance.org/

## Core components

### 1) `plugin-surface/v0`
A host-side declaration of what extension ecosystem is being supported.

Possible contents:
- host identity
- extension-point ids
- support levels:
  - stable
  - experimental
  - internal-only
  - deprecated
- runtime kinds per extension point:
  - native-dylib
  - native-stable-abi
  - wasm-component
  - extism-wasm
  - framework-plugin
  - custom-host-runtime
- lifecycle hooks in scope:
  - load
  - init/register
  - activate/deactivate
  - event/command callbacks
  - shutdown/unload
- compatibility policy and versioning posture
- packaging/distribution posture
- links to raw runtime-specific artifacts

Design rule: host extension-point identity must be explicit and stable enough to diff over time. Do not treat crate names or symbol names alone as the extension contract.

### 2) `extension-point-map/v0`
A normalized map of what each extension point actually expects.

Possible contents:
- extension-point id and title
- runtime kind
- input/output contract references
- host callbacks/imports/commands/events/resources exposed to plugins
- lifecycle order assumptions
- threading / async / reentrancy notes
- state or storage hooks
- UI/webview/app-shell hooks when relevant
- raw attachments:
  - WIT worlds/interfaces
  - Extism host function signatures
  - stable-ABI descriptors
  - framework metadata

Design rule: preserve raw runtime truth. Normalize metadata around it instead of flattening Wasm, native ABI, and framework plugins into one fake call model.

### 3) `host-capability-profile/v0`
A declaration of what powers a plugin may request or receive.

Possible contents:
- capability ids
- required vs optional vs denied
- prompt/consent model
- filesystem/network/process/device/UI/event/state access
- host-function namespaces
- quotas, limits, and timeouts
- sandbox/isolation notes
- platform-specific capability limits
- provenance for who grants the capability:
  - compile-time default
  - runtime policy
  - user prompt
  - signed plugin allowlist

Design rule: treat capability posture as a first-class support claim. Do not bury it inside loader code or README prose.

### 4) `plugin-manifest/v0`
A portable statement of what a particular plugin artifact claims.

Possible contents:
- plugin id and display metadata
- implementation/runtime kind
- artifact locations and hashes
- host/SDK compatibility ranges
- declared capabilities and permissions requested
- extension points implemented
- optional transitive runtime requirements
- packaging kind:
  - raw dylib
  - cdylib + metadata
  - wasm/component bundle
  - extism manifest bundle
  - framework package
- provenance and signature pointers
- raw attached manifests from underlying runtimes

Design rule: preserve raw plugin-manifest truth where it exists. v0 should add a review layer, not require every ecosystem to adopt one invented manifest format immediately.

### 5) `plugin-example-catalog/v0`
Small canonical flows and fixtures.

Possible contents:
- successful host startup with plugin present
- capability-granted flow
- capability-denied flow
- version-mismatch flow
- missing-manifest or invalid-signature flow
- upgrade/downgrade compatibility example
- sandbox escape attempt / blocked operation example
- provenance labels:
  - illustrative only
  - generated
  - checked in CI
  - captured from fixture replay

Design rule: keep examples small and scrubbed. Do not ship whole demo applications as the evidence layer.

### 6) `plugin-check-plan/v0`
A concrete plan for what is checked.

Required ideas:
- host versions selected
- plugin fixtures selected
- runtime kinds exercised
- capabilities/policy combinations exercised
- manifest validation steps
- compatibility and upgrade/downgrade checks
- unsupported or intentionally omitted lanes
- platform matrix assumptions
- source-truth adapters used:
  - Wasm Component docs/tools
  - Extism manifest/runtime
  - stable-ABI loaders
  - framework plugin metadata

This is where the kit stops pretending “we can load a plugin” means “the extension ecosystem is understood.”

### 7) `plugin-check-report/v0`
Evidence from tests, comparisons, and runtime checks.

Possible contents:
- extension-point coverage summary
- compatibility pass/fail by host/plugin version pair
- capability mismatches
- lifecycle ordering failures
- manifest/schema drift findings
- runtime-kind-specific findings
- load/unload or activate/deactivate findings
- raw attachments:
  - manifests
  - WIT/component inspection outputs
  - ABI layout/type reports
  - plugin test transcripts
  - signed package metadata
  - platform-specific loader diagnostics

### 8) `plugin-diff-report/v0` (optional)
For compatibility-sensitive changes:
- extension point added/removed/renamed
- lifecycle hook changed
- capability added/removed/retightened
- runtime kind changed
- compatibility range changed
- packaging/distribution rule changed
- support level changed
- deprecation/sunset notes added or removed

Should distinguish:
- additive changes
- breaking changes
- runtime-specific changes
- documentation-only drift
- manual migration required

### 9) `plugin-pack/v0`
Bundle format containing:
- `plugin-surface/v0`
- `extension-point-map/v0`
- one or more `host-capability-profile/v0`
- one or more `plugin-manifest/v0`
- optional `plugin-example-catalog/v0`
- one or more `plugin-check-report/v0`
- optional `plugin-diff-report/v0`
- optional raw attachments: WIT docs, Extism manifests, ABI reports, framework package metadata, signatures, and check transcripts

This is the unit that should travel through CI, release review, SDK docs, marketplace ingestion, policy, and later archaeology.

### 10) `cargo plugincheck`
Reference UX:
- `cargo plugincheck init`
- `cargo plugincheck surface`
- `cargo plugincheck caps`
- `cargo plugincheck manifests`
- `cargo plugincheck diff`
- `cargo plugincheck pack`

`cargo plugincheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true plugin runtime.

## Default policy
- **Separate extension-point identity, plugin identity, and runtime kind.**
- **Preserve raw runtime/manifest truth as attachments** instead of flattening Wasm, native ABI, and framework-specific metadata into one fake canonical binary model.
- **Treat capabilities, permission prompts, and host imports as support surfaces**, not incidental loader details.
- **Distinguish checked fixtures from illustrative examples** so docs stay honest.
- **Prefer runtime adapters over runtime replacement** in v0.
- **Keep compatibility posture explicit** across host versions, plugin SDK versions, and package/runtime versions.

## What the kit should provide to others
- **Host authors:** one reviewable statement of what extension points and capabilities they really support.
- **Plugin authors:** a portable way to declare compatibility, required capabilities, and packaging expectations.
- **Platform teams:** CI/release artifacts for extension ecosystems that survive loader/runtime churn.
- **Marketplace or policy tooling:** structured inputs for signatures, trust signals, capability review, and deprecation/sunset decisions.
- **Tool authors:** stable inputs that can attach Wasm Component, Extism, ABI, signature, support-envelope, and release-pack artifacts without owning them.

## Overlap boundaries
- **Not Wasm Component Kit:** that kit is about WIT/component packaging/composition as a runtime boundary in general. Plugin Surface Kit is about host-defined extension ecosystems, capability handshake, lifecycle, compatibility, and plugin packaging/review. It may attach `component-pack/v0` for Wasm-based plugins.
- **Not FFI Boundary Kit:** that kit is about native ABI/header/binding contracts. Plugin Surface Kit may attach native ABI evidence, but it is about extension points and host/plugin compatibility above the boundary.
- **Not Compile-Time Capabilities Kit:** this is runtime extension loading and plugin ecosystems, not proc-macro/build-script execution.
- **Not Service Surface or Event Surface Kits:** plugins may expose commands, routes, or messages, but those remain distinct surfaces rather than being flattened into the host/plugin layer.
- **Not Release Pipeline Kit:** release tooling should attach `plugin-pack/v0`; it should not absorb extension-boundary truth.

## Hard problems (explicitly scoped)
1. **Rust has no stable native Rust ABI**
   - v0 must not pretend otherwise. Native runtime lanes should preserve ABI adapter truth and compatibility evidence explicitly.
2. **Runtime plurality is real**
   - native dylibs, stable-ABI shims, Wasm components, Extism, and framework-specific plugin ecosystems all matter; v0 must adapt rather than force one winner.
3. **Plugin identity is not crate identity**
   - extension-point ids, plugin ids, manifests, and package metadata all matter independently of Cargo crate names.
4. **Capability drift matters operationally**
   - a plugin gaining network access or a new host function can be as consequential as an API break.
5. **Load success is not ecosystem success**
   - version compatibility, lifecycle sequencing, permission posture, and actual checked interactions are part of the contract too.
