# 156. Voting device attestation profile + reference values registry

**Track:** C (North Star)


This doc defines a **first-pass** profile for:
- what a voting device must attest to (claims), and
- how the ecosystem publishes the “expected” values (reference values + endorsements).

The intent is to make the North Star **auditably non-hand-wavy**.

## 156.1 Claims container: EAT

Use EAT as the claims container and align naming where possible (RFC 9711).

The profile below is intentionally conservative:
- keep a minimal “must have” set,
- allow extension fields as URIs,
- and require canonical hashing rules for any referenced objects.

## 156.2 Required claim groups (normative)

### Identity and model
MUST include:
- Stable device identifier (UEID-style)
- Hardware model + revision

### Boot chain and firmware
MUST include:
- Secure boot / measured boot evidence sufficient for a verifier to determine:
  - ROM/bootloader lineage
  - firmware image hash (or measurement set)
  - anti-rollback state

### Election binding
MUST include:
- `epb_hash`: hash of the ElectionParameterBundle the device is operating under
- `election_id` and `jurisdiction_id` (or equivalent)

### Provenance pointers
MUST include:
- hashes of the supply-chain statements (in-toto) that produced:
  - the firmware build
  - the device enrollment event
OPTIONALLY include:
- test/audit statement hashes

### Freshness and replay resistance
MUST include at least one:
- nonce (verifier challenge)
- timestamp with an external time source or monotonic counter
- or inclusion proof against a transparency service that is time-bounded

## 156.3 Reference values

A reference value entry captures the “expected” measurements and constraints for a lineage.

See `schemas/ReferenceValueEntry.json`.

Normative requirements:
- Reference values MUST be **content-addressed** (hash stable canonical form).
- Reference values MUST be published to a transparency service that produces receipts.
- Reference values MUST include an **expiry/validity** window.

## 156.4 Endorsements

Endorsements are statements about reference values (or about a signer / process), such as:
- manufacturer declaration
- lab certification result
- authority acceptance list

See `schemas/EndorsementEntry.json`.

Normative requirements:
- Endorsements MUST be publishable with receipts and MUST be revocable.

## 156.5 Attestation evidence bundles

An attestation bundle is what gets published/retained as evidence:
- device EAT (or hash)
- verifier evaluation result
- referenced reference values + endorsements (by ID)
- inclusion proofs / receipts

See `schemas/AttestationEvidenceBundle.json`.

## 156.6 Reference values registry (public API / publication)

At minimum, publish:
- a registry index of active reference value IDs by hardware model
- a registry index of active endorsement IDs by issuer
- revocations

This can be a signed JSON index (content-addressed) that itself is logged.

## 156.7 What to do next

1. Turn this profile into a formal EAT profile document (with exact claim keys and types).
2. Decide where reference values live:
   - within the election transparency log,
   - or in a dedicated SCITT-style transparency service for attestations/provenance.
3. Add enforcement:
   - a verifier MUST NOT accept evidence unless all required groups are present.