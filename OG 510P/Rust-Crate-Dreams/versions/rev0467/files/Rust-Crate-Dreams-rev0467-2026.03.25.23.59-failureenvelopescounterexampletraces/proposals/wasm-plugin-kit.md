---
id: P-0002
title: Wasm Plugin Kit — capability-based plugins via the Component Model
status: idea
domains: [wasm, plugins, sandboxing, extensibility, components, tooling]
last_reviewed: 2026-03-21
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://docs.wasmtime.dev/wasip2-plugins.html
  - https://docs.wasmtime.dev/api/wasmtime/component/index.html
  - https://component-model.bytecodealliance.org/design/packages.html
  - https://component-model.bytecodealliance.org/design/worlds.html
  - https://component-model.bytecodealliance.org/composing-and-distributing/distributing.html
  - https://github.com/bytecodealliance/cargo-component
  - https://extism.org/docs/concepts/plug-in-system/
  - https://extism.org/docs/concepts/manifest/
  - https://extism.org/docs/concepts/configuration/
  - https://docs.wasmtime.dev/examples-interrupting-wasm.html
  - https://docs.wasmtime.dev/api/wasmtime/struct.Config.html
  - https://docs.wasmtime.dev/api/wasmtime/struct.PoolingAllocationConfig.html
  - https://docs.rs/extism/latest/extism/struct.Manifest.html
  - https://docs.rs/extism/latest/extism/struct.Pool.html
---

# Problem

Rust now has serious plugin substrate for WebAssembly, but it still lacks one boring crate that lets teams publish an **honest support contract** for plugins.

Today the substrate is real:

- the Rust project has a 2026 flagship goal to improve the state of Wasm Component support in Rust;
- Wasmtime now documents an application-with-plugins pattern using WebAssembly components;
- Wasmtime's component embedding API can generate Rust bindings from a WIT world and wire those bindings through a `Linker`;
- the component-model docs now make **packages**, **worlds**, and **distribution/fetching** first-class concepts;
- `cargo component` can scaffold, add interface deps, update lock state, and publish to a registry, but it is still explicitly experimental;
- Extism shows a parallel practical plugin stack with manifests, host-provided configuration, allowlisted hosts/paths, timeouts, and plugin pools.

But those pieces still do **not** by themselves answer the questions downstream users actually need answered:

- which **WIT package/world** defines the plugin contract,
- which **capabilities** the host actually grants,
- how **execution budgets** are enforced,
- whether instances are **fresh, pooled, or state-reusing**,
- and whether a plugin bundle is a stable component contract or just a tool/runtime-specific artifact.

The missing crate is therefore **not** another runtime, another registry, or another plugin marketplace.
It is a **Wasm Plugin Kit** that makes plugin support posture reviewable via receipts.

# Main judgment

This lane is now worthy because plugin systems touch an extreme variety of real Rust use cases:

- editor and CLI extensions,
- enterprise workflow and SaaS rule plugins,
- user-defined functions and policy engines,
- game mods and simulation components,
- desktop app extensions,
- edge/server embedded business logic,
- and cross-language extension points where the host is Rust but guest languages vary.

The current ecosystem already proves that “plugins” is too vague.
A worthy crate contribution should not merely load a `.wasm` file and call a function.
It should help other people answer four review questions with stable artifacts:

1. **What interface world/package is this plugin actually targeting?**
2. **What capability grants does the host really make?**
3. **What execution budget and interruption model applies?**
4. **What happens to instance state across calls, pooling, and teardown?**

# What it provides

- `plugin-interface.receipt.json` — WIT package/world identity, binding basis, component-vs-module class, import/export surface, and compatibility posture.
- `capability-grant.receipt.json` — filesystem/network/host-function/configuration/WASI posture and whether grants are explicit or inferred.
- `execution-budget.receipt.json` — interrupt basis, determinism class, memory/instance budget basis, and concurrency posture.
- `instance-lifecycle.receipt.json` — fresh-vs-pooled-vs-long-lived instance mode, state persistence, teardown basis, and concurrency usage posture.
- `plugin-bundle.manifest.json` — hashes, registry/package route, runtime/tooling assumptions, and attached receipts.
- `plugin.summary.md` — one human summary suitable for review or support handoff.
- `plugin.diff.json` — compares interface/capability/budget/lifecycle posture across plugin releases.
- `cargo plugin receipt` — emits receipts from a host/plugin workspace.
- `cargo plugin gate` — fails builds or reviews on missing truths.
- `cargo plugin diff` — compares two plugin contracts.
- `cargo plugin bundle` — emits one small support/review archive.

# What the crate should provide other people

1. **Interface exactness** so a host can say which package/world or host-function surface is authoritative.
2. **Capability honesty** so “sandboxed” does not hide broad WASI or host-function reach.
3. **Budget honesty** so timeouts, fuel, epochs, memory caps, and pool limits are not blurred together.
4. **Lifecycle honesty** so pooled warm instances do not masquerade as fresh isolated executions.
5. **Loss-aware imports** so Extism-style plugins, Wasmtime components, and raw module imports can coexist without fake equivalence.
6. **One boring review vocabulary** that product teams, security reviewers, runtime engineers, and plugin authors can all share.

# Personas / who it’s for

- application/framework authors building extension points
- platform/security teams reviewing untrusted code execution
- SaaS vendors exposing user-defined functions
- game/tool authors designing mod/plugin ecosystems
- infra teams standardizing plugin deployment and support bundles
- plugin authors who need a stable review target

# Users & user stories

- **Framework author:** “I need third-party plugins, but I want the interface world and capability grants to be explicit and reviewable.”
- **Security reviewer:** “Tell me whether this plugin can touch the filesystem, network, or broad host functions, and how those grants were derived.”
- **Infra owner:** “I need to know whether timeouts are deterministic fuel budgets, coarse epoch interrupts, or just host-side waits.”
- **Product maintainer:** “If instances are pooled or warm-reused, I need that truth visible in support bundles.”
- **Plugin author:** “I want one portable contract for compatibility review without having to teach every host my internal build stack.”

# Prior art (and why it’s insufficient)

- Wasmtime provides powerful component embedding and plugin examples, but not one receiver-facing support contract.
- The component-model documentation defines WIT packages, worlds, and distribution concepts, but does not define one Rust review/bundle crate above them.
- `cargo component` is promising build tooling, but it explicitly says it is experimental and may break projects as the component model evolves.
- Extism is a practical plugin ecosystem with manifests, config, and pools, but its manifest/runtime shape is not identical to a full WIT-world/component contract.
- Native ABI-stable plugin strategies remain useful, but they answer a different lane from capability-based Component Model plugins.

What remains missing is the **interface world + capability grant + execution budget + instance lifecycle** layer above today’s runtimes and build tools.

# Design goals

1. **Contract-first, not runtime-first.** Start from what another team can review.
2. **WIT-aware core.** Package/world identity must be first-class when available.
3. **Capability explicitness.** Default-deny and allowlist posture should survive export.
4. **Budget exactness.** Fuel, epochs, host timeout, memory, and pool limits must stay separate.
5. **Lifecycle honesty.** Fresh instance, pooled reuse, and long-lived instance modes must not blur together.
6. **Import, don’t replace.** Build above Wasmtime, Extism, and `cargo component` rather than forking them.
7. **Loss-aware classification.** Raw `.wasm` modules, components, and host-specific manifests should not masquerade as one universal contract.
8. **Manual-review over fake certainty.** When a source cannot justify a claim, emit `manual_review_required`.
9. **Small bundles.** `0.1` should fit code review, CI, and support handoff.

# MVP surface

- Minimal types:
  - `PluginInterfaceReceipt`
  - `CapabilityGrantReceipt`
  - `ExecutionBudgetReceipt`
  - `InstanceLifecycleReceipt`
  - `PluginBundleManifest`
  - `PluginDiff`
- Minimal functions:
  - `capture_plugin_receipts()`
  - `import_extism_manifest()`
  - `import_component_world()`
  - `diff_plugin_contract()`
  - `bundle_plugin_contract()`
- Feature flags:
  - `serde`
  - `wasmtime-component`
  - `extism-import`
  - `cargo-component-import`
  - `cli`

# First-class review objects

## `plugin-interface.receipt`

Captures:
- whether the plugin is a Component Model component, an Extism-style module, or another/manual import class;
- WIT package and world identity when available;
- binding basis (`wasmtime_bindgen`, `wit_bindgen_guest`, `extism_pdk`, `manual_host_api`);
- declared imports/exports;
- compatibility class (`component_exact`, `component_adapter_required`, `host_specific`, `experimental_tooling`, `manual_review_required`).

## `capability-grant.receipt`

Captures:
- WASI enablement posture,
- filesystem grants,
- network grants,
- host-function/API reach,
- configuration mutability,
- and whether grants were declared by manifest, linker wiring, or manual policy.

## `execution-budget.receipt`

Captures:
- interrupt basis (`fuel`, `epoch`, `timeout_only`, `none`),
- determinism class,
- memory budget basis,
- pooling/store-limiter basis,
- and concurrency posture.

## `instance-lifecycle.receipt`

Captures:
- fresh-per-call, fresh-per-request, pooled-reuse, or long-lived instance mode;
- whether plugin state is ephemeral, reused, or externalized in the host;
- teardown basis (`drop_instance`, `pool_return`, `process_reset`, `manual_review_required`);
- and single-threaded vs host-pooled concurrency posture.

# Suggested commands

- `cargo plugin receipt`
- `cargo plugin import-extism`
- `cargo plugin import-component`
- `cargo plugin gate`
- `cargo plugin diff old.json new.json`
- `cargo plugin bundle`

# Compatibility story

- Stable Rust first for receipt schemas and bundle logic.
- Must classify `cargo component` artifacts without pretending the upstream tool is already stable forever.
- Must import Extism manifests and runtime posture without rewriting them as full WIT-world certainty.
- Must allow raw `.wasm` modules to exist, but downgrade interface exactness when component/world identity is missing.
- Must leave room for future OCI/package provenance without requiring a registry in `0.1`.
- Should treat native ABI-stable plugin hosts as an adjacent lane, not a hidden fallback story.

# Conformance & fixtures

- one fixture where a `cargo component` project builds successfully but still carries `experimental_tooling` compatibility posture
- one fixture where Extism allowlisted hosts/paths and immutable config become an explicit capability receipt rather than a vague “sandboxed plugin” claim
- one fixture where fuel and epochs are kept separate because only fuel provides deterministic interruption semantics while epochs trade that for speed
- one fixture where pooled/warm instance reuse requires an explicit lifecycle receipt instead of pretending every call is fresh

# Path to boring stability

- Freeze receipt vocabulary before inventing a full plugin marketplace or universal runtime layer.
- Start with capture/import/diff/gate workflows instead of fancy registries or automatic migrations.
- Keep native ABI-stable plugins as a separate adjacent lane.
- Require explicit loss/capability/budget/lifecycle receipts before blessing “safe plugin support” claims.
- Prefer tiny scenario bundles over sprawling demos.

# Non-goals

- Not a replacement for Wasmtime, Wasmer, or Extism runtimes.
- Not a plugin marketplace, package registry, or update service.
- Not a generic OCI distribution client.
- Not a universal sandbox policy engine.
- Not a promise that every `.wasm` module can be upgraded into a full Component Model contract.
- Not a replacement for native ABI-stable plugin systems.

# Architecture & API sketch

```rust
pub struct PluginInterfaceReceipt {
    pub subject: String,
    pub interface_kind: InterfaceKind,
    pub package_id: Option<String>,
    pub world_id: Option<String>,
    pub binding_basis: BindingBasis,
    pub compatibility_class: CompatibilityClass,
}

pub struct CapabilityGrantReceipt {
    pub wasi_enabled: WasiPosture,
    pub filesystem_grant: FilesystemGrant,
    pub network_grant: NetworkGrant,
    pub host_function_grant: HostFunctionGrant,
    pub config_mutability: ConfigMutability,
}

pub fn capture_plugin_receipts(subject: &Path) -> Result<PluginBundle>;
pub fn import_extism_manifest(path: &Path) -> Result<PluginBundle>;
pub fn import_component_world(path: &Path) -> Result<PluginBundle>;
pub fn diff_plugin_contract(old: &PluginBundle, new: &PluginBundle) -> PluginDiff;
```

# Maintenance & governance plan

- Keep the receipt vocabulary compact and versioned.
- Publish tiny fixture families for Wasmtime component plugins, Extism manifests, and raw module/manual imports.
- Treat distribution/registry/provenance as a later layer above the core receipts.
- Require every “sandboxed” or “safe to run” claim to carry explicit capability and budget receipts.
- Prefer `manual_review_required` whenever interface authority, state reuse, or capability derivation is ambiguous.
