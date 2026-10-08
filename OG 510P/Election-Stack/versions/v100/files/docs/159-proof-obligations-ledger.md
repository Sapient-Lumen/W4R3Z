# 159. Proof obligations ledger (what must be provable)

**Track:** Shared


This file is the “what must be provable” counterpart to the hazard register.

It answers: **what claims would we stake legitimacy on, and what evidence must exist to support them?**

This ledger is meant to be expanded and then linked into:
- `../artifacts/claims/claim-evidence-matrix.csv`
- drills/checklists
- ADRs and freeze plan

## 159.1 Core proof obligations (Track A)

### PO-001 Inclusion and no-false-recording
It MUST be provable that:
- any displayed “RECORDED/ACCEPTED” status corresponded to a real log inclusion proof.

### PO-002 No undetected equivocation
It MUST be provable that:
- a dishonest log operator cannot show inconsistent histories to different audiences without fork evidence.

### PO-003 Election parameter immutability (EPB)
It MUST be provable that:
- ballot definitions and critical policies were committed and witnessed before voting.

### PO-004 Results publication integrity + audience parity
It MUST be provable that:
- published results objects are content-addressed and consistent across mirrors/audiences.

### PO-005 Dispute-ready evidence bundles
It MUST be provable that:
- evidence bundles are immutable, signed, and interpretable under a stated contract.

## 159.2 Verification ecosystem proof obligations (public inspections)

### PO-101 Anti-grinding challenge coverage
It MUST be provable that:
- monitors/watchers could not cherry-pick easy challenges; challenges follow a public schedule.

### PO-102 Suppression proof
It MUST be provable that:
- non-response/missed deadlines produce signed suppression artifacts.

### PO-103 Monitor accountability
It MUST be provable that:
- monitors’ behavior is itself auditable (watchers inspecting monitors).

## 159.3 North Star proof obligations (Track C)

### PO-201 Device state attestability
It MUST be provable that:
- devices were in an expected state when used (attestation evidence + reference values).

### PO-202 Provenance chain completeness
It MUST be provable that:
- firmware and device identity trace back through signed supply-chain statements.

### PO-203 Endorsement transparency
It MUST be provable that:
- reference values and endorsements were publicly published on time and are non-equivocating.

## 159.4 What to do next

For each proof obligation:
- assign an owner,
- define evidence artifacts + validation scripts,
- define a drill/test lane and a cadence,
- and record compatibility/freeze implications.