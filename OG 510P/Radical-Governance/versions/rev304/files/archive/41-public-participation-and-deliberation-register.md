# Public Participation & Deliberation Register (Stop “Participation Theatre”)

**Purpose:** prevent participation theatre by binding input to decisions (duty‑to‑respond, decision hooks, complaint lanes) with a stable public record.
**Person served:** a resident asked to participate who needs their input bound to decisions (and the process itself contestable).

**From-below:** This stops participation theater by recording who was asked, what was heard, and how it actually changed decisions.
**EXP pointer:** counters `EXP-07` (Indifference) and `EXP-08` (Invisibility) by routing patterns into rule/policy change with representation (`98-persons-path-and-accessibility-invariants.md`).
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `53`, `70`, `73`). (`101` NR-07, NR-15)

Many governance systems run *participation* as a ritual: meetings happen, input disappears, and no one can later answer **what decision it changed**.

This memo makes participation **joinable** and **contestable** by treating each participation process as a first-class public object with a stable ID.

**Core claim:** participation becomes legitimate when (a) it has a **decision hook**, (b) it has a **duty-to-respond**, and (c) complaints about the process itself have a clear lane.

**Boundary note (why this matters beyond individual appeals):** individual remedy corrects errors; participation is where communities contest and change rules/policies that produce harm even when correctly applied. The point of joinable receipts, reasons, and systemic redress is to make those patterns visible and route them into legitimate rule‑change processes (`76-...`, `28-...`). (See `101-claude-rev142-normative-requirements.md` (NR-11).)

For representative deliberation (assemblies/juries/mini‑publics) commissioning invariants, see `88-deliberative-institutions-and-sortition.md`.

Anchors: OECD citizen participation design guidance and evaluation guidance; plus IAP2 Core Values (practice baseline). See [BIB-OECD-CITPART-2022], [BIB-OECD-DEL-EVAL-2021], [BIB-IAP2-COREVALUES].

---

## Kernel anchors (do not repeat)
- **Person-facing access:** `98-persons-path-and-accessibility-invariants.md` (no digital-only gate; safety; assisted access).
- **Remedy + duty-to-respond:** `08-remedy-and-grievance.md`, `36-...` (engagement must connect to an accountable response path).
- **Institutional forms:** `88-deliberative-institutions-and-sortition.md` (functional equivalents; legitimacy constraints).
- **Records + publication:** `31-records-foi-and-government-memory.md`, `51-...` (public record of inputs and responses).
- **Protective legibility:** `99-protective-legibility-and-adoption-dynamics.md` (participation can be weaponized).

## Named tensions (design must surface these)
- **Inclusion vs capture:** open forums can be dominated; design representativeness and guardrails.
- **Transparency vs safety:** public testimony can trigger retaliation; provide protected channels.
- **Scale vs depth:** mass comment ≠ deliberation; match method to decision class.
- **Voice vs authority:** participation must not be theater; publish what changed and why (or why not).

## 1) The object: `ENG-*` (an engagement / deliberation process)

An `ENG` object is any structured process that invites the public to inform, co-design, prioritize, or review public decisions, including:
- consultations, hearings, and open meetings
- participatory budgeting
- representative deliberative processes (citizens’ assemblies/juries, civic lotteries)
- citizen science / civic monitoring / open innovation

(These categories mirror OECD guidance on participation methods. See [BIB-OECD-CITPART-2022].)

**Interface rule:** If a process is intended to influence a decision, it MUST have an `ENG-*` entry.

---

## 2) Minimum anti-theatre requirements (MUST)

An `ENG-*` entry MUST include:

1) **Decision hook (what it can change)**
- The authorizing decision record (`DRR`) OR the upcoming decision(s) it will inform.
- The route: which legitimacy generator(s) this is providing (consultation, deliberative review, PB allocation).

2) **Duty-to-respond (what decision-makers owe the public)**
- A response deadline.
- The form of response: (a) accept, (b) accept in part, (c) reject with reasons, (d) defer with conditions.
- The response MUST be published as a `DRR` (or a linked decision memo that is itself indexed in records).

3) **Process contestability (complaints about the process)**
- A named complaint/appeal lane `AL-*` from the ALR (`36-...`).
- A disclosure of any facilitator/vendor and funding path (link `CON` and `TRF` where relevant).

4) **Inclusion & accessibility baseline**
- Eligibility and exclusions.
- Accessibility accommodations and compensation rules (including travel/childcare where applicable).
- **Community representation norm:** when a decision materially affects a defined community (geographic, indigenous, occupational, etc.), the process MUST specify how that community is represented (community‑nominated reps, sortition within the community, or other legitimate mechanism), not only individual submissions. (See `101-claude-rev142-normative-requirements.md` (NR-12).)
- **No digital‑only gate:** if online tools are used, provide at least one staffed/non‑digital path (in‑person/phone/paper) and do not require proprietary apps for participation in rights‑salient processes. (`98-persons-path-and-accessibility-invariants.md`)

5) **Information integrity**
- The public information pack MUST be linked: key `RULE-*` constraints, relevant official releases (`REL-*`), and (where relevant) the testable claims (`CLM-*`) that are in play.

**Note:** for representative deliberative processes, evaluation criteria should follow OECD evaluation guidance (minimum quality gates). See [BIB-OECD-DEL-EVAL-2021].

---

### 2a) Participation integrity (anti‑astroturf baseline)

Online comment systems are easy to flood with bots, identity theft, and mass form letters; treat **volume** as untrusted unless input provenance is disclosed (see [BIB-PEW-FCC-COMMENTS-2017]; [BIB-STANFORD-FILTERINGBOTS-2017]; [BIB-NYAG-FAKECOMMENTS-2021]).

**MUST**
- Publish an **Input Provenance Summary** as a joinable release (`REL-*` or indexed report): counts by channel, dedupe method, share verified (where relevant), form‑letter clustering rates, and a brief fraud/bot screening method note.
- If eligibility/weighting/one‑person‑one‑input is material, disclose the assurance tier(s) and the `IDN-*` gate(s) used (risk‑tuned; do not over-collect).
- For materially influential processes, require **sponsor/organizer disclosure** for organized campaigns (or mark “undisclosed”); publish aggregate affiliation tags where lawful.
- Maintain a privacy‑preserving path for anonymous input, but label it **unverified** in the provenance summary.

**SHOULD**
- Sample‑verify a small random subset (where lawful) and publish the verification rate.
- Publish the “how input is used” policy (binding vs advisory; any weighting rules).
- If manipulation is credibly suspected, open an `OFR-*` case (`CASE-TYPE: PARTICIPATION-INTEGRITY`) and publish a corrective action `DRR` (see `32-...`).

## 3) Minimal schema (register entry)

**Version semantics (canonical):** treat this register as **append‑only** and queryable **as‑of** a date. Publish revisions with monotonic `REV`, `PUBLISHED-AT`, and (when behavior changes) `EFFECTIVE-*` timestamps—see `70-interoperability.md` §“Version semantics & ‘as‑of’ queries”.

A minimal `ENG-*` entry is a single page with a machine-readable mirror.

| Field | Meaning |
|---|---|
| `ENG-*` | stable process ID (namespaced by Unit ID) |
| Owning unit | Unit ID (competence ledger) |
| Method class | one of: info/data, open meeting, consultation, open innovation, citizen science, civic monitoring, PB, deliberative mini-public (OECD categories) |
| Decision hook | authorizing `DRR` + target decision(s) (planned `DRR` IDs if pre-issued) |
| Scope & affected publics | geography + who is materially affected |
| Community representation | if a defined community is affected, how representatives are engaged/selected |
| Timeline | announce → recruit → deliberate → publish → decision response |
| Inclusion | eligibility, exclusion grounds, accessibility/compensation |
| Selection method (if participants) | recruitment channel + representativeness goals + conflicts policy |
| Info pack | linked `RULE` (constraints), `REL` (facts), `CLM` (claims), and any `STD` incorporated |
| Outputs | report URL + `REL`/doc ID + recommendation summary tags |
| Input provenance summary | `REL-*` (or indexed report) with dedupe/verification method note + aggregate counts |
| Assurance / Sybil controls | stated assurance tier(s), eligibility checks, and any `IDN-*` gate(s) used (link from provenance note) |
| Official response | `DRR` link(s) + status (accepted/partial/rejected/deferred) |
| Process complaint lane | `AL-*` |
| Vendors/funding | `CON` (facilitation/platform) + `TRF` if funded externally |
| Privacy note | what participant data is collected; link `DPR-*` if personal data processing is material |
| Change log | revisions to scope/method/timeline and why |

---

## 4) Representative deliberative processes (extra requirements)

For deliberative mini-publics (citizens’ assemblies/juries):

- **Sampling transparency:** publish the sampling frame, stratification variables, and the refusal/attrition handling policy (publish aggregates; do not dox participants).
- **Compensation & care:** publish compensation and support (time off, childcare, accessibility) to reduce participation bias.
- **Facilitation independence:** publish facilitator selection and conflict disclosures (link `CON-*`).
- **Balanced information:** publish the evidence docket and expert input list; publish dissent where relevant.
- **Impact pathway:** in the `ENG` entry, name the specific decisions it will feed and the response deadline.

Anchors for evaluation and design checks: see [BIB-OECD-DEL] and [BIB-OECD-DEL-EVAL-2021].

---

## 5) Privacy and safety

Participation can expose people to retaliation.

- Default publication SHOULD be **aggregate** (demographics, representativeness stats, attendance rates).
- Participant identities SHOULD be protected unless there is an explicit consent basis and safety assessment.
- If personal data collection is material (rosters, contact lists, demographic forms), mint a `DPR-*` and reference it from the `ENG-*` entry.

---

## 6) Interoperability rules (join graph)

- `DRR` ↔ `ENG`: decisions that were informed by participation SHOULD cite the `ENG-*` process ID, and the `ENG-*` entry MUST link to the official response `DRR`.
- `ENG` ↔ `CON`: if the process is vendor-run (platform/facilitation/recruitment), link the `CON` (and OCID if used).
- `ENG` ↔ `AL`: process complaints must be routable; publish the lane.
- `ENG` ↔ `CLM/REL/RULE`: participation without shared facts becomes narrative conflict; make the references portable.
- `ENG` ↔ `REL` (provenance): publish a joinable provenance summary release so manipulation/deduping is contestable.

See: `70-interoperability.md` (ID types + join keys) and `31-records-foi-and-government-memory.md` (records discipline).

---

## 7) One-screen `ENG-*` skeleton (copy/paste)

ENG-ID: <UNITID-ENG-#####>
Title: <short>
Owning unit: <UNITID>
Method class: <consultation | PB | deliberative | ...>
Decision hook: DRR: <ID> ; Target decision(s): <planned DRR IDs or description>
Affected publics: <who + territory>
Timeline: <announce → recruit → sessions → publish → response>
Inclusion: <eligibility, exclusion grounds, accessibility, compensation>
Selection (if applicable): <sampling frame + representativeness goals + conflicts>
Info pack: RULE: <...> ; REL: <...> ; CLM: <...>
Input provenance summary: REL: <REL-* (dedupe/verification summary)>
Outputs: <report/doc link + tags>
Official response: DRR: <ID> (due <date>)
Process complaint lane: AL: <AL-*>
Vendors/funding: CON: <...> ; TRF: <...>
Privacy note: <what is collected> ; DPR: <DPR-* if needed>
Change log: <what changed and why>
