# Administrative Justice Mesh (Complaints + Ombuds + Tribunals + Courts)

**Purpose:** make “effective remedy” real by treating complaint-handling and administrative justice as **infrastructure**: discoverable, safe, time-bounded, learnable, and ultimately enforceable.

**Person served:** a person harmed by a public decision who needs a **no-wrong-door** path to contest it, obtain interim protection, and (if needed) reach binding review.

**From-below:** you can file safely, get a receipt, understand next steps, and force an outcome instead of being bounced until you give up.

**See also:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`, `66-justice-and-administrative-justice-governance.md`, `31-records-foi-and-government-memory.md`.

**Anchor set:** UNGP effectiveness criteria for non‑judicial mechanisms (legitimate, accessible, predictable, equitable, transparent, rights‑compatible, learning, and engagement) [BIB-UNGP-BHR-2011] + operational guidance [BIB-OHCHR-ARP-EFFECTIVE-2022].

---

## 1) Design claim
Most systems fail not because courts don’t exist, but because **the path to binding review is non‑navigable** (fear, complexity, silence, and “wrong door” attrition). Fix: a **mesh** that explicitly composes:

1) **Front-door complaint handling** (fast, assisted, multi‑channel, receipted)
2) **Independent, informal ombuds** (safe escalation + pattern detection + recommendations)
3) **Administrative tribunals** (specialized, accessible, binding review)
4) **Courts** (rights enforcement + last resort)

The mesh is *not* one portal. It is a **protocol**: shared receipt semantics, routing rules, and escalation guarantees.

---

## 2) The minimum viable mesh (MVM)

### A) No-wrong-door intake (the “router”)
- Any public-facing intake MUST either accept the grievance **or route it** without losing deadlines (single tracking number).
- Intake MUST support **assisted and oral** filing (translation/interpretation), and a **non‑smartphone** path (`98`).
- Intake MUST publish time-bounds and **no-response rules** (auto-escalation / interim protection for essentials/rights).

### B) Common receipt semantics (joinable without becoming a surveillance join)
Define a **Complaint Receipt** (`CRR-*`) that can be issued by any lane.

Minimum fields (link to `31` Decision Receipt fields; don’t invent parallel bureaucracies):
- `CRR-*` stable ID; submission channel; timestamp; scope (agency/program/region)
- claimed harm class + urgency flag (e.g., detention/eviction/benefits cutoff)
- the challenged `DRR-*` (or `AL-LEG` legibility failure if missing)
- disclosed next step(s): `AL-*` lane(s) + deadlines + authority (binding vs advisory)
- contact safety preference (confidential/representative) + retaliation-risk marker

**Rule:** if the state acts against you, the relevant receipt(s) MUST exist unless a narrow logged exception applies.

### C) Ombuds as a *safety lane* and a *pattern sensor*
An ombuds lane is valuable when it is **independent, impartial/neutral, confidential, and informal**—and when it can report patterns without exposing complainants. The professional model emphasizes these core principles and access-to-information within the organization. See IOA standards/ethics for the “organizational ombuds” model [BIB-IOA-STANDARDS-2009].

Required properties (adapt by scope):
- **Independence:** protected budget line + appointment safeguards (`113`) and access to necessary information.
- **Confidentiality by default:** publish narrow exceptions (e.g., serious harm risk) and safe-handling rules (don’t “turn it into a report”).
- **Own-initiative / systemic inquiry power** where feasible, so patterned harms can be investigated without waiting for a perfect complainant.
- **Public reporting:** regular redacted reports with “what changed” tracking.

### D) Administrative tribunals as the binding workhorse
The mesh should treat tribunals as the **fast binding lane** for many everyday harms (benefits, housing, licensing, immigration administrative steps), with simplified procedure for non-lawyers.

### E) Courts as the rights backstop
Courts remain essential when the problem is unlawful policy, constitutional conflict, systemic discrimination, or noncompliance with tribunal orders.

---

## 3) Standards you can borrow without importing the whole bureaucracy

### Complaint-handling systems (front door)
ISO 10002 provides guidelines for designing and operating complaint handling as a managed process (planning, operation, maintenance, improvement) [BIB-ISO-10002-2018]. Use it as a **process template**, not as a reason to create a new silo.

### Effectiveness criteria (non-judicial mechanisms)
Use UNGP criteria as the mesh’s acceptance tests: legitimacy, accessibility, predictability, equitability, transparency, rights-compatibility, continuous learning, and engagement/dialogue [BIB-UNGP-BHR-2011] [BIB-OHCHR-ARP-EFFECTIVE-2022].

### Administrative justice as the “interface” with the state
OECD frames administrative justice as the everyday interface between people and institutions, including ombuds, tribunals, and complaint systems—central to trust and fairness in daily state encounters [BIB-OECD-ADMINJUSTICE-2025].

---

## 4) Threat model (why the mesh fails in practice)

- **Silence as denial:** agencies “run out the clock” → solve with time bounds + no-response rules + interim protection.
- **Wrong-door churn:** people are routed across units until deadlines lapse → solve with no-wrong-door routing duty.
- **Retaliation chilling:** people avoid filing → solve with confidentiality/representation lanes + retaliation monitoring (`03`, `83`).
- **Ombuds capture:** ombuds becomes PR → solve with independence + public reporting + “what changed” receipts.
- **Complaint inflation / proceduralism:** more process, less remedy → solve with outcome tracking and a binding escalation guarantee.

---

## 5) Implementation pattern: “mesh by compacts” (polycentric-friendly)
In overlapping jurisdictions, the mesh can be implemented via **service compacts**:
- shared `CRR/DRR/AL-*` receipt semantics
- mutual routing obligations (no wrong door)
- shared escalation triggers (e.g., essentials/rights harm)
- cross-scope dispute resolution (`114`)

This keeps autonomy while making remedies portable and legible.

---

## 6) Small but crucial: publish a complaints guide
Publish a single “how to complain” guide per major service (like the European Ombudsman’s public-facing approach for complaints) [BIB-EU-OMBUDS-GUIDE-COMPLAINTS]. The guide MUST be usable offline and in multiple languages/channels (`98`).

---

## Acceptance tests (copy/paste)
A jurisdiction can claim it has an “effective remedy” only if:
- a low‑literacy person offline can file and get a receipt within one visit/call
- the receipt names binding vs advisory lanes + deadlines
- no-response triggers escalation/interim protection for essentials/rights
- ombuds independence/confidentiality is real and auditable
- patterned harms produce public learning and system change

