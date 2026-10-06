# Trust policy diffs as review surfaces

**Tier:** A (Core)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD treats **trust policy as data**: it is the authority for *which signatures, roles, and attestations are accepted*.
That authority is high-leverage enough that “we changed the trust rules” must never be folklore.

This doc adds a missing ergonomic: a **typed, deterministic diff surface** for trust policy drift.

## Artifact

- Diff kind: `trust.policy.diff`
- Schema: `spec/trust.policy.diff.schema.json`
- Example: `spec/examples/trust.policy.diff.json`

The diff compares two `trust-policy` objects (by digest) and emits a compact review surface:
- namespaces added/removed,
- per-namespace channel posture changes (rollback windows, expiry requirements),
- key set drift (added/removed/key material changes),
- target admission rule drift (required signers/attestations/closure proof).

This is a **review surface**, not an execution primitive.
Execution remains “evaluate trust-policy → record decision” in the normal Plan→Receipt/Evidence flow.

See: `docs/57-namespaces-channels-trust.md`, `docs/260-release-authority-policy-and-key-management.md`.

## Where it fits

### Drift bundles

When a generation change modifies the effective trust policy digest for a host/unit, attach the diff to the drift bundle:
- `drift.bundle` links to `trust.policy.diff` alongside other canonical diffs.

This keeps trust posture drift reviewable in the same funnel as:
- `pki.trust.bundle.diff` (root anchors and constraints)
- `trust.boundary.diff` (new crossings)
- `closure.diff` (new code/input surfaces)

See: `docs/395-drift-bundles-and-review-summaries.md` and `docs/430-diff-surface-registry.md`.

### Evidence spine

Trust policy is a first-class evidence object; the diff is the “what changed?” companion artifact.
See: `docs/229-evidence-spine-overview.md`.

## Risk flags

Diffs may emit `risk_flags` for gating/UI using stable ids from `risk.flag.registry`.

Recommended canonical reason codes for this surface:
- `trust-policy-changed` (any non-trivial trust-policy drift; treat as high leverage)

## Typical gates (suggested)

Profiles/policy may choose to gate harder on specific change classes even if the diff is always attached:

- key material drift for `root` or `signing` roles
- relaxations in `required_signers`, `required_attestations`, or `require_closure_proof`
- rollback/expiry relaxations on channels

## Notes / references

Trust policy diff surfaces align with established update/security models where policy and role separation are explicit.
Primary reference:
- The Update Framework (TUF) specification (roles, thresholding, rollback/freeze model): https://theupdateframework.github.io/specification/latest/

Last updated: 2026-02-28r167
