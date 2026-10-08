# Compacts & Cooperative Governance (IOP-1)

**Cross-stack note:** use `305-interjurisdiction-compacts-authority-routing-and-cross-border-dispute-guide.md` for the canonical route across the inter-jurisdiction / compacts / authority-routing / cross-border-dispute family. This memo is the compact / cooperative-governance front door; `17` handles boundary and map change; `182` supplies the general polycentric design language; `197` handles overlapping sovereignty and federal design; `219` handles shared-service operations; `221` is the authority-routing substrate; `114` is the live dispute lane; and `230` handles cross-border recognition and conflict-of-laws. Use `322-executive-agreements-mous-political-commitments-and-international-instrument-typing-rails.md` when the question is whether the cross-border instrument should be a treaty, executive agreement, exchange of notes, MOU, or political commitment at all. Use `321-treaty-ratification-domestic-effect-reservations-and-implementation-rails.md` when the question is not whether a treaty-like compact is justified, but how an international agreement becomes domestically effective, how reservations are surfaced, or how treaty obligations are cross-walked into internal law. Use `324-treaty-lifecycle-change-provisional-application-amendment-suspension-and-withdrawal-rails.md` when the question is how an already-existing treaty or compact safely changes over time — provisional application, amendment uptake, suspension, denunciation, withdrawal, or public status-change control — rather than whether the compact should exist in the first place.

**Purpose:** make inter-jurisdiction compacts legible and enforceable so cooperation doesn’t become unaccountable discretion.
**Person served:** someone affected by cross‑jurisdiction agreements who needs compacts to be legible and contestable, rather than a way to evade accountability.

**From-below:** This makes cross‑government deals readable so cooperation doesn’t become a way to evade accountability or bury responsibility.

A **compact** is a written, enforceable agreement among jurisdictions (or public bodies) to jointly do something they can each do alone, or to coordinate where boundaries cause failure.

Compacts are the *default “in-between” layer* for polycentric systems: they let governments cooperate **without** creating a new general-purpose tier.

At global scope, treaty regimes behave like compacts and need the same clause disciplines (measurement, finance, remedy, exit/upgrade rules): e.g., IHR amendments and the WHO Pandemic Agreement: see [BIB-WHO-IHR-AMEND-QA] and [BIB-WHO-PA-2025].

**Primary advantage:** fast coordination, reversible by design.
**Primary risks:** hidden government (low transparency), weak accountability, free-riding/holdouts, off-book money.

**See also:** `70-interoperability.md` (interfaces + compact register), `24-mutual-aid-and-serious-incident-protocol.md` (mutual aid + serious-incident independence), `15-functional-authorities.md` (when to upgrade to a narrow authority), `16-metropolitan-governance.md` (metro selection), `17-jurisdiction-formation-and-boundaries.md` (when structure/boundaries must change), `18-intergovernmental-finance.md` (money map).

## Kernel anchors (do not repeat)

- **EXP pointer:** compacts must reduce EXP-01 Opacity and prevent EXP-07 Indifference (see `98-persons-path-and-accessibility-invariants.md`).
- **Person-facing invariants:** `98-persons-path-and-accessibility-invariants.md` (no AI/digital-only gates; oral/assisted options; safety).
- **Remedy is part of the interface:** `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md` (contestability; time bounds; functional equivalents).
- **Protective legibility (transparency ≠ safety):** `99-protective-legibility-and-adoption-dynamics.md`.
- **Records + publication integrity:** `31-records-foi-and-government-memory.md`, `51-release-registry.md`.
- **Intergovernmental finance constraints:** `18-intergovernmental-finance.md`.

## Named tensions (design must surface these)
- **Cooperation vs sovereignty:** shared solutions vs local autonomy.
- **Symmetry vs bargaining power:** strong jurisdictions setting terms for weak ones.
- **Flexibility vs enforceability:** adaptive compacts vs toothless promises.
- **Speed vs ratification:** crisis deals vs democratic legitimacy.

## Anchor set (start here)
- Council of Europe / UNDP / LGI — *Toolkit Manual: Inter‑Municipal Cooperation* (2010) (PDF): [BIB-COE-UNDP-IMC-2010]
- OECD/SIGMA Paper No. 70 (2024) — *Inter‑municipal co‑operation in the Western Balkans* (PDF): [BIB-OECD-SIGMA-IMC-WBALKANS-2024]
- OECD (2024) — *Enabling Inter‑Municipal Shared Service Provision in Lithuania* (PDF): [BIB-OECD-IMC-LITHUANIA-2024]
- Rosenbaum (2024) — “The Local Lawmaking Loophole” (*Yale Law Journal*) (PDF): [BIB-ROSENBAUM-LOCALLOOPHOLE-2024]

---

## 1) When to use a compact (and when not to)

### Use a compact when
- the problem is **cross-boundary** but does not require a new coercive sovereign;
- the task is **shared services / joint procurement / mutual aid / standards alignment**;
- the distributional conflict is manageable with formulas and a dispute path;
- reversibility is valuable (pilots, learning, uncertain institutional fit).

### Don’t use a compact when
- sustained **capex + debt** is central and accountability is likely to blur (upgrade to a functional authority with consolidated accounts);
- **land-use / redistribution** conflicts dominate and bargaining repeatedly fails (consider metro regional layer or conditional funding);
- the real need is **boundary/responsibility change** (use the process in `17-...`).

**Rule of thumb:** if a compact needs permanent staff, a balance sheet, and coercive enforcement, it is probably becoming an authority—treat it as such (`15-...`, `07-...`).

---

## 2) Minimum Viable Compact (MVC) — clauses that prevent failure

A compact MUST be fileable as a single “compact record” (`CMP-*`) and linkable from the competence ledger (`34-competence-ledger-and-mandate-registry.md`). It MUST include:

### A) Scope and competence boundaries
- **Purpose + scope**: what is covered and what is explicitly *not* covered.
- **Legal basis**: statute/charter authority for each party to sign.
- **Decision rights**: who decides what (including veto/override rules).

### B) Contributions and money discipline
- **Contributions**: funding formula, in-kind duties, data duties.
- **Residual risk**: who bears overruns and under what rules.
- **No off-book money**: pooled funds, SPVs, guarantees, and PPP liabilities MUST be disclosed and (where applicable) consolidated (`07-...`, `18-...`).

### C) Governance and transparency
- **Meeting transparency**: agendas, votes, minutes, and key documents.
- **Influence transparency** where relevant (lobbying and conflicts): cite `INF-*` / `INT-*` (see `46-...`).
- **Public filing** in the compact register (see §4).

### D) Performance and reporting
- **3–10 measures** tied to decisions, with reporting cadence (`03-...`).
- **Service standards** where users are affected (response times, access, continuity).
- **Verification & compliance ladder:** specify how reporting is checked (audit/inspection cadence + sampling), what counts as evidence (`REL-*` with methods + revision logs), and how noncompliance escalates (assist → warn → corrective plan → penalty/suspension). For material findings, require `DRR-*` + `AL-*` and `OFR-*` follow‑through. See `81-verification-inspection-and-compliance-ladders.md`.

### E) Enforcement ladder (graduated)
- a stepwise response to non-compliance (cure period → mediation → penalties/withholding → replacement operator/receiver → exit/upgrade trigger), **with due process**: notice, reasons, proportionality, and an appeal/dispute lane; each step SHOULD issue a `DRR` that links the relevant `CMP-*`.

### F) Dispute resolution and remedy
- **Administrative dispute path** (rapid mediation/arbitration) plus escalation points (`70-...`).
- **User remedy path** when services or rights are impacted (`08-...`).

### G) Sunset, renewal, and exit with continuity
- default **sunset/review** date; renewal requires evidence.
- **exit clause** with a transition plan (data handoff, asset allocation, staff transfer rules, continuity requirements).

### H) Amendment discipline
- change control: how amendments happen, what requires supermajority, and what requires public consultation.

---

## 3) Compact types (a small pattern library)

Use compacts as “lego bricks”:

- **Shared service compacts**: joint HR/payroll, permitting back-office, emergency dispatch.
- **Joint procurement compacts**: buying power + standard contracts + vendor oversight.
- **Mutual aid compacts**: surge capacity with rights constraints and serious-incident protocols; activations SHOULD be logged as `DRR-*` tagged `DRR-TYPE: AID` (MAAL), and serious incidents SHOULD open an `OFR-*` case within 24 hours (`05-...`, `24-...`, `70-...`).
- **Corridor/network standards compacts**: road design, transit interoperability, permitting standards, cross-border enforcement coordination.
- **Watershed/airshed compacts**: ecological budgets + monitoring + enforcement clauses (`11-...`, `70-...`).

---

## 4) The Compact Register (anti-“hidden government”)

Every jurisdiction MUST publish (or participate in) a **compact register** that:
- assigns each compact a **stable ID** (`CMP-*`),
- stores the **compact record** (metadata + link to full text),
- links compacts to the **competence ledger** entries of all parties,
- links money flows to the **transfer register** when public funds move (`18-...`),
- exposes a simple, searchable list of: parties, scope, term, dispute path, and sunset date.

### Skeleton: `CMP` compact record (publishable; minimal)

```yaml
CMP-ID: CMP-____
AUTH-DRR: DRR-____ # authorizing decision to enter/renew/terminate (join rule in `70-...`)
TITLE: ...
TYPE: (SERVICE_SHARING | MUTUAL_AID | JOINT_PROCUREMENT | BASIN/GW | CORRIDOR | MARKET_RULES | OTHER)
MUTUAL_AID (if TYPE=MUTUAL_AID):
 ACTIVATION_LOG: DRR-TYPE: AID # MAAL
 SERIOUS_INCIDENT_CASE: OFR-* # independence pipeline
PARTIES:
 UNITS: [UNIT-____, ...]
SCOPE:
 PURPOSE: ...
 EXCLUDES: [...]
TERM:
 START: YYYY-MM-DD
 END: YYYY-MM-DD
 SUNSET/RENEWAL_RULE: ...
DECISION_RIGHTS:
 GOVERNANCE_BODY: (name + UNIT)
 VETO/OVERRIDE_RULES: ...
MONEY:
 CONTRIBUTION_FORMULA: ...
 POOLED_FUNDS: (Y/N)
 LINKED_TRANSFERS: [TRF-____, ...]
MEASURES:
 KPI: [metric_id_or_name, ...] # 3–10
 REPORTING_CADENCE: ...
ENFORCEMENT:
 LADDER: [cure, mediation, penalty/withhold, receiver/replace, exit/upgrade]
 DUE_PROCESS: [notice, reasons, proportionality, appeal_lane]
DISPUTE_PATH:
 LANES: [AL-____, ...] # include AL-COMP if competence questions possible
PUBLIC_FILING:
 FULL_TEXT: (link)
 MEETINGS/MINUTES: (link)
REVISION:
 VERSION: v__
 CHANGELOG: (link or inline note)
```

**Join rule:** material enforcement actions, dispute outcomes, and upgrades SHOULD issue `DRR`s that link the `CMP-ID` (so “the compact did it” becomes auditable). See `31-records-foi-and-government-memory.md` and `70-interoperability.md`.

**Rationale:** interlocal agreements can create real law and spending while remaining low-salience and poorly disclosed; the register makes compacts governable objects.

---

## 5) Failure modes (and the minimum fixes)

- **Paper cooperation** (no operational reality): require measures + reporting + cure/enforcement.
- **Free-riding / holdouts:** formula-based contributions, measurable obligations, and arbitration.
- **Capture in low-salience spaces:** meeting + influence transparency, independent audit, and board appointment rules.
- **Off-book debt / SPVs:** consolidation rules and fiscal risk disclosures (`07-...`).
- **Blame shifting (“not us, the compact”):** competence ledger linkage + public service charters + a clear user remedy path.

### 5a) Captured partner / bad-faith counterparty (dominant real-world failure)
Compacts fail most often not by “missing paperwork” but by a party that **won’t comply** (or has been captured). Minimum hardening:
- **Independent MRV:** shared metrics MUST allow third-party sampling or audit (even if full disclosure is limited); publish the audit schedule and summary findings.
- **Legible noncompliance events:** missed obligations and cure-period expiries SHOULD produce `DRR` records linked to the `CMP-*` (so patterns are joinable, not folklore).
- **Receiver/replace option:** the enforcement ladder SHOULD include a time-bounded receiver/replace step for service delivery (with due process), not just “penalty or exit.”
- **Conditionality with continuity:** funding/withholding tools must protect essential-service continuity (`35-transfer-register-and-conditionality.md`, `80-implementation-roadmap.md`).
- **Escalation trigger:** repeated breach SHOULD open an `OFR-*` finding (oversight file) and force an explicit keep/upgrade/exit decision with reasons.

---

## 6) Upgrade path (when compacts fail)

Compacts SHOULD be designed to “harden” in place:
1) **Improve the compact** (add transparency/audit/enforcement).
2) **Upgrade to a functional authority** with a narrow charter and consolidated accounts (`15-...`).
3) **Change boundaries/responsibilities** using the MV boundary/reorg process (`17-...`).

A compact MUST specify the trigger conditions that force escalation to (2) or (3) (e.g., repeated non-compliance, capex thresholds, persistent distributional conflict).
