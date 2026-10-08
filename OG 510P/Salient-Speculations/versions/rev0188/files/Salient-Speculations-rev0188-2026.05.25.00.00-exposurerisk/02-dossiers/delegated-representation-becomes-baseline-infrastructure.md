---
id: ss-0183-delegated-representation-becomes-baseline-infrastructure
revision_promoted: pre-rev0180
title: Delegated Representation Becomes Baseline Infrastructure
constellation:
- care-and-demography
- resilience-and-continuity
- model-governance
- managed-legibility
- maintenance-and-repair
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- care / ageing / household capacity
- healthcare / biological observability / diagnostics
- energy / grid / flexible load
- logistics / cold chain / physical continuity
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
bottleneck_type:
- allocation priority
- queue position
- fallback / graceful degradation
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- liability-tail custody
- maintenance capacity
- replayability / reconstructability
enforcement_surface:
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
- permit / license
- underwriting / insurance renewal
artifact_type:
- registry entry
- notice
- state label
- certificate / attestation
- replay bundle
lifecycle_stage:
- publish
- rely
- dispute
- correct
- archive
- retire
primary_actors:
- household
- public-agency
- provider
- operator
- utility
- model-provider
- buyer
- auditor
- broker
- source-vendor
- insurer
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
authority_role: delegate-representative and principal-subject
authority_stage:
- grant
- bind
- scope
- act
- dispute
state_family:
- authority
state_terms:
- authority-active
- scope-limited
- joint-approval-required
- disputed-authority
consolidation_status: state-family-member
---
# Dossier: Delegated Representation Becomes Baseline Infrastructure

## Core claim

The important shift is not merely that some people need help with complex services. It is that **as more high-stakes systems harden around verified identity, digital filing, recovery workflows, linked records, and formal compliance steps, institutions increasingly need a governed way for one person or organisation to act inside the workflow for another**. Once taxes, benefits, healthcare, company law, and digital-public-service access move through portals, authentication layers, and tightly specified evidentiary paths, the decisive question is no longer only whether a user can reach the service. It becomes: **who is allowed to stand in for whom, for which actions, under which safeguards, and with what revocation path?**

The stronger version of the thesis is not simply that agents or carers become more common. It is that **delegated representation becomes baseline infrastructure**. Trusted helpers, authorised representatives, solicitors, accountants, guardians, fiduciaries, and family carers increasingly become part of the ordinary completion layer for public and regulated services. In that world, representation is no longer an unusual legal add-on. It becomes part of the architecture of access itself.

## Why this belongs in the archive

The archive already contains dossiers on human fallback, plain language, language access, credential recovery, record repair, and authoritative-source hierarchies. The missing layer was the **proxy layer**: not just whether a service has human support, but **whether another person can formally and safely act inside the service when the principal user cannot, should not, or does not want to do every step alone**.

GOV.UK One Login now publishes explicit guidance for people helping someone else use the service [S328]. The guidance says a helper can lend a device, help scan ID, and assist with parts of identity proofing, but cannot choose the person’s password, enter their security codes, or answer security questions on their behalf [S328]. Its contact page routes struggling users directly to this helper model and to live support [S329]. These sources matter because they show a modern government identity system openly specifying a bounded representation layer instead of pretending that every user will always act alone.

The business-compliance stack is moving the same way. Companies House says agents who verify the identity of clients must register as an Authorised Corporate Service Provider (ACSP) [S330], and that in future all agents filing with Companies House on behalf of clients will need to register [S331]. Once authorised agents become a formal, registered path for identity verification and filing, professional intermediaries are no longer peripheral conveniences. They become part of the legal operating layer of company administration. This builds naturally on the already-promoted Companies House identity-verification regime [S327].

Healthcare and benefits show the same pattern. HealthCare.gov defines an authorized representative as someone you choose to act on your behalf with the Marketplace, like a family member or other trusted person [S332]. In Marketplace appeals, that representative becomes the main contact, can provide documents, return calls, attend hearings or conferences, and tell the Marketplace what the appellant wants to do after the decision [S333]. Medicare maintains a standard Appointment of Representative path for appeals and explicitly frames it as giving another person legal permission to help file [S334]. These are strong signals that representation is not a rare courthouse event; it is now designed into ordinary benefit and coverage operations.

Social Security separates different kinds of representation rather than relying on one blunt model. The Representative Payee Program appoints a suitable payee to manage benefit payments for beneficiaries incapable of managing them, first looking to family or friends and then to qualified organisations when necessary [S335]. Separately, SSA lets a person appoint someone to help with their case by written statement or Form SSA-1696, including electronic submission started by the representative [S336]. This matters because it shows the state distinguishing between **advocacy representation** and **fund-management representation**, both as routine administrative forms.

Tax administration does the same with even finer granularity. IRS guidance explicitly distinguishes among Power of Attorney, Tax Information Authorization, and Third Party Designee routes [S337]. One path allows representation before the IRS; another lets a designee review or receive confidential information for specified matters and periods; another allows limited discussion of a specific return [S337]. This is a clear institutional signal that modern service systems increasingly require **graded delegation**, not a binary between full autonomy and full guardianship.

Health privacy law confirms how deep the pattern goes. HHS explains that a personal representative is treated as the individual for relevant purposes under the HIPAA Privacy Rule, can access protected health information, exercise the individual’s rights, and authorize disclosures within the scope of the representation [S338]. But HHS also describes scope limits and abuse / endangerment exceptions [S338]. This is exactly what a baseline infrastructure looks like: recognition, bounded authority, and safeguarding rules.

Other federal systems show the same structure. VA’s fiduciary program appoints and oversees a fiduciary for beneficiaries unable to manage VA benefits, considers beneficiary preference in selection, and preserves appeal routes around fiduciary decisions [S339]. USCIS Form G-28 exists specifically so an attorney or accredited representative can formally appear on behalf of an applicant, petitioner, or respondent [S340]. Once these models proliferate across benefits, immigration, healthcare, tax, and corporate compliance, the broader speculation becomes hard to ignore: **representation is becoming a normal operating requirement of the service stack, not merely a specialist accommodation for rare edge cases**.

## Speculative consequences worth tracking

### 1. Role-based permissions become mainstream design surfaces

Institutions may increasingly need interfaces, notices, and audit trails built for principals, helpers, authorised representatives, fiduciaries, and professionals with different scopes of action.

### 2. Access inequality shifts toward representation inequality

Some people may be excluded less by raw literacy or connectivity than by whether they have a trustworthy person or affordable professional who can act for them when systems become brittle.

### 3. Safeguarding and revocation become core governance problems

The more services depend on delegated action, the more they need good answers for abuse prevention, mandate expiry, role conflict, emergency access, and how authority is withdrawn when relationships break down.

### 4. Professional intermediary markets thicken

Accountants, solicitors, brokers, fiduciaries, and registered agents may gain quiet power because they occupy the practical bridge between people and increasingly formal service systems.

### 5. “Self-service” becomes partly fictional

Many services may still market themselves as self-serve even while ordinary completion increasingly depends on carers, family members, call-centre staff, or professionals operating around or inside the workflow.

### 6. Administrative law shifts toward representation architecture

Conflicts may increasingly arise not only over the merits of a decision but over who counted as properly authorised to receive notices, answer for the user, submit evidence, or make downstream choices.

## What could falsify or weaken the thesis

- Services become genuinely simpler, more resilient, and more accessible, so the share of users needing proxy action does not rise much in practice.
- Portable credentials, good wallet architectures, and better recovery paths let people complete high-stakes actions themselves without needing representatives nearly as often.
- Fraud, abuse, or privacy backlash leads institutions to narrow delegation so sharply that representation remains legally possible but operationally marginal.
- Expanded in-person public service capacity reduces dependence on formal proxy roles by letting frontline staff resolve most difficulties directly.
- Intermediary-heavy sectors such as immigration, benefits appeals, and company filing turn out to be special cases rather than leading indicators for the wider service stack.

## Research queue

- Which sectors are normalising delegation fastest: tax, pensions, health, schooling, immigration, housing, banking, or company law?
- Where do institutions clearly distinguish helper, representative, fiduciary, and professional agent roles, and where do those categories blur?
- Which delegation models produce the least abuse without making legitimate help too burdensome to grant?
- How often do users lose access or miss deadlines because a representative was not recognised, had the wrong scope, or could not be revoked cleanly?
- Does delegated representation reduce exclusion overall, or mainly shift exclusion toward people who lack trustworthy and competent intermediaries?
