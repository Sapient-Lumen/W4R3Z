# 60 — Scope composition attack corpus

rev0088 adds an executable attack corpus for mixed-layer composition failures. The corpus lives in `tests/mixed-layer-scope-composition.yaml` and is validated by `check_scope_composition_decision_matrix(...)`.

The required rows are:

```text
safe-separated-mixed-layer-current-guarded
downgrade-cannot-bypass-lifecycle-suppression
lifecycle-rollup-cannot-bypass-profile-drift
transparency-policy-equivalence-cannot-reopen-profile-assessment
aggregate-rollup-cannot-update-actionability
unknown-newer-version-metadata-only
digest-binding-cannot-become-profile-evidence
```

The positive row permits guarded current interpretation only when each surface is current in its own scope and no surface attempts to update TimeState, profile assessment, or actionability. Attack rows must block unsafe upgrades and must not use `current_use_guarded` as the safe effect.

The corpus is intentionally small and compositional. It is not a provenance model, incident-response workflow, policy registry, credential system, transparency-log API, or evidence-sufficiency algorithm.
