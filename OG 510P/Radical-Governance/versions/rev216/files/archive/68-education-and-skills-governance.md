# Education & Skills Governance (Learning + Credentialing as Auditable Infrastructure)

**Purpose:** make education systems accountable for access, quality, and exclusion decisions that shape life chances.

**Problem class:** education is a mass, long-horizon public interface with deep distributional effects. Failure modes often hide in *procedures* (exclusion by capacity or paperwork), *sorting* (segregation, tracking, selective admissions), *punitive discipline*, *credential opacity*, and *datafication* (profiling and automated gating).

**Design goal:** treat education as an **auditable pipeline** (entitlement → enrollment/placement → learning conditions → assessment → credentialing → transitions) so access, discretion, safety, and outcomes are measurable and contestable across scopes.

**This memo is intentionally minimal.** It composes existing MVGS interfaces: services (`SRV-*`), rules (`RULE-*`), standards (`STD-*`), decision receipts (`DRR-*`), reason codes (`RC-*`), remedy lanes (`AL-*`), releases (`REL-*`), programs/evaluations (`PROG/EVAL/CLM`), automation registers (`ADS-*`), data governance (`DPR`), integrity/oversight (`OFR-*`), assets (`AST-*`), contracts (`CON-*`), and grants/subsidies (`GRT/TEX`).

**Anchors:** rights-based education commitments and minimums ([BIB-UNESCO-ED2030-2015]); system-level learning failure and “learning crisis” framing ([BIB-WB-WDR2018]); assessment framework discipline (PISA as an exemplar of published frameworks, not a mandate) ([BIB-OECD-PISA-SCI-2025]); safeguarding standards ([BIB-UNICEF-SAFEGUARD-2025]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (persona + comprehension + no-wrong-door), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Data/identity safety for children: `33-...`, `12-...`, and `44-...` (minimize linkability; enforce correction rights).
- Automation governance (placement/discipline/triage): `06-...`, `42-...`.
- Publication integrity + records (no silent edits; durable standing): `53-...`, `31-...`.
- Safeguarding + retaliation discipline + follow-through: `83-...`, `32-...`, `55-...`, and pattern remediation `76-...`.

## Named tensions (design must surface these)
- Safeguarding/child protection vs privacy/over-surveillance (protect without building targeting infrastructure).
- Discipline/order vs inclusion/non-exclusion (avoid exclusion-by-discipline ratchets).
- Standardization/portability vs local pedagogy/pluralism (functional equivalence is allowed).
- Measurement/accountability vs gaming/teaching-to-metrics (treat metrics as fallible instruments).
- Transparency of placement/admissions vs stigma/safety (publish what enables contestation without doxxing).



### Adjacent-domain causal chain checks (education ↔ benefits ↔ labor)
Education exclusions are often *administrative spillovers* from benefits status, work classification, or migration enforcement. When auditing or designing education interfaces, explicitly check:
- household benefits/eligibility determinations (`64-...`) as gatekeepers for access (fees, transport, supports),
- work classification and employer retaliation (`69-...`) as drivers of attendance/placement instability,
- migration-status entanglement that suppresses complaint and access (`67-...`).


---

## A) Non-negotiable constraints (always-on)
1) **Non-discrimination and accessible enrollment:** enrollment and transfers MUST be treated as defined services (`SRV-*`) with clear evidence requirements, time bounds, and accessible channels. Missing capacity triggers published waitlist and placement rules (`RULE-*`) plus receipt + appeal (`DRR-*` + `AL-*`). (`47-...`, `31-...`, `36-...`)
2) **Receipts for exclusion and discipline:** expulsions/suspensions/denials of placement/accommodations MUST emit `DRR-*` (as‑of `RULE-*` + `RC-*` + lane `AL-*`) and be trackable in aggregate via `REL-*` releases. (`08-...`, `52-...`, `51-...`)
3) **Safeguarding is not optional:** safeguarding policies, reporting pathways, and response timelines MUST be explicit, trained, and auditable; recurring failures open `OFR-*` cases with duty-to-respond and verified closure. (`32-...`, `55-...`)
4) **Automation cannot become a hidden gate:** any algorithmic triage, risk scoring, or placement recommendation that materially affects access MUST be in `ADS-*`, explainable at the person level, and appealable; publish aggregate error/appeal/override signals as `REL-*`. (`42-...`, `06-...`)
5) **Data minimization and purpose limitation:** education data is power over children and families. Processing MUST be bounded by lawful basis, minimization, retention, correction, and portability rules (`DPR`), and cross-agency sharing requires explicit rule basis + auditability. (`33-...`, `12-...`)
6) **Credential integrity:** credentials that gate employment or further study MUST be verifiable (revocable where fraud is proven) and decisions to award/withhold MUST be receipted and appealable. (Use `DRR-*` + `AL-*`, and publish credential verification methods as `REL-*`.)

---
7) **Representation duty (children and non‑self‑advocates):** discipline/placement/exclusion decisions MUST support representative filings and SHOULD provide an independent advocate intake path for safeguarding‑relevant cases. For high‑stakes decisions, the notice/receipt MUST also name (and where feasible, CC) that advocate channel, not only the parent/guardian.


## B) Minimum Viable Education & Skills Governance Spine (MVESGS)

### B1) Public artifacts (what must be joinable)
- **Program inventory:** each major education program (compulsory schooling, special education supports, vocational training, financial aid) is a `PROG-*` with: purpose, eligibility, the authoritative rule IDs (`RULE-*`), funding sources, and key services (`SRV-*`). (`28-...`, `39-...`, `47-...`)
- **Curriculum + assessment standards:** publish curricular standards, assessment frameworks, and qualification requirements as pinned `STD-*` entries (or PRR instruments when binding law). Publish “as‑of” access and change logs via `REL-*`. (`27-...`, `39-...`, `51-...`, `53-...`)
- **Enrollment and placement journeys:** define `SRV-*` entries for: enrollment, transfer, special supports/accommodations, complaints, credential verification. Include required evidence, deadlines, and no-response behavior. (`47-...`)
- **Decision receipts:** admissions lotteries/denials, placements (including special education accommodations), disciplinary actions, and credential awards/withholding MUST emit `DRR-*` with portable `RC-EDU-*` reasons and a discoverable `AL-*` lane. (`31-...`, `52-...`, `36-...`)
- **Learning condition releases:** publish versioned `REL-*` releases of minimal system indicators (e.g., attendance, staffing ratios, facility condition grades joined to `AST-*`, safeguarding incident categories, and assessment participation) with methods + revision logs. (`51-...`, `48-...`)
- **Funding and procurement joinability:** publish budget allocations and execution for education functions, plus open contracting and grant/subsidy flows (school procurement, capital works, aid programs) in joinable registers (`CON-*`, `GRT/TEX`) and rollups (`REL-*`). (`07-...`, `38-...`, `49-...`)
- **Oversight closure:** recurring failure patterns (exclusion spikes, discipline disparities, safeguarding incidents, chronic understaffing) SHOULD open `OFR-*` cases with explicit remedial commitments and verified closure evidence. (`55-...`)

### B2) Decision typing (legitimacy routing)
- **Standards and curriculum changes:** treat as high-salience long-horizon decisions; log consultation/deliberation (`ENG-*`) with duty-to-respond; publish evidence packs as `REL-*`. (`41-...`, `51-...`)
- **Individual placement/discipline decisions:** administrative route, but always receipt + appeal + correction channel.
- **School closure/merger and major boundary changes:** require scope and equity analysis (`REL-*`), and record mandate/ownership changes as `DRR-TYPE: SCOPE` using the scope test docket. (`54-...`, `34-...`)

### B3) Boundary rules (multi-level)
Education often mixes scopes (local delivery, regional administration, national standards/funding). Use the scope assignment test (`54-...`) when:
- local discretion creates unequal citizenship (postcode access or quality),
- national rules impose unfunded administrative burdens,
- labor market mobility and credential portability require standardization,
- or safeguarding requires independent escalation routes.

Prefer **compacts** (`CMP-*`) for shared funding/standards and record assignments as `DRR-TYPE: SCOPE` with `RC-SCOPE-*`. (`19-...`, `18-...`, `35-...`)

---

## C) Typical failure modes to design against
- **Exclusion by capacity or paperwork:** silent waitlists and opaque residency proofs. Mitigation: `SRV-*` journey specs + queue metrics + receipted denials.
- **Sorting/segregation:** selective admissions and tracking without auditable criteria. Mitigation: publish admissions/placement rubrics (`RULE-*`), receipted decisions (`DRR-*`), and disparity monitoring releases (`REL-*`).
- **Punitive discipline ratchets:** suspensions/expulsions used as de facto exclusion. Mitigation: receipts + appeal; publish discipline rates by category; trigger oversight when thresholds persist.
- **Safeguarding failure:** under-reporting or retaliation. Mitigation: independent reporting routes, `OFR-*` follow-through, and audit-ready incident categorization (without doxxing).
- **Algorithmic gating:** risk scores become unreviewable gatekeepers. Mitigation: register systems (`ADS-*`), publish override and error signals, and guarantee human review for high-stakes classes.
- **Credential opacity/fraud:** unverifiable or arbitrary credential decisions. Mitigation: publish verification method as `REL-*`; receipt + appeal for award/withholding; audit patterns via `OFR-*`.

---

## D) Reason code starter set (`RC-EDU-*`)
Use these alongside `RC-PROC-*` (procedural), `RC-ELIG-*` (eligibility), and where coercion is present `RC-ENF-*`.

- `RC-EDU-001` **Enrollment denied (capacity / catchment rule)** — denial/waitlist under a published placement rule; MUST include next steps and appeal lane.
- `RC-EDU-002` **Enrollment denied (documentation / residency proof)** — denial due to missing evidence; MUST state acceptable alternatives and deadline.
- `RC-EDU-003` **Placement / track assignment** — placement into program/track under a published rubric; MUST cite criteria and review lane.
- `RC-EDU-004` **Accommodation/support decision** — support granted/denied/modified under a published framework; MUST include reassessment timeline.
- `RC-EDU-005` **Disciplinary action (suspension/expulsion)** — action taken under a published code; MUST include proportionality test and appeal lane.
- `RC-EDU-006` **Credential awarded/withheld** — credential decision under a published standard; MUST state unmet element(s) and remedy/retest path.


## E) Adjacent domain joins (follow causal chains)
- **Triad note (benefits ↔ education ↔ labor):** failures in one domain often show up as denials/exclusions in the others (benefits eligibility gates school supports; employment-status misclassification gates benefits; migration/labor enforcement can chill complaints). When auditing harms, follow causal chains across `64`, `68`, `69`, and (often) `67`.
- **Benefits ↔ education:** family benefits status and administrative burdens can drive enrollment/attendance; education aid programs share eligibility and identity gates (`64-...`, `44-...`).
- **Education ↔ labor:** credentials gate work; labor status and employer practices shape apprenticeships, internships, and school‑to‑work transitions (`69-...`).
- **Migration ↔ education/labor:** status rules can suppress complaints and create de facto exclusion even when rules promise access (`67-...`).
