# 59 — Dispute Resolution & Adjudication Playbook

**Track:** A (Deployable core)


## Why this exists (paranoid assumption)
Even if everything works, **someone will claim fraud**. The system must produce:
- clear evidence types
- a deterministic process for evaluating claims
- a recovery path anchored in software independence (paper + RLAs)

## Evidence hierarchy (recommended)
1. **Paper ballot of record** (or voter-verifiable paper record) + custody evidence
2. **Risk-limiting audit evidence** (sampling method + hand interpretation)
3. **Public cryptographic evidence** (log checkpoints, proofs, notarization)
4. **Operator logs and telemetry** (lowest trust)

## Claim types and required evidence
### A) “My ballot was not recorded”
Required:
- IntakeReceipt (PENDING) or SCT-like promise
- missed-deadline proof (receipt + checkpoint history)
Outcome:
- either inclusion is demonstrated, or censorship evidence is published and escalation triggers.

### B) “Log equivocated / split views”
Required:
- ForkProof (conflicting STH/checkpoint signatures)
Outcome:
- invalidate affected period; revert to paper-of-record adjudication; legal incident path.

### C) “Wrong parameters / ballot style shown”
Required:
- EPB hash observed by voter + any included proofs
- comparison to public EPB archive
Outcome:
- if mismatch, treat as substitution/client compromise; run targeted investigation; consider nullification of affected ballots per law.

### D) “Tallies don’t match evidence”
Required:
- evidence bundle hash
- verifier reports
- RLA discrepancy report
Outcome:
- escalate to full recount / expanded audit.

## Process (operational)
1. **Freeze**: publish last known good checkpoint and notarize it.
2. **Triage**: classify claim, request evidence types.
3. **Reproduce**: independent verifiers re-run checks.
4. **Decide**: per pre-committed DisputePolicy in EPB.
5. **Recover**: paper + audit determine final if conflict persists.
6. **Publish**: final public report with hashes + notarization records.

## Template
See `artifacts/templates/dispute-filing.md` and `artifacts/templates/public-audit-report.md`.