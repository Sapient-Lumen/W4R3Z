# Public Health Preparedness & Response Rails

**Merge relation:** artifact-led preparedness/response operating pack. Use `57-public-health-and-biosecurity-governance.md` as the canonical public-health governance front door; use this memo when you need the tighter preparedness/response register-and-ledger layer.


**Purpose:** Make public health powers **fast enough to save lives** and **bounded enough to prevent abuse**, with receipts that let the public verify decisions without turning every crisis into a legitimacy collapse.

**Scope:** Applies to routine health protection (surveillance, prevention, vaccination, food/water safety) and crisis response (outbreaks, pandemics, biothreats, cross‑border events).

**Design stance:** Public health is a *high-uncertainty, high-externality* domain. The governance answer is **pre-committed triggers + transparent decision artifacts + equity and rights constraints**.

---

## A. Minimum viable artifact set (MV-PH)

### PH-01. Health Threat Register (HTR)
A public register of monitored hazards.

**Fields (minimum):**
- Threat ID; category (infectious / environmental / foodborne / occupational / other)
- Monitoring sources; reporting cadence
- Baseline indicators + thresholds (see PH-02)
- Responsible unit + cross-jurisdiction links (`221-jurisdiction-graph-and-authority-routing.md`)

### PH-02. Trigger & Threshold Pack (TTP)
Pre-committed triggers for escalation/de-escalation.

**Rules:**
- Thresholds must be versioned (Change Receipts) and justified with uncertainty bounds.
- Triggers must include **equity-sensitive** measures (disparate impact early warnings).

### PH-03. Health Advisory & Orders Ledger (HAOL)
A log of advisories, orders, and restrictions.

**Each entry includes:**
- Order/Advisory ID; legal authority; effective window; jurisdiction scope
- Intended mechanism (why it works) + evidence basis
- Rights impact summary + mitigation (least restrictive alternative test)
- Exemptions policy + appeal/redress path (no silent waivers)

### PH-04. Evidence Packet Receipt (EPR‑PH)
A short, publishable packet attached to PH-03 actions.

**Must include:**
- What is known / unknown; key uncertainties
- Expected benefit + harm; distributional impact
- Alternative options considered and why rejected
- Monitoring plan: which metrics will decide continuation

(See `133-evaluation-and-learning-integrity.md` and `214-evaluation-learning-agendas-and-evidence-governance-rails.md`.)

### PH-05. Resource Allocation & Scarcity Protocol (RASP)
When resources are scarce (beds, antivirals, vaccines, PPE):

**Requirements:**
- Queue cards and prioritization rules (`140-queues-and-prioritization-integrity.md`)
- Public criteria + override receipts + audit trail
- Anti‑fraud and anti‑capture measures (e.g., vendor performance ledger; see `179-open-contracting-and-procurement-rails.md`)

### PH-06. Cross‑jurisdiction Coordination Compact (CJCC)
Pre-negotiated compacts for cross-border or multi‑region outbreaks.

**Includes:**
- Mutual aid, stockpile sharing, lab surge, staffing surge
- Data sharing interface + purpose limitation (`127-data-governance-and-privacy-interfaces.md`)
- Seam continuity: no “jurisdiction ping‑pong” for people seeking care

(See `154-critical-infrastructure-resilience-compacts.md` and `230-conflict-of-laws-and-cross-border-dispute-rails.md`.)

### PH-07. Public Communications & Correction Discipline (PCCD)
Crisis comms is a core governance function.

**Must include:**
- Claim register: what is asserted, what evidence supports it
- Correction propagation protocol (don’t bury updates)
- Acknowledgement of uncertainty (with ranges)

(See `129-public-sphere-and-epistemic-infrastructure.md`.)

---

## B. Guardrails that prevent emergency abuse

### B1. Emergency powers must pass Four Locks
If emergency authority is invoked, require:
1) **Authority lock:** explicit legal basis + scope/time bounds
2) **Evidence lock:** EPR‑PH attached (publishable)
3) **Oversight lock:** independent review lane with access
4) **Sunset lock:** automatic expiry + renewal requires justification

(See `112-exception-control-and-emergency-powers.md` and `186-emergency-powers-derogations-and-sunset-discipline.md`.)

### B2. Least restrictive alternative test
For restrictions on movement/assembly/economic activity:
- show why less restrictive measures fail
- specify objective de-escalation triggers (PH-02)
- publish a review cadence

### B3. Equity + accessibility invariants
Actions must include:
- language access and accessibility plan
- non-digital alternative access path
- targeted mitigations for groups bearing disproportionate burdens

(See `98-persons-path-and-accessibility-invariants.md` and `209-equal-protection-accessibility-and-language-access-rails.md`.)

---

## C. Observability & accountability

### C1. Outcome dashboards that can’t be gamed
- Publish Metric Cards and use receipts (`142-metrics-and-indicators-integrity.md`)
- Separate *leading* indicators (early signals) from *lagging* outcomes
- Publish revision history; never silently re-base

### C2. Independent serious‑harm lane
When coercion is used (forced isolation, policing support, detention for quarantine):
- force event receipts, independent investigation lane, and remedy path

(See `116-coercion-use-of-force-and-detention-governance.md` and `233-policing-and-use-of-force-governance-rails.md`.)

### C3. Post‑incident review (PIR‑PH)
For every declared public health emergency:
- publish what worked / what failed
- update PH-02 triggers + PH-06 compacts
- publish procurement and allocation lessons

---

## D. Implementation sequence (Phase 0 → 2)

**Phase 0 (30–90 days):**
- Stand up PH-03 ledger + EPR‑PH template
- Publish PH-02 triggers for the top 5 hazards
- Adopt PCCD correction discipline

**Phase 1 (3–9 months):**
- Integrate CJCC compacts with neighbors
- Implement RASP queue cards for scarcity items
- Establish independent review lane for emergency powers

**Phase 2 (9–18 months):**
- Full HTR with interoperability interfaces
- Red‑team drills with publishable exercise receipts
- Institutionalize PIR‑PH with binding update obligations

---

## External touchpoints (cite, don’t import)
- International Health Regulations (IHR) and core capacities. [BIB-WHO-IHR]
- WHO guidance on risk communication and community engagement. [BIB-WHO-RCCE]
- OECD work on health system resilience. [BIB-OECD-RESILIENCE]
- Global Health Security agenda / preparedness benchmarking. [BIB-GHSA]

