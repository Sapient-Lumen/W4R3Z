# TimeSync rev0094 audit — discovery freshness and portable replay windows

## Deep-read finding

rev0093 correctly hardened several post-evaluation evidence relationships, but two surfaces still had high-risk executable gaps:

1. A discovery result could mark `version_negotiation.current_use_allowed` or `digest_binding.current_use_allowed` as true without any local freshness metadata on the returned result item.
2. An authorized-verifier challenge result could be replayed with some replay-window checks, but the portable-result status evaluation did not reject revocation evidence observed after the status evaluation, and replay did not explicitly fail when it occurred before the challenge response or before the portable-result status evaluation.

Both are backfill risks. They let a record look current because all individual timestamps are valid strings, while the evidence ordering that makes the current-use claim meaningful is underchecked.

## rev0094 changes

### Discovery result freshness

`schema/discovery-request.schema.json` now allows a `freshness` object on each result item. The validator requires this object whenever a discovery result is used for current interpretation.

The semantic checks enforce:

```text
freshness.observed_at <= freshness.current_use_not_after
freshness.basis_time <= freshness.observed_at
fresh current-use result age <= max_age_seconds
returned value timestamp, when present, equals freshness.basis_time
freshness metadata updates discovery interpretation only
```

The positive discovery examples with current-use result items now carry explicit freshness metadata.

### Authorized-verifier replay windows

`tools/temporal_coherence.py` now includes `check_authorized_verifier_replay_temporal(...)`.

The semantic checks enforce:

```text
portable_result_state.revocation_check.checked_at <= portable_result_state.evaluated_at
challenge_result.responded_at <= portable_result_state.evaluated_at
replay_context.replayed_at >= challenge_result.responded_at
replay_context.replayed_at >= portable_result_state.evaluated_at
replay_context requires usable_for_commitment_verification_only and checked_not_revoked
```

The standalone positive authorized-verifier result was corrected so its portable-result status evaluation occurs after its revocation check rather than before it.

## Refactor note

The validator remains large, but rev0094 moves two more timestamp relation families into `tools/temporal_coherence.py`. This is the right direction: helper extraction is useful when it removes executable drift, not when it creates a new registry or doctrine layer.

## Remaining risk

The next highest-risk work is not another semantic surface. It is maintainability and artifact size:

- split replay-transparency and authorized-verifier checks into small validator modules only if the split removes duplicate executable logic;
- reduce negative-fixture bulk by generating repeated mutated fixtures from compact patches;
- keep FT-0090 open until discovery, replay, and lifecycle temporal checks are covered by helper self-tests and not just vector fixtures.
