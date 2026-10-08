---
id: ss-0183-successor-map-freshness-guarantees-become-a-service-metric
revision_promoted: pre-rev0180
title: Successor-map freshness guarantees become a service metric
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
migration_status: inferred-rev0183-minimal+freshness-reviewed
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
refactor_cluster:
- evidence-freshness
freshness_role: successor-map lag budget
consolidation_status: standalone-mechanism
state_family:
- freshness
freshness_clock:
- validated_at
- relied_at
state_terms:
- successor-gap
- superseded-prospective
---
# Successor-map freshness guarantees become a service metric

**Thesis:** once downstream systems begin depending on maintained remap layers to traverse deprecated CPEs, duplicate CVEs, withdrawn records, renamed products, replacement endpoints, and archive handoffs, the important question stops being only whether a successor map exists. It becomes whether that map is **fresh enough to trust operationally**. When upstream ecosystems already publish last-modified timestamps, incremental change files, update-check intervals, archive pointers, and relocation changelogs, remap staleness becomes measurable. At that point, successor-map freshness guarantees become a service metric.

## Core claim

The archive has already argued that **machine-readable retirement notices become a buyer-control surface**, **successor-map brokers become migration infrastructure**, **feed-escrow continuity services become a new intermediary market**, and **conformance-regression alerts become contract triggers**. Those dossiers explain how machine-readable sources are withdrawn, why handoff layers appear, and how visible breakage eventually becomes a routed event. But they still leave one practical reliability question under-described: *how fresh does a successor map need to be before a downstream team can automate against it?*

Current documentation makes that question unusually concrete. NVD's developer guidance says that after initial population, users should maintain local repositories with `lastModStartDate` / `lastModEndDate` updates, no more than once every two hours, and that enterprise-scale implementations should centralize this practice so all users stay in sync with the latest CVE, CPE, and CPE match-criteria information [S987]. The NVD Product API documentation reinforces that point by saying a CPE record is considered modified not only when created or edited, but also when deprecated, and that deprecated CPEs can carry a `deprecatedBy` replacement relation [S973]. In other words, the replacement layer is already embedded in a stream of timestamped mutation, not a static dictionary.

OSV exposes the same operational pattern in a different form. Its data-download documentation says users can efficiently download only new or updated records through `modified_id.csv`, that both top-level and per-ecosystem files are published, and that the CSVs are sorted in reverse chronological order specifically so consumers can stop once they reach a timestamp they have already processed [S988]. That is not merely an export convenience. It is an explicit acknowledgment that downstream correctness depends on update cadence and replay position.

Red Hat's security-data surfaces push the pattern further toward service semantics. The live CSAF advisory tree publishes `changes.csv`, `deletions.csv`, `index.txt`, `releases.csv`, and `archive_latest.txt` with visible modification times [S952]. Its security-data changelog then says the published advisory archives are refreshed once a week and that updates made after the archive date should be fetched from individual files using `changes.csv` [S989]. That is effectively a freshness contract: the consumer is being told which surfaces are batch snapshots, which are incremental deltas, and how to combine them without drifting behind.

The VEX Repository Specification shows the same logic at the repository-design layer. It requires an `update_interval` in `vex-repository.json`, requires `index.json` to expose an `updated_at` timestamp, and tells clients to store the last successful update time locally when deciding whether to check for new data [S966]. That is direct evidence that ecosystem designers already treat freshness as a first-class, machine-usable property of a maintained evidence repository.

Taken together, these sources point to the next bottleneck above successor-map brokerage: **freshness guarantees for the handoff layer itself**. A buyer, scanner, migration tool, or compliance dashboard may already know how to read a replacement relation. The harder question is whether that relation was refreshed quickly enough to reflect a newly deprecated CPE, a duplicate-CVE collapse, a relocated security-data endpoint, a withdrawn upstream record, or a replacement pointer that only became visible this morning. Once downstream teams start relying on remap layers to make automated decisions, stale maps begin to look less like normal catalog drift and more like service defects.

That is why the next bottleneck is best understood as a **successor-map freshness guarantee**. This is not just a timestamp on a file. It is a maintained claim about update tempo, lag, and validation recency for the map that says what now stands in for what no longer governs. Once buyers and operators care about that claim, successor-map freshness stops being metadata and becomes a service metric.

## Why this belongs in the archive

This thesis belongs here because it names the reliability layer that appears after successor brokerage. First, ecosystems publish retirement and replacement fragments. Then brokers reconcile those fragments into usable handoff maps. After that, the bottleneck shifts again: not every map that exists is current enough to trust. The scarce capability becomes proving that a remap layer is recent, monitored, and synchronized closely enough to be operationally admissible.

That pattern is broader than software vulnerability data. Any machine-readable governance stack that evolves through deprecation, aliasing, duplicate collapse, renamed authorities, moved endpoints, or changing canonical references eventually creates the same question: *how stale is too stale for a maintained map of what now counts?* Once that threshold matters, freshness guarantees become part of the governance surface.

## Speculative consequences worth tracking

### 1. Buyers start asking for map-lag budgets

Suppliers and intermediaries may increasingly be asked not only whether they publish successor metadata, but what their worst-case lag is for reflecting upstream deprecations, replacements, withdrawals, or archive moves.

### 2. “Last validated” becomes more important than “last generated”
A useful map may increasingly need to publish when a successor relation was last checked against upstream authority, not only when the local file was last rewritten.

### 3. Stale-map incidents become recognizable outage classes

Downstream breakage may increasingly be blamed on successor-map lag even when every upstream publisher technically exposed the necessary raw signals.

### 4. Freshness classes emerge

Intermediaries may increasingly label handoff data as near-real-time, daily, weekly snapshot-plus-delta, archive-only, or unverified historical, because downstream automation cannot treat those classes as equivalent.

### 5. Audit trails shift from content correctness to tempo correctness

More disputes may center on whether a broker updated quickly enough after an upstream change, deletion, or replacement notice, rather than only whether the final remap relation was logically correct.

### 6. Continuity and freshness converge

Mirror operators, archive providers, and successor-map brokers may increasingly converge into a combined layer that preserves old data while also proving how recently its handoff instructions were revalidated.

### 7. The pattern spreads beyond security data

Similar freshness guarantees may appear for standards catalogs, schema registries, model-governance artifacts, identity lists, benefits eligibility tables, and public-service record crosswalks wherever outdated handoff logic can silently misroute automation.

## What could falsify or weaken the thesis

- Downstream teams tolerate large successor-map lag and continue treating stale remap data as a minor inconvenience rather than a reliability issue.
- Authoritative publishers begin shipping complete, timely, and directly consumable replacement metadata, leaving little room for separate freshness guarantees on broker layers.
- Most migrations remain sparse enough that teams can manually verify replacements at the moment of need.
- Archive access and predecessor availability matter more than remap recency, so preserving old data is enough even when successor maps drift.
- Successor relations remain too ambiguous to support meaningful freshness commitments beyond “best effort.”

## Research queue

- Which ecosystems first publish explicit freshness SLOs or lag dashboards for remap layers rather than leaving consumers to infer freshness from file timestamps?
- Which metric becomes standard in practice: maximum upstream-to-map lag, median lag, last-validated timestamp, freshness class, or per-relation confidence age?
- Where do stale successor maps first become visible incidents: deprecated CPE rewrites, duplicate-CVE handoffs, relocated endpoint pointers, or archive-only fallbacks?
- Do buyers start testing successor freshness the way they test replay fixtures, feed uptime, or conformance results?
- Which adjacent domains first need freshness guarantees most urgently: standards profile catalogs, identity registries, public forms, or model-governance schemas?
