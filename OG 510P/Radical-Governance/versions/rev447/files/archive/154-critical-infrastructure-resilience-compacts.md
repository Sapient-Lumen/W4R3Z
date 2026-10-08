# Critical infrastructure resilience compacts (cross-scope)

**Problem:** Critical infrastructure (energy, water, telecoms, logistics, health systems) fails *across* jurisdictions and layers. Most governance failures here are not “lack of plans,” but:
- fragmented authority (no one owns the whole failure mode),
- underinvestment in slack / redundancy,
- opaque operator incentives and weak accountability,
- brittle mutual aid (paper agreements that don’t actually move people/equipment fast).

This note defines a **compact + operating model** that works from municipal to national to cross-border settings.

## Design goals (tight)
1. **No silent swaps:** operational responsibilities and authorities cannot change without a logged handoff (see competence ledger / mandate registry).
2. **Graceful degradation:** minimum service levels under stress are explicit and tested.
3. **Mutual aid that actually mobilizes:** pre-negotiated credentialing, liability, reimbursement, and dispatch rails.
4. **Interdependency-aware:** energy ↔ telecom ↔ water ↔ transport ↔ health dependencies are mapped and exercised.
5. **Public truthfulness:** standardized outage reporting and post-incident learning that is not captured by operators.

## Compact architecture
### 1) The Resilience Compact (RC)
A multi-party agreement among:
- operators (public + private),
- regulators / municipalities / regions,
- emergency management agencies,
- (optionally) neighboring jurisdictions.

Minimum contents:
- **Critical service inventory** (what, where, who operates it; “single points of failure”).
- **Service floors**: minimum deliverables in crisis (e.g., potable water access, emergency comms, shelter power).
- **Continuity requirements**: operators maintain business continuity and recovery plans consistent with BCMS practice (e.g., ISO 22301). [BIB-ISO-22301-2019]
- **Cyber-physical governance**: align to lifecycle governance functions for cyber risk management (NIST CSF 2.0 adds an explicit **Govern** function). [BIB-NIST-CSF-2-0]
- **Risk governance alignment**: shared risk language and responsibilities, consistent with disaster-risk governance principles (Sendai Priority 2). [BIB-UNDRR-SENDAI-2015]

### 2) Mutual-aid rail (MAR)
The RC should embed or interoperate with a **mutual-aid mechanism** that solves: *liability, reimbursement, credentialing, and legal authority*.
- US example: EMAC provides a legally binding foundation for state-to-state assistance and addresses liability/credentialing/cost terms. [BIB-EMAC-WHAT-IS]
- Cross-border analogs: regional agreements + pre-approved visa/credential fast lanes (design pattern; jurisdiction-specific).

### 3) The “Resilience Control Loop”
Make resilience governable as a loop, not a binder:
- **Sense:** live dependency map + asset health + leading indicators (e.g., maintenance backlog, staffing gaps).
- **Decide:** a small joint board (operators + public) with *clear authority* for emergency posture changes.
- **Act:** staged actions + resource dispatch via MAR; public comms playbook.
- **Learn:** after-action report with *public version* and redacted sensitive annex; tracked corrective actions.

## Implementation patterns (high leverage)
- **Stress-test cadence:** annual multi-hazard exercises + “table-top to field” escalation; include cascading failures.
- **Redundancy markets:** procure *options* for surge capacity (mobile generators, water tankers, satellite comms).
- **Transparency norms:** public outage dashboards; incident taxonomy; time-to-restore metrics (with Goodhart defenses).
- **Equity floor:** resilience spending must include distributional checks (who loses power/water first).
- **Operator incentive hygiene:** penalties for negligence *and* rewards for verified resilience investment; avoid “performative compliance.”

## Scope fit notes
- **Micro-local / municipal:** focus on community-level service floors (shelter, comms, cooling/heating) and local operator accountability.
- **Regional / state:** mutual-aid rail, bulk purchasing of surge assets, unified standards, interdependency mapping.
- **National / supranational:** cross-border coordination, supply-chain constraints, strategic reserves, shared cyber rules, large-scale exercises.

## Links to other archive pieces
- Competence ledger + mandate registry: operational authority must be legible.
- Service standards & time budgets: define “service floors.”
- Emergency governance: exception discipline, proportionality, and review.
- Industrial policy & supply-chain resilience: upstream constraints for replacement parts and skilled labor.

