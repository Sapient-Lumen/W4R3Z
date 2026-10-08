---
id: ss-migrated-authority-check-middleware-becomes-part-of-digital-public-infrastructure
revision_promoted: pre-rev0182
migration_status: inferred-rev0182
title: Authority-Check Middleware Becomes Part of Digital Public Infrastructure
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
refactor_cluster:
- authority-lifecycle
authority_role: authority-broker and verifier-relying-party
authority_stage:
- present
- verify
- fallback
- audit
state_family:
- authority
state_terms:
- authority-active
- authority-stale
- verifier-unregistered
- fallback-accepted
consolidation_status: state-family-member
---
# Dossier: Authority-Check Middleware Becomes Part of Digital Public Infrastructure

## Core claim

The important shift is not merely that more services recognise helpers, proxies, attorneys, brokers, carers, agents, or authorised representatives. It is that **once many services need to know who can act for whom, the authority check itself starts becoming shared infrastructure**. Relying parties increasingly need broker layers that sit between identity, mandate state, and the final transaction: verification brokers, permission APIs, agent accounts, relationship services, managed lists, orchestration providers, or authority-query layers.

The stronger version of the thesis is not simply that mandate registries spread. It is that **authority-check middleware becomes part of digital public infrastructure**. Instead of every service inspecting static paperwork or rebuilding delegation logic from scratch, more systems may come to rely on common intermediaries that answer operational questions such as: is this representative current, what can they do, is the relationship verified, which permissions attach, which actions require a step-up check, and which channels can trust the answer.

## Why this belongs in the archive

The archive already contains dossiers on delegated representation, safeguarded delegation, representation-risk telemetry, mandate-lifecycle registries, and revocation propagation. The missing layer was **relying-party mediation**: not who grants authority, and not only how authority changes, but **how ordinary services check authority at the moment of action**.

The conceptual signal is now explicit in UK digital-identity policy. The 1.0 publication of the UK digital verification services trust framework now includes formal rules for **orchestration service providers**, defines them as services whose technology infrastructure securely shares data between participants, and pairs that architecture with a public register of certified services maintained by OfDIA [S439]. The same framework treats interoperability as a core principle and explicitly points certified services to the delegated-authority guidance when checking whether a user can act for someone else [S439]. In parallel, the government’s March 2026 consultation on digital identity says the national digital-ID ecosystem will sit inside this trust-framework infrastructure and explicitly floats whether a digital ID should indicate that an authorised representative is acting on someone’s behalf [S440]. That matters because it pulls delegated-authority checks toward the same shared trust layer as identity itself.

Healthcare shows what that looks like in practice. NHS England’s National proxy service says proxy status linked to an individual’s NHS login can be safely extended to national services and other health technology integrated with NHS login [S441]. The service uses the VRS API to communicate with existing NHS systems such as the Personal Demographics Service and National Events Management to verify parental relationships, and the national proxy data store will hold legal basis, expiry and review dates, and an auditable record of changes [S441]. Other services will be able to integrate with the National proxy service using the same API, and existing locally held proxy relationships are being migrated into the national store [S441]. The key point is not just that there is a registry. It is that a common middleware layer is being built so relying services do not each solve relationship verification and permission checks alone.

US tax administration now shows a similar shift inside a very different domain. IRS Business Tax Account lets a Designated Official authorize a Designated User by selecting which tax forms, tax periods, and permissions the user may access; the user must sign in and e-sign to accept, and the official must revalidate annually to keep access [S442]. Separately, IRS directs taxpayers and professionals to use Tax Pro Account to submit power-of-attorney and tax-information-authorisation requests through the taxpayer’s online account with all-digital submission, electronic signature, and real-time processing [S443]. These are not just digital versions of old forms. They are shared permission interfaces sitting between legal authority and the underlying tax actions.

Australia’s welfare and business stacks point the same way. Services Australia’s Centrelink Organisation Nominee Services lets organisations, via Business Hub, accept or decline nominee requests, view and update customer information, access mail online, and manage access to those services for their own personnel [S444]. The public-facing nominee flows let people add or cancel acting arrangements online, require the person or organisation acting for them to verify identity, and route organisational access through PRODA [S445]. Meanwhile, the ATO’s Relationship Authorisation Manager (RAM) is explicitly described as an authorisation service that lets a person act on behalf of a business or entity online when linked with a Digital ID [S448]. RAM requires acceptance of authorisation requests, supports machine-credential administrators, and works with Access Manager to assign or reassign software permissions [S448]. This is exactly the architecture of authority-check middleware: a shared layer that other government-facing services rely on instead of bespoke local checks.

Company law is moving in the same direction. Companies House now provides an authorised-agent account in which ACSP users sign in with their own GOV.UK One Login, access ACSP services, verify people’s identity, view account status information, and add or remove users depending on role [S446]. It also maintains a public list of ACSPs and a ceased / suspended list to support third-party checking of who may act as a Companies House authorised agent [S447]. That means authority-checking no longer happens only inside bilateral accountant-client relationships. It increasingly routes through maintained service accounts and queryable public status.

CMS’s Marketplace compliance rules make the operational effect plain. Agents and brokers may not make changes to a consumer’s Federally-facilitated Marketplace enrollment unless they are already associated with that enrollment; otherwise the change must go through a three-way call with the consumer and the Marketplace Call Center or through an approved consumer pathway such as HealthCare.gov or EDE [S449]. They may check only the status of applications with which they are affiliated [S449]. The deeper point is that the authority check has become part of the transactional path. It is no longer just background paperwork.

Taken together, these signals support a broader thesis than the existing delegation dossiers: **the next infrastructural layer is not merely authority state, but the brokered systems that relying parties use to check and trust that state in real time or near real time**.

## Speculative consequences worth tracking

### 1. Authority-query layers spread faster than fully shared registries

In many sectors, the practical win may come not from one giant source of truth but from common broker layers, managed service accounts, or APIs that let many services ask the same question in a standard way.

### 2. Relying-party logic starts to standardise

Services may increasingly stop designing delegation rules entirely on their own. Instead they may inherit shared role models, scope vocabularies, assurance levels, and query semantics from a middleware layer.

### 3. Identity and authority stacks converge

Digital-ID platforms, proofing services, access managers, and proxy registries may increasingly merge into one broader trust architecture in which identity, delegated authority, and permission to transact are checked together.

### 4. Middleware outages become governance outages

If authority checks move into shared brokers or APIs, service disruption may increasingly come from authority-check failure rather than from the primary service itself. A broken broker may prevent filing, payment, care access, enrolment, or identity verification across many channels at once.

### 5. Quiet intermediaries gain leverage

Orchestration providers, permission brokers, agent-account platforms, public-status lists, and API custodians may acquire strategic power because they become the hidden chokepoints through which many services decide who may proceed.

### 6. Query semantics become policy questions

Questions that once looked technical — snapshot versus live check, caching rules, step-up triggers, acceptable stale windows, fallback evidence, or which actor can rely on which result — may increasingly become part of legal and compliance design.

## What could falsify or weaken the thesis

- Most services continue using local casework and static evidence, with little shift toward shared authority-query layers.
- Registries spread, but relying parties still inspect documents manually instead of calling common brokers or APIs.
- Middleware layers remain narrow sector tools with no broader architectural convergence.
- Privacy, liability, or interoperability barriers stop cross-service authority checking from becoming routine.
- The real bottleneck remains mandate creation or revocation, while authority checks at the point of action stay simple enough not to require a separate infrastructural layer.

## Research queue

- Which actions actually require live authority checks, and which can safely rely on a recent snapshot or document?
- Who is liable when a relying party acts on a wrong answer from a broker or middleware service?
- Which data fields are minimally needed for interoperable authority checks: subject, representative, scope, legal basis, expiry, review date, status, or change history?
- Can open standards prevent authority-check brokers from becoming new hidden monopolies or single points of failure?
- What uptime, freshness, and auditability guarantees would make authority-check middleware trustworthy enough for high-stakes use?
