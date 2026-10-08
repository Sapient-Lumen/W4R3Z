# FT-0070 closure — challenge-result portability/replay/revocation

FT-0070 asked whether detached authorized-verifier challenge results should have portable replay/revocation semantics or remain entirely local retained artifacts.

## Decision

TimeSync now defines a narrow portable surface:

```text
portability_boundary
challenge_result.portable_result_state
optional replay_context
```

A challenge result may be reused only as a commitment-verification receipt for the same redacted commitment, summary, assessment, and assessed-profile digest.

## Explicit non-goals

A challenge result still cannot:

```text
satisfy profile obligations
update TimeState
refresh validity horizon
change profile conformance
supply current actionability
act as transport authentication
serve as provenance
carry salt or preimage material
```

## Validator-backed closure

rev0071 rejects revoked results, usable results without checked-not-revoked status, replay-use upgrades, profile-digest replay mismatch, cross-operator portability without compatibility-statement digest, and weak evidence-policy compatibility statements that claim challenge-result portability.
