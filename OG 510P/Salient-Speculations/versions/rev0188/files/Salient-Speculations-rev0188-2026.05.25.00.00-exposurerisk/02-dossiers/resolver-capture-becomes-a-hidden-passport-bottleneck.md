---
id: ss-0182-resolver-capture
revision_promoted: rev0182
title: Resolver capture becomes a hidden passport bottleneck
constellation:
- managed-legibility
- standards-and-conformance
- anti-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- product identity / passports / traceability
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- source-of-truth precedence
- registry coverage
- provenance / custody
- fraud resistance
enforcement_surface:
- customs / market surveillance
- platform eligibility
- procurement / framework contract
- repair / warranty / resale workflow
artifact_type:
- resolver / pointer
- registry entry
- due-diligence statement
- state label
lifecycle_stage:
- publish
- route
- rely
- supersede
- archive
failure_modes:
- resolver-capture
- stale-redirect
- service-provider-succession
- subject-mismatch
- outage
refactor_cluster:
- provenance-lineage
lineage_role: resolver-operator and registry-steward
lineage_stage:
- resolve
- rely
- archive
state_family:
- provenance
state_terms:
- resolver-current
- resolver-suspect
consolidation_status: state-family-member
---
# Resolver capture becomes a hidden passport bottleneck

## Core claim

Digital Product Passports, due-diligence statements, repair records, recall statuses, and circularity claims are often discussed as if the core question is what data the passport contains. But most verifiers will not hold the whole record. They will scan, resolve, query, redirect, authenticate, and retrieve.

That makes the resolver a bottleneck. **Resolver capture becomes a hidden passport bottleneck** when the actor controlling the pointer layer can shape what a verifier sees, which version appears current, which service provider is reached, which jurisdictional view is displayed, which historical states are hidden, and which fallback path is available during outage, dispute, transfer, or issuer failure.

The passport is the visible object. The resolver is the gate to the object.

## Why this belongs in the archive

The EU's Ecodesign for Sustainable Products Regulation creates the framework for product passports, identifiers, data carriers, access rights, and registry functions [S1504]. The Commission's DPP consultation explicitly asks how passport data should be stored and managed by service providers and whether a certification scheme for service providers is needed [S1484]. GS1 Digital Link style infrastructure shows how identifiers, links, and resolvers can connect physical product identifiers to digital resources [S1491].

Those signals validate the archive's product-biography lane, but they also reveal the weak point: the route from physical product to authoritative current state is itself governable, capture-prone, and failure-prone.

A QR code on a product does not prove that the verifier reached the authoritative passport. A registry entry does not prove that all resolvers point to the current state. A service-provider certificate does not prove continuity after insolvency, acquisition, migration, revocation, sanctions, endpoint retirement, DNS loss, or jurisdictional blocking. The pointer layer has its own politics.

## Speculative consequences worth tracking

### 1. Resolver continuity becomes a service obligation

Passport service providers may need uptime, mirror, escrow, successor-map, and emergency-resolution obligations. A product's compliance state cannot depend on a dead URL, unmaintained API, expired domain, bankrupt vendor, or unsupported QR encoding.

### 2. Resolver neutrality becomes contested

Manufacturers, platforms, marketplaces, repair networks, recyclers, customs authorities, and consumers may want different views. A resolver may privilege the manufacturer's current marketing page, a regulator's compliance view, a repairer's diagnostic view, or a marketplace's resale view. Control over default routing becomes power.

### 3. Historical views become necessary

A verifier may need to know what the passport said at import, at first sale, at repair, at recall, at resale, and at destruction. If the resolver only returns current state, it can erase reliance history. If it returns too much, it creates privacy and trade-secret exposure.

### 4. Resolver trust lists become procurement inputs

Buyers may require products to use approved resolver services, certified passport providers, accepted identifier namespaces, or public fallback registries. That turns resolver membership into a market-access condition.

### 5. Resolver disputes become product disputes

If a passport is valid but unreachable, stale, misrouted, or controlled by the wrong successor, the product may become temporarily non-reliant. Disputes over the pointer can block the thing even when the underlying compliance data is sound.

## How this gets abused

- A provider redirects verifiers to favorable or incomplete views.
- A manufacturer hides repair or recall history behind role-gated endpoints.
- A marketplace caches old clean status after a recall.
- A malicious actor clones a resolver route and serves forged passport data.
- A dominant resolver operator raises fees or excludes smaller passport service providers.
- A buyer demands a resolver path that reveals unnecessary supplier relationships.

## Who pays, who saves, who captures

Manufacturers and importers pay for reliable passport resolution because market access may depend on it. Customs, regulators, repairers, and marketplaces save when resolver paths are standardized. Resolver operators, identity namespace controllers, and certified passport service providers can capture rents. Small suppliers are at risk if approved resolver participation becomes costly or technically complex.

## Near misses

- A digital passport is not a resolver governance system.
- A QR code is not a trust path.
- A URL is not an authoritative state unless conflict rules say it wins.
- A central registry is not enough if verifiers usually enter through private resolvers, cached marketplace views, or outdated product labels.

## Falsifiers

The thesis weakens if passport data is mostly embedded directly and remains static; if product passports are not used for customs, repair, recall, resale, or procurement decisions; if public registries provide free, authoritative, durable lookup that bypasses private resolver capture; or if standardization makes resolver governance boring, cheap, and neutral.

## Signals to watch

- Certification schemes for product-passport service providers.
- Contracts naming approved resolvers or fallback registries.
- Disputes over stale QR codes, dead passport endpoints, or service-provider succession.
- Marketplace rules requiring live passport lookup before listing.
- Insurance products for resolver continuity and passport availability.
