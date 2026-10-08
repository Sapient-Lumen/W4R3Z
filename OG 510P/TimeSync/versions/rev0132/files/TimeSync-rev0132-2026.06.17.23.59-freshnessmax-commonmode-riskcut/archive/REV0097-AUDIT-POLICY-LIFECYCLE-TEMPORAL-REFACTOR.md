# rev0097 audit — policy-lifecycle temporal refactor

rev0097 continues FT-0090 with executable validation changes only.

## What was risky

Policy-lifecycle authority references are intentionally compact and non-provenance. That makes them safer than importing policy repositories or authority registries, but it also means every timestamp boundary has to be explicit. The remaining gap was not conceptual vocabulary; it was simple ordering:

```text
status evidence must exist before the lifecycle status that consumes it
recovery attestation checks must exist before the compromise response that consumes them
current replay visibility must not rely on authority evidence gathered after replay evaluation
```

## What changed

`tools/policy_lifecycle_temporal.py` now centralizes those checks. It covers:

```text
discovery.discovered_at
renewal_hint.hint_checked_at
anti_rollback_sequence.checked_at
anti_rollback_sequence.freeze_check.basis_time
rotation_delegation_status.rotation_checked_at
rotation_delegation_status.delegation_checked_at
rotation_delegation_status.compromise_response.checked_at
recovery_attestation_reference.issued_at
recovery_attestation_reference.verified_at
recovery_attestation_reference.incident_window.contained_at
recovery_attestation_reference.portability.portability_checked_at
```

The helper is wired into `check_policy_lifecycle_authority_reference` and `check_policy_lifecycle_authority_recovery_attestation`.

## What did not change

The revision does not add a policy repository, authority registry, status endpoint, recovery protocol, incident forensics model, or trust-anchor system. It only rejects impossible or stale compact status relationships.

## Fixture strategy

The three new negatives are derivation-checked. Rendered JSON remains in `examples/negative/` for audit review, while `tests/fixture-derivations.yaml` proves the files match a positive base plus explicit mutations.
