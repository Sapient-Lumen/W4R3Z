# Time source policy diff as a review surface

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

Time is an **evidence primitive**.
If a system’s time-source allowlist, quorum policy, or bootstrap rules change silently, you lose confidence in:
- certificate validity decisions,
- attestation timelines,
- incident ordering,
- any evidence that depends on trustworthy timestamps.

This doc introduces a stable review surface for time-source posture drift:

- Diff kind: `time.source.policy.diff`
- Schema: `spec/time.source.policy.diff.schema.json`
- Example: `spec/examples/time.source.policy.diff.json`

The diff compares two signed `time-source-policy` objects (by digest) and emits a compact, deterministic summary of:
- sources added/removed/changed,
- quorum changes,
- bootstrap changes,
- optional `risk_flags` (canonical ids; see below).

## Where this fits in DeriveBSD

- **Evidence spine:** time discipline artifacts (inventories, snapshots, receipts, proof bundles) are part of the platform truth spine. This diff is the *review surface* for time-source posture drift.
- **Review funnel:** when a promoted generation changes the active `time-source-policy` digest, attach `time.source.policy.diff` to the `drift.bundle` as an optional posture diff.

See:
- Time as evidence: `docs/227-time-discipline-and-trustworthy-timestamps-as-evidence.md`
- Time sources in practice: `docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md`
- Profile floors: `docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`
- Drift bundles: `docs/395-drift-bundles-and-review-summaries.md`
- Diff registry: `docs/430-diff-surface-registry.md`

## Drift bundle wiring

When the activated `time-source-policy` digest changes:
- produce `time.source.policy.diff` (`from_policy.digest` → `to_policy.digest`),
- attach it to the drift bundle alongside other posture diffs (e.g. `boot.manifest.diff`, `pki.trust.bundle.diff`),
- optionally attach supporting evidence:
  - `time.sync.receipt` for the activation window (did we converge?),
  - `time.proof.bundle` when the policy requires authenticated proofs.

Policy decides whether the diff is required for promotion (profile-aware).

## Risk flags

Diff summaries should use canonical ids from `risk.flag.registry`.
Minimal starter set for time-source posture drift:

- `time-source-added` — a new time source was added.
- `time-source-removed` — a time source was removed (may reduce redundancy).
- `time-source-changed` — an existing source changed endpoint/protocol/parameters.
- `time-source-trust-root-changed` — a source’s `trust_root_digest` changed.
- `time-quorum-relaxed` — quorum policy weakened (e.g., `min_sources` decreased or `max_skew_ms` increased).
- `time-bootstrap-relaxed` — bootstrap rules weakened (e.g., RTC allowed, larger forward/backward jumps).

## Suggested gates

These are suggested **defaults**; profiles/policy can tighten or relax:

- If `risk_flags` contains `time-quorum-relaxed` or `time-bootstrap-relaxed`, require explicit approval; for high assurance profiles (A/D), consider two-person integrity.
- If `risk_flags` contains `time-source-trust-root-changed`, require a provenance note and (when applicable) ensure the referenced trust root is governed by a reviewed trust bundle (pair with `pki.trust.bundle.diff`).
- If `risk_flags` contains `time-source-added`, consider requiring a `time.sync.receipt` (convergence evidence) after activation.

## Notes

- This diff is **posture drift**, not runtime health. Runtime health stays in snapshots/receipts (`time.sync.snapshot`, `time.sync.receipt`).
- Avoid forking by expressing stricter requirements as profile/policy gates (e.g., “fleet host requires 2-of-3 quorum and NTS-only”).

Last updated: 2026-03-23r453
