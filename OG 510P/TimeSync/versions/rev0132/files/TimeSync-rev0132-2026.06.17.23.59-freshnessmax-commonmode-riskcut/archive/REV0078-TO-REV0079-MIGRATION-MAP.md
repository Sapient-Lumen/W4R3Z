# Migration map — rev0078 to rev0079

## Additions

- Add `schema/policy-lifecycle-authority-recovery-attestation.schema.json`.
- Add `recovery_attestation_reference` under contained lifecycle-authority `compromise_response` when a contained compromise is used for replay-visibility evaluation.
- Add `recovered_current` as a compromise-response replay-visibility effect.
- Add `lifecycle_authority_recovery_attestation` to the evaluator evidence class catalog and to each profile's forbidden obligation-satisfaction classes.

## Validation impact

A rev0078 record with `confirmed_contained` compromise but no recovery attestation is no longer sufficient for current replay visibility. Historical-only or contested recovery posture can still be retained, but it must not be promoted to `current_at_evaluation`.

## Boundary preserved

No TimeState field changes. No profile-assessment conclusion changes. No export of incident forensics, key material, rosters, legal details, policy repositories, or external provenance.
