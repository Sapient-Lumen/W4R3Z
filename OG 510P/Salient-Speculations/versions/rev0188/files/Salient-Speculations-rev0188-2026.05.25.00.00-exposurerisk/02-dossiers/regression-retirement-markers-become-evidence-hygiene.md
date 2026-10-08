---
id: ss-0183-regression-retirement-markers-become-evidence-hygiene
revision_promoted: pre-rev0180
title: Regression-retirement markers become evidence hygiene
constellation:
- resilience-and-continuity
- standards-and-conformance
- model-governance
- managed-legibility
- maintenance-and-repair
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- energy / grid / flexible load
- logistics / cold chain / physical continuity
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
bottleneck_type:
- allocation priority
- queue position
- fallback / graceful degradation
- conformance capacity
- interoperability translation
- version / support-window compatibility
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- liability-tail custody
- maintenance capacity
- replayability / reconstructability
enforcement_surface:
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
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
- operator
- utility
- public-agency
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
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
# Regression-retirement markers become evidence hygiene

**Thesis:** once replay fixtures, public result matrices, regression alerts, disclosure windows, retirement notices, successor-gap reason codes, and historical trust artifacts all coexist, the hard question stops being only whether a regression can be detected or disclosed. It becomes **how a once-reportable regression is explicitly closed**: resolved, withdrawn as a false alarm, superseded by a later notice, moved to archive-only status, or still historically relevant but no longer actionably current. When downstream dashboards, support queues, contracts, and audit trails start depending on that distinction, regression-retirement markers become evidence hygiene.

## Core claim

The archive has already argued that **public replay-result matrices become a buyer shortcut**, **conformance-regression alerts become contract triggers**, **regression-disclosure windows become a governance surface**, **machine-readable retirement notices become a buyer-control surface**, and **successor-gap reason codes become operator signals**. Those dossiers explain how degradations become visible, routable, and interpretable. But they still leave one operational question under-described: *what tells a downstream system that a previously live regression notice has now been cleanly retired, and why?*

Current documentation suggests that the building blocks for that layer are already present.

Dependency-Track's notifications documentation says audit-change notifications fire whenever the analysis state changes or when a finding is suppressed or unsuppressed [S1009]. Its analysis-state and auditing documentation says findings keep audit history for every analysis-state change, including the user and timestamp, and that the platform keeps track of audit history, comments, and analysis decisions for all findings [S1010][S1011]. That means the ecosystem already treats a reversal or closure decision as a first-class event with provenance, not as mere disappearance from a dashboard.

Red Hat's Clair documentation pushes the same pattern into vulnerability-watch operations. It says the notifier service informs users if **new or removed vulnerabilities** affect an indexed manifest, and that users then re-query the matcher for an up-to-date vulnerability report [S1013]. Red Hat's CSAF advisories directory simultaneously publishes `changes.csv`, `deletions.csv`, `releases.csv`, and `archive_latest.txt` as distinct machine-readable surfaces [S1007]. In other words, the live evidence layer is already separating change, removal, release, and archival continuity rather than collapsing all post-alert states into one silent absence.

NVD shows that retirement and reversal states can also remain historically visible. Its vulnerability-status documentation says rejected CVE records remain on the CVE List so users know the record is invalid and should no longer be used [S1012]. Its change-history API then treats `CVE Rejected` and `CVE Unrejected` as separate events, alongside other change types that can be monitored over time [S1002]. This is strong evidence that an ecosystem can preserve a historical notice while still marking that notice as no longer current, and can even reverse the retirement later.

OpenID Federation generalizes the point outside vulnerability records. The specification defines a historical-keys endpoint whose purpose is to verify historical trust chains after keys have expired or been revoked, and it says the signed response attests to expired and revoked keys [S1014]. It also strongly encourages meaningful revocation reasons such as `compromised` or `superseded` [S1014]. That is not just key management. It is a concrete example of evidence hygiene: a previously valid trust object needs an explicit retirement state, a reason, and enough retained history for later verification.

Taken together, these sources point to the same missing layer above alerts and disclosure windows: **regression retirement has to become explicit**. Once a failing case, withdrawn vulnerability, suppressed finding, removed scanner result, revoked trust object, or archived advisory can still matter to buyers or auditors, a downstream system cannot safely infer closure from silence alone. It needs to know whether the notice was resolved by remediation, withdrawn because it was wrong, superseded by another notice, archived for historical reconstruction, or reversed back into live scope.

That is why the next scarce layer is best described as a **regression-retirement marker**. A regression-retirement marker is a compact, inspectable signal that a once-live negative state has been closed, reclassified, or moved into history, together with enough reason and timing metadata to tell downstream consumers what should happen next.

## Why this belongs in the archive

This thesis belongs here because it names the hygiene layer that appears once result changes become public enough to accumulate institutional residue. Detection creates events. Disclosure makes them official. But retirement determines whether yesterday's event still counts as today's fact.

That pattern is broader than software security tooling. Any ecosystem with public status pages, conformance lists, revocation feeds, casework outcomes, dependency maps, or replayable proofs will eventually need a way to say not just that something once failed, but how that failure was closed and whether the old signal should still travel. Once that matters, retirement markers stop being clerical and become infrastructural.

## Speculative consequences worth tracking

### 1. Resolved, withdrawn, superseded, and archived diverge

Downstream systems may increasingly refuse to treat all closed notices as equivalent, because each retirement mode implies a different next action.

### 2. Silent disappearance becomes low-trust behavior

Buyers and operators may increasingly distrust vendors or platforms that make regressions vanish from dashboards without a visible retirement signal, reason, or timestamp.

### 3. Notice-retirement latency becomes measurable

Contracts and scorecards may increasingly ask how long a regression remains publicly or operationally live after the underlying issue is resolved or the notice is disproven.

### 4. Historical verification depends on retained retired objects

Ecosystems may increasingly keep signed or queryable historical views of retired notices so auditors can reconstruct what was believed when decisions were made.

### 5. Replay matrices split into current and historical views

Pass/fail grids and support dashboards may increasingly need to distinguish active regressions from retired regressions rather than flattening everything into a single current snapshot.

### 6. Retirement reasons become governance vocabulary

Reason labels such as resolved, false alarm, duplicate, superseded, revoked, expired, or archive-only may increasingly turn into stable cross-tool policy inputs rather than free-form notes.

### 7. The pattern spreads beyond vulnerability data

Similar retirement-marking problems may emerge around certification status, trust-anchor rollovers, policy-translation regressions, eligibility decisions, public-service complaints, or authority revocations wherever old negative states can linger after closure.

## What could falsify or weaken the thesis

- Downstream teams remain satisfied inferring closure from a return to green status or the disappearance of a warning.
- Historical reconstruction proves unimportant enough that retired notices do not need durable visibility.
- The practical distinctions among resolved, withdrawn, superseded, archived, and reversed states remain too domain-specific to standardize usefully.
- Most relevant systems stay human-mediated enough that free-form ticket comments are sufficient.
- Buyers care about detection time and remediation time, but not about how the corresponding notice is retired.

## Research queue

- Which retirement vocabulary stabilizes first in practice: resolved, withdrawn, superseded, reversed, expired, archived, or duplicate-closed?
- Do buyers first ask for machine-readable retirement reasons, retirement timestamps, or maximum retirement-lag guarantees?
- Which ecosystems first preserve retired notices as signed historical objects rather than deleting them from the live surface?
- Does retirement state attach to the notice, the underlying case, the data feed entry, or all three?
- When a retired notice later reactivates, does the ecosystem treat that as reopening the same object or issuing a fresh one with a backward pointer?
