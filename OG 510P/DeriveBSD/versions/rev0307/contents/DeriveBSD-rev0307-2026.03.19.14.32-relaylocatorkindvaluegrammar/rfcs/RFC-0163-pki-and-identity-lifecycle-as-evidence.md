# RFC-0163: PKI + identity lifecycle as evidence (trust bundles / issue plans / receipts / events)

Status: draft  
Last updated: 2026-02-24

## Problem
Identity drift is one of the most common “quiet failures” in systems:
- trust stores vary across hosts
- cert renewal fails silently until an outage
- app teams reinvent issuance and key handling
- incident response can’t answer which identity was presented

DeriveBSD’s ops spine wants the opposite:
- desired state is explicit
- transitions are planned
- outcomes are receipted
- events are typed and queryable

## Goals
- `pki-trust-bundle` is a signed, versioned trust-root artifact.
- `pki-issue-plan` expresses desired identity/cert issuance and renewal posture.
- `pki-issue-receipt` provides evidence for issuance/renewal/install outcomes.
- `pki-event` provides typed journal events for correlation/fleet queries.
- `change-set` supports `apply-pki` as a first-class step.
- Private keys remain in the secret broker lane (no key bytes in PKI evidence objects).

## Non-goals
- Defining a single “universal CA” or mandating a particular PKI backend.
- Solving all of trust (browser PKI, exotic X.509 profiles) inside the OS.
- Replacing org infrastructure (internal CA, Vault PKI, cloud IAM).

## Data model

### pki-trust-bundle
Declares a set of trust anchors for one or more purposes.

Recommended fields:
- `bundle_id` (stable id)
- `created_at`
- `scope`: fleet/cluster/host
- `anchors[]`:
  - `anchor_id`
  - `purpose`: tls-server/tls-client/ssh-host-ca/ssh-user-ca/package-signing/etc
  - `fingerprint_sha256`
  - `object_digest` (optional pointer to stored PEM/DER)

### pki-issue-plan
Declares desired issuance and renewal behavior:
- `identity_id` (stable id referenced by services)
- `issuer`:
  - `kind`: acme/internal-ca/offline
  - `name` and optional endpoint/profile
- `subject` and `sans`
- `usages`: tls-server/tls-client/ssh-host/ssh-user/etc
- `key_ref`:
  - `secret_id` (private key lives under the secret broker)
  - optional constraints (require attestation/time discipline)
- `renewal_policy`:
  - `min_remaining_days` (renew when below)
  - optional jitter
  - max lifetime guardrails

### pki-issue-receipt
Evidence for an issuance action:
- `action`: issue/renew/revoke/install
- `result`: ok/failed
- `issuer` and `request_id`
- `identity_id`
- `cert` metadata:
  - serial
  - not_before / not_after
  - spki fingerprint
  - chain digests (`leaf_digest`, `chain_digest`)
- correlation:
  - `change_set_digest` + `step_id` (when applicable)

### pki-event
Typed events in the structured event journal:
- `pki.trust-bundle.updated`
- `pki.renewal.scheduled`
- `pki.issued` / `pki.renewed`
- `pki.install.failed`

Events are metadata-only.

## Apply semantics

### Where policy comes from
- fleet policy provides the authoritative `pki-trust-bundle` and `pki-issue-plan`
- service manifests may declare desired identities, but compilation into plans must be policy-approved or signed

### apply-pki change-set step
`apply-pki` performs:
1) validate and install/activate required trust bundle(s)
2) for each `pki-issue-plan`, ensure:
   - private key is available via the secret broker (grant)
   - cert exists and meets renewal policy
   - if renewal/issue required, run issuance flow via issuer adapter
3) install cert chain into the correct identity slot
4) emit `pki-issue-receipt` and `pki-event`

### Health gates
Rollouts may require:
- trust bundle digest matches the expected bundle for this generation
- identities referenced by critical services have `not_after` > N days
- recent issuance failures are not present (via receipts/events)

## Security notes
- trust bundles are public-ish but still policy-controlled (prevent “CA sprawl”)
- private keys never appear in PKI evidence objects or bundles
- issuance adapters must be capability-bounded (network + secret broker grants only)

## Open questions
- Do we want an OS-level default identity format (SPIFFE-style URIs), or allow arbitrary identity strings?
- Should we standardize an “identity slot” ABI for services (files vs FD vs broker API)?
- How should offline issuance workflows inject receipts without weakening the evidence chain?
