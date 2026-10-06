# Contract registries + API-diff gates (treat every interface as a versioned surface)

DeriveBSD already treats crossings as contracts (RPC endpoints, portal broker APIs, file-shaped control planes, IDL surfaces).
The missing “boring but powerful” substrate is to make **contract drift mechanically reviewable** the same way we’re making kernel UAPI drift reviewable.

> Every stable interface surface is registered. Every change produces a diff. Every diff is classified.

This is an ecosystem feature: it makes it cheap to build tooling (lint, docs, test harnesses, deprecations) that normally arrives years too late.

## Prior art worth stealing

- Fuchsia platform API evolution guidelines (API-level thinking, stability tiers, required review discipline):
  https://fuchsia.dev/fuchsia-src/development/api/evolution

- Fuchsia API levels as “snapshot of the platform surface” (components target a level; runtime enforces support):
  https://fuchsia.dev/fuchsia-src/concepts/versioning/api_levels

- Google AIP-180 (a crisp compatibility taxonomy for API evolution):
  https://google.aip.dev/180

- Protobuf “updating definitions without breaking” (field-number discipline as a practical compat hack):
  https://protobuf.dev/overview/

- gRPC core versioning guide (explicit compatibility constraints and “EXPERIMENTAL can break” discipline):
  https://grpc.github.io/grpc/core/md_doc_versioning.html

## The registry (derived artifact)

Define two canonical objects:

- `contract.registry` — compiled, normalized list of *stable* contract surfaces
- `contract.diff` — a classification of deltas between two registries

These are to *interfaces* what `closure.proof` is to *dependencies*: a compact, digestable, auditable summary.

### What counts as a “contract surface”

At minimum:

- RPC methods (local and remote): object-capability RPC endpoints, broker calls, CapTP/OCapN actions
- Portal broker APIs (e.g., file picker, screencast, crypto ops, device grants)
- File-shaped control planes (if “writing a file” triggers privileged action, it’s an interface)
- Stable schema objects (e.g., receipts/plans that cross trust domains)

Non-goal: registering every internal function. This is about **crossings that other components depend on**.

### Suggested registry entry shape

```json
{
  "id": "portal.crypto.sign",
  "surface": "rpc|portal|file|schema",
  "stability": "stable|provisional|deprecated|internal",
  "owner": "brokers/crypto",
  "since": "2026-02-27r104",
  "contract_digest": "sha256:…",
  "idl": {
    "type": "wit|json-schema|protobuf|manual",
    "ref": "spec/crypto.op.request.schema.json",
    "digest": "sha256:…"
  },
  "risk_tags": ["parses_untrusted_input", "returns_authority"],
  "tests": {
    "conformance": "tests/contracts/portal.crypto.sign/*",
    "fuzz": "fuzz/contracts/portal_crypto_sign"
  }
}
```

## The diff gate (CI posture)

A required check for any PR that changes contract-bearing code or schemas:

1) Compile `contract.registry` for `main` and for the PR.
2) Compute `contract.diff`.
3) Classify each delta:

- **compatible**: additive, old clients continue to work (new optional fields; new methods marked provisional; extended enums with unknown handling)
- **breaking**: removal, incompatible semantics, renames without aliasing, tightening that breaks old callers
- **suspicious**: new parser, new authority, “returns authority” expansion, new ambient side effects
  - If the interface introduces a meaningful untrusted decode surface, link it into `parser.registry` / `parser.diff` (see `docs/376-parser-surface-registry-and-fuzz-gates.md`).

4) Require explicit approvals for:
- breaking
- suspicious
- “stable surface now depends on unstable surface”

This plugs into:
- blast-radius diffs (`docs/106-blast-radius-diff.md`)
- authority diffs (`docs/366-capability-graphs-and-authority-diff-surfaces.md`, schema `spec/authority.diff.schema.json`)
- lint reports + contract testing (`docs/237-lint-reports-and-contract-testing.md`)

## Interaction with other registries

- Kernel UAPI has its own registry/diff: `docs/362-uapi-surface-registry-and-compat-gates.md`.
- The **authority graph** should be able to point at contract ids/digests for edges like `rpc.endpoint` and `portal.session`.

The key rule:

> A new stable contract surface is a “new authority edge” unless proven otherwise.

## Wiring (schemas + examples)

- Contract registry schema: `spec/contract.registry.schema.json` (example: `spec/examples/contract.registry.json`)
- Contract diff schema: `spec/contract.diff.schema.json` (example: `spec/examples/contract.diff.json`)
- UAPI registry schema: `spec/uapi.registry.schema.json` (example: `spec/examples/uapi.registry.json`)
- UAPI diff schema: `spec/uapi.diff.schema.json` (example: `spec/examples/uapi.diff.json`)

## Related docs

- Contract language option (WIT): `docs/356-wasm-component-model-and-wit-contracts.md`
- Unit manifests as contract declarations: `docs/344-derive-unit-manifests-and-capability-routing.md`
- Remote capability discipline (optional): `docs/353-captp-ocapn-remote-capabilities.md`

Last updated: 2026-02-27r104
