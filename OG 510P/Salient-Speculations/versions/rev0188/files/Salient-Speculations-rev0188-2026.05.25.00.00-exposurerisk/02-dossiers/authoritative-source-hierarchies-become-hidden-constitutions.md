---
id: ss-migrated-authoritative-source-hierarchies-become-hidden-constitutions
revision_promoted: pre-rev0182
migration_status: inferred-rev0182
title: Authoritative-Source Hierarchies Become Hidden Constitutions
constellation:
- managed-legibility
- energy-sovereignty
- anti-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- source-of-truth precedence
- admissible evidence
enforcement_surface:
- procurement / framework contract
- platform eligibility
- audit / assurance engagement
artifact_type:
- registry entry
- notice
lifecycle_stage:
- source
- capture
- publish
- rely
failure_modes:
- stale-state
- nonpropagation
refactor_cluster:
- provenance-lineage
lineage_role: source-issuer and registry-steward
lineage_stage:
- identify
- bind
- verify
state_family:
- provenance
state_terms:
- source-bound
- source-unbound
consolidation_status: state-family-member
---
# Dossier: Authoritative-Source Hierarchies Become Hidden Constitutions

## Core claim

The important shift is not merely that institutions keep larger digital records or perform more automated matching. It is that **practical power increasingly sits in the precedence rules that decide which record counts as final when systems disagree**. Once benefits portals, tax workflows, health systems, company registers, and digital-identity layers begin checking each other, the decisive question is no longer only whether information exists somewhere. It becomes: **which upstream record is treated as authoritative enough to govern downstream action?**

The stronger version of the thesis is not simply that master data matters. It is that **authoritative-source hierarchies start behaving like hidden constitutions**. They quietly decide where a correction must be made, which institution can overrule another, where a user must appeal, which identifier binds a person or company across systems, and which mismatch can suspend filing, payment, treatment, coverage, or legal status in practice. In a linked administrative world, source-of-truth order becomes a power map.

## Why this belongs in the archive

The archive already contains dossiers on provenance, human fallback, plain language, language access, credential recovery, record repair, and service completion. The missing layer was the **precedence layer**: not just whether a record can be corrected, but **which record controls the others once systems synchronize**.

ASTP’s Health IT Playbook states that an authoritative data source is an official source of information that may be the source that creates the data or the best source for a specific dataset depending on context, and says governance should define, prioritize, and control authoritative sources to reduce inconsistent or duplicate patient records [S319]. Its companion guidance on data-management platforms says the platform can serve as a system of record, trusted source, or authoritative source of patient demographic data across multiple consuming systems [S320]. These sources matter because they say the quiet rule set is not optional: institutions must decide where authority sits before interoperable systems can operate safely.

The same pattern appears in government data design. GDS described a register as an authoritative list of information you can trust, a canonical source of truth [S324], and later argued that registers should replace many published lists as the recognized canonical sources of data wherever possible, while making data interdependencies more visible [S325]. Once the state begins explicitly building canonical datasets and linking them, conflict over precedence stops being a backend engineering detail and becomes an administrative design choice with constitutional consequences.

Public-service identity systems make that logic even clearer. The UK government’s March 2026 consultation says trusted digital identity is meant to help government match and verify existing information about people across multiple public services in responsible, privacy-enhancing ways, potentially via a universal unique identifier or similar approach, without creating a single database of all government data about a person [S321]. This is a strong signal that future coordination may depend less on one giant record than on **a governed ordering among multiple existing records**.

Healthcare already runs on such ordering. Medicare says that to change your official address with Medicare, you must contact Social Security because Medicare works with SSA to maintain your records [S307]. NHS Digital says the Personal Demographics Service is the national master database of all NHS patients in England, Wales, and the Isle of Man, holding core demographic details and the NHS number [S322]. The same service is used to identify patients and link them to care records across settings [S322]. PCSE’s National Back Office then exists as a national data-quality function for PDS, responsible for management of NHS numbers and PDS records and for resolving duplicates, confused records, and incorrect demographic data [S323]. These are not just data-cleaning facts. They reveal a layered order: a master demographic record, a national custodian, and downstream systems that defer.

Tax, immigration, and company law show the same structure. IRS TIN Matching lets authorized payers validate name-and-TIN combinations against IRS records before filing [S308]. USCIS SAVE is a standing service used by agencies to verify immigration status or citizenship for benefits and licenses [S313]. Companies House now requires identity verification to set up, run, own, or control a company in the UK, routes verification through GOV.UK One Login or an authorized corporate service provider, and links the verified identity back to a Companies House personal code used to connect the person to official roles on the register [S327]. The public register then becomes a downstream legal surface whose trust increasingly depends on upstream identity proofing plus the rules that bind those layers together [S318][S327].

Social Security’s own operating rules make the hierarchy more explicit. The January 2026 POMS update says SSA only corrects an existing NUMIDENT iteration when there is a documented keying error; otherwise it updates the record by creating a new appended iteration [S326]. That is a small but revealing governance choice: even correction is structured by rules about provenance, evidence, and the integrity of the authoritative record over time.

Taken together, these signals support the broader speculation that **authoritative-source hierarchies become hidden constitutions**. As more services depend on cross-checks, master records, unique identifiers, verified roles, and synchronized registries, practical sovereignty accumulates around the question of which dataset wins, which custodian may override, and how downstream systems inherit those decisions.

## Speculative consequences worth tracking

### 1. Registry custodians gain quiet constitutional power

The institution that maintains the authoritative record may acquire more practical influence than the front-end service the public thinks they are using.

### 2. Appeals migrate upstream

People may increasingly discover that the real remedy for a blocked service is not arguing with the local interface, but changing the upstream record or persuading the upstream custodian.

### 3. Integration increases dependence on precedence rules

The more governments and firms promise seamless, cross-service flows, the more they need explicit rules for which field, registry, or identifier is final when conflicts appear.

### 4. Local discretion shrinks

Frontline staff may lose room to improvise once synchronized systems require deference to master records, central identifiers, or proofing outcomes.

### 5. Unique identifiers become politically hotter

Debates about privacy, convenience, and fraud may increasingly collapse into fights over whether one identifier should coordinate more services and therefore expand the reach of a source-of-truth hierarchy.

### 6. Data-governance failures look constitutional, not clerical

A wrong address, duplicate person record, stale status field, or broken role link may matter because it places the user on the wrong side of the hierarchy that downstream systems obey.

## What could falsify or weaken the thesis

- Cross-system integration remains shallow enough that most services can still resolve conflicts locally without deferring to a stable upstream source.
- Institutions retain broad manual override powers, so precedence order exists on paper but does not actually govern real outcomes.
- Privacy and decentralization architectures push systems toward selective verification without strong master records or durable upstream hierarchies.
- Users gain portable attribute wallets that let them carry corrected status across domains more effectively than today’s registries do.
- Political resistance blocks universal identifiers and large-scale synchronization strongly enough that source-of-truth ordering stays fragmented and sector-specific.

## Research queue

- Which authoritative hierarchies are most rigid in practice: health, tax, immigration, pensions, corporate filing, banking, or education?
- Where are precedence rules explicit and published, and where are they only discoverable through failure and escalation?
- Which local services still retain meaningful override authority after a central source has spoken?
- Do unique identifiers reduce exclusion overall, or mainly shift exclusion upstream into proofing and source governance?
- Which institutions publish metrics on downstream error caused by stale upstream data, delayed propagation, or registry precedence mistakes?
