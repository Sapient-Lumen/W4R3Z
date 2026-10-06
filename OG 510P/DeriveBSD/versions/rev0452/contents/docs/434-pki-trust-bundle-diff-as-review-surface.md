# PKI trust bundle diffs as review surfaces

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability, reproducibility, isolation
**Patterns:** Registry→Diff→Gate, Plan→Receipt, Bundles

Trust roots are a common place where real systems quietly lose discipline:
- trust stores drift across hosts and apps,
- “just add this root” becomes tribal knowledge,
- incident response cannot answer what roots were trusted *at the time*.

DeriveBSD already models trust roots as a signed store object: `pki-trust-bundle`.
This doc adds the missing ergonomic piece: a **typed, deterministic diff surface** for trust bundle drift.

## Artifact

- Diff kind: `pki.trust.bundle.diff`
- Schema: `spec/pki.trust.bundle.diff.schema.json`
- Example: `spec/examples/pki.trust.bundle.diff.json`

The diff compares two `pki-trust-bundle` objects (by digest) and emits a compact review surface:
- intended use tags added/removed,
- anchors added/removed,
- anchor metadata changes (constraints/labels/etc.),
- distribution selector drift (where the bundle applies).

This is a *review surface*, not an execution primitive.
Execution/apply proof remains distinct: `pki.trust.bundle.apply.receipt` answers which exact trust view a host or unit actually served, while issuance/rotation stays under `docs/228-pki-and-identity-lifecycle-as-evidence.md`.

## Where it fits

### Drift bundles

When a generation update changes the effective trust bundle digests for a host/unit, the diff can be attached to the drift bundle:
- `drift.bundle` links to `pki.trust.bundle.diff` alongside other canonical diffs.

This keeps “trust drift” reviewable in the same funnel as:
- `authority.diff` (capability creep)
- `trust.boundary.diff` (new crossings)
- `crypto.diff` (suite/key policy drift)

See: `docs/395-drift-bundles-and-review-summaries.md` and `docs/430-diff-surface-registry.md`.

### Evidence spine

Trust bundles remain first-class evidence objects, the diff stays the “what changed?” companion artifact, and `pki.trust.bundle.apply.receipt` is the “what exact trust view was served?” companion artifact.
See: `docs/229-evidence-spine-overview.md`, `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`.

## Typical gates / flags

Policy can gate on the diff summary and/or its derived `risk_flags`.
Conservative defaults for high-assurance profiles (A / D) now come from `docs/480-trust-bundle-posture-by-profile.md` and often include:
- **new anchor added** → require review + two-person integrity
- **anchor removed** → require review + rollout staging
- **constraints broadened** (name constraints, validity windows) → require explicit justification
- **distribution broadened** (bundle applies to more nodes) → require review

Lower-assurance profiles can keep the diff advisory, but still gain explainability.

## Adapters (no forks)

Interop renderers (OpenSSL CAfile, NSS DB, p11-kit, etc.) remain **killable adapters**.
This diff surface is adapter-agnostic: it reviews the *governed trust bundle*, not the rendering.

See: `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/327-shadow-trust-and-system-ca-governance.md`.

Last updated: 2026-03-21r352
