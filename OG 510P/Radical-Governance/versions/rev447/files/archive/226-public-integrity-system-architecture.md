# Public Integrity System Architecture (System–Culture–Accountability)

**Merge relation:** canonical architecture memo for the public-integrity cluster. `187-public-integrity-system-blueprint.md` remains a compact orientation memo; this file is the stronger current anchor for interfaces, institutions, and observability.


**Purpose:** define a *minimal, implementable* architecture for a public integrity system that is **hard to capture**, **easy to audit**, and **usable by ordinary people**.

**Why this memo exists:** many anti-corruption and “integrity” programs fail because they are treated as a policy list, not an *operational system*. This memo specifies the system as **interfaces + institutions + observability**, aligned to widely used integrity frameworks.

## Invariant
A jurisdiction’s integrity system must produce three things:
1) **Low-friction compliance** for honest actors.
2) **High-friction concealment** for corrupt actors.
3) **Fast, non-retaliatory correction** when integrity fails.

## Three-pillars model (design requirement)
Use a **System–Culture–Accountability** framing (not just “rules”).

- **System:** rules, registries, role boundaries, procurement/budget controls, and conflict controls.
- **Culture:** norms, incentives, and training that make integrity the default.
- **Accountability:** detection, enforcement, remedy, and visible consequences.

(See the OECD Recommendation on Public Integrity for this three‑pillar framing.) citeturn0search0

## Minimum viable integrity stack (MVIS)
The MVIS is the smallest stack that can be *truthfully said* to exist.

### A. Interfaces (public, machine-readable, receipt-first)
1. **Influence & lobbying interface**
   - Lobby register with meeting disclosures, client/issue tagging, and cooling-off rules.
   - “Influence receipts” for policy contacts: who, when, about what, outcome link.
   - A public “lobbying transparency + accountability” baseline is widely recommended in anti-corruption monitoring practice. citeturn0search2turn0search17

2. **Conflict of interest + asset disclosure interface**
   - COI statements as *structured declarations*.
   - Asset/interest disclosures with verification sampling + penalties.

3. **Procurement + spending interface**
   - Open contracting baseline: tender docs, awards, change orders, vendor performance.
   - “Spend receipts” linking: appropriation → contract → payment → delivery evidence.

4. **Appointments & revolving-door interface**
   - Appointment packets, reasoned selection notes, and post-employment restrictions.

5. **Complaint, protected disclosure, and remedy interface**
   - No-wrong-door intake; case ID; timeline clocks; anti-retaliation guarantees.

### B. Institutions (separation, independence, and cross-checks)
1. **Integrity coordination function** (design authority)
   - Sets standards and integration rules across agencies.

2. **Independent audit & inspection**
   - Access to records; publish follow‑through; ability to compel correction.

3. **Investigative integrity body**
   - Receives referrals and conducts investigations with clear jurisdiction.

4. **Prosecutorial/disciplinary function**
   - Must have independence safeguards and transparent case-handling rules.

5. **Courts/tribunals or adjudication lane**
   - Timely, accessible, reviewable decisions.

UNCAC’s prevention chapter emphasizes integrity, transparency, accountability, and participation as preventive measures, and includes anti‑corruption bodies as core tools. citeturn0search1turn0search16turn0search10

### C. Observability (how the public knows it’s working)
1. **Integrity dashboards**
   - Case volumes, average clocks, disposition types, recovery amounts.

2. **Integrity incident ledger**
   - Published incident summaries (redacted as needed) with causal factors + fixes.

3. **Audit trail coverage metric**
   - % of spend covered by open contracting; % of meetings disclosed; % of officials with current disclosures.

4. **Sampling + verification regime**
   - Random audits of disclosures, procurement change orders, and appointment packets.

## Anti-capture design rules
1. **Two-key control:** no single office controls intake + investigation + prosecution.
2. **Budget insulation:** multi‑year baseline; transparent cuts; public justification for staffing changes.
3. **Publication default:** publish registers, statistics, and follow‑through.
4. **Retaliation tripwires:** rapid protective orders + independent review.

## Scope assignment
- **Micro/municipal:** implement interfaces + local audit + complaint intake; regional/national bodies provide investigation/prosecution backstop.
- **National:** integrity standards, national registers, cross‑border asset recovery, and judicial independence supports.
- **Supranational/global:** mutual legal assistance, beneficial ownership interoperability, and cross‑jurisdiction procurement integrity compacts.

## Implementation sequence (tight)
1) Stand up **public registers + receipts** (influence, spend, COI).  
2) Add **complaint + protected disclosure** with clocks and anti-retaliation.  
3) Add **verification sampling + audit follow‑through ledger**.  
4) Harden **independence + separation** (intake/investigate/prosecute).  

## Tests (add to Governance Test Suite)
- **T‑Integrity‑01:** Every material policy decision has an influence disclosure path (meeting/position receipts).
- **T‑Integrity‑02:** Every public dollar has a joinable trace (appropriation→contract→payment→delivery).
- **T‑Integrity‑03:** Whistleblowing produces a receipt and anti-retaliation protections within a clock.
- **T‑Integrity‑04:** Audit findings have follow‑through with visible corrective actions.
