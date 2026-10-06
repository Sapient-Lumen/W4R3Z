# RFC-0121: Policy modules as WebAssembly (optional)

Status: **draft**

## Motivation

DeriveBSD policy needs to scale from a safe baseline (schema + matchers) to richer org policy
without embedding a general-purpose language into the core planner/activator.

A Wasm module lane offers:
- digest-pinned, sandboxable policy evaluation
- language choice via compilation (Rego→Wasm, Cedar→Wasm, bespoke)
- a small, stable evaluation ABI

## Goals

- Allow policy bundles to reference Wasm policy modules.
- Keep policy evaluation deterministic and explainable.
- Keep the host runtime surface minimal (no ambient I/O).

## Non-goals

- Mandating one policy language.
- Shipping a feature-rich runtime at v0.
- Allowing policy modules to perform side effects.

## Proposal

### Artifact: policy module

A `policy.module` is a content-addressed artifact with:
- module digest
- ABI version
- declared hostcall set
- compiler metadata (optional)

### ABI v0 (sketch)

- Input: canonical JSON bytes (`context`, `data`)
- Output: canonical JSON bytes (`result`)

The result must include at least:
- `decision: allow|deny`

Optional:
- `obligations[]`
- bounded `trace`

### Execution constraints

- no network
- no filesystem
- fuel + memory limits
- pinned runtime (version is selected by trust policy)

### Integration

- Policy engine runs baseline schema policy first.
- Optional: invoke Wasm modules as an additional backend.
- Decision trace records which modules were consulted and their digests.

## Evidence

- `policy.module` evidence object describes the module and binds it to a signer.
- Policy decision records include the module digests used.

## References

- OPA Wasm docs: https://openpolicyagent.org/docs/wasm
- OPA integration patterns: https://openpolicyagent.org/docs/integration
