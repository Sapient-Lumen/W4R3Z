# Attester provisioning + key lifecycle receipts (make attestation operable)

Measured boot and remote attestation are only as good as the **attester identity lifecycle**.
Most stacks treat this as “some TPM key exists” and bolt on process later.
DeriveBSD should bake in a minimal, typed lane now so fleets can answer:

- *Which attestation key is this host using?*
- *How was it provisioned/enrolled?*
- *Was the endorsement verified?*
- *When did the key rotate (and why)?*

This doc complements:
- trust bootstrap: `docs/155-trust-bootstrap.md`
- measured boot evidence: `docs/176-measured-boot-attestation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- sealed secrets: `docs/272-sealed-secrets-attested-unsealing.md`

## The missing evidence object: `attester.provision.receipt`

DeriveBSD already has:
- evidence (`boot.attestation`)
- reference values (`attestation.reference`)
- verifier results (`attestation.receipt`)

What’s missing in many ecosystems is a durable record of **how the attester identity came to exist**.

Add a typed receipt:
- kind: `attester-provision-receipt`
- schema: `spec/attester.provision.receipt.schema.json`
- example: `spec/examples/attester.provision.receipt.json`

This is not a secret; it is metadata that must still be export-governed.

## What the receipt should capture (minimum)

- subject host id + (optional) host identity key id
- TPM identity handles:
  - EK cert digest (or a digest pointer to stored EK chain object)
  - AK id + digest of canonical public area
  - whether endorsement verification succeeded
- enrollment mode (maps to bootstrap modes):
  - `offline-root`, `hardware-backed`, `factory-anchor`, `manual`
- evidence pointers used during enrollment:
  - boot attestation digest
  - boot manifest digest
  - attestation reference + verifier receipt digests (if enrollment reused the verifier)
- correlation pointers:
  - `bootstrap.evidence` digest
  - `change-set` digest if rotation happened as part of a planned transition

## Provisioning flow (hardware-backed, typical)

1) Host creates or loads its **host identity** key.
2) Host creates an **Attestation Key (AK)** in TPM.
3) Enrollment service verifies:
   - EK chain (if required by org policy)
   - a quote signed by AK
   - event-log replay against expected `boot.manifest` (preferred)
4) Enrollment service issues scoped trust roots / grants.
5) System emits `attester.provision.receipt` capturing the decision and key identifiers.

Why capture this?
- later, if a host starts failing attestation, you can see whether it’s a key mismatch, a TPM clear, or a policy drift.

## Rotation and revocation (must be first-class)

- TPM clear, board replacement, or suspected compromise triggers rotation.
- Rotation should be explicit:
  - new receipt: `outcome=rotated`
  - old key marked revoked (either via a receipt or via a trust-policy update)
- Any policy that depends on AK identity should treat the attester receipt digest as a stable join key.
- `attester_key_id` alone is never the review surface; the portable answer is the exact `attester.provision.receipt` digest that explains how that key became trusted.
- `attester_key_id` alone is never the review surface; the portable answer is the exact `attester.provision.receipt` digest that explains how that key became trusted.

## Privacy and export constraints

Attester lifecycle receipts can leak inventory:
- hardware class labels
- EK-derived identifiers

So:
- store raw EK certs separately (receipts reference digests)
- avoid serial numbers by default
- treat export of attester receipts like other posture evidence (policy-gated, time-bounded)

## Integration hooks

- `bootstrap.evidence` should include the latest `attester.provision.receipt` digest when a hardware-backed mode is used.
- `attestation.receipt` now uses a direct exact digest join: when it carries `subject.attester_key_id`, it must also carry `identity_provenance.attester_provision_receipt_digest`.
- sealed-secret unseals should be able to cite:
  - the attestation receipt (verifier verdict)
  - the attester provision receipt (identity provenance)

## Non-goals (v1)

- mandating TPM presence
- forcing a single vendor enrollment protocol
- embedding confidential-computing attestation formats (TDX/SEV-SNP) into core; treat those as adapters that still emit Derive receipts (see `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`)

Last updated: 2026-03-21r374
