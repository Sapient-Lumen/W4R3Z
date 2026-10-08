# rev0100 audit — authorized-verifier temporal refactor

## Why this pass mattered

Most high-risk timestamp surfaces had been hardened by rev0099, but authorized-verifier portable results still mixed temporal checks across the monolithic validator and the generic temporal helper. During the pass, replay-positive fixture copies showed a concrete stale-status pattern: the portable-result revocation check occurred before the challenge response it purported to qualify.

This is exactly the kind of error FT-0090 is meant to eliminate: not new doctrine, just executable rejection of evidence that is too early or too late for the artifact consuming it.

## Implemented checks

`tools/authorized_verifier_temporal.py` now checks:

```text
authorized verifier challenge issued_at < expires_at
challenge_result.responded_at >= issued_at
challenge_result.responded_at <= expires_at
portable_result_state.evaluated_at <= portable_result_state.not_after
portable_result_state.not_after <= challenge expires_at
portable_result_state.revocation_check.checked_at <= portable_result_state.evaluated_at
portable_result_state.revocation_check.checked_at >= challenge_result.responded_at
replay_context.replayed_at >= challenge_result.responded_at
replay_context.replayed_at >= portable_result_state.evaluated_at
replay_context.replayed_at <= portable_result_state.not_after
```

The helper has its own self-test and is invoked by the main validator.

## Refactor result

`tools/validate_archive.py` shrank slightly and no longer owns authorized-verifier timestamp arithmetic inline. `tools/temporal_coherence.py` also shed the authorized-verifier replay branch, leaving that module as a shared timestamp/freshness helper rather than a domain-specific catch-all.

## Fixture strategy

Two new rendered negative fixtures were added, and both are derivation-checked from the positive authorized-verifier result fixture.

Existing replay and replay-transparency copies were normalized where the stale revocation check was inherited. This is a correction to positive fixture hygiene, not a new semantic surface.

## What did not change

rev0100 does not add a new authorized-verifier workflow, registry, evidence class, or TimeState field. It does not make verifier disclosure material profile evidence. It only checks that current portable verifier status is temporally capable of supporting the response and replay record that consume it.

## Next useful refactor

The next high-value extraction is likely replay-transparency semantic validation, but only if it removes concrete duplicated branches from `tools/validate_archive.py`. A cosmetic split would not help.
