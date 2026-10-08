# 016 — Status surfaces and the end of one-time verification

**Status:** canon

## Thesis

As machine-verifiable governance stacks spread, more institutions will stop treating issuance-time checks, uploaded copies, and once-approved counterparties as sufficient.
The operative question shifts from “were you valid when this was issued?” to “what is your current standing right now?”

The scarce asset is increasingly not just the proof, the query, the relay, or the digitally structured event.
It is the live status surface that says whether the issuer is still trusted, the credential is still unrevoked, the representative still holds the role, the endpoint can still receive the document, the verifier is still authentic, or the product passport still exists in the relevant registry.

## Why it matters

Older administrative systems tolerated stale proofs because updating validity was slow, expensive, and often impossible at the moment of use.
Digital governance stacks change that.
Once credentials, providers, products, and participants become machine-readable, institutions can ask a more demanding question at runtime: is the relevant thing still in force **now**?

That changes where leverage sits.
A person, firm, or object can hold a seemingly valid document and still fail in practice if a linked status surface says the issuer has lost standing, the role has changed, the certificate has been revoked, the participant metadata has moved, or the registry cannot confirm existence.
Status publication, revocation, suspension, and live discovery become hidden infrastructure for admissibility.

This note is not the same as proof surfaces, query surfaces, or relay surfaces.
Proof surfaces ask what can be presented.
Query surfaces ask whether current evidence can be retrieved from an authoritative source.
Relay surfaces ask which operator is trusted to carry the message.
Status surfaces ask whether the relevant credential, provider, verifier, participant, product, or delegated role is **currently** in good standing.

## Mechanism sketch

- In the eIDAS trust-services stack, Member States must establish and publish trusted lists containing qualified trust service providers and their qualified trust services, and those lists are published in signed or sealed formats suitable for automated processing.
- In the W3C credential stack, Bitstring Status List v1.0 standardises status publication for revocation and suspension, making current standing a normal machine-checkable part of credential verification rather than a purely administrative afterthought.
- In EUDI wallet proximity scenarios, verifier authentication itself depends on service provider certificates and trusted lists. The verifier is not simply assumed to be legitimate because it asks.
- In Peppol, current network standing is not static onboarding paperwork. The SML tells an Access Point which SMP to connect to; the SML management interface supports adding, updating, removing, and migrating participant metadata; and Peppol provider certificates can be revoked when providers breach their agreements.
- In digital product passport rollout for detergents and surfactants, customs authorities are expected to automatically verify that a passport reference exists in the registry, confirm the identifier and commodity code against registry data, and use that interconnection for border controls and risk management.
- In the vLEI role-credential stack, a Legal Entity Official Organizational Role credential must be revoked if the person no longer holds the role or leaves employment, revocation events must be reported through the vLEI Reporting API, and GLEIF must remove the credential details from the Legal Entity’s public LEI page when revocation is reported.

The deeper pattern is that many institutions no longer want merely a good-enough proof of prior validity.
They want a status-bearing object that can survive a live standing check.
As more systems become machine-readable, runtime admissibility starts depending on revocation feeds, trusted lists, capability metadata, and registry-confirmed current state.

## What this speculation predicts

1. More regulated workflows will require live status checks at the moment of presentation, routing, or clearance rather than accepting static copies, stale exports, or issuance-time approvals as sufficient.
2. Operational failures in status infrastructure — stale registries, sync gaps, false revocations, broken trust lists, or directory outages — will increasingly become first-order governance incidents rather than mere back-office bugs.
3. Economic power will accumulate around the operators and vendors who can publish, synchronize, cache, monitor, and contest live standing across credentials, products, endpoints, and delegated authority chains.
4. People and firms will increasingly discover that “having the credential” is not enough; what matters is whether every linked status surface is green at the moment of use.
5. Policy conflict will intensify around offline grace periods, privacy-preserving status checks, appeal rights after erroneous suspension, and whether institutions may demand continuous reachability to central status infrastructure.

## Watchpoints

- official systems adding machine-readable trusted lists, revocation APIs, credential status endpoints, or registry lookups as explicit runtime requirements
- more workflows where product clearance, identity verification, signature acceptance, or network routing depends on status checks performed at transaction time
- public incidents involving stale metadata, false revocation, registry outages, or inability to prove current standing after an otherwise valid issuance
- regulatory fights over caching, offline fallback, privacy, or due process when live status infrastructure becomes mandatory
- signs that static documents, annual certifications, or cached exports remain good enough in practice and live status never becomes a durable condition of admissibility

## What would weaken this

- most high-trust workflows continuing to accept issuance-time evidence without meaningful runtime status checking
- status publication remaining fragmented, optional, or too unreliable to become a reusable cross-domain infrastructure layer
- institutions preferring periodic re-attestation or fresh re-issuance over live standing checks at the point of use
- strong policy pushback successfully treating central status infrastructure as too privacy-invasive, failure-prone, or anti-competitive to become normal governance practice

## Source anchors

- [SRC-079](../00-meta/bibliography.md#src-079)
- [SRC-080](../00-meta/bibliography.md#src-080)
- [SRC-081](../00-meta/bibliography.md#src-081)
- [SRC-082](../00-meta/bibliography.md#src-082)
- [SRC-083](../00-meta/bibliography.md#src-083)
- [SRC-084](../00-meta/bibliography.md#src-084)
- [SRC-085](../00-meta/bibliography.md#src-085)
