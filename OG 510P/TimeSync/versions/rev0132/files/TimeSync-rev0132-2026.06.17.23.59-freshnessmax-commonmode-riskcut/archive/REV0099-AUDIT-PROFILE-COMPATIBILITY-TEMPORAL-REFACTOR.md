# rev0099 audit — profile compatibility temporal refactor

## Why this pass mattered

The archive had already hardened most current-use temporal surfaces by rev0098, but profile compatibility statements remained a compact portable-artifact seam. They could say they were issued before expiry while still being signed after expiry, or could include compatibility-drift evidence evaluated after the signature that claims to bind the statement.

That is not a new conceptual surface. It is a missing executable check.

## Implemented checks

`tools/profile_compatibility_temporal.py` now checks:

```text
profile compatibility statement issued_at <= binding.signed_at
profile compatibility statement binding.signed_at <= expires_at
profile compatibility drift evaluated_at <= compatibility statement binding.signed_at
profile compatibility drift evaluated_at <= compatibility statement expires_at
```

The helper has its own self-test and is invoked by the main validator.

## Fixture strategy

rev0099 added two rendered negative fixtures, but it also added derivation checks so the new fixtures are not untracked copies.

It also pulled one older profile-compatibility fixture into the derivation manifest:

```text
examples/negative/profile-compatibility-challenge-workflow-weaker-invalid.json
```

That fixture now derives from:

```text
profiles/compatibility/p3-challenge-portability-workflow.json
```

This is better than deleting rendered fixtures because reviewers still need inspectable JSON, but it reduces hidden copy drift.

## What did not change

rev0099 does not add any new profile compatibility workflow, evidence class, registry, or TimeState core field. It does not convert signatures into profile evidence. It only checks that a compatibility statement's own artifact timeline is coherent.

## Next useful refactor

The main validator remains too large. The next high-value extraction is probably a `profile_compatibility.py` semantic module or a replay-transparency semantic module, but only if it removes executable branches from the monolith. The project should avoid splitting files merely to create nicer architecture diagrams.
