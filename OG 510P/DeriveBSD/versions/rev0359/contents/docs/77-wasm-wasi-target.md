# Wasm/WASI target kind (optional): capability-sandboxed payloads

Wasm/WASI is a compelling “blast-radius reducer” for certain services:
- capability-oriented APIs
- strong sandbox defaults
- portable artifacts

## Target model
A `wasm` artifact includes:
- wasm module(s) blobs (content-addressed)
- a WASI interface profile (which syscalls/capabilities are permitted)
- runtime manifest describing:
  - filesystem preopens (by digest-backed mounts)
  - env vars (non-secret)
  - network permissions (deny by default)
  - resource profile (docs/68)

## Runtimes
DeriveBSD can support one or more runtimes:
- Wasmtime
- WasmEdge
- others (policy-controlled)

## Policy posture
- deny network by default
- explicit filesystem preopens only
- forbid dynamic module fetch at runtime

References:
- WASI intro and interface proposals in `docs/32-curated-references.md`.

See RFC-0050.

Last updated: 2026-02-23
