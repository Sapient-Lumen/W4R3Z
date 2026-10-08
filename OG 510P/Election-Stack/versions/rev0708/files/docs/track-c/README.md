# Track C — North Star (Attestable electronic voting + transparent manufacturing)

**Track:** C (North Star)



> **Deployment honesty:** Track C documents describe a "North Star" hardening agenda.
> They are **not Track A deployment guidance** and must not be used to imply supply‑chain or fully electronic voting safety.
> Before reading, review [`docs/167` non-claims](../167-non-claims-and-boundaries.md) (especially **N‑4**) and the [`promotion protocol`](../229-experiment-to-spec-promotion-protocol.md).

## Quick navigation
- [Curated bundle](BUNDLE.md)

Track C is the “we chose to build the ecosystem” world:
**fully electronic voting in its best imaginable form**, with attestable devices and
transparent manufacturing/provenance.



## Relationship to Track A
Track C defines **conditional claims**. Over time, pieces may be promoted into Track A (toward A3) only via explicit changes to `166`/`167`, new or updated proof obligations, and checkable artifacts.

Canonical statement of claim tiers and boundaries:
- `../166-scope-and-claims-contract.md`
- `../167-non-claims-and-boundaries.md`

Track C statements are **conditional claims**: they become plausible only if the ecosystem assumptions
(attestation, provenance, endorsement transparency, governance) are met. Track C is where we specify
*what would have to be true* and how to harden that ecosystem against capture.


This track treats *verification capture* as the primary threat: attackers win by corrupting the
attestation/endorsement/reference-value ecosystem and selectively disclosing “good news”.

## Recommended read order
1. `../155-north-star-attestation-and-provenance-stack.md`
2. `../156-attestation-claims-profile-and-reference-values-registry.md`
3. `../157-manufacturing-evidence-pipeline.md`
4. `../131-monitor-accountability-and-public-inspections.md` (public inspections patterns)
5. `../159-proof-obligations-ledger.md` (PO-201+)

## What we want from Track C
- A **normative attestation claims profile** (EAT-aligned) and a reference-value/endorsement registry
  with transparency receipts and gossip.
- A manufacturing evidence pipeline that produces auditable supply-chain statements.


## Anti-capture governance (new)
- Minimal governance for endorsements/reference values: `docs/175-minimum-governance-for-endorsements-and-reference-values.md`
- Canonical evidence envelopes & packets: `docs/173-canonical-evidence-envelopes-and-packets.md`
