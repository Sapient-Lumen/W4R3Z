# Attestation degraded admission stays requirement-shaped and forbids hidden waivers

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

The archive already fixed the decisive attestation join on authoritative action receipts.
What still needed one more hard cut was the meaning of **`degraded` admission**.

If the archive leaves degraded acceptance fuzzy, implementations will quietly invent verifier-side override tables, policy-service switches, or portal-only “allow just this once” buttons.
That would put one of the most security-sensitive decisions right back into hidden state.

Related:
- ADR: `adrs/ADR-0236-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md`
- action-side exact tuple boundary: `docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
- evidence/admission boundary: `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`
- posture receipts as evidence: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- profile default: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`

## The boundary

In v0, degraded attestation admission stays **requirement-shaped**.

That means:

- `attestation.requirement.min_verdict = degraded` is the sole portable way to allow degraded posture.
- if an authoritative action receipt records `attestation_verification.decision = degraded`, the exact consumed `attestation.requirement` must itself allow `degraded`.
- notes, dashboards, verifier rows, or ticket prose must not silently widen a `pass` requirement.
- if an operator really needs to proceed despite a stricter requirement, the answer is not a hidden attestation-waiver lane. It must use an already-authoritative path such as a reviewed requirement/policy change or an action-specific emergency lane like breakglass.
- that same escape hatch now has a tighter rejected posture meaning too: ordinary authority does not silently succeed on `rejected`; explicit recovery must move into breakglass instead of hiding a rejected override inside a normal receipt.

## Why this matters

### 1) It keeps policy reviewable

The exact requirement digest already tells reviewers the freshness and minimum-verdict rule that was consumed.
Making degraded admission ride that same artifact keeps the archive honest.

### 2) It avoids a fake “later” subsystem

A hidden degraded-waiver table would feel convenient, but it would become the real product immediately.
DeriveBSD should not casually invent that second control plane.

### 3) It keeps A/B/C/D coherent

- **A / fleet host:** degraded secret release or identity issuance remains a reviewed policy choice, not an operator-memory trick.
- **B / workstation:** sensitive-operation gating can explain why degraded posture still counted without turning remote verifier UX into the authority source.
- **C / general-purpose OS:** optional attestation stays explicit when used.
- **D / appliance factory / regulatory:** audit review can prove that degraded admission was already in the approved requirement instead of reconstructed from backend state.

## Schema/example consequence

`spec/attestation.requirement.schema.json` now teaches this explicitly: `min_verdict = degraded` is the sole portable degraded-admission knob.

The consuming authority schemas (`secret-receipt`, `breakglass-receipt`, `workload-identity-issue-receipt`) now also teach the corresponding action-side rule:
`attestation_verification.decision = degraded` means the consumed requirement allowed degraded posture; v0 has no hidden degraded-waiver lane.

The archive also carries a canonical degraded-path example:

- `spec/examples/attestation.requirement.degraded.json`
- `spec/examples/secret.receipt.degraded.json`

That keeps the boundary checkable instead of aspirational.

## Guardrail

`tools/check_attestation_degraded_admission_contract.py`

This guardrail checks that:

- `attestation.requirement.min_verdict` teaches the no-hidden-waiver boundary,
- consuming authority schemas teach the same `degraded` meaning,
- the degraded requirement example actually uses `min_verdict = degraded`,
- and the degraded secret-receipt example binds to that exact requirement digest rather than a dashboard-only override story.

## What stays open

This cut does **not** settle:

- the full future UX vocabulary for collect-only vs warning vs hard-gate,
- every action type that may eventually want a richer degraded posture summary,
- or whether a future explicit attestation-exception lane is worth designing.

It only makes one narrow decision now:
**degraded admission must already be in the reviewed requirement, not in hidden service-side state.**

Last updated: 2026-03-21r378
