# Open Contracting & Procurement Rails

**Purpose:** make procurement legible, contestable, and hard to capture—without making government unable to buy things.

**Threat model:** vendor lock-in, bribery/collusion, “requirements laundering”, opaque change orders, non-delivery, and post-award corruption.

(Connects to: `115-information-integrity-and-record-interfaces.md`, `07-fiscal-and-budgetary-governance.md`, `09-public-service-and-state-capacity.md`.)

---

## Procurement is a governance interface
Treat procurement as a **public record pipeline** with:
- a standardized data model,
- disclosure clocks (what becomes public when),
- and a grievance path for bidders, auditors, and the public.

The Open Contracting Data Standard (OCDS) provides a common model to publish data across contracting stages. citeturn0search2turn0search5

---

## Minimum disclosure bundle (per contract)
Publish (at minimum), with stable record pointers:
1) **Planning:** needs statement, budget, procurement plan
2) **Tender:** notice, criteria, clarifications
3) **Award:** award notice, evaluation summary, bidder list (as allowed by law)
4) **Contract:** signed contract + key terms
5) **Implementation:** amendments, payments, delivery milestones, completion

(OCDS supports disclosure across the full cycle.) citeturn0search2turn0search1

---

## Anti-capture procurement gates
### Gate A: Requirement integrity
- requirements must be traceable to public need
- forbid “brand-by-proxy” specs without explicit justification
- maintain a change-log with approvals

### Gate B: Competition health check
- minimum viable competition threshold (or justification for sole-source)
- publish conflict-of-interest attestations

### Gate C: Award explainability
- publish scoring rubric + decision rationale (within legal limits)
- record and publish exceptions (small, not narrative)

### Gate D: Post-award drift control
- change orders require:
  - change classification (scope/price/time)
  - approval level
  - public disclosure
- vendor performance record updates each milestone

---

## Vendor performance as a public signal
Maintain a **vendor performance ledger**:
- delivery timeliness
- defect rate / rework
- security incidents (if relevant)
- cost overrun delta
- dispute rate

This ledger feeds future evaluations and reduces repeat failure patterns.

(World Bank guidance emphasizes procurement monitoring/reporting and vendor management features for GovTech procurement.) citeturn0search11turn0search8

---

## “Right to contest” (procurement grievance loop)
Every procurement process must expose:
- how to challenge a tender spec
- how to appeal award decisions
- time limits
- independent review path
- publication of outcomes and remedies

(Connects to: `08-remedy-and-grievance.md`.)

---

## Implementation note: adopt standards, not platforms
OCDS is not an e-procurement platform; it is a publication and interoperability standard. citeturn0search5

---

## Integration hooks (add to tests)
- **Disclosure clock present:** every contract has stage-by-stage publication timing.
- **Change-order transparency:** amendments are published with classification.
- **Competition exception log:** sole-source decisions have public rationale.
- **Vendor performance ledger:** exists and is actually used in later awards.

---

## References (external)
- Open Contracting Partnership, OCDS documentation. citeturn0search2turn0search12
- World Bank, *GovTech Procurement Practice Note* (mentions OCDS + monitoring/reporting features). citeturn0search11turn0search8
