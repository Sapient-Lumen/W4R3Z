# Secrets and key management as evidence (sealed creds / brokers / receipts)

Most OSes treat secrets as an embarrassing side-channel:
- plaintext sprinkled through `/etc`, env vars, unit files
- ad-hoc “secret injection” wrappers
- post-incident forensics that accidentally exfiltrate credentials

DeriveBSD already has the right pattern for fixing this:
**inventory → explicit policy/plan → receipts → typed events → bounded export**.

Bake secrets in early as a first-class lane so that:
- configs *reference* secrets but do not contain them
- access is mediated by a **credential broker** (no ambient secret files)
- secret materialization emits receipts and can participate in health gates
- incident bundles include safe metadata by default (never raw secret bytes)


Note: certificates/trust bundles are governed in the PKI lane (trust bundle + issuance plans/receipts).
See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`.

Private keys deserve special handling: prefer **non-exportable keys** and brokered crypto operations (sign/decrypt) over "secret files".
See: `docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, `spec/crypto.key.policy.schema.json`, `spec/crypto.op.request.schema.json`, `spec/crypto.op.receipt.schema.json`.

## Lessons worth stealing

### systemd “credentials” (and systemd-creds)
The under-appreciated lesson is not “yet another secret store”. It’s:
- **credentials as named objects**
- optional **TPM2-backed encryption** “that just works”
- delivery into a service via a managed, non-swappable staging area

### TPM2 sealing (optional, for host-bound secrets)
TPM2 gives a practical way to bind a secret to:
- a host identity
- a measured boot state (PCR policies)

For operability notes (PCR brittleness, policy-authorized evolution, unseal receipts), see:
- `docs/272-sealed-secrets-attested-unsealing.md`

This is especially useful for:
- disk unlock keys
- node identity keys
- bootstrap tokens that should only exist on a “known-good boot” host

### External secret stores (Vault-shaped)
DeriveBSD should not try to replace org secret infrastructure.
But it should provide:
- a clean adapter surface (“provider”)
- typed receipts with lease/rotation metadata
- brokered delivery to services without teaching every app a Vault client

## DeriveBSD approach

### 1) `secret-policy` (desired secret inventory + access rules)
A `secret-policy` is a signed object declaring:
- **which secrets exist** (ids, classes, rotation expectations)
- **where they come from** (sealed blob, TPM2-sealed, external provider)
- **who may access them** (subject selectors)
- **how they may be delivered** (memfd/ramfs file/env/FD)
- audit posture (emit `secret-event` on access/denial/rotation)

This is intentionally **boring and portable**.
The apply engine maps it to whatever backend is in use.

### 2) `secret-grant` (time-bounded authority to materialize)
Secrets should not be readable by “root by default”.
Instead, access is mediated by the credential broker and expressed as:
- a `secret-grant` object (think: a portal-style lease)
- correlated by `lease_id` across lanes (r45: `lease_id` becomes canonical; `grant_id` is legacy alias)
- scoped to a secret id + purpose + subject identity
- time-bounded and optionally single-use
- optionally bound to host boot evidence (measured boot / attestation)

A supervised service starts with:
- *no* secret files
- a narrow grant (or set of grants)
- a broker-mediated delivery path

### 3) `secret-receipt` (evidence of provisioning/rotation/materialization)
Every meaningful secret action emits a receipt:
- provisioned / rotated / revoked
- provider backend used
- version/lease metadata (never the secret value)
- correlation to a `change-set` step

Receipts are the audit/logical “truth” for:
- compliance (“when did we rotate?”)
- rollbacks (“did rotation happen during this rollout?”)
- safe incident response (“what changed?”)

### 4) `secret-snapshot` (safe query surface)
A `secret-snapshot` answers:
- which secrets are present/configured for this host
- last rotation time + next due
- whether each secret is **healthy** (valid lease, unseal possible)

It never contains secret bytes.

### 5) `secret-event` (typed access/denial/rotation events)
The structured event journal should carry secret events like:
- `secret.access.granted`
- `secret.access.denied`
- `secret.materialized`
- `secret.rotation.scheduled` / `secret.rotation.completed`

Payloads must be metadata-only.

## Wiring into the ops spine

- `change-set`: add an `apply-secrets` step referencing `secret-policy`.
  - the apply engine can validate/unseal/fetch required secrets
  - emit `secret-receipt` per secret (or per batch)
  - optionally gate commit on a `secret-snapshot` health rule
- incident bundles: include `secret-snapshot` + recent `secret-receipt` digests by default
- config plans: configs reference secrets via stable ids/refs, not inline values

See: `docs/219-change-sets-and-apply-engine.md`, `docs/216-incident-snapshots-and-support-bundles.md`,
`docs/215-structured-event-log-as-evidence.md`, RFC-0158.


## Posture-gated secret release (optional)

Some deployments only want secrets released to hosts in a verified posture.
Secret grants can express this without hard-binding to an attestation vendor:

- set `constraints.require_attestation=true`
- prefer `constraints.attestation_requirement_digest` (freshness + minimum verdict)
- or pin `constraints.attestation_receipt_digest` for narrow workflows

See: `docs/226-platform-posture-and-attestation-results-as-evidence.md`.

Last updated: 2026-02-26

