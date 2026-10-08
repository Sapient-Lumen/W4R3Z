# 918 — Applied public AI register case packet for federal AI use-case inventories, SBA, IRS, ATRS, EU database, and no use by inventory row

## One-line thesis

The U.S. federal AI use-case inventory, late SBA reporting, IRS public/internal inventory split, UK ATRS, and EU high-risk AI database together form a public AI register maintenance case: transparency rows must be reconciled to live use, risk, monitoring, redress, and retirement evidence, with no public use by inventory row.

## Why this matters

This packet turns public AI registers into a concrete maintenance problem. The U.S. federal inventory now offers a centralized, machine-readable view of agency-reported AI uses, but it is compiled from agency-hosted public inventories and coexists with agency-specific omissions, exemptions, inconsistent publication, COTS aggregation, and rapidly changing use. GAO’s recent SBA and IRS reviews show why this cannot be treated as a clean registry story: an agency may publish late, pause use, restart pilots, omit active tools from inventory, or withhold sensitive / R&D uses while still needing public and protected oversight.

The comparative lesson from the UK ATRS and EU high-risk AI database is not “build more registers.” It is “registers need upkeep, state labels, machine-readable fields, accountable owners, protected evidence lanes, and links to actual operational controls.” A public register that cannot answer whether a system is live, paused, exempt, high-impact, monitored, appealable, or retired can improve visibility while still failing governance.

## Pattern pack

Use this packet when someone cites an AI inventory, algorithmic transparency record, AI use-case page, high-risk AI database row, COTS AI rollup, or agency AI register as proof that a tool is governed or not used. The packet’s working sequence is: identify the source-of-truth hierarchy; split public row, internal inventory, and operational deployment; map lifecycle state; reconcile omissions and exemptions; test high-impact / risk classification; connect the row to authority, procurement, data, model, monitoring, incidents, and redress; then preserve row-level currentness.

## Case packet

### 1. Form verdict

| Field | Verdict |
| --- | --- |
| live problem | public AI inventory rows, central aggregation, agency-hosted CSVs, late reporting, sensitive / R&D exemptions, COTS rollups, risk labels, and row currentness |
| lower form insufficient | ordinary transparency-register doctrine is too thin because the register can be stale, incomplete, exempted, aggregated, or disconnected from operational controls |
| higher form excessive | a general AI regulator form is too thick because the immediate repair is a row-to-evidence maintenance waist across existing agency inventories, audits, and oversight lanes |
| form verdict | public AI register maintenance waist with lifecycle state, source hierarchy, omission reconciliation, high-impact substantiation, and no use by inventory row |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| OMB / central repository | aggregates and standardizes public agency inventories; it is not the original deployment authority or the only source of truth |
| agency public inventory | publishes publicly releasable rows; it must retain stable row IDs, dates, state labels, and links to agency evidence |
| agency internal inventory | should include nonpublic, sensitive, R&D, paused, pilot, or exempt uses for protected oversight and reconciliation |
| Chief AI Officer / governance body | owns inventory discipline, risk acceptance workflow, and reporting quality; it should not become a ceremonial signoff body |
| program owner | explains the business process, affected population, output role, operational state, and redress route |
| procurement / platform owner | links contracts, commercial suite features, cloud services, vendor updates, and configuration changes to inventory rows |
| auditor / GAO / inspector general | reconciles public reporting against internal inventories, procurement records, staff interviews, and actual use |
| public / affected person | should be able to understand whether a listed use could affect guidance, eligibility, payment, enforcement, records, or service handling |
| protected evidence lane | handles lawful non-disclosure while preserving oversight, source, risk, and correction evidence |
| comparative register operator | UK ATRS and EU AI database examples show machine-readable and mandatory-public-register design pressures, but do not prove local deployment repair |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| OMB 2025 Federal Agency AI Use Case Inventory | central machine-readable aggregation, agency submissions, COTS split, high-impact counts, and agency-source hierarchy |
| OMB M-25-21 | annual inventory obligation, public posting expectation, ongoing update encouragement, and high-impact governance frame |
| GAO generative-AI management report | rapid year-to-year inventory growth and guidance-change pressure |
| GAO SBA AI report | late / inconsistent public reporting, paused AI use, pilot/pre-pilot state, and reporting-procedure recommendation |
| SBA AI inventory page | agency public inventory page and last-updated surface to be reconciled with GAO findings |
| GAO IRS AI management report | active AI use count, sensitive/R&D split, omitted contracted tools, benefit-information gaps, and strategic-management weakness |
| GAO IRS public inventory supplement | public subset of IRS internal inventory and data-definition surface |
| UK ATRS guidance | mandatory-scope example for public-sector algorithmic transparency records |
| EU AI Act Article 71 / high-risk database | public, user-friendly, navigable, machine-readable database requirement and deployer/provider entry split |

### 4. Live chain notes

Use `857`, `876`, `879`, `887`, `901`, `910`, `917`, and this packet first. For this case, live fields are:

- `813` for legal authority, AI policy authority, reporting obligations, public-disclosure boundaries, and protected non-disclosure rules;
- `814` for procurement, license, cloud, platform, vendor, monitoring, audit, and decommissioning costs;
- `815` for inventory intake, owner certification, risk classification, publication, revision, and retirement workflows;
- `816` for GAO, inspectors general, chief AI officers, privacy / civil-rights offices, legislative oversight, public dashboards, and source-health checks;
- `817` for service users, taxpayers, small businesses, claimants, applicants, staff users, affected communities, auditors, and suppliers;
- `818` for public rows, internal rows, row IDs, data dictionaries, status labels, COTS rollups, sensitive-use reasons, and diff logs;
- `819` for OMB, agency program offices, CIO / CAIO offices, procurement offices, vendors, auditors, register operators, and civil-society users;
- `820` for annual inventory cycles, ongoing updates, policy revisions, pilots, pauses, deployments, model changes, and database implementation clocks;
- `821` for public correction requests, FOIA, audit findings, inspector-general referrals, affected-person complaints, and row-level dispute routes;
- `823` for model providers, cloud services, commercial suites, agency systems, inventory repositories, data platforms, and monitoring logs;
- `824` for claims of transparency, innovation, efficiency, public trust, compliance, fraud control, service improvement, and risk mitigation.

Reserve `822` unless a physical asset, contract handback, platform retirement, or data-center / vendor exit becomes the live issue.

### 5. Public AI register tests activated

This packet activates the `PUBLIC_AI_REGISTER_TESTS` matrix:

1. source-of-truth hierarchy;
2. public/internal/exempt reconciliation;
3. lifecycle and deployment state;
4. high-impact / risk classification basis;
5. authority, procurement, and system linkage;
6. model, data, vendor, and version drift;
7. monitoring, incident, and redress evidence;
8. machine-readable comparability and row identity;
9. material-change and retirement receipts;
10. register quality metrics.

### 6. Rival readings

**Rival 1: The best repair is more complete public disclosure.** More disclosure helps, but this packet’s target is maintenance and reconciliation. Some uses may lawfully require protected lanes; even fully public rows still need state, authority, monitoring, and redress evidence.

**Rival 2: Central repositories solve the source-of-truth problem.** Central repositories improve discoverability, but they can be downstream of agency-hosted inventories and reporting definitions. The source-of-truth hierarchy must remain visible.

**Rival 3: Sensitive and R&D exclusions make public registers unreliable.** They make public registers partial, not useless. The repair is public aggregate where lawful, protected oversight, and internal reconciliation.

**Rival 4: A public inventory is only transparency, not governance.** Correct, but if officials, auditors, journalists, and service users rely on it, then its freshness, definitions, and source links become governance surfaces.

## Findings table

| Risk | Bad shortcut | Repair |
| --- | --- | --- |
| OMB aggregate | central row treated as original proof | preserve agency source URL, reporting period, and row lineage |
| agency late reporting | eventual publication treated as historical compliance | record missed reporting cycles, responsible office, and procedure repair |
| internal/public split | nonpublic use treated as invisible | protected oversight and public aggregate / reason class where lawful |
| paused use | old use case treated as active or repaired | pause reason, restart condition, pilot boundary, and residual-risk receipt |
| high-impact count | category treated as self-proving | impact basis, risk acceptance, monitoring, and review clock |
| COTS rollup | license count treated as deployment | workflow-specific decomposition before consequence claims |
| omitted contracted tool | procurement stays outside inventory | procurement-to-inventory reconciliation and vendor-feature watch |
| public supplement | public subset treated as full inventory | subset scope statement and internal reconciliation clock |
| EU / UK comparator | register mandate treated as operational repair | implementation evidence, row quality, and redress linkage |

## Failure modes

- **No-use by silence**: public absence is cited as proof that an agency does not use AI.
- **Use by inventory row**: listing is cited as approval, authority, or monitoring proof.
- **Late-report amnesia**: the register eventually appears but missed reporting years are not reconstructed.
- **Pilot fog**: development, pilot, paused, and deployed states are merged.
- **Sensitive-use sinkhole**: lawful non-disclosure becomes no oversight and no aggregate signal.
- **COTS generalization**: a commercial tool category hides case-specific public effects.
- **Risk-label drift**: high-impact or low-risk status is not rechecked after model, vendor, data, or use changes.
- **Procurement omission**: vendor or platform AI features enter operations without inventory linkage.
- **Retirement by row disappearance**: a row is removed while outputs, data, contracts, or affected cases persist.

## Anti-theater tests

1. Can the agency identify whether the inventory row is source, copy, aggregate, supplement, or derived standardization?
2. Can the public row be reconciled to internal inventory, procurement, COTS, pilot, paused, and exempt-use records?
3. Does every row have a lifecycle state that distinguishes development, pilot, deployed, paused, withdrawn, and decommissioned?
4. Does each high-impact or rights-facing label link to the assessment basis and risk-acceptance record?
5. Does each row name authority, owner, affected function, output role, data source, model / vendor dependency, and system linkage?
6. Can model, data, vendor, prompt, threshold, workflow, or policy changes trigger row update and re-review?
7. Does the row point to monitoring, incident, complaint, appeal, redress, and fallback evidence?
8. Are row IDs, data dictionary, dates, and machine-readable exports stable enough for annual diffing?
9. Can paused, retired, or omitted tools be traced to decommissioning, residual-data, and protected-oversight receipts?
10. Do register-quality metrics report timeliness, completeness, reconciliation failures, and correction latency rather than only row count?

## Reconstruction instruction

When reviewing a public AI register, start with this packet instead of the generic AI-assistant or model-decision notes. Route to `876` for public generative guidance, `879` for staff-facing copilots, `874` for consequential model decisions, `901` for identity gates, `915` for watchlist / border / law-enforcement automation, `887` for platform migration, and `859` / `867` for supplier dependency. Keep the register row as a pointer to these controls; do not let it become the control.

## Sources

Source anchors are registered in `sources/source_keys.json` and attached to this note in `sources/source_catalog.json`, including OMB’s 2025 inventory repository, OMB M-25-21, GAO’s generative-AI, SBA, and IRS reports, SBA’s public inventory page, the UK ATRS guidance, and the EU AI Act database provisions.
