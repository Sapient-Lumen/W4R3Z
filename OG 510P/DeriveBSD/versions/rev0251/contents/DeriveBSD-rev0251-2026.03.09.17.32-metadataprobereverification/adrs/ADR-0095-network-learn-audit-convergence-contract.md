# ADR-0095: Network learn/audit convergence contract

- Status: Accepted
- Date: 2026-03-08

## Context

`docs/328-learned-network-policies-from-flow-receipts.md` already argued for a learn→review→enforce loop,
and `docs/504-dns-receipt-detail-and-export-posture-by-profile.md` fixed the DNS-evidence privacy/export baseline.

The expensive ambiguity that remained was no longer whether DeriveBSD *should* learn network policy,
but **how that learning lane avoids becoming a permanent permissive bypass**.

If “audit mode” is just a vague runtime switch, teams will leave it on forever.
If the only review surface is a pile of raw `net-flow-receipt` objects, teams will fall back to packet captures,
handwritten allowlists, and folklore exceptions.

## Decision

1. Treat network learning as an explicit **bounded convergence lane**, not a standing runtime mode.
   Learn/audit runs must be tied to a named session with both:
   - a wall-clock bound, and
   - an event bound.

2. Introduce `net-flow-summary` as the canonical **derived evidence / review surface** for learn sessions.
   It summarizes the bounded receipt set into stable destination/class observations suitable for review,
   but it is **evidence-only** and never becomes authority by itself.

3. Keep authority boundaries crisp:
   - `net-egress-policy` remains the authoritative reviewed policy object,
   - `policy-suggestion` remains the reviewable proposed patch,
   - `net-flow-summary` remains evidence-only,
   - and raw `net-flow-receipt` / `net-dns-query-receipt` objects remain the lower-level source evidence.

4. Make the default review posture profile-shaped:
   - **A:** learn sessions are allowed for test/canary/incident lanes, but widening classes, hostname wildcards,
     CIDR broadening, or DNS-mediation relaxations require stronger review by default.
   - **B:** bounded learn sessions may be started from a trusted UI for app/service troubleshooting, but results still land as reviewable policy suggestions rather than silent ambient allow rules.
   - **C:** bounded learn sessions are normal for derived workloads, while adapter gaps remain explicit instead of being laundered through learned policy.
   - **D:** learn sessions are not a normal production posture; they exist only in approved maintenance / incident / lab lanes, and suggested broadening remains strongly reviewed.

5. Ban automatic promotion from learn evidence to enforced policy by default.
   The system may generate `policy-suggestion` artifacts, but enforcement still requires explicit review.

## Consequences

- Risk 53 shrinks from “what is learn/audit mode?” to implementation detail.
- The archive gets a stable summary artifact (`net-flow-summary`) instead of relying on packet captures or ad-hoc log scraping.
- DNS evidence privacy stays governed by the already-decided posture in `docs/504-dns-receipt-detail-and-export-posture-by-profile.md` rather than being reopened through learning ergonomics.
- A new guardrail can keep the session-bound + evidence-only + review-before-enforce contract from drifting.

## Why this is narrow enough

This ADR does **not** standardize:
- exact CLI affordances,
- exact aggregation heuristics for every destination type,
- exact approval/quorum counts,
- or exact diff formats for applying a suggested policy patch.

It only fixes the core convergence contract so future schemas and code have a coherent target.
