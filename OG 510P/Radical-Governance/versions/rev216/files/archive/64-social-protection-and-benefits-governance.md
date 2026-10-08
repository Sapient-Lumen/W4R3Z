# Social Protection & Benefits Governance (Auditable Eligibility + Delivery)

**Purpose:** ensure benefits systems are navigable, time-bounded, and correctable so poverty isn’t administered as punishment.

**Problem class:** social protection is a high-volume, high-stakes interface with the state. Failure modes are often *procedural* (exclusion by burden), *informational* (opaque eligibility), or *technical* (payments and identity gates), with large human welfare impact.

**Design goal:** treat benefits as an **auditable pipeline** (program → eligibility rules → intake → determination → payment → recertification → remedy) so access, errors, and discretion are measurable and contestable across scopes.

**This memo is intentionally minimal.** It composes existing interfaces: service journeys (`SRV-*`), identity/eligibility systems (`IDN-*`), rules (`RULE-*`), decision receipts (`DRR-*`), reason codes (`RC-*`), remedy lanes (`AL-*`), releases (`REL-*`), programs/evaluations (`PROG/EVAL/CLM`), and integrity/oversight (`OFR-*`).

**Adjacency triad note (audit causal chains):** when diagnosing exclusion/denial or suppressed complaints, check adjacent domains that often create the *real* cause: employment status/misclassification (`69-...`), education access gates (`68-...`), and (where relevant) migration enforcement interactions (`67-...`). Treat cross‑domain chains as first‑order, not edge cases.


**Anchors:** social protection floors and rights-based minimums ([BIB-ILO-SPF-R202-2024]); social registries as delivery infrastructure ([BIB-WB-SOCIALREG-2017]); digital delivery systems and G2P architecture ([BIB-WB-DIGDELIVERY-2025], [BIB-WB-G2PX], [BIB-WB-NEXTGEN-G2P]); administrative burden as a governance failure mode ([BIB-RSF-ADMINBURDEN-2018]).

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (persona test; non-digital/non-reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + power reality: `99-protective-legibility-and-adoption-dynamics.md` plus [TM-29] (fear/retaliation) and [TM-33] (enforcement doesn’t bite).
- Identity/data/automation boundaries: `12-...`, `33-...`, `44-...`, `42-...`, and `06-...`.
- Publication integrity + “as-of” access: `53-...`, `51-...`, and records continuity `31-...`.
- Pattern remediation + follow-through: `76-...`, `32-...`, `55-...`.

## Named tensions (design must surface these)
- Anti-fraud/verification vs inclusion/dignity (don’t turn “integrity” into blanket exclusion).
- Automation/efficiency vs contestability (avoid hidden gates; preserve human paths).
- Auditability/transfers vs privacy/targeting risk (regime-change safety is not hypothetical).
- Uniform floors vs local discretion/capacity (avoid postcode eligibility while respecting delivery reality).
- Conditionality/sanctions vs welfare stability (don’t create churn as policy-by-attrition).



### Adjacent-domain causal chain checks (benefits ↔ labor ↔ education)
Benefits outcomes are often *caused upstream* by labor status, school access, or migration enforcement. When auditing or designing benefits interfaces, explicitly check:
- employment classification and wage/hrs records (`69-...`) as causes of eligibility errors/denials,
- school enrollment/placement exclusions that hinge on household status (`68-...`),
- chilling effects when labor complaints trigger migration enforcement (`67-...`).


---

## A) Non-negotiable constraints (always-on)
1) **No “procedural denial by burden”:** the application/recertification journey MUST be defined as a service (`SRV-*`) with accessible channels, time bounds, and published queue metrics (see `47-...`).
2) **Rule traceability:** eligibility and benefit-calculation criteria MUST be in the PRR (`RULE-*`) and queryable “as-of” (no hidden scoring rubrics). (`39-...`, `70-...`)
3) **Receipts for determinations:** grants/denials/suspensions/recoupments MUST emit `DRR-*` (reasons + cited `RULE-*` + relevant `REL-*` + `AL-*` lanes). (`31-...`, `08-...`)
4) **Payment integrity without doxxing:** publish program-level disbursement and reconciliation as versioned `REL-*` releases with method notes and privacy protection; person-facing joinability happens via the individual’s receipt and possession-based verification. (`51-...`, `53-...`, `31-...`)
5) **Remedy is real (timelines + interim protection):** benefits are often essential; appeal lanes MUST be discoverable and SHOULD include interim-protection rules where interruption creates high harm risk. (`36-...`, `08-...`)
6) **Representation duty:** where the affected party cannot effectively contest (children, people under guardianship, severe disability), adverse determinations MUST support representative filings and SHOULD route through an independent advocate/ombuds intake path. For high‑stakes child determinations, the notice/receipt MUST also name (and where feasible, CC) an independent advocate channel, and must not rely solely on the parent/guardian when conflict risk is plausible.

7) **Purpose limitation (anti-function creep):** identity and registry data use MUST be bounded by a lawful basis, minimization, retention, and correction rights; cross-agency sharing requires an explicit rule basis and auditability (DPR + ADS joins where relevant). If using tax/revenue records for income or identity verification, treat it as high-risk sharing and follow `93-...` + `33-...` discipline. (`33-...`, `44-...`, `42-...`)

---

## B) Minimum Viable Social Protection Governance Spine (MVSPGS)

### B1) Public artifacts (what must be joinable)
- **Program inventory:** each benefit program is a `PROG-*` with: purpose, target group, funding source, payment cadence, and the authoritative eligibility rule IDs (`RULE-*`). (`28-...`, `39-...`)
- **Service journey(s):** each program has an `SRV-*` entry for intake + recertification with channel options, required evidence, deadlines, and “no-response” behavior. (`47-...`)
- **Eligibility systems register:** all major eligibility/registry systems (including social registries) are listed in `IDN-*` with purpose, assurance tier(s), inclusion risks, correction pathways, and cross-agency sharing boundaries. (`44-...`, `33-...`)
- **Determination receipts:** each decision emits `DRR-*` (grant/deny/suspend/adjust/recoup) with portable `RC-*` reasons and a discoverable `AL-*` lane. (`31-...`, `52-...`, `36-...`)
- **Payments + reconciliation releases:** periodic `REL-*` releases publish *program-level* totals, delivery channel mix, timeliness, exception rates, and reconciliation status (methods + revision logs). Link to procurement/financial service provider contracts where relevant (`CON-*`). (`51-...`, `38-...`)
- **Learning loop:** program changes, fraud-control expansions, or major automation MUST link to a `CLM-*` and (where feasible) an `EVAL-*` commitment (so “tighten eligibility” is not a permanent ratchet without evidence). (`37-...`, `28-...`)
- **Oversight closure:** recurring failure patterns (wrongful suspensions, extreme backlog, disparate impact) SHOULD open `OFR-*` cases with duty-to-respond and closure verification. (`55-...`, `32-...`)

### B2) Decision typing (legitimacy routing)
- **Eligibility rule changes** (means-test thresholds, conditionality, sanctions, new exclusions): treat as major rights/redistribution policy; require public consultation logged as `ENG-*` with a duty-to-respond, and publish fiscal notes and distributional methods as `REL-*`. (`41-...`, `51-...`)
- **Individual determinations**: administrative route, but always receipt + appeal + correction channel.
- **Automation introductions** (risk scoring, eligibility triage): must be registered (`ADS-*`), appealable, and auditable; publish model purpose/version and contestation notes. (`42-...`)

### B3) Boundary rules (multi-level delivery)
Social protection often mixes scopes (local intake, regional casework, national financing/standards). Use the scope test (`54-...`) when:
- local discretion creates unequal citizenship or “postcode eligibility,”
- national rules impose unfunded admin burdens on local delivery,
- or spillovers (migration, homelessness, labor market shocks) force coordination.

Prefer **compacts** (`CMP-*`) for shared funding/standards and record the assignment as `DRR-TYPE: SCOPE` with `RC-SCOPE-*`. (`19-...`, `35-...`, `18-...`)

---

## C) Typical failure modes to design against
- **Administrative burden as exclusion:** endless documentation, re-verification, and opaque deadlines. Mitigation: publish burden metrics (drop-off rates, processing times) by `SRV-*` and trigger oversight when thresholds are exceeded.
- **Identity gating:** ID requirements or correction backlogs deny eligible people. Mitigation: define assurance tiers, publish correction timelines, and provide alternative verification paths; log disputes as `AL-*`.
- **Payments that fail “quietly”:** delays, partial payments, reconciliation gaps. Mitigation: publish timeliness + exception rates as `REL-*` and open `OFR-*` cases when failure persists.
- **Fraud panic ratchet:** “anti-fraud” expansions become permanent surveillance or blanket exclusions. Mitigation: require `CLM-*` + evaluation windows, purpose limitation, and due-process receipts for adverse actions.
- **Automation-induced denial:** triage models become de facto gatekeepers. Mitigation: register systems, publish error/appeal stats, and require a human-review path for high-stakes classes.

---

## D) Reason code starter set (`RC-SP-*`)
Use these *in addition to* `RC-ELIG-*`, `RC-PROC-*`, and (where sanctions apply) `RC-ENF-*`.

- `RC-SP-001` **Benefit granted (criteria met)** — eligibility and amount verified under as‑of `RULE-*` (cite method/inputs).
- `RC-SP-002` **Benefit suspended/terminated (recertification failure)** — required recertification or contact step missed; MUST include reactivation path and appeal lane.
- `RC-SP-003` **Benefit adjusted (reported change)** — amount changed due to a documented change in circumstances under a published rule; include effective date and backpay/recoup method.
- `RC-SP-004` **Overpayment recovery / clawback** — recovery initiated under a published method; MUST include dispute/waiver path where the law allows.

---

## E) Where this plugs in
- Municipal delivery and access equity: `20-municipal.md`
- National redistribution + standards: `40-national.md`
- Labor/work status and enforcement joins (classification can gate benefits): `69-labor-and-work-governance.md`
- **Triad note (benefits ↔ education ↔ labor):** benefits status can shape enrollment/attendance and school support access; labor status misclassification can deny both protections and eligibility. When auditing harms, follow causal chains across `64`, `68`, and `69`.
- Migration enforcement interactions (chilling effect on claims; eligibility boundary moves): `67-migration-and-mobility-governance.md`
- Identity/eligibility systems: `44-identity-credential-and-eligibility-systems-register.md`
- Service journeys and administrative burden: `47-service-catalog-and-access-journeys-register.md`
- Grants/subsidies/tax expenditures joins: `49-grants-subsidies-and-tax-expenditures-register.md`
- Data protection + ADS governance: `33-...`, `42-...`
- Remedy/appeals discipline: `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`
