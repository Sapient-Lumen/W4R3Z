# Compliance and Sanctions Integrity

When enforcement power is real, it is also a prime capture surface. An “ideal” enforcement regime makes sanctions **legible, reviewable, proportionate, and reversible**—and makes non-punitive compliance the default whenever possible.

**Routing note:** this memo is the generic domestic sanction-ladder / enforcement-integrity front door. Use `326-international-sanctions-listings-countermeasures-humanitarian-exemptions-and-delisting-rails.md` when the question is specifically about international targeted sanctions, listings, humanitarian carve-outs, delisting, or countermeasure limits rather than ordinary administrative enforcement design.

This memo defines a portable **Compliance & Sanctions Integrity Protocol (CSIP)** that plugs into:
- control loops and circuit breakers (`104`, `105`)
- legitimacy/receipts (`106`)
- service clocks (`108`)
- dispute/coordination (`114`)
- information/records (`115`)
- rulemaking/versioning (`118`)
- fiscal/procurement (`110`)
- audit/inspection follow‑through (`130`)
- remedy/grievance (`08`)

References: see **[BIB-OECD-REI-2014]**, **[BIB-OECD-REI-TOOLKIT-2018]** and due-process baselines already in the docket.

---

## CSIP primitives

### 1) Sanction Ladder (SL-*)
A standardized ladder of responses from least to most coercive, tuned by domain:

1. **Notice + assistance** (education, service fix)
2. **Corrective order** (bounded requirements + time budget)
3. **Compliance agreement** (milestones + monitoring plan)
4. **Administrative penalty** (bounded, proportional, appealable)
5. **License/privilege modification** (conditions, suspension)
6. **Exclusion / debarment** (time-bounded, criteria‑based)
7. **Referral** (civil/criminal where appropriate)

**Default rule:** prefer the least coercive step that plausibly achieves compliance in time. Escalation requires a reason receipt (below) and a contest window. (OECD risk‑based enforcement principles: **[BIB-OECD-REI-2014]**.)

### 2) Case File Receipt (CFR-*)
Every enforcement action produces a joinable receipt:

- `CFR-ID` (stable pointer; joins to records in `115`)
- `SCOPE` (who/where; jurisdiction basis)
- `RULES` (rule versions implicated; join to `118`)
- `FACTS` (evidence pointers; do not “reset” on transfer; join to `109/114`)
- `RISK-TIER` (why this is prioritized; join to audit/inspections `130`)
- `DECISION` (chosen ladder rung + why lower rungs are insufficient)
- `DEADLINES` (service/time budget; join to `108`)
- `CONTEST` (how/when to challenge; join to `08/106`)
- `REVIEW` (auto‑review date and conditions; anti-permanence)

### 3) Proportionality & reversibility checks (PRC-*)
Before any rung ≥ 4 (penalty or stronger), require a short PRC:

- **Necessity:** is coercion necessary vs. assistance/correction?
- **Least-restrictive:** is there a lower rung that works?
- **Proportionality:** magnitude vs. harm, intent, repetition, ability to comply
- **Reversibility:** what restores status on compliance?
- **Collateral minimization:** avoid punishing third parties where possible

These checks must be recorded in the `CFR-*` and are contestable.

### 4) Compliance Agreement Receipt (CAR-*)
For negotiated compliance (preferred where safe):

- milestones + verification methods
- monitoring cadence + stop conditions
- consequences of failure (precommitted, bounded escalation)
- fairness safeguards (no “coercive settlement” without recourse)
- exit/transfer rule (agreement follows the person/org across seams)

### 5) Debarment/Exclusion Receipt (DERX-*)
If exclusion is used (procurement, licensing, etc.), it must be:

- time‑bounded + criteria‑based reinstatement
- published with redactions only where necessary
- automatically reviewable (no “silent indefinite bans”)

(Connects to procurement integrity `110`.)

---

## Circuit breakers for enforcement capture

Trigger automatic **pause/review** (see `105`) if any of the following hold:

- **Volume anomaly:** enforcement spikes concentrated on a class or geography without a risk justification
- **Contest suppression:** challenge rates collapse while penalties rise
- **Repeat non-compliance loop:** same parties re‑enter enforcement without service fixes (signals system failure)
- **Retaliation signal:** enforcement appears correlated with protected speech/association (`123`) or disclosures (`121`)

On trigger: require an independent review memo and publish a compact explanation.

---

## Minimum publishable metrics

- percent of cases resolved at ladder rungs 1–3 vs 4+
- median days from detection → first contact → resolution (with service clock compliance)
- contest rate and reversal rate (by rung, by cohort)
- repeat cycle rate (same issue reappears within X months)
- debarment duration distribution + reinstatement outcomes

These are “health metrics,” not targets.

---

## Implementation notes

- Align inspection findings (`130`) with enforcement case files (`CFR-*`).
- Use rule replay (`118`) to ensure enforcement references the correct rule version.
- Make transfers non‑reset (`109`, `114`): the burden to move the file is on institutions, not people.

