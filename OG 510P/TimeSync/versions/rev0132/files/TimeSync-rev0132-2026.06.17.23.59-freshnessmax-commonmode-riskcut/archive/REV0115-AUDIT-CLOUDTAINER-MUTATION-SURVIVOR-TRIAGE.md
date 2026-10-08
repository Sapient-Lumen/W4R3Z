# rev0115 audit detail — cloudtainer mutation-survivor triage

The motivating audit was a targeted class-substitution test. A passing fixture was loaded, one digest `binds` field was replaced with a different schema-allowed class, and the archive validator was run again. Survivors were inspected manually to distinguish intentional polymorphism from wrong artifact-class acceptance.

## Closed survivors

| Surface | Field | Required artifact class |
| --- | --- | --- |
| Replay receipt | `replay_event.replay_event_digest` | `challenge_result_replay_event` |
| Replay receipt | `transparency_anchor.digest` | `append_only_replay_log_checkpoint` |
| Replay receipt | `anchor_evaluation.checkpoint_consistency.current_checkpoint_digest` | `append_only_replay_log_checkpoint` |
| Aggregate verifier audit | `aggregate_summary.integrity_binding.digest` | `aggregate_verifier_audit_summary` |
| Aggregate correction authority | `authority_binding.authority_digest` | `aggregate_correction_authority_rules` or `aggregate_correction_authority_identity` |
| Aggregate correction authority | `authority_binding.authorization_policy_digest` | `aggregate_correction_authority_policy`, or `profile_compatibility_statement` for portable compatibility-backed authority |
| Aggregate correction authority | `notification_cadence.notification_digest` | `aggregate_correction_notification_batch` |
| Transparency trust policy | `lifecycle_status.status_record_digest` | `transparency_trust_policy_lifecycle_status` |
| Transparency trust policy | `lifecycle_status.revocation_check.digest` | `transparency_trust_policy_revocation_status` |

## Not closed here

The audit did not introduce an external policy repository, authority registry, credential-verification layer, Merkle proof verifier, or public transparency-log client. Those remain outside the TimeSync datacube boundary. The right near-term correction is stricter digest-class semantics and a repeatable mutation-survivor test, not a large new trust infrastructure.
