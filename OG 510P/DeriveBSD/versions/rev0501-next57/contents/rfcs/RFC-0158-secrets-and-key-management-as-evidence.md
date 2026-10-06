# RFC-0158: Secrets and key management as evidence (secret-policy / grant / snapshot / receipt / events)

Status: draft  
Last updated: 2026-02-24

## Problem
DeriveBSD is building an “ops evidence spine”:
- plans and changes are explicit objects
- outcomes are receipts
- events are typed and queryable

Secrets are where systems usually abandon these principles:
- plaintext config drift in `/etc`
- copy-paste deploy pipelines
- incident bundles that accidentally leak credentials
- no coherent audit story for rotation and access

Greenfield advantage: make secret handling **boring, explicit, and auditable**.

## Goals
- A signed `secret-policy` declares the **inventory** and **rules** for secrets.
- Secret bytes are never embedded in configs; configs reference secret ids/refs.
- Access requires an explicit, time-bounded `secret-grant` (lease model).
- The system can produce a safe `secret-snapshot` that never includes secret bytes.
- Secret actions emit `secret-receipt` evidence; access/denial emits `secret-event`.
- Incident bundles include safe metadata by default (snapshot + receipts), not secrets.

## Non-goals
- Replacing enterprise secret stores (Vault, cloud KMS) as the authoritative source.
- Defining a single universal “secret injection” runtime for all applications.
- Perfect defense if the host is fully compromised (we focus on reducing blast radius and raising the audit bar).

## Data model

### secret-policy
Declares:
- list of secrets with:
  - `secret_id`, `class` (password, token, tls-key, ssh-key, opaque)
  - `source`:
    - `sealed-blob` (encrypted object in store)
    - `tpm2-sealed` (TPM-bound unseal)
    - `provider` (external store)
  - rotation expectation: `rotation_interval_days` (or `lease_seconds`)
  - access rules: selectors (service_id, workload labels) + allowed delivery modes
  - optional attestation requirements (bind access to measured boot evidence)

### secret-grant
A scoped authorization for the credential broker:
- `secret_id`
- subject identity (service_id/workload identity)
- allowed operations (`read`, `materialize`, `rotate`)
- delivery mode constraints (file/memfd/env/fd)
- TTL, optional max-reads
- optional `boot_attestation_digest` binding

This is intentionally analogous to portal leases.

### secret-receipt
Evidence emitted for:
- provisioning (initial materialization)
- rotation
- revoke
- unseal/fetch attempt (optional)

Contains:
- `action`, `result`
- provider backend name
- version/lease metadata
- references to related events and the triggering change-set step

Never contains secret bytes.

### secret-snapshot
A safe, compact query surface:
- configured secret ids
- status per secret (ok/expired/unseal-failed/missing)
- last rotated, next due
- pointers to latest receipts

### secret-event
Typed event record in the structured journal:
- `secret.access.granted` / `secret.access.denied`
- `secret.materialized`
- `secret.rotation.*`

Payloads are metadata-only and redactable.

## Apply semantics

### Where policy comes from
- Fleet policy: org-signed `secret-policy` (preferred)
- Derived policy: compiled from service manifests (hints) but must be re-signed or policy-approved

### How secrets are delivered
DeriveBSD uses a **credential broker** (factotum-ish):
- services do not read a global `/etc/secrets`
- services request credentials via a narrow API
- supervision supplies grants and staging paths

Delivery modes:
- `memfd`/FD passing (preferred; avoids filesystem)
- `ramfs`/tmpfs file staged with tight perms
- environment variables (discouraged; permitted only with policy and redaction rules)

### Change orchestration
`change-set` adds an `apply-secrets` step:
- validates policy
- pre-fetches/unseals required secrets for the target generation
- emits receipts
- optionally requires a “secret health gate” (snapshot checks)

### Rotation
Rotation can be driven by:
- scheduled policy
- explicit change-set step
- provider lease expiry

Rotation emits:
- `secret-receipt` + `secret-event`
- optional incident bundle capture on repeated failure

## Security / privacy
- By default, secrets are never written to disk unencrypted.
- Incident bundles must not include secret bytes unless there is an explicit export grant and policy allows.
- Events/receipts are metadata-only; redaction transforms apply at export/view time.
- Access logs can leak sensitive structure; keep them coarse, policy-gated, and tenant-aware.

## Integrations
- `docs/151-factotum-style-credential-broker.md`: broker model inspiration.
- `docs/214-service-supervision-health-as-evidence.md`: supervision supplies grants/staging.
- `docs/215-structured-event-log-as-evidence.md`: secret events become first-class journal records.
- `docs/216-incident-snapshots-and-support-bundles.md`: include snapshot/receipts, not secret bytes.
- `docs/219-change-sets-and-apply-engine.md`: `apply-secrets` step + correlation.

## Open questions
- Best “safe by default” delivery mode on FreeBSD (memfd vs ramfs vs fd-passing patterns).
- Policy language for access selectors (labels vs explicit service ids).
- Attestation binding: whether to require measured boot evidence for specific secret classes.
- Rotation semantics for long-lived TLS private keys (planned rekey vs on-demand).
