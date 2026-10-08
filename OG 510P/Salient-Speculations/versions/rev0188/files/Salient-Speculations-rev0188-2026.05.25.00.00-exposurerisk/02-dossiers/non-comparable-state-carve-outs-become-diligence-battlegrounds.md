---
id: ss-migrated-non-comparable-state-carve-outs-become-diligence-battlegrounds
revision_promoted: pre-rev0182
migration_status: inferred-rev0182-targeted
title: Non-comparable-state carve-outs become diligence battlegrounds
constellation:
- managed-legibility
- anti-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- interoperability translation
- recipient-scope precision
enforcement_surface:
- procurement / framework contract
- underwriting / insurance renewal
- audit / assurance engagement
artifact_type:
- correction record
- state label
lifecycle_stage:
- publish
- rely
- dispute
- stay
failure_modes:
- semantic-loss
- noncomparability
source_refs:
- S1403
- S1404
- S1405
- S1406
- S1407
- S1408
- S1409
- S1410
- S1411
- S1412
- S1413
---
# Non-comparable-state carve-outs become diligence battlegrounds

## Core claim

Once renewal-history packets, normalization-loss warranties, source-object identity warranties, and transformation-code escrow start affecting price, eligibility, insurance, holdbacks, procurement admission, or regulatory posture, the most fought-over row in the packet may not be a bad mapping. It may be the row that says **non-comparable**.

A non-comparable label looks technical: the source state does not cleanly map into the target state model. But in a relied-upon diligence packet, that label reallocates burden. Is the state missing evidence? A disclosed limitation? A seller carve-out? A broker warranty boundary? A buyer approval right? A reason to exclude the item from a score? A holdback trigger? A reason to reopen native evidence? Or a neutral statement that the target vocabulary is too crude for the source reality?

As soon as normalized packets travel into contracts, **non-comparable-state carve-outs become diligence battlegrounds**. The fight is not merely whether the broker translated correctly. It is whether a relying party may treat declared non-comparability as a defect, a priced uncertainty, a permitted exclusion, or a reason to require native-source review.

## Why this belongs in the archive

The archive’s current lifecycle-governance lane has moved from extension-lineage disclosures to renewal-history normalization, normalization-loss warranties, source-object identity warranties, and transformation-code escrow. That sequence now makes the next layer visible. A broker can preserve source objects, disclose semantic loss, and escrow its transform apparatus, yet the buyer and seller may still disagree about what should happen to fields that remain outside the target comparison regime.

Official mapping practice already treats equivalence as contextual rather than automatic. FHIR’s ConceptMap says mappings are one-way, that reverse mappings cannot be assumed, and that mappings are intended for a particular business usage; the same source terminology might map differently for billing than for analysis [S1403]. FHIR also gives each target mapping a required relationship such as `equivalent`, `source-is-narrower-than-target`, `source-is-broader-than-target`, or `not-related-to`, and its `noMap` element explicitly says there is no target mapping for the source concept [S1404]. That matters because “non-comparable” is not a lazy failure to map; mature mapping systems already need explicit ways to say that no valid target exists, that the source is broader, or that the comparison is direction-bound.

SKOS makes the same point for knowledge-organization systems. It distinguishes `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, and `relatedMatch`; `exactMatch` indicates high-confidence interchangeability across a wide range of information-retrieval applications, while `closeMatch` is only sometimes interchangeable, and exact matches are disjoint from broad or related matches [S1405]. A buyer-facing packet that collapses close, broad, narrow, related, unknown, or no-map cases into one “mapped” field is therefore not just simplifying. It is hiding the quality of the comparison.

Control and requirements mapping reinforces the burden problem. NIST/NCCoE’s OLIR mapping material uses set-theory relationships — subset of, intersects with, equal, superset of, and not related to — and treats “fulfilled by” differently depending on whether the focal element is subset/equal versus superset, intersecting, or unrelated [S1406]. This is almost exactly the contractual shape of the future dispute: if a source status only intersects the buyer’s target category, who gets the benefit of that overlap?

Security-normalization practice gives the operational substrate. AWS describes OCSF schemas as extendable by adding attributes, objects, categories, profiles, and event classes when a domain needs more context than the core schema provides [S1407]. That extension model is a quiet admission that the common schema will not always contain the native distinctions a relying party later wants. Microsoft Graph security enum lists include `unknown` and `unknownFutureValue`, a pattern that preserves forward compatibility and uncertainty rather than forcing every value into a known bucket [S1408].

Vulnerability-exchange formats show how consequential these labels become. CSAF VEX documents must include at least one of `fixed`, `known_affected`, `known_not_affected`, or `under_investigation` in product status, and a `known_not_affected` assertion requires an impact statement [S1409]. CycloneDX VEX similarly separates vulnerability `state`, `justification`, and `response`; `not_affected` is tied to the specified context, and the justification explains why [S1410]. These systems do not merely say “green” or “red.” They preserve states such as not affected, under investigation, fixed, known affected, mitigated, will not fix, and context-specific justification. A normalized diligence packet that maps all of those into “closed,” “accepted,” or “not applicable” will create liability.

Native platform taxonomies are even messier. GitHub Dependabot alert filters expose states such as `auto_dismissed`, `dismissed`, `fixed`, and `open`, along with severity, scope, package, manifest, EPSS, and runtime-risk filters [S1411]. Tenable accept rules can hide findings from active remediation queues while retaining the record for audit and compliance, can expire, make targeted findings reappear, and do not alter vulnerability scoring [S1412]. A buyer may read “dismissed,” “accepted risk,” “auto-dismissed,” “not affected,” “under investigation,” and “fixed” as materially different. A seller may argue that some of those are not comparable with the buyer’s chosen defect category. A broker may need to prove that the distinction was preserved rather than silently flattened.

Even formal tailoring systems show why non-comparability is not a corner case. OSCAL profile resolution applies a profile to a catalog to produce a new tailored catalog, and its specification emphasizes deterministic, repeatable output across tools [S1413]. A tailored control set is not simply the source catalog, nor is it arbitrary. It is a governed output of inclusions, modifications, and transformations. Diligence packets will increasingly contain the same kind of governed derivative state: not equivalent to the source, not unrelated to it, and not safely comparable without a stated reliance purpose.

That is why this thesis belongs here. The archive already has semantic-equivalence grades, translation-loss proofs, scope crosswalks, normalization-loss warranties, object-identity warranties, and transform escrow. What it still needed was the next contractual question: **what happens when the correct normalized answer is that no comparison should be relied on for the disputed purpose?**

## Speculative consequences worth tracking

### 1. “Non-comparable” becomes a price term

If a packet contains ten non-comparable states, a buyer may ask for a haircut, reserve, covenant, holdback, remediation plan, manual review, or native-evidence fallback. Sellers may counter that non-comparable states were expressly disclosed and should not count as defects. The label becomes an economic term, not a footnote.

### 2. Buyers treat non-comparability as missing proof

From a buyer’s point of view, “we cannot compare this state to the target warranty category” often looks like “we cannot prove the thing we need proved.” A non-comparable carve-out may therefore be scored closer to absent evidence than to benign disclosure, especially when the packet controls eligibility, insurance, or payment release.

### 3. Sellers treat non-comparability as a liability boundary

Sellers and brokers will try to make non-comparable labels function as carve-outs: the packet warrants that the field is non-comparable, not that it satisfies the buyer’s target standard. That distinction can protect a seller from breach while still giving the buyer a reason to demand more evidence.

### 4. Reliance purpose splits the category

A state may be comparable enough for portfolio triage but not for item-level indemnity. It may be comparable enough for internal audit but not for a procurement exclusion screen. It may be comparable enough for insurance underwriting but not for regulatory self-disclosure. Non-comparable schedules will therefore become reliance-specific rather than universal.

### 5. “Unknown,” “under investigation,” and “not applicable” stop being interchangeable

Source systems often contain uncertainty states with different meanings. `unknownFutureValue` preserves enum evolution; `under_investigation` signals an active unresolved inquiry; `known_not_affected` may require an impact statement; accepted-risk rules can hide findings without changing the underlying score; dismissed alerts may be automatic or analyst-driven. Normalization that collapses these states into one bucket will be easy to challenge.

### 6. Extension fields become defensive evidence

OCSF-style extensions, unmapped payload retention, source-native sidecars, and broker-specific status fields may be used to show that a non-comparable state was not omitted. The packet may say: “this is not comparable to the target category, but the native payload is retained here.” That will be more defensible than silent loss.

### 7. Broker neutrality becomes contested

A broker that labels a state non-comparable is making a distributional choice. Conservative buyers will prefer more non-comparable labels because they force manual review or price protection. Sellers will prefer narrower use of the label because too many carve-outs make the packet look unreliable. Brokers will be accused of buyer-friendly or seller-friendly comparability defaults.

### 8. Scorecards acquire coverage ratios

Substitute-control scorecards, supplier scorecards, remediation histories, and exception-quality dashboards may start showing not only a score, but a **comparability coverage ratio**: what percentage of material states were exact, close, broader, narrower, inferred, retained-unmapped, non-comparable, or excluded from scoring.

### 9. Non-comparable labels need expiry and review

Some states are permanently non-comparable because the source and target concepts differ. Others are temporarily non-comparable because the source vendor has not yet exposed enough fields, the target schema is outdated, an investigation is unresolved, or a future enum value has not yet been interpreted. Carve-outs may need review dates, not just static labels.

### 10. Appeals become a support queue

A buyer may appeal a non-comparable label because it wants the item counted as noncompliant. A seller may appeal because it wants the item treated as satisfied or excluded. A source-system vendor may object because the broker’s label misstates native semantics. Non-comparability becomes a recurring broker-support function.

## Likely artifact shape

A mature artifact probably looks like a **non-comparable-state carve-out schedule** attached to a normalization-loss warranty and transformation-escrow packet. A minimum useful schedule would include:

- **Reliance purpose** — procurement eligibility, acquisition diligence, cyber-insurance pricing, lending covenant, regulatory submission, remediation holdback, supplier scorecard, internal audit, or supervisory review.
- **Target comparison regime** — the buyer’s control, warranty, scorecard, vulnerability category, exception taxonomy, closure rule, or remediation covenant that the source state was tested against.
- **Source-state inventory** — each native status, enum, label, rule, workflow state, lifecycle state, dismissal state, accepted-risk state, investigation state, or product-status assertion considered.
- **Mapping disposition** — exact, close, broader, narrower, intersects, stricter, weaker, inferred, retained-unmapped, no-map, not-related, non-comparable, or excluded.
- **Non-comparable reason code** — no target category, source state conflates multiple target meanings, target requires missing evidence, time granularity mismatch, source is broader, source is narrower, source is context-specific, future/unknown enum, source state expired, active investigation, accepted risk without remediation, vendor extension only, or native payload retained but not translated.
- **Burden allocation** — whether the item is buyer-risk, seller-risk, broker-carve-out, native-vendor fact question, manual-review queue, holdback item, or excluded-from-score item.
- **Economic treatment** — no price effect, disclosure-only, holdback inclusion, reserve inclusion, covenant trigger, score haircut, underwriting surcharge, eligibility block, or manual approval required.
- **Coverage math** — denominator rules, whether non-comparable states count as failed, missing, excluded, pending, partially comparable, or separate coverage loss, and how ratios are displayed.
- **Native-evidence sidecar** — retained source payload, screenshots, API response, audit log, advisory, VEX statement, ticket history, accept-rule record, profile-resolution output, or transform-run trace.
- **Alternative proof path** — what additional source-native evidence would make the item comparable, who must produce it, and whether manual judgment can substitute for schema-level comparability.
- **Review and expiry** — whether the carve-out is permanent, temporary, tied to source-vendor documentation, tied to target-schema update, tied to investigation closure, or scheduled for reclassification.
- **Approval trail** — who accepted the carve-out, whether buyer approval was required, whether broker counsel or auditor reviewed it, and whether source-system vendor clarification was sought.
- **Challenge path** — how a buyer, seller, insurer, auditor, or vendor disputes the label, what evidence is needed, who reruns the transform, and whether revised labels retroactively affect score, price, eligibility, or holdback release.
- **Escrow linkage** — hash, transform-run ID, mapping table version, schema version, source snapshot, and replay procedure needed to verify that the non-comparable label was actually produced by the warranted method.

This artifact matters because it gives every party a safer alternative to pretending that comparison is either perfect or impossible. It lets a buyer see where reliance is thin. It lets a seller disclose non-equivalence without conceding breach. It lets a broker warrant the classification boundary rather than over-warranting the target result. And it lets later disputes focus on the specific burden assigned to each non-comparable state.

## What could falsify or weaken the thesis

- Buyers continue accepting aggregate dashboards without asking how many states were non-comparable, retained-unmapped, inferred, or excluded.
- Brokers refuse to expose non-comparable categories because explicit carve-outs increase liability more than they increase trust.
- Native platforms converge quickly enough on shared state taxonomies that non-comparable states become rare.
- Contracts treat non-comparable rows as ordinary disclaimers rather than as priced diligence terms.
- Buyers require native-system review for every material exception, preventing normalized packet carve-outs from becoming important.
- Regulators or standards bodies define canonical mappings for the main source states, leaving little negotiated room.
- Market participants prefer simple indemnity pools or insurance adjustments over granular carve-out schedules.
- Source-system license terms or privacy rules prevent retention of enough native payload to defend a non-comparable label.

## Research queue

- Which state creates the first serious dispute: accepted risk, auto-dismissed alert, under investigation, known not affected, false positive, compensating control, expired exception, or reopened finding?
- Which buyer class insists on non-comparable schedules first: cyber insurers, acquirers, lenders, government procurement teams, prime contractors, auditors, or regulators?
- Does non-comparable count as missing evidence, disclosed limitation, separate carve-out, score exclusion, or holdback item in early contracts?
- Do brokers publish conservative non-comparable labels to reduce liability, or buyer-friendly mappings to make packets easier to use?
- Which coverage ratio becomes market shorthand: exact-only coverage, exact-plus-close coverage, manual-review burden, non-comparable materiality, or retained-unmapped rate?
- Do source-system vendors start publishing official mapping guidance to prevent brokers from misclassifying native states?
- Do non-comparable carve-outs get expiry dates tied to schema updates, source-vendor documentation, or investigation closure?
- Do transform-escrow bundles become necessary to prove that a non-comparable label was produced under the claimed mapping table and not inserted opportunistically after dispute?
