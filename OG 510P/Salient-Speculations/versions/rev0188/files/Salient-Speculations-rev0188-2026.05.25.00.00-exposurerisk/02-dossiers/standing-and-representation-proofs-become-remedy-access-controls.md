---
id: ss-0185-standing_and_representation_proofs_become_remedy_access_cont
revision_promoted: rev0185
title: Standing and representation proofs become remedy access controls
constellation:
- managed-legibility
- administrative-repair
- market-and-state-capacity
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- identity / credentials / delegated authority
- consumer services / transactions / redress
- platform moderation / content governance
- public services / eligibility
bottleneck_type:
- appealability / redress
- delegated authority
- subject identity matching
- privacy-preserving proof
enforcement_surface:
- platform governance
- consumer protection
- market-surveillance complaint
- data-rights operations
artifact_type:
- standing proof
- representative authority receipt
- subject-match proof
- scope grant
lifecycle_stage:
- notice
- intake
- standing-check
- evidence-request
- review
failure_modes:
- false-standing-denial
- overbroad-authority-demand
- representative-exclusion
- privacy-leaking-proof
- bot-filing-abuse
refactor_cluster:
- remedy-lifecycle
- authority-lifecycle
remedy_role: standing, subject identity, and representative authority
remedy_stage:
- notice
- intake
- standing-check
- evidence-request
- review
consolidation_status: standalone-mechanism
state_family:
- remedy
- authority
source_refs:
- S1541
- S1542
- S1544
- S1545
- S1550
- S1552
authority_role: delegate-representative and reviewer-auditor
authority_stage:
- present
- verify
- dispute
state_terms:
- delegate-unverified
- scope-limited
- disputed-authority
---
# Standing and representation proofs become remedy access controls

## Core claim

When remedies become operational infrastructure, the first disputed question is often not the merits. It is whether the filer is allowed to be there. Is the complainant the affected person, a buyer who relied on the packet, a supplier whose score changed, a consumer whose credit file was wrong, a parent, guardian, attorney, employee representative, trusted flagger, civil-society complainant, downstream recipient, platform user, or malicious stranger?

The speculative claim: **standing and representation proofs become remedy access controls**. Appeal systems will need structured proofs of affectedness, subject identity, reliance status, delegated authority, representative scope, and privacy permission. These proofs will govern who can file, see evidence, request a stay, receive correction notices, or escalate externally.

The archive already has delegated authority, recipient graphs, privacy proofs, identity-match appeals, and source-object identity warranties. This dossier connects them to the remedy door itself.

## Why this belongs in the cube

Redress systems fail in two opposite ways. They exclude legitimate parties because proving standing is hard, or they expose sensitive information because any claimant can pull records into a dispute. Both are infrastructure failures.

The DSA’s platform redress architecture distinguishes users, notifiers, internal complaint channels, and certified out-of-court dispute bodies [S1541, S1542, S1552]. AI Act complaints may be lodged by natural or legal persons with grounds to consider an infringement occurred [S1550]. Privacy restriction rights depend on the data subject and processing context [S1544]. Credit disputes depend on consumer, furnisher, and reporting-agency roles [S1545]. None of these roles map neatly onto the same credential.

The cube needs a general model: remedy access depends on proving the right relationship to the contested state.

## Likely proof classes

- **Subject proof** — I am the person, firm, product, record subject, account holder, or packet subject.
- **Affectedness proof** — the decision, score, restriction, or state change materially affected me.
- **Reliance proof** — I relied on this packet version, score, registry entry, or certificate.
- **Representative proof** — I am authorized to act for the subject, and my scope includes this remedy.
- **Guardian or fiduciary proof** — I can act where the subject lacks capacity or legal control.
- **Public-interest proof** — I can file because the regime allows trusted flaggers, civil-society actors, competitors, regulators, or legal persons.
- **Recipient proof** — I am entitled to amended notices without seeing the full recipient graph.
- **Confidential-review proof** — I may view sealed or redacted materials under a neutral access rule.

## Speculative consequences

### 1. Appeal portals become identity and authority portals

Remedy systems will integrate wallets, delegated-authority logs, representative rosters, account possession proofs, notarized authority, organizational roles, and role-masked proof credentials.

### 2. Standing denial becomes its own appeal category

A person may be denied not because the underlying decision is valid, but because the portal says they lack standing. That denial will itself need reasons, clocks, and escalation.

### 3. Privacy-preserving standing proofs become valuable

A buyer may need to prove reliance on a packet without revealing the deal. A user may need to prove affectedness without exposing all account activity. A representative may need to prove authority without showing unrelated powers.

### 4. Representative ecosystems professionalize

Small suppliers, disabled people, older adults, small creators, migrants, and low-resource consumers may depend on representatives. Whoever controls accepted representation proofs controls access to remedy.

## Abuse and capture

Standing proofs can become exclusion machines. A platform can demand impossible account access after lockout. A broker can require documentary evidence that only large counterparties possess. A state system can refuse representatives. Fraud actors can use synthetic authority to pull records. Competitors can weaponize public-interest complaint paths.

The remedy-lifecycle model therefore needs both inclusion and containment: low-friction entry for legitimate parties, strict evidence boundaries for access to sensitive material, and appealable denials of standing.

## Falsifiers

This thesis weakens if remedy systems remain simple account-holder workflows. It strengthens if dispute bodies, platforms, credit systems, AI deployers, product-passport resolvers, or procurement systems begin publishing accepted role credentials, representative-authority schemas, or standing-denial metrics.
