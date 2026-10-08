# rev0114 to rev0115 migration map

rev0115 is a fail-closed digest-binding refinement. The TimeState core, profile catalog, transport catalog, evidence-class catalog, and public schema names remain stable.

## Added

- `tools/replay_digest_semantics.py`
- `tools/aggregate_correction_digest_semantics.py`
- `tools/transparency_policy_digest_semantics.py`
- `examples/negative/replay-transparency-replay-event-wrong-bind-invalid.json`
- `examples/negative/replay-transparency-aggregate-integrity-wrong-bind-invalid.json`
- `examples/negative/aggregate-correction-authority-reference-authority-wrong-bind-invalid.json`
- `examples/negative/transparency-policy-lifecycle-status-wrong-bind-invalid.json`
- Semantic vectors `TV-N314` through `TV-N317`
- Fixture derivations `DF-0115-001` through `DF-0115-004`

## Tightened semantic checks

- Replay receipt `replay_event_digest` must bind `challenge_result_replay_event`.
- Replay transparency checkpoint digests must bind `append_only_replay_log_checkpoint` when the local anchor/checkpoint path is used.
- Aggregate verifier audit `integrity_binding.digest` must bind `aggregate_verifier_audit_summary`.
- Aggregate correction `authority_digest` must bind correction-authority rules or identity.
- Aggregate correction `authorization_policy_digest` must bind `aggregate_correction_authority_policy` except when `authorization_basis` is `profile_compatibility_statement`, where it must bind `profile_compatibility_statement`.
- Aggregate correction notification/lifecycle/emergency/contestation digest fields must bind the artifact classes named by their local fields.
- Transparency trust-policy lifecycle status, revocation, drift, successor, and compatibility statement digests must bind their corresponding artifact classes.

## Compatibility note

Existing valid rev0114 fixtures continue to validate after the conditional authorization-policy adjustment for portable correction chains. Producers that emitted schema-shaped but semantically wrong `binds` values now fail semantic validation.
