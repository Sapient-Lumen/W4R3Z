---
id: ss-0184-cache-age-disclosures
revision_promoted: rev0184
migration_status: reviewed
title: Cache-age disclosures become reliance boilerplate
constellation:
- managed-legibility
- standards-and-conformance
- resilience-and-continuity
status: dossier
maturity: S3-enforcement-surface
confidence: medium-high
time_horizon: near
domain:
- standards / interoperability / conformance
- cyber / software supply chain / vulnerability governance
- identity / credentials / delegated authority
- procurement / purchasing / offtake
bottleneck_type:
- state freshness
- admissible evidence
- replayability / reconstructability
- underwritability
enforcement_surface:
- procurement / framework contract
- audit / attestation / assurance
- operational-resilience supervision
- platform eligibility / ranking
artifact_type:
- state label
- audit log
- certificate / attestation
- registry entry
- reason code
lifecycle_stage:
- validate
- publish
- rely
- archive
state_family:
- freshness
- observability
state_terms:
- valid-cached
- stale-permitted
- stale-if-error
- revalidation-due
freshness_clock:
- source_observed_at
- validated_at
- relied_at
refactor_cluster:
- evidence-freshness
freshness_role: cache-age and validation-age disclosure
primary_actors:
- buyer
- auditor
- platform
- registry-operator
- security-team
- identity-provider
failure_modes:
- hidden-cache-age
- stale-state
- nonpropagation
- source-unavailable
adversarial_pressure:
- staleness-arbitrage
- selective-refresh
- snapshot-laundering
distributional_effect:
- small-supplier-burden
- incumbent-compliance-advantage
- appeal-access-gap
depends_on:
- validation-expiry-dates-become-procurement-terms
- authority-freshness-guarantees-become-compliance-metrics
- successor-map-freshness-guarantees-become-a-service-metric
decision_grade: DG-A
evidence_grade: E3-artifact-live
---
# Cache-age disclosures become reliance boilerplate

## Core claim

As more operational decisions rely on copied, cached, mirrored, transformed, or brokered proof objects, the question “is this valid?” becomes insufficient. The decisive question becomes: **how old is the state on which the relying party is acting?**

That pushes cache age, source-observation time, validation time, and revalidation deadline into ordinary contract and API boilerplate.

The strong form of the thesis is:

> Important proof systems will increasingly need to disclose not only the asserted state, but the age and validation path of that state at the moment of reliance.

## Why this belongs in the archive

The archive already contains dossiers on validation expiry, authority freshness, successor-map freshness, VEX expiry, and feed uptime. Those dossiers show that evidence can decay. This dossier names the next shared artifact: the **cache-age disclosure**.

HTTP caching already treats freshness as first-class infrastructure. RFC 9111 defines HTTP caching and cache-control semantics [S1534], while stale-use extensions define circumstances under which a cache may serve stale content during revalidation or error [S1535]. Security-data ecosystems show the same pattern in governance form. NVD tells API users to maintain local repositories with last-modified update windows rather than repeatedly pulling the entire dataset [S1532]. Verifiable credential specifications expose validity windows and proof timing fields, showing that proof age is now native to credential design [S1536][S1537].

The speculative move is to generalize those patterns beyond web caching and credentials. A procurement packet, certificate-state lookup, product passport, AI evaluation report, delegated-authority record, eligibility determination, supplier attestation, or vulnerability status may all be technically valid while being too old for a high-risk decision.

## The new boilerplate

A relying party will increasingly ask for fields like:

```yaml
source_observed_at: 2026-05-25T12:13:00Z
broker_received_at: 2026-05-25T12:14:03Z
validated_at: 2026-05-25T12:15:10Z
max_reliance_age: PT24H
cache_mode: valid-cached
stale_if_error_allowed: false
revalidation_due: 2026-05-26T12:15:10Z
source_unavailable_policy: escalate-before-rely
```

The important shift is not the syntax. It is the transfer of burden. Once cache age is disclosed, a buyer, auditor, insurer, or platform can no longer pretend that a packet was simply “valid.” It relied on a state with a known age.

## Speculative consequences

### 1. “Live checked” becomes a premium state

Some vendors will sell live or near-live validation; others will sell cheaper batch snapshots. Buyers may accept both, but not for the same risk class.

### 2. Cached reliance becomes contractual

A contract may allow a 24-hour cache for ordinary supplier status, a 2-hour cache for vulnerability exposure, and a live lookup for authority to move funds.

### 3. Stale use requires a reason code

A system that relies on stale state may need to say why: source outage, emergency continuity, low-risk action, grace period, dispute stay, or human override.

### 4. Cache-age hiding becomes actionable

If a broker displays “clear” without showing that the status was last checked three weeks ago, the omission may become a diligence failure.

### 5. Small suppliers face asymmetric burden

Large firms may automate live proof refresh. Small firms may need public-good refresh brokers, shared credential wallets, or grace rules to avoid exclusion by freshness demands they cannot economically satisfy.

## Abuse path

Cache-age disclosures can be gamed.

- A broker can disclose validation time but hide source-observation time.
- A supplier can route buyers to the freshest favorable registry and avoid the unfavorable one.
- A platform can refresh disfavored sellers more slowly.
- A buyer can require live proof where stale proof would be safe, raising barriers to entry.
- An auditor can treat any stale state as failure even when the governing policy permits stale-if-error use.

## Falsifiers

The thesis weakens if high-stakes buyers remain satisfied with binary validity states, if source-observation time remains invisible, or if disputes rarely turn on when a proof was last checked.

## Research queue

- Which proof systems already expose source-observation time separately from validation time?
- Which procurement templates begin requiring maximum reliance age?
- Which sectors distinguish cached, live, and stale-if-error reliance?
- When do courts, auditors, or insurers treat hidden cache age as material?
