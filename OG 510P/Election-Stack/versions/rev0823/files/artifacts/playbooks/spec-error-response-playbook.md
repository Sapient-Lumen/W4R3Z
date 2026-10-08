# Spec / verifier error response playbook (false-confidence incident)

**Track:** Shared (cross-cutting)


This playbook is for the failure mode: **the stack was followed, but the specification or verifier behavior was substantively wrong** (insufficient proof obligation, bad assumption, tool bug, misleading verifier output).

Treat this as a legitimacy incident: internal coherence is not evidence of correctness.

Canonical hazard/proof binding: **HZ-024 / PO-104**.

## Triggers (examples)
- Independent implementations disagree on digests/decisions for the same packet.
- A credible external review identifies a security-relevant assumption gap.
- A verifier-report example/regression vector fails after a change.
- Real-world pilot/adoption reveals a dispute the current evidence lanes cannot settle.

## Immediate actions (first 24 hours)
1) **Freeze:** stop silent patching. Record the issue as a bounded incident note (ADR or issue log entry) with a public pointer.
2) **Reproduce:** capture the smallest packet/vector that demonstrates the failure (ship as an example packet or test vector).
3) **Classify impact:** what claims/non-claims are affected? what catastrophe class does this enable?
4) **Publish a response note (bounded):**
   - what we believe is wrong,
   - what evidence supports that belief,
   - what is uncertain,
   - what changes are proposed, and what remains unchanged.
Template: `artifacts/templates/spec-error-response-note.md`.

5) **Add a regression vector:** update examples/tests so the specific failure cannot re-enter silently.

## Correction actions (next release)
- Update **claims/non-claims** (`166`/`167`) if the mistake changes the project’s warranty boundary.
- Update **proof obligations** (PO registry) and map affected hazards.
- Update tooling and **re-run the full release gate**; publish the new VERSION and MANIFEST.
- If the fix changes verifier semantics, publish a “compatibility note” (what old reports mean now).

## What not to do
- Do not “paper over” with prose-only patches.
- Do not rely on “expert says it’s fine” in place of regression vectors.
- Do not expand schemas unless a concrete dispute requires it.

## Outputs (must exist)
- ADR/incident note (with precise scope)
- Regression vector (example packet / test vector)
- Response note (bounded, publishable)
- VERSION bump + updated MANIFEST.sha256
