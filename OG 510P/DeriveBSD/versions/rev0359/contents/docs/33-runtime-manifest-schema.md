# Runtime manifest schema (microVM)

The runtime manifest is the **backend-agnostic contract** between:
- Derive planning (Spec/Lock/Plan) and
- runtime realization (`derive-vmmd` + hypervisor backend)

It must be **hashable**, **signable**, and stable across backends.
For component-derived launches, it is the **launch authority object**, not the human-authored source.
The reviewed source is `derive.unit`; the source→compiled provenance join is `derive.unit.compile.receipt`.

## Design goals
- Deterministic digest for policy + audit + provenance
- Explicit “no surprise devices”: virtio baseline; passthrough is opt-in
- Separation of concerns:
  - reviewed human source (`derive.unit`)
  - compiled launch authority (`runtime.manifest`)
  - evidence-only source→compiled join (`derive.unit.compile.receipt`)
  - image content (artifact) is immutable
  - instance config is injected (non-secret)
  - secrets flow via a separate channel (never baked)

## Canonicalization and digest
Define:
- `manifest_digest = sha256( JCS(manifest_json) )`

Where JCS is the JSON Canonicalization Scheme (RFC 8785) to avoid ambiguity from key order/whitespace.
(See `docs/32-curated-references.md`.)

## Bindings (audit + enforcement)

To support “why/what/where-from” and offline verification, a runtime manifest should carry digests that bind it to the derivation:
- `artifact.digest` (what will run)
- `policy_decision_digest` (why it is allowed) — see `docs/93-policy-decision-records.md`
- `closure_manifest_digest` (what else must exist) — see `docs/90-closure-proof.md`
- `runtime_contract.derive_unit_digest` (which reviewed component source drove this launch)
- `runtime_contract.stratum_stack_digest` (which runtime composition stack was selected)
- `runtime_contract.mount_view_digest` (which compiled namespace / mount graph was enforced)

These are inputs to `derive verify` and to runtime hard checks in `derive-vmmd`.

## Minimal v1 fields

- `kind`: `"microvm"`
- `manifest_version`: `"0.1"`
- `artifact`: `{ "digest": "<artifact-digest>", "signing_key_hint": "<optional>" }`
- `backend`: `{ "preferred": "bhyve", "compat": ["bhyve"] }`
- `resources`: `{ "cpu": 1, "mem_mb": 256 }`
- `devices`:
  - `virtio`: `{ "net": true, "blk": true, "rng": true, "console": true }`
  - `passthrough`: `[]` (default empty; enabling requires policy)
- `storage`:
  - `base`: `{ "ref": "<zfs-snap-or-raw>", "mode": "ro" }`
  - `overlay`: `{ "mode": "ephemeral|persistent", "ref": "<zfs-dataset-optional>" }`
- `network`:
  - `attachments`: `[ { "mode": "isolated|nat|bridged", "name": "wan0", "pf_anchor": "derivebsd/vm/<id>" } ]`
- `injection`:
  - `config`: `{ "channel": "metadata-disk", "schema": "derivebsd/meta-v1" }`
  - `secrets`: `{ "channel": "vsock|virtio-console", "schema": "derivebsd/secrets-v1" }`
- `secrets_contract`:
  - `required`: `[]`
  - `optional`: `[]`
  - `rotation`: `{ "reload": "restart|signal|hot", "ttl_s": 0 }`
- `observability`:
  - `console`: `{ "channel": "virtio-console", "port": "derive.console.0" }`
  - `logs`: `{ "sink": "host", "tag": "<instance_id>" }`
- `update`:
  - `strategy`: `"replace-image"` (default; in-guest mutation discouraged)
  - `restart_policy`: `"manual|on-failure|always"`
- `runtime_contract`:
  - `derive_unit_digest`: `"<derive.unit-digest>"`
  - `stratum_stack_digest`: `"<stack-digest>"`
  - `mount_view_digest`: `"<mount-view-digest>"`

## Policy hooks (v1)
Policy must be able to deny:
- passthrough devices
- bridged networking
- persistent overlays
- specific secret names
- resource requests above ceilings

See RFC-0015.

Last updated: 2026-03-08r229
