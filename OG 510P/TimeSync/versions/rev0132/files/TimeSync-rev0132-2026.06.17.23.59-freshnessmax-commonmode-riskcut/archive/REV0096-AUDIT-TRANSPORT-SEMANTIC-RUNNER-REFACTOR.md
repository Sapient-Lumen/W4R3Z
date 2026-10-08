# rev0096 audit — transport envelope temporal boundary and semantic-vector runner refactor

rev0096 continues FT-0090 with executable changes instead of doctrine growth.

## Transport-envelope temporal boundary

Prior revisions validated payload semantics inside transport envelopes, but did not check whether the envelope `sent_at` was earlier than semantic event timestamps in the payload. This created an artifact-time inconsistency: an envelope could appear to carry facts before those facts existed.

`tools/transport_envelope_temporal.py` now rejects that pattern. The helper is generic over payloads but intentionally narrow over timestamp names. It checks event timestamps and avoids future-looking window bounds.

## Semantic-vector runner extraction

`tools/semantic_vectors.py` now owns:

```text
semantic vector duplicate-ID detection
example fixture coverage checks
fail_json expectation handling
pass/fail_schema/fail_semantic accounting
expected_error_contains matching
```

The archive validator passes in callbacks for schema and semantic checks. That keeps the runner independent of the profile catalog, adapter catalog, and schema registry details.

## Fixture derivation

The three new transport negatives are rendered JSON fixtures, but they are also declared in `tests/fixture-derivations.yaml`. This keeps audit review easy while reducing copy-paste drift.

## Do not overgeneralize

The new `sent_at` check is not a freshness rule. It is an artifact-order sanity check. Transport authentication, signatures, file timestamps, stream offsets, and API poll times still cannot update TimeState or satisfy profile obligations.
