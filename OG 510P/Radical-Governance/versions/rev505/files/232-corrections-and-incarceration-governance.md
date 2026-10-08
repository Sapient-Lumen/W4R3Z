# Corrections & incarceration governance (custody that stays accountable)

**Stack relation:** use `292-coercion-custody-and-public-safety-routing-guide.md` for the canonical route across the coercion / custody / public-safety cluster. This memo is the custody and corrections specialization; `05` is the canonical coercion and public-safety front door; `116` is the portable coercion protocol; `233` is the policing specialization; `193` is the non-carceral / restorative neighbor.

**Purpose:** treat prisons/jails/probation/parole as **high‑coercion public services** whose legitimacy depends on *continuous auditability*, *health & safety floors*, and *real remedy*—not on slogans, secrecy, or “administrative” labeling.

**Person served:** someone deprived of liberty (or under custody-like constraints) and their family—who needs **dignity, safety, healthcare, contact**, and a **workable complaint lane** even when retaliation risk is high.

**Design stance:** incarceration governance must be **more inspectable** than ordinary services, because the affected people cannot “exit.” Use the archive’s coercion primitives (`116`, `43`, `131`, `130`, `200`, `121`) and add **facility‑level rails** that prevent abuse-by-architecture.

---

## Core failure modes (what goes wrong)
- **Opacity capture:** what happens inside is unknowable; abuses surface only via scandals.
- **Rule drift:** segregation, discipline, healthcare denial, or “administrative” holds expand without public rule control.
- **Medical neglect:** custody becomes a health catastrophe; deaths are treated as paperwork.
- **Retaliation & silence:** people cannot safely complain or contact counsel/advocates.
- **Shadow custody:** pretrial, immigration, psychiatric, youth, or “secure care” sites evade prison rules.
- **Reentry failure:** release becomes a cliff (IDs, meds, housing) → recidivism as system output.

---

## Minimum primitives (portable across legal systems)

### COR‑1 Places of detention registry (no hidden sites)
- MUST maintain a **Places of Detention Register (PDRG-*)** covering *all* deprivation‑of‑liberty sites (police lockups, prisons, jails, youth facilities, immigration detention, forensic psychiatric, secure disability/aged care where liberty is restricted).
- MUST publish: operator, legal basis, capacity, population types, oversight body, inspection cadence, complaint channels, and last inspection date.
- MUST join to procurement/outsourcing (`110`, `219`) so privatization cannot erase accountability.

### COR‑2 Conditions baseline (dignity floor + measurable constraints)
- MUST treat the **Nelson Mandela Rules** as a dignity baseline: sanitation, food/water, healthcare equivalence, discipline limits, and protection from torture/ill‑treatment. ([BIB-MANDELA])
- SHOULD publish a **Facility Conditions Card (FCC-*)** per site:
 - occupancy, staff ratios, healthcare access times, out‑of‑cell hours, visitation/contact availability,
 - segregation counts + durations,
 - incidents (use‑of‑force, self‑harm, assaults) with method notes.

### COR‑3 Segregation / solitary confinement discipline (bounded + reviewable)
- MUST define **segregation reason codes** and time limits; all placements require a receipted decision + scheduled review.
- SHOULD treat prolonged solitary as a high‑risk exceptional measure requiring senior authorization, medical review, and independent oversight triggers. (Baseline discipline: [BIB-MANDELA])

### COR‑4 Healthcare & duty of care as auditable service
- MUST provide **healthcare equivalence**: access, continuity of meds, disability accommodations, and emergency response.
- MUST keep custody‑compatible **medical privacy** (purpose limits; no punitive use of clinical disclosure) consistent with `127`.
- SHOULD publish time‑to‑care metrics (median/p90) and adverse event reviews.

### COR‑5 Complaint & protected disclosure lanes that work under fear
- MUST provide at least **three** complaint routes:
 1) internal grievance (receipted, clocked)
 2) independent ombuds/inspector channel (confidential)
 3) counsel/advocate channel (uncensored legal mail/contact)
- MUST protect complainants from retaliation and publish retaliation substantiation + remedy stats (joins to `121`).

### COR‑6 Independent preventive inspection (anti‑torture architecture)
- SHOULD implement **regular independent visits** to all detention sites in line with the preventive model of OPCAT and National Preventive Mechanisms (NPMs). ([BIB-OPCAT]; [BIB-COE-CPT-STANDARDS])
- MUST require inspection reports to:
 - state scope/access limits,
 - list findings + recommendations,
 - open follow‑through tickets with deadlines (`130`, `226`, `227`).

### COR‑7 Deaths & serious harm in custody (no paper closure)
- MUST treat deaths in custody, life‑threatening injuries, and credible torture/sexual violence allegations as **automatic oversight events**:
 - immediate evidence preservation,
 - independent investigation,
 - family notification + access to information,
 - publishable findings with redactions justified.
- MUST prohibit “internal‑only” closure for these classes.

### COR‑8 Reentry as continuity duty (release is not a cliff)
- MUST treat release as a **service continuity event**:
 - identity documents, discharge meds, health handoff,
 - housing/contact plan,
 - probation conditions that are legible and realistically satisfiable.
- SHOULD use time budgets + complexity budgets (`108`, `134`) and publish failure rates.

---

## Facility‑level joinable artifacts (small set)
- `PDRG-*` — Places of Detention Register entry
- `FCC-*` — Facility Conditions Card (monthly/quarterly)
- `SEG-*` — segregation placement + review receipts (counts/durations published)
- `UOF-*` — use‑of‑force incident receipt (joins to `116`)
- `HCR-*` — healthcare access incident/denial receipt (privacy‑safe)
- `CGR-*` — custody grievance receipt (clocked)
- `INS-*` — inspection report + scope receipt
- `DIC-*` — death‑in‑custody investigation receipt + public summary
- `RER-*` — reentry readiness receipt (IDs/meds/housing/contact)

---

## Cross-links
- Coercion, detention, and use‑of‑force governance: `116-coercion-use-of-force-and-detention-governance.md`.
- Enforcement/custody event register: `43-enforcement-and-custody-event-register.md`.
- Audit/inspection integrity + follow‑through: `130-audit-and-inspection-integrity.md`, `55-oversight-findings-and-response-register.md`, `231-supreme-audit-institutions-and-public-accounts-rails.md`.
- FOI/ATI and protected disclosures: `200-freedom-of-information-and-access-to-official-documents-rails.md`, `121-whistleblowing-and-protected-disclosure.md`.

## Citations
- [BIB-MANDELA] (UN Standard Minimum Rules for the Treatment of Prisoners; adopted by UNGA res 70/175).
- [BIB-OPCAT] (Optional Protocol establishing independent preventive visits to places of detention).
- [BIB-COE-CPT-STANDARDS] (CPT standards/tools for detention monitoring; useful reference model).
