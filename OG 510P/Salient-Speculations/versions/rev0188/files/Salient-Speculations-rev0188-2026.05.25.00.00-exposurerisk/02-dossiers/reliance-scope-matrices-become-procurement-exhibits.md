---
id: ss-0183-reliance-scope-matrices-become-procurement-exhibits
revision_promoted: pre-rev0180
title: Reliance-Scope Matrices Become Procurement Exhibits
constellation:
- place-and-climate
- model-governance
- managed-legibility
- maintenance-and-repair
- market-and-state-capacity
- anti-abuse
- anti-legibility
status: dossier
maturity: S3-enforcement-surface
confidence: medium-low
time_horizon: mixed
domain:
- climate / retreat / habitability
- land / parcel / place-proof
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
- insurance / risk transfer / underwriting
bottleneck_type:
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- liability-tail custody
- maintenance capacity
- replayability / reconstructability
- underwritability
- small-actor evidence capacity
- fraud resistance
- selective disclosure / minimization
enforcement_surface:
- permit / license
- title / conveyancing / property transfer
- underwriting / insurance renewal
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
- lending covenant / credit agreement
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
- municipality
- insurer
- property-owner
- model-provider
- buyer
- auditor
- broker
- source-vendor
- operator
- supplier
failure_modes:
- stale-state
- nonpropagation
- false-match
- spoofed-proof
- overbroad-disclosure
- evidence-burden-exclusion
adversarial_pressure:
- forged-artifact
- graph-poisoning
- overbroad-disclosure
distributional_effect:
- small-supplier-burden
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword
  context; review before treating as authoritative.
refactor_cluster:
- authority-lifecycle
authority_role: scope-translator and verifier-relying-party
authority_stage:
- define
- scope
- verify
state_family:
- authority
state_terms:
- scope-limited
- nondelegable-action
consolidation_status: state-family-member
---
# Dossier: Reliance-Scope Matrices Become Procurement Exhibits

## Core claim

Once conditioned places are governed through searchable restrictions, machine-readable rule objects, action clearances, replay-grade logs, preserved source snapshots, and reliance-grade source attestations, the next bottleneck is no longer simply **who will stand behind a source bundle**. It becomes **what exactly that actor is willing to stand behind, for which transaction class, under which exclusions, and for how long**.

The stronger version of the thesis is that the archive’s conditioned-place lane naturally hardens into a fifth object above the attestation: a **reliance-scope matrix**. The same parcel, corridor, or facility can generate many legitimate but non-interchangeable decision objects: an acquisition-liability review, a flood-lending determination, an approved jurisdictional determination for waters, a certified wetland determination for USDA program compliance, an excavation clearance, or a title-search-backed restriction review. Once those objects proliferate, institutions stop being satisfied with vague assurances that a site was “reviewed.” They increasingly need a table that says which question was answered, for whom, with what source hierarchy, under what validity window, and with what residual obligations still left to another actor.

## Why this belongs in the archive

The archive already has a coherent lifecycle-governance sequence running from **institutional controls become a shadow zoning layer**, through **restriction-search infrastructure becomes routine conveyancing**, **machine-readable restriction objects become transaction middleware**, **action-clearance objects become field-work middleware**, **replay-grade clearance logs become insurance evidence**, **source-snapshot escrow becomes liability-tail infrastructure**, and **reliance-grade source attestations become a service tier**. That sequence explains how conditioned places remain governed, how the decision state gets preserved, and how another institution begins accepting a source bundle as sufficient. It still leaves one practical bottleneck under-described: **how that sufficiency gets bounded by transaction class instead of asserted in the abstract**.

EPA’s all-appropriate-inquiries framework already shows that one property-facing workflow is specifically about acquisition-side environmental liability. EPA describes AAI as the process of evaluating a property’s environmental conditions and assessing potential liability for contamination, and says parties use it to seek CERCLA liability protections when purchasing non-residential property [S1107; S1113]. Yet EPA’s own Superfund institutional-control pages warn that the public site information does not replace a title search and does not satisfy all-appropriate-inquiries requirements [S1108]. In other words, one official source surface can be useful for screening while still being insufficient for the acquisition-liability question.

Flood governance shows a different official reliance object for a different downstream question. Federal banking rules require national banks and federal savings associations to use FEMA’s Standard Flood Hazard Determination Form when deciding whether collateral is in a Special Flood Hazard Area, and to retain the completed form for as long as the institution owns the loan [S1115]. FEMA’s own underwriting page says that form is required for federally backed loans [S1114]. FEMA’s Flood Map Service Center, meanwhile, describes itself as the official public source for NFIP flood-hazard information while also warning that effective map information may change or be superseded over time [S1119]. That is already a scope distinction between a public source surface and a loan-grade determination object.

The same pattern appears in wetland and waters regulation. The Corps says an Approved Jurisdictional Determination is an official determination that jurisdictional waters are present or absent on a particular site, valid for five years and appealable through the Corps’ administrative appeal process [S1116]. NRCS says a certified wetland determination identifies areas subject to wetland-conservation provisions and stays in effect as long as the land remains in agricultural use unless the producer requests review after error or hydrologic change [S1117]. NRCS separately explains that producers use wetland determinations to maintain eligibility for USDA programs and that drainage, filling, land leveling, clearing, or excavation can trigger renewed review [S1118]. Those are not generic truth objects about land. They are scope-bound determination products tied to specific institutional consequences.

Taken together, these official sources imply the next bottleneck above reliance-grade attestation: **reliance-scope matrices become procurement exhibits**. Once multiple legitimate reliance objects coexist for the same geography, buyers, lenders, owners, insurers, developers, utilities, and consultants increasingly need the matrix that says: this package is acquisition-grade but not permitting-grade; this one supports flood-lending compliance but not redevelopment fill decisions; this one is valid until source drift, drainage change, map revision, or parcel alteration; this one requires title work; this one requires a licensed environmental professional; this one is only discovery-grade. The scarce object is no longer just the attestation. It is the **structured scope table** that lets institutions know what the attestation does and does not buy them.

So this belongs in the archive because it names the layer above admissibility: **reliance-scope matrices become procurement exhibits**. The actors who can standardize, negotiate, and eventually machine-encode those matrices may increasingly determine which transactions move quickly, which ones trigger expensive duplicative diligence, which liabilities remain insurable, and which public information systems are treated as merely informative versus sufficient for a named operational or financial act.

## Speculative consequences worth tracking

### 1. Contract appendices become more important than marketing claims

Vendors, consultants, and public-interest data operators may increasingly be forced to publish explicit scope tables instead of vague promises about being “decision-ready” or “transaction-ready.”

### 2. The same site gains multiple parallel admissibility profiles

A parcel may increasingly carry distinct profiles for acquisition, loan underwriting, redevelopment planning, excavation, utility work, agricultural compliance, disclosure, and litigation support rather than one generic diligence status.

### 3. Procurement starts buying exclusion clarity

Buyers may increasingly care less about maximum data coverage in the abstract and more about clear exclusions, refresh triggers, re-review triggers, and handoff boundaries between professionals.

### 4. Scope mismatch becomes a major dispute class

Claims may increasingly center on whether a party used an attestation outside its intended transaction class, relied on a discovery-grade product as if it were underwriting-grade, or failed to escalate to a stronger determination object when the use case changed.

### 5. Matrices become machine-readable policy bundles

Over time, reliance-scope tables may increasingly be expressed as structured profiles that can be attached to work orders, lender files, permit systems, diligence rooms, and insurer workflows instead of remaining prose-only contract language.

### 6. Public agencies may stay broad while private wrappers become narrow and expensive

Public viewers and registries may remain discovery-oriented, while higher-margin private or quasi-public services increasingly sell the transaction-class interpretation layer above them.

### 7. Audit trails begin preserving not only evidence but the active scope profile

Replay systems may increasingly need to show not just which source bundle existed, but which reliance matrix, exclusions, and escalation rules were in force when an action was approved.

## What could falsify or weaken the thesis

- Official public systems converge on one broadly accepted parcel-diligence object that is sufficient for most transaction classes without additional scoping.
- Lenders, insurers, regulators, and buyers keep tolerating informal judgment and generic engagement letters instead of demanding explicit scope matrices.
- Professional and institutional workflows remain too bespoke for reusable transaction classes to stabilize.
- Liability fights remain dominated by source error rather than by out-of-scope use or missing escalation.
- Machine-readable policy bundles fail to emerge and scope remains too contingent to operationalize.

## Research queue

- What are the minimal fields of a reliance-scope matrix: transaction class, governing question, source hierarchy, attestor role, excluded uses, validity window, change triggers, required escalations, and successor obligations?
- Which transaction classes stabilize first: flood lending, contaminated-property acquisition, wetland/agriculture compliance, utility excavation near conditioned parcels, or redevelopment pre-clearance?
- Do the first durable matrices emerge from procurement templates, insurer endorsements, lender overlays, consultant engagement letters, or regulator-issued forms?
- When do scope matrices become structured policy objects that software can route on instead of narrative attachments that humans must reinterpret each time?
- What is the smallest viable taxonomy of scope classes that avoids collapsing real differences while still being portable across institutions?
