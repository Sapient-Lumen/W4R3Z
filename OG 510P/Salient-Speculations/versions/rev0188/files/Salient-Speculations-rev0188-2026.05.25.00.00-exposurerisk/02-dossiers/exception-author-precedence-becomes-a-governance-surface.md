---
id: ss-0183-exception-author-precedence-becomes-a-governance-surface
revision_promoted: pre-rev0180
title: Exception-author precedence becomes a governance surface
constellation:
- model-governance
- managed-legibility
- market-and-state-capacity
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- insurance / risk transfer / underwriting
bottleneck_type:
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- underwritability
- small-actor evidence capacity
enforcement_surface:
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
- underwriting / insurance renewal
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
- model-provider
- buyer
- auditor
- broker
- source-vendor
- insurer
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
# Exception-author precedence becomes a governance surface

**Thesis:** once vulnerability applicability judgments can travel as portable objects, the decisive question is no longer only whether an exception exists. It becomes which author, repository, attestation, or local override gets to govern when several credible actors publish different machine-readable judgments about the same vulnerability and product. At that point, exception-author precedence becomes a governance surface.

## Core claim

The archive has already argued that **reusable exception-case objects become a portability layer**, **scanner-ingestion scoreboards become a vendor competition surface**, and **feed-escrow continuity services become a new intermediary market**. Those dossiers explain why applicability judgments now travel, why tool support matters visibly, and why evidence continuity itself has become operational. But they still leave one quiet rule under-described: once more than one actor can publish a machine-readable judgment, whose judgment wins?

The answer is already being pushed out of theory and into implementation. OpenVEX makes `author` a required field, says the author must be an individual or organization, and recommends that author identity be cryptographically associated with the signature of the VEX document or other exchange mechanism [S934]. Docker’s scanning guidance shows the same image can carry VEX statements from different authors along the provenance chain: a base-image VEX from Docker and a child-image VEX from the downstream builder are both applied cumulatively, each attributed to its respective author, without requiring a single aggregate document [S937]. Docker’s exception guidance also distinguishes between organization-private GUI exceptions and VEX-document exceptions that are visible to anyone who can pull the image, which means applicability judgments can already travel through distinct authority channels with different visibility and control properties [S920].

Trivy makes the precedence problem even more explicit. Its VEX overview says repository, local file, OCI attestation discovery, and SBOM-reference methods can be enabled simultaneously, and the order of specification determines which method has priority [S940]. Its repository documentation then says repository order determines priority, the search stops at the first matching VEX document, and the first matching document determines final status even when a lower-priority repository would state the opposite result [S939]. In other words, precedence is not a future possibility; it is already encoded as operational policy inside the scanner.

That policy layer is not neutral. VEX Hub says users should trust package maintainers and their governance processes rather than VEX Hub itself, says it does not vet the content of VEX documents, and says that when multiple VEX files exist for one PURL it distributes only one file in `index.json`, selected by lexicographic order [S941]. OpenVEX attestation guidance likewise says statements may originate from third parties exploring the same product, and that when an identity signs an attestation containing third-party statements, the signer implies trust in those statements and has decided to include them in the VEX impact history [S942]. The `vexctl` project goes further and documents explicit merging of documents from more than one stakeholder to produce the most up-to-date impact assessment [S943].

Taken together, these sources show something stronger than generic “multi-tool VEX support.” They show the emergence of a hidden constitution for machine-readable exception handling: who is recognized as an author, which signatures matter, which repository or method outranks another, whether a downstream operator may override an upstream maintainer, how third-party claims are adopted into local history, and what happens when multiple truthful-looking statements cannot all govern at once.

That is why the bottleneck is best understood as **exception-author precedence**. Once reviewed applicability judgments are portable, the scarce capability shifts toward defining and defending precedence policy. Institutions increasingly need explicit answers to questions that used to stay implicit: Does the upstream maintainer outrank the image rebuilder? Can a buyer-side security team overrule a vendor statement locally? Does a repository curator merely mirror, or does it effectively legislate by choosing order and inclusion? Which override paths are legitimate emergency escape hatches, and which ones are unacceptable ways of laundering risk?

## Why this belongs in the archive

This thesis belongs here because it names the governance layer that appears immediately after portability. Portability explains how a judgment travels. Precedence explains what that traveling judgment is allowed to do when it arrives in a system already populated by other judgments.

That makes this a broad speculation rather than a narrow scanner note. Many institutional systems go through the same transition: first a decision is trapped locally, then it becomes a portable object, then conflict between portable objects forces an explicit precedence regime. Vulnerability applicability is now far enough along that curve for precedence to matter as its own institutional surface.

## Speculative consequences worth tracking

### 1. Precedence policies become auditable governance artifacts

Large buyers, regulated operators, and scanner vendors may increasingly need written policy for whose machine-readable applicability judgment governs in common conflict patterns: maintainer versus integrator, vendor versus platform steward, or upstream statement versus local override.

### 2. Local overrides become politically charged, not just technically convenient

What looks like a harmless local override feature may increasingly become a contested governance escape hatch, because it decides when a buyer or platform is allowed to reject upstream judgment without breaking the portability story.

### 3. Repository order quietly becomes policy

As scanners and internal catalogs search repositories in priority order and stop at the first match, configuration order may increasingly function like law: a one-line ordering choice can decide which exception becomes operational truth.

### 4. Visibility tiers create authority tiers

Private dashboard exceptions, registry-visible VEX attestations, public repositories, and signed local files may increasingly be treated as different authority channels with different presumptions of legitimacy, reuse, and admissibility.

### 5. Signer independence becomes a credibility signal

Buyers may increasingly distinguish between self-issued exceptions and judgments signed or republished by a separately accountable maintainer, auditor, distribution steward, or sector intermediary.

### 6. Merger tools become quasi-adjudicators

Tools that merge, curate, or republish VEX statements may increasingly become quiet governance actors because they shape which conflicting statements survive into the “most up-to-date” record that downstream systems actually consume.

### 7. The pattern spills beyond software security

If the pattern holds, other portable-decision systems may face the same turn: waivers, eligibility overrides, conformance deviations, machine-readable permissions, or policy dispensations that become portable first and precedence-governed second.

## What could falsify or weaken the thesis

- Most ecosystems converge on a single recognized author for each applicability judgment, leaving little room for meaningful conflict.
- Tools increasingly aggregate all statements without imposing effective priority, so precedence does not become operationally decisive.
- Buyers stay comfortable with one vertically integrated platform handling conflicts invisibly inside a private product.
- Local overrides remain rare and tightly bounded, so override legitimacy never becomes a broad governance issue.
- Portable exception handling stalls before cross-organizational reuse becomes common enough for author conflict to matter.

## Research queue

- Which buyers first require a documented precedence policy for machine-readable vulnerability exceptions?
- Where do conflicts first become routine between upstream maintainers, image vendors, downstream rebuilders, and local security teams?
- Which tools expose precedence decisions clearly enough for auditors and operators to review them?
- When does repository ordering start being governed as a change-controlled policy surface rather than a convenience setting?
- Do independent signers, sector curators, or neutral exception brokers emerge as credibility layers above self-issued supplier claims?
