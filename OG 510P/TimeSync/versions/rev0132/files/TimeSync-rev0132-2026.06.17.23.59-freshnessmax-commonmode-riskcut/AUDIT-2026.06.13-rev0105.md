# TimeSync rev0105 audit — profile-reference binding refactor

rev0105 continues FT-0090 with executable validation work only. The pass focuses on `assessed_profile` references because they are the bridge between a local assessment/evidence/challenge artifact and the named profile rules the artifact claims to evaluate.

## Risk found

The schema has long allowed profile references to carry a `binding` object of type `signed_profile_binding`. That is useful metadata, but before rev0105 the validator did not enforce two important semantic boundaries:

1. A profile-reference binding could be signed after the assessment, evidence summary, or authorized-verifier challenge that relied on it.
2. A profile reference carrying a digest could also carry a signed binding whose `covers` list omitted `digest`, making the signed metadata look stronger than it was.

The first problem is a future-artifact problem. The second problem is a coverage/binding problem. Neither requires cryptographic verification to catch; both are executable structural checks.

## Change made

rev0105 adds `tools/profile_reference_binding.py` and wires it into:

```text
local profile assessments
evaluator evidence summaries
authorized-verifier challenge target bindings
```

The helper rejects:

```text
profile reference binding.signed_at after the artifact/assessment use time
signed_profile_binding without a covers list
signed_profile_binding that omits authority/id/version/revision fields present on the reference
signed_profile_binding that omits digest when the profile reference carries a digest
```

## Boundary preserved

The helper does not verify signatures, create a profile-binding authority registry, infer profile compatibility, or let a signature replace a required digest. It is intentionally a coherence check over metadata that is already present.

## New regression coverage

rev0105 adds three derivation-checked negative fixtures:

```text
examples/negative/local-assessment-profile-binding-after-assessment-invalid.json
examples/negative/local-assessment-profile-binding-missing-digest-cover-invalid.json
examples/negative/authorized-verifier-profile-binding-after-issued-invalid.json
```

and semantic vectors:

```text
TV-N282
TV-N283
TV-N284
```

The suite now covers 303 semantic vectors.

## Remaining work

FT-0090 should remain open. The next highest-value work is still selective decomposition of `tools/validate_archive.py`, especially large evidence-summary and discovery-result branches, but only where extraction produces smaller executable checks or prevents copy-drift.
