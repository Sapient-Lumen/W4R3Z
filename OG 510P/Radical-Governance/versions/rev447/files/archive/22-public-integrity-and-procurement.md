# Public Integrity & Procurement (Anti-Capture Infrastructure)

**Purpose:** reduce corruption and capture by making procurement/integrity controls auditable and consequence‑bearing.
**Person served:** a public served (or harmed) by public spending who needs procurement and integrity rules that prevent insider capture and make abuse contestable.

**From-below:** This makes corruption and capture harder by requiring traceable procurement and conflict controls you can inspect and contest.
**EXP pointer:** counters `EXP-07` (Indifference) by making integrity failures contestable and closable (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** integrity controls must have a binding lever (pause/nullify/debar/claw back/discipline) and a duty-to-respond loop that can be invoked from below (`32`, `55`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect bidders/insiders and affected people using protected disclosures + safe complaint lanes (`83`, `36`, `77`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)

**Proof burdens:** publish required evidence + least-burdensome alternatives; disclose “once-only” retrieval of state-held facts; ensure adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)

Many governance failures are not “policy mistakes” but **integrity failures**: public power is quietly re-routed through influence, contracts, and opaque exceptions. This memo defines a small, portable integrity stack that works from micro-local to global.

It applies to **procurement, grants/subsidies, transfers, and tax expenditures** — any channel where benefits can be routed (see also `49-...` for non-procurement spending).

Capital projects are a special integrity risk class (scope changes, change orders, optimism bias). When capex is material, bind integrity controls to stage-gated project discipline (`97-public-investment-and-capital-project-governance.md`).

## Kernel anchors (do not repeat)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- **Receipts + remedy for integrity power:** debarment, bid protests, grant denials, and retaliation findings MUST emit `DRR-*` with `AL-*` lanes discoverable in the receipt. (`31-...`, `08-...`, `36-...`)
- **Protective legibility:** publish joinable contracting/influence data without creating a targeting surface; default to aggregate + scoped disclosure when retaliation risk is real. (`99-protective-legibility-and-adoption-dynamics.md`, `77-...`, `83-...`)
- **Power, not paperwork:** integrity controls must have at least one binding lever (pause/nullify, debar, claw back, discipline) or they are theater. (`32-...`, `55-...`) (See `101-claude-rev142-normative-requirements.md` (NR-02).)

## Named tensions (design must surface these)
- **Transparency vs retaliation/defamation**
- **Competition vs speed/continuity under crisis** (emergency procurement is a capture magnet)
- **Disclosure vs security/privacy** (beneficial ownership, vendor identities)

**Anchor set (start here):**
- OECD Recommendation on Public Integrity (OECD/LEGAL/0435): see [BIB-OECD-PI].
- Illicit finance / beneficial ownership joins that prevent “silent vendor swap”: `155-illicit-finance-and-kleptocracy-defense.md`.
- OECD Recommendation on Public Procurement (OECD/LEGAL/0411): see [BIB-OECD-PROC].
- OECD lobbying recommendation (influence transparency baseline): see [BIB-OECD-LOB].
- UN Convention Against Corruption (UNCAC) (procurement + prevention baselines): see [BIB-UNCAC].
- Open Contracting Data Standard (OCDS) (contracting disclosure schema): see [BIB-OCDS].
- World Bank Procurement Regulations for IPF Borrowers (integrity + value-for-money framing; 7th ed. Sep 2025): see [BIB-WB-PROC-REG-2025].
- FATF Guidance on Beneficial Ownership of Legal Persons (R.24 guidance, 2023): see [BIB-FATF-BO-2023].

---

## A. Minimum viable public integrity system (MVPIS)
This is the smallest integrity stack that makes “anti-capture” operational.

1) **Conflict-of-interest (COI) + gifts + outside income**
- MUST: COI rules for elected, appointed, and high-risk staff roles; disclosed recusal logic.
- MUST: gifts/hospitality rules with a simple public disclosure threshold.
- SHOULD: outside income limits for high-risk roles.

2) **Influence transparency (lobbying + revolving door)**
- SHOULD: lobbying register (who, for whom, about what, when) and a meeting log for senior officials.
- SHOULD: cooling-off rules for regulated sectors and high-value procurement roles.
- SHOULD: treat revolving-door determinations and waivers as joinable `DRR-TYPE: INTEGRITY` receipts linked to `INT-*` (see `79-conflict-of-interest-and-revolving-door-discipline.md` and `46-influence-and-interests-register.md`).
- See toolkit: `ACC-5` and `OPEN-10` (regulatory footprint).

3) **Asset declarations (risk-based)**
- MUST: asset/interest declarations for senior decision-makers and procurement/high-risk positions.
- MUST: a compliance process (not just a form): late/missing declarations trigger escalation.

4) **Whistleblowing + retaliation controls**
- MUST: protected disclosure lane(s) with at least one independent channel; published triage/timeline rules; confidentiality handled via receipts (see `83-...`, `77-...`).
- MUST: retaliation monitoring with enforceable remedies; retaliation determinations emit `DRR-TYPE: INTEGRITY-RETALIATION` and are reportable as periodic stats (`REL-*`).

5) **Internal controls + audit trail**
- MUST: minimum internal controls for payments, procurement, and grants (segregation of duties, documentation rules).
- MUST: records management and decision logs (pairs with `IOP-4/5`).

6) **Independent oversight + enforcement**
- MUST: supreme audit / external audit capacity (`ACC-1`) with publication.
- SHOULD: inspector general / anti-corruption function (`ACC-2`) with protected leadership removal rules.
- SHOULD: a credible sanctions ladder (admin discipline → debarment → referral → prosecution).

7) **Public transparency baseline**
- MUST: publish budgets, audits, and major contracts (`OPEN-1/2`) in a **usable** form (machine-readable + human summary, not PDF dumps).
- SHOULD: publish enforcement stats and closure rates.

**Design rule:** keep the system *risk-based* and *legible*. If you can’t enforce it, simplify it.

---

## B. Minimum viable procurement integrity (MVPI)
Procurement is where integrity meets large money flows.

1) **Default competition; exceptions are typed and logged**
- MUST: competitive tender as default; the exception list is finite.
- MUST: every non-competitive award has a public “exception record” (reason code + approvals + time limit).

2) **Open contracting with stable IDs**
- SHOULD: publish the contracting process with stable IDs (planning → tender → award → contract → implementation) using OCDS where feasible.
- MUST: publication is **machine-readable** (OCDS feed/CSV/JSON) with stable IDs; PDF-only publication is legibility theater. (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
- MUST: publish the award, contract, amendments, and implementation milestones for high-value / high-risk contracts.

3) **Beneficial ownership (where feasible)**
- SHOULD: require bidders to disclose beneficial owners for high-value contracts, and publish or share with competent authorities depending on law; use an open schema for exchange where feasible (see [BIB-BODS]).
- SHOULD: require stable counterparty identifiers (`EID` bundles) on awards, grants, and influence records so ownership/conflict joins are feasible; where beneficial ownership is required, publish joinable statements (often as a `REL-*` release) and publish verification status (see [BIB-OPENOWNERSHIP-VERIFY-2020], [BIB-GLEIF-ISO17442]).
- MUST: prohibit awards when ownership/related-party conflicts cannot be resolved.

4) **Debarment + performance history**
- MUST: debarment policy and an appeal path.
- SHOULD: vendor performance history and close-out discipline (deliverables verified before final payment).

5) **Bid rigging and collusion (procurement as cartel surface)**
- SHOULD: adopt a bid‑rigging prevention/detection protocol (screening triggers, safe reporting channel, rapid evidence preservation, and referral path).
- SHOULD: treat confirmed bid‑rigging patterns as integrity incidents that trigger independent follow‑through (`OFR-*`) and (where a competition authority exists) a coordinated response; see `94-competition-and-market-power-governance.md`.
- Anchor: OECD bid‑rigging guidance update [BIB-OECD-BIDRIGGING-2025].

6) **Integrity controls for emergencies**
- MUST: emergency procurement still requires: (a) a written justification, (b) time-bound scope, (c) post-award publication, (d) after-action audit.
- MUST: cap “emergency contracting” duration before re-tender.

7) **Vendor lock-in and sovereignty**
- MUST: exit clauses and data portability for high-stakes systems (pairs with `06-digital-and-algorithmic-governance.md`).
- SHOULD: for contracts that materially govern access/eligibility/enforcement, require **contractual legibility** (CLC pack: receipts/records, rule traceability, oversight access) so accountability cannot be outsourced (`38-...`).
- SHOULD: split contracts to reduce single-supplier dependency when feasible.

8) **Concessions / PPPs (long-horizon capture risk)**
- MUST: treat concessions/PPPs as procurement + regulation: publish award criteria, key risk allocations, and renegotiations/amendments (no “silent contract law”).
- MUST: publish performance obligations and an implementation log; major renegotiations trigger an independent review and (where feasible) competitive retest.
- SHOULD: link concession objects to `CON` IDs (and OCID where used) and to tariff/fee Rule IDs where relevant (`13-regulation-utilities-and-soes.md`).

---

## C. Failure modes (and the smallest countermeasure)
- **Single-bid normalization:** publish single-bid rate and require leadership sign-off above a threshold.
- **Exception laundering (“emergency” as routine):** exception record + time caps + post-award audit.
- **Amendment capture (award small, expand later):** publish amendment rate/value and require re-tender triggers.
- **Shell vendors / hidden related parties:** beneficial ownership disclosure and related-party checks for high-risk contracts.
- **Debarment as politics:** independent review and time-bounded debarment with public reasons summary.
- **Integrity theater:** enforce 2–3 controls *well* and measure closure, rather than adopting a long code with no follow-through. (See `101-claude-rev142-normative-requirements.md` (NR-20).)

---

## D. Minimal metrics (portable, low-burden)
Keep to a small set and tie each to an action rule. Prefer metric IDs from `03-metrics-and-evidence.md` packs.
- **Open publication coverage** (share of awards/spend published with stable IDs; timeliness) [IPM-1].
- **Single-bid share** (count and value) + threshold-triggered review [IPM-2].
- **Vendor concentration** (top-10 share or HHI) with trigger thresholds [IPM-3].
- **Integrity disclosures & protections:** asset declaration compliance; whistleblower retaliation incidence [IPM-4].
- **Audit closure:** % recommendations closed within 12/24 months [IPM-5].
- **Debarment and appeals:** counts + time-to-resolution [LRR-4].
- Optional local add-ons (keep ≤3): exception share + reasons; amendment inflation; close-out discipline.

---

## E. Minimal registers (make integrity legible)
Where capacity is low, these can start as simple CSVs with stable IDs.

### 1) Influence & interests register (integrity disclosures)
- Canonical spec: `46-influence-and-interests-register.md` (covers **interests/COI declarations** + **lobbying/meetings/gifts** as joinable objects).
- Interface rule: high-risk `DRR`s SHOULD cite relevant `INF-*` disclosures (or `INF: NONE DECLARED`) and any `INT-*` recusals/management actions.

### 2) Contract register (open contracting)
- Canonical spec: `38-contracting-and-procurement-register.md`.
- ID rule: every procurement process MUST have a stable `CON` (prefer OCID where using OCDS).
- Interface rule: awards and major amendments SHOULD cite a `DRR` and name the `AL-*` lane(s) for bid protest / supplier sanction appeal.
