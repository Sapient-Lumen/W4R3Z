# Equal Protection, Accessibility, and Language Access Rails

**Problem:** rights on paper fail in practice when services are inaccessible, decisions hide discriminatory effects behind “neutral” procedures, or people can’t understand/participate due to language, disability, or literacy barriers.

**Goal:** make non-discrimination and accessibility **operational**: measurable, receipted, contestable, and enforceable across scopes.

**Design stance:** treat *access* as a **service interface** and *equal protection* as a **continuous control loop**, not a one-time legal statement.

(External baselines: UN CRPD accessibility duties; non-discrimination guarantees in constitutional / charter frameworks; open government participation and accountability norms; civil-rights constraints on federally funded programs in the U.S.). See References.

---

## A. Core invariants

1. **No wrong door for access barriers**
 - A person must be able to request accommodations / language help at **any** entry point (phone, counter, web, mail).
 - The request produces a receipt and a default interim support action.

2. **Accessibility is not optional infrastructure**
 - If a service is public, the accessibility layer is part of the service’s definition (not a separate “program”).

3. **Disparate harm is contestable even without proving intent**
 - Systems must publish enough aggregate and audit evidence to contest patterns.
 - Institutions must be able to *explain*, *mitigate*, and *repair* patterned harms.

4. **Reason codes must be legible and challengeable**
 - Denials must be explainable in plain language with evidence pointers (join to `DRR-*`).

5. **Participation is an access right**
 - If participation is offered (hearings, consultations, votes, forms), it must be accessible by design.

---

## B. Minimum artifacts (receipts + registers)

### 1) Accommodation & Access Support Receipt (`AAR-*`)
Issued when a person requests accessibility or participation support.

**Fields (minimum):**
- request channel + timestamp
- requested support type(s) (assistive tech, interpreter, captioning, mobility access, simplified format, quiet room, remote option, etc.)
- service/program identifier and deadline(s)
- **decision + rationale** (granted/partial/denied) with alternatives offered
- delivery plan + who is responsible
- escalation lane + response clocks

**Rule:** denial requires an explicit *burden/feasibility* explanation and a *less-restrictive alternative* attempt.

### 2) Language Access Offer Receipt (`LAR-*`)
Issued when language support is offered or requested.

**Fields:**
- preferred language (self-reported)
- interpretation/translation mode provided (in-person, phone, video, written)
- key documents translated (or a refusal-with-reasons)
- complaint/appeal lane

### 3) Accessibility Conformance Register (`ACR-*`)
Public register of service accessibility posture.

**Fields:**
- service card join key (`USC-*` or equivalent)
- supported channels + accessibility features
- known gaps + mitigation timeline
- last independent accessibility audit receipt (join to `APR/AFR-*`)

### 4) Equity Impact Receipt (`EIR-*`)
Issued for material changes (rules, budgets, queue criteria, enforcement policy, eligibility systems, major procurement).

**Fields:**
- affected populations (by mechanism, not identity labels alone)
- predicted risk pathways (e.g., documentation burdens, travel burden, disability barrier, language barrier)
- mitigations and fallback protections
- measurement plan + publish cadence
- contest lane

**Join:** `CCR-*` change receipts + `DUR-*` update receipts + `FTL-*` follow-through ledger.

### 5) Pattern Harm Ledger (`PHL-*`)
A public, privacy-safe ledger of confirmed or suspected systemic harms.

**Fields:**
- harm class + scope + start date
- evidence pointers (aggregate stats, audit findings, complaint clusters)
- remediation plan + deadlines
- closure criteria + independent verification

---

## C. Controls (what institutions must do)

### 1) Barrier budgets (access complexity budgets)
For each person-facing pathway, publish:
- maximum steps / time / cost / travel / documentation
- supported languages
- accessibility supports available
- *what happens if the budget is exceeded* (interim protection, deadline tolling, escalation)

(Join: `134-legibility-and-complexity-budgets.md`.)

### 2) Protected assistance channel
A staffed, non-digital channel for people who cannot navigate the system.
- produces receipts for calls/visits
- can file on behalf of the person with explicit delegation receipts

(Join: `98-persons-path-and-accessibility-invariants.md`, `141-delegation-and-representation-integrity.md`.)

### 3) Disparity monitoring without surveillance
Publish *privacy-safe* aggregates for high-impact decisions:
- denial/approval rates by relevant mechanism proxies (e.g., channel used, document types, disability accommodation requested, language used, geography)
- turnaround times and drop-off points
- appeal overturn rates

**Rule:** monitoring must not increase enforcement exposure for marginalized people. (Join: `127-data-governance-and-privacy-interfaces.md`.)

### 4) Counter-capture safeguards
Equity/access systems are themselves a capture target.
- independent audit lanes for access denials and accommodation refusals
- publish refusal patterns
- enforceable sanctions for retaliation or procedural sabotage

(Join: `187-public-integrity-system-blueprint.md`, `130-audit-and-inspection-integrity.md`.)

---

## D. Scope assignment (who owns what)

- **Micro-local / municipal:** front-door accessibility, local language access, staffed assistance, barrier budgets, complaint intake.
- **Regional / national:** standards, funding mandates, shared tooling, independent audit bodies, cross-jurisdiction continuity.
- **Supranational / global:** baseline conventions, mutual learning, portability compacts, and cross-border standards for accessibility in transnational systems.

(Join: `71-interface-obligations-by-scope.md`, `176-ideal-governance-by-scope-synthesis.md`.)

---

## E. Tests (add to Governance Test Suite)

- **T1.x — Accommodation trace:** For any person-facing service, can an affected person request support and receive an `AAR-*` within a bounded clock, with an escalation lane and no retaliation risk?
- **T1.x — Language access:** Can a person receive interpretation/translation and contest refusals via `LAR-*`?
- **T1.x — Pattern contestability:** Can the public observe privacy-safe disparity indicators, and does a confirmed pattern open a `PHL-*` remediation loop?

---

## References (external, cite-only)

- UN OHCHR, *Convention on the Rights of Persons with Disabilities (CRPD)* (instrument hub). https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-rights-persons-disabilities
- UN DESA (CRPD), *Article 9 — Accessibility*. https://social.desa.un.org/issues/disability/crpd/article-9-accessibility
- EU Fundamental Rights Agency, *EU Charter Article 21 — Non-discrimination*. https://fra.europa.eu/en/eu-charter/article/21-non-discrimination
- University of Minnesota Human Rights Library, *EU Charter Article 41 — Right to good administration* (consolidated text). https://hrlibrary.umn.edu/instree/europeanunion2.html
- U.S. DOJ Civil Rights Division, *Title VI of the Civil Rights Act of 1964 (overview)*. https://www.justice.gov/crt/fcs/TitleVI
- OECD, *Recommendation of the Council on Open Government (OECD-LEGAL-0438)* (overview page). https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0438
