# Audit note — rev0100 authorized-verifier temporal/refactor pass

rev0100 is a milestone cleanup, but the change is executable rather than ceremonial. The deep-read target was a stale-evidence seam in authorized-verifier portable results plus continued validator decomposition.

## Finding

Authorized-verifier result records already had replay-window checks, but their timing was split between the monolithic validator and the general temporal helper. That made it easy to miss one compact artifact relation: a portable-result revocation check could predate the challenge response it was supposed to qualify.

The stale shape was present in copied replay-positive fixtures:

```text
challenge_result.responded_at = 2026-05-21T09:35:00Z
portable_result_state.revocation_check.checked_at = 2026-05-21T09:10:02Z
```

Those records could still pass as portable current status even though the status check happened before the response. A separate bad shape was also possible:

```text
challenge_result.responded_at < issued_at
```

Neither gap requires a new registry or new evidence class. It requires keeping the challenge artifact, response, revocation status, portable-result evaluation, and replay window in one executable helper.

## Change

rev0100 adds `tools/authorized_verifier_temporal.py` and wires it into `check_authorized_verifier_challenge`.

The helper now enforces:

```text
issued_at < expires_at
challenge_result.responded_at >= issued_at
challenge_result.responded_at <= expires_at
portable_result_state.evaluated_at <= portable_result_state.not_after
portable_result_state.not_after <= expires_at
portable_result_state.revocation_check.checked_at <= portable_result_state.evaluated_at
portable_result_state.revocation_check.checked_at >= challenge_result.responded_at
replay_context.replayed_at >= challenge_result.responded_at
replay_context.replayed_at >= portable_result_state.evaluated_at
replay_context.replayed_at <= portable_result_state.not_after
```

The authorized-verifier replay timing logic was removed from `tools/temporal_coherence.py`; that file now remains a shared timestamp/freshness primitive module instead of accumulating every domain-specific temporal branch.

## Fixture/refactor work

rev0100 adds two negative fixtures:

```text
examples/negative/authorized-verifier-challenge-response-before-issued-invalid.json
examples/negative/authorized-verifier-challenge-revocation-before-response-invalid.json
```

Both are derivation-checked:

```text
DF-0100-001 -> authorized-verifier-challenge-response-before-issued-invalid.json
DF-0100-002 -> authorized-verifier-challenge-revocation-before-response-invalid.json
```

rev0100 also normalizes existing replay-positive and copied replay-transparency fixtures so the positive examples no longer carry pre-response revocation checks.

## Boundary retained

Authorized-verifier status timing still does not update:

```text
TimeState freshness
profile assessment
current actionability
ordinary retained-summary disclosure
transport authentication
profile evidence obligations
```

It only prevents a portable challenge result from relying on status material that is temporally unable to support that result.

## Remaining risk

FT-0090 remains open. The riskiest remaining work is continued validator decomposition and selective derivation of large replay-transparency/discovery fixture families where that materially reduces copy drift.
