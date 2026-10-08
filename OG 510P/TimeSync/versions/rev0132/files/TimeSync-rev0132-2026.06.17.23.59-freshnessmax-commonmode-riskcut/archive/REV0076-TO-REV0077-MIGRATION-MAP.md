# Migration map — rev0076 to rev0077

rev0077 closes FT-0076 by adding lifecycle-authority discovery, renewal hints, and anti-rollback sequencing to transparency trust-policy references.

## Required producer changes

- Add `lifecycle_authority_reference` to each `transparency_trust_policy_reference`.
- Add `sequence_equivalence` to replay-transparency `policy_lifecycle_equivalence` compatibility statements.
- Ensure current replay-visibility claims use monotonic, non-rolled-back, fresh lifecycle status.
- Keep repository topology, status endpoints, APIs, trust anchors, policy language, and authority credentials outside TimeSync.

## Consumer changes

- Treat unknown lifecycle-authority discovery as insufficient for current replay visibility.
- Treat rollback, sequence gap, stale status, or unchecked sequence as non-current replay visibility.
- Treat renewal hints as advisory only; they do not update profile assessment, actionability, traceability, or provenance.

## Unchanged

- The six-field TimeState core is unchanged.
- Profile applicability maps are unchanged.
- Evidence classes are unchanged.
- Transport adapters are unchanged.
