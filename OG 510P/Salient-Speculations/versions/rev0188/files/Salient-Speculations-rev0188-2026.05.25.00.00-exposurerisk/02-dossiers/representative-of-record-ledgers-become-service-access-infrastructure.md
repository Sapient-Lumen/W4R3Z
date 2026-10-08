---
id: ss-0186-representative-of-record-ledgers
revision_promoted: rev0186
title: Representative-of-record ledgers become service-access infrastructure
constellation:
- managed-legibility
- administrative-repair
- market-and-state-capacity
status: dossier
maturity: S3-enforcement-surface
confidence: medium-high
time_horizon: near
domain:
- identity / credentials / delegated authority
- tax / accounting / filing
- public services / eligibility
- healthcare / biological observability / diagnostics
- consumer services / transactions / redress
bottleneck_type:
- delegated authority
- notice routing
- source-of-truth precedence
- appealability / redress
enforcement_surface:
- tax administration
- public-benefit portal
- healthcare proxy access
- consumer redress
- audit / assurance engagement
artifact_type:
- representative-of-record ledger
- authority receipt
- notice-routing entry
- matter-scope grant
lifecycle_stage:
- grant
- publish
- verify
- act
- revoke
- propagate
- dispute
failure_modes:
- wrong-representative-notified
- ghost-representative
- matter-scope-confusion
- revocation-lag
- representative-exclusion
refactor_cluster:
- authority-lifecycle
authority_role: delegate-representative and authority-broker
authority_stage:
- grant
- publish
- verify
- revoke
- propagate
consolidation_status: standalone-mechanism
state_family:
- authority
- remedy
state_terms:
- authority-active
- scope-limited
- revocation-pending
- revoked
- disputed-authority
evidence_grade: E3-artifact-live
decision_grade: DG-A
decision_total: 16
source_refs:
- S1553
- S1554
- S1555
- S1562
- S1563
---
# Representative-of-record ledgers become service-access infrastructure

## Core claim

Delegation becomes operational only when a service knows the current representative for a matter. Not the abstract possibility of representation. Not a PDF in a drawer. The current actor of record: who may receive notices, inspect records, submit evidence, bind the principal, request extensions, withdraw filings, or receive adverse-action explanations.

The speculative claim: **representative-of-record ledgers become service-access infrastructure**. In tax, benefits, healthcare, company administration, marketplaces, elder care, insurance, platform appeals, and agentic transactions, systems increasingly need a maintained ledger of who currently stands in relation to a subject, matter, account, enrollment, property, case, or transaction.

## Why this belongs in the cube

The archive already has mandate lifecycle registries and authority-check middleware. This dossier sits between them. A mandate registry says a power exists. Authority-check middleware verifies a query. A representative-of-record ledger answers a more operational question:

> For this concrete matter, who is the party the system should treat as able to receive, respond, file, or bind?

The IRS Form 2848 page states that the form authorizes an eligible individual to represent a taxpayer before the IRS and that the authorization allows the representative to receive and inspect confidential tax information [S1562]. IRS online submission guidance also distinguishes secure upload from Tax Pro Account real-time processing [S1562]. This is not just identity. It is matter-scoped representation.

GOV.UK's LPA guidance makes the same distinction in a different domain: the LPA must be registered before use; attorneys may have joint or separate decision powers; they must follow restrictions and conditions; and they must not let other people use the LPA [S1563]. The representative-of-record problem is therefore not solved by knowing that “an attorney exists.” The service needs current, scoped, role-specific state.

EUDI Wallet architecture points toward the same operational layer by modeling natural persons representing other natural persons and legal persons, including guardianship, care, and power-of-attorney use cases [S1554]. Once these relationships can be presented digitally, relying parties will need ledgers that decide which representative is the active one for which matter.

## Likely ledger fields

- represented subject;
- representative identity;
- representative type;
- matter, account, filing, case, enrollment, asset, or transaction scope;
- powers included and excluded;
- notice-routing rules;
- joint-action requirements;
- effective date;
- review / expiry date;
- revocation source;
- verification source;
- last status check;
- audit trail;
- dispute route.

## Speculative consequences

### 1. Notice routing becomes authority routing

If a representative of record exists, the wrong notice recipient can create legal and operational failure. Deadlines, appeal windows, and evidence requests may increasingly depend on current representative-state propagation.

### 2. Matter scope becomes more important than identity scope

The same person may represent a principal for one tax year but not another, one company filing but not another, one medical decision but not another, one platform appeal but not a settlement, or one purchase but not a recurring subscription.

### 3. Removal becomes as important as enrollment

The hard operational question is often not adding a representative. It is removing, narrowing, suspending, or replacing one without losing continuity or enabling abuse.

### 4. Representative ledgers become dispute evidence

When a transaction is challenged, the ledger may be asked to prove that the representative was active, properly scoped, fresh enough, and notified correctly at the time of action.

### 5. Intermediaries gain quiet power

Tax professionals, brokers, carers, platform agents, benefits advisers, corporate-service providers, and AI-agent operators may become more powerful if they control how representative-of-record state is created and maintained.

## Abuse and capture risks

- representatives remain listed after the relationship ends;
- principals do not understand who can access their records;
- coercive actors enroll themselves as helpers;
- organizations over-centralize control through “authorized users”;
- services refuse legitimate informal helpers because they lack ledger entries;
- ledger operators monetize access to representation state;
- notices are routed to representatives who have conflicts of interest.

## Falsifiers

The thesis weakens if services keep accepting ad hoc evidence without maintaining representative state, or if digital delegation remains siloed enough that representative-of-record state never travels across service boundaries.

## Near miss / not this

A contact list is not a representative-of-record ledger. The ledger matters only when representation changes access, notice, liability, deadline, remedy, or transaction validity.
