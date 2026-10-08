# Whistleblowing & Protected Disclosures (Make Integrity Speakable)

**Merge relation:** broad safety-and-integrity framing memo. For the tighter implementation-facing protected-disclosure interface, pair this with `121-whistleblowing-and-protected-disclosure.md`; use `121` as the canonical starting point when you need concrete rails, and return here when you need the wider organizational and anti-retaliation frame.


**Purpose:** protect disclosures so insiders can surface wrongdoing without sacrificing their lives or livelihoods.

**Person served:** A worker who sees wrongdoing and fears retaliation, who needs safe disclosure channels and protection that actually holds.

**From-below:** This protects people who speak up so wrongdoing can surface without retaliation or career destruction.

**EXP pointer:** addresses `EXP-05` (Fear) and `EXP-07` (Indifference) by making reporting safe and consequence-bearing (see `98-persons-path-and-accessibility-invariants.md`).

**Material floor (one sentence):** assumes MVF staffing and assisted/offline access; in degraded mode, preserve salvage‑core obligations: receipting, time bounds, and continuity of records. (See `07` MVF; `80` Phase −1; `98`; `31`; `101-claude-rev142-normative-requirements.md` (NR-13).)
**Assistance & representation:** publish staffed/oral/offline paths (incl. interpretation) and who can act on behalf of someone (advocate/authorized representative); allow third‑party/collective filing where harms are collective or the person can’t safely file; disclose conflict/consent rules (see `98`, `36`, `47`, `41`; `101-claude-rev142-normative-requirements.md` (NR-12, NR-17)).
**Authority:** disclosure owners must be independent enough to investigate and trigger binding remedies (discipline/contract action/referral) and route to enforceable `AL-*` lanes (`36`). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-09).)
**Retaliation safety:** core—confidential channels, interim protections, and retaliation monitoring/remedy; include at least one degraded/offline safe channel (no personal device required) and publish a privacy‑safe chilling indicator (`03` IPM‑4); treat retaliation as its own violation with consequences. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed, a timely challenge is pending, or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)
**Proof burdens:** whistleblowers need only a good‑faith, minimally specified report; agencies bear the burden to investigate and to prove non‑retaliation; evidentiary demands must be least‑burdensome and receipted (`44`, `03`, `36`). (See `101-claude-rev142-normative-requirements.md` (NR-06).)
**Join constraints:** cross‑scope joins/IDs/data sharing MUST name an empowered use‑path + corrective action (per `70`), stay purpose‑limited/minimized, and provide a narrow fallback when joins are unsafe or missing (prefer person‑portable receipts/reference numbers). (See `70-interoperability.md`; `101-claude-rev142-normative-requirements.md` (NR-14).)


Capture and corruption persist when insiders and affected parties cannot report wrongdoing safely. “Hotlines” fail when the channel is controlled by the implicated unit, cases disappear into HR, or retaliation is handled informally.

This memo defines a minimal **Protected Disclosure System** that plugs into existing joinable artifacts (`AL/DRR/OFR/REL/RC`) and the secrecy exception discipline (`77-...`) without creating a new institution tier.

**Scope note (governed-person fear):** this memo focuses on *insider* protected disclosures. The more common experience is the governed person who fears retaliation for using remedy/appeal lanes; that interface obligation is specified in `08-remedy-and-grievance.md`, `36-appeal-lanes-and-redress-registry.md`, and `98-persons-path-and-accessibility-invariants.md` and should be monitored via `03-metrics-and-evidence.md` [LRR-14]. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Anchor set:** [BIB-UNCAC] (Art. 33), [BIB-EU-WHISTLE-2019], [BIB-COE-WHISTLE-2014], [BIB-UNODC-REPORTINGPERSONS-2015], [BIB-OECD-WHISTLE-2016], [BIB-ISO-37002].

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Oversight findings + response register: `55-...`.
- Records custody and publication integrity for allegations/outcomes: `31-...`, `53-...`.
- Person-facing safety/access (non-digital options): `98-persons-path-and-accessibility-invariants.md`.
- Retaliation/chilling monitoring (metrics discipline): `03-...`.
- Threat framing: retaliation/fear collapses reporting even when formal channels exist (see [TM-29]), and “hotline theater” is legibility without consequences (see [TM-33]).

## Named tensions (design must surface these)
- Anonymity/protection vs due process for the accused.
- Disclosure for accountability vs safety risk to whistleblowers and third parties.
- Broad intake channels vs malicious/strategic allegations.
- Transparency of outcomes vs confidentiality needed for participation.

---
## A. Minimum viable protected disclosure system (MVPDS)

1) **Coverage (who can report)**
- MUST: employees, contractors, vendors, grantees, and service users where relevant (not only “employees”).
- MUST: protection applies to *attempts* to report (chilling is the harm).

2) **Channels (plural + independent)**
- MUST: at least **two** channels:
 - an internal channel (for routine issues), and
 - an **independent** channel (ombuds/IG/audit-style function) that can bypass the implicated chain.
- SHOULD: allow confidential reporting; anonymous reporting where feasible (with anti-abuse controls).

3) **Triage with written outcomes**
- MUST: intake classification produces a typed receipt (`DRR-TYPE: INTEGRITY-INTAKE`) with:
 - a stable case ID,
 - an initial routing decision (investigate / refer / close),
 - a reason code (`RC-*`) and the applicable lane (`AL-*`) for challenge.
- MUST: publish the triage rule (finite categories + timelines).

4) **Independent investigation (or referral)**
- MUST: conflicts-of-interest test for investigators; ability to refer to external bodies when implicated.
- MUST: time-boxed milestones; “no-response” is not allowed (treat as `AO-NORESP` defects when applicable).

5) **Anti-retaliation: prevention + remedy**
 (This is the core hazard named in [TM-29].)
- MUST: clear list of prohibited retaliatory acts (formal and informal).
- MUST: interim protections available (schedule change, reassignment, pay protection, no-contact orders, etc.).
- MUST: retaliation determinations issue a joinable receipt (`DRR-TYPE: INTEGRITY-RETALIATION`) with reasons (`RC-*`) and remedies/discipline where applicable.
- SHOULD: burden-shifting / evidentiary presumptions where legally feasible (to avoid “prove intent” traps).

6) **Due process and anti-chilling safeguards**
- MUST: accused parties receive fair process; malicious reporting can be sanctioned **only** with a high bar and typed reasons (avoid chilling).
- MUST: confidentiality/secrecy exceptions are logged as withholding receipts (`77-...`) rather than used to bury existence.

---

## B. How it plugs into the archive (joinable artifacts)

**Required joins**
- `AL-*` lanes: at least one lane for protected disclosures and one for retaliation challenge/remedy (defined in `36-...`).
- `DRR-*` receipts: intake, routing, retaliation findings, and closure outcomes (typed; cite `RC-*`).
- `REL-*` releases: quarterly/annual stats + method note and (where safe) redacted exemplars.
- `OFR-*` cases: recurring patterns (repeat offender units, retaliation spikes, chronic non-response) trigger systemic oversight files with follow-through (`55-...`, `76-...`).

**Where to register**
- AL lane(s) in `36-appeal-lanes-and-redress-registry.md`
- oversight follow-through in `55-oversight-findings-and-response-register.md`
- integrity controls in `22-public-integrity-and-procurement.md` and `79-...`

---

## C. Failure modes → smallest countermeasure

- **“Hotline theater” (channel exists, nothing happens):** require published triage categories + time-boxed milestones + `AO-NORESP` defect logging (see [TM-33]).
- **HR capture / conflicts in investigations:** independent channel + COI test; escalate to an external authority when implicated.
- **Retaliation hidden as “performance” or “reorg”:** treat retaliation as its own case type; publish retaliation incidence and remedy outcomes (disaggregated by unit).
- **NDA / secrecy misuse:** require withholding receipts and review dates (`77-...`); publish existence metadata even when payload is withheld.

---

## D. Minimal metrics (tie to `03-...`)

Use [IPM-4] as the pack anchor; keep the public set ≤6:
- disclosure volume + channel mix (internal vs independent) and time-to-triage (median/90p)
- time-to-first-action and time-to-closure by category
- substantiation / referral rate (interpreted cautiously)
- retaliation incidence and remedy/discipline outcomes (including **post‑filing adverse‑action uplift** vs baseline where measurable)
- `AO-NORESP` / missed-deadline defect rate for the disclosure lane(s)
- recurrence rate after systemic `OFR-*` closure (tie to [LRR-12])
