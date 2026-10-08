# REV0094 audit — discovery freshness and replay-window refactor

## What was risky

The archive had strong boundary language around discovery negotiation and authorized-verifier replay, but two important current-use paths still depended too much on prose:

- discovery results could be accepted for current interpretation without declaring when the result was observed or how old the returned object was allowed to be;
- authorized-verifier portable results checked expiration and some replay target relationships, but did not reject status evidence assembled after its own `evaluated_at`, nor replay before the result/status existed.

## What changed executably

`tools/temporal_coherence.py` gained two helper families:

```text
check_discovery_result_freshness(...)
check_authorized_verifier_replay_temporal(...)
```

`tools/validate_archive.py` now calls those helpers instead of embedding new timestamp arithmetic directly in the already-large validator.

## Why this is not doctrine creep

No new registry was added. The new `freshness` object is a local current-use interpretation gate. It does not certify the returned object, does not create provenance, does not update TimeState, and does not satisfy profile obligations.

The authorized-verifier changes are similarly narrow: they only constrain when an existing commitment-verification receipt can be replayed.

## Validator decomposition status

This revision is a useful partial decomposition, but not a full validator split. The validator still contains many concern families. Further decomposition should be done only where it yields one of these outcomes:

```text
less duplicated timestamp arithmetic
less duplicated digest/canonicalization logic
fewer ad hoc cross-object consistency checks
more helper-level self-tests
```

A split that only moves code around without helper-level tests would not be worth the churn.
