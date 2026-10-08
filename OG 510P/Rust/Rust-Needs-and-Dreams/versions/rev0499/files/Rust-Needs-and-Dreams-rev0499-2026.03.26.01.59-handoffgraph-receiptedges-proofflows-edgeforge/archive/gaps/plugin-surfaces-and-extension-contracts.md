# Gap: plugin surfaces and extension contracts

## What is missing
Rust has credible ways to load, sandbox, and structure extensions, but it still lacks a **shared plugin-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which extension points a host officially exposes,
- which lifecycle hooks and call shapes plugins are expected to implement,
- which host capabilities and permissions a plugin can request or assume,
- which runtime model is in force for a given extension point (native dynamic library, stable-ABI shim, Wasm component, Extism-style Wasm plug-in, framework plugin, etc.),
- which compatibility promises exist across host versions and plugin SDK versions,
- which packaging and manifest fields are part of the support promise,
- which example host↔plugin interactions were actually checked,
- and what evidence exists that the declared extension boundary still matches the shipped host and plugin artifacts.

That missing layer matters because “plugin support” is not one thing. The Rust Reference is explicit that the `Rust` ABI offers no stability guarantees, which pushes native plugin systems toward explicit ABI layers or other runtimes. At the same time, the ecosystem already has real point solutions: `libloading` for dynamic library loading, `abi_stable` and `stabby` for stable binary interfaces, Extism for Wasm-based plug-in systems with manifests and host functions, Tauri for application plugin ecosystems, and the WebAssembly Component Model for interoperable component boundaries. What Rust still lacks is a portable review layer above those pieces.

Sources:
- https://doc.rust-lang.org/reference/items/external-blocks.html
- https://docs.rs/libloading
- https://docs.rs/abi_stable
- https://docs.rs/stabby
- https://extism.org/docs/concepts/plug-in-system/
- https://extism.org/docs/concepts/manifest/
- https://v2.tauri.app/develop/plugins/
- https://component-model.bytecodealliance.org/

## The current seam is awkward
The ecosystem clearly has ingredients:
- `libloading` gives Rust a safer cross-platform interface for dynamic library loading,
- `abi_stable` already supports ffi-safe trait objects, extensible prefix types, and load-time layout checking,
- `stabby` is another serious stable-ABI lane for shared libraries,
- Extism models plug-ins as Wasm modules with explicit manifests, host functions, runtime constraints, and runtime-level testing,
- Tauri treats plugins as first-class extension units that can hook lifecycle events, expose Rust and mobile code, and integrate with the webview/event system,
- and the WebAssembly Component Model exists to make interoperable component boundaries possible across libraries, applications, and environments.

But real plugin ecosystems still hand-assemble their support story out of:
- crate-specific traits and version gates,
- hand-written manifests,
- ad hoc permission and capability checks,
- per-runtime packaging conventions,
- loader-specific compatibility lore,
- framework-specific lifecycle docs,
- test harnesses for some happy paths,
- and release notes explaining what host/plugin combinations are still expected to work.

The result is not that Rust lacks extension mechanisms.
The result is that there is no portable way to say:
- “these are the supported extension points and runtime kinds,”
- “these capabilities are required or granted,”
- “this host version remains compatible with these plugin SDK or manifest ranges,”
- “these host↔plugin interactions were actually checked,”
- or “this plugin package is suitable for this host surface.”

Wasm Components help with interoperable interfaces, and stable-ABI crates help with native binary boundaries, but neither one by itself is the whole support story for extension ecosystems. Extensibility also needs host lifecycle declarations, permission/capability posture, packaging truth, and compatibility evidence. That is the archive pattern worth elevating: strong parts, weak shared boundary.

Sources:
- https://docs.rs/libloading
- https://docs.rs/abi_stable
- https://docs.rs/stabby
- https://extism.org/docs/concepts/plug-in-system/
- https://extism.org/docs/concepts/manifest/
- https://v2.tauri.app/develop/plugins/
- https://component-model.bytecodealliance.org/

## Why this matters
This gap is bigger than “better plugin docs.”
It affects:
1. **extension-platform design** — hosts need stable extension-point identities, lifecycle rules, capability models, and packaging expectations if they want a third-party ecosystem instead of one-off integrations;
2. **compatibility review** — changing lifecycle hooks, required capabilities, or host APIs can break plugins just as surely as ordinary API drift breaks crates;
3. **runtime plurality** — teams should be able to preserve one extension surface while experimenting with native loading, stable-ABI shims, Wasm-based runtimes, or framework-specific adapters;
4. **security and sandboxing posture** — capabilities and host-provided imports are part of the support promise, not a side note;
5. **testing honesty** — plugin ecosystems often have examples or demo plugins, but not one attachable artifact saying which host/plugin combinations and behaviors were actually checked;
6. **ecosystem composition** — Wasm Component Kit, FFI Boundary Kit, Support Envelope Kit, Identity Surface Kit, Runtime Settings Kit, and Release Pipeline Kit all benefit from a host/plugin boundary without owning it.

Extism even describes a plugin system as an interface your application defines so that someone else can implement their own functionality in your app, while Tauri explicitly treats plugins as the way to add external functionality without bloating the core. Those are direct signals that the missing substrate is the supported extension boundary itself, not another narrow loader wrapper.

Sources:
- https://extism.org/docs/concepts/plug-in-system/
- https://v2.tauri.app/develop/plugins/
- https://doc.rust-lang.org/reference/items/external-blocks.html
- https://docs.rs/abi_stable
- https://component-model.bytecodealliance.org/

## What “good” looks like
A worthy contribution here is **not** another dynamic-loader crate, another framework-specific plugin SDK, another marketplace, or another Wasm runtime.

It is a shared plugin-surface boundary:
- one `plugin-surface/v0` describing host identity, supported extension points, lifecycle hooks, runtime kinds, support levels, and host/plugin API version posture,
- one `extension-point-map/v0` giving stable extension-point ids, host callbacks/imports/commands/events/resources in scope, and links to attached runtime-specific artifacts,
- one `host-capability-profile/v0` describing what the host may expose or deny to plugins (filesystem/network/UI/event/command/state capabilities, host functions, permission prompts, quotas, sandbox notes, etc.),
- one `plugin-manifest/v0` describing plugin identity, implementation/runtime kind, declared capabilities, compatibility ranges, packaging attachments, and provenance pointers,
- one `plugin-example-catalog/v0` containing canonical host↔plugin flows, negative cases, upgrade/downgrade cases, and sandbox-denial examples,
- one `plugin-check-plan/v0` describing which host versions, runtimes, SDK versions, and plugin fixtures were exercised,
- one `plugin-check-report/v0` recording compatibility findings, manifest drift, capability mismatches, lifecycle failures, and raw attachment pointers,
- one optional `plugin-diff-report/v0` for additive/breaking extension-surface changes,
- and one `plugin-pack/v0` bundle for CI, release review, SDK docs, marketplace ingestion, and later archaeology.

That would let Rust teams treat extension ecosystems as reviewable support surfaces instead of a pile of loader code, trait impls, manifests, and release-note folklore.
