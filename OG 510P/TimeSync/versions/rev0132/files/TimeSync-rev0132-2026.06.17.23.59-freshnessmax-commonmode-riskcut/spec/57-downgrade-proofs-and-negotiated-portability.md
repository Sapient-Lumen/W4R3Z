# 57 — Downgrade proofs and negotiated portability

rev0087 extends discovery semantic-version negotiation with downgrade-proof metadata.

## Boundary

A downgraded discovery result is not automatically safe. Downgrade means the producer returned or interpreted a surface under an older supported semantic version. That may be safe only if the selected older semantics are exact, equivalent, or stricter-or-equal for the named result item.

## Required current-use proof

For `version_negotiation.decision = downgraded_to_supported` with `current_use_allowed = true`, the result must include:

```text
source_semantic_version
selected_semantic_version
downgrade_basis
stronger_or_equal_semantics = true
downgrade_proof_digest binding profile_downgrade_proof
```

If the request says `downgrade_proof_required_for_current_use = true`, the validator rejects current downgraded results without that digest-bound proof.

## Rejection cases

The validator rejects:

```text
downgraded current use without a proof digest
downgraded current use with weaker_or_unknown basis
downgraded current use with stronger_or_equal_semantics = false
selected versions not in the requester's supported set
negotiation metadata that updates profile assessment or actionability
```

Downgrade proof gates discovery interpretation only. It cannot turn compatibility metadata into timing evidence or current actionability.
