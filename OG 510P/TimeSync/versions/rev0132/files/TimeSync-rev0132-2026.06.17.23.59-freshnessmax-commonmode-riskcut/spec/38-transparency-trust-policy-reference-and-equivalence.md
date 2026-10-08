# Transparency trust-policy references and threshold-equivalence boundary

rev0075 closes FT-0074 by adding a compact, digest-bound `transparency_trust_policy_reference`.

The reference answers a narrow question: which external transparency policy supplied the threshold meaning for anchor freshness, checkpoint consistency, witness counts, monitor-cohort observations, split-view handling, or cross-operator replay-visibility equivalence?

It does not export the policy language, witness or monitor rosters, trust anchors, legal authority, verifier identities, gossip transcripts, proof material, salts, preimages, or external provenance.

## Placement

`transparency_trust_policy_reference` may appear on detached replay-transparency records, especially `challenge_replay_transparency_receipt`. Discovery may return it as its own optional item. It is not a TimeState field, not a profile-assessment field, and not a profile-obligation evidence class.

## Cross-operator use

Cross-operator current replay visibility requires a compatibility-statement-backed policy equivalence claim. Same-operator receipts may cite a local policy digest without cross-operator equivalence.

Profile compatibility statements may now include the workflow `replay_transparency_policy_equivalence` and a `transparency_policy_equivalence` object. That object is scoped to replay visibility only. It cannot state profile equivalence, verifier authorization equivalence, source-traceability equivalence, current-actionability equivalence, transport-security equivalence, or external-provenance equivalence.

## Negative rules

A transparency trust-policy reference MUST NOT:

- satisfy profile obligations,
- update profile assessment, TimeState, validity horizon, current actionability, or source posture,
- export trust anchors, policy language, witness or monitor rosters, identities, proof material, or gossip transcripts,
- treat an external transparency framework as TimeSync provenance,
- authorize challenge disclosure or replay by itself,
- weaken threshold semantics under a compatibility statement.

## Validator-backed invariants

rev0075 adds checks for malformed policy references, cross-operator current replay visibility without compatibility-backed equivalence, threshold non-compliance, weaker policy-equivalence claims, and trust-policy references used as profile-obligation evidence.
