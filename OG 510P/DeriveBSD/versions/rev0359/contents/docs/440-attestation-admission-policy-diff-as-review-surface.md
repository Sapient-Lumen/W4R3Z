# Attestation admission policy diff as a review surface

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

Remote attestation only becomes operationally meaningful when other subsystems **gate admission** on verifier-issued receipts.
That immediately creates a new high-leverage drift surface:

- *what* actions are gated,
- *who* the rule applies to,
- *which* `attestation.requirement` digest is required.

This doc introduces a stable review surface for that drift:

- Diff kind: `attestation.admission.policy.diff`
- Schema: `spec/attestation.admission.policy.diff.schema.json`
- Example: `spec/examples/attestation.admission.policy.diff.json`

The diff compares two `attestation-admission-policy` objects (by digest) and emits a compact, deterministic summary of:
- rules added/removed (keyed by `(action, selector)`),
- requirement changes for existing `(action, selector)` pairs,
- optional `risk_flags` (canonical ids; see below).

## Where this fits in DeriveBSD

- **Policy as evidence:** `attestation.admission.policy` is a typed policy input that other gates reference (issue identity, unseal secrets, join fleet, promote update, allow remote assist). It does not replace the authoritative action receipt that records the final `attestation_verification` decision.
- **Review funnel:** when the active admission policy digest changes, attach `attestation.admission.policy.diff` to the `drift.bundle` as a posture diff.
- **No forks:** profiles decide strictness (A/D can require two-person integrity for removals; B/C can be advisory) without changing the artifact shape.

See:
- Remote attestation admission & enrollment: `docs/388-remote-attestation-admission-and-enrollment.md`
- Drift bundles: `docs/395-drift-bundles-and-review-summaries.md`
- Diff registry: `docs/430-diff-surface-registry.md`

Ecosystem anchors (for intuition, not copy/paste):
- Red Hat Enterprise Linux 10 Keylime guide (attestation is valuable when it gates actions): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/security_hardening/ensuring-system-integrity-with-keylime
- Azure Trusted Launch (measured boot/vTPM posture as a trust decision input): https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch

## Profile-aware review expectations

The diff artifact stays the same across profiles, but the default consequences differ:

- **A / fleet_host**: weakening or removing a rule that gates secrets, identity issuance, rollout, or recovery should normally be treated as a sensitive review event.
- **B / workstation**: review should preserve the rule that attestation gates sensitive operations, not ordinary local use; changes that accidentally make remote verifier reachability a hard dependency deserve extra scrutiny.
- **C / general_os**: explicit gates may exist, but drift should not silently redefine ordinary installs into verifier-dependent systems.
- **D / appliance_factory**: weakening production enrollment, maintenance, or secret-release gates should normally require stronger approval and durable evidence.

## Drift bundle wiring

When the verifier’s active `attestation.admission.policy` digest changes:

- generate `attestation.admission.policy.diff` (`from_policy.digest` → `to_policy.digest`),
- attach it to the drift bundle alongside other posture diffs (e.g. `boot.manifest.diff`, `pki.trust.bundle.diff`),
- optionally attach supporting evidence:
  - the referenced `attestation.requirement` objects (so reviewers can see the full requirement graph),
  - a verifier `lint-report` (policy lint + requirement graph lint),
  - a short “why” note in the drift bundle review summary.

Policy decides whether the diff is required for promotion (profile-aware).

## Risk flags

Diff summaries should use canonical ids from `risk.flag.registry`.
Minimal starter set for admission policy drift:

- `attestation-admission-policy-changed` — umbrella flag for admission-policy drift.
- `attestation-admission-rule-added` — a new `(action, selector)` rule was added.
- `attestation-admission-rule-removed` — a `(action, selector)` rule was removed (risk: previously gated action becomes ungated or denied-by-default posture changes).
- `attestation-admission-requirement-changed` — an existing rule’s `requirement_ref` changed.

Last updated: 2026-03-07r221
