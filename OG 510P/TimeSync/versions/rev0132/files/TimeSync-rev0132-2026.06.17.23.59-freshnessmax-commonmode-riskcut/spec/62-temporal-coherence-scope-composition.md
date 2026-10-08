# 62 — Temporal coherence for scope composition

rev0090 adds executable temporal coherence to mixed-layer scope-composition guards.

## Problem

A composed surface can be valid in isolation and still be unsafe as a current guard input if it was observed at a stale or incompatible time. A profile-drift decision, downgrade proof, digest-binding policy, lifecycle check, revocation check, lifecycle rollup, and transparency-policy observation must not be combined into one current-use guard merely because each surface validates independently.

## Required guard fields

`scope-composition-guard` now requires `temporal_coherence` with:

```text
policy_version
evaluation_window
input_observations
coherence_decision
non_provenance_boundary
```

A current guard requires `coherence_decision.decision = coherent_current_guard`, `all_current_inputs_within_window = true`, `guard_evaluated_within_window = true`, and `stale_input_blocks_current_use = true`.

## Required timestamp roles

Current-use surfaces require these observation roles:

```text
profile_compatibility_drift -> profile_drift_evaluated_at
discovery_version_negotiation -> discovery_negotiated_at
discovery_digest_binding -> digest_policy_checked_at
aggregate_correction_authority_lifecycle -> lifecycle_checked_at, revocation_checked_at
aggregate_lifecycle_rollup -> lifecycle_rollup_checked_at
transparency_trust_policy_lifecycle -> transparency_policy_checked_at
mixed_layer_portability_review -> decision_matrix_observed_at
```

## Fail-closed behavior

A stale or unchecked current-use input must block current use through `suppress_current_use`, `historical_only`, or `fail_closed`. A guard may not claim current use when a current surface observation is stale, unchecked, missing, or outside the declared evaluation window.

## Boundary

Temporal coherence is guard metadata. It constrains composition and freshness assumptions, but it does not update TimeState, profile assessment, profile conformance, actionability, or time-source provenance.

## rev0091 hardening

Current-use input observations must also satisfy two ordering checks:

```text
observed_at <= guard.evaluated_at
guard.evaluated_at - observed_at <= max_age_seconds when max_age_seconds is declared
```

These checks prevent a broad evaluation window from admitting observations that were not available at guard evaluation time, and prevent declared freshness limits from becoming unchecked labels.
