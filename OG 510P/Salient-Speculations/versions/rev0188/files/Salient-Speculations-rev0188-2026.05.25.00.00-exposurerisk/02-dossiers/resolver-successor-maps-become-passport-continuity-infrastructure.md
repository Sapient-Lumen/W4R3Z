---
id: ss-0187-resolver-successor-maps
revision_promoted: rev0187
title: Resolver-successor maps become passport-continuity infrastructure
constellation:
- managed-legibility
- standards-and-conformance
- resilience-and-continuity
status: dossier
maturity: S3-enforcement-surface
confidence: medium-high
time_horizon: near
domain:
- product identity / passports / traceability
- standards / interoperability / conformance
- repair / warranty / resale workflow
- customs / market surveillance
bottleneck_type:
- resolver continuity
- source-of-truth precedence
- registry coverage
- fallback / graceful degradation
- admissible evidence
enforcement_surface:
- customs / market surveillance
- repair / warranty / resale workflow
- procurement / framework contract
- platform eligibility / ranking
artifact_type:
- resolver-successor map
- registry pointer
- linkset archive
- service-provider continuity certificate
lifecycle_stage:
- resolve
- transfer
- supersede
- archive
- rely
failure_modes:
- resolver-capture
- stale-redirect
- service-provider-succession
- dead-link
- wrong-granularity
refactor_cluster:
- provenance-lineage
lineage_role: resolver-operator and registry-steward
lineage_stage:
- resolve
- transfer
- supersede
- archive
state_family:
- provenance
- freshness
state_terms:
- resolver-current
- resolver-suspect
- resolver-successor-declared
- archive-evidentiary
consolidation_status: standalone-mechanism
evidence_grade: E3-artifact-live
decision_grade: DG-A
decision_total: 17
source_refs:
- S1574
- S1575
- S1576
---
# Resolver-successor maps become passport-continuity infrastructure

## Core claim

Digital product passports, repair records, recall status, sustainability claims, customs declarations, and resale diligence will not be reached by magic. They will be reached through identifiers, data carriers, registries, resolvers, APIs, default links, linksets, mirrors, service providers, and jurisdiction-specific views. The prior archive named the hidden bottleneck: resolver capture. The next bottleneck is continuity after the resolver changes.

**Resolver-successor maps become passport-continuity infrastructure** when the market needs a reliable way to know that a physical product, batch, serial number, repair event, recall notice, or end-of-life record has moved from one resolver, service provider, endpoint, registry, brand owner, importer, or data host to another without losing its evidentiary identity.

The map is not a redirect convenience. It is the chain of custody for the route to the object.

## Why this belongs in the archive

GS1 Digital Link and GS1-Conformant Resolver material make the institutional shape visible. A product identifier encoded in a Web URI can lead to one or more sources of information; a resolver may redirect to a default link or return a linkset; the same identifier can be resolved at different granularities; a resolver has to distinguish bad syntax from no information; and resolver-description material can disclose capabilities [S1574][S1575]. The European Commission's Digital Product Passport consultation asks how passport data should be stored and managed by service providers and whether certification for service providers is needed [S1576].

Together those signals imply a continuity problem. If the service provider goes bankrupt, a brand is acquired, a domain expires, a registry is migrated, an importer changes, a market-surveillance authority suspends access, or a passport host is decertified, the data carrier on the physical item still points somewhere. The verifier needs to know where it should point now and whether the successor path preserves historical reliance.

## Speculative consequences worth tracking

### 1. Successor maps become procurement terms

Large buyers may require product-passport providers to maintain successor maps, escrow resolver tables, publish linkset history, and support a regulator-access fallback. A product may be ineligible for certain channels if its passport depends on a single unescrowed resolver.

### 2. Historical resolver views become diligence surfaces

A customs officer, repairer, buyer, insurer, recycler, or court may need to know not only the current passport but what the resolver returned on a prior date. Linkset snapshots become evidence.

### 3. Service-provider certification expands into continuity certification

Certification may not stop at security and availability. It may include handoff obligations, insolvency procedures, export formats, successor-record signing, and time-bounded mirror operation.

### 4. Resolver capture becomes a takeover vector

A successor who controls the default link can bury recall notices, privilege a warranty channel, hide repair data, route to a marketplace, or create a jurisdiction-specific view. Successor maps should therefore include who authorized the change and what view classes changed.

## Abuse and burden

Resolver-successor maps can be abused by incumbents to lock in service providers, by counterfeiters to make fake product histories look persistent, or by platforms to require approved resolver networks. Small suppliers may face a hidden tax: proving continuity long after a product has moved through distributors, repairers, refurbishers, and recyclers.

## Falsifiers

The thesis weakens if product passports are implemented as centralized regulator registries with no material resolver competition, if historical linkset states are rarely used in enforcement or disputes, or if service-provider continuity stays outside procurement, certification, and insurance language.
