# Epic proposal: Plugin Surface Kit

## Thesis
Rust’s extension ecosystem is mature enough that the missing contribution is no longer “yet another plugin runtime.”
The higher-leverage missing piece is a **portable plugin-surface contract** that lets teams declare, diff, validate, and ship what their extension ecosystems actually promise: extension-point identities, lifecycle hooks, runtime kind, host capabilities, plugin manifests, compatibility posture, checked host↔plugin flows, and linked runtime-specific evidence.

In other words: Rust needs a boring, attachable `plugin-pack/v0` more than it needs another one-off loader wrapper.

## Why now
The ecosystem signals line up:
- the Rust Reference is explicit that the `Rust` ABI is not a stable plugin boundary,
- `libloading` shows dynamic loading is practical but still platform-sensitive,
- `abi_stable` and `stabby` show real demand for explicit native plugin boundaries,
- Extism already treats plugin systems, manifests, host functions, and testing as first-class concepts,
- Tauri already uses plugins as a core extensibility model for real applications,
- and the WebAssembly Component Model exists precisely because interoperable component boundaries matter.

That means the missing substrate is not raw capability.
It is the **reviewable host/plugin boundary above today’s pieces**.

Sources:
- https://doc.rust-lang.org/reference/items/external-blocks.html
- https://docs.rs/libloading
- https://docs.rs/abi_stable
- https://docs.rs/stabby
- https://extism.org/docs/concepts/plug-in-system/
- https://extism.org/docs/concepts/manifest/
- https://v2.tauri.app/develop/plugins/
- https://component-model.bytecodealliance.org/

## What should be built
A first credible version should ship:
1. `plugin-surface/v0`, `extension-point-map/v0`, `host-capability-profile/v0`, `plugin-manifest/v0`, optional `plugin-example-catalog/v0`, `plugin-check-plan/v0`, `plugin-check-report/v0`, optional `plugin-diff-report/v0`, and `plugin-pack/v0`
2. adapters for common Rust runtime lanes (`libloading`, `abi_stable`, `stabby`, Extism manifests/runtime checks, Wasm Component attachments, Tauri plugin metadata)
3. docs/reference generation for supported extension points, lifecycle hooks, capabilities, packaging expectations, and compatibility ranges
4. validation/reporting support for capability drift, lifecycle drift, version-range mistakes, manifest mismatch, and host/plugin matrix results
5. release/CI examples showing plugin packs attached to hosts, SDKs, plugin marketplaces, and enterprise review workflows

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one native plugin host using `libloading` plus explicit ABI metadata and compatibility checks
- one `abi_stable` or `stabby`-based ecosystem proving that load-time ABI/layout evidence can attach cleanly to the same pack
- one Extism-based host showing manifests, host functions, capabilities, and runtime tests feeding the same review surface
- one Wasm Component-backed plugin ecosystem proving the kit can attach WIT/component artifacts without flattening them
- one Tauri plugin pilot proving framework-specific mobile/desktop lifecycle hooks and permission posture can still fit the shared contract

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve extension-point ids, runtime kind, capabilities, and compatibility posture
2. **v0.2 adapters**
   - support native loading + stable-ABI metadata + Extism attachments + Wasm Component attachments + framework plugin metadata
   - support raw manifests and package metadata without flattening them
3. **v0.3 cross-kit integration**
   - integrate with Wasm Component, FFI Boundary, Support Envelope, Identity Surface, Policy, Trust Signals, Signed Binaries, and Release Pipeline workflows
   - support diff/baseline workflows across runtime kinds and host versions
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one runtime model

## Success metrics
- Teams can review extension-interface changes as explicit artifacts instead of reading loader code, trait impls, and release notes.
- Supported extension points, lifecycle rules, and capability posture remain documented from one declared source.
- Plugin compatibility becomes easier to trust because checked and illustrative materials stay distinct.
- Runtime migrations become easier because extension-surface claims survive beyond one loader or one framework.
- Rust plugin ecosystems become easier to hand off to platform, security, documentation, and release workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Wasm Component Kit covers WIT/component packaging and composition,
- FFI Boundary Kit covers native ABI and generated bindings,
- Support Envelope Kit covers host/platform claims,
- Identity Surface Kit and Policy Kit cover access and governance,
- and Release Pipeline / Signed Binaries / Trust Signals cover packaging and distribution evidence.

But none of those is the portable contract for the **composed host/plugin extension boundary itself**.
Plugin Surface Kit is the missing substrate that keeps extension points, capabilities, manifests, compatibility posture, and checked host↔plugin behavior attached to one reviewable interface without absorbing every runtime into one mega-format.
