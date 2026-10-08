---
id: ss-0186-authority-scope-crosswalks
revision_promoted: rev0186
title: Authority-scope crosswalks become interoperability infrastructure
constellation:
- managed-legibility
- standards-and-conformance
- administrative-repair
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- identity / credentials / delegated authority
- public services / eligibility
- consumer services / transactions / redress
- data spaces / data sharing
- AI / model governance / automated decisions
bottleneck_type:
- delegated authority
- interoperability translation
- verifier sufficiency
- selective disclosure / minimization
enforcement_surface:
- digital identity wallet acceptance
- procurement / framework contract
- platform eligibility
- audit / attestation / assurance
- consumer protection
artifact_type:
- scope grammar
- authority matrix
- scope crosswalk
- disclosure policy
- nondelegable-action list
lifecycle_stage:
- define
- scope
- present
- verify
- act
- dispute
failure_modes:
- scope-inflation
- false-authority-denial
- nondelegable-action-leakage
- privacy-overcollection
- semantic-mismatch
refactor_cluster:
- authority-lifecycle
authority_role: scope-translator and verifier-relying-party
authority_stage:
- define
- scope
- verify
- dispute
consolidation_status: standalone-mechanism
state_family:
- authority
state_terms:
- scope-limited
- nondelegable-action
- step-up-required
- verifier-unregistered
evidence_grade: E3-artifact-live
decision_grade: DG-A
decision_total: 16
source_refs:
- S1553
- S1554
- S1555
- S1556
- S1557
- S1562
- S1563
---
# Authority-scope crosswalks become interoperability infrastructure

## Core claim

The hard part of delegated authority is no longer just proving that a delegate exists. It is translating what the delegate may do across systems that use different action grammars.

A power, role, mandate, wallet attestation, employee credential, guardian relationship, professional representation, OAuth scope, or AI-agent permission may all claim to authorize action. But the operational question is more exact: can this actor **read**, **download**, **disclose**, **sign**, **submit**, **settle**, **pay**, **waive**, **appoint another actor**, **withdraw a claim**, **receive notice**, **bind a legal person**, or **trigger a remedy clock**?

The speculative claim: **authority-scope crosswalks become interoperability infrastructure**. As wallets, portals, agent systems, data spaces, and representative accounts spread, the scarce object becomes a shared translation layer between one system's authority vocabulary and another system's transaction grammar.

## Why this belongs in the cube

The archive already has `scope-crosswalk-services-become-quiet-comparability-brokers`, but that dossier is broad. This one narrows the mechanism to **action authority**. In authority systems, semantic mismatch is not merely annoying. It can produce unlawful disclosure, denied care, invalid filings, unauthorized purchases, irreversible waivers, or impossible appeals.

The EUDI framework already defines attributes as including a characteristic, quality, right, or permission of a natural or legal person or object [S1555]. It also models users as natural or legal persons, or natural persons representing other natural persons or legal persons [S1555]. That is a strong signal that identity wallets cannot remain mere ID cards. They will carry permissions and representational states.

But a permission is not yet a cross-system action. A tax representative's ability to inspect confidential information [S1562] does not automatically map to a healthcare proxy's authority to make a decision, a parent's educational-platform authority, a corporate employee's authority to sign a procurement statement, or an AI agent's authority to execute a tool call. GOV.UK's LPA guidance distinguishes conditions, joint versus separate decisions, confidentiality, and limits on use [S1563]. NIST's digital identity guidelines formalize identity proofing, authentication, federation, and assertions, but those functions still need application-specific action semantics [S1556].

That gap is where scope crosswalks become infrastructure.

## Likely artifacts

- authority-scope taxonomies;
- nondelegable-action lists;
- scope-to-transaction maps;
- role-to-action maps;
- wallet disclosure policies;
- action-risk classes;
- representative-type matrices;
- step-up trigger tables;
- cross-regime scope dictionaries;
- machine-readable “cannot bind principal” markers;
- reusable authority translation reports.

## Speculative consequences

### 1. Scope vocabularies become policy battlegrounds

The fight will not only be about whether a representative exists. It will be about which verbs count as equivalent. “Manage account” may be too broad. “View correspondence” may be too narrow. “Submit application” may or may not include “certify truth,” “appeal denial,” or “accept settlement.”

### 2. Overbroad scopes become a compliance smell

Portals that use crude all-or-nothing delegation will look increasingly unsafe. Procurement, insurance, and regulators may start asking whether systems support granular scopes, nondelegable actions, high-risk step-up, and revocation propagation.

### 3. Wallet acceptance creates translation pressure

If a wallet can present a right, permission, professional qualification, or representational relationship, relying parties need to map that presentation into local transaction rights. Wallet proof alone will not resolve the meaning of the action.

### 4. AI-agent permissions inherit the same problem

A tool permission such as “book travel” hides many acts: search, reserve, pay, accept cancellation terms, disclose passport data, buy insurance, select seat, or waive refund rights. Agentic systems will need scope crosswalks just as public services do.

### 5. Scope translation becomes a small-actor burden

Large institutions will build policy engines. Small firms, carers, attorneys, clinics, NGOs, and small suppliers may need intermediaries that package authority scopes into acceptable proof bundles.

## Failure modes

- **Scope inflation** — a narrow grant is treated as broad authority.
- **Scope collapse** — a valid grant is rejected because the receiving system cannot represent it.
- **Nondelegable-action leakage** — a system permits an action that cannot legally or ethically be delegated.
- **Semantic substitution** — one system maps “manage” to “bind” without explicit consent.
- **Privacy-overcollection** — a verifier requests the full authority document instead of the minimum scope proof.
- **Stale crosswalk** — policy changes but old mappings keep granting actions.

## What would make this decision-grade

- wallet or portal ecosystems publish common authority-scope taxonomies;
- procurement asks vendors to demonstrate delegation-scope controls;
- courts, regulators, or auditors reject actions because a scope mapping was wrong;
- AI-agent authorization profiles start carrying structured task and action constraints;
- representative portals expose machine-readable nondelegable-action or step-up lists.

## Near miss / not this

A menu of account permissions is not an authority-scope crosswalk unless it translates a legally or institutionally meaningful authority relationship into a transaction-specific action rule.
