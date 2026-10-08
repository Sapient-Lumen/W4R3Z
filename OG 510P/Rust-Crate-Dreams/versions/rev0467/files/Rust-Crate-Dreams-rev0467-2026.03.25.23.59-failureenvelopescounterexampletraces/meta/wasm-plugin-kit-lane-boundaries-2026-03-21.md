# wasm-plugin-kit lane boundaries — 2026-03-21

This note keeps **P-0002 Wasm Plugin Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable Wasm plugin support contract** over one plugin/host relationship.
It should answer:

- which package/world or host-function surface is authoritative,
- which capabilities the host grants,
- what execution budget and interruption posture applies,
- and whether instance state is fresh, pooled, or reused.

## Keep this distinct from nearby lanes

### Distinct from `cargo component`

`cargo component` is build/publish tooling.
`P-0002` is the receiver-facing contract above it.

### Distinct from Wasmtime or Extism runtimes

Wasmtime and Extism are runtime substrate.
`P-0002` is the small review vocabulary above them.

### Distinct from `P-0081 Stable Plugin Host Kit`

`P-0081` is the native ABI-stable dynamic-library lane.
`P-0002` is the Component Model / Wasm capability-based plugin lane.

### Distinct from component artifact conformance/distribution lanes

Component artifact conformance and OCI/package distribution are adjacent substrate.
`P-0002` stays focused on what another team can review about **interface**, **capabilities**, **budgets**, and **lifecycle**.

### Distinct from generic sandbox/isolation crates

This lane is not a general-purpose seccomp/jail/VM policy engine.
It should import sandbox facts when available, not replace them.

## Four truths this lane must keep separate

1. **plugin interface** — WIT package/world identity, binding basis, and compatibility class;
2. **capability grant** — filesystem/network/host-function/configuration rights;
3. **execution budget** — fuel/epoch/timeout/memory/pool/store-limiter basis;
4. **instance lifecycle** — fresh, pooled, long-lived, or host-externalized state posture.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a raw `.wasm` module and a Component Model world contract,
- a successful `cargo component build` and a stable long-term interface promise,
- “WASI enabled” and a precise capability grant,
- host timeout and deterministic fuel budget,
- pooled warm instance reuse and fresh per-call isolation,
- or registry/package names and exact fetch/provenance routes.

## Preferred artifact vocabulary

- `plugin-interface.receipt`
- `capability-grant.receipt`
- `execution-budget.receipt`
- `instance-lifecycle.receipt`
- `plugin-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
