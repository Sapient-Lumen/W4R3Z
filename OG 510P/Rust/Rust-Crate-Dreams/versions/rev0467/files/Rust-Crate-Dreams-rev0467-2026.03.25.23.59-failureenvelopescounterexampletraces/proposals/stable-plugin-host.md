---
id: P-0081
title: Stable Plugin Host Kit — ABI-surface receipts, capability negotiation, lifecycle truth, and compatibility witnesses
status: idea
domains: [plugins, ffi, dynamic-loading, architecture, tooling, extensibility]
last_reviewed: 2026-03-21
evidence:
  - https://docs.rs/abi_stable/
  - https://docs.rs/abi_stable/latest/abi_stable/library/index.html
  - https://docs.rs/abi_stable/latest/abi_stable/docs/prefix_types/index.html
  - https://docs.rs/libloading/
  - https://docs.rs/libloading/latest/libloading/struct.Library.html
  - https://docs.rs/cglue
  - https://docs.rs/safer_ffi
  - https://docs.rs/interoptopus/
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://slightknack.github.io/rust-abi-wiki/intro/initial_proposal.html
---

# Problem

Rust still lacks a **boring, reviewable native plugin contract** for teams that want real runtime-loaded plugins today.

The substrate is real:

- `abi_stable` explicitly targets Rust-to-Rust FFI, load-time type-checking, extensible prefix modules/vtables, and plugin systems that can be loaded at runtime even when built with a different Rust version than the loader;
- `abi_stable::library` documents a `RootModule` loading path with compatibility checks over the root module and the types it references;
- prefix types give a concrete additive-evolution story for modules and vtables;
- `libloading` provides the lower-level dynamic loading substrate with stronger symbol-lifetime safety, while also documenting that library initialization and termination routines are conceptually like calling unknown foreign code;
- `cglue`, `safer_ffi`, and `interoptopus` prove there is active substrate for FFI-safe traits, safer C-compatible boundaries, and generated bindings.

But ordinary downstream users still cannot answer the practical questions they care about:

- what **ABI surface** is actually authoritative,
- whether the host boundary is **stable-ABI types**, **serialized messages**, or some mixed shim,
- how **capabilities / optional APIs** are negotiated,
- whether the plugin can be **unloaded, hot-reloaded, or only replaced on process restart**,
- and what **compatibility witness** another team can actually trust before dropping a plugin into production.

The missing crate is therefore **not** a new stable Rust ABI and **not** another raw dylib loader.
It is a **Stable Plugin Host Kit**: one receiver-facing contract for native Rust plugins above `abi_stable`, `libloading`, and adjacent FFI substrate.

# Main judgment

This lane is worthy because native plugins are still the right answer for many Rust domains where Wasm is too constrained, too young, or too expensive as the primary extension surface:

- editors and desktop applications that want native access and low-latency hooks,
- CLIs and developer tools with local analyzers, formatters, or policy plugins,
- game, media, and simulation stacks that need tight native data paths,
- enterprise platforms that load organization-specific logic inside a Rust host,
- industrial/edge products that need offline dynamic extension without a whole component/runtime stack,
- and ecosystems that want Rust-to-Rust extension points without pretending a universal Rust ABI already exists.

The current ecosystem already proves that “supports native plugins” is too vague.
A worthy crate contribution should help other people answer four review questions with stable artifacts:

1. **What ABI surface is authoritative?**
2. **How are optional capabilities negotiated or downgraded?**
3. **What lifecycle / unload / reload truth actually applies?**
4. **What compatibility witness exists before the plugin is trusted?**

# What it provides

- `abi-surface.receipt.json` — interface crate / root module authority, boundary style, load-check basis, and extensibility posture.
- `capability-negotiation.receipt.json` — required and optional capabilities, negotiation route, downgrade policy, and failure posture.
- `lifecycle-posture.receipt.json` — load mode, unload support, reload route, state persistence, and init/termination routine posture.
- `compatibility-witness.receipt.json` — target/runtime/API-version facts, load verdict, mismatch classes, diagnostics coverage, and evidence basis.
- `plugin-bundle.manifest.json` — hashes, platform assumptions, attached receipts, and optional test-fixture witnesses.
- `plugin.summary.md` — one short human handoff note for review, support, or deployment approval.
- `plugin.diff.json` — compares two host/plugin contracts and classifies `abi_surface_changed`, `negotiation_changed`, `reload_posture_changed`, `compatibility_scope_changed`, and `manual_review_required`.
- `cargo native-plugin receipt` — emits receipts from a host/plugin workspace.
- `cargo native-plugin gate` — fails review when receipts are missing or over-claim support.
- `cargo native-plugin doctor` — diagnoses version drift, shadowed symbols, unsupported unload claims, or capability-negotiation gaps.
- `cargo native-plugin bundle` — emits one small review/support archive.

# What the crate should provide other people

1. **ABI authority exactness** so teams know whether the authoritative contract is an `abi_stable` root module, a hand-rolled symbol table, a serialized boundary, or something weaker.
2. **Negotiation honesty** so optional APIs and downgrade paths stop living only in README folklore.
3. **Lifecycle honesty** so “hot reload” does not silently mean “restart the host process” and “unload” does not ignore termination hazards.
4. **Compatibility witnesses** so another team can see what was actually checked before the plugin was declared compatible.
5. **Loss-aware boundary imports** so `abi_stable`, `libloading`, C-ABI shims, and serialized fallbacks can coexist without fake equivalence.
6. **One boring review vocabulary** that host authors, plugin authors, security reviewers, and support engineers can share.

# Personas / who it’s for

- application and framework authors building native extension points
- platform teams reviewing third-party native code
- desktop / editor / tool authors who need runtime-loaded Rust plugins
- plugin authors who need a stable target for compatibility review
- organizations standardizing internal plugin packaging and upgrade review

# Users & user stories

- **Host author:** “I need real native plugins, but I want the authoritative ABI surface and downgrade rules to be reviewable.”
- **Security reviewer:** “Tell me whether this plugin is just a hand-waved dylib, an `abi_stable` module, or a serialized boundary with fewer direct privileges.”
- **Support engineer:** “If plugin reload requires a restart or unload is unsupported, I want that truth in the handoff bundle.”
- **Plugin author:** “I want one compatibility witness that proves what was checked against the host.”
- **Release reviewer:** “I need to know whether the new release changed the root-module ABI, optional capabilities, or reload posture.”

# Prior art (and why it’s insufficient)

- `abi_stable` is the strongest current Rust-native substrate, but it is still primarily underlying machinery rather than one productized support-contract kit.
- `libloading` is the flexible low-level loader, but its docs make clear that load/unload safety remains a serious boundary with unknown initialization and termination routines.
- `cglue`, `safer_ffi`, and `interoptopus` are important adjacent FFI tools, but they do not by themselves define a reviewable native plugin contract for one host/plugin relationship.
- Hand-rolled `cdylib` + C-ABI shims remain common, but the resulting support story is often ad hoc and difficult to review or evolve.
- Wasm component/plugin approaches are valuable, but they are a different lane with a different capability and distribution story.

What remains missing is the **ABI surface + capability negotiation + lifecycle posture + compatibility witness** layer above today’s native plugin substrate.

# Design goals

1. **Contract-first, not loader-first.** Start from what another team can review.
2. **Authoritative-surface exactness.** Keep root modules, prefix modules, symbol tables, and serialized boundaries explicit.
3. **Lifecycle honesty.** Unload, reload, restart-only replacement, and state persistence must not blur together.
4. **Negotiation explicitness.** Optional APIs and downgrade rules must survive export.
5. **Compatibility-witness focus.** Successful loading should produce a stable witness, not just an absence of crashes.
6. **Import, don’t replace.** Build above `abi_stable`, `libloading`, and adjacent FFI substrate.
7. **Loss-aware classification.** Do not pretend C-ABI shims, `abi_stable` modules, and serialized message boundaries are equivalent.
8. **Manual-review over fake certainty.** When the source cannot justify a claim, emit `manual_review_required`.
9. **Small bundles.** `0.1` should fit code review, CI, and operational support handoff.

# MVP surface

- Minimal types:
  - `AbiSurfaceReceipt`
  - `CapabilityNegotiationReceipt`
  - `LifecyclePostureReceipt`
  - `CompatibilityWitnessReceipt`
  - `PluginBundleManifest`
  - `PluginDiff`
- Minimal functions:
  - `capture_native_plugin_receipts()`
  - `import_abi_stable_root_module()`
  - `import_libloading_contract()`
  - `diff_native_plugin_contract()`
  - `bundle_native_plugin_contract()`
- Feature flags:
  - `serde`
  - `abi-stable-import`
  - `libloading-import`
  - `ffi-adapters`
  - `cli`

# First-class review objects

## `abi-surface.receipt`

Captures:
- whether the boundary is an `abi_stable` prefix/root module, FFI-safe trait object surface, serialized message boundary, C-ABI shim, or another/manual class;
- interface crate authority and exported root/symbol basis;
- load-check basis (`abi_stable_root_module`, `manual_symbol_lookup`, `out_of_band_contract`, `manual_review_required`);
- extensibility posture (`prefix_additive`, `fixed_vtable`, `serialized_schema_evolution`, `manual_review_required`).

## `capability-negotiation.receipt`

Captures:
- required and optional capabilities/APIs;
- negotiation route (`versioned_module_fields`, `trait_probe`, `manifest_flags`, `serialized_capabilities`, `none`, `manual_review_required`);
- downgrade policy;
- and failure posture when a requested capability is unavailable.

## `lifecycle-posture.receipt`

Captures:
- load mode (`startup_scan`, `explicit_on_demand`, `per_request_subprocess`, `manual_review_required`);
- unload posture (`unsupported`, `host_drop_only`, `process_restart_only`, `unsafe_or_manual`, `manual_review_required`);
- reload posture (`unsupported`, `replace_on_restart`, `side_by_side_slot`, `manual_review_required`);
- state posture (`stateless`, `plugin_internal_state`, `host_managed_state`, `mixed`, `manual_review_required`);
- and init/termination routine assumptions.

## `compatibility-witness.receipt`

Captures:
- host/plugin target facts;
- interface/API version facts;
- load verdict (`loads_cleanly`, `loads_with_downgrade`, `rejected_version_mismatch`, `rejected_layout_mismatch`, `manual_review_required`);
- diagnostics coverage (`load_time_layout_checks`, `symbol_lookup_only`, `integration_test_only`, `manual_review_required`);
- evidence basis and mismatch classes.

# Suggested commands

- `cargo native-plugin init`
- `cargo native-plugin receipt`
- `cargo native-plugin import-abi-stable`
- `cargo native-plugin gate`
- `cargo native-plugin doctor`
- `cargo native-plugin diff old.json new.json`
- `cargo native-plugin bundle`

# Compatibility story

- Stable Rust first for receipt schemas and bundle logic.
- Must import `abi_stable` root-module and prefix-type facts when present.
- Must tolerate lower-level `libloading` integrations while classifying them honestly.
- Must distinguish native in-process plugins from process-isolated or serialized fallback plugins.
- Should classify reload/unload support conservatively by default.
- Should allow custom host/plugin checkers to attach extra evidence rather than forcing one universal runtime model.

# Conformance & fixtures

- one fixture where an `abi_stable` prefix module adds an optional field and the surface remains additively extensible;
- one fixture where `libloading`-style dynamic loading forces an explicit `unsupported` or `process_restart_only` unload posture;
- one fixture where a serialized fallback boundary is imported honestly rather than mislabeled as a full stable-ABI surface;
- one fixture where optional capability negotiation downgrades the active plugin surface without pretending nothing changed.

# Path to boring stability

- Freeze receipt vocabulary before inventing a universal hot-reload manager.
- Start with capture/import/diff/gate workflows rather than a whole plugin marketplace.
- Keep compatibility witnesses and lifecycle truth explicit before adding more codegen or scaffolding sugar.
- Require explicit loss/lifecycle receipts before blessing reload or unload claims.
- Prefer tiny bundles that can be attached to release review or support tickets.

# Non-goals

- Not a replacement for `abi_stable`, `libloading`, or lower-level FFI crates.
- Not a new stable Rust ABI.
- Not a full sandbox or policy-engine product.
- Not a universal marketplace or plugin registry.
- Not a promise that arbitrary hand-rolled dylib contracts can be imported losslessly.

# Architecture & API sketch

```rust
pub enum BoundaryStyle {
    AbiStablePrefixModule,
    AbiStableTraitObject,
    SerializedBoundary,
    CAbiShim,
    ManualReviewRequired,
}

pub fn capture_native_plugin_receipts(host: &Path, plugin: &Path) -> anyhow::Result<PluginBundleManifest>;
pub fn import_abi_stable_root_module(path: &Path) -> anyhow::Result<AbiSurfaceReceipt>;
pub fn diff_native_plugin_contract(old: &PluginBundleManifest, new: &PluginBundleManifest) -> PluginDiff;
```

Bundle draft: `abi-surface.receipt.json`, `capability-negotiation.receipt.json`, `lifecycle-posture.receipt.json`, `compatibility-witness.receipt.json`, `plugin.summary.md`, `plugin.diff.json`, `plugin-bundle.manifest.json`.
