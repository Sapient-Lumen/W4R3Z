# Migration map — rev0070 to rev0071

## Add fields to authorized-verifier challenge records

Every authorized-verifier challenge record now needs:

```text
portability_boundary
```

Every `authorized_verifier_challenge_result` now also needs:

```text
challenge_result.portable_result_state
```

Add `replay_context` only when a result is being replayed or copied for review.

## Update profile compatibility statements if used for challenge-result portability

Profile compatibility statements may optionally declare:

```text
compatible_workflows:
  - authorized_verifier_challenge_result_portability
```

If this workflow is named, `evidence_policy_relation` must be `identical` or `stricter_or_equal`.

## Migration rule

Existing rev0070 challenge results can be migrated only as local retained records unless an operator adds explicit portability boundary and current revocation status.
