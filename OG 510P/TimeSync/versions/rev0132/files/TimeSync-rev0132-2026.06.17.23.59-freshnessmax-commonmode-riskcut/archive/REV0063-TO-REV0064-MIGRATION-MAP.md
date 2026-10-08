# Migration map — rev0063 to rev0064

## Conceptual move

rev0063 could carry local assessed states and retained exports, but it could not explain why a profile evaluator reached its conformance result except through a small `evaluation_summary` field.

rev0064 adds a structured evidence-input summary:

```text
profile_assessment.evidence_summary?
retained_export.evidence_input_summaries[]?
```

## Required implementation changes

1. Add `evidence_policy` to profile applicability maps.
2. Recompute normative profile digests because evidence policy is now part of profile rules.
3. Accept optional `evaluator_evidence_summary` in profile assessments.
4. Include evidence summaries in retained P3/P5 exports when the profile evidence policy requires them.
5. Reject attempts to use `transport_metadata_only` as profile evidence.
6. Keep raw source/provenance material outside TimeSync.

## Compatibility

Existing ordinary local assessed states remain valid if they do not cross a retained/export boundary that requires evidence summaries. Retained exports for P3/P5 now need evidence summaries for audit/review purposes.
