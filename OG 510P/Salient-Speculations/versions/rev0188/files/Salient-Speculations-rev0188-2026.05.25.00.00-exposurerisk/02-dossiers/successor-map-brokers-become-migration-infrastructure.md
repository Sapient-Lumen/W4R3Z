---
id: ss-0183-successor-map-brokers-become-migration-infrastructure
revision_promoted: pre-rev0180
title: Successor-map brokers become migration infrastructure
constellation:
- place-and-climate
- standards-and-conformance
- model-governance
- managed-legibility
- market-and-state-capacity
status: dossier
maturity: S3-enforcement-surface
confidence: medium-low
time_horizon: mixed
domain:
- climate / retreat / habitability
- land / parcel / place-proof
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- insurance / risk transfer / underwriting
bottleneck_type:
- conformance capacity
- interoperability translation
- version / support-window compatibility
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- underwritability
- small-actor evidence capacity
enforcement_surface:
- permit / license
- title / conveyancing / property transfer
- underwriting / insurance renewal
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
- lending covenant / credit agreement
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
- municipality
- insurer
- property-owner
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
- supplier
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- small-supplier-burden
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
---
# Successor-map brokers become migration infrastructure

**Thesis:** once machine-readable ecosystems begin exposing retirement notices, replacement IDs, alias relations, duplicate-record handoffs, upstream pointers, and change/deletion manifests, downstream teams stop treating succession as something they can resolve case by case. They increasingly need maintained brokers that tell them what now governs, how strong the replacement claim is, what should be mirrored or pinned, and how to cross the gap without breaking automation. At that point, successor-map brokers become migration infrastructure.

## Core claim

The archive has already argued that **machine-readable retirement notices become a buyer-control surface**, **feed-escrow continuity services become a new intermediary market**, and **compatibility shims become strategic intermediaries**. Those dossiers explain how a relied-on source can stop governing, why continuity layers appear when publishers or endpoints are unstable, and how bridge operators gain power during incompatible transitions. But they still leave one practical migration problem under-described: *who tells a consumer what now counts as the replacement, alias, or canonical successor across partially overlapping ecosystems?*

The current documentation shows that the ingredients of successor mapping are no longer hypothetical. NVD’s deprecated-products API says a deprecated CPE is one that has been replaced by one or more other CPEs and that the `deprecatedBy` element identifies the replacements [S973]. Its public CPE detail pages expose that remap concretely; for example, the deprecated `json-java_project` CPE points to a `stleary` replacement CPE [S974]. NVD’s record-level lifecycle handling goes further: rejected duplicate CVEs can explicitly tell users not to use the old identifier and to reference a different CVE instead [S977]. These are not generic deprecation blog posts. They are structured handoff signals attached to operational identifiers.

Other ecosystems expose adjacent pieces of the same problem. The OSV schema defines `withdrawn`, `aliases`, `upstream`, and `related` fields, which means that withdrawal state, cross-database identity, and upstream/downstream reference structure are already part of the intended machine-readable object model [S975]. OSV.dev then adds operational distribution behavior on top of that model: it publishes `modified_id.csv` for incremental tracking, excludes withdrawn records from some query surfaces while still preserving them in direct lookup and exports, and currently handles deleted upstream records differently depending on source type [S976]. It also says it prefers not to act as a broker between downstream consumers and upstream sources [S976]. That is a revealing signal. The ecosystem already knows a brokerage function exists; one major operator is simply saying that it does not want to own that role.

Supplier-side advisory systems are publishing lifecycle clues too. Red Hat’s CSAF advisory tree publishes `changes.csv`, `deletions.csv`, `releases.csv`, and `archive_latest.txt` alongside the advisory corpus [S952]. Red Hat also states that OVAL is deprecated for vulnerability scanning applications and that CSAF is its successor [S954]. Those documents provide essential migration facts, but they do not by themselves solve the downstream crosswalk problem. A consumer still has to connect the format succession, the changed endpoint, the deleted record, the deprecated identifier, the duplicate CVE, the archived copy, and the local query or policy engine that still expects yesterday’s namespace.

That is why the emerging bottleneck is best understood as a **successor-map broker**. A successor-map broker is a maintained remap layer that ingests retirement and replacement signals from many authoritative systems and emits actionable handoff guidance: which identifier supersedes which, whether the relation is strict replacement or only rough equivalence, whether the old object remains queryable, how long overlap lasts, where archives live, which replacement is most authoritative, and what automation should do next. Once buyers, scanners, dashboards, compliance tools, and migration programs start depending on that layer, successor mapping stops being clerical cleanup and becomes infrastructure.

## Why this belongs in the archive

This thesis belongs here because it names the coordination layer that appears after retirement signaling but before universal translation. Retirement notices tell consumers that something has changed. Translation services help incompatible systems continue talking. Successor-map brokers sit between them: they answer the narrower but unavoidable question of *what now stands in for what just stopped governing?*

That pattern is broader than vulnerability data. Any machine-readable governance stack eventually accumulates renamed fields, deprecated endpoints, merged categories, withdrawn entries, duplicate IDs, successor schemas, and partial upstream/downstream mirrors. At first, specialists resolve those transitions manually. Later, the volume of change and the number of dependent systems force the market to externalize the handoff logic into maintained maps. When that happens, the power center moves toward whoever curates the successor chain.

## Speculative consequences worth tracking

### 1. Buyer tools start scoring remap quality

Procurement and assurance workflows may increasingly ask not only whether a vendor publishes machine-readable evidence, but whether it publishes enough lifecycle metadata for a broker to build a reliable successor map without hand curation.

### 2. Equivalence strength becomes a first-class field

Successor brokers may increasingly need to distinguish strict replacement, likely replacement, alias, upstream reference, bundled replacement, and historical archive-only continuation, because downstream automation cannot safely treat those as the same thing.

### 3. Migration queues become partially automated

Security platforms, registry browsers, or policy engines may increasingly consume successor maps to decide when to pin old identifiers, when to mirror retired sources, when to rewrite local references, and when to surface a human review step.

### 4. Successor freshness becomes a trust signal

A stale successor map may increasingly look like a service defect, because downstream teams can make the wrong replacement choice even when every individual upstream source is technically publishing the relevant fragments.

### 5. Brokers acquire quiet standard-setting power

If a broker becomes widely used, its judgments about which replacement is canonical, how duplicate chains collapse, and which alias relations are strong enough to automate may begin acting like de facto policy.

### 6. Archive access and migration access converge

Mirror operators, archive providers, and successor brokers may increasingly converge into one class of intermediary, because a reliable handoff often depends on both knowing the successor and preserving the predecessor long enough to verify the migration.

### 7. The pattern spreads beyond software security

Once this stabilizes, similar broker layers may appear for standards profiles, conformance suites, schema registries, identity lists, public-service forms, model governance artifacts, and policy taxonomies wherever machine-readable authority keeps changing names faster than dependent systems can keep up.

## What could falsify or weaken the thesis

- Most ecosystems converge on sufficiently stable identifiers and endpoints that successor resolution remains rare enough to stay local.
- Official publishers begin shipping complete, interoperable successor metadata that downstream tools can consume directly without third-party remap layers.
- Local operators remain willing to perform migration mapping by hand because the operational cost of a separate brokerage layer exceeds the benefit.
- Downstream systems mostly fall back to archives or mirrors and do not need to know which successor governs so long as old data remains retrievable.
- The replacement relations prove too ambiguous or politically contested to support durable automation.

## Research queue

- Which ecosystems first publish explicit machine-readable replacement strength rather than only raw successor pointers?
- Do buyers or scanners begin storing brokered successor maps locally the way they store vulnerability feeds, trust bundles, or mirrors?
- Which fields become standard in practice: replacement type, confidence, overlap window, archive URI, issuer, signature, or last-validated timestamp?
- Where do successor-map errors first become visible incidents: false rewrites, duplicate collapse mistakes, stale archive pointers, or broken policy references?
- Which adjacent domains first need the same layer most urgently: standards catalogs, identity registries, model-governance schemas, or public-service administrative records?
