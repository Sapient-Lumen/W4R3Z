# Crypto key policies + non-exportable handles (keys are objects, not files)

DeriveBSD’s secrets lane already makes "credentials" a first-class concept.
Private keys deserve even tighter structure:
- they are high-value
- they are long-lived
- they are easy to exfiltrate accidentally
- they are often reused across unrelated workflows

The greenfield move is to make keys **policy-defined objects** whose *default* posture is:
- **non-exportable**
- **operation-only access** (sign/decrypt/derive)
- **lease-gated use**
- **receipted operations**

See: `docs/306-crypto-operations-portal-and-split-keys.md`.

## `crypto.key.policy`

A `crypto.key.policy` declares the key’s lifecycle and who may request operations.
It is the key-side counterpart to `secret-policy`:

- stable `key_id`
- purpose + allowed operations
- algorithm constraints
- export posture (default: `nonexportable`)
- subject selectors (units/users) allowed to request ops
- optional user presence / multiparty approvals
- rotation expectations
- backend binding (KeyVM / TPM / PKCS#11 / external KMS adapter)

Schema:
- `spec/crypto.key.policy.schema.json`

### Minimal key policy fields (by convention)

- `key_id` (stable)
- `class` (signing/encryption/identity/tunnel)
- `backend` (where the key lives)
- `allowed_ops` (subset of `crypto.op.request.op.kind`)
- `algorithms` (declared constraints)
- `access.selectors` (who)
- `user_presence` (when)
- `audit` (receipts/retention)

## Handles, not key bytes

Keys should be referenced by **id + policy digest**, not by path.
Callers receive either:
- a lease to request operations (`lease_id`), or
- a capability handle that is only meaningful to the crypto broker.

The broker can enforce:
- per-op allowlists
- rate limits
- destinations ("release signing" vs "ssh")
- user presence or quorum approvals

Receipts bind:
- request digest
- key id + policy digest
- subject identity
- input/output digests

See schemas:
- `spec/crypto.op.request.schema.json`
- `spec/crypto.op.receipt.schema.json`

## Backend mapping (FreeBSD-first)

- **KeyVM (default high-assurance backend):** crypto broker runs in a dedicated microVM; no network; minimal storage/export.
- **TPM backend:** non-exportable TPM keys; PCR-bound usage where appropriate.
- **PKCS#11 backend:** HSM/smartcard tokens; OS policy remains the same.
- **External KMS adapter:** allowed only under explicit policy.

The policy model should not change based on backend.
Only the adapter does.

## Wiring

- `derive.unit` should be able to declare crypto intent:
  - which `key_id`s it expects
  - whether user presence is required
  - operation budgets (ops/minute)

- `crypto.registry` should include key-policy ids as crypto surfaces so key sprawl is reviewable.

See:
- component declarations: `docs/344-derive-unit-manifests-and-capability-routing.md`
- authority budgets: `docs/298-authority-budgets-and-permission-drift-alarms.md`
- crypto surface drift: `docs/391-crypto-surface-registry-and-agility-gates.md`

Last updated: 2026-02-27r111
