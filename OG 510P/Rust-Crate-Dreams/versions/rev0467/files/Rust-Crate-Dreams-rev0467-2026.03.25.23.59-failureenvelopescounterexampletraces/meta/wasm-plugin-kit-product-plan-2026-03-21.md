# Wasm Plugin Kit — product plan (2026-03-21)

This note sharpens **P-0002 Wasm Plugin Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0002** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to become a new Wasm runtime, a plugin marketplace, or a universal package/distribution system.
It should provide one boring, reviewable **plugin support contract** above today’s Wasmtime component tooling, component-model/WIT docs, `cargo component`, and Extism substrate.

`0.1` should make four things first-class:

1. **plugin interface** — which WIT package/world or host-function surface is actually authoritative;
2. **capability grant** — which filesystem/network/host-function/configuration rights really exist;
3. **execution budget** — how time, interruption, memory, and pool/store limits are actually enforced;
4. **instance lifecycle** — whether calls get fresh instances, pooled warm instances, or long-lived stateful ones.

## What `0.1` should provide other people

- one compact `plugin-interface.receipt.json`
- one compact `capability-grant.receipt.json`
- one compact `execution-budget.receipt.json`
- one compact `instance-lifecycle.receipt.json`
- one compact `plugin-bundle.manifest.json`
- one compact `plugin.summary.md`
- one compact `plugin.diff.json`
- a portable review/support bundle

## Commands worth shipping first

- `cargo plugin receipt`
- `cargo plugin import-component`
- `cargo plugin import-extism`
- `cargo plugin gate`
- `cargo plugin diff`
- `cargo plugin bundle`

## What to import, not reinvent

- WIT package/world identity from component-model tooling and generated bindings
- Wasmtime component `bindgen!`, `Linker`, and component/runtime assumptions when present
- `cargo component` build and package metadata, but with explicit experimental-tooling posture
- Extism manifests, allowlists, WASI enablement, config posture, and pool/runtime hints
- OCI/package/digest data only as imported provenance, not as a required registry client

## Suggested `0.1` doctor warnings

- `cargo_component_experimental_used_as_stable_contract`
- `raw_module_claims_wit_world_without_basis`
- `sandbox_claim_exceeds_manifest_or_linker_receipt`
- `timeout_only_claimed_as_deterministic_budget`
- `pooled_instance_reuse_missing_lifecycle_receipt`
- `registry_alias_without_digest_or_fetch_route`
- `host_function_surface_missing_capability_scope`

## First proving-ground scenarios

1. **A `cargo component` project builds, but the resulting contract still needs `experimental_tooling` compatibility posture because the upstream tool explicitly warns of instability**
2. **An Extism manifest with `allowed_hosts`, `allowed_paths`, immutable host config, and timeout becomes one explicit capability receipt rather than a vague “sandboxed plugin” claim**
3. **Fuel and epochs are kept separate because Wasmtime documents fuel as deterministic interruption while epochs are coarser but faster**
4. **Pooling and warm-slot reuse require an explicit lifecycle receipt instead of pretending each call gets a fresh isolated plugin instance**

## What to leave for later

- a plugin marketplace or registry UX
- automatic upgrade/migration shims between worlds
- full attestation and signature policy engines
- a universal runtime abstraction across all Wasm hosts
- deep organization-specific sandbox policy languages
- large hosted conformance labs or plugin analytics backends
