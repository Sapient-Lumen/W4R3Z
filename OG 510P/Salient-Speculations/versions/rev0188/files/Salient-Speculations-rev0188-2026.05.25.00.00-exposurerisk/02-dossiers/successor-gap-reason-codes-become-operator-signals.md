---
id: ss-0183-successor-gap-reason-codes-become-operator-signals
revision_promoted: pre-rev0180
title: Successor-gap reason codes become operator signals
constellation:
- standards-and-conformance
- model-governance
- managed-legibility
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
bottleneck_type:
- conformance capacity
- interoperability translation
- version / support-window compatibility
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
enforcement_surface:
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
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
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
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
# Successor-gap reason codes become operator signals

**Thesis:** once downstream teams begin relying on maintained remap layers to traverse deprecated CPEs, rejected CVEs, withdrawn OSV records, deleted advisories, stale VEX files, archive handoffs, and renamed or superseded identifiers, the important question stops being only *what is the successor?* It becomes *why is there no clean successor yet?* When official ecosystems already expose several distinct non-successor states — duplicate, withdrawn, assigned in error, invalid source data, orphaned after deletion, archive-only continuation, or unresolved upstream/downstream mismatch — a generic null stops being operationally sufficient. At that point, successor-gap reason codes become operator signals.

## Core claim

The archive has already argued that **machine-readable retirement notices become a buyer-control surface**, **successor-map brokers become migration infrastructure**, **successor-map freshness guarantees become a service metric**, and **translation-loss proofs become an audit surface**. Those dossiers explain why handoff layers appear, why they need to stay fresh, and why semantic drift matters. But they still leave one practical question under-described: *what should a downstream system infer when a handoff layer cannot yet produce a clean successor?*

Current documentation shows that this question is no longer hypothetical. NVD's API transition guide says the CPE API now returns both `deprecatedBy` and `deprecates` relations, and that the CVE API now includes records marked `REJECT` / `Rejected` so users get a more complete picture rather than silently missing them [S1001]. The NVD Vulnerability APIs documentation then names both `CPE Deprecation Remap` and `CVE Rejected` as explicit change-history events, and it says rejection can occur for several different reasons including duplicate entries, withdrawal by the original requester, incorrect assignment, or other administrative reasons [S1002]. That is already a reason vocabulary in substance, even if it is not yet normalized as a compact downstream signal.

The CVE Program describes the same practical split more directly. Its FAQ says the reason a record is marked REJECT will usually be stated in the description and gives examples such as duplicate record, withdrawal by the original requester, incorrect assignment, or another administrative reason; it also notes that a previously rejected record can later move back to a published state [S1003]. So even within one authoritative system, “do not use this identifier” can mean several materially different things for downstream handling: follow another ID, stop using it entirely, treat the rejection as potentially reversible, or look for more context before automating a replacement.

OSV exposes another family of non-successor states. The OSV schema distinguishes `aliases`, `upstream`, and `related` as different kinds of relationship, and explicitly says `aliases` should not be used for upstream/downstream supply-chain relationships [S1004]. OSV.dev's FAQ says withdrawn records are excluded from POST query responses and the main list page but remain retrievable through `GET /vulns/{id}` and in exports, while deleted records are handled differently depending on source type: some are converted to withdrawn, while REST and Git sourced deletions can remain valid but orphaned [S1005]. That is a strong signal that “this record is not the active routing surface” already includes multiple states with different operational meanings. A deleted record left orphaned is not the same thing as a withdrawn record, and neither is the same thing as an alias, an upstream pointer, or a clean successor.

Red Hat's security-data guidance pushes the same pattern into live advisory operations. Its changelog says deleted CSAF and VEX files are tracked in `deletions.csv`, that files are deleted when source data changes or becomes invalid, and that users should remove deleted or unpublished files from their systems [S1006]. Its live advisory directory simultaneously publishes `changes.csv`, `deletions.csv`, `releases.csv`, and `archive_latest.txt` as distinct machine-readable surfaces [S1007]. That means a downstream consumer may already need to distinguish between at least four practical outcomes: a live record changed, a live record was released, a record was deleted because it became stale or invalid, or the relevant material has shifted into an archive cadence. None of those states is equivalent to “no successor known.”

NVD's CPE documentation reinforces that the replacement layer itself is structured but incomplete enough to require interpretation. The Product API says deprecated CPEs are not returned by default, describes deprecation as the result of correction or product-name evolution, and models `deprecated` / `deprecatedBy` as separate fields in the record [S1008]. In practice, this means downstream automation can already see that an identifier has moved into a deprecated state, but still needs surrounding context to decide whether to auto-follow a replacement, pause for review, fall back to archive context, or escalate because the handoff is not obvious.

Taken together, these sources point to the next bottleneck above successor-map freshness: **the absence of a successor needs an interpretable reason**. Once remap layers are treated as operational dependencies, a downstream operator cannot afford for every unresolved handoff to collapse into the same blank state. “No successor” may mean duplicate collapsed elsewhere; withdrawn and should disappear from search; invalid and should be purged; archive-only and still relevant historically; orphaned and awaiting source repair; contested and awaiting human judgment; or simply not yet mapped. Those are different actions.

That is why the next scarce layer is best understood as a **successor-gap reason code**. It is not a replacement for successor maps. It is the control surface that tells another system what sort of absence it is looking at, how cautious it should be, and which queue or tool should handle it next.

## Why this belongs in the archive

This thesis belongs here because it names the interpretive layer that appears after handoff maps become real infrastructure. First the ecosystem publishes retirement and replacement fragments. Then brokers reconcile them into usable successor maps. Then freshness becomes measurable. After that, the remaining ambiguity concentrates in the unresolved edges.

That pattern is not specific to security data. Any machine-readable governance stack with deprecated identifiers, merged records, archive fallbacks, duplicate collapse, contested equivalence, or asynchronous source repair will eventually face the same question: *what should downstream systems do with a gap that is not just a temporary null, but a named class of unresolved handoff?* Once that matters, reason codes become a higher-value signal than another bare pointer.

## Speculative consequences worth tracking

### 1. Generic nulls become operationally unacceptable

Downstream tools may increasingly refuse to treat an absent successor as a single undifferentiated state, because different gaps imply purge, pause, archive lookup, duplicate follow, or human review.

### 2. Support queues start sorting by gap reason

Broker, scanner, and vendor-support teams may increasingly triage unresolved handoffs differently depending on whether the gap is caused by stale upstream data, contested equivalence, duplicate collapse, orphaned deletion, or publisher silence.

### 3. Buyers begin asking for unresolved-gap visibility

Procurement and audit workflows may increasingly ask not only how often successor maps update, but how many unresolved handoffs exist in each reason class and how long they stay there.

### 4. Archive-only continuation becomes its own status

More ecosystems may explicitly separate “there is no live successor, but the historical artifact remains authoritative enough for reconstruction” from “the record is invalid and should be discarded.”

### 5. Gap aging becomes a quality signal

An unresolved mapping that stays in “awaiting source repair” or “contested replacement” too long may increasingly be treated as evidence of broker weakness, source neglect, or ecosystem fragmentation.

### 6. Reason-code translation becomes its own interoperability problem

As different ecosystems publish different absence states, intermediaries may increasingly need translation layers that preserve whether a gap means withdrawn, deprecated-without-clean-match, duplicate-resolved-elsewhere, or orphaned-after-delete.

### 7. The pattern spreads beyond vulnerability data

Similar reason vocabularies may emerge for public registries, standards catalogs, digital identity lists, benefits crosswalks, educational-credential equivalence tables, and model-governance records wherever stale or ambiguous handoffs can silently misroute automation.

## What could falsify or weaken the thesis

- Authoritative publishers converge on complete, timely successor metadata so unresolved handoffs become rare and low-stakes.
- Downstream teams keep tolerating generic null states because unresolved handoffs are handled manually at low volume.
- The practical distinctions between duplicate, withdrawn, invalid, orphaned, and archive-only states prove too domain-specific to compress usefully.
- Freshness and uptime remain much more important than absence semantics, so operators care only whether data is available, not why a successor is missing.
- Most consumers continue consulting the original upstream descriptions directly rather than relying on compact, machine-readable gap classes.

## Research queue

- Which reason vocabulary becomes most useful in practice: duplicate elsewhere, withdrawn, invalid, archive-only, orphaned, contested, unmapped, or source-silent?
- Which metric becomes standard first: count of unresolved gaps, median age by reason class, oldest unresolved gap, or fraction of handoffs resolved automatically?
- Do successor-gap reason codes remain an internal broker artifact, or do buyers and auditors start requesting them directly?
- Which ecosystems first distinguish “archive-only continuation” from “invalid / purge” in a way that downstream tools can automate against?
- Does gap-reason translation itself become a new intermediary function once multiple authoritative systems publish incompatible absence vocabularies?
