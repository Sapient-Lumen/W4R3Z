---
id: ss-0183-orphan-state-inventories-become-reconciliation-backlogs
revision_promoted: pre-rev0180
title: Orphan-state inventories become reconciliation backlogs
constellation:
- model-governance
- managed-legibility
- maintenance-and-repair
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
bottleneck_type:
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
- model-provider
- buyer
- auditor
- broker
- source-vendor
- operator
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
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
---
# Orphan-state inventories become reconciliation backlogs

**Thesis:** once records can remain **withdrawn but retrievable**, **rejected but visible**, **deprecated with partial remap data**, **deleted and marked for purge**, or even **deleted upstream yet still valid-but-orphaned downstream**, the important operational question stops being only *what is the successor?* It becomes *which unresolved states are still hanging around, how old are they, why are they unresolved, and who owns the next repair action?* When official ecosystems already expose those states through machine-readable history, deletion, deprecation, and event feeds, orphan handling stops being an edge case. **Orphan-state inventories become reconciliation backlogs.**

## Core claim

The archive has already argued that **machine-readable retirement notices become a buyer-control surface**, **successor-gap reason codes become operator signals**, **historical-state views become buyer due-diligence surfaces**, and **successor-map freshness guarantees become a service metric**. Those dossiers explain how states retire, how unresolved handoffs are classified, how history stays inspectable, and how remap layers stay fresh. But they still leave one practical object under-described: *what does an operator actually manage once unresolved or half-retired states begin to accumulate?*

Current documentation suggests that this object is already emerging.

OSV.dev’s FAQ says withdrawn records are excluded from main POST query responses and list views but remain retrievable through the direct `GET /vulns/{id}` endpoint and in exports [S1005]. The same FAQ then says deleted records are not handled uniformly: for GCS sources they are converted to withdrawn, but for REST and Git sources OSV.dev currently leaves the existing records **valid but orphaned** [S1005]. That is unusually direct evidence that a live public ecosystem already has records that are no longer cleanly routed by their source but are still present enough to require downstream handling.

OSV’s own data-quality guidance makes the same pressure point even more explicit. It says a high-quality OSV record should let an automated consumer answer, among other things, whether it should “replace or remove this **(potentially orphaned)** package with known unfixed vulnerabilities” [S1021]. In other words, “orphaned” is not merely an archival curiosity. It is already being treated as a concrete decision condition for automated consumers.

NVD shows the same pattern from adjacent directions. Its vulnerability-status documentation says REJECTED CVE records remain on the CVE list so users know the identifier is invalid and should no longer be used [S1012]. Its current Product APIs documentation says deprecated CPE records can expose both `deprecatedBy` and `deprecates`, and that consumers are expected to keep up by requesting only records modified since their last request; related match criteria also carry `lastModified` and `cpeLastModified` changes when relevant names are created, modified, or deprecated [S1022]. Its data-feeds guidance then says local mirrors should stay synchronized through modified feeds and associated META files rather than through one-off bulk downloads [S1024]. Taken together, that means a consumer is already expected to maintain something closer to a living reconciliation inventory than to a static lookup table.

Red Hat’s security-data operation pushes this from registry semantics into day-to-day feed maintenance. Red Hat’s changelog says deleted or unpublished CSAF and VEX files should be removed from downstream systems and notes that stale entries now move into `deletions.csv` when corresponding files disappear [S1006]. Its advisory directory simultaneously publishes `changes.csv`, `deletions.csv`, `releases.csv`, and `archive_latest.txt` as separate machine-readable surfaces [S1007]. So the downstream consumer is not simply following a live stream. It is already expected to reconcile changed, deleted, newly released, and archived material as distinct states.

OpenID Federation broadens the pattern beyond vulnerability records. The new Subordinate Events Endpoint specification says trust anchors and intermediates can publish historical events about immediate subordinates, including registration, revocation, and key updates, specifically to provide transparency and accountability [S1023]. Once historical subordinate events are published as a distinct surface, unresolved or inconsistent subordinate states can also accumulate into review queues rather than disappearing into prose.

Taken together, these sources point to the next bottleneck above retirement markers and historical-state panes: **someone has to carry the unresolved remainder**. Once records can persist in half-routed, invalid, withdrawn, archived, or source-orphaned form, the scarce operational object is no longer just the remap rule or history pane. It is the **inventory of unresolved orphan states**: the list of items that still need purge, successor assignment, archive classification, source repair, or explicit owner confirmation.

That is why the next scarce layer is best understood as an **orphan-state inventory**. It is not simply a report. It is the maintained backlog that says which awkward residual states still exist, why they exist, how long they have existed, and which queue should close them.

## Why this belongs in the archive

This thesis belongs here because it names the operational queue that appears after state history stops being lossy. First a system publishes live records. Then it adds change histories, rejection reasons, deletion files, or historical event endpoints. Then buyers ask for historical-state views. After that, the remaining coordination burden concentrates in the unresolved leftovers: records that are still visible enough to matter but not clean enough to route automatically.

That pattern is broad. Any machine-readable ecosystem with deletions, deprecations, withdrawals, archive paths, invalidations, key rollovers, or partial replacement graphs will eventually face the same question: *which residual states are still open, and who owns their repair?* Once those residuals accumulate, an explicit orphan backlog becomes more valuable than another elegant live-state schema.

## Speculative consequences worth tracking

### 1. Silent leftovers become counted work

Systems may increasingly stop tolerating orphan states as scattered anomalies and instead maintain explicit backlog counts for valid-but-orphaned, deleted-pending-purge, archive-only, and unresolved-remap items.

### 2. Age distribution becomes a quality signal

A registry or broker may increasingly be judged not only by how many orphan states exist, but by how long the oldest ones remain unresolved and how quickly each reason class is cleared.

### 3. Repair ownership gets formalized

Suppliers, brokers, and buyers may increasingly need explicit responsibility rules for whether an orphaned state belongs to the source publisher, the intermediary, the local mirror, or the downstream consumer.

### 4. Archive-only continuation splits from bad-data residue

More ecosystems may explicitly separate “historically retained and intentionally archive-only” from “still present because the routing or source repair is incomplete.”

### 5. Backlog exports become portable artifacts

Platforms may increasingly package orphan-state inventories for handoff across teams, tools, or suppliers the same way they already package findings, advisories, or result objects.

### 6. Procurement starts asking for unresolved-state counts

Buyers may increasingly ask how many unresolved orphan states a supplier or broker is carrying, what their age profile looks like, and whether the backlog is shrinking.

### 7. The pattern spreads beyond security data

Certification directories, trust frameworks, benefits registries, sanctions lists, digital-identity ecosystems, and product-passport systems may all eventually need orphan-state inventories once deletions and historical events stop being purely destructive.

## What could falsify or weaken the thesis

- Upstream publishers converge on complete, timely successor and deletion semantics, so unresolved orphan states remain rare.
- Downstream operators keep treating orphan states as low-volume exceptions handled manually without maintained inventory.
- Retained residual states prove too heterogeneous to compress into a useful shared backlog model.
- Liability or privacy concerns push ecosystems to hard-delete or hide residual states before they accumulate into a meaningful queue.
- Historical-state views satisfy most review needs, so orphan-specific inventories never become a distinct management object.

## Research queue

- What is the minimal schema for an orphan-state inventory: identifier, source, state class, first seen, last confirmed, reason, expected successor, responsible queue, and purge/archive deadline?
- Which distinction matters most operationally: valid-but-orphaned vs withdrawn, archive-only vs invalid, or source-silent vs contested remap?
- Which metric becomes standard first: backlog count, age buckets, median repair time, unresolved-share by reason code, or oldest open orphan?
- Who should publish the inventory: the original source, the broker, the local mirror, or a buyer-side platform?
- When does an orphan state stop being an open backlog item and become a closed historical record?