# Tax & Revenue Administration (Revenue as Legitimacy Infrastructure)

**Purpose:** raise revenue with **fairness, predictability, and due process** while minimizing coercion, corruption, and privacy harm. Revenue administration is an *exercise of power* (assessment, audit, collection, penalties), so it must emit the same **joinable artifacts** as any other rights‑affecting system.

**Person served:** A taxpayer or claimant facing assessment, collection, penalties, or refunds who needs fair rules, receipts, and non‑coercive dispute paths.

**From-below:** This makes tax collection and enforcement contestable so errors and abuse have clear correction, evidence, and remedy paths.
**EXP pointer:** counters `EXP-05` (Fear) and `EXP-01` (Opacity) by requiring receipted, appealable coercive actions (`98-persons-path-and-accessibility-invariants.md`).

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).

**Authority:** assessments/penalties/collections must name the binding review lane and stay rules (where available) so “pay first, contest later” is explicit and contestable (`36`, `66`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** safe complaint/appeal channels without retaliatory audits or collections; protect whistleblowers and publish chilling indicators (`83`, `77`, `03`). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)

**Proof burdens:** publish required evidence + least-burdensome alternatives; disclose “once-only” retrieval of state-held facts; ensure adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)

**Interfaces to reuse (no new ID families):** `RULE-*` (tax law), `REL-*` (forms/tables/rates/method notes), `DRR-*` (assessments/penalties/refunds/collection actions), `AL-*` (tax appeals/urgent lanes), `OFR-*` (oversight cases), `SRV-*` (filing/payment/refund services), `ADS-*` (risk scoring/automation), `ENF-*` (custody/coercion only if used).

**Anchors (start here):** [BIB-OECD-TAXADMIN-2025] (comparative tax administration patterns and trends); [BIB-TADAT] (diagnostic framework hub); [BIB-IMF-VITARA-ORG-2024] / [BIB-IMF-VITARA-STRAT-2023] (operating model / strategy components).

See also: `07-fiscal-and-budgetary-governance.md` (budget legitimacy), `43-enforcement-and-custody-event-register.md` (log coercive collection events where applicable), `05-public-safety-and-coercion.md` (coercion/receipt baseline), `33-data-protection-and-personal-data-governance.md` (sensitive data), `36-appeal-lanes-and-redress-registry.md` (contestability), `84-internal-controls-and-continuous-assurance.md` (control map), `06-digital-and-algorithmic-governance.md` + `42-...` (automation).

**Commons/eco junction:** where revenue comes from commons-linked charges (resource rents, pollution fees, land value capture), treat it as both a fiscal and ecological interface: publish the legal basis (`RULE-*`), method notes (`REL-*`), and any earmark/transfer rules so the burden and the use of funds are contestable (see `11-...`, `07-...`, `18-...`).

## Kernel anchors (do not repeat)
- Coercion boundary and enforcement event logging: `05-...`, `43-...`.
- Person-facing access floors (non-digital; assisted): `98-persons-path-and-accessibility-invariants.md`.
- Records/receipts for assessments/collections and corrections: `31-...`.
- Appeals lanes for determinations and enforcement actions: `36-...`, `08-...`.
- Publication integrity for rules/interpretations: `53-...`, `39-...`.
- Protective legibility / adoption dynamics (tax consent + political economy): `99-protective-legibility-and-adoption-dynamics.md`.

## Named tensions (design must surface these)
- Enforcement to fund the state vs fairness/legitimacy (tax as consent surface).
- Transparency for trust vs evasion/adversarial adaptation.
- Automation/scale vs contestability and individualized justice.
- Revenue urgency vs harm from aggressive collection (subsistence reality).

---
## A. Minimum viable revenue administration (MVRA)

### 1) Legibility of obligations (reduce “surprise coercion”)
- MUST: a **Public Rules Register** entry for material tax rules (`RULE-*`) with “as‑of” access and a change log (`39-...`).
- MUST: publish authoritative *rate tables, thresholds, and calculation methods* as versioned `REL-*` releases (diffable; no silent edits) (`51-...`, `53-...`).
- SHOULD: publish a plain-language *taxpayer rights & obligations* charter and keep it aligned with appeal lanes (`AL-*`).

### 2) Registration, filing, payment, and refunds as services
Treat core workflows as `SRV-*` services and attach minimum service guarantees (`82-...`).
- MUST: accessible channels + predictable deadlines.
- MUST: receipt discipline for submissions and payments (timestamped, queryable, non-repudiable) (`31-...`).
- MUST: refund decisions emit `DRR-*` with reasons (`RC-*`) and a contestation lane (`AL-*`).
- SHOULD: publish aggregate timeliness and backlog metrics as `REL-*` (methods + revision log).

### 3) Assessment and penalties emit decision receipts
- MUST: any assessment, penalty, interest calculation, or adverse determination emits a **Decision Receipt** (`DRR-*`) citing:
  - the controlling `RULE-*` (as‑of),
  - any controlling releases (`REL-*`) used in the calculation,
  - plain-language reasons + reason codes (extend `RC-*` locally if needed),
  - the appeal lane(s) (`AL-*`) with deadlines.
- SHOULD: publish standard penalty matrices and settlement/abatement criteria as versioned `REL-*` (prevents “secret discounting”).

### 4) Compliance risk management without discrimination
- SHOULD: a written compliance strategy (publish high-level: risk categories, protections, audit selection controls) and tie it to the threat model (`TM-*`).
- MUST: combine **risk-based + random sampling** (anti-gaming); publish a sampling policy consistent with `81-...`.
- MUST: if automated risk scoring is used, register the system (`ADS-*`) and publish contestability notes; treat adverse outcomes as appealable (`06/42/36`).
- MUST: prohibit “proxy discrimination” in selection rules; require periodic disparate-impact checks where feasible (publish as `REL-*` with privacy protection).

### 5) Collection power bounded by due process
- MUST: graduated enforcement ladder (notice → installment → offset → lien/garnishment) with explicit thresholds and time bounds.
- MUST: any coercive collection action (seizure, garnishment, restriction) is logged as an `ENF-*` event (and included in the enforcement event register `43-...` where applicable) linked to the authorizing `DRR-*` (and is appealable via `AL-*`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
- MUST: hard constraints on coercive actions; emergency/summary powers (if any) require strict logging + review (`23-...`, `45-...`).
- MUST: publish a discoverable urgent protection lane (`AL-*`) for imminent irreversible harm (e.g., wrongful seizure).

### 6) Anti-corruption and internal controls
- MUST: separation of duties for assessment/audit/collection; tamper‑evident logs for adjustments and write-offs.
- MUST: publish a control map + exception handling (route material exceptions into `OFR-*`) (`84-...`, `55-...`).
- SHOULD: protected disclosures for staff and taxpayers (`83-...`) and clear COI rules for auditors/settlement staff (`79-...`).

### 7) Data governance and confidentiality
- MUST: purpose limitation and least-privilege access for taxpayer data; publish access and sharing rules.
- MUST: any cross-system data sharing uses a narrow legal basis (`RULE-*`) + logged releases (`REL-*`) and is reviewable (`33-...`, `77-...`).
- SHOULD: publish de-identified aggregate statistics as `REL-*` (methods + revision log) to enable public scrutiny without leaking sensitive records.

---

## B. Failure modes (and minimal countermeasures)

- **“Hidden law” via guidance:** inventory binding guidance and attach it to PRR; publish calculation tables as versioned releases.
- **Selective enforcement / politicization:** publish selection controls, add random audits, publish audit outcome distributions, and protect appeals.
- **Corruption via discretionary settlements:** publish criteria + logs, separate roles, and audit write-offs.
- **Data overreach:** purpose limitation + narrow sharing gateways + independent review; register automation.
- **Refund abuse vs. refund denial:** publish refund rules + dispute lanes; measure both fraud controls and legitimate refund timeliness.

---

## C. Minimal metrics (portable)
Keep small; tie to a decision loop.
- **Filing/payment timeliness:** % on-time; backlog days (by service `SRV-*`).
- **Dispute fairness:** average time to resolve; % overturned on appeal (by issue class).
- **Refund discipline:** median days to refund; % refunds delayed beyond standard.
- **Compliance posture:** estimated tax gap (where feasible) + cost of collection.
- **Integrity signals:** write-off volume + variance; staff disciplinary cases (aggregate); protected disclosure throughput.

---

## Anchors (start here)
- Tax Administration Diagnostic Assessment Tool (TADAT) framework: see [BIB-TADAT].
- OECD Tax Administration Series (comparative admin data; ISORA): see [BIB-OECD-TAXADMIN-2025].
- IMF VITARA revenue administration reference guides (org/strategy): see [BIB-IMF-VITARA-ORG-2024] and [BIB-IMF-VITARA-STRAT-2023].
- OECD compliance risk management guidance (framework notes): see [BIB-OECD-CRM-2012] and [BIB-OECD-MITC-2004].
