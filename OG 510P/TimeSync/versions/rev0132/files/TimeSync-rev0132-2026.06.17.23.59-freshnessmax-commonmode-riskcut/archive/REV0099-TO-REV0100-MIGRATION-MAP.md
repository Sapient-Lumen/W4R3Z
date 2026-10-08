# rev0099 to rev0100 migration map

## Summary

rev0100 is compatible with rev0099 consumers that ignore the new negative fixtures and helper module. It tightens validation for authorized-verifier challenge records by making response/revocation artifact-time ordering executable.

## New helper

```text
tools/authorized_verifier_temporal.py
```

## Validator change

`tools/validate_archive.py` now delegates authorized-verifier issue/expiry, response, portable-result state, revocation-check, and replay timing to `tools/authorized_verifier_temporal.py`.

`tools/temporal_coherence.py` no longer owns the authorized-verifier replay check; it remains the shared timestamp/freshness helper used by other concern modules.

## New rejection cases

A rev0099 authorized-verifier challenge record can become invalid in rev0100 if:

```text
challenge_result.responded_at < issued_at
portable_result_state.revocation_check.checked_at < challenge_result.responded_at
```

Existing rev0099 rejection cases are preserved:

```text
issued_at >= expires_at
challenge_result.responded_at > expires_at
portable_result_state.evaluated_at > portable_result_state.not_after
portable_result_state.not_after > expires_at
portable_result_state.revocation_check.checked_at > portable_result_state.evaluated_at
replay_context.replayed_at < challenge_result.responded_at
replay_context.replayed_at < portable_result_state.evaluated_at
replay_context.replayed_at > portable_result_state.not_after
```

## Fixture changes

New semantic vectors:

```text
TV-N268
TV-N269
```

New derivation entries:

```text
DF-0100-001
DF-0100-002
```

Positive replay fixtures whose revocation check was earlier than the response were normalized to use the response time as the revocation-check timestamp.

## Boundary

No TimeState core field changes. No profile obligation changes. No new authority registry. No transport semantics change. Authorized-verifier disclosure material remains external and non-provenance.
