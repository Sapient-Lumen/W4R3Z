# ADR-0234: Attestation receipts carry attester identity provenance by digest

Status: Accepted  
Date: 2026-03-21

## Context

`docs/314-attester-provisioning-and-key-lifecycle-receipts.md` already introduced `attester.provision.receipt` so DeriveBSD could explain how an attester identity came to exist.

`ADR-0233` then made measured-boot evaluation exact-digest-pinned on the reference side.

That still left an expensive ambiguity on the **identity** side of attestation results:

- should a verifier receipt only carry `subject.attester_key_id`,
- should operators be expected to consult a registrar/inventory database later,
- or should attestation results carry an exact digest join to the reviewed attester-identity provenance artifact?

Keylime’s current security docs make the risk concrete: the verifier must reliably identify and authenticate the underlying platform or the wrong verification policy can be applied; by default Keylime’s registrar/tenant/verifier do not verify node identity for you; and many deployments end up relying on inventory or binding databases around AK/EK identity instead of portable attestation artifacts.

DeriveBSD should not let the real attester-identity truth live only in verifier-side tables, registrar rows, or operator memory.

## Decision

**Whenever a classic `attestation.receipt` names `subject.attester_key_id`, it must also carry an exact `identity_provenance.attester_provision_receipt_digest`.**

This means:

1. `attestation.receipt.subject.attester_key_id` remains a useful handle, but is not a sufficient review surface by itself.
2. `attestation.receipt.identity_provenance.attester_provision_receipt_digest` is the portable join to the reviewed `attester.provision.receipt` that explains how that attester identity was enrolled, rotated, or otherwise established.
3. Operators, support tooling, and downstream gates may still use registrars or local caches as implementation detail, but the archive truth remains the exact digest join, not a database lookup convention.
4. If an adapter/imported attestation result cannot name a reviewed attester-provision receipt, it should omit `subject.attester_key_id` rather than pretending an unenrolled key handle is authoritative.

## Consequences

- A/B/C/D keep measured posture explainable without normalizing a hidden inventory database as the real identity authority.
- AK rotation, TPM clear, and motherboard replacement become easier to explain because the attestation result can point straight at the attester-lifecycle evidence that justified the current key.
- Incident/support flows can recover the attester-identity story from portable artifacts instead of registrar archaeology.
- This does **not** solve the whole lifecycle model yet (revocation, replacement ceremonies, long-term retention budgets remain open), but it closes the receipt-side provenance gap.

## Alternatives considered

- **Keep `attester_key_id` only.** Rejected: that pushes identity truth into registrar/inventory folklore.
- **Allow indirect lookup via registrar or database row.** Rejected: non-portable and hard to export/audit.
- **Invent a new attester catalog subsystem now.** Rejected: too large when the immediate need is one exact digest join on the receipt we already have.

## Implementation notes

Accepted and wired through `spec/attestation.receipt.schema.json`, the canonical example, the attester-lifecycle/measured-boot/profile docs, and `tools/check_attestation_identity_provenance_contract.py`.
