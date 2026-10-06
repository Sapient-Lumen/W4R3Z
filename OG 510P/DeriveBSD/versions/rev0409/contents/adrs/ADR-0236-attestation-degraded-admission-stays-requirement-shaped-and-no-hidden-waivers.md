# ADR-0236: Attestation degraded admission stays requirement-shaped and forbids hidden waivers

- Status: Accepted
- Date: 2026-03-21
- Deciders: DeriveBSD archive maintainers

## Context

Recent archive cuts already fixed several expensive attestation ambiguities:

- reference authoring is cohort/replay-first by default,
- non-baseline references are explicit timeboxed exceptions,
- reference selection is exact-digest-pinned,
- attester identity provenance is digest-joined,
- and authoritative consuming receipts pin the exact requirement/receipt/policy tuple.

That still leaves one quiet loophole:
**what does it mean when an authoritative action proceeds under `attestation_verification.decision = degraded`?**

Without a narrow answer, implementations will drift toward one or more hidden behaviors:

- verifier-side override rows,
- portal-only “allow degraded just this once” buttons,
- ticket prose that silently widens a gate,
- or action-specific secret/broker logic that treats `degraded` as an ambient soft-pass.

Those are exactly the kinds of backend-state folklore this archive has been cutting away.

## Decision

**In v0, degraded attestation admission stays requirement-shaped. There is no hidden degraded-waiver lane.**

That means:

1. `attestation.requirement.min_verdict` is the sole portable artifact knob that allows a consuming action to proceed under degraded posture.
2. If an authoritative action receipt records `attestation_verification.decision = degraded`, the exact consumed `attestation.requirement` must itself allow `min_verdict = degraded`.
3. Notes, dashboards, verifier database rows, or ticket systems must not silently widen a `pass` requirement into a degraded acceptance.
4. If a deployment needs to proceed despite failing the reviewed requirement, the answer is not a hidden verifier waiver. It must instead use an already-authoritative lane such as a changed reviewed requirement/policy or an action-specific emergency lane (for example breakglass), with its own receipt trail.

## Consequences

### Positive

- Degraded posture stays reviewable in typed policy instead of service memory.
- A/B/C/D can explain why degraded authority happened using the same digest-bound artifacts they already export.
- Implementations do not need a second implicit exception database just to explain why a degraded action was still allowed.

### Negative / limits

- This does **not** settle the entire future vocabulary for collect-only vs visible-warning vs hard-gate UX.
- This does **not** define a generic cross-lane “waive attestation” subsystem.
- Some deployments may need richer future policy constructs; those should arrive later as explicit RFC/ADR work, not as hidden service behavior.

## Why this is the right small hard decision now

This cut removes one more silent implementation choice without inventing a broad new subsystem.
It keeps the archive converging toward implementable truth:
when degraded posture is accepted, the reviewed requirement says so.
