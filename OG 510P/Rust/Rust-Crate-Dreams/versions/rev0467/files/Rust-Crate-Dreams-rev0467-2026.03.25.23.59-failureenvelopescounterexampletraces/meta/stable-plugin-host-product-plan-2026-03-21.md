
# Stable Plugin Host Kit — product plan (2026-03-21)

This note sharpens **P-0081 Stable Plugin Host Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0081** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a new stable Rust ABI, a universal hot-reload runtime, or a plugin marketplace.
It should provide one boring, reviewable **native plugin support contract** above today’s `abi_stable`, `libloading`, and adjacent FFI substrate.

`0.1` should make four things first-class:

1. **ABI surface** — which root module / symbol surface / boundary style is actually authoritative;
2. **capability negotiation** — which required and optional APIs exist and how downgrades behave;
3. **lifecycle posture** — whether loading is startup/on-demand/process-isolated, whether unload exists, and how reload really works;
4. **compatibility witness** — what target/version/layout checks or integration evidence justify trusting the plugin.

## What `0.1` should provide other people

- one compact `abi-surface.receipt.json`
- one compact `capability-negotiation.receipt.json`
- one compact `lifecycle-posture.receipt.json`
- one compact `compatibility-witness.receipt.json`
- one compact `plugin-bundle.manifest.json`
- one compact `plugin.summary.md`
- one compact `plugin.diff.json`
- a portable review/support bundle

## Commands worth shipping first

- `cargo native-plugin receipt`
- `cargo native-plugin import-abi-stable`
- `cargo native-plugin gate`
- `cargo native-plugin doctor`
- `cargo native-plugin diff`
- `cargo native-plugin bundle`

## What to import, not reinvent

- `abi_stable` root-module, prefix-type, and load-check facts when present
- lower-level `libloading` route facts and platform-specific loader paths when that is the real substrate
- hand-written serialized fallback boundaries when the host explicitly chose them
- test-fixture or conformance evidence from host/plugin integration suites
- target/platform/toolchain metadata only as imported provenance, not as a bespoke build system

## Suggested `0.1` doctor warnings

- `root_module_missing_authoritative_surface_receipt`
- `serialized_boundary_claimed_as_full_abi_surface`
- `unload_claim_present_without_lifecycle_basis`
- `restart_only_reload_presented_as_hot_reload`
- `optional_capabilities_missing_downgrade_receipt`
- `symbol_lookup_only_claimed_as_layout_checked`
- `target_or_api_version_drift_missing_compatibility_witness`

## First proving-ground scenarios

1. **An `abi_stable` prefix/root module adds an optional field and remains additively extensible rather than forcing a fake breaking-change panic**
2. **A `libloading`-based host must record that unload is unsupported or restart-only instead of bluffing true hot reload**
3. **A serialized fallback boundary is useful, but still needs to be labeled as a different surface class from a typed stable-ABI module**
4. **Optional capabilities / API probes downgrade the active surface and therefore need an explicit negotiation receipt**

## What to leave for later

- marketplace / registry UX
- full codegen/scaffolding suites for every plugin shape
- organization-specific sandbox policy engines
- generalized cross-language bindings-generation strategy
- universal hot reload for arbitrary native plugins
- large hosted conformance farms
