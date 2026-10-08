# FT-0072 closure — Transparency-anchor freshness and checkpoint consistency

## Closed in rev0073

FT-0072 asked whether TimeSync should define a compact boundary for replay-transparency anchor freshness, checkpoint consistency, and split-view/equivocation evidence without becoming a transparency-log protocol.

rev0073 answers yes, narrowly.

## Resolution

A replay-transparency receipt now carries `anchor_evaluation`, which summarizes:

- anchor freshness at an explicit evaluation time,
- checkpoint consistency status,
- split-view/equivocation status,
- whether the receipt is current, historical, contested, or unknown replay visibility.

## Non-goals preserved

The closure does not add:

- Merkle proof formats,
- inclusion/consistency proof transport,
- witness or monitor rosters,
- gossip transcripts,
- transparency-log APIs,
- verifier identities,
- salts or preimages,
- legal-authority detail,
- external-log provenance semantics.

## Guardrail

Current replay visibility is not current profile actionability. A fresh, consistent, non-conflicting transparency anchor cannot update TimeState, profile conformance, source traceability, source diversity, validity horizon, policy acceptance, verifier authorization, or profile-obligation satisfaction.
