# Evaluation, Learning Agendas, and Evidence Governance Rails

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the institutional evidence-system anchor for evidence functions, learning agendas, annual evaluation plans, and publication guarantees; `03` is the person-facing measurement front door; `28` handles program commitments; `190` handles experimentation; `184` handles official statistics; `202` handles evidence commons and scientific integrity; `142` handles indicator governance; `37` / `51` / `53` are narrower claims/publication components.

**Purpose:** make governments *structurally unable* to run on vibes alone by requiring a durable **evidence-building system**: priority questions, evaluation plans, data access with confidentiality, and publishable results.

**Threat model:** evaluation as PR; “metric theater”; suppressed negative findings; fragmented data access; un-auditable models; harm hidden in averages; and evidence that never reaches decisions.

(Connects to: `03-metrics-and-evidence.md`, `104-governance-control-loops.md`, `107-governance-test-suite.md`, `183-governance-observability-and-public-audits.md`, `190-policy-experimentation-and-evidence-rails.md`, `185-microdata-access-and-disclosure-avoidance-rails.md`.)

---

## 1) Institutional minimum: an Evidence Function (not a team)
A serious state has an **Evidence Function** that survives administrations.

**EF-1 Roles MUST exist (named + staffed):**
- **Evaluation lead** (own: evaluation portfolio, standards, publication)
- **Statistics/data protection lead** (own: confidentiality rules, safe access)
- **Learning agenda steward** (own: priority questions + decision integration)
- **Program owners** (own: implementation + measurement hooks)

**EF-2 Independence rails:** evaluators must be able to publish findings without program veto. Programs can append a response memo, not suppress results.

**EF-3 Resourcing rule:** a bounded share of program spend SHOULD be earmarked for monitoring + evaluation (with a floor for high-stakes/coercive programs).

---

## 2) The Learning Agenda (questions first)
A **Learning Agenda** is a public list of the priority questions the government commits to answer.

**LA-1 Each question MUST specify:**
- decision that will change if answered (what it will unlock)
- primary affected groups (benefits/burdens)
- owner (accountable official)
- evidence method target (e.g., quasi-experimental, RCT, audit, qualitative)
- time horizon

**LA-2 Renewal cadence:** renew at least annually; major administrations SHOULD publish a refreshed agenda within 120 days.

**LA-3 “No orphan questions”:** if a question is in the agenda, it MUST be attached to a budget line + evaluation slot.

---

## 3) Evaluation Plan (portfolio, not one-offs)
An **Annual Evaluation Plan** is the executable set of evaluations aligned to the learning agenda.

**EP-1 Portfolio balance:**
- a) **impact** (what changed)
- b) **implementation fidelity** (did we do what we said)
- c) **distribution & equity** (who benefits, who pays)
- d) **cost + cost-effectiveness**

**EP-2 Pre-commitment:** publish the plan, including intended designs and publication dates.

**EP-3 Negative results are first-class:** “no effect” outcomes MUST be published with the same visibility as “wins”.

---

## 4) Evidence-to-decision join rails
Evidence is governance only if it binds decisions.

**JD-1 Decision memo requirement:** non-trivial policy changes MUST include an **Evidence Appendix**:
- what evidence exists, what’s missing
- uncertainty and transfer risks
- distributional impacts
- planned evaluation + guardrails

**JD-2 Sunset / review hook:** every major program MUST have a **review date** tied to the evaluation plan (renew / reshape / sunset).

**JD-3 Rebuttable presumption:** if no credible evaluation exists after a reasonable period, continuation requires an explicit waiver with reasons.

---

## 5) Data access + confidentiality rails (make learning possible without privacy collapse)

**DG-1 Default: safe access, not “no access.”** Build governed lanes for researchers/auditors (see `185`).

**DG-2 Minimal lanes (choose by risk):**
- open aggregates (public dashboards)
- restricted microdata (secure environment)
- synthetic/test data for tooling

**DG-3 “Traceable joins”:** when linking datasets, log purpose, authority, retention, and disclosure review.

**DG-4 Confidentiality is a service:** disclosure avoidance / privacy controls MUST have published methods and independent review.

---

## 6) Ethics rails for policy experiments

**ET-1 Independent review:** interventions affecting rights, access, or coercion require IRB-equivalent review.

**ET-2 No-randomize-harm rule:** if substantial harm is plausible, do not randomize; use safer designs (stepped-wedge, phased rollout with guardrails).

**ET-3 Redress:** participants and affected groups must have a grievance + remedy path (`08`, `76`).

---

## 7) Publication, replication, and auditability

**PR-1 Publication guarantee:** publish methods + results on a schedule, with exceptions narrowly defined (personal data, safety, classified details).

**PR-2 Reproducibility pack (when feasible):**
- code + parameter logs
- data dictionaries + lineage
- versioned definitions of outcomes

**PR-3 Evaluation-of-evaluation:** periodically audit the evaluation system itself (coverage, bias, time-to-publication, stakeholder trust).

---

## 8) Minimal governance tests
Add/expect these in `107-governance-test-suite.md`:
- **T?.? Learning agenda exists:** public priority questions, owners, dates.
- **T?.? Evaluation plan exists:** mapped to agenda + budget.
- **T?.? Publishability:** negative findings publishable without program veto.
- **T?.? Evidence-to-decision hook:** major changes carry an evidence appendix.

---

## References (external)
- OECD Recommendation of the Council on Public Policy Evaluation (2022) (legal instrument landing page): https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0478
- OECD Implementation Toolkit for the Recommendation (landing page): https://www.oecd.org/en/publications/2025/02/implementation-toolkit-for-the-oecd-recommendation-on-public-policy-evaluation_f24516be.html
- U.S. Evidence Act summary and agency evidence plan structure (evaluation.gov): https://www.evaluation.gov/evidence-plans/summary/
- Office of Evaluation Sciences (GSA) toolkits (learning agendas, evaluation plans): https://oes.gsa.gov/toolkits/
- UK HM Treasury: The Magenta Book (evaluation guidance landing page): https://www.gov.uk/government/publications/the-magenta-book
- J-PAL practical guide: Ethical conduct of randomized evaluations: https://www.povertyactionlab.org/resource/ethical-conduct-randomized-evaluations
