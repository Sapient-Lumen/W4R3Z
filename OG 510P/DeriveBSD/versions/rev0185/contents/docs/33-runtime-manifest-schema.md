# Runtime manifest schema (microVM)

The runtime manifest is the **backend-agnostic contract** between:
- Derive planning (Spec/Lock/Plan) and
- runtime realization (`derive-vmmd` + hypervisor backend)

It must be **hashable**, **signable**, and stable across backends.

## Design goals
- Deterministic digest for policy + audit + provenance
- Explicit “no surprise devices”: virtio baseline; passthrough is opt-in
- Separation of concerns:
  - image content (artifact) is immutable
  - instance config is injected (non-secret)
  - secrets flow via a separate channel (never baked)

## Canonicalization and digest
Define:
- `manifest_digest = sha256( JCS(manifest_json) )`

Where JCS is the JSON Canonicalization Scheme (RFC 8785) to avoid ambiguity from key order/whitespace.
(See `docs/32-curated-references.md`.)

## Bindings (audit + enforcement)

To support “why/what/where-from” and offline verification, a runtime manifest should carry (or be accompanied by) digests that bind it to the derivation:
- `artifact.digest` (what will run)
- `policy_decision_digest` (why it is allowed) — see `docs/93-policy-decision-records.md`
- `closure_manifest_digest` (what else must exist) — see `docs/90-closure-proof.md`

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

## Policy hooks (v1)
Policy must be able to deny:
- passthrough devices
- bridged networking
- persistent overlays
- specific secret names
- resource requests above ceilings

See RFC-0015.

Last updated: 2026-02-23
