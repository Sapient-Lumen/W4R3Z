# Export policy diff as a review surface (gate data egress drift)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** operability, supply-chain, reproducibility
**Patterns:** Registry→Diff→Gate, Plan→Receipt, Bundles

DeriveBSD treats **exporting evidence** (support bundles, crash reports, diagnostic artifacts) as a distinct capability:
- the *selection* is explicit (`bundle.plan` when used)
- the *redaction transforms* are explicit (`redaction.transform` + `redaction.receipt`)
- the *act of exporting* is explicit and receipted (`export.policy` + `export.receipt`)

What was missing is a compact, mechanical answer to:

> **What changed in our export boundary posture?**

Without a typed diff, export policies drift like folklore:
- new recipients slip in as “temporary exceptions”
- encryption/consent constraints quietly relax
- raw blob uploads (coredumps, traces) get enabled under pressure

That kind of drift degrades **forensics UX** (nobody can explain “why was this shared?”) and **provenance posture** (exports become unreviewable exfil events).

This doc introduces a single stable diff artifact that makes export-policy drift **reviewable**, **gateable**, and **attachable to drift/support bundles**.

## The artifact: `export.policy.diff`

`export.policy.diff` compares two `export.policy` objects (by digest) and emits a compact drift surface:

- consent posture drift (interactive / two-person / approver set)
- recipient constraint drift (class / identifiers / ticket requirements)
- encryption posture drift (mode / recipients)
- transport adapter constraint drift (`transport_policy_digest`)
- transparency posture drift (mode / required)
- per-artifact rule drift (added/removed/changed rules)
- optional `risk_flags` suitable for review UI + policy gates

Schema: `spec/export.policy.diff.schema.json`  
Example: `spec/examples/export.policy.diff.json`

### Noise rule (keep the diff surface stable)

`export.policy.diff` is intentionally **high-signal**.
It does not attempt to fully restate the policy, and it does not replace the export receipt stream.

- If you need “what was exported in a specific incident”, that belongs in `export.receipt` and the incident bundle timeline.
- If you need “what redaction transform ran”, that belongs in `redaction.receipt`.

Keep the diff surface stable so it remains a crisp review surface.

## Where it plugs in

### 1) Drift bundles (one review attachment)

Export policy changes are **trust-boundary posture changes**.
When the active export policy digest changes between generations (or between policy promotions), attach `export.policy.diff` to the `drift.bundle` next to other operator-facing drift surfaces.

See: `docs/395-drift-bundles-and-review-summaries.md` and `docs/430-diff-surface-registry.md`.

### 2) Evidence spine (egress is evidence)

Forensics UX improves when “sharing” is explainable:
- which export policy digest was in force,
- what constraints applied (consent/encryption/recipient class),
- what changed in those constraints (the diff),
- and what actually happened (the export receipt).

See: `docs/229-evidence-spine-overview.md` and `docs/251-export-policies-and-support-bundle-portal.md`.

### 3) Policy gates

Policy can require `export.policy.diff` in higher-assurance lanes:
- any consent relaxation (two-person → one-person; interactive approval disabled)
- any recipient-class broadening (`internal` → `external-vendor` → `public`)
- any encryption downgrade or keyset expansion
- any rule change that enables raw blob uploads
- any new transport adapter surface

Gates can start small:
- fail promotion if `risk_flags` includes `raw-blobs-enabled` without explicit waiver
- require two-person integrity if `risk_flags` includes `new-external-recipient` in fleet/appliance profiles

## Risk flags (minimal starter set)

Diff generators should emit conservative flags (low false-negative bias):

- `raw-blobs-enabled`
- `consent-relaxed`
- `new-external-recipient`
- `transparency-required`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References (ecosystem anchor points)

- sosreport (support bundle ecosystem baseline): https://github.com/sosreport/sos
- RHEL: generating sos reports for technical support: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html-single/generating_sos_reports_for_technical_support/index

Last updated: 2026-02-28r155
