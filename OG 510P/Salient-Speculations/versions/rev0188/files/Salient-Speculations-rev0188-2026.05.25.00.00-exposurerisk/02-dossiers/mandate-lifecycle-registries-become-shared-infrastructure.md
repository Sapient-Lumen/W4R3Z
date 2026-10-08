---
id: ss-0183-mandate-lifecycle-registries-become-shared-infrastructure
revision_promoted: pre-rev0180
title: Mandate-Lifecycle Registries Become Shared Infrastructure
constellation:
- care-and-demography
- model-governance
- managed-legibility
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- care / ageing / household capacity
- healthcare / biological observability / diagnostics
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
bottleneck_type:
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
enforcement_surface:
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
artifact_type:
- registry entry
- notice
- state label
lifecycle_stage:
- publish
- rely
- dispute
- correct
primary_actors:
- household
- public-agency
- provider
- model-provider
- buyer
- auditor
- broker
- source-vendor
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword
  context; review before treating as authoritative.
refactor_cluster:
- authority-lifecycle
authority_role: issuer-authentic-source and revocation-publisher
authority_stage:
- grant
- publish
- revoke
- propagate
state_family:
- authority
state_terms:
- grant-pending
- authority-active
- revocation-pending
- revoked
- expired
consolidation_status: state-family-member
---
# Dossier: Mandate-Lifecycle Registries Become Shared Infrastructure

## Core claim

The important shift is not merely that more people, agents, carers, solicitors, brokers, accountants, attorneys, and proxies are allowed to act for someone else. It is that **once delegated action becomes common, authority itself has to become stateful infrastructure**. Modern institutions increasingly need live, machine-readable answers to questions such as: who may act, for whom, under what legal basis, with what scope, from when until when, with what expiry or review date, and with what record of changes.

The stronger version of the thesis is not simply that more services accept representatives. It is that **mandate-lifecycle registries become shared infrastructure**. They do not have to take the form of one giant national database. But more sectors may need authority-state layers that other systems can check and rely on: registries, broker services, APIs, account-based permission stores, or public lists that turn representation from a paper attachment into a maintained operational state.

## Why this belongs in the archive

The archive already contains dossiers on delegated representation, safeguarded delegation, representation-risk telemetry, authoritative-source hierarchies, and credential recovery. The missing layer was **authority-state infrastructure**: not merely whether a representative can be appointed, but whether multiple services can tell, in a timely and reliable way, what that representative is currently allowed to do.

The conceptual signal is now unusually clear. The UK’s new 1.0 delegated-authority guidance, published in March 2026 for services certified against the digital verification services trust framework, explicitly treats delegated authority as something services must check rather than assume [S419][S420]. It says the evidence must identify the subject, the representative, the permissions granted, when the permissions were given, and any conditions on the authority [S419]. It also says a service may either ask for evidence or **create the authority within the service**, may check a database itself, and may rely on a public-body-maintained list as stronger digital evidence [S419]. That is a major signpost. Delegated authority is no longer being treated merely as a private document that happens to exist somewhere. It is being framed as something that digital services must model, verify, and sometimes instantiate.

The strongest practical examples also now look more like live authority-state systems than static paperwork. The Office of the Public Guardian’s **Use an LPA / View an LPA** flow lets attorneys generate organisation-specific access codes so companies can verify the donor’s details, the attorney’s status, how decisions may be made, any instructions or preferences, and whether the LPA is still valid and registered [S421]. OPG is explicit that the online view is more up to date than the paper instrument because replacement attorneys, name changes, address changes, and other state changes can be reflected there even though the paper copy cannot be altered [S421]. That is exactly the kind of stateful authority layer the archive needs to name.

Healthcare is moving in the same direction. NHS England’s **National proxy service** is building a national data store of proxy relationships for use across health and care settings [S422]. The planned store will include the patient-proxy relationship, who granted access, the legal basis for the access, expiry and review dates, and an auditable record of changes [S422]. From 2027, GP practices in England are expected to use the National proxy service when awarding proxy access [S422]. The related Proxy application service already verifies identity and parental relationship information, routes applications into GP workflows, and frames proxy access as something to decide on the basis of whether it is safe, necessary, and relevant [S423]. This is no longer a local sticky note in a single practice. It is becoming a portable authority-state layer.

Australia’s business-access stack shows the same architecture in a different domain. The ATO’s **Relationship Authorisation Manager (RAM)** lets a principal authority link a business to a Digital ID and then manage who can act on behalf of the business online [S424]. Authorised individuals must accept the request in RAM [S424]. The same infrastructure manages machine credentials, assigns or reassigns permissions through Access Manager, tracks expiry, sends warning notifications, and supports revocation of unused or duplicate credentials [S424]. That matters because it shows mandate state reaching beyond human proxies into machine-to-machine permissions and software-mediated filing.

Tax administration now also looks increasingly like maintained authorization infrastructure rather than one-off forms. IRS guidance says Power of Attorney and Tax Information Authorization records are placed on the **Centralized Authorization File (CAF)** so IRS staff can verify a representative’s permission to access confidential tax information [S378]. Taxpayers can now review, electronically sign, and manage authorizations in their online account [S378]. Tax Pro Account lets practitioners view all active authorizations on the CAF, see request history, and withdraw an authorization in real time, removing it immediately from the CAF database [S379]. The IRS also treats the CAF number itself as a standing identifier for third-party authorization [S427]. This is the anatomy of a registry, even if IRS does not market it that way.

Social Security and company law point in the same direction. SSA’s representation stack now includes the AARPS portal, where registered representatives can view registration details, client lists, status reports, fee history, and withdrawal pathways [S425]. Companies House has created a new regime for Authorised Corporate Service Providers (ACSPs), with registered agent accounts, role management, user addition and removal, update and closure workflows, suspension / cessation consequences, and a public list of registered ACSPs that others can consult [S331][S426][S428]. Individuals can also choose to have an ACSP verify their identity for Companies House and find one through that public list [S428]. These features matter because they show authority becoming something both services and relying parties can check against maintained status, not merely infer from a PDF attached to an email.

Taken together, these signals support a broader thesis than the earlier proxy and safeguarding dossiers: **modern institutions are beginning to need live authority-state infrastructure because too many important actions now depend on knowing, at the moment of action, whether a mandate exists, what it allows, and whether it has changed**.

## Speculative consequences worth tracking

### 1. Static documents lose status relative to live checks

Paper powers, scanned letters, and local notes may increasingly be treated as fallback evidence, while services prefer APIs, platform accounts, registry lookups, access codes, or authoritative-state queries that show current mandate status.

### 2. Revocation propagation becomes a hidden reliability problem

As more systems rely on distributed authority state, the hard part may become making replacements, suspensions, expiries, and withdrawals propagate quickly enough that stale permissions do not continue to work somewhere else.

### 3. Permission taxonomies standardise

Institutions may converge on more explicit authority fields such as preparer, filer, signer, viewer, carer, trusted contact, attorney, deputy, patient proxy, or machine credential custodian, each with bounded scope rather than generic proxy access.

### 4. Cross-service portability becomes a policy objective

Once a person has proved they are a parent, carer, deputy, or authorised business officer in one place, pressure may grow to let other services rely on that state instead of making them re-prove the same relationship repeatedly.

### 5. Mandate infrastructure becomes a new privacy and power frontier

The authority layer may start to reveal intimate facts about dependence, illness, business control, guardianship, and institutional trust. That could make mandate registries politically important even when they are administratively useful.

### 6. Private verification and middleware markets may deepen

Where states do not provide portable authority-state services directly, software vendors, trust intermediaries, and regulated professionals may step in to provide authority-check, audit, and relying-party integration layers.

## What could falsify or weaken the thesis

- Most sectors continue accepting static documents and local discretionary notes, with no real movement toward maintained authority-state systems.
- Shared registries or authority-check APIs prove too politically contentious, too privacy-invasive, or too costly to sustain.
- The evidence remains concentrated in tax, elder-law, and health-proxy systems rather than spreading across the broader service stack.
- Institutions standardise identity, but not mandate state, leaving representation to be re-proved manually in every service.
- The main gains come from better casework and support rather than from persistent authority-state infrastructure.

## Research queue

- Which sectors are most likely to converge on portable authority-state layers first: tax, healthcare, company law, pensions, banking, or social care?
- Which mandate attributes matter most in practice: scope, legal basis, expiry, review date, revocation history, or relying-party audit logs?
- Where does authority-state portability reduce friction, and where does it create unacceptable privacy or concentration risks?
- Do public lists, APIs, and account-based permission stores converge toward common standards, or remain fragmented by sector?
- What metrics would reveal mandate-lifecycle quality without exposing sensitive individual relationships?
