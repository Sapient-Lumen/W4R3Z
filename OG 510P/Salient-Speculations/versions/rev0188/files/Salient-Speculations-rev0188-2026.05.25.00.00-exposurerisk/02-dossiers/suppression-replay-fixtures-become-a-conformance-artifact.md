---
id: ss-0183-suppression-replay-fixtures-become-a-conformance-artifact
revision_promoted: pre-rev0180
title: Suppression-replay fixtures become a conformance artifact
constellation:
- care-and-demography
- standards-and-conformance
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
- care / ageing / household capacity
- healthcare / biological observability / diagnostics
- standards / interoperability / conformance
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
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
- household
- public-agency
- provider
- standards-body
- certifier
- buyer
- model-provider
- auditor
- broker
- source-vendor
- operator
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
---
# Suppression-replay fixtures become a conformance artifact

**Thesis:** once machine-readable exception support affects procurement, downstream metrics, and cross-tool scanner output, buyers stop trusting generic claims like “we support VEX” or “exceptions propagate.” They increasingly want a tiny, replayable proof bundle that shows the same finding before and after the relevant exception logic is applied across named tools and outputs. At that point, suppression-replay fixtures become a conformance artifact.

## Core claim

The archive has already argued that **reusable exception-case objects become a portability layer**, **exception-author precedence becomes a governance surface**, and **suppression-propagation audits become a procurement checklist**. Those dossiers explain how applicability judgments travel, how conflicting judgments are prioritized, and why buyers increasingly care whether a reviewed judgment changes real dashboards, metrics, and reports. But they still leave one proving-ground question under-described: *how does a buyer, auditor, or platform team verify that a supplier’s claimed support actually works?*

The current documentation shows that the ingredients for such proof packs already exist. Docker documents that OpenVEX exceptions can be attached to an image as signed attestations and then inspected directly from the registry without rebuilding the image [S935]. Its scanner-integration guidance says VEX-enabled scanners can read the same signed attestations, preserve transparency and auditability, and let teams switch scanners without rebuilding exclusion lists, while non-VEX flows require repeated manual translation into tool-specific mechanisms [S936]. Docker’s DHI scan guidance also says base-image and child-image VEX attestations are applied cumulatively and can be used across multiple scanners rather than only inside one proprietary view [S937].

Trivy exposes the same proof surface from the consumer side. It can apply local VEX files during scans, consume VEX documents from repositories that follow the VEX Repository Specification, and automatically discover VEX attestations in OCI registries when scanning container images [S938, S939, S950]. Its filtering documentation says suppressed results can be shown explicitly with `--show-suppressed` and exported in JSON as `ExperimentalModifiedFindings` [S947]. That matters because it turns suppression behavior into something machine-observable. A fixture can now name not just the input image and the input VEX statement, but also the expected changed output.

Dependency-Track extends the same logic into buyer-facing review and downstream metrics. Its suppression documentation says suppressed findings change portfolio metrics, inherited risk, and external-system metrics, and its auditing documentation says audit history, comments, and analysis decisions are tracked for findings [S923, S948]. Its procurement guidance says the platform is meant for vendor risk assessments during and after procurement [S944]. That means the audience for replayable proof is already present. Buyers are not only using exception data operationally; they are beginning to evaluate suppliers through it.

The repository layer is maturing as well. The VEX Repository Specification defines a machine-readable manifest, update intervals, an `index.json`, package identifiers, and archive-based distribution for VEX data [S949]. Combined with OpenVEX’s schema-backed document model and standard examples, this means the ecosystem is no longer missing a shape for compact, distributable evidence bundles [S934]. What it still lacks is a normalized expectation that vendors and toolmakers should publish **small replay fixtures** that let others verify end-to-end behavior across named tools.

That is why the emerging bottleneck is best understood as a **suppression-replay fixture**. A suppression-replay fixture is a compact conformance pack containing a stable input artifact (for example, an image, SBOM, or package set), one or more machine-readable exception objects, and an expected set of observable outcomes such as filtered findings, preserved rationale, changed report contents, or altered downstream metrics. Once those packs become routine, exception support stops being a prose claim and starts becoming an executable claim.

## Why this belongs in the archive

This thesis belongs here because it names the proving-ground layer that appears after publication, portability, precedence, and propagation. Publication asks whether the judgment exists. Portability asks whether it can travel. Precedence asks which judgment governs. Propagation asks whether the judgment changes the places buyers care about. Replay fixtures ask whether someone else can verify all of that without trusting marketing language, screenshots, or bespoke support calls.

That makes this a broad speculation rather than a narrow scanner note. Many governance systems evolve from textual standards toward executable conformance artifacts: reference implementations, test suites, validator services, signed reports, and public result registries. The security-exception layer now looks ready for the same shift. Once the judgment is machine-readable and the output is machine-observable, a small replay bundle becomes the natural object of trust.

## Speculative consequences worth tracking

### 1. Vendor support claims get replaced by proof packs

Suppliers may increasingly attach small replay fixtures to docs, RFP responses, or trust portals instead of merely stating that their images, advisories, or feeds are “VEX compatible.”

### 2. Scanner releases start breaking named fixtures

Tool vendors may increasingly treat fixture compatibility as a release-gating surface, because a regression that breaks a widely used replay pack will look like a conformance defect rather than a minor parsing bug.

### 3. Buyer security teams maintain local reference chains

Large buyers may increasingly keep a small house suite of replay packs that reflects their actual scanner, dashboard, reporting, and aggregation stack, and use those fixtures when evaluating suppliers or approving tool upgrades.

### 4. Shared fixture corpora become a quiet standards layer

Open-source communities, sector consortia, or major buyers may increasingly publish reusable fixture corpora that quietly define what “working VEX support” means in practice, even if the formal standard says less.

### 5. Procurement asks for before/after outputs, not only documents

RFPs and vendor-risk reviews may increasingly ask for a runnable example showing the pre-exception view, the exception object, and the post-exception view in named outputs rather than only requesting a sample SBOM or sample VEX document.

### 6. Downstream metrics become part of conformance scope

Replay packs may increasingly assert not only filtered CVE lists but expected changes to inherited risk, policy outcomes, exported reports, or synced external metrics, pulling downstream behavior into the definition of “support.”

### 7. The pattern spills beyond vulnerability exceptions

If this stabilizes, other machine-readable adjudication domains may adopt similar packs: policy waivers, eligibility overrides, conformance deviations, or approval artifacts that are verified through tiny replay bundles rather than prose assertions.

## What could falsify or weaken the thesis

- Buyers remain satisfied with generic claims of standards support and do not request runnable or inspectable proof bundles.
- Major tools converge quickly enough that suppression behavior becomes too uniform to need shared fixtures.
- Output instability across versions makes fixture maintenance too costly for suppliers or buyers.
- Organizations keep relying on screenshots, PDFs, or narrative support tickets rather than machine-observable before/after outputs.
- Downstream metrics and report changes remain too product-specific for cross-tool replay packs to become a practical buying aid.

## Research queue

- Which suppliers first publish compact replay packs as part of security or procurement documentation?
- Which scanner or platform teams first treat fixture compatibility as a release gate or public compatibility promise?
- Do sector consortia or large buyers begin maintaining public fixture corpora for exception propagation across named toolchains?
- Which outputs become the standard observation points in replay packs: CLI results, JSON exports, dashboards, reports, policy gates, or external-system metrics?
- Do public result matrices emerge that compare vendors and tools by how many canonical replay fixtures they pass unchanged over time?
