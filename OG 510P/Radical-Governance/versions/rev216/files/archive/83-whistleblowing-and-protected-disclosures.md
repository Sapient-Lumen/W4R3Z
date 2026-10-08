# Whistleblowing & Protected Disclosures (Make Integrity Speakable)

**Purpose:** protect disclosures so insiders can surface wrongdoing without sacrificing their lives or livelihoods.

Capture and corruption persist when insiders and affected parties cannot report wrongdoing safely. “Hotlines” fail when the channel is controlled by the implicated unit, cases disappear into HR, or retaliation is handled informally.

This memo defines a minimal **Protected Disclosure System** that plugs into existing joinable artifacts (`AL/DRR/OFR/REL/RC`) and the secrecy exception discipline (`77-...`) without creating a new institution tier.

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
