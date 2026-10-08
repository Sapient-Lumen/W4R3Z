# Policy Experimentation & Evidence Rails

**Stack relation:** use `290-evidence-statistics-and-publication-integrity-routing-guide.md` for the canonical route across the evidence / statistics / publication-integrity cluster. This memo is the experimentation and causal-learning layer; `03` is the measurement front door; `214` is the institutional evidence-system anchor; `28` handles program commitments; `184` handles official statistics; `202` handles evidence commons; `142` handles indicator governance; `37` / `51` / `53` are narrower claims/publication components.

**Purpose:** make policy change **testable, reversible, and legible**—so we learn fast without gambling on people.

**Threat model:** ideology masquerading as evidence, pilot “success theater”, vendor-driven evaluation, harm hidden in averages, and reforms that can’t be unwound.

(Connects to: `03-metrics-and-evidence.md`, `104-governance-control-loops.md`, `108-service-standards-and-time-budgets.md`, `183-governance-observability-and-public-audits.md`.)

---

## Core commitments
1. **Every change has a measurable claim.** A policy proposal MUST state:
 - intended outcome(s) (who benefits)
 - plausible failure modes (who may be harmed)
 - measurement plan (what, when, by whom)
2. **Default to reversibility.** Prefer designs that can be rolled back without cliff effects.
3. **Heterogeneity is first-class.** Report effects by subgroup, geography, and service pathway—not just global means.
4. **Evidence governance is governance.** Who can publish? who can block publication? who owns the data? are part of the design.

---

## Evidence ladder (choose the least-cost rigorous method)
Use the lightest method that can credibly answer the claim:

- **Operational metrics**: service SLOs, queue times, error rates (fast, cheap; can mislead)
- **Natural experiments / quasi-experimental**: diff-in-diff, regression discontinuity (good when randomization infeasible)
- **Randomized evaluations**: when feasible and ethical (strongest causal attribution)
- **Mechanism checks**: qualitative + process tracing to ensure the “why” is true

**Rule:** the stronger the coercion / stakes, the higher the evidentiary bar.

---

## Experiment design checklist (minimum viable rigor)
A policy experiment charter MUST include:

- **Unit of assignment** (person, school, clinic, neighborhood) and spillover plan
- **Primary outcome(s)** and *one* primary time horizon
- **Guardrail metrics** (harm indicators) with thresholds
- **Pre-analysis plan** (or rationale for not pre-registering)
- **Stop / pause / rollback triggers** (“kill-switches”)
- **Fairness and distribution plan** (who bears burdens vs benefits)
- **Data governance** (collection, retention, access, audit)
- **Publication commitment** (results are published even if negative)

---

## Ethics and legitimacy rails
- **Consent and transparency:** if consent is not possible, justification MUST be explicit and contestable.
- **Independent review:** use IRB-equivalent review for human-subject risk and coercive interventions.
- **No “randomize harm”:** if substantial harm is plausible, randomization is disallowed; use stepped-wedge or observational learning.
- **Compensation & redress:** participants and affected groups must have a grievance path (`08-remedy-and-grievance.md`).

---

## The “What Works” registry (small, practical)
Maintain a public registry of evaluated interventions with:

- claim (what it tries to do)
- context (where/for whom it was tested)
- effect size + uncertainty
- cost per outcome
- known failure modes
- implementation requirements
- portability warnings (when it stops working)

This prevents “policy amnesia” and reduces repeated failure cycles.

---

## Anti-gaming rules
- **No metric monopoly:** pair outcome metrics with *auditable* process measures.
- **No single-source evaluation:** if vendor builds the system, vendor cannot be the sole evaluator.
- **Pre-commit to publication:** stop suppression by incumbents.
- **Audit the evaluation:** evaluate the evaluators (methods, incentives, access).

---

## Governance tests to add
- **T?.? Evidence charter present:** every non-trivial change has a measurable claim + guardrails.
- **T?.? Rollback plan exists:** reversibility is explicit, with triggers.
- **T?.? Publication guarantee:** negative results are publishable by default.

---

## References (external)
- OECD work on evidence-informed policy-making: https://www.oecd.org/en/publications/building-capacity-for-evidence-informed-policy-making_86331250-en.html
- OECD “Mobilising Evidence for Good Governance”: https://www.oecd.org/en/publications/mobilising-evidence-for-good-governance_3f6f736b-en.html
- Campbell Collaboration (evidence synthesis): https://www.campbellcollaboration.org/evidence/
- J-PAL guidance on ethical conduct of randomized evaluations: https://www.povertyactionlab.org/resource/ethical-conduct-randomized-evaluations
