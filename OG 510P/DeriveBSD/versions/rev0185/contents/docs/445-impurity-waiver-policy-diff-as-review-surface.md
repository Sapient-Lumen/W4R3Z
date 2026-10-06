# Impurity waiver policy diff as a review surface (`impurity.waiver.policy.diff`)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt, Bundles

DeriveBSD is **deterministic-by-default**, but real ecosystems leak “ambient impurity”:

- time/entropy
- environment probing
- host-specific firmware/microcode payloads
- adapter lanes (ports/pkg) that were not designed for hermetic builds

Non‑negotiable stance: **impurity is policy-controlled and receipted**.

This doc introduces a small, typed control surface that makes that stance operational:

- `impurity.waiver.policy` — explicit, time‑bounded impurity allowances (allowlist)
- `impurity.waiver.policy.diff` — a stable review surface for drift bundles + gates

The goal is to prevent “known impurities” from becoming folklore (“it flakes sometimes, shrug”).

## 1) What the policy controls

## The artifacts

Primary review surface: `impurity.waiver.policy.diff`

Schema (policy): `spec/impurity.waiver.policy.schema.json`  
Example (policy): `spec/examples/impurity.waiver.policy.json`

Schema (diff): `spec/impurity.waiver.policy.diff.schema.json`  
Example (diff): `spec/examples/impurity.waiver.policy.diff.json`

`impurity.waiver.policy` is the single object that answers:

- which impurity ids are allowed (by `impurity_id`)
- where they are allowed to apply (scope metadata)
- when they expire (`expires_at`)
- what evidence must accompany a use (e.g., diff reports)

Design intent:

- **Default deny:** unknown impurity ids are not tolerated unless explicitly waived.
- **Time-bounded:** waivers must expire; extensions are review events.
- **Evidence-bound:** if a waiver is used, required receipts/reports must be attached.

This keeps the reproducibility pillar crisp without forcing every profile to run every optional lane.

## 2) Where this plugs in

### Determinism checks (`repro.check.*`)

`repro.check.plan.known_impurity_ids[]` should be interpreted as **references to waivers**:

- If a check result is `known_impurity`, the receipt should include:
  - the `impurity.waiver.policy` digest in force
  - the waiver ids that justified the classification

This turns “known impurity” into a queryable, auditable choice.

See: `docs/367-reproducible-generations-and-determinism-checks.md`.

### Build stabilizers (optional)

If a stabilizer lane is enabled, a waiver can require specific stabilizer receipts (or forbid stabilizers entirely).
This prevents “normalization” from becoming an unreviewed impurity sink.

See: `docs/431-build-stabilizers-and-determinism-normalizers.md`.

## 3) Why a typed diff exists

Without a stable diff surface, impurity policy drifts invisibly:

- waivers get added “temporarily” and never removed
- scopes expand (e.g., adapter-only → all builds)
- expiry gets extended repeatedly
- default posture relaxes

`impurity.waiver.policy.diff` makes this drift mechanical:

- **Stable review surface** for reproducibility posture.
- **Gateable** additions, scope broadenings, and expiry extensions.
- **Bundle-friendly** attachment: the diff can travel in `drift.bundle.artifacts`.

## 4) Tiering and product-shape viability

- **Tier B (Base):** the policy + diff surface exist so “known impurity” is never ambient.
- **Tier C (Optional lane):** determinism checks and stabilizers remain optional, profile-selected lanes.

Profiles use this surface differently:

- **Appliance / regulatory (D):** default deny; short expiries; strict evidence requirements.
- **Fleet host (A):** default deny; allow only narrowly scoped waivers; require two-person integrity for extensions.
- **Workstation / general OS (B/C):** allow adapter-lane waivers in bounded scopes, still time-bounded and receipted.

## 5) Wiring into drift bundles + gates

When impurity waiver policy changes between generations, include `impurity.waiver.policy.diff` in the drift bundle:

- `drift.bundle.artifacts[]` entry with `kind: impurity.waiver.policy.diff`
- pair it with the “consequences” evidence when relevant:
  - `repro.check.receipt` (match / known_impurity / mismatch)
  - `closure.diff` (new code ingress, especially via adapters)

Policy can gate promotion on `summary.risk_flags` using the canonical risk-flag registry.

## Risk flags

The diff summary should emit stable reason codes (canonical ids) so gates and reviewers have consistent semantics:

- `impurity-waiver-added`
- `impurity-waiver-extended`
- `impurity-waiver-scope-broadened`
- `impurity-default-relaxed`

See: `docs/435-risk-flags-registry-and-gate-vocabulary.md`.

## References (primary)

- Nix experimental feature: impure derivations (explicitly marking non-fixed outputs): https://nix.dev/manual/nix/2.21/contributing/experimental-features#impure-derivations
- Reproducible Builds tooling overview: https://reproducible-builds.org/tools/

Last updated: 2026-02-28r172
