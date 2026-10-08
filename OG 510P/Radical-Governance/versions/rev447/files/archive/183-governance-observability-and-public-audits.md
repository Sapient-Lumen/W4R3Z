# Governance Observability & Public Audits (Making Power Legible)

**Goal:** make governance *inspectable* by default: a citizen, journalist, auditor, or opposition party should be able to answer “what happened, who decided, who benefited, and did it work?” without insider access.

Observability is how you prevent:
- quiet capture
- capability rot
- epistemic drift (“we’re doing great” with no evidence)
- legitimacy collapse caused by opacity

---

## The Observability Stack (minimum viable)

### 1) Decision traces (why + who)
Publish:
- the decision object (policy, procurement, enforcement rule, standard)
- the deliberation summary (arguments + evidence + dissent)
- the authority chain (who had standing; who signed; appeal path)
- a “change log” for amendments

This is compatible with election integrity norms emphasizing transparency, stability of rules, and credible dispute resolution. [^venice]

### 2) Money traces (from budget → outcomes)
For any major program:
- budget allocation → contracts → payments → deliverables
- variance + change orders + exceptions
Open contracting disclosures are a practical anchor for this layer. [^ocds]

### 3) Performance traces (did it work?)
- pre-registered objectives + leading indicators
- independent evaluation cadence
- “stop / pivot / scale” gates

### 4) Integrity traces (influence + conflicts)
- conflicts-of-interest register
- lobbying / influence disclosures
- enforcement actions + outcomes

OECD integrity guidance treats these disclosures as core anti-corruption infrastructure. [^oecd_integrity]

---

## Public audit lanes (two-track)

### A) Routine audit (scheduled)
- annual financial audit
- program effectiveness reviews on a rolling cycle
- compliance audits for high-risk areas (procurement, enforcement)

### B) Triggered audit (event-driven)
Triggers:
- threshold overruns (cost, time, harm)
- anomaly detection (outliers vs peers)
- credible whistleblower submissions
- petition threshold (citizen or council)
- randomized spot checks (anti-gaming)

Triggered audits should have **independence guarantees** (budget protection + appointment rules) and **publication defaults** (redactions must be justified).

---

## Design rules that prevent “audit theater”

- **publish raw-ish data + methods**, not only glossy summaries
- **counterfactual discipline:** compare to baselines, peers, or pre-specified targets
- **disaggregate outcomes** (who benefited; who bore costs)
- **audit the auditors** (quality checks + conflict rules)
- **close the loop:** audits must generate remediation obligations with deadlines

---

## Minimal artifact set (what to publish)

For each governing node:

1. **Public dashboard:** service availability, outcomes, finances, complaints, response times
2. **Registers:** authorities, programs, contracts, incidents, enforcement, conflicts, influence
3. **Evidence library:** evaluation reports, datasets, methodology notes
4. **Appeals log:** disputes and resolutions (with privacy redactions)

---

## References

[^ocds]: Open Contracting Data Standard (OCDS) – publishes data and documents across the full contracting cycle. https://standard.open-contracting.org/  
[^oecd_integrity]: OECD Recommendation on Public Integrity (2017) + handbook guidance. https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0435  
[^venice]: Venice Commission, *Code of Good Practice in Electoral Matters* (2002). https://rm.coe.int/090000168092af01
