
# stable-plugin-host lane boundaries — 2026-03-21

This note keeps **P-0081 Stable Plugin Host Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable native plugin support contract** over one host/plugin relationship.
It should answer:

- which ABI surface is authoritative,
- how optional capabilities are negotiated,
- what load / unload / reload posture actually applies,
- and what compatibility witness another team can trust.

## Keep this distinct from nearby lanes

### Distinct from `P-0002 Wasm Plugin Kit`

`P-0002` is the Wasm Component / capability-sandboxed plugin lane.
`P-0081` is the native dynamic-library / ABI-surface lane.

### Distinct from raw `abi_stable` / `libloading`

Those crates are substrate.
`P-0081` is the receiver-facing contract above them.

### Distinct from generic FFI / bindings crates

`safer_ffi`, `cglue`, and `interoptopus` are adjacent FFI tools.
`P-0081` is specifically about one reviewable host/plugin contract for runtime-loaded native plugins.

### Distinct from sandbox / process-isolation policy crates

This lane may import isolation facts, but it is not a general-purpose sandbox policy engine.

### Distinct from a hypothetical universal stable Rust ABI effort

`P-0081` is the pragmatic “what can teams ship today?” lane.
It should not promise a language-level stable ABI.

## Four truths this lane must keep separate

1. **ABI surface** — root-module / symbol authority, boundary style, and extensibility posture;
2. **capability negotiation** — required vs optional APIs, negotiation route, downgrade policy;
3. **lifecycle posture** — load mode, unload truth, reload route, and state persistence;
4. **compatibility witness** — version/target/layout checks, diagnostics coverage, and mismatch evidence.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a hand-rolled dylib symbol table and an `abi_stable` root module,
- a serialized message boundary and a typed stable-ABI surface,
- restart-only replacement and true hot reload,
- dropping a loader handle and a proved-safe unload story,
- “plugin loaded in CI” and a portable compatibility witness,
- or optional capability probes and a fixed guaranteed API surface.

## Preferred artifact vocabulary

- `abi-surface.receipt`
- `capability-negotiation.receipt`
- `lifecycle-posture.receipt`
- `compatibility-witness.receipt`
- `plugin-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
