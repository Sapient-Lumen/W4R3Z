# rev0077 → rev0078 migration map

## Schema changes

- `policy_lifecycle_authority_reference` now requires `rotation_delegation_status`.
- `transparency_trust_policy_reference` and replay-transparency audit records inherit the updated authority reference.
- `profile_compatibility_statement.transparency_policy_equivalence.policy_lifecycle_equivalence` now requires `authority_rotation_equivalence`.
- `lifecycle_authority_rotation_summary` is added as a non-satisfying evidence class.

## Existing data

For existing active references that have no rotation/delegation/compromise issue, add:

```json
"rotation_delegation_status": {
  "rotation_state": "current_authority_active",
  "rotation_checked_at": "<checked-at>",
  "delegation_state": "not_delegated",
  "delegation_scope": "none",
  "delegation_checked_at": "<checked-at>",
  "compromise_response": {
    "state": "none_known",
    "checked_at": "<checked-at>",
    "replay_visibility_effect": "no_current_effect",
    "compromise_response_updates_replay_visibility_only": true,
    "compromise_response_interpreted_as_timesync_provenance": false
  },
  "non_interpretation_boundary": {
    "authority_key_material_exported": false,
    "delegation_chain_exported": false,
    "authority_roster_exported": false,
    "rotation_protocol_exported": false,
    "compromise_forensics_exported": false,
    "rotation_or_delegation_is_profile_evidence": false,
    "rotation_or_delegation_updates_actionability": false,
    "rotation_or_delegation_reopens_assessment": false,
    "rotation_or_delegation_interpreted_as_timesync_provenance": false,
    "rotation_or_delegation_updates_replay_visibility_only": true
  }
}
```

When delegation or planned rotation is present, include the matching digest handle. Do not export authority key material, delegation chains, rosters, endpoints, repository topology, protocol transcripts, or incident forensics.
