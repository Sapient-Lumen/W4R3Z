# Migration map — rev0064 to rev0065

## Evidence summaries

Add these fields where missing:

```text
profile_assessments[*].assessment_id
evidence_summary.summary_id
evidence_summary.obligation_results
evidence_summary.conclusion_binding.assessment_id
```

`assessment_index_hint` may remain but is no longer the stable binding.

## Evidence policy

Replace use of `default_visibility: retention_required` with:

```text
default_visibility: retention_only
retention_required: true
```

Profiles that do not require retained summaries should set `retention_required: false` and use one of:

```text
local_only
requestable
profile_default
retention_only
```

as their default visibility lane.

## Forbidden evidence classes

Treat all evidence classes with `may_satisfy_profile_obligation: false` as unable to satisfy a `met` profile obligation. In rev0065 this includes:

```text
unauthenticated_source_claim
retained_prior_assessment
transport_metadata_only
not_observed
```

## Minimum summary items

For each resolved profile, ensure `evidence_policy.minimum_summary_items` is accounted for. Most names must appear as `input_items[*].name`. Assessment-conclusion names may be satisfied by the summary/conclusion fields.

## Compatibility

Use `schema/profile-compatibility-statement.schema.json` for detached compatibility assertions. Do not use transport envelopes or discovery results as profile negotiation.
