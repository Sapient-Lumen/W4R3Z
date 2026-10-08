# Constitutional & Charter Change (Amendment Discipline as Integrity Infrastructure)

**Purpose:** make constitutional change processes legible and non‑laundering so foundational power shifts stay contestable.

**Person served:** A resident whose rights and political membership are reshaped by constitutional change and who needs notice, voice, and protection against rushed or captured amendments.

**From-below:** This slows foundational rule changes so rights can’t be amended away without clear notice, evidence, and contestation.

**EXP pointer:** counters `EXP-06` (Complexity) and `EXP-08` (Invisibility) by making constitutional change legible, bounded, and reachable beyond insiders (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)

**Assistance & representation:** provide assisted/oral paths (incl. interpretation) for proposal/ballot packs and dispute intake; name independent advocates where conflict risk is high (see `98`, `36`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** amendment gatekeeping decisions (eligibility, clarity/neutrality, certification, emergency-window tests) MUST be grounded in `RULE-*` and receipted (`DRR-*`), naming the binding review lane and decision-maker (`34`, `31`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** protect petitioners, voters, and participants from intimidation/harassment; keep reporting channels safe and apply protective disclosure/redaction to campaign/contact lists and complaint evidence (`83`, `77`, `03`); include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4). (See `101-claude-rev142-normative-requirements.md` (NR-08).)
**Mercy / interim protection:** default to cooling‑off/stay rules: credible intimidation, accessibility barriers, or unresolved disputes trigger interim protection and deadline relief; emergency-window invocations require heightened review (`85`, `82`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** publish minimum publication/cooling‑off windows, challenge deadlines, and certification timelines; include a no‑response rule so disputes can’t be killed by delay (`82`, `36`, `31`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** proposal bundles, eligibility rulings, and certification steps MUST have stable IDs and person‑usable receipts with the `31` minimum fields (what changed, why, what to do next, by when), referencing the controlling `RULE-*` and contestation lane (`31`, `53`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** gatekeeping decisions (eligibility, clarity/neutrality, emergency-window tests) MUST disclose evidentiary standards + allocation (what proponents must show vs what the state must prove) and provide least-burdensome alternatives; adverse outcomes cite `RC-*` + `AL-*` (`44`, `47`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**As-of & corrections:** authoritative texts and diffs MUST remain retrievable “as‑of”; corrections/retractions publish as new `REL-*` with linkage (no silent incorporation) (`51`, `53`, `31`). (`101` NR-07, NR-15)
**Join constraints:** where registries/petition rolls/identity checks are used, joins MUST follow `70` and preserve safe alternatives (paper receipts; offline filing) (`70`). (See `101-claude-rev142-normative-requirements.md` (NR-14).)

Constitutions, charters, and top‑tier compacts are **rule hierarchies**: they allocate authority, define rights, and constrain coercion. Changes to these instruments therefore require **integrity-grade procedure** and a **tamper-evident, contestable paper trail**.

This memo defines a compact **Minimum Viable Constitutional Change Discipline (MVCCD)** using existing join-keys (`PRR/RULE-*`, `REL-*`, `DRR-*`, `AL-*`, `INT/INF-*`, `OFR-*`, `EMR-*`) and the archive’s publication integrity layer (`53-...`).  
Anchors: referendum good practice ([BIB-VENICE-REFERENDUMS-2007], [BIB-VENICE-REFERENDUMS-2022]), direct democracy design ([BIB-IDEA-DIRECTDEMO]), and amendment theory/practice ([BIB-ALBERT-CONSTAMEND]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Publication integrity + point-in-time access for top-tier rules: `53-...`, `51-...`, `31-...`, PRR `39-...`.
- Person-facing comprehension + offline access for ratification materials: `98-persons-path-and-accessibility-invariants.md`.
- Dispute/appeal lanes (pre- and post-vote): `36-...` / `08-...`.
- Influence, procurement, and integrity joins (anti-capture): `46-...`, `22-...`.
- Oversight follow-through (no “paper compliance”): `32-...`, `55-...`.

## Named tensions (design must surface these)
- Speed in crisis vs democratic deliberation/cooling-off (avoid panic entrenchment).
- Simplicity/clarity vs real complexity (don’t launder major shifts through vague summaries).
- Popular sovereignty mechanisms vs rights floors/minority protection (legitimacy is not just majorities).
- Transparency of campaigning vs safety/retaliation (protective disclosure where needed).
- Stability/constitutional continuity vs adaptability (guardrails that still allow repair).

---

## 1) Failure modes (design against)
- **Invisible constitutional change**: people cannot find the authoritative text “as of” a date; amendments are incorporated silently.
- **Rushed change under panic**: emergency conditions become a pathway to permanent entrenchment.
- **Ballot/question manipulation**: compound questions, misleading wording, or asymmetric information.
- **Capture via money / influence**: opaque funding and undisclosed conflicts dominate constitutional design.
- **Rights backsliding**: formal amendment used to hollow out effective remedy, oversight, or minority protections.
- **Implementation mismatch**: amendment passes without mapping to mandates, budgets, services, and remedy continuity.

---

## 2) MVCCD pipeline (what must be joinable)

### A) Inventory: the top-tier rule must be findable
- The constitution/charter MUST exist in the **Public Rules Register** (`39-...`) as a PRR entry (portable kind: `CONSTITUTION` or `CHARTER`; see updates in `39-...`).
- The PRR entry MUST support **as-of queries** (effective dates; amendment lineage) and point to the authoritative publication bundle (`REL-*`) (see `53-...`, `51-...`).

### B) Proposal bundle (`REL-*`)
Every proposed change MUST publish a **proposal release** (`REL-*`) containing, at minimum:
- **Baseline reference:** the “as-of” instrument (`RULE-*` / PRR entry version) being changed.
- **Proposed text:** full proposed text + a machine-readable diff against baseline.
- **Plain-language explanation:** what changes, who is affected, and what stays the same.
- **Accessibility/comprehension:** voter-facing materials MUST meet the `98-persons-path-and-accessibility-invariants.md` comprehension test (in-language; disability access) and include an offline/phone path and a no-wrong-door dispute intake.
- **Implementation map:** affected mandates (`34-...`), services (`47-...`), transfers (`35-...`), contracts/assets if relevant (`38-...`, `48-...`).
- **Integrity disclosures:** relevant influence interactions and conflicts (`46-...`).

### C) Eligibility + clarity decisions (`DRR-*`, typically `DRR-TYPE: INTEGRITY`)
Before a change can proceed to ratification (referendum or supermajority vote), the administering forum MUST emit a joinable decision record covering:
- **Single-subject / anti-logrolling check** (or the jurisdiction’s equivalent).
- **Clarity / neutrality review** for any ballot question or summary.
- **Rights-floor review** (at least: does this touch remedy/oversight/equality protections?).
- **Emergency-window test**: if emergency powers are active, either forbid constitutional change or require heightened thresholds + cooling-off (link `EMR-*` where relevant).

### D) Ratification as verifiable publication
- Ratification outcomes (votes, quorum rules, certification, recount/audit if applicable) MUST publish as `REL-*` with methods + correction lanes (`51-...`, `53-...`).
- Disputes MUST be time-bounded and discoverable via `AL-*` (see `36-...`).

### E) Promulgation + incorporation discipline
- When adopted, promulgation MUST publish an **incorporation release** (`REL-*`) that:
  - links baseline, proposal, and final authoritative text,
  - records effective dates and any phased commencement,
  - and updates the PRR entry lineage (no “silent edit” merges).

---

## 3) One-screen Constitutional Change Docket (attach to key `DRR-*`)
Use this docket as the minimal, portable integrity record for constitutional/charter change gating.

```yaml
DRR-ID: DRR-____
DRR-KIND: DEC
DRR-TYPE: INTEGRITY
SUBJECT: CONSTITUTIONAL-CHANGE   # or CHARTER-CHANGE / TOP-TIER-COMPACT
BASELINE: RULE-____  # or PRR entry/version
PROPOSAL: REL-____   # proposal bundle (text + diff + explanation + implementation map)
BALLOT-PACK: REL-____  # question text, translations, voter info pack (if applicable)
CHECKS:
  single_subject: (PASS/FAIL/NA)
  clarity_neutrality: (PASS/FAIL/NA)
  rights_floor: (PASS/FAIL/NA)
  emergency_window: (PASS/FAIL/NA)  # link EMR if not NA
INFLUENCE_JOINS: [INF-____, INT-____]  # only what applies
RATIFICATION_PATH: (supermajority vote | referendum | mixed)
APPEAL_LANES: [AL-____]  # pre-vote and post-vote lanes
EFFECTIVE_DATE: YYYY-MM-DD
REVIEW: (date/trigger; required post-implementation review if major)
LINKS: [PRR-ENTRY, REL-____, OFR-____]  # only what applies
```

---

## 4) Minimal hard rules (tight, high leverage)
- **Cooling-off for high-impact change:** require a minimum publication window between proposal release and ratification (longer if rights/oversight/remedy are altered).
- **No quorum traps:** avoid turnout quorums that incentivize strategic abstention; prefer supermajority thresholds if needed ([BIB-VENICE-REFERENDUMS-2007]).
- **Neutral information baseline:** publish a voter information pack as `REL-*` with sources, assumptions, and a correction lane (`37-...`, `51-...`).
- **Ballot pack accessibility:** if the voter information pack cannot be accessed in practice (language/disability/offline constraints), pause the ratification timeline until an accessible pack exists; treat “published but unusable” as legitimacy failure.
- **Finance legibility:** campaign finance and lobbying related to the change MUST be joinable via `INF/INT` and any enforcement actions should link to `OFR-*` (`46-...`, `55-...`).
- **Rights backstop:** changes that weaken remedy, oversight, or equality protections SHOULD trigger heightened procedural safeguards (multiple legitimacy generators; see `21-...`).

---

## 5) Scope notes (micro-local → global)
- **Micro-local / municipal charters:** apply the same release + docket discipline, even when “constitution” is a charter/bylaw.
- **Supranational/global treaties:** treat ratification/withdrawal/derogations as top-tier changes: inventory in PRR where enforceable, publish releases, and maintain appeal/oversight joins (`50-...`, `60-...`).
