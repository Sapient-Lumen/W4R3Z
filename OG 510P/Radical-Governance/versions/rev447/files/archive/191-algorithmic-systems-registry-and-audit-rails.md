# Algorithmic Systems Registry & Audit Rails

**Purpose:** ensure any algorithmic system used in public authority is **discoverable, contestable, monitored, and recallable**.

**Threat model:** invisible decision systems, unbounded discretion via “models”, proxy discrimination, silent model drift, procurement capture, and “no one can explain it”.

(Connects to: `06-digital-and-algorithmic-governance.md`, `152-algorithmic-impact-assessment-and-public-ai-governance.md`, `179-open-contracting-and-procurement-rails.md`, `183-governance-observability-and-public-audits.md`.)

---

## Minimum viable registry (public index)
Every algorithmic system affecting rights, benefits, obligations, eligibility, prioritization, enforcement, or surveillance MUST appear in a registry with:

- **system name** + owning agency + accountable officer
- **decision surface:** what decisions it influences (and what it does *not*)
- **inputs:** data sources, collection basis, update cadence
- **model class:** rules, scoring, ML, LLM, ensemble; version identifier
- **human role:** where humans can override; override logging
- **appeals & redress path:** how a person challenges outcomes (`08-remedy-and-grievance.md`)
- **monitoring:** key performance + harm metrics; drift detection; incident criteria
- **procurement:** vendor(s), contract IDs, evaluation independence
- **impact assessment:** link to AIA + mitigation plan
- **sunset/review date:** forced re-authorization cadence

**Rule:** “Not in the registry” means “not allowed in production.”

---

## Transparency tiers (don’t pretend everything is open)
Choose the strongest tier compatible with security and abuse prevention:

1. **Public explanation tier:** plain-language rationale, known limitations, appeal path
2. **Qualified access tier:** auditors and approved researchers can inspect data/model artifacts
3. **Secure enclave tier:** high-risk systems audited in controlled environments
4. **Redacted tier:** minimal disclosure only when disclosure would materially increase harm

**Always required:** an accountable official and an appeal path.

---

## Audit rails (continuous, not annual theater)
### Pre-deployment
- threat model + misuse analysis
- dataset provenance + legality
- bias and error profiling on relevant subgroups
- “human override” and explanation UX testing
- rollback plan + incident playbook

### In-production
- drift monitoring + alert thresholds
- periodic re-evaluation against baseline
- incident logging and external reporting
- sampling-based case audits (“mystery shopper” for algorithms)

### Post-incident
- containment + rollback
- root cause analysis (technical + organizational)
- public postmortem (with redactions only when strictly necessary)

---

## Safety constraints for high-stakes uses
- **No sole-automated denial** of essential benefits/services without review.
- **Right to reasons:** a person can obtain a meaningful explanation in time to act.
- **Adversarial resilience:** systems must be evaluated against manipulation and gaming.
- **Procurement separation:** vendor cannot be sole validator; independent evaluation is required.

---

## Governance tests to add
- **T?.? Registry completeness:** any rights-impacting system is registered with required fields.
- **T?.? Contestability path:** appeals exist and are usable within time budgets.
- **T?.? Drift + incident disclosure:** monitoring exists; incidents are reportable and reviewed.

---

## References (external)
- NIST AI Risk Management Framework (AI RMF 1.0): https://www.nist.gov/itl/ai-risk-management-framework
- OECD evidence governance context (for evaluation discipline): https://www.oecd.org/en/publications/mobilising-evidence-for-good-governance_3f6f736b-en.html
