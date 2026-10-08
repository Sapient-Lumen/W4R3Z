# Justice & Administrative Justice Governance (Auditable Courts + Tribunals)

**Purpose:** make administrative justice real: reasons, counsel/representation, safe contestation, and follow‑through.

**Person served:** A person contesting a government decision in a tribunal/court who needs a timely, affordable hearing with enforceable relief.

**From-below:** This makes legal processes legible so you can understand timelines and remedies when the state acts against you.
**EXP pointer:** counters `EXP-02` (Waiting) and `EXP-05` (Fear) by making justice timelines and interim relief usable (`98-persons-path-and-accessibility-invariants.md`).

**Assistance & representation:** publish assisted/oral paths (incl. interpretation) and who can act on behalf of someone; name independent advocates where conflict risk is high (see `98`, `36`, `47`, `82`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).

**Authority:** courts/tribunals are the binding backstop: orders, interim relief, and enforcement against non‑compliance must be explicit and reachable from below (`36`, `55`). (See `101-claude-rev142-normative-requirements.md` (NR-09).)
**Retaliation safety:** protective procedures for claimants/witnesses (safe filing, confidentiality where needed, anti‑reprisal enforcement) so contestation is not self-harm (`77`, `83`, `03`). (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)

**Proof burdens:** publish required evidence + least-burdensome alternatives; disclose “once-only” retrieval of state-held facts; ensure adverse outcomes cite `RC-*` + a contestation lane (`47`, `44`, `52`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)

**Problem class:** justice systems are the ultimate “backstop” for legitimacy. When they are slow, captured, inaccessible, or non‑compliant (orders ignored), *every* other governance interface decays.

**Design goal:** treat courts/tribunals as **auditable infrastructure**: case entry → procedure → decision → remedy → compliance, with publication integrity and accessible pathways.

**Mercy / equitable relief:** rule‑of‑law systems still require space for humane outcomes (hard cases, exceptional hardship). This archive cannot *produce* mercy, but it can make mercy **possible without secrecy**: create lawful discretion spaces and require reasons/receipts so both cruelty and favoritism are contestable. **Accountability without mercy becomes bureaucratic cruelty; mercy without accountability becomes arbitrary power.** Where mercy/discretion exists, it SHOULD be exercised through logged, reviewable paths (waivers/variances with receipts) rather than informal favoritism (see `85-waivers-variances-and-exceptions-discipline.md` and `08-remedy-and-grievance.md`).

**This memo is intentionally minimal.** It composes existing interfaces: rules (`RULE-*`), decision receipts (`DRR-*`), reason codes (`RC-*`), remedy lanes (`AL-*`), releases (`REL-*`), oversight follow‑through (`OFR-*`), and publication integrity (`53-...`).

**Anchor set:** independence and judicial conduct baselines [BIB-UN-JUD-INDEP-1985], [BIB-BANGALORE-2002]; timeliness tools [BIB-CEPEJ-SATURN-2018]; rule-of-law measurement (optional) [BIB-WJP-ROL-2025].

## Kernel anchors (do not repeat)
- Person-facing invariants: `98-persons-path-and-accessibility-invariants.md` (incl. non‑digital/non‑reading options), service journeys `47-...`, remedy lanes `36-...` / `08-...`.
- Protective legibility + adoption dynamics: `99-protective-legibility-and-adoption-dynamics.md` (transparency ≠ accountability; identify who loses discretion / who gains contestation capacity).
- Publication integrity (no silent edits; “as‑of” access): `53-...` and `31-...` where relevant.
- Anti‑retaliation and safe filing (especially where the state is a party): `98-persons-path-and-accessibility-invariants.md`, `08-...`, `77-...`.
- Assurance-case discipline for high‑stakes systems (case management, evidence tech, AI triage): `73-...`, `06-...`.

## Named tensions (design must surface these)
- Speed/timeliness vs due process/quality (delay is denial; haste is error).
- Transparency/publication vs privacy/safety of parties, witnesses, and vulnerable claimants.
- Formal access-to-justice vs retaliation/chilling (especially where the state is a party) (see [TM-29]).
- Uniformity/predictability vs equity/mercy (arbitrary power vs bureaucratic cruelty).
- Judicial independence vs democratic accountability (capture risk in both directions).
- Access-to-justice vs resource constraints (design interfaces that reduce procedural load).

---

## A) Scope (what this memo covers)
This memo focuses on:
- **Administrative justice** (state decisions challenged by people/organizations),
- **Civil justice access** (dispute resolution and enforcement where the state provides forums),
- **Court/tribunal publication and integrity** (no silent edits; accessible precedent).

It does **not** attempt a full criminal justice architecture (see `05-public-safety-and-coercion.md` for coercion controls and `43-...` for enforcement/custody events).

---

## B) Minimum Viable Administrative Justice & Courts Spine (MVAJCS)

### B1) Every rights-/resource‑affecting administrative act emits a receipt
For any adverse determination, suspension, penalty, denial, recoupment, or license action:
- MUST issue a `DRR-*` citing `RULE-*` (as‑of), plain reasons + `RC-*`, and the next `AL-*` lane(s).
- MUST state deadlines, evidence relied on (`REL-*` where applicable), and what interim relief exists.

This prevents “procedural denial by opacity” and lets remedies route correctly (`36-...`).

### B2) Remedy ladder is discoverable and time‑bounded
A minimal ladder (exact steps vary by domain):
1) **Internal review / reconsideration** (fast, paper‑capable)  
2) **Independent tribunal** (specialized, accessible, published decisions)  
3) **Court review** (rule‑of‑law backstop; constitutional/rights questions)  
4) **Enforcement / compliance** (orders are executed; noncompliance becomes auditable)

Each forum MUST be registered in ALR (`AL-*`) with: jurisdiction, filing methods, fees/waivers, representation rules, available remedies, timelines, and escalation.

**Waiting is harm:** courts/tribunals MUST publish time commitments (acknowledgement, first hearing, decision) and treat missed timelines as auditable failures; where delay would moot rights, interim relief/stay rules must be clear and usable. (`82-...`, `03-...`) (See `101-claude-rev142-normative-requirements.md` (NR-05).)

### B3) Decisions are published as integrity‑grade releases
Courts/tribunals SHOULD publish:
- a **decision feed** as a versioned `REL-*` release (with “as‑of” access and change logs),
- a **redaction policy** (privacy + safety) treated as a `RULE-*` instrument,
- and a tamper‑evident publication pipeline per `53-...` (at least L1: visible revision history; ideally L2/L3 for high‑stakes systems).

### B4) Independence, recusals, and discipline are logged without compromising safety
- Independence and conflicts‑of‑interest standards SHOULD be codified as `RULE-*` instruments (appointments, tenure protections, recusal triggers, disclosure).
- Misconduct findings and systemic failures SHOULD appear in OFRR (`OFR-*`) with a public response plan and deadlines (`55-...`).

### B5) Access is engineered, not assumed
Minimum access protections:
- **Fee waivers** and **plain‑language forms** for self‑represented users.
- Interpreter and disability accommodation pathways.
- Legal aid/assistance ecosystem mapped as a service journey (`SRV-*`) with routing rules and capacity metrics.
- Remote participation allowed where it improves access and does not undermine fairness.

---

## C) Minimal artifacts (one-screen skeletons)

### C1) `DRR-TYPE: JUDGMENT` (court/tribunal decision receipt)
```yaml
DRR-ID: DRR-____
DRR-KIND: DEC
DRR-TYPE: JUDGMENT
FORUM: (court/tribunal name)      # MUST map to an AL-* lane
CASE-REF: (local case identifier)  # publishable reference or redacted handle
DECISION-DATE: YYYY-MM-DD
PARTIES: (redacted as needed)
SUBJECT: (plain language)
BASIS: [RULE-… , STD-…]            # controlling rules/standards (as-of)
FINDINGS: (short; cite evidence releases where possible)
REASON-CODES: [RC-JUS-…]           # procedural disposition codes if applicable
OUTCOME: (granted/denied/partial; orders)
REMEDY: (what is ordered; timelines)
NEXT: (appeal lane AL-…; deadline; interim relief)
LINKS: [REL-… , OFR-…]             # if evidence release or oversight case applies
```

### C2) `REL-*` Decision Feed (publication release)
```yaml
REL-ID: REL-____
TITLE: (e.g., Tribunal Decisions — YYYY-MM)
VERSION: vN
AS_OF: YYYY-MM-DD
METHOD: (publication method; redaction approach; completeness caveats)
SCHEMA: (fields; identifiers; how to join to DRR)
INTEGRITY: (hash/signature/log pointer; see `53-...`)
CONTACT: (challenge/correction lane AL-…)
```

---

## D) Failure modes (what to watch)
- **Backlog as denial:** long time-to-hearing; remedies become moot (measure clearance + age-of-caseload).
- **Opacity:** unpublished decisions; inconsistent reasons; missing `AL-*` routing.
- **Noncompliance:** orders ignored; “paper victories” (measure compliance time + rate; see [TM-33]).
- **Capture/selection:** politicized appointments; retaliatory transfers (log and audit patterns; use `OFR-*`).
- **Access cliffs:** language, disability, digital-only filing, fee traps (measure representation + waiver uptake + default rates).

---

## E) Cross-scope notes
- Shared tribunals across units SHOULD be governed via a `CMP-*` compact (who funds, who appoints, which standards apply, dispute path).
- National/supranational courts can require **remedy continuity plans** when mandates shift (link to `DRR-TYPE: SCOPE` and `54-...`).
- Alternative dispute resolution (ADR/ODR) SHOULD still emit `DRR-*` for binding outcomes and register lanes in `ALR`.