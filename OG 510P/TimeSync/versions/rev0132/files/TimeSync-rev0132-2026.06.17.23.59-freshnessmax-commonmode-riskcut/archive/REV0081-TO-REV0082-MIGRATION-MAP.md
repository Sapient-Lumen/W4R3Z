# Migration map — rev0081 to rev0082

## Required aggregate-summary addition

Aggregate verifier audit summaries now require:

```text
aggregate_summary.aggregate_revision_lineage
```

For an existing rev0081 aggregate publication with no correction lineage, use:

```json
{
  "status": "original",
  "publication_sequence": 1,
  "correction_reason": "not_applicable",
  "correction_effect": "aggregate_posture_only",
  "withdrawal_disposition": "not_applicable",
  "lineage_boundary": {
    "prior_publication_rewritten": false,
    "suppressed_delta_exported": false,
    "individual_result_identifiers_exported": false,
    "verifier_identity_exported": false,
    "correction_updates_profile_assessment": false,
    "correction_updates_replay_visibility_only": true,
    "external_correction_record_interpreted_as_timesync_provenance": false
  }
}
```

If the aggregate is a correction, withdrawal, supersession, or reconciliation, provide `prior_aggregate_digest`, monotonic sequence fields, and the appropriate correction/reconciliation disposition.

## Evidence class catalog

Add `aggregate_revision_lineage_summary` to the set of evidence classes that cannot satisfy profile obligations.

## Profile digests

The profile normative digests changed because the forbidden evidence-class set is part of profile evidence policy.
