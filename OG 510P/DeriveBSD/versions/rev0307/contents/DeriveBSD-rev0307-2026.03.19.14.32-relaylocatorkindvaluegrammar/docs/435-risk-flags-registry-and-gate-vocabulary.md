# Risk flags registry (stable gate vocabulary)

**Tier:** A (Core)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD diffs are **stable review surfaces**. Many diffs include a small `risk_flags` set suitable
for:
- reviewer UI (quick scanning / sorting)
- policy gates (promotion rules)
- drift bundle summaries

This doc makes the `risk_flags` vocabulary **explicit and stable** by introducing a typed registry:
- `risk.flag.registry` (`spec/risk.flag.registry.schema.json`)

Why this exists:
- **Entropy control:** “risk flag strings” otherwise drift into ad-hoc, inconsistent names.
- **Gate explainability:** policy can say “blocked because `raw-blobs-enabled`” (stable reason code).
- **Interop without forks:** adapters can map foreign signals into canonical flags.

See also:
- Canonical diff list: `docs/430-diff-surface-registry.md`
- Drift bundles (review funnel): `docs/395-drift-bundles-and-review-summaries.md`
- Feature intake rubric (new flags are design surface): `docs/348-design-review-rubric-and-feature-intake.md`

## The artifact

`risk.flag.registry` is a small registry of:
- canonical `id` (kebab-case)
- severity (coarse UI hint)
- optional aliases (legacy ids or adapter imports)
- typical sources (which diff kinds may emit it)
- default gate posture (advisory/approve/two-person/block)
- optional profile overrides (A–D viable without forks)

The registry is intended to be:
- referenced by policy and UI
- included in context packs
- treated as a **stable contract** (changes are RFC/ADR-worthy if they affect gates)

## Rules

1) **Diff outputs MUST use canonical ids**.
   - Adapters may accept aliases on input and map them to canonical ids.

2) Introducing a new `risk_flags` id requires:
   - adding it to `risk.flag.registry`
   - updating the relevant wiring doc to show how it affects gates
   - avoiding design tourism: keep the vocabulary small and reusable

3) `risk_flags` are **not** a substitute for full diffs.
   - reviewers and gates should still anchor on the typed diff contents.
   - `risk_flags` are the “summary reason codes”.

## Policy gates

DeriveBSD gate policy can be expressed in multiple ways (choose an engine as an implementation detail):
- Open Policy Agent (OPA) for policy-as-code evaluation: https://www.openpolicyagent.org/
- Kubernetes-style admission policy patterns (CEL/validating admission): https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/

The registry exists so gate decisions can be explained using stable, portable reason codes.

## Examples

- `export.policy.diff` emits `raw-blobs-enabled` when export policy broadens to allow raw blobs.
  Policy can:
  - require two-person integrity in fleet/appliance profiles
  - block entirely in regulated factory lanes

- `fw.inventory.diff` emits `trust-roots-changed` when Secure Boot digests drift.
  Policy can:
  - require quarantine/promote receipts and provenance evidence

Last updated: 2026-02-27r152
