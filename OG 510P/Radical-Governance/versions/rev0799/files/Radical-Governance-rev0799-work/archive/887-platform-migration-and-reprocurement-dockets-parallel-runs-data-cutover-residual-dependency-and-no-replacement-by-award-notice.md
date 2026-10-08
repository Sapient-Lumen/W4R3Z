# 887 — Platform migration and reprocurement dockets: parallel runs, data cutover, residual dependency, and no replacement by award notice

## One-line thesis

A public platform has not been replaced, repaired, or safely migrated merely because a new supplier, product, portal, SaaS tenant, data hub, or digital proof channel has been selected; the archive needs a platform-migration docket proving old/new function mapping, data and identity continuity, backlog/error tail, interface dependencies, parallel-run reconciliation, cutover/rollback gates, user continuity, contract exit, legacy fallback, and post-migration value.

## Why this matters

The transition-receipt layer in `884` asks what a real ending looks like. Platform migration is a narrower and more dangerous kind of transition: the old system is often still live, the new system is not yet fully authoritative, and the public authority is under pressure to say the replacement itself is repair.

That is the mistake this note blocks. A payroll system, immigration-status service, health record, border portal, case-management platform, identity register, tax account, benefit payment service, permit platform, or public-records repository can fail during migration even if procurement was lawful, the new software passed feasibility tests, and the old interface is politically discredited. Migration risk lives in data, rules, interfaces, users, fallbacks, staff capacity, records, contracts, and the exact moment when one system becomes authoritative.

The archive should therefore treat platform migration as a first-class governance event, not as an IT milestone.

## Pattern pack

### 1. Migration forms

| Form | Honest label | Core question |
| --- | --- | --- |
| product replacement | new application replaces old application | what function moved, what did not, and when is the old system no longer authoritative? |
| SaaS migration | public function moves to vendor-hosted platform | what public owner controls configuration, data, audit, and exit? |
| reprocurement | supplier changes while function persists | what obligations, records, data, licenses, warranties, and dependencies survive? |
| data-hub migration | source records are centralized, normalized, or re-keyed | what native evidence is preserved and what new semantic owner is created? |
| account migration | users move from document, local account, or paper proof to digital identity / account proof | who is stranded, mismatched, locked out, or misrepresented? |
| parallel run | old and new systems operate together | what records prove reconciliation, divergence handling, and old-system authority? |
| phased wave | departments, regions, cohorts, or user classes are onboarded in stages | what is the wave gate and what happens if one cohort fails? |
| legacy retirement | old system or document is withdrawn | what fallback, evidence tail, and access route remain? |
| vendor/platform exit | contract or technical platform ends | what export, audit, portability, support, and residual lock-in proof exists? |

Selection is not migration. Migration is a governed chain of evidence.

### 2. Minimum platform-migration docket

| Field | Required proof |
| --- | --- |
| public owner | named legal and operational owner for old state, migration state, and new state |
| old/new function map | what functions, rights, records, workflows, decisions, notices, and checks move, stay, split, or die |
| data inventory | source records, identifiers, personal data, financial data, statuses, entitlements, logs, and retention basis |
| identity / entitlement mapping | how persons, accounts, statuses, rights, obligations, pay cases, cases, or permits are matched and corrected |
| backlog and error tail | unresolved old-system errors, manual cases, appeals, compensation, overpayment, underpayment, or complaint residue |
| interface map | upstream and downstream systems, third parties, staff consoles, APIs, reports, and paper routes affected by migration |
| parallel-run evidence | test cases, live comparisons, divergence rules, reconciliation thresholds, and sign-off records |
| cutover gate | who authorizes new authority, when old authority ends, and what failure threshold blocks cutover |
| rollback / fallback | how service continues if the new system, account, portal, supplier, or data hub fails |
| affected-user continuity | notice, assistance, accessible channels, vulnerable-user support, and no-rights-loss proof |
| contract / exit ledger | old and new suppliers, licences, customizations, warranties, admin access, escrow, portability, and termination duties |
| value and quality proof | cost, benefit, performance, error-rate, service-standard, and user-experience evidence after migration |

A migration docket can be staged, but it cannot be empty at the cutover gate.

### 3. Anti-theater labels

These are useful facts but not sufficient proof:

- preferred supplier selected;
- feasibility completed;
- government accepted lessons learned;
- cloud-based and modern;
- phased approach;
- parallel run planned;
- old documents still show the same status;
- no change to legal rights;
- users can get help online;
- service is optional;
- legacy platform retired;
- data has been migrated;
- final release planned;
- value for money expected.

Each label should trigger a proof demand. None should be accepted as proof by itself.

### 4. The old-system-error problem

The most dangerous migration residue is not the old software. It is the old system's unresolved state.

A backlog, erroneous debt, wrong status, missing pay transaction, unresolved appeal, duplicate identifier, corrupted account, uncorrected address, unlinked passport, invalid entitlement, or pending complaint can be carried into the replacement. Once migrated, the error may gain new legitimacy because it appears inside the new authoritative platform.

So the archive should ask:

1. Is the old state true, uncertain, disputed, or merely operationally recorded?
2. Is it being copied, recalculated, reconciled, or quarantined?
3. Can the affected person see and contest the migration record?
4. Does the new system preserve the old evidence needed to correct it?
5. Does the migration create a new limitation period, repayment demand, enforcement action, boarding refusal, service denial, or pay error?

A migrated error is not a repaired error.

### 5. Parallel run discipline

A parallel run is not proof unless it produces usable public records.

Minimum parallel-run evidence:

- representative and high-risk scenarios;
- real or safely simulated edge cases;
- old/new output comparison;
- divergence taxonomy;
- root-cause assignment;
- correction responsibility;
- sign-off thresholds;
- independent challenge;
- user and staff feedback;
- public summary for high-risk systems.

If the old system is wrong, the new system should not be judged only by matching it. If the old system is incomplete, the new system should not inherit its silence as truth.

### 6. Reprocurement is not transformation

A procurement record asks whether the public authority bought correctly. A migration record asks whether the public function moved safely.

Those are different proof lanes. A supplier can win lawfully and still be unable to carry the function safely. A platform can be technically feasible and still fail because business rules, staff capacity, data quality, legacy cases, third-party checkers, or public-help routes were not ready. A new SaaS tenant can be cleaner than the old system while still becoming a new public-power chokepoint.

The archive should therefore separate:

- procurement confidence;
- product confidence;
- data confidence;
- rule/process confidence;
- staff readiness;
- user continuity;
- rights/remedy confidence;
- exit confidence;
- post-migration value confidence.

Do not let one confidence lane launder another.

### 7. Special rule for proof-of-status platforms

Where the platform is not the legal right but the practical proof of the right, the migration docket must be stricter. The public authority may say the underlying right does not change. That is not enough if the affected person cannot prove the right to an employer, landlord, carrier, bank, school, benefit office, hospital, border official, or licensing body.

Proof-of-status migration needs:

- stable account recovery;
- identity-document linking;
- correction of wrong names, photos, dates, statuses, and conditions;
- checker education;
- third-party acceptance records;
- outage and incident disclosure;
- assisted and non-digital channels;
- legacy-document continuity where lawful status is otherwise stranded;
- remedy when failure of proof causes practical loss.

No right should depend only on portal uptime.

### 8. Relationship to existing notes

Use this note with:

- `884` for the broader transition receipt;
- `859` and `867` for supplier dependency, admin access, portability, and exit rehearsal;
- `874` and `875` when migrated data may become debt, benefit loss, enforcement, or legal fact;
- `879` when staff tools, queueing, or casework records are migrated into a new platform;
- `856` when the new platform, account, portal, or data hub becomes the practical waist;
- `818` for information and public-record discipline;
- `821` for disputes and correction routes;
- `823` for contracts, concessions, task authorizations, licences, and supplier duties;
- `861` for the defeat test: no replacement by award notice.

### 9. Claim-status rule

Every platform-migration claim should be split into at least six claims:

1. **selection claim** — what product, supplier, or platform has been selected;
2. **feasibility claim** — what has actually been tested and what remains unresolved;
3. **readiness claim** — whether data, rules, users, departments, interfaces, and staff are ready;
4. **cutover claim** — what authorizes the new system to become authoritative;
5. **continuity claim** — how affected users retain service, proof, pay, rights, and remedies;
6. **value claim** — whether cost, quality, performance, and benefit claims survived live use.

A positive selection claim cannot cure a weak readiness claim. A positive feasibility claim cannot cure an unresolved affected-user tail.

### 10. Holding

The archive should treat platform migration and reprocurement as governance events with their own proof surfaces. The core rule is: **no replacement by award notice**. A public platform is not repaired by choosing a new product, not migrated by loading data, not decommissioned by hiding the old portal, and not validated by surviving a pilot. It becomes authoritative only through a record-rich cutover that preserves evidence, protects users, controls suppliers, and leaves a rollback / correction route.

## Anti-theater tests

This note fails if the archive treats supplier selection, feasibility, cloud adoption, parallel-run planning, account creation, or legacy retirement as proof of safe migration. It passes only when the migration docket shows old/new authority, data, backlog, interfaces, parallel-run reconciliation, cutover gates, fallback, user continuity, contract exit, residual dependency, and post-migration value.
