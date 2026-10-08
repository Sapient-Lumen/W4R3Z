# Grants, Subsidies & Tax Expenditures Register (Spend Without Contracts)

**Purpose:** make public financial favors legible and evaluable (who benefits, why, and with what outcomes) so capture and quiet subsidies become contestable.
**Person served:** a resident or applicant affected by grants, subsidies, or tax breaks who needs who benefits and why to be visible and contestable.

**From-below:** This makes subsidies and tax breaks traceable so hidden patronage and no‑strings spending can be audited and challenged.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-07` (Indifference) by making discretionary spend legible, joinable, and challengeable (see `98-persons-path-and-accessibility-invariants.md`).
**Join constraints:** identifiers/joins using this artifact MUST follow `70-interoperability.md` (empowered use‑path + corrective action), stay purpose‑limited/minimized, and have a narrow alternative when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `101-claude-rev142-normative-requirements.md` (NR-14).)
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)
**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations (receipting, time bounds, continuity of records) for applications/denials and disbursement status. (See `80-implementation-roadmap.md`, `82-service-standards-and-minimum-service-guarantees.md`, `31-records-foi-and-government-memory.md`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Notices & receipts:** eligibility denials, suspensions, recaptures, and material criteria shifts MUST emit `DRR-*` Decision Receipts with `31` minimum fields (as‑of basis + contestation windows + “if you do nothing…” semantics + what‑next lane). (`101` NR-02, NR-15)
**Proof burdens:** publish required evidence + least‑burdensome alternatives for each major gate (prefer reuse of state‑held facts); adverse outcomes cite `RC-*` + an `AL-*` lane. (`101` NR-06)
**Assistance & representation:** provide assisted/oral + representative channels for applicants/recipients (especially where fear/retaliation or disability/language barriers exist) and make the options measurable in `SRV-*`/`82`. (`101` NR-12, NR-17)


A large share of “government by decision” happens **outside procurement**: grants to NGOs, subsidies to firms, vouchers and rebates to households, and tax expenditures (credits, deductions, exemptions). These instruments can **govern outcomes** while bypassing the contracting interfaces and their controls.

This memo defines a minimal **GSTXR** interface: a joinable register that lets people answer:

- *Who authorized the support?* (`DRR-*` + `RULE-*`)
- *Who received it, for what purpose, on what terms?* (`GRT-*` / `TEX-*`)
- *What did it cost (including foregone revenue) and how did that estimate change?*
- *What evidence was claimed, and what happened after evaluation?* (`CLM-*` / `EVAL-*`)
- *How can it be contested (eligibility denial, discrimination, misuse, “silent” policy shifts)?* (`AL-*`)

**Anchors:** tax expenditure reporting guidance in [BIB-IMF-TE-2019] and evaluation guidance in [BIB-IMF-TE-EVAL-2022]; fiscal transparency baselines in [BIB-IMF-FTC-2019] and [BIB-PEFA-2016].

---

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- **Budget spine:** `07-fiscal-and-budgetary-governance.md` (why spend; who benefits).
- **Transfers/conditionality:** `35-transfer-register-and-conditionality.md` (TRF joins).
- **Records + remedy:** `31-...` (DRR), `08-...` + ALR `36-...` (eligibility/award disputes).
- **Releases:** `51-...` (REL-* disbursement + outcome reporting).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (beneficiary safety; doxxing risks).

## Named tensions (design must surface these)
- **Speed vs accountability:** urgent relief needs throughput without losing the audit spine.
- **Reporting burden vs equity:** compliance can exclude smaller/poorer recipients; scale burdens to risk.
- **Transparency vs beneficiary safety:** disclose enough to deter capture without exposing vulnerable people.
- **Discretion vs fairness:** flexible programs need typed reasons and contestable criteria.

## A. Coverage (what belongs here)
Include any **non-procurement** fiscal instrument that delivers a material benefit:

1) **Grants / contributions (`GRT-*`)**
Cash or in-kind support to non-public recipients (NGOs, firms, individuals), including operating and capital grants.

2) **Subsidies / incentives (`GRT-*` with `INSTRUMENT: SUBSIDY`)**
Rebates, vouchers, price supports, co-financing, and other incentive schemes that are not structured as contracts-for-delivery.

3) **Tax expenditures (`TEX-*`)**
Deductions, exemptions, credits, preferential rates, and deferrals treated as “spending through the tax code.”

**Exclusions / joins:**
- Procurement remains in the Contracting & Procurement Register (`CON-*` / OCDS) (`38-...`).
- Intergovernmental transfers remain in `TRF-*` (`35-...`).
- Loan guarantees / credit programs SHOULD be recorded here **and** referenced in the fiscal risk statement (`07-...`) when material.

---

## B. Register discipline (non-negotiables)
- **Stable IDs:** each instrument/award has a stable ID: `GRT-*` (grants/subsidies) or `TEX-*` (tax expenditures).
- **No silent policy shifts:** eligibility/criteria/rates/ceilings change → new version + effective date + change log (and for material changes, `AUTH-DRR`).
- **Costing is part of legitimacy:** publish the costing method and revisions (foregone revenue estimates for `TEX-*`).
- **Joins, not PDFs:** publish as data (`REL-*`) + a human view; link the authoritative `REL-*` releases.
- **Publication tiers:** protect personal data for individual recipients (publish aggregates by default), but preserve joinability for oversight (see `33-...`).
- **Person-facing access is part of the instrument:** if households, workers, or small firms must *apply* or can be *denied*, treat the application/appeal journey as a service (`SRV-*`): denials MUST emit `DRR-*` receipts (see `**Notices & receipts:**` above) with cited `RULE-*` basis, reasons, and remedy lane (`AL-*`), and SHOULD publish time promises (ack / first contact / decision) including tail waits (`47`, `82`, `98`).
- **Assistance + safe contestation:** where applicants face fear or retaliation (e.g., reporting employer fraud, discriminatory denial), support confidential filing and representation/advocacy channels; do not require “self-advocacy” to access lawful benefits (`08`, `36`, `98`).
---

## C. Minimum schema (publish as data + a human view)

**Version semantics (canonical):** treat this register as **append‑only** and queryable **as‑of** a date. Publish revisions with monotonic `REV`, `PUBLISHED-AT`, and (when behavior changes) `EFFECTIVE-*` timestamps—see `70-interoperability.md` §“Version semantics & ‘as‑of’ queries”.

| Field | Meaning |
|---|---|
| **ID (`GRT-*` / `TEX-*`)** | stable ID + version |
| **Instrument class** | grant / subsidy / voucher / rebate / tax expenditure |
| **Payer Unit ID** | authority responsible for the fiscal decision |
| **Implementing Unit / administrator** | who runs eligibility + disbursement |
| **Recipient category** | individual / NGO / firm / local unit / mixed |
| **Recipient identifier (tiered)** | `EID` bundle for orgs/firms + (for firms, optional BO statement reference); protected identifier for individuals |
| **Purpose + program link** | `PROG-*` (if part of a program) + tags (COFOG where fiscal-facing) |
| **Legal basis (`RULE-*`)** | statute / regulation / appropriations / tax code section |
| **`AUTH-DRR`** | the authorizing `DRR-*` for discretionary awards/denials, holds, major revisions, or terminations |
| **Eligibility rule** | thresholds, required documents, and data sources (and update cadence) |
| **Selection method** | formula / open call / competitive selection / discretionary (with criteria) |
| **Amount + timing** | authorized amount/cap, schedule, disbursed, variances; for `TEX-*`, foregone revenue estimate and range |
| **Conditions / reporting** | reporting duties; audit rights; misuse definitions; suspension/recapture ladder |
| **Evidence claim link (`CLM-*`)** | claimed mechanism/benefits; harms/guardrails; confidence level |
| **Evaluation commitments (`EVAL-*`)** | if high-spend or high-risk, register evaluation in `28-...` |
| **Remedy / contestation** | `AL-*` lanes for eligibility denials, discrimination, misuse findings, and policy changes |
| **Conflict & influence joins** | join to `INF/INT` records where decisions were lobbied or conflicted |
| **Sunset / review trigger** | mandatory periodic review; criteria for renewal/scale/stop |
| **Changelog** | what changed and why |

---

## D. Funding Legibility Clauses (FLC) (for grants/subsidies)
When the instrument funds non-public recipients, the award SHOULD include a small standard clause pack:

- **FLC-1 Records duty:** recipients maintain records keyed to `GRT-*` and deliverables for a minimum retention period.
- **FLC-2 Audit + access:** audit rights for the payer + independent audit bodies; no NDA terms that block oversight access.
- **FLC-3 Disclosure floor:** publish award, purpose, and totals; publish sub-awards where material.
- **FLC-4 Beneficial ownership (firms):** recipients disclose controlling interests where feasible; prefer joinable statements using BODS ([BIB-BODS]) and implement proportionate verification checks ([BIB-OPENOWNERSHIP-VERIFY-2020]) (align with [BIB-FATF-BO-2023]).
- **FLC-5 Remedy continuity (people-facing programs):** if the administrator fails, provide continuity backstops for `ESS-1` services (see `47-...`).
- **FLC-6 Self-report + correction:** use ACC-8 style self-report channels for mispayments/data errors (log via `DRR-*`).

---

## E. Notes on tax expenditures (`TEX-*`)
- Treat `TEX-*` as **spending:** publish an annual inventory with cost ranges, policy intent, and distributional notes where feasible.
- Prefer **sunsets + renewal receipts:** large or risky `TEX-*` provisions SHOULD have sunset dates and renewal `DRR-*` with evidence review.
- Evaluation is especially important because beneficiaries often have incentives to supply favorable evidence; require a published response to evaluations (see `28-...`).

---

## F. Minimal joins (what must connect)
Every payment/disbursement release SHOULD be joinable:

`GRT-*` / `TEX-*` ↔ `REL-*` (payments/cost estimates) ↔ `DRR-*` (authorizations/denials/revisions) ↔ `RULE-*` (legal basis) ↔ `AL-*` (contestability) ↔ `CLM-*` / `EVAL-*` (claimed outcomes and tests)

If the instrument is created or altered via compact (`CMP-*`) or transfer program (`TRF-*`), reference those IDs as well.
