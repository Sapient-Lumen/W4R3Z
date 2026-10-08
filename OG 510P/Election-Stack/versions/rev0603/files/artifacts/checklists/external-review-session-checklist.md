# External review session checklist (surface-focused)

**Track:** Shared

This checklist turns “external review” into a **repeatable capability**: one surface, one bounded claim, one actionable output.

Size discipline: do not ship large appendices. Prefer **packet digests**, **minimal reproducers**, and **pinned citations**.

## Inputs

- Target surface (choose one): PublicNotice, publication compliance, witness governance, offline verifier, results release packaging, etc.
- Target version(s): archive `VERSION`, tool versions, and any deployed keyset IDs.
- Reviewers: names + affiliations + COI notes.

## Checklist

1) **Declare the scope boundary (one thing)**
   - Name the specific claim card / proof obligation / hazard being reviewed.
   - State what is *out of scope* for this session.

2) **Provide a bounded reproducer**
   - One example packet (or minimal test vector) with a manifest digest.
   - One verifier invocation (copy/paste) and expected PASS/FAIL condition.
   - If the surface is a public pointer (status page/feed), include a parity snapshot + request-context note.

3) **Run the review as an adversarial walkthrough**
   - “How could this be wrong while still looking correct?”
   - “What would a captured institution publish to create false confidence?”
   - “What evidence would a court/journalist need within 24 hours?”

4) **Capture a bounded critique**
   - Reviewer submits `artifacts/templates/external-challenge-report.md`.
   - If the issue is tool/spec correctness, include the smallest reproducer.

5) **Triage + record**
   - Classify as ARCH-* (spec/tool) or election hazard (HZ-*), as appropriate.
   - Add a row to `artifacts/registries/known-issues.csv` when there is any deployment-relevant break or risk.

6) **Respond with a repair note**
   - Use `artifacts/templates/spec-error-response-note.md` (or an ADR if policy semantics change).
   - State: what changed, what did not, and the claim boundary impact (`docs/166`/`docs/167`).

7) **Patch with drift-proofing**
   - Add at least one regression vector / gate check / example packet update that would have caught the issue.

8) **Close out**
   - Update `CHANGELOG.md` and (if relevant) `docs/207`.
   - Set the next review target surface (keep it single-surface).
