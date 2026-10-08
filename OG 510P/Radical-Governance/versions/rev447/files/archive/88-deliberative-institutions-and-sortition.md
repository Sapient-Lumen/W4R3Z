# Deliberative Institutions & Sortition (Representative Public Judgement)

**Stack relation:** use `284-deliberation-stack-binding-and-legitimacy-guide.md` for the canonical route across the deliberation cluster. This memo is the institution-design / sortition-heavy specialization; `143` is the front door; `159` covers infrastructure; `111` covers binding; `224` covers process rails; `180` compares legitimacy engines.

**Purpose:** specify deliberative institutions that broaden power while remaining contestable and non-symbolic.

**Person served:** Residents asked to deliberate (and those bound by outcomes) who need deliberation that is real, inclusive, and linked to decisions.

**From-below:** This helps ordinary people participate with real power, not token consultation, by building deliberation you can trust.
**EXP pointer:** counters `EXP-08` (Invisibility) by requiring legitimate community representation in deliberative designs (`98-persons-path-and-accessibility-invariants.md`).

This memo defines **deliberative institutions** (assemblies, juries, panels, mini‑publics) as a reusable legitimacy module: they produce **public judgement** (reasons + tradeoffs) rather than raw opinion.

Use this memo alongside:
- `21-legitimacy-architecture.md` (how deliberation composes with elections/rights/courts)
- `41-public-participation-and-deliberation-register.md` (the **ENG-*** register and required fields)
- `03-metrics-and-evidence.md` + `28-program-register-and-evaluation-commitments.md` (evaluation discipline)
- OECD design evidence/principles: [BIB-OECD-DELIBWAVE-2020], [BIB-OECD-DEL]

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** transparency can be weaponized; design disclosures and incentives accordingly. (`99-protective-legibility-and-adoption-dynamics.md`)
- Participation register and non-digital access: `41-...`, `98-persons-path-and-accessibility-invariants.md`.
- Legitimacy architecture (who decides what): `21-...`.
- Records and publication integrity for deliberative outputs: `31-...`, `53-...`.

## Named tensions (design must surface these)
- Deliberative legitimacy vs elite capture and agenda control.
- Transparency of deliberation vs participant safety/harassment risk.
- Representativeness vs competence/time burdens (who can afford to serve).
- Population representativeness vs affected‑community self‑determination (sortition alone can erase collective standing). (See `101-claude-rev142-normative-requirements.md` (NR-12).)
- Advisory bodies vs binding authority (symbolism vs power).

---
## 1) When to use deliberation (a selection rule)

Trigger deliberation when **any** of the following holds:
- **Value conflict:** the dispute is about *ends* (not just means), and compromise requires shared reasoning.
- **Legitimacy deficit:** distrust/high polarisation makes “winner‑takes‑all” decisions brittle.
- **Long time-horizon:** intergenerational effects are material (see `89-intergenerational-governance-and-future-obligations.md`).
- **Hard tradeoffs under uncertainty:** experts disagree; evidence is incomplete; distributional impacts are contested.
- **Rights + policy entanglement:** the decision affects protected classes/rights boundaries and needs public reasons.

Avoid using deliberation as:
- a **stall tactic**, 
- a substitute for **remedy** (see `08-remedy-and-grievance.md`), or
- cover for a decision that is already made (“consultation theatre”).

---

## 2) Minimal design invariants (what makes it real)

A deliberative process is “real” only if it satisfies these invariants (adapted from OECD principles):
1) **Representative selection:** sortition with stratification to match the population on key dimensions; publish method. If a defined community/collective subject is materially affected, selection MUST include a legitimate community‑representation mechanism (community‑nominated reps, reserved seats, or sortition *within* the community); general‑population sortition is not a substitute. (See `101-claude-rev142-normative-requirements.md` (NR-12).)
2) **Learning phase:** participants get time + balanced briefings + the ability to question experts and stakeholders.
3) **Facilitated reasoning:** neutral facilitation; structured deliberation; time for small‑group + plenary synthesis.
4) **Transparency:** publish the charge/question, agenda, materials, conflicts of interest, outputs, and a methods appendix.
5) **Response duty:** the convening authority MUST publish a **formal response** with reasons and an implementation plan (or a justified “no”).

If any invariant is missing, treat it as a different instrument (survey, hearing, focus group) and label it accordingly in `ENG-*`.

---

## 3) Interface obligations (MVGS joinability)

Every deliberative process MUST create a single public entry in `41-...`:

- **ENG-ID:** unique ID for the process (join key)
- **Charge / decision hook:** the exact question and where it binds (or does not bind)
- **Selection receipt:** sampling frame, stratification variables, recruitment steps, exclusions, compensation
- **Evidence docket:** briefings, submissions, expert list, assumptions, “what we did not use and why”
- **Deliberation log:** session schedule + facilitation method (not verbatim transcripts unless needed)
- **Outputs:** recommendations + minority views (if any) + confidence notes
- **Government response:** adopt/modify/reject + reasons + timeline + budget reference(s)
- **Follow‑through tracker:** status updates until closure

**Reason codes:** the response SHOULD include `RC-*` reason codes and cite relevant `RULE-*` / `DRR-*` artifacts (see `52-reason-codes-registry.md`).

---

## 4) Failure modes (treat as threats)

Common failure modes map to threat models in `04-threat-models.md`:
- **Agenda capture** (TM‑8): the question is framed to pre‑select an answer.
- **Evidence capture** (TM‑6/TM‑8): briefings are unbalanced; experts are curated.
- **Representativeness collapse** (TM‑10): recruitment/retention bias; barriers to participation.
- **Tokenism** (TM‑3): no response duty; recommendations ignored without reasons.
- **Media/disinfo distortion** (TM‑7): selective leaks; participant harassment; identity targeting.

Minimum mitigations:
- independent steering group (declared COI; link `79-...`)
- published “charge + constraints” up front
- participant protection plan (privacy, safety, comms discipline)
- guaranteed response duty + follow‑through tracker

---

## 5) How deliberation composes (common patterns)

Pick one of these patterns explicitly (do not blur them):

- **Advisory with response duty (default):** assembly issues recommendations; government must respond with reasons.
- **Agenda‑setting:** assembly chooses a shortlist/options; elected body chooses among them with public reasons.
- **Co‑drafting:** assembly co‑drafts a proposal with officials/experts; final decision remains with elected body.
- **Trigger + referendum:** assembly recommends a constitutional/package change that proceeds to referendum (rare; high‑risk; ensure strong remedy lanes for rights).

---

## 6) Quick spec (commissioning checklist)

If you commission a deliberative process, the call for proposals MUST specify:
- the decision hook and non‑negotiable constraints (law, budget caps, rights floors)
- the representativeness target and sampling method
- facilitation neutrality and COI rules
- publication requirements (materials, outputs, response)
- evaluation plan (what “good” looks like; see `03-...`)
