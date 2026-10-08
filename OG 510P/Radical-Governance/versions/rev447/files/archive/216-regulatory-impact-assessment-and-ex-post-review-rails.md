# Regulatory Impact Assessment & Ex Post Review Rails (Close the policy loop)

**Problem:** governments often “regulate and forget”: rules ship without clear hypotheses, measurement plans, or review triggers; evaluation arrives too late (or never), and negative results don’t lead to change.

**Design goal:** make every material rule a **testable, monitorable, reversible** intervention with a public evidence plan and a binding update pathway.

---

## A. Core principles

1) **Proportionality:** heavier burdens require stronger evidence and clearer review triggers.

2) **Iterative RIA:** impact assessment is not a one-off document; it updates as the proposal changes and should include plans for monitoring and evaluation. citeturn0search0

3) **Independent scrutiny:** a body with access and capability can challenge assumptions before adoption (methods, distributional effects, alternatives).

4) **Ex post is mandatory for material rules:** validation after implementation is a core part of high-quality regulatory systems. citeturn0search8turn0search12

5) **Publication by default:** decisions must be legible to non-insiders and contestable; better-regulation approaches emphasize evidence-based lawmaking and evaluation. citeturn0search2turn0search6

---

## B. Minimal artifacts

### 1) Impact Assessment Packet (`IAP-*`)
Required for any rule/program that crosses a materiality threshold (defined locally):
- **Problem statement** + scope + jurisdiction rationale
- **Theory of change / hypotheses** (what must be true for success)
- **Alternatives analysis** (including do-nothing)
- **Distributional impacts** (who benefits/pays; equity/accessibility)
- **Administrative burden** (forms, time, compliance costs)
- **Risks & failure modes** (capture, displacement, gaming, error)
- **Enforcement/compliance plan** (bounded discretion)
- **Data plan** (what data is needed; how collected; quality risks)
- **Evaluation plan** (see `EPR-*` family in `133-evaluation-and-learning-integrity.md`)
- **Sunset/review triggers** (see `SRR-*` in `122-intergenerational-and-future-protection.md`)

### 2) Review Commitment (`RCR-*`)
A small receipt published at adoption:
- review date(s)
- responsible unit
- minimum evidence set
- rollback / modification lane if harms detected

### 3) Ex Post Evaluation Record (`XER-*`)
For each review:
- outcomes vs hypotheses
- unintended effects
- distributional analysis
- implementation/administrative burden reality check
- decision: renew/modify/sunset + the change receipt

---

## C. Review cadence patterns

### Pattern 1: Default post‑implementation review
- **6–12 months:** implementation reality + early harms
- **24–36 months:** outcome evaluation + distributional impacts

### Pattern 2: Risk-triggered review
Trigger an accelerated review if any of:
- high complaint volume / appeal reversal rate
- error rate or disparate impact spikes
- major change orders / enforcement-intensity drift
- clear evidence of capture/gaming

(Join to service SLOs: `189-service-level-governance-and-redress-ops.md` and integrity tripwires: `187-public-integrity-system-blueprint.md`.)

---

## D. Binding loop closure (the part most systems lack)

A review is not “complete” until it produces one of:
1) a **renewal** with updated assumptions + next review date
2) a **modification** with a `CHG-*` packet + release note
3) a **sunset/rollback** with continuity plan for affected people

Better-regulation frameworks explicitly frame evaluation and review as essential to keeping rules fit for purpose. citeturn0search2turn0search12

---

## E. Interop hooks

- Link `IAP-*` and `RCR-*` to the public rule inventory and “as‑of” rule version pointers. (Join: `39-rulebook-and-instruments-registry.md`, `53-publication-integrity-and-tamper-evident-logs.md`.)
- Ensure the evaluation outputs (`XER-*`) join to remedy/pattern remediation when harms are detected. (Join: `76-systemic-redress-and-pattern-remediation.md`.)

---

## F. Quick checks
- Can the public state the rule’s **hypothesis** and **success metric**?
- Is there a published **review date** and evidence plan?
- When evaluation is negative, does a **binding update** happen (not just a report)?

(See `107-governance-test-suite.md`.)
