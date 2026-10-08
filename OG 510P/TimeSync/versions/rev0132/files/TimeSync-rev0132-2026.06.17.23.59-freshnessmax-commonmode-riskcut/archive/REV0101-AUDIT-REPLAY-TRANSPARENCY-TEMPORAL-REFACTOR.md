# rev0101 audit — replay-transparency temporal refactor

## Why this mattered

Replay transparency is a high-leverage boundary because it can make a retained authorized-verifier result visible for later commitment-verification review. The dangerous failure mode is not a bad schema shape; it is a plausible-looking current replay-visibility record whose supporting replay event, anchor log event, witness observation, or freshness basis does not actually predate the evaluation that consumes it.

## Concrete risk closed

Before rev0101, freshness arithmetic used `anchor_freshness.basis_time`, but there was no executable check that a declared `basis: logged_at` actually used the `transparency_anchor.logged_at` value. This allowed a record to be fresh by one timestamp while citing a different anchor timestamp as the semantic basis.

rev0101 rejects that pattern and also rejects replay events and anchor log events after `anchor_evaluation.evaluated_at`.

## Refactor

The new helper is intentionally narrow:

```text
tools/replay_transparency_temporal.py
```

It handles timestamp ordering only. It does not decide policy thresholds, visibility status semantics, disclosure boundaries, trust-policy equivalence, recovery-attestation portability, or aggregate rollups.

Moved out of the monolithic validator:

```text
anchor freshness age arithmetic
checkpoint_consistency.checked_at <= anchor_evaluation.evaluated_at
witness_cohort_evaluation.observed_at <= anchor_evaluation.evaluated_at
```

Added there:

```text
replay_event.replayed_at <= anchor_evaluation.evaluated_at
transparency_anchor.logged_at <= anchor_evaluation.evaluated_at
anchor_freshness.basis_time == transparency_anchor.logged_at when basis is logged_at
split_view_boundary.first_observed_at <= anchor_evaluation.evaluated_at
witness split-view signal first_observed_at <= anchor_evaluation.evaluated_at
```

## Fixture strategy

The three new negative fixtures are rendered JSON files for review, but each is checked by `tests/fixture-derivations.yaml` as a patch from `examples/evaluator/replay-transparency-receipt-p3-witnessed.json`. This reduces copy-drift without removing human-readable test artifacts.

## Boundary

No new TimeState field, profile registry, evidence class, or transport rule was added. This is an executable coherence pass, not a doctrine expansion.
