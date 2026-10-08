---
id: ss-migrated-authority-check-outages-become-civic-incidents
revision_promoted: pre-rev0182
migration_status: inferred-rev0182
title: Authority-Check Outages Become Civic Incidents
constellation:
- managed-legibility
- energy-sovereignty
- anti-legibility
- operational-resilience
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- identity / credentials / delegated authority
- civic services / casework / appeals
- procurement / purchasing / offtake
bottleneck_type:
- admissible evidence
- state freshness
- appealability / redress
enforcement_surface:
- procurement / framework contract
- platform eligibility
- audit / assurance engagement
artifact_type:
- registry entry
- notice
lifecycle_stage:
- publish
- rely
failure_modes:
- stale-state
- nonpropagation
- procedural-debt
refactor_cluster:
- remedy-lifecycle
- authority-lifecycle
- exposure-liability
remedy_role: outage-triggered remedy path
remedy_stage:
- outage
- fallback
- repair
consolidation_status: state-family-member
state_family:
- remedy
- authority
- exposure
authority_role: authority-broker and fallback-operator
authority_stage:
- verify
- fallback
- audit
state_terms:
- offline-verifiable
- fallback-accepted
- authority-stale
- materiality-determination-pending
- reserve-held
- tail-open
exposure_role: service-provider and public-risk-bearer
exposure_stage:
- trigger
- reserve
- close
---
# Dossier: Authority-Check Outages Become Civic Incidents

## Core claim

The important shift is not merely that more services use identity proofing, sign-in brokers, proxy registries, permission APIs, or representative checks. It is that **once those checks sit inside the path of ordinary action, their downtime stops looking like ordinary backend trouble**. A user is no longer merely failing to load a page. They may be unable to verify a director, manage someone else's medicines, lodge as an agent, access a pension account, or complete a benefits task before a deadline.

The stronger version of the thesis is not simply that outages are inconvenient. It is that **authority-check outages become civic incidents**. As digital public services depend on sign-in, proofing, proxy, and permission layers, degradation in those layers increasingly has to be managed as a public-facing continuity problem with status pages, contingency routes, support lines, maintenance windows, retry logic, manual fallback, and eventually explicit policy about which actions may pause and which must still go through.

## Why this belongs in the archive

The archive already contains dossiers on authority-state registries, revocation propagation, authority-check middleware, and authority freshness guarantees. The missing layer was **incident exposure**: not how authority is modeled when the stack works, but what happens when the checking layer is unavailable, degraded, or uncertain at the moment of action.

The clearest signal is that governments are now publishing status machinery for these systems as if they were shared public utilities. GOV.UK One Login runs a public status page that says it will post updates when it experiences difficulties and directs users to other help channels if the issue is not listed [S459]. Its incident-history page supports email and text subscriptions whenever incidents are created, updated, or resolved [S460]. The support stack is correspondingly operational: GOV.UK One Login offers live webchat, phone support, and email support on defined office-hour schedules [S461][S462]. This is already more than ordinary website troubleshooting. It is the apparatus of a public incident surface.

The dependency has become visible enough that relying services now point users directly to that incident surface. Companies House says users can access some Companies House services and verify identity through GOV.UK One Login, explicitly tells them to check One Login service availability and status updates, and sends them to the One Login team for help or problem reports [S463]. Once a filing and identity-verification pathway sends people to an upstream status page, the constitutional shape of the stack is clearer: a downstream civic function is now partially hostage to the health of an upstream authority broker.

Healthcare proxy infrastructure shows the same pattern in a more operational form. NHS England's National Proxy Service is building a national store of verified proxy relationships and says other services will integrate using the VRS API [S464]. The service is in private beta and, crucially, is currently only a **bronze** service, available and supported between 8am and 6pm on weekdays excluding bank holidays [S464]. The VRS API likewise describes itself as a bronze service for accessing the national database of validated proxy relationships [S465]. That matters because the archive can now name a new design fact: once proxy checks become infrastructural, **support hours and service tier become part of the practical shape of delegated care access**.

Broader NHS practice already treats such outages as continuity events, not just minor defects. Joint guidance on the NHS e-Referral Service says that back-up procedures must exist for system failure or outage, that planned outages are communicated in advance and placed outside office hours, and that organisations should keep contingency plans for unplanned and prolonged outages that are user-friendly and safe [S466]. The dossier does not require authority services to be identical to e-referrals. The point is that the NHS already treats digital-service failure in clinically consequential pathways as something that requires explicit continuity planning rather than ad hoc apology.

Social Security now exposes the same incident logic publicly. SSA's web-services status site provides real-time and historical availability, 90-day uptime figures, incident categories such as degraded performance, partial outage, major outage, and maintenance, and a recent history including scheduled maintenance windows and a brief portal-access disruption on March 17, 2026 [S467]. This is evidence that online access to benefit-adjacent identity and account systems has become important enough that reliability is communicated publicly as operational state.

The U.S. health-insurance stack points in the same direction through fallback design. HealthCare.gov says there are several ways to apply for Marketplace coverage, including online and over the phone, and that the phone route can help users fill out an application, review choices, and enroll, with help in other languages [S468]. Its login troubleshooting guidance repeatedly routes users to the Marketplace Call Center when security questions, security codes, or account access fail [S469]. Its contact page keeps the main call center available 24 hours a day, 7 days a week except holidays, and also points users to local helpers [S470]. In other words, once account, proofing, and credential problems interfere with coverage access, fallback contact capacity becomes part of the service itself.

Australian systems make the same move even more explicitly. myGov's terms of use say the service cannot guarantee uninterrupted access and instruct users who need to complete a task straight away to contact the relevant linked service if myGov is unavailable [S471]. The myGov helpdesk publishes its hotline hours for exactly this purpose [S472]. Services Australia maintains a standing page for customer-service changes caused by system maintenance, public holidays, or natural disasters [S473]. Its Child Support contact guidance tells users with online-account issues to check for scheduled outages if they receive an error and, if needed, call technical support [S474]. And the ATO's Online Services for Agents dashboard goes furthest: it uses real-time data, supports incident subscriptions, publishes current status and scheduled maintenance, records recent intermittent degradation, and explicitly warns that the dashboard may not reflect the status of other systems that OSFA interacts with or relies upon, including digital-identity login services [S475]. That is a striking admission that authority-check outages can be **dependency-chain incidents**, not just single-service incidents.

Taken together, these signals support a broader thesis than the earlier authority dossier set: **as authority checking becomes infrastructural, outage management, graceful degradation, and public incident communication become part of governance rather than merely part of IT operations**.

## Speculative consequences worth tracking

### 1. Status pages become quasi-civic utilities

Public status dashboards, incident subscriptions, and maintenance calendars may increasingly matter for benefits, filing, care access, and regulated representation the way transit alerts and weather warnings already do.

### 2. Fallback channels become constitutional safety valves

Phone routes, webchat, local helpers, paper submission, supervised overrides, and in-person recovery may become less like secondary convenience features and more like legitimacy-preserving alternatives when authority checks fail.

### 3. Service tiers start to matter politically

Bronze, silver, and higher support tiers may stop being backend procurement vocabulary and start to matter for how much real-world dependence a service is allowed to accumulate.

### 4. Dependency mapping becomes a public-governance task

Institutions may increasingly need to identify when a downstream service failure is actually an upstream identity, sign-in, or authority-broker failure — and communicate that clearly enough for users to understand where to seek help.

### 5. Graceful degradation becomes a design frontier

Systems may need explicit rules for which actions fail closed, which actions can proceed with cached or recent authority, which actions require supervised exception handling, and which can fall back to paper or phone without unacceptable risk.

### 6. Incident budgets and maintenance windows gain civic meaning

Planned downtime, overnight windows, freeze periods, and release timing may become politically consequential whenever the affected service sits in the path of welfare, healthcare, company law, or tax compliance.

### 7. Outage externalities become measurable

Institutions may start tracking blocked filings, deferred referrals, missed enrollment deadlines, failed proxy actions, recontact volume, backlog growth, or compensation exposure caused by identity and authority outages.

### 8. Support operations become part of reliability engineering

A service may increasingly be judged not only by how rarely it fails, but by how fast it posts incident status, how clearly it explains fallback routes, and how competently support teams route affected users across linked services.

## What could falsify or weaken the thesis

- Authority-check systems remain mostly optional or low-frequency, so their downtime rarely blocks important action.
- Most services retain robust local alternatives, making upstream status pages and incident communication marginal rather than central.
- Shared sign-in and authority services become so reliable that outages rarely accumulate enough social consequence to count as civic incidents.
- Users do not actually rely on published status pages, fallback channels, or support subscriptions, leaving incident communication as a thin operator practice rather than a meaningful public interface.
- The real bottleneck remains verification or recovery rather than outage handling, so continuity design never becomes a distinct governance layer.

## Research queue

- Which actions should fail closed during an authority-check outage, and which should continue under supervised fallback?
- What counts as an acceptable outage budget when the affected service gates healthcare proxying, benefits access, filings, or regulated representation?
- Which incident metrics best capture public consequence: blocked actions, wait-time spikes, casework diversion, deferred deadlines, or cross-service backlog?
- How should downstream services communicate dependence on upstream identity and authority layers without confusing users or diffusing accountability?
- Do short-lived offline artifacts, cached proofs, or supervised override tokens reappear as resilience tools once live authority checks become unavoidable?
