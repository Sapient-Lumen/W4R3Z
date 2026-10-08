# REV0093 to REV0094 migration map

## Revision character

rev0094 continues FT-0090 by extending the temporal helper to the next two highest-risk current-use surfaces: discovery result freshness and authorized-verifier portable-result replay windows.

## Files changed materially

```text
schema/discovery-request.schema.json
tools/temporal_coherence.py
tools/validate_archive.py
tests/semantic-test-vectors.yaml
examples/discovery-request-with-version-negotiation.json
examples/discovery-request-with-byte-envelope-binding.json
examples/discovery-request-with-downgrade-proof.json
examples/discovery-request-with-scope-composition-guard.json
examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json
```

## New negative fixtures

```text
examples/negative/discovery-current-result-stale-freshness-invalid.json
examples/negative/discovery-current-result-missing-freshness-invalid.json
examples/negative/discovery-current-result-basis-mismatch-invalid.json
examples/negative/authorized-verifier-challenge-revocation-after-state-invalid.json
examples/negative/authorized-verifier-challenge-replay-before-response-invalid.json
examples/negative/authorized-verifier-challenge-replay-not-usable-invalid.json
examples/negative/authorized-verifier-challenge-replay-after-window-invalid.json
```

## Semantic-vector delta

```text
rev0093: 267 semantic vectors
rev0094: 274 semantic vectors
```

## Compatibility note

Current-use discovery result items now need `freshness` metadata. Historical or metadata-only discovery results are not made invalid solely because they omit it. Authorized-verifier replay remains limited to commitment verification and now has stricter timestamp ordering for the portable-result status and replay context.
