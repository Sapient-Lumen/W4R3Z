---
id: ss-0186-legal-person-wallets-organizational-authority
revision_promoted: rev0186
title: Legal-person wallets turn organizational authority into transaction evidence
constellation:
- managed-legibility
- standards-and-conformance
- market-and-state-capacity
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- data spaces / data sharing
- corporate services / company law
- payments / financial services
bottleneck_type:
- delegated authority
- organizational identity
- source-of-truth precedence
- verifier sufficiency
- fraud resistance
enforcement_surface:
- digital identity wallet acceptance
- procurement / framework contract
- data-space participation
- KYC / KYB
- audit / assurance engagement
artifact_type:
- legal-person wallet
- role attestation
- organizational authority chain
- electronic seal
- wallet-relying-party registration
lifecycle_stage:
- bind
- scope
- publish
- present
- verify
- act
- log
- revoke
failure_modes:
- role-drift
- orphaned-admin
- overbroad-employee-authority
- legal-person-subject-mismatch
- trust-anchor-capture
refactor_cluster:
- authority-lifecycle
authority_role: legal-person-controller and organizational-admin
authority_stage:
- bind
- scope
- publish
- present
- verify
- act
- log
consolidation_status: standalone-mechanism
state_family:
- authority
state_terms:
- authority-active
- scope-limited
- joint-approval-required
- delegate-unverified
- revoked
evidence_grade: E2-signal-cluster
decision_grade: DG-B
decision_total: 14
source_refs:
- S1553
- S1554
- S1555
- S1556
- S1557
---
# Legal-person wallets turn organizational authority into transaction evidence

## Core claim

Digital identity is often framed around individuals. But many high-stakes transactions are not done by individuals in their personal capacity. They are done by natural persons acting through organizations: employees, directors, officers, agents, administrators, procuration holders, contractors, professional representatives, service accounts, bots, and AI agents.

The speculative claim: **legal-person wallets turn organizational authority into transaction evidence**. As wallet ecosystems and verifiable credentials extend to legal persons, the central object becomes the chain from organization to role to natural person to device or agent to action.

## Why this belongs in the cube

The EUDI framework defines electronic identification schemes as covering natural persons, legal persons, and natural persons representing other natural or legal persons [S1555]. It also defines person identification data as enabling establishment of the identity of a natural or legal person, or a natural person representing another natural person or legal person [S1555]. This is a strong signal that organizational authority will not remain a paperwork appendix. It will become part of the presentation and verification path.

The same framework defines relying parties, wallet-relying-party registration certificates, access certificates, authentic sources, electronic attestations of attributes, and trusted-list repositories [S1555]. That ecosystem gives organizational authority a place to live: not merely “the company logged in,” but “this person, under this legal person, with this role, through this wallet or relying-party registration, may request or assert this attribute.”

NIST's identity guidance covers proofing, authentication, federation, and assertions [S1556]. W3C Verifiable Credentials model claims by issuers, held and presented to verifiers, with metadata such as issuer, validity, verification material, and status [S1557]. Together these signals point to a growing technical vocabulary for organizational authority chains.

## The missing chain

A transaction-grade organizational authority proof may need to answer:

1. Does the legal person exist?
2. Which authentic source says so?
3. Is the natural person bound to that legal person?
4. What role do they hold?
5. Who granted that role?
6. Does the role include the action?
7. Is approval joint, separate, amount-limited, time-limited, branch-limited, or matter-limited?
8. Is the presentation coming from an authorized wallet, device, service account, or agent?
9. Has the role been revoked, suspended, or expired?
10. Can a relying party verify without overcollecting internal corporate data?

## Likely artifacts

- legal-person wallet units;
- role attestations;
- employee authority credentials;
- electronic seals;
- board-resolution proofs;
- procurement-signing authority receipts;
- authorized-representative chains;
- service-account authority maps;
- organizational revocation lists;
- wallet-relying-party registration certificates;
- trust-list status histories.

## Speculative consequences

### 1. KYB becomes transaction-specific

Know-your-business checks will not stop at beneficial ownership or company status. Relying parties may require proof that the presenting person or agent can perform the particular act.

### 2. Procurement shifts from signature images to authority chains

A signed PDF is weak evidence compared with a verifiable chain showing legal person, role, scope, time, and transaction context.

### 3. Service accounts become corporate actors

Many organizational actions will be taken by systems. Legal-person wallets may force firms to maintain clearer links between service accounts, responsible humans, policy engines, and legal entities.

### 4. Internal role governance leaks outward

A company's internal authorization model becomes externally visible when third parties depend on role attestations. That can improve trust but also create privacy, surveillance, and competitive-intelligence risks.

### 5. Corporate authority failures become replayable

If a transaction is disputed, the question will be reconstructable: which authority chain was presented, what did the verifier check, and what state was current at the time?

## Abuse and failure modes

- dormant employees retain wallet-based signing power;
- broad “admin” roles substitute for scoped authority;
- service accounts act without attributable human responsibility;
- small businesses cannot maintain compliant authority chains;
- parent/subsidiary relationships are misrepresented;
- internal role data is over-disclosed to relying parties;
- trusted-list or access-certificate operators become hidden chokepoints.

## What would make this decision-grade

- legal-person wallet pilots move into procurement, payments, customs, data-space participation, or public filing;
- relying parties require role attestations rather than static appointment documents;
- audit firms or insurers ask for organizational authority-chain logs;
- disputes arise over whether a wallet-presented employee had authority to bind a company.

## Near miss / not this

A company login is not a legal-person authority wallet. The thesis requires a verifiable chain from legal person to actor to scope to action.
