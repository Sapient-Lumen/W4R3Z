# Attestation receipts carry attester identity provenance by digest

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

The archive already had a typed attester-lifecycle object: `attester.provision.receipt`.
What it still lacked was the **receipt-side join** that makes that lifecycle evidence unavoidable when an attestation result names a specific attester key.

This cut makes that direct.
A classic `attestation.receipt` that carries `subject.attester_key_id` must also carry `identity_provenance.attester_provision_receipt_digest`.

Related:
- ADR: `adrs/ADR-0234-attestation-receipts-carry-attester-identity-provenance-by-digest.md`
- attester lifecycle: `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`
- measured-boot baseline: `docs/176-measured-boot-attestation.md`
- exact-digest reference selection: `docs/643-attestation-reference-selection-stays-exact-digest-pinned-and-no-latest-wins.md`

## Why this was still missing

The archive had already fixed the reference side of the problem:

- baseline references stay cohort-shaped and replay-first,
- non-baseline references are explicit, timeboxed exceptions,
- renewed exceptions are digest-linked successor artifacts,
- and evaluation stays exact-digest-pinned instead of latest-wins or selector-overlap folklore.

But identity provenance could still drift into the wrong place.
If a verifier receipt only says `attester_key_id = ...`, support and admission tooling are forced to recover the real story from:

- a registrar row,
- an inventory database,
- a ticket note,
- or operator memory about which AK/EK binding was current.

That is exactly the kind of backend-only truth DeriveBSD is trying to avoid.

## The boundary

### 1) `attester_key_id` is a handle, not the whole review surface

`attestation.receipt.subject.attester_key_id` stays useful for correlation and debugging.

It is **not** enough by itself to explain why this verifier trusted that attester identity.

### 2) The attestation result must carry the exact lifecycle join

If `subject.attester_key_id` is present, `identity_provenance.attester_provision_receipt_digest` is required.

That digest names the exact `attester.provision.receipt` that explains the enrolled attester identity used for this evaluation.

This keeps the receipt-side answer portable:

- which enrolled AK identity was in play,
- what enrollment mode established it,
- whether endorsement verification happened,
- and what earlier evidence/correlation objects participated.

### 3) Registrar/database lookups stay implementation detail

Registrars, tenant tools, and verifier databases can still exist.
They are useful operational helpers.

They do **not** become the archive truth.
The portable answer remains the exact digest join carried on the attestation receipt itself.

### 4) Imported adapters fail closed on provenance

If an imported or adapter-backed verifier result cannot name a reviewed `attester.provision.receipt`, it should not pretend an unenrolled `attester_key_id` is authoritative.

The safe posture is:

- either provide the exact attester-provision digest,
- or omit `attester_key_id` and keep the receipt at the weaker host-id-only story.

## Why this matters for A/B/C/D

### A) Secure fleet host

Fleets need attestation outcomes that survive verifier migration, incident export, and AK rotation.
The exact digest join keeps the attester-identity story portable instead of backend-private.

### B) Secure workstation

Workstations should stay explainable when motherboard replacement, TPM clear, or repair events happen.
Receipts that point at the exact attester-provision receipt are easier to support than “some AK handle changed” folklore.

### C) General-purpose OS

C keeps attestation optional.
But environments that opt in should still get a portable identity-provenance trail instead of a vendor/adapter database dependency.

### D) Appliance factory / regulatory

Factories and regulated deployments often care about exact enrollment provenance and hardware identity ceremonies.
Digest-bound joins help those stories survive export, audit, and offline review.

## Guardrail

`tools/check_attestation_identity_provenance_contract.py`

This guardrail checks that:

- `attestation.receipt` teaches the exact `attester.provision.receipt` digest join,
- receipts that carry `subject.attester_key_id` also require `identity_provenance.attester_provision_receipt_digest`,
- the canonical example exercises that shape,
- and the measured-boot / attester-lifecycle / profile docs keep teaching the same no-registrar-folklore boundary.

## Still open after this cut

This does not finish the entire attester lifecycle story.
Still-open details include:

- explicit revocation and replacement ceremonies,
- whether support bundles need a first-class attester-provision join of their own,
- and retention/export budgets for identity-lifecycle evidence.

Those are real next questions, but they no longer justify leaving attester identity provenance implicit on `attestation.receipt`.

Last updated: 2026-03-21r374
