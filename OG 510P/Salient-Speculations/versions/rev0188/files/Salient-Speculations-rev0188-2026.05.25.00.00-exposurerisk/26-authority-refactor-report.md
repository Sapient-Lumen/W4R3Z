# Authority Refactor Report

rev0186 audits and refactors the cube's authority/delegation/proxy layer.

## Audit target

The target cluster included dossiers that used any of the following as central mechanisms:

- delegated representation;
- mandate or power lifecycle;
- proxy authority;
- standing and representation proof;
- authority freshness;
- authority-check middleware;
- revocation propagation;
- organizational identity;
- AI-agent authority;
- offline authority artifacts;
- representation risk telemetry;
- scope and permission crosswalks.

The audit found that the archive had enough material for a shared model, but not yet a normalized state vocabulary.

## Problem found

The authority family was split across at least four constellations:

1. `managed-legibility` — because authority becomes a proof object;
2. `administrative-repair` — because representation determines who can appeal or correct;
3. `operational-resilience` — because authority-check outages and stale revocation can stop services;
4. `model-governance` — because AI agents require delegated-action logs.

That distribution is correct, but it hid the shared state machine.

The repeated pattern is:

> a system can authenticate an actor, but still not know whether that actor may bind, represent, disclose for, access for, decide for, pay for, file for, waive for, appeal for, or receive notices for someone else.

## Existing dossiers tagged

The following existing dossiers now receive `refactor_cluster: authority-lifecycle` metadata:

- `delegated-representation-becomes-baseline-infrastructure.md`
- `safeguarded-delegation-becomes-a-mass-design-problem.md`
- `mandate-lifecycle-registries-become-shared-infrastructure.md`
- `authority-check-middleware-becomes-part-of-digital-public-infrastructure.md`
- `authority-check-outages-become-civic-incidents.md`
- `authority-freshness-guarantees-become-compliance-metrics.md`
- `delegate-freshness-proofs-become-a-service-metric.md`
- `delegate-change-propagation-delays-become-a-standing-incident-class.md`
- `revocation-propagation-becomes-a-hidden-reliability-bottleneck.md`
- `offline-verifiable-authority-artifacts-return.md`
- `representation-risk-telemetry-becomes-a-supervisory-surface.md`
- `standing-and-representation-proofs-become-remedy-access-controls.md`
- `delegated-ai-agent-authority-logs-become-consumer-protection-infrastructure.md`
- `credential-recovery-becomes-a-civic-bottleneck.md`
- `identity-match-appeals-become-broker-support-queues.md`
- `organizational-identity-becomes-infrastructure.md`
- `public-proof-profile-registries-become-verification-constitutions.md`
- `data-minimization-proofs-become-procurement-requirements.md`
- `emergency-override-constitutions-become-procurement-questions.md`
- `action-clearance-objects-become-field-work-middleware.md`
- `notice-authenticity-proofs-become-an-assurance-layer.md`
- `reliance-scope-matrices-become-procurement-exhibits.md`
- `scope-crosswalk-services-become-quiet-comparability-brokers.md`
- `recipient-graph-privacy-proofs-become-broker-trust-products.md`

## New dossiers added because of the audit

The audit exposed five gaps.

### 1. Authority-scope crosswalks

Existing dossiers talked about authority and scope, but not the translation problem. A grant that means “inspect records” in one system may map poorly to “download,” “share,” “sign,” “settle,” “appoint sub-agent,” or “waive rights” in another. The new dossier models scope translation as its own infrastructure.

### 2. Representative-of-record ledgers

The archive had mandate registries and authority-check middleware, but not the narrower operational object: the current representative of record for a matter, account, case, enrollment, property, company, tax period, or benefit file. The new dossier treats representative-of-record state as a notice, liability, and access object.

### 3. Legal-person wallets

The cube had organizational identity, but not the transaction-grade authority chain from legal person to natural person to role to wallet to action. The new dossier treats legal-person wallets and organizational authority chains as market infrastructure.

### 4. Capability-token provenance

The AI-agent dossier identified authority logs, but the audit showed a deeper technical object: tokens, token exchanges, proof-of-possession, protected-resource metadata, task context, and chain-of-delegation evidence. The new dossier treats token provenance as the audit layer for agentic systems.

### 5. Proxy-abuse telemetry

Delegation is not only an access benefit. It is also an abuse surface, especially in elder care, disability support, guardianship, domestic control, tax representation, financial affairs, and platform account administration. The new dossier treats abuse telemetry as safeguarding infrastructure.

## Consolidation decisions

- Do **not** merge delegated representation, mandate lifecycle, authority-check middleware, and revocation propagation. They correspond to different lifecycle stages.
- Do merge future narrow examples into the lifecycle unless they introduce a genuinely new stage, failure mode, or enforcement surface.
- Treat “agent” as ambiguous. The cube must distinguish legal agents, platform agents, authorized representatives, brokers, software agents, service accounts, and AI agents.
- Treat “scope” as a first-class object, not merely a label on a token.
- Treat “revocation” as both a freshness problem and an authority problem. The prior rev0184 freshness model remains valid, but rev0186 adds the action-rights consequence.

## Metadata changes

Affected dossiers now use:

- `refactor_cluster: authority-lifecycle`
- `authority_role`
- `authority_stage`
- `state_family: authority`
- `state_terms`

This allows the index to answer questions such as:

- Which dossiers concern grant creation?
- Which concern verification or middleware?
- Which concern revocation propagation?
- Which concern AI-agent delegation?
- Which concern representative-of-record state?
- Which authority failures are also remedy failures?
- Which authority failures are also freshness failures?

## Anti-overfit warning

Do not promote every new government portal, wallet API, or OAuth profile into a dossier. The cube should promote only the institutional bottleneck:

- incompatible authority scopes;
- invisible representative-of-record state;
- legal-person-to-natural-person chain proof;
- agentic token provenance;
- proxy abuse telemetry;
- revocation propagation failure;
- offline / outage fallback;
- dispute and correction of authority use.

## Next refactor candidates

After authority, the next overloaded clusters appear to be:

1. **scope / comparability / translation** — standards crosswalks, semantic equivalence, taxonomy mapping, and mutual recognition;
2. **issuer / resolver / registry governance** — who gets to publish, resolve, suspend, or canonicalize proof objects;
3. **fallback / graceful degradation** — when live checks fail and institutions must decide whether to stop, cache, accept paper, or proceed under risk;
4. **small-actor burden** — when evidence requirements become barriers to participation.
