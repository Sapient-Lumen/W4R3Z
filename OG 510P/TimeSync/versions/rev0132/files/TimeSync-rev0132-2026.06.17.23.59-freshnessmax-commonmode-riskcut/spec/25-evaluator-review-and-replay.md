# 25 — Evaluator review and semantic replay

The evidence summary supports semantic review, not full algorithmic replay.

A reviewer can check:

```text
which assessment_id was reviewed
which profile was assessed
which evaluator version produced the decision
which semantic items were present, absent, unknown, or not applicable
which evidence classes were used
which profile obligations were met, missing, failed, or not applicable
which fallback mapping was selected, if any
which applicability label was exported
```

A reviewer cannot reconstruct from this layer alone:

```text
source selection
clock servo behavior
raw timing sample history
network path history
cryptographic chain of custody
sector-specific audit proof
```

## Challenge pattern

A challenge compares the evidence summary to the profile map and the exported assessment.

```text
1. Resolve assessed_profile.
2. Verify profile-reference digest when required.
3. Confirm the evidence summary binds to the same assessment_id, assessment_time, profile, and conclusion.
4. Confirm every profile minimum_summary_item is accounted for.
5. Check that required/default/profile-specific obligations are not marked met by forbidden evidence classes.
6. Confirm fallback applicability is non-stronger and profile-local.
7. Recheck current-policy acceptance separately from historical conformance.
```

If the summary is absent where a profile requires it for retained export, the export may still be well-formed JSON but it fails the retained-review semantic contract.

If a summary is returned through discovery as `evaluator_evidence_summary`, it is still just a flat request/result item. It must satisfy the same nested schema and semantic checks as any other summary.
