# Conflict‑of‑Interest & Revolving Door Discipline (Integrity Controls that Actually Bind)

**Purpose:** reduce capture by making conflicts legible, constrained, and consequence-bearing across hiring and procurement.

**Person served:** Residents harmed when decisions are sold or captured who need conflicts disclosed, managed, and enforceably punished.

**From-below:** This stops self‑dealing by making conflicts and revolving‑door risks explicit, enforceable, and inspectable by the public.

**EXP pointer:** counters `EXP-01` (Opacity) and `EXP-05` (Fear) by making conflicts enforceable and giving safe reporting lanes when capture/harassment would otherwise chill complaints (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** COI/revolving‑door controls must have binding levers (recusal, nullification, debarment, discipline, clawback) and duty-to-respond closure loops (`32`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** safe reporting for conflicts/capture with protective procedures and monitoring for harassment/chilling (`83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish `03` IPM‑4. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** officeholders and agencies bear the burden to disclose and evidence conflict handling (recusal, divestment, waivers); complainants must not be required to prove hidden facts; adverse outcomes cite `RC-*` + `AL-*` (`44`, `83`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


The archive already makes **decisions** and **money** joinable. Integrity failures happen when *influence* and *conflicts* are treated as “personal ethics” rather than a **governance interface**.

This memo defines a minimal, portable discipline for:
- **conflict-of-interest (COI)** identification and management,
- **gifts/hospitality/outside income** controls,
- **revolving door** (entry/exit restrictions, cooling‑off, and waiver discipline), and
- making all of the above **auditable** without doxxing.

It is intentionally short: the detailed disclosure schemas live in `46-influence-and-interests-register.md`.

**See also:** `22-public-integrity-and-procurement.md`, `78-delegation-and-acting-authority-discipline.md` (recusal → replacement authority), `71-interface-obligations-by-scope.md` (when this becomes mandatory), and `76-systemic-redress-and-pattern-remediation.md` (pattern correction).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- Decision receipts (person-facing) default to `31-records-foi-and-government-memory.md` (Decision Receipt minimum fields).
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Influence and interests register (entities and ties): `46-...`.
- Procurement/contracting joins: `38-...`.
- Oversight findings + enforcement hooks: `55-...`, `32-...`.
- Publication integrity for disclosures: `53-...`.

## Named tensions (design must surface these)
- Transparency for trust vs privacy and harassment risks.
- Strict rules vs enforceability (paper compliance vs real constraints).
- Deterrence vs staffing/skill retention (especially in low-capacity states).
- Central standards vs local professional norms and plural institutions.

---
## Anchor set (start here)
- OECD Guidelines for Managing Conflict of Interest in the Public Service: [BIB-OECD-COI].
- OECD Recommendation on Public Integrity + implementation handbook: [BIB-OECD-PI], [BIB-OECD-PI-HANDBOOK-2020].
- OECD Recommendation on Transparency and Integrity in Lobbying and Influence (includes revolving door emphasis): [BIB-OECD-LOB].
- OECD *Preventing Policy Capture* (risk framing and integrated controls): [BIB-OECD-POLICYCAPTURE-2017].
- UNCAC prevention baselines (conflicts, codes, procurement): [BIB-UNCAC].
- Council of Europe lobbying transparency recommendation (legal regulation pattern): [BIB-COE-LOBBY-2017].

---

## A. Minimal success condition (one screen)
For any high‑risk decision, a reviewer can answer from joinable artifacts:

1) **Was the relevant conflict disclosed?** (`INT-*` status is current)
2) **If there was a conflict, what management action occurred?** (recusal/divestment/firewall), via a `DRR-*` receipt.
3) **If someone else acted, were they authorized?** (`DRR-TYPE: DELEGATION` where applicable; see `78-...`).
4) **Was influence logged?** (`INF-*` disclosures or `INF: NONE DECLARED` for covered decision classes).
5) **Were any waivers granted?** (typed waiver receipts; no silent “exceptions”).

If any of these are missing, treat it as a **governance incident**: open an `OFR-*` `LEGIBILITY-GAP` case and/or allow `AL-LEG` complaints (see `55-...`, `08-...`, `36-...`).

---

## B. Coverage rules (risk‑tiered; avoid bureaucracy)
Define a small set of covered role tiers. The tiers are *role classes* (not people) and should be recorded in the competence ledger.

### Tier 1 — highest discretion / highest capture risk
- elected officials and political executives;
- ministers/agency heads;
- senior procurement, permitting, licensing, enforcement, and regulator roles;
- roles with direct control over grants/subsidies/transfers;
- roles with access to material non‑public market‑moving or enforcement information.

### Tier 2 — significant discretion
- managers approving contracts/permits/grants below Tier 1 thresholds;
- policy‑drafters and standards‑setters for major regimes.

### Tier 3 — minimal (only where needed)
- roles with limited discretion but high contact exposure (e.g., frontline inspectors) when local risk warrants.

**Rule:** start with Tier 1 only; expand only if you can enforce.

---

## C. What must be disclosed (keep categories stable)
Disclosures should be category‑based. Detailed schema is `INT-*` in `46-...`; here is the minimum category set:

- **Outside roles and employment** (including consulting/advisory roles)
- **Financial interests** relevant to the role (holdings, beneficial interests where required)
- **Gifts/hospitality/travel** above threshold
- **Close relationships** that create decision conflicts (avoid public details; manage in protected layer)
- **Negotiating future employment** with a regulated/vendor entity (revolving‑door trigger)

**Design rule:** publish **status + categories + management actions**, not sensitive personal details.

---

## D. Management actions must be joinable (not private)
Every management action that changes how authority is exercised emits a `DRR-*` receipt.

### D1) Recusal (the default)
- Issue a `DRR-KIND: DEC` with `DRR-TYPE: INTEGRITY` referencing the relevant `INT-*`.
- The receipt states: decision class affected, recusal scope, and duration.

If recusal requires a substitute signer:
- emit `DRR-TYPE: DELEGATION` for replacement authority (time‑bounded), and link it to the integrity `DRR` and `INT-*` (see `78-...`).

### D2) Divestment / blind trust / firewall
- Use a `DRR-TYPE: INTEGRITY` receipt to record the action type and effective date.
- If details are sensitive, publish the receipt with withholding discipline (reason category + review date) and keep full detail in a protected layer with audit logs (see `77-...`).

### D3) Disqualification / removal (for severe conflicts)
- Issue a `DRR-TYPE: INTEGRITY` decision with a stated appeal lane (`AL-*`), and link it to the relevant `INT-*` and any impacted mandates (competence ledger update if needed).

---

## E. Revolving door discipline (entry + exit)
Revolving‑door risk is not only “official goes to industry”; it’s also **industry enters government** with private entanglements.

### E1) Entry (private → public)
For Tier 1 roles, require a pre‑appointment integrity packet:
- `INT-*` declaration filed and reviewed;
- a management plan (`DRR-TYPE: INTEGRITY`) for any active conflicts (recusals/firewalls);
- a public note of any *material* prior lobbying/representation in the policy area (category‑level only; do not publish private client lists unless required by law).

### E2) Exit (public → private)
For Tier 1 roles, adopt a simple **cooling‑off** rule for:
- lobbying/representation to the former agency/portfolio;
- contracts/grants with the former unit;
- regulated entities where the official had material decision authority.

**Implementation pattern:** treat exit restrictions as an **integrity decision**:
- issue a `DRR-TYPE: INTEGRITY` exit determination that records the restriction categories and end date.

### E3) Waivers are decisions (no silent exceptions)
If a waiver is allowed at all:
- it MUST be time‑bounded;
- it MUST cite the legal basis (`RULE-*` as‑of);
- it MUST name a public interest justification;
- it MUST specify mitigation conditions (e.g., no contact with portfolio; firewall).

Publish a waiver receipt as `DRR-TYPE: INTEGRITY` and link it to the relevant `INT-*` (and `INF-*` if lobbying contact will occur).

---

## F. Influence disclosure rule (regulatory footprint lite)
For high‑risk decision classes (permits, procurement awards/amendments, major regulatory changes, enforcement discretion):

- the decision receipt (`DRR-*`) MUST include either:
  - the relevant `INF-*` IDs, or
  - `INF: NONE DECLARED`.

This makes influence auditing feasible without expanding the archive into a lobbying handbook.

---

## G. Enforcement and remedy (keep it credible)
A discipline without enforcement becomes “ethics theater.” Minimum ladder:

1) **Late filing visibility:** overdue `INT` status is public (no silent grace).
2) **Auto‑notice + escalation:** repeated noncompliance triggers a formal notice (`DRR-TYPE: INTEGRITY`).
3) **Typed sanctions:** administrative discipline, disqualification from decision classes, or supplier remedies (debarment where applicable) with an appeal lane.
4) **Independent review access:** ethics determinations and waiver decisions are reviewable (`AL-*`), and pattern failures can trigger a systemic `OFR-*` case (see `76-...`).

---

## H. Minimal metrics (use existing packs)
- **[IPM-4]** Integrity disclosures & protections (filing compliance; retaliation incidence).
- **[IPM-20]** Influence transparency & recusal compliance (INF/INT joins; recusal traceability).
- **[IPM-13]** Procurement openness & change‑order share (capture signal, when procurement is material).

---

## I. Where to wire this
- **Registers:** `46-influence-and-interests-register.md` (INF/INT schemas).
- **Procurement:** `22-public-integrity-and-procurement.md` (MVPI controls + open contracting).
- **Permissioning:** `29-permissioning-and-approvals.md` (discretion + delay power + anti‑rent controls).
- **Delegation:** `78-delegation-and-acting-authority-discipline.md` (recusal → substitute signer discipline).
- **Threats:** [TM-19] in `04-threat-models.md` (influence laundering).
