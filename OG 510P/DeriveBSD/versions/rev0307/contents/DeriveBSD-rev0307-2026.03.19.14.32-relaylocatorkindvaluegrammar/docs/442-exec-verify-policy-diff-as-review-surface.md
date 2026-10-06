# Verified execution policy diff as a review surface

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate, Bundles  

DeriveBSD now treats execution integrity as a **typed contract**:

- authoritative policy: `exec.integrity.policy`
- authoritative activation result: `exec.integrity.receipt`
- backend observation: `exec-verify-snapshot`, `exec-verify-event`

The operator pain point remains the same:
**when execution-integrity posture drifts, reviewers need a compact, stable, gateable surface**.

This doc keeps `exec.verify.policy.diff` as that surface.

## The artifact

- Schema: `spec/exec.verify.policy.diff.schema.json`
- Example: `spec/examples/exec.verify.policy.diff.json`

The artifact name stays historic for continuity, but the compared objects are **authoritative `exec.integrity.policy` digests**.

An `exec.verify.policy.diff` summarizes:

- scope mode drift (`off` / `warn` / `enforce`)
- allowed-source drift
- explicit exception drift

## Where it shows up

### Drift bundles (review funnel)

If execution-integrity posture changes between generations, attach:

- the old `exec.integrity.policy` digest
- the new `exec.integrity.policy` digest
- an `exec.verify.policy.diff` (preferred)

This keeps runtime-integrity posture reviewable without forcing every profile to adopt the same backend.

### Incident/support bundles

When execution integrity is enabled, incident bundles should include:

- the latest `exec.integrity.receipt`
- any relevant `exec-verify-snapshot` / `exec-verify-event` observations in the bundle window
- and optionally the `exec.verify.policy.diff` if policy drift is part of the incident story

That makes “why did execution get denied?” answerable without collapsing policy and telemetry into one object.

## Typical gates

Execution-integrity drift is posture drift.
Typical gate posture is profile-aware:

- **relaxation is high leverage:** `enforce→warn` or `warn→off` should require explicit approval and a declared recovery window
- **disabling is often unacceptable in strict profiles:** treat `off` as a breakglass-style exception or block it entirely
- **new exceptions should be rare:** additions should be linked to a decision record and a removal plan
- **new source classes matter:** adding broader execution sources should be reviewed like any other authority expansion

If an interop story needs weaker execution-integrity posture, it must live in a **killable adapter lane**, never as a permanent silent global requirement.

## Risk flags

`exec.verify.policy.diff` may emit canonical `risk_flags`:

- `exec-verify-disabled`
- `exec-verify-relaxed`
- `exec-verify-exception-added`

See: `docs/435-risk-flags-registry-and-gate-vocabulary.md`.

## Related docs

- `docs/289-exec-integrity-policy-and-verified-execution.md`
- `docs/233-verified-execution-as-evidence.md`
- `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`
- `docs/430-diff-surface-registry.md`
- `docs/395-drift-bundles-and-review-summaries.md`

Last updated: 2026-03-07r215
