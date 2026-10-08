# 169. Endorsement & reference-value transparency (anti-capture)

**Track:** C (North Star)

The North Star assumes **attestable devices** and **transparent manufacturing/provenance**.
The most likely failure mode is not “crypto breaks” — it is **ecosystem capture**:

> attackers win by corrupting *what verifiers believe* (endorsements, reference values, verifier policy),
> not by directly tampering with tallies.

This doc specifies how to make the attestation ecosystem **publicly auditable**.

Authoritative sources:
- RATS architecture (`source: rfc9334_txt`)
- EAT (`source: rfc9711_txt`)
- SCITT architecture draft (`source: draft_scitt_architecture_22_txt`)
- SCITT receipts profile draft (`source: draft_scitt_receipts_ccf_profile_00_txt`)
- SCITT reference APIs draft (`source: draft_scitt_scrapi_07_txt`)

## 169.1 The capture threat model

Attackers attempt:
1. **Split-view endorsements:** show different relying parties different “approved firmware” sets.
2. **Reference-value drift:** silently change “known good” hashes, then claim it was always so.
3. **Verifier capture:** modify verifier policy/keys while leaving devices “apparently compliant”.
4. **Selective blindness:** monitors omit bad endorsements or bad revocations from certain audiences.

We treat these like CT split-world attacks, but for **attestation policy**.

## 169.2 Normative requirements (North Star)

### 169.2.1 Public registry for endorsements and reference values

All of the following MUST be publishable as signed, content-addressed objects:

- `Endorsement` (who vouches, for what, with what scope)
- `ReferenceValueSet` (hashes/measurements, validity window, device model constraints)
- `VerifierPolicy` (what evidence is required; which endorsers are trusted; revocation rules)
- `Revocation` (of endorsements, keys, or reference values)

These objects MUST be:
- versioned,
- time-bounded (validity intervals),
- and include explicit issuer identity and key ids.

### 169.2.2 Transparency service anchoring (SCITT-style)

A transparency service SHOULD provide:
- registration receipts proving inclusion,
- consistency/append-only guarantees,
- and query mechanisms for third-party monitors.

SCITT provides a standards-aligned vocabulary for this (`source: draft_scitt_architecture_22_txt`),
and current work includes receipt profiles and reference APIs (`source: draft_scitt_receipts_ccf_profile_00_txt`, `source: draft_scitt_scrapi_07_txt`).

### 169.2.3 Gossip and multi-vantage auditing

The system MUST assume split-world attempts and include **gossip**:
- verifiers exchange checkpoint hashes/receipts opportunistically (piggybacked gossip is allowed),
- monitors watch the monitors (“public inspections” of third-party monitors),
- missing revocations or withheld endorsements must become provable suppression events.

(See: `23-witness-gossip-and-cross-checkpointing.md`, `147-inspection-gossip-and-suppression-detection.md`)

## 169.3 Practical design: “Reference Values as EPB”

To keep the full stack coherent, treat attestation policy artifacts like Election Parameter Bundles:
- signed,
- logged,
- MMD-style deadline-bound (`145-mmd-style-deadlines-for-evidence-publication.md`),
- and included in dispute-ready bundles (`92-offline-verifier-bundle-spec.md`).

## 169.4 Proof obligations

This doc primarily supports:
- PO-202 (attestation claim set is stable and auditable)
- PO-203 (manufacturing evidence pipeline is checkable)
- PO-203 (endorsement + reference values are transparent and split-world-resistant)

(See `artifacts/proof_obligations/proof-obligations.csv`.)


## Governance
See `docs/175-minimum-governance-for-endorsements-and-reference-values.md` for minimal governance rules (MMD, revocation semantics, disputes).
