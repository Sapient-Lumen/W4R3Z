# Digital public infrastructure (DPI) governance

**Merge relation:** shorter DPI rails/operating layer. Use `164-digital-public-infrastructure-governance.md` as the canonical architectural front door; this memo is best read as the compact implementation companion.


**Purpose:** define governance rails for *foundational digital systems* (identity, payments, registries, data exchange) so they remain **public-benefit, interoperable, contestable, and rights-preserving** across political cycles.

This archive treats DPI as *public infrastructure*, not “an app”: a small set of shared, reusable rails that enable many services (public + private) at societal scale. citeturn0search2turn0search18

## Why DPI needs special governance
DPI has three properties that amplify governance risk:
- **High coupling:** a failure or capture event spills across services and sectors.
- **Invisible coercion:** enrollment + authentication can become de facto mandatory.
- **Path dependence:** early design choices lock in power, vendors, and surveillance.

So DPI should be governed like critical infrastructure: *explicit mandates, independent audits, and hard-to-bypass redress*.

## Core rails (minimum)
1. **Open standards + interoperability**  
   - published specs; versioned change control; conformance tests  
   - “exit ramps” so jurisdictions can migrate off a vendor without losing users
2. **Separation of roles**  
   - operator ≠ policy setter ≠ auditor ≠ redress authority  
   - minimize single points of political or commercial control
3. **Rights + due-process envelope**  
   - lawful basis + necessity/proportionality for data use  
   - appeal paths and non-digital alternatives for essential services
4. **Safety + security by design**  
   - threat modeling; independent security review; incident disclosure windows  
   - resilience planning (degraded modes, failover, offline contingencies)
5. **Public accountability artifacts**  
   - annual “DPI report” (uptime, fraud, exclusion rates, incidents, audit findings)  
   - procurement transparency for core rails

## Governance model (recommended default)
A compact, legible institutional split:

- **DPI Steward (policy & architecture):** sets public-benefit mandate, scope, and standards roadmap.
- **DPI Operator (runtime):** runs infrastructure to published SLOs; no unilateral rule changes.
- **DPI Auditor (independent):** security/privacy audits, performance audits, fairness/exclusion audits.
- **DPI Ombuds / Redress (independent):** handles complaints, reversals, and remedies with deadlines.

This mirrors the broader archive approach: *interface obligations by scope + independent inspection + remedy.*  

## Change control (anti-capture)
Treat rule changes as “public law”:
- publish proposals + impact notes
- consultation windows with recorded stakeholder footprint (regulatory footprint)
- staged rollout + rollback plan
- post-change evaluation at 30/180/365 days (measured exclusion/fraud/error)

The OECD’s 2024 lobbying/influence recommendation is a good anchor for “who influenced what” transparency in such processes. citeturn0search4

## Inclusion and exclusion budgets
DPI must make exclusion measurable and unacceptable:
- **Exclusion budget:** maximum allowable denial/lockout rate for essential services
- **Appeal SLA:** time-to-review for identity/payment/data disputes
- **Non-digital channel parity:** requirements for offline/assisted access

## Cross-border and federation notes
When DPI is federated across jurisdictions:
- publish mutual recognition criteria
- create dispute-resolution compacts (see polycentric compacts doc)
- define data-sharing ceilings and “data free flow with trust” constraints, aligning with applicable law

## References (starting points)
- UNDP on DPI as foundational systems enabling secure interactions across society. citeturn0search2
- Gates Foundation overview framing DPI as shared interoperable building blocks. citeturn0search18
- OECD (2024) recommendation on transparency/integrity in lobbying and influence. citeturn0search4
