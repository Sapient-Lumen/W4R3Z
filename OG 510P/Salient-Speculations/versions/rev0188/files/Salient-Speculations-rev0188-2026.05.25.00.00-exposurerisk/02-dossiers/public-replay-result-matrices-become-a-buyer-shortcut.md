---
id: ss-0183-public-replay-result-matrices-become-a-buyer-shortcut
revision_promoted: pre-rev0180
title: Public replay-result matrices become a buyer shortcut
constellation:
- resilience-and-continuity
- standards-and-conformance
- model-governance
- managed-legibility
- maintenance-and-repair
- market-and-state-capacity
- anti-abuse
- anti-legibility
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
- insurance / risk transfer / underwriting
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
- underwritability
- small-actor evidence capacity
- fraud resistance
- selective disclosure / minimization
enforcement_surface:
- certification / conformity assessment
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
- permit / license
- underwriting / insurance renewal
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
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
refactor_cluster:
- exposure-liability
exposure_role: buyer and underwriter
exposure_stage:
- classify
- renew
state_family:
- exposure
state_terms:
- loss-run-sensitive
- renewal-restricted
consolidation_status: state-family-member
---
# Public replay-result matrices become a buyer shortcut

**Thesis:** once compact replay fixtures, signed test attestations, auditable exception trails, and public-facing metric surfaces all exist, many buyers stop reading every proof artifact for themselves. They increasingly want a maintained public grid that says which suppliers, scanners, dashboards, or registries pass the same named replay cases and which ones regress over time. At that point, public replay-result matrices become a buyer shortcut.

## Core claim

The archive has already argued that **suppression-replay fixtures become a conformance artifact**, **suppression-propagation audits become a procurement checklist**, **scanner-ingestion scoreboards become a vendor competition surface**, **independent exception signers become a credibility premium**, and **public conformance-result registries become market-ranking surfaces**. Those dossiers explain how machine-readable applicability judgments become portable, visible, testable, commercially legible, and signer-differentiated. But they still leave one compression question under-described: *once proof bundles exist, what do buyers actually look at first?*

The current documentation suggests that the ecosystem is already producing the raw ingredients for a compact answer. Docker’s scanner-integration guidance explicitly compares named scanners, says VEX-enabled scanners can read the same attestations, switch without rebuilding exclusion lists, and deliver consistent results across tools, while scanners without VEX support require manual filtering and create higher false-positive rates [S961]. Docker’s image-testing guidance then says images ship with a signed **test attestation** that contains a list of tests and their results and can be verified against Docker’s public key [S962]. In other words, result-bearing, verifiable, comparable proof objects already exist.

The buyer side is already present too. Dependency-Track’s procurement guidance says the platform is meant for vendor risk assessments during and after procurement [S944]. Its auditing guidance says it keeps audit history, comments, and analysis decisions for findings [S948]. Its badge guidance says vulnerability and policy-violation metrics can be surfaced as SVG badges and, if an operator allows it, even exposed to unauthenticated users [S963]. That means the ecosystem now has procurement demand, retained adjudication context, and compact public-facing score surfaces.

The repository and publication layers make the same move easier to standardize. The VEX Repository Specification defines a machine-readable manifest, update interval, archive structure, and `index.json` manifest for distributed VEX content [S949]. OpenID’s conformance ecosystem shows the public-side precedent: the Foundation governs disclosure and reporting of testing identities and results [S785], and it publishes public tables of certified implementations by profile and role [S797]. That does not prove that security-exception ecosystems will copy OpenID’s exact model. It does show that once executable cases, reportable results, and buyer demand exist together, public result matrices are an institutional pattern rather than an exotic idea.

That is why the next bottleneck is best understood as a **public replay-result matrix**. A public replay-result matrix is a maintained comparison surface that maps named replay fixtures or conformance cases against named tools, suppliers, products, versions, or profiles and summarizes the observable outcome: pass, fail, partial support, stale support, unsupported, or regressed. The buyer value is compression. Instead of opening every signed attestation, replay pack, and audit trail individually, the buyer can first inspect a compact, continuously maintained summary surface and only dive into the underlying artifacts when something important disagrees.

## Why this belongs in the archive

This thesis belongs here because it names the **compression layer** that appears after replayability. Replay fixtures make support claims executable. Public replay-result matrices make many executable claims scannable at market speed.

That makes this a broad speculation rather than a narrow dashboard feature request. Many institutional assurance systems evolve the same way: first they standardize claims, then create testable artifacts, then expose public or semi-public tables that compress many results into one comparison surface. Once that happens, the table itself becomes a buying aid, a reputational lever, and a quasi-regulatory object. Machine-readable exception handling now appears close to that threshold.

## Speculative consequences worth tracking

### 1. Buyers screen with matrices before they inspect artifacts

Procurement and vendor-risk teams may increasingly use public replay-result matrices as a first-pass filter, opening the underlying proof packs only when a supplier is borderline, disputed, or strategically important.

### 2. Regression becomes publicly legible

A supplier or tool that passed a named replay case last quarter but fails it after an update may increasingly suffer visible reputational damage even before a formal incident or support escalation occurs.

### 3. Fixture stewardship becomes agenda-setting power

Whoever defines the named replay cases in a widely trusted matrix may quietly shape the practical meaning of “support,” “portability,” “trustworthy suppression,” or “credible exception handling” for the rest of the ecosystem.

### 4. Badge and widget surfaces proliferate

Teams may increasingly expose matrix slices as status badges, buyer portals, trust-center widgets, procurement attachments, or API endpoints rather than forcing every evaluator to run the replay packs locally.

### 5. Version-specific support becomes more visible than vendor-wide marketing claims

Public matrices may increasingly show that one vendor is reliable only for certain products, scanner combinations, or release lines, weakening broad claims like “we support VEX” in favor of profile- and version-specific status.

### 6. Disputes shift upward into result-governance fights

Once pass/fail tables start influencing buying behavior, more arguments may focus on fixture design, expected outcomes, test-environment assumptions, and disclosure timing rather than on the underlying file format alone.

### 7. The pattern spills beyond vulnerability exceptions

If this stabilizes, similar public replay-result matrices may appear for portable waivers, conformance deviations, identity assertions, policy overrides, or model-assurance artifacts wherever the costly part is no longer generating evidence but comparing it quickly.

## What could falsify or weaken the thesis

- Buyers keep demanding raw proof bundles and do not trust summarized public matrices enough to use them as a meaningful first-pass screen.
- Result variability across environments, versions, or deployment choices makes stable public comparison too noisy to be useful.
- Toolmakers and suppliers refuse to publish enough fixture outputs for third parties to maintain credible public tables.
- Private buyer-run replay suites remain more trusted than any shared or public matrix, preventing a visible market shortcut from consolidating.
- Public matrices appear but stay too sparse, stale, or politicized to influence real procurement or vendor selection.

## Research queue

- Which ecosystems first publish public pass/fail tables for named replay fixtures rather than only shipping the raw fixture corpus?
- Which buyers first cite a public replay-result matrix in procurement, renewal, or exception-review workflows?
- Do trust centers and procurement portals begin embedding live matrix slices or badge-like summaries for specific fixture families?
- Which disputes become common first: fixture design, expected output semantics, signer requirements, environment assumptions, or regression disclosure timing?
- Do public replay-result matrices remain descriptive dashboards, or do they harden into an admissibility threshold for supplier shortlisting?