# TimeSync rev0097 audit — policy-lifecycle temporal boundary and fixture derivation

## Finding 1 — lifecycle-authority evidence could be later than the status it supported

rev0096 had strong replay-transparency and transport-envelope timestamp checks, but lifecycle-authority validation still mixed business rules with a small inline replay-evaluation time loop. That loop checked several authority fields against `anchor_evaluation.evaluated_at`, but it did not centralize the relationship between lifecycle-authority events and `transparency_trust_policy_reference.lifecycle_status.evaluated_at`.

rev0097 adds `tools/policy_lifecycle_temporal.py`. When a lifecycle-authority reference is consumed by a trust-policy lifecycle status, authority discovery, renewal hints, anti-rollback sequence checks, freeze-status basis time, rotation/delegation checks, compromise checks, and nested recovery-attestation event times must not occur after `lifecycle_status.evaluated_at`.

## Finding 2 — recovery attestations needed a compromise-response clock boundary

Contained-compromise recovery attestations are compact replay-visibility status material. They do not import forensics or authority registries, but they still need artifact-time plausibility. Before rev0097, an attestation could be verified or portability-checked after the compromise response that relied on it.

rev0097 rejects that pattern. Recovery-attestation `issued_at`, `verified_at`, `incident_window.contained_at`, and `portability.portability_checked_at` must not be after `compromise_response.checked_at` when the attestation supports that response.

## Finding 3 — anti-rollback freeze basis needed to predate the sequence check

The anti-rollback sequence already required fresh status and age bounds, but the status basis timestamp was not tied to `anti_rollback_sequence.checked_at`. rev0097 rejects `freeze_check.basis_time` values after the sequence check they support.

## Refactor result

`tools/validate_archive.py` delegates lifecycle-authority temporal ordering to `tools/policy_lifecycle_temporal.py`. This does not fully solve validator size, but it removes another high-risk timestamp family from the monolith and gives the helper its own self-test.

## New negative fixtures

```text
examples/negative/policy-lifecycle-authority-freeze-basis-after-sequence-invalid.json
examples/negative/replay-transparency-policy-authority-discovery-after-lifecycle-invalid.json
examples/negative/replay-transparency-recovery-attestation-after-compromise-invalid.json
```

All three are derivation-checked in `tests/fixture-derivations.yaml`.

## Remaining risk

FT-0090 should remain open, but the remaining work should stay practical: extract concern families where it reduces executable complexity, and convert copied negative fixture families into derivation-checked fixtures where it prevents drift.
