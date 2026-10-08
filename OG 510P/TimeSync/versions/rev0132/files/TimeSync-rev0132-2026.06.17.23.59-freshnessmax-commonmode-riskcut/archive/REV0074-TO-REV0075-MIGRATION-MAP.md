# Migration map — rev0074 to rev0075

rev0075 is backward-compatible for ordinary TimeState, profile assessment, retained evidence-summary, authorized-verifier challenge, replay-transparency, and witness/cohort records that omit `transparency_trust_policy_reference`.

New optional surface:

- `schema/transparency-trust-policy-reference.schema.json`
- `replay_transparency_audit.transparency_trust_policy_reference`
- `profile_compatibility_statement.compatible_workflows += replay_transparency_policy_equivalence`
- `profile_compatibility_statement.transparency_policy_equivalence`

New non-satisfying evidence class:

- `transparency_trust_policy_reference`

Because the forbidden evidence-class set is normative profile policy, P1-P6 normative profile digests changed.
