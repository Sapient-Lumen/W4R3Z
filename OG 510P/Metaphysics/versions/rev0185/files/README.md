Version: rev0185
Date: 2026-05-26 05:18 UTC
Working codename: debt-cube-lifecycle-prioritization-audit-refactor

Current release note: rev0185 refactors the DebtCube with lifecycle, priority, relation, and audit observations. It does not claim debt closure, owner assignment, external remediation verification, public deployment, accessibility conformance, source-currentness, or philosophical completeness.

# Metaphysics archive — rev0184

Version: rev0184
Date: 2026-05-26 03:46 UTC
Working codename: claim-cube-warrant-defeasance-audit-refactor
Package: `Metaphysics-rev0185-2026.05.26.05.18-debt-cube-lifecycle-prioritization-audit-refactor.zip`

Current layer: `docs/190-claim-cube-warrant-defeasance-contradiction-audit-governance.md`.

Allowed release claim: rev0184 normalizes local ClaimCube observations, adds claim relation and claim audit observations, and checks claim-graph/evidence/contradiction/defeasance coverage locally.

Forbidden release claims remain: external audit, public deployment, RDF/SHACL publication, source-currentness guarantee, live URL validation, accessibility conformance, legal compliance, public support, claim truth graph completeness, automatic truth maintenance, formal bibliography completeness, semantic correctness guarantee, and external philosophical/source/claim review.

## rev0184 additions

- `CLAIM_OBSERVATION_INDEX.yml`
- `CLAIM_RELATION_MAP.yml`
- `CLAIM_AUDIT_LEDGER.yml`
- `CUBE/observations/claim_relations.yml`
- `CUBE/observations/claim_audit.yml`
- `tools/generate_claim_observations.py`
- `tools/check_claim_cube_refactor.py`
- `tools/check_claim_audit.py`
- `REGISTERS/rev0184-claim-observation-index.yml`
- `REGISTERS/rev0184-claim-relation-map.yml`
- `REGISTERS/rev0184-claim-audit.yml`
- `REGISTERS/rev0184-claim-cube-refactor.yml`
- `REGISTERS/claim-observation-index-report-rev0184.yml`
- `REGISTERS/claim-relation-map-report-rev0184.yml`
- `REGISTERS/claim-audit-report-rev0184.yml`
- `REGISTERS/claim-cube-refactor-report-rev0184.yml`

## {new} audit/refactor focus

The ClaimCube is now normalized across claim observations, claim relations, and claim-audit rows. This exposes local links between claim graph nodes, evidence packets, contradiction states, and defeasance rules while preserving the boundary that these are local structural observations only.

---

# Metaphysics archive — rev0182

Version: rev0182  
Date: 2026-05-25 23:32 UTC  
Working codename: concept-cube-audit-refactor-cross-dataset-integrity
Package: `Metaphysics-rev0182-2026.05.25.23.32-concept-cube-audit-refactor-cross-dataset-integrity.zip`

Current layer: `docs/188-concept-cube-audit-refactor-cross-dataset-integrity-governance.md`.

Allowed release claim: rev0182 expands and locally checks the concept cube, concept-relation observations, and cube-audit observations.

Forbidden release claims remain: external audit, public deployment, RDF/SHACL publication, accessibility conformance, legal compliance, public support, formal ontology completeness, semantic correctness guarantee, and external philosophical review.

## rev0182 additions

- `CONCEPT_FAMILY_MAP.yml`
- `CONCEPT_RELATION_MAP.yml`
- `CUBE_AUDIT_LEDGER.yml`
- `CUBE/observations/concept_relations.yml`
- `CUBE/observations/cube_audit.yml`
- `tools/generate_concept_observations.py`
- `tools/check_concept_cube_refactor.py`
- `tools/check_cube_audit.py`
- `REGISTERS/rev0182-concept-family-map.yml`
- `REGISTERS/rev0182-concept-relation-map.yml`
- `REGISTERS/rev0182-concept-cube-refactor.yml`
- `REGISTERS/rev0182-cube-audit.yml`

---

# Metaphysics Archive

Historical version: rev0181  
Historical date: 2026-05-25 21:34 UTC  
Working codename: current-release-normalization-cube-observation-expansion

Rev0181 normalizes the current-release identity and expands the datacube from a manifest/conformance index into separate local observation datasets for artifacts, claims, debts, controls, sources, access/comprehension evidence, and metaphysical concepts. It repairs the front door, adds reader routes, creates source/debt ledgers, adds planned accessibility/comprehension test surfaces, introduces concept/discovery rows, and adds local checkers for current release drift, stale revision tokens, expanded cube files, and new schema constraints.

Allowed claim: local rev0181 current-release, cube-expansion, source/debt/access/concept, reader-route, and stale-token surfaces are present and checked. Forbidden inference: external audit, public deployment, RDF publication, SHACL validation, WCAG conformance, accessibility certification, reader comprehension, legal compliance, public support, SPDX/CycloneDX/OSCAL/SLSA export, FAIR or RO-Crate conformance, source-currentness guarantee, or philosophical completeness.

## Reader routes

- Beginner path: `README.md` → `CORE_THESIS_COMPRESSIONS.md` → `docs/00-start-here.md`.
- Research path: `CORE_THESIS_COMPRESSIONS.md` → `docs/01-working-synthesis-layered-process-realism.md` → `CONCEPT_CUBE.yml` → `DISCOVERY_BACKLOG.yml`.
- Application path: `docs/06-kernel-operators.md` → `CLAIM_LANGUAGE_LEDGER.yml` → `DEBT_TAXONOMY.yml` → `QUERY_REGRESSION_SUITE.yml`.
- Governance path: `CURRENT_RELEASE.yml` → `CONTROL_STACK.yml` → `CUBE/datasets.yml` → `CUBE_INDEX.yml` → `tools/validate_archive.py`.

## Rev0181 new or promoted artifacts

- `CURRENT_RELEASE.yml`
- `READER_JOURNEY_MAP.yml`
- `CORE_THESIS_COMPRESSIONS.md`
- `SCHEMA_CONSTRAINT_PROFILE.yml`
- `SOURCE_ANCHOR_LEDGER.yml`
- `SOURCE_REVIEW_LEDGER.yml`
- `DEBT_TAXONOMY.yml`
- `ACCESSIBILITY_TEST_MATRIX.yml`
- `COMPREHENSION_STUDY_PLAN.yml`
- `READER_TASK_PROTOCOL.yml`
- `GLOSSARY_USABILITY_LEDGER.yml`
- `SCREEN_READER_SMOKE_TEST_LOG.yml`
- `KEYBOARD_NAVIGATION_CHECK.yml`
- `TRANSLATION_READINESS_LEDGER.yml`
- `EXPORT_READINESS_LEDGER.yml`
- `DISCOVERY_BACKLOG.yml`
- `CONCEPT_CUBE.yml`
- `datapackage.json`
- `ro-crate-metadata.json`
- `CUBE/datasets.yml`
- `CUBE/dimensions.yml`
- `CUBE/measures.yml`
- `CUBE/attributes.yml`
- `CUBE/observations/artifacts.yml`
- `CUBE/observations/claims.yml`
- `CUBE/observations/debts.yml`
- `CUBE/observations/controls.yml`
- `CUBE/observations/sources.yml`
- `CUBE/observations/access.yml`
- `CUBE/observations/concepts.yml`
- `tools/check_current_release.py`
- `tools/check_stale_revision_tokens.py`
- `tools/check_expanded_cube.py`
- `tools/check_schema_constraints.py`
- `tools/generate_debt_observations.py`
- `RUNBOOKS/current-release-cube-expansion-review-v1.md`

## Prior front-door text retained as historical lineage

# Metaphysics Archive

Version: rev0181  
Date: 2026-05-25 21:34 UTC  
Working codename: current-release-normalization-cube-observation-expansion  
Package: `Metaphysics-rev0181-2026.05.25.21.34-current-release-normalization-cube-observation-expansion.zip`

## Current release summary

Rev0181 repairs current-release drift and expands the local datacube. The archive now has a single current-release file (`CURRENT_RELEASE.yml`), split cube datasets under `CUBE/`, source-anchor and source-review ledgers, a generated debt taxonomy, accessibility/comprehension evidence planning artifacts, a concept cube, a discovery backlog, packaging metadata boundaries, and current-release/stale-token tools.

Allowed claim: rev0181 records local current-release normalization, local split cube observations, source/debt/access/concept observation rows, and local structural checks. Forbidden inference: RDF Data Cube publication, SHACL conformance, WCAG conformance, accessibility certification, plain-language certification, RO-Crate conformance, Data Package validation, OSCAL publication, SPDX or CycloneDX SBOM publication, SLSA level, in-toto attestation, legal compliance, external audit, public support, public deployment, or philosophical completeness.

## Reader paths

- Beginner path: start with `CURRENT_RELEASE.yml`, then `docs/00-start-here.md`, then this README's forbidden-claim boundary.
- Research path: read the Layered Process Realism synthesis, then `CONCEPT_CUBE.yml`, then `DISCOVERY_BACKLOG.yml`.
- Application path: use `CUBE/observations/claims.yml`, `CUBE/observations/debts.yml`, and `CLAIM_LANGUAGE_LEDGER.yml` before reusing any claim.
- Governance path: use `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, `QUERY_REGRESSION_SUITE.yml`, `CURRENT_RELEASE.yml`, and the validator tools.

## Current rev0181 artifact map

- `ABUSE_MISUSE_CASE_REGISTER.yml`
- `ACCEPTANCE_CRITERIA_MATRIX.yml`
- `ACCESSIBILITY_REVIEW_PLAN.yml`
- `ACCESSIBILITY_TEST_MATRIX.yml`
- `ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml`
- `ACCOUNTABILITY_REVIEW_LEDGER.yml`
- `AFFECTED_PARTY_ANALYSIS.yml`
- `APPEAL_REVIEW_POLICY.yml`
- `APPROVAL_CONSENT_LEDGER.yml`
- `ARCHIVE_INDEX.md`
- `ASSURANCE_CASE_SKELETON.yml`
- `ATTESTATION_BOUNDARY_LEDGER.yml`
- `ATTRIBUTION_CITATION_LEDGER.yml`
- `AUDIT_SAMPLING_PLAN.yml`
- `BENEFIT_HARM_REGISTER.yml`
- `BUILD_REPRODUCIBILITY_LEDGER.yml`
- `CHANGE_IMPACT_MATRIX.yml`
- `CLAIM_GRAPH.yml`
- `CLAIM_LANGUAGE_LEDGER.yml`
- `CLOSURE_VERIFICATION_LEDGER.yml`
- `COMMUNICATION_ESCALATION_LEDGER.yml`
- `COMPLIANCE_BOUNDARY_LEDGER.yml`
- `COMPREHENSION_STUDY_PLAN.yml`
- `CONCEPT_CUBE.yml`
- `CONFIDENTIALITY_ACCESS_MATRIX.yml`
- `CONTESTATION_INTAKE_LEDGER.yml`
- `CONTRADICTION_LEDGER.yml`
- `CONTRIBUTOR_PROVENANCE_LEDGER.yml`
- `CONTROL_STACK.yml`
- `CORRECTIVE_ACTION_REGISTER.yml`
- `CUBE/attributes.yml`
- `CUBE/datasets.yml`
- `CUBE/dimensions.yml`
- `CUBE/measures.yml`
- `CUBE/observations/access.yml`
- `CUBE/observations/artifacts.yml`
- `CUBE/observations/claims.yml`
- `CUBE/observations/concepts.yml`
- `CUBE/observations/controls.yml`
- `CUBE/observations/debts.yml`
- `CUBE/observations/sources.yml`
- `CUBE_INDEX.yml`
- `CURRENT_RELEASE.yml`
- `DEBT_TAXONOMY.yml`
- `DEFEASANCE_PROPAGATION.yml`
- `DELEGATION_HANDOFF_LEDGER.yml`
- `DEPENDENCY_UPDATE_POLICY.yml`
- `DERIVATIVE_REDISTRIBUTION_POLICY.yml`
- `DISCLOSURE_PUBLICATION_REVIEW.yml`
- `DISCOVERABILITY_NAVIGATION_MAP.yml`
- `DISCOVERY_BACKLOG.yml`
- `DISSENT_MINORITY_REPORT_LEDGER.yml`
- `DOWNSTREAM_RELIANCE_LEDGER.yml`
- `DRIFT_ANOMALY_LEDGER.yml`
- `ETHICAL_IMPACT_ASSESSMENT.yml`
- `EVIDENCE_CHAIN_CUSTODY.yml`
- `EVIDENCE_PACKET_INDEX.yml`
- `EXECUTION_LOG_LEDGER.yml`
- `EXERCISE_INCIDENT_DRILL_LEDGER.yml`
- `EXTERNAL_CROSSWALK.yml`
- `FAIRNESS_BIAS_REVIEW_LEDGER.yml`
- `FEEDBACK_INTAKE_LEDGER.yml`
- `FIXTURE_CORPUS.yml`
- `FRESHNESS_POLICY.yml`
- `GLOSSARY_USABILITY_LEDGER.yml`
- `HARM_IMPACT_REVIEW_LEDGER.yml`
- `INCLUSIVE_ACCESS_RISK_REGISTER.yml`
- `INVARIANT_CATALOG.yml`
- `KEYBOARD_NAVIGATION_CHECK.yml`
- `LICENSE_REUSE_POLICY.yml`
- `LOCALIZATION_TRANSLATION_BOUNDARY.yml`
- `MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml`
- `MIGRATION_LEDGER.yml`
- `MISUSE_SENSITIVE_RELEASE_POLICY.yml`
- `OBSERVABILITY_MONITORING_PLAN.yml`
- `PORTABILITY_INTEROPERABILITY_MATRIX.yml`
- `PRESERVATION_ARCHIVAL_PLAN.yml`
- `PRIVACY_MINIMIZATION_POLICY.yml`
- `PRIVACY_RISK_REVIEW_LEDGER.yml`
- `PROVENANCE_LEDGER.yml`
- `PUBLIC_INTEREST_BALANCING_LEDGER.yml`
- `PUBLIC_RELEASE_ATTESTATION.yml`
- `QUERY_REGRESSION_SUITE.yml`
- `READABILITY_PLAIN_LANGUAGE_LEDGER.yml`
- `READER_TASK_PROTOCOL.yml`
- `README.md`
- `REDRESS_REVERSAL_LEDGER.yml`
- `REFERENCE_MAP.yml`
- `RELEASE_DECISION_LEDGER.yml`
- `RELEASE_GATE_POLICY.yml`
- `REMEDIATION_TRIAGE_POLICY.yml`
- `RETENTION_DELETION_LEDGER.yml`
- `RISK_ACCEPTANCE_LEDGER.yml`
- `ROLE_AUTHORITY_MATRIX.yml`
- `ROLLBACK_RETRACTION_PLAN.yml`
- `SCREEN_READER_SMOKE_TEST_LOG.yml`
- `SECRET_KEY_MATERIAL_POLICY.yml`
- `SECURITY_HARDENING_BASELINE.yml`
- `SECURITY_THREAT_MODEL.yml`
- `SEGREGATION_OF_DUTIES_POLICY.yml`
- `SENSITIVE_DATA_CLASSIFICATION.yml`
- `SERVICE_OBJECTIVE_LEDGER.yml`
- `SEVERITY_CLASSIFICATION_MATRIX.yml`
- `SOURCE_ANCHOR_LEDGER.yml`
- `SOURCE_REVIEW_LEDGER.yml`
- `STAKEHOLDER_CHALLENGE_REGISTER.yml`
- `STATUS_VOCABULARY.yml`
- `SUCCESSION_CONTINUITY_PLAN.yml`
- `SUNSET_END_OF_LIFE_LEDGER.yml`
- `THIRD_PARTY_CONTENT_REGISTER.yml`
- `TRACEABILITY_MATRIX.yml`
- `TRANSLATION_READINESS_LEDGER.yml`
- `TRUST_BOUNDARY_LEDGER.yml`
- `USER_GUIDANCE_ONBOARDING_LEDGER.yml`
- `VULNERABILITY_DISCLOSURE_INTAKE.yml`
- `WAIVER_EXCEPTION_LEDGER.yml`
- `datapackage.json`
- `ro-crate-metadata.json`
- `tools/check_current_release.py`
- `tools/check_stale_revision_tokens.py`
- `tools/generate_debt_observations.py`

## Historical retained front-door material

The following text is retained for lineage. Prior revision tokens below are historical unless explicitly routed through `CURRENT_RELEASE.yml`, a migration/lineage field, or a current rev0181 record.

# Metaphysics Archive

Version: rev0179  
Date: 2026-05-22 01:20 UTC  
Working codename: licensing-reuse-attribution-compliance

Rev0178 adds legal/reuse-boundary governance: `docs/184-licensing-reuse-attribution-third-party-contributor-derivative-and-compliance-boundary-governance.md`, `LICENSE_REUSE_POLICY.yml`, `ATTRIBUTION_CITATION_LEDGER.yml`, `THIRD_PARTY_CONTENT_REGISTER.yml`, `CONTRIBUTOR_PROVENANCE_LEDGER.yml`, `DERIVATIVE_REDISTRIBUTION_POLICY.yml`, `COMPLIANCE_BOUNDARY_LEDGER.yml`, `RUNBOOKS/legal-reuse-attribution-compliance-review-v1.md`, and `tools/check_legal_reuse.py`. Current reports include `REGISTERS/license-reuse-report-rev0179.yml`, `REGISTERS/attribution-citation-report-rev0179.yml`, `REGISTERS/third-party-content-report-rev0179.yml`, `REGISTERS/contributor-provenance-report-rev0179.yml`, `REGISTERS/derivative-redistribution-report-rev0179.yml`, and `REGISTERS/compliance-boundary-report-rev0179.yml`.

Allowed claim: local licensing/reuse, attribution, third-party-content, contributor-provenance, derivative/redistribution, and compliance-boundary surfaces are present and checked. Forbidden inference: public legal license grant, legal advice, copyright clearance, contributor assignment, derivative authorization, regulatory compliance, warranty, indemnity, or external legal approval.

## Prior front-door text

# Metaphysics Archive

Version: rev0175  
Date: 2026-05-21 18:40 UTC
Working codename: contestability-appeals-redress
Rev0175 adds privacy minimization, confidentiality/access, disclosure/publication, retention/deletion, sensitive-data classification, and privacy-risk-review governance. New artifacts: `PRIVACY_MINIMIZATION_POLICY.yml`, `CONFIDENTIALITY_ACCESS_MATRIX.yml`, `DISCLOSURE_PUBLICATION_REVIEW.yml`, `RETENTION_DELETION_LEDGER.yml`, `SENSITIVE_DATA_CLASSIFICATION.yml`, `PRIVACY_RISK_REVIEW_LEDGER.yml`, `RUNBOOKS/privacy-confidentiality-access-retention-review-v1.md`, and `tools/check_privacy_confidentiality.py`. Current reports include `REGISTERS/privacy-minimization-report-rev0175.yml`, `REGISTERS/confidentiality-access-report-rev0175.yml`, `REGISTERS/disclosure-publication-report-rev0175.yml`, `REGISTERS/retention-deletion-report-rev0175.yml`, `REGISTERS/sensitive-data-classification-report-rev0175.yml`, and `REGISTERS/privacy-risk-review-report-rev0175.yml`.

## Rev0175 front-door delta

Rev0175 adds contestability, appeal, dissent-preservation, harm-impact review, redress/reversal, and stakeholder-challenge governance. New artifacts: `CONTESTATION_INTAKE_LEDGER.yml`, `APPEAL_REVIEW_POLICY.yml`, `DISSENT_MINORITY_REPORT_LEDGER.yml`, `HARM_IMPACT_REVIEW_LEDGER.yml`, `REDRESS_REVERSAL_LEDGER.yml`, `STAKEHOLDER_CHALLENGE_REGISTER.yml`, `RUNBOOKS/contestability-appeal-redress-review-v1.md`, and `tools/check_contestability_redress.py`. Current reports include `REGISTERS/contestation-intake-report-rev0175.yml`, `REGISTERS/appeal-review-report-rev0175.yml`, `REGISTERS/dissent-report-rev0175.yml`, `REGISTERS/harm-impact-report-rev0175.yml`, `REGISTERS/redress-reversal-report-rev0175.yml`, and `REGISTERS/stakeholder-challenge-report-rev0175.yml`.

Allowed claim: local contestability/redress surfaces are present and checked. Forbidden inference: public appeal, legal remedy, stakeholder consultation, public consent, downstream recall, or external adjudication.

## Prior front-door text

Version: rev0175  
Date: 2026-05-21 17:00 UTC
Working codename: accountability-authority-dutysegregation

This archive is a compact research program for a **non-skeptical, non-reductive metaphysics**. It now contains the default synthesis, the operator kernel, live alternatives, method and compression rules, frontier tests, source anchors, a large body of typed diagnostic files, and an increasingly explicit governance stack for routing cases, stress-testing distinctions, recording calibration cases, propagating accepted changes, controlling terminology, assigning commitment status, writing application dossiers, governing precedent, controlling transmission, auditing reception, gating releases, managing version lineage, recording provenance, classifying review warrant, governing public reliance, assigning stewardship duties, preserving operational memory, validating local invariants, executing runbook workflows, bounding automation and delegated agents, auditing semantic fidelity and warning retention, bounding operational reliance and deployment, classifying incidents and recovery, extracting post-incident learning and recurrence controls, monitoring whether controls remain effective, aggregating residual risks across a portfolio, and now allocating capacity, admitting backlog items, limiting work in progress, and classifying deferrals before priority is allowed to masquerade as work done. The point is not file-count expansion. The point is to preserve distinctions and limits as archive material moves from reasoning to package, from package to summary, from summary to teaching, from teaching to derivative or public use, from public use toward action, policy, workflow, classification, decision support, or deployment, from deployment into incident response and recovery when something goes wrong, from recovery into learning and prevention, from learned prevention into longitudinal monitoring, from individually monitored controls into cross-case portfolio review, and from portfolio priority into capacity-aware execution and honest deferral.

## What this revision changes

1. **Adds `docs/171-schema-conformance-datacube-control-stack-and-queryable-governance.md`**, a schema-conformance / datacube-control / queryable-governance file that turns the earlier warning — priority is not work done — into a stronger rule: registers, schemas, validators, and control sequences must become rows, checks, control-stack entries, query boundaries, and forbidden inferences before they are treated as machine-readable governance evidence.
2. **Adds canonical machine-readable artifacts**: `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, and `EXTERNAL_CROSSWALK.yml`.
3. **Adds local schema/datacube artifacts**: `RUNBOOKS/schema-conformance-datacube-review-v1.md`, `REGISTERS/schemas/schema-conformance-report-v1.yml`, `REGISTERS/schemas/control-stack-record-v1.yml`, and `REGISTERS/schemas/datacube-index-record-v1.yml`.
4. **Adds full-profile current records**: `REGISTERS/rev0166-release-validation.yml`, `REGISTERS/rev0166-release-workflow.yml`, `REGISTERS/rev0166-automation-boundary.yml`, `REGISTERS/rev0166-semantic-fidelity.yml`, `REGISTERS/rev0166-deployment-boundary.yml`, `REGISTERS/rev0166-incident-response.yml`, `REGISTERS/rev0166-post-incident-learning.yml`, `REGISTERS/rev0166-effectiveness-monitoring.yml`, `REGISTERS/rev0166-risk-portfolio.yml`, `REGISTERS/rev0166-capacity-allocation.yml`, `REGISTERS/rev0166-schema-conformance.yml`, `REGISTERS/rev0166-control-stack.yml`, and `REGISTERS/rev0166-datacube-index.yml`.
5. **Repairs the rev0164 capacity-record field defect** by exposing `deferral_class` as a machine-readable required field while retaining a schema-repair note.
6. **Adds `tools/query_cube.py`** as a read-only local helper for observation, debt, forbidden-claim, schema, capacity, and control-stack queries.
7. **Strengthens `tools/validate_archive.py`** so current release records are checked against declared `required_fields`; `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, and `EXTERNAL_CROSSWALK.yml` receive basic structure checks; and the validator no longer lets mere artifact presence stand in for schema conformance.
8. **Adds schema-conformance statuses SC0–SC9, datacube-readiness statuses DC0–DC9, control-stack statuses CST0–CST9, and query-permission classes QRY0–QRY9**.
9. **Adds an explicit Bet 96 for rows-before-rhetoric discipline** in `docs/00-start-here.md`.
10. **Updates the front door, archive index, source note, register README, runbook inventory, manifest, current records, and validator** so the package can say exactly what is locally queryable — and what remains forbidden to infer.

## Current archive default

The present default remains **Layered Process Realism**, but in a more disciplined form:

- **processual** enough that becoming belongs to being,
- **form-bearing** enough that organization is ontologically serious,
- **power-laden** enough that modality is not merely descriptive bookkeeping,
- **structured** enough that relations and arrangements can be constitutive,
- **grounded** enough that ontological order is real,
- **dependence-plural** enough not to flatten constitution, realization, and composition into grounding,
- **layered** enough that some higher-level realities are genuine without becoming fundamental,
- **sortal-sensitive** enough that counting, identity, and persistence are not treated as one flat problem,
- **truthmaker-disciplined** enough that negative truths and absences do not automatically generate bloated ontology,
- **property-disciplined** enough to distinguish repeatables, particularized features, and kinds without collapsing into either plenitude realism or bare nominalism,
- **modally disciplined** enough to distinguish essence, law, conceivability, and possible-worlds representation,
- and **category-disciplined** enough not to slide between objects, processes, facts, relations, and kinds as if they were one ontological type,
- and **substitution-disciplined** enough not to treat same function, same role, same stock, same organization, and same individual as one flat continuity verdict,
- and **migration-profile-disciplined** enough to distinguish moved bearer, transplanted part, ported lineage, redeployed function, changed host, changed site, and successor continuity rather than letting migration language settle bearer identity by itself,
- and **host-guest-profile-disciplined** enough to distinguish occupancy, tenancy, carriage, platform hosting, parasitic residence, multitenant support, and stronger incorporation rather than treating being in or on a host as one flat verdict of parthood, ownership, or identity,
- and **attachment-profile-disciplined** enough to distinguish anchoring, tethering, mooring, docking, mounted or hitched connection, and stronger incorporation rather than treating being attached to something as automatic parthood, fusion, or mere proximity,
- and **support-profile-disciplined** enough to distinguish bearing support, suspension, hanging load paths, bracing, rack-or-bracket support, and principal load-path carriage rather than treating every supported-by relation as generic attachment, hosting, or identity,
- and **embedding-profile-disciplined** enough to distinguish insertion, implantation, insetting, embedded subsystem placement, and transboundary indwelling passage rather than treating being set into something as automatic identity, hosting, or fusion,
- and **enclosure-profile-disciplined** enough to distinguish protective housing, transient encapsulation, channel-maintaining casing, encysted or encased surround, and stronger incorporation rather than treating being enclosed by something as automatic identity, hosting, embedding, or parthood,
- and **surface-layer-profile-disciplined** enough to distinguish coating, cladding, lining, veneer, wrapping, and laminated stratification rather than treating every cover, skin, sheath, or multilayer arrangement as one flat metaphysical relation,
- and **seal-closure-profile-disciplined** enough to distinguish compressed interface seals, gap-filling seam seals, perimeter seals, occlusive plugs, closure-system integrity, and self-sealing repeated-access relations rather than treating every closed, plugged, gasketed, or caulked case as enclosure, embedding, or mere attachment,
- and **joining-profile-disciplined** enough to distinguish adhesive bonding, welded joining, filler-mediated joints, soft-tissue approximation, hybrid joined assemblies, and stronger fusion claims rather than treating every joined, bonded, welded, or stapled case as automatic identity or as mere attachment,
- and **autonomy-profile-disciplined** enough to distinguish self-maintenance, self-governance, institutional autonomy, local explanatory autonomy, and stronger independence claims rather than treating every autonomous-looking case as one flat achievement,
- and **scaffold-profile-disciplined** enough to distinguish enabling background, persistent external support, developmental scaffolding, ecological niche construction, institutional enablement, and constitutive inclusion rather than treating every helpful environment as either mere noise or automatic part of the thing,
- and **boundary-exchange-profile-disciplined** enough to distinguish hard barriers, porous interfaces, passive leakage, selective gatekeeping, tolerated hosting, nested boundaries, and constitutive incorporation rather than treating openness as boundary failure or traffic as automatic fusion,
- and **overlap-sharing-profile-disciplined** enough to distinguish shared proper parts, complete coincidence, overlapping location without shared parts, shared-member/resource overlap, temporal overlap, and transitional overlap rather than treating every common basis as identity, merger, or negligible accident,
- and **gating-coupling-profile-disciplined** enough to distinguish standing receptivity, windowed gating, tuned sensitivity, coupling-strength modulation, switch-like route selection, selective coherence, protective filtering, and mistuning rather than treating every live channel as either indiscriminate openness, mere support, or full synchronization,
- and **capacity-limit-profile-disciplined** enough to distinguish saturation, refractory nonresponse, bottleneck congestion, reserve drawdown, protective throttling, and overload-driven regime shift rather than treating every flat or absent output as absence,
- and **response-recalibration-profile-disciplined** enough to distinguish habituation, sensitization, desensitization, tolerance, stimulus-specific retuning, and allostatic recalibration rather than treating every changed response after repetition as mere fatigue, simple amplification, or disappearance,
- and **attractor-landscape-profile-disciplined** enough to distinguish stable attractors, basins, metastable corridors, hysteretic return asymmetry, and quasi-attractor wandering rather than treating every recurring mode as either a hidden substance or a merely decorative phase portrait,
- and **history-trace-profile-disciplined** enough to distinguish residual marks, stored states, embodied skills, developmental sediment, operative records, environmental carryover, and path-dependent lock-in rather than treating every historically loaded present either as the literally persisting past or as a history-free snapshot,
- and **critical-transition-profile-disciplined** enough to distinguish threshold entry within a fixed landscape, resilience loss, bifurcation, hysteretic tipping, basin loss, noise- or rate-induced shift, and apparent tipping rather than treating every abrupt change as one flat metaphysical rupture,
- and **attrition-degradation-profile-disciplined** enough to distinguish ordinary wear, cyclic fatigue, cumulative damage, reserve erosion, compensated degradation, maintenance debt, and degradation-driven threshold approach rather than treating every weakening either as no metaphysical difference or as already collapse,
- and **exclusion-incompatibility-profile-disciplined** enough to distinguish contradiction, same-slot exclusion, resource or niche competition, blocked co-manifestation, precedence-governed conflict, and regime-bounded incompatibility rather than treating every cannot-both case as global impossibility, elimination, or proof of one giant bearer,
- and **counteraction-cancellation-profile-disciplined** enough to distinguish vector-like cancellation, compensatory opposition, inhibitor or antidote neutralization, double prevention, countervailing governance, active equilibrium, and measurement-level suppression rather than treating every no-net-effect case as absence, contradiction, or one privileged surviving cause,
- and **overdetermination-redundancy-profile-disciplined** enough to distinguish jointly necessary plurality, genuine simultaneous overdetermination, standing backup, preempted reserve, architectural redundancy, functional degeneracy, and failover-preserved continuity rather than treating every many-route success case as one privileged actual cause or as mere duplicate clutter,
- and **stabilizing-control-profile-disciplined** enough to distinguish passive damping, buffering reserve, negative-feedback regulation, homeostatic range-maintenance, adaptive retuning, oscillatory stabilization, and nested mixed control rather than treating every stable-looking case as inert stillness, mere cancellation, or proof of one privileged controller,
- and **entrainment-synchrony-profile-disciplined** enough to distinguish independent coincidence, shared external pacing, unidirectional entrainment, mutual synchronization, stable phase locking, resonance-driven gain, gated coordination, and clustered synchrony rather than treating every shared rhythm as one hidden controller, one giant bearer, or accidental simultaneity,
- and **dephasing-decoherence-profile-disciplined** enough to distinguish harmless phase drift, intermittent phase slipping, clustered partial synchrony, chimera-like coexistence, noise-driven decoherence, pathological misalignment, and regime transition after lock loss rather than treating every timing breakdown as disappearance, pathology, or mere noise,
- and **amplification-synergy-profile-disciplined** enough to distinguish simple addition, cooperative synergy, catalytic enablement, positive-feedback amplification, recruitment cascade, autocatalytic expansion, and runaway escalation rather than treating every stronger-together case as one hidden cause, one giant whole, or magical novelty,
- and **repair-resilience-profile-disciplined** enough to distinguish buffered resistance, repair, compensation, plastic continuity, adaptive reorganization, temporary masking of failure, and successor replacement rather than treating any post-disturbance continuity as either exact sameness or obvious loss,
- and **latency-dormancy-profile-disciplined** enough to distinguish temporary inactivity, standing but unexercised status, reversible dormancy, externally imposed suspension, archive-backed continuity, and terminal loss rather than treating any quiet phase as either unreality or automatic sameness,
- and **delegation-enactment-profile-disciplined** enough to distinguish direct performance, delegated execution, proxy performance, office enactment, shared action, corporate agency, and successor performance rather than treating any action-through-others case as either simple individual action or automatic holistic fusion,
- and **malfunction-profile-disciplined** enough to distinguish mere variation, localized dysfunction, pathology, environmental obstruction, social mismatch, misuse/corruption, misfire, and retyping rather than treating every bad or deviant case as one flat verdict,
- and **blocked-manifestation-profile-disciplined** enough to distinguish untriggered capacity, masking, internal inhibition, external prevention, strategic withholding, dormancy, finking, mimicry, and genuine loss rather than treating every non-display case as one flat lesson about absence or hidden presence,
- and **onset-activation-profile-disciplined** enough to distinguish first existence, first activation, released manifestation, threshold crossing, developmental maturation, institutional coming-into-force, phase-entry, and genuine new-bearer formation rather than treating every beginning as one flat metaphysical event,
- and **cessation-ending-profile-disciplined** enough to distinguish deactivation, dormancy, revocation, expiration, dissolution, death, offlining, and annihilation rather than treating every stopping-point as one flat lesson about disappearance or continuity,
- and **return-reactivation-profile-disciplined** enough to distinguish resumption, reactivation, reinstatement, cyclical recurrence, repair-and-restart, fresh token repetition, and successor reconstruction rather than treating every comeback as either strict same-bearer persistence or fresh creation,
- and **succession-lineage-profile-disciplined** enough to distinguish same-bearer persistence, office succession, lineage continuity, charter continuity, design inheritance, and transmitted practice continuity rather than treating every historically linked later case as either strict identity or total discontinuity,
- and **duplication-branching-profile-disciplined** enough to distinguish same-bearer persistence, copy-production, fission, branching continuers, archive-based re-instantiation, and repeatable-type multiplicity rather than treating every multiply preserved pattern as either strict identity or total discontinuity,
- and **fusion-merger-profile-disciplined** enough to distinguish coordination, aggregation, organized composition, higher-order integration, asymmetric incorporation, new-bearer formation, and rhetorical or legal unification rather than treating every convergent many either as one simple bearer or as mere plurality,
- and **normativity-disciplined** enough to distinguish reasons, permissions, requirements, correctness conditions, and authority structures rather than treating all “ought”-talk as one flat phenomenon,
- and **person-profile-disciplined** enough to distinguish organism, subject, self, person, persona, and role-bearer rather than treating all first-personal or socially legible unity as one flat ontological kind,
- and **life-profile-disciplined** enough to distinguish organism, colony, symbiotic consortium, mechanism, ecosystem, and living stage-profile rather than treating every organized biochemical process as one flat kind of living individual,
- and **consciousness-profile-disciplined** enough to distinguish phenomenality, access, report, subjecthood, self-consciousness, personhood, and mere informational proxy rather than treating every mind-adjacent profile as one flat kind of awareness,
- and **grounding/fundamentality-profile-disciplined** enough to distinguish dependence, grounding, ontological dependence, metaphysical explanation, relative priority, absolute fundamentality, and complete basis rather than treating all depth-language as one flat building relation,
- and **hylomorphic-profile-disciplined** enough to distinguish material basis, organizational form, visible shape, kind-sensitive unity, and persistence-through-turnover rather than treating all form-talk as one flat doctrine,
- and **process-profile-disciplined** enough to distinguish event, process, activity, accomplishment, achievement, state, maintenance-cycle, and process-sustained individual rather than treating all dynamic cases as one flat kind of becoming,
- and **world-profile-disciplined** enough to distinguish actual cosmos, domain-totality, possible world, Lewisian concrete world, modal index, and merely representational world-talk rather than treating all “world” language as one flat ontology,
- and **appearance-profile-disciplined** enough to distinguish perceptual presentation, phenomenal manifestation, social legibility, instrument display, interface-mediated disclosure, and merely model-relative showing rather than treating all “appearance” or “manifest” language as one flat metaphysical verdict,
- and **structure-profile-disciplined** enough to distinguish relation, pattern, network, symmetry-linked order, model-structure, and constitutive relational architecture rather than treating all structural language as one flat ontological verdict,
- and **fact-profile-disciplined** enough to distinguish facts, obtaining states of affairs, non-obtaining states of affairs, events, propositions, and leaner positive ontological grounds rather than treating all “the fact that” language as one flat category,
- and **truth-profile-disciplined** enough to distinguish truthbearers, truthmakers, broad correspondence, narrow fact-matching, approximate scientific truth, centered truth, and deflationary or expressive uses of “true” rather than treating all truth-talk as one flat metaphysical verdict,
- and **status-profile-disciplined** enough to distinguish fundamental reality, derivative but robust reality, thinly dependent or aspectual reality, idealized but world-tracking posit, and merely representational or fictional posit rather than treating all uses of “real”, “objective”, or “constructed” as one flat verdict,
- and **objectivity-profile-disciplined** enough to distinguish mind-independent reality, observer-sensitive objectivity, response-dependent but real profiles, institutionally objective order, centered but objective facts, and merely private or projective seeming rather than treating all uses of “objective” and “subjective” as one flat contrast,
- and **promotion-profile-disciplined** enough to distinguish practical or ideological indispensability, explanatory pressure, target/vehicle separation, world-tracking idealization, representational scaffolding, and earned ontological promotion rather than treating every indispensable posit or successful pattern as one flat realism verdict,
- and **measurement-profile-disciplined** enough to distinguish target, setup, indicator, proxy, readout, operational criterion, calibration/error profile, and ontological verdict rather than treating every measured variable or instrument-dependent display as one flat revelation of what there is,
- and **directness-profile-disciplined** enough to distinguish phenomenological directness, epistemic directness, practical directness, representational mediation, instrument mediation, interface opacity, and genuine world-contact rather than treating every use of “direct” or “mediated” as one flat verdict about reality-access,
- and **evidence-profile-disciplined** enough to distinguish data, interpreted result, confirmation, underdetermination, historical retention, and selective ontological promotion rather than treating all support as one flat realism verdict,
- and **abduction-profile-disciplined** enough to distinguish deduction, induction, selective abduction, no-miracles pressure, local diagnosis, explanatory scope, simplicity, unification, causal depth, and support for entities versus structures or mechanisms rather than treating all explanatory superiority as one flat route to ontology,
- and **convergence-profile-disciplined** enough to distinguish repetition, reproducibility, triangulation, convergence, robustness, independence, artifact-risk reduction, and family-of-model stability rather than treating many successful routes as one flat guarantee of ontology,
- and **artifact-profile-disciplined** enough to distinguish distortion from fabrication, proxy failure from target absence, setup artifact from ontological defeat, theory-ladenness from arbitrariness, and local route failure from global defeat rather than treating every failure mode as one flat skeptical or eliminative verdict,
- and **access-architecture-disciplined** enough to distinguish disclosure, registration, target-fixing, correction, support, and promotion rather than letting one word like “access” or “evidence” settle ontology by itself,
- and **reference-profile-disciplined** enough to distinguish naming, denotation, target-fixation, centered anchoring, institutional designation, proxy capture, lexical continuity, and typed reference failure rather than letting one reused label or one successful term settle what the case is really about,
- and **revision-profile-disciplined** enough to distinguish preservation, reinterpretation, target-splitting, target-merging, status-demotion, approximate retention, and elimination rather than treating every theory change as one flat lesson for ontology,
- and **contrast-profile-disciplined** enough to distinguish genuine rivalry, grain-shift, category-shift, target-sharing, layered coexistence, pragmatic-only plurality, and typed comparative superiority rather than treating all ontological comparison as one flat winner-take-all contest,
- and **idealization-profile-disciplined** enough to distinguish abstraction, approximation, controlled distortion, ideal limits, effective-regime description, and merely heuristic scaffolding rather than treating all tractable model-use as one flat realism verdict,
- and **equivalence-profile-disciplined** enough to distinguish empirical equivalence, formal or definitional equivalence, gauge-related redundancy, duality, interpretive preservation, and full ontological sameness rather than treating all reformulation-success as one flat metaphysical verdict,
- and **regime-profile-disciplined** enough to distinguish strict universality, ceteris-paribus stability, effective-regime realism, transition-sensitive behavior, bounded domains of validity, and merely heuristic scope restrictions rather than treating all “local”, “effective”, or “normal conditions” language as one flat metaphysical verdict,
- and **mereologically disciplined** enough not to confuse arbitrary sums with integrated wholes or boundary vagueness with unreality,
- and **causally disciplined** enough to distinguish production, prevention, intervention-sensitive difference-making, and omissive failure from constitutive dependence,
- and **temporally disciplined** enough to distinguish temporal order, persistence, tense, passage, and irreversibility rather than treating them as one flat issue,
- and **spatially disciplined** enough to distinguish region, site, locale, location, overlap, co-location, and operational reach rather than treating all place-talk as one flat issue,
- and **metaontologically disciplined** enough to distinguish existence, fundamentality, ontological commitment, and mere representational convenience rather than treating all “there is” talk as one flat ontological verdict,
- and **metametaphysically disciplined** enough to distinguish worldly disagreement, category variance, counting policy, status disagreement, scope-relative coexistence, and merely verbal variance rather than treating all ontology disputes as one flat contest,
- and **teleologically disciplined** enough to distinguish selected function, organizational role, design purpose, agential end, and institutional aim rather than treating all purposive vocabulary as one flat phenomenon,
- and **abstracta-disciplined** enough to distinguish mathematical objects, propositions, structures, and idealized entities rather than treating all non-concrete candidates as one flat ontological kind,
- and **potentiality-disciplined** enough to distinguish standing capacities, developmental potencies, organized readiness, actualizations in progress, achieved manifestations, and frustrated fulfillments rather than treating all “can” and “is becoming” talk as one flat modal status,
- and **relation-disciplined** enough to distinguish internal from external relations, thin order from thick linkage, and local holism from global connectedness rhetoric,
- and **levels-disciplined** enough to distinguish fundamentality, explanatory level, local mechanism level, scale, resolution, and domain rather than treating all “higher-level” talk as one flat hierarchy,
- and **indeterminacy-disciplined** enough to distinguish semantic vagueness, epistemic limitation, representational imprecision, and metaphysical indeterminacy rather than treating all borderline cases as one flat problem,
- and **substance-disciplined** enough to distinguish persisting bearers, hylomorphic compounds, bundle-like unities, bare-substratum proposals, and process-stabilized individuals rather than treating all objecthood as one flat substance model,
- and **identity-disciplined** enough to distinguish numerical identity, qualitative indiscernibility, individuality, and haecceity rather than treating all “this very thing” talk as one flat issue,
- and **naturalness-disciplined** enough to distinguish mere predicability, explanatory usefulness, comparative naturalness, and genuinely joint-carving classification rather than treating every successful vocabulary as equally reality-revealing,
- and **grain-disciplined** enough to distinguish determinable structure, determinate specificity, explanatory resolution, and ontological depth rather than treating every finer description as metaphysically superior,
- and **supervenience-disciplined** enough to distinguish no-free-floating-difference claims from stronger claims about realization, grounding, reduction, and explanatory sufficiency,
- and **architecture-disciplined** enough to distinguish strict hierarchy, bounded descent, reciprocal organization, and vicious or non-vicious loops rather than treating every circle as one metaphysical verdict,
- and **nonexistent-profile-disciplined** enough to distinguish fictional entities, merely possible objects, failed posits, intentional targets, and impossible descriptions rather than treating every meaningful singular discourse as one flat ontological case,
- and **constitution-profile-disciplined** enough to distinguish co-location, material continuity, constitution, identity, composition, and realization rather than treating every coincidence case as one flat verdict,
- and **distributed-being-profile-disciplined** enough to distinguish thing-like, stuff-like, field-like, medium-like, and network-like presences rather than treating every concrete existent as one flat kind of occupant,
- and **social-ontology-profile-disciplined** enough to distinguish practice, status, role, office, organization, institution, group agency, record system, and infrastructural support rather than treating all socially instituted reality as one flat kind of construction,
- and **representation-profile-disciplined** enough to distinguish signals, contents, propositions, maps, models, records, interfaces, and institutional encodings rather than treating all aboutness as one flat phenomenon,
- and **symmetry-profile-disciplined** enough to distinguish invariant structure, gauge-style redundancy, broken symmetry, conserved form, and presentation-sensitive differences rather than treating every transformation-related contrast as one flat ontological issue,
- and **chance-profile-disciplined** enough to distinguish credence, evidence, frequency, objective chance, effective higher-level probability, and merely model-internal stochasticity rather than treating all uncertainty as one flat metaphysical kind,
- and **granularity-profile-disciplined** enough to distinguish continuity, discreteness, quantization, threshold structure, sampling, measurement grain, and explanatory resolution rather than treating every difference in grain as one flat ontological verdict,
- and **indexicality-profile-disciplined** enough to distinguish uncentered description, self-location, role-centeredness, interface-mediated positioning, and objective centered facts rather than treating every “I/here/now/actual/current” claim as either ontologically empty or merely subjective,
- and **agency-profile-disciplined** enough to distinguish mere behavior, intentional action, organized control, self-governance, delegated or distributed agency, and stronger freedom claims rather than treating all action-talk as one flat metaphysical verdict,
- and **operator-family-map-disciplined** enough to route new cases through status, category, unity, dependence, modality, access, process, stock/flow, interface, passage, and control families before promoting a new operator or treating the latest available distinction as the default answer,
- and **adversarial-audit-disciplined** enough to test preferred diagnoses against same-word/changed-basis, same-basis/changed-word, wrong-grain, proxy-artifact, fission, failure-mode, and update-footprint variants before allowing a revision to harden into doctrine,
- and **calibration-ledger-disciplined** enough to preserve not only verdicts but also positive controls, negative controls, hard positives, hard negatives, boundary cases, regression instructions, defeaters, and update debt before treating a hard case as reusable precedent,
- and **revision-propagation-disciplined** enough to update, explicitly decline, or ledger downstream changes across the front door, synthesis, method rules, frontier tests, family map, adversarial protocol, case ledger, source ledger, index, version marker, and manifest before treating a revision as complete,
- and **terminology-register-disciplined** enough not to let ordinary words, source terms, aliases, metaphors, or umbrellas settle ontology before their target, basis, grain, rivals, artifact risks, and forbidden inferences have been made explicit,
- and **commitment-status-disciplined** enough not to let file existence, vivid examples, useful distinctions, source authority, or synthesis prose turn provisional probes, live rivals, local rules, calibrated precedents, quarantined metaphors, or open debts into stronger doctrine than the archive has earned,
- and **application-dossier-disciplined** enough to turn reusable verdicts into auditable decision records with target, route, rivals, basis, grain, source role, hostile variants, non-verdict, status, maturity, future-use permission, open debts, and review triggers explicit,
- and **precedent-reuse / appeal-disciplined** enough not to let dossiered verdicts travel as unbounded slogans; later uses must preserve target, basis, grain, family, source role, term status, commitment status, non-verdict, transfer conditions, appeal triggers, and supersession rules,
- and **transmission-safe enough** that summaries, excerpts, teaching examples, diagrams, tables, conversational answers, paper sections, rubrics, and derivative outputs preserve the minimum limits appropriate to their compression level instead of turning responsible verdicts into stronger public slogans,
- and **reception-audited enough** that reader uptake, misreadings, criticisms, teaching failures, errata, reuse patterns, source-boundary failures, and operational failures are classified before they are allowed to revise doctrine or harden into uncontrolled corrections,
- and **release-gated / maintenance-ledgered enough** that edits, corrections, deprecations, source refreshes, hotfixes, rollbacks, open debts, migration paths, and package-verification results are classified before a versioned archive is treated as complete,
- and **lineage-governed / compatibility-audited enough** that released packages, old citations, forks, derivative artifacts, branch merges, migrations, teaching adaptations, and historical retentions are related by explicit compatibility verdicts rather than assumed continuity,
- and **provenance-audited / reproducibility-aware enough** that packages, forks, derivatives, generated outputs, source-refresh branches, recovered copies, and migrations carry evidence of origin, custody, transformation, validation, and trust status rather than gaining authority from polish or file names alone,
- **review-warrant-governed enough** that self-checks, mechanical checks, source checks, provenance audits, adversarial reviews, external reviews, and public certification claims do not exceed their stated authority, scope, evidence, independence, and permitted claim language,
- **public-reliance-governed enough** that published, cited, taught, repeated, disputed, withdrawn, or retracted claims do not acquire broader permission than their version, status, review packet, source scope, and public-use packet allow,
- and **stewardship-governed enough** that maintainers, reviewers, citers, teachers, fork maintainers, derivative authors, source-domain adapters, automated-output stewards, and public relying users know which duties they accept, decline, delegate, hand off, or must not claim,
- and **continuity-register-governed enough** that accepted duties, watches, notices, closures, derivative registries, source-refresh needs, public errata, fork declarations, and successor-memory items are findable rather than merely implicit in prose,
- and **validation-governed enough** that schemas, validation transcripts, scripts, manifests, and machine-readable registers state what they check, what they do not check, what failed, what was waived, and what wording they permit,
- and **workflow-governed enough** that release steps are run through named runbooks, stage gates, validation points, packaging points, fresh-extraction checks, and handoff traces rather than reconstructed from memory.
- and **automation-boundary-governed enough** that scripts, validators, generated drafts, packaging tools, scheduled checks, search systems, and delegated agents have explicit permissions, evidence records, human-review gates, stop conditions, and forbidden claims,
- and **semantic-fidelity-governed enough** that summaries, diagrams, tables, teaching handouts, generated answers, source digests, release notes, and derivative excerpts preserve source version, target, basis, status, non-verdict, warnings, source boundaries, and public-use limits,
- and **deployment-boundary-governed enough** that faithful outputs are not treated as policy, procedure, classifier, recommendation, automated trigger, operational guidance, or high-stakes advice until deployment status, action-reliance class, domain authority, affected parties, human override, notice path, rollback path, and forbidden use have been stated.
- and **incident-response-governed enough** that harmful uses, near misses, unauthorized escalations, warning failures, evidence losses, derivative misuses, public-reliance failures, rollback failures, and domain-sensitive reliance events are preserved, classified, contained, recovered, and closed only with residual risk and successor memory stated.
- and **post-incident-learning-governed enough** that recovered incidents and near misses do not count as learned until root-cause profile, recurrence-risk class, corrective action, preventive action, verification evidence, residual risk, and reopening trigger have been stated,
- and **effectiveness-monitoring-governed enough** that learned controls, validation checks, warnings, deployment boundaries, source-dependent limits, and sunset claims do not count as durable merely because they were verified once; monitoring status, effectiveness evidence, residual-risk trend, review trigger, and sunset/renewal criteria must be stated before the archive claims stability,
- and **portfolio-governed enough** that individually bounded residual risks, open debts, source dependencies, derivative permissions, deployment boundaries, incident patterns, monitoring obligations, validation checks, and stewardship duties are aggregated for exposure, correlation, cumulative burden, and priority treatment before the archive claims that its risk posture is manageable,
- and **capacity-allocation-governed enough** that portfolio priorities, release debts, source-refresh needs, derivative duties, deployment-boundary reviews, incident lessons, monitoring triggers, validation gaps, and stewardship obligations do not count as handled until capacity status, backlog admission, work-in-progress class, deferral class, resource basis, owner or declined responsibility, next action, and forbidden claim language are explicit.
- and **schema-conformance/datacube-governed enough** that current records, control sequences, source anchors, and queryable claims do not count as machine-readable governance evidence until profile, required-field result, control-stack position, row type, dimensions, measures, attributes, query permission, forbidden inference, and open debt are explicit.

## New archive guidance

The archive should now prefer **family-aware, stress-tested, calibration-ledgered, propagation-complete, terminology-safe, status-assigned, application-auditable, reuse-governed, transmission-safe, reception-audited, release-gated, lineage-governed, provenance-audited, review-warranted, public-reliance-safe, stewardship-accountable, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantic-fidelity-audited, deployment-boundary-governed, incident-response-prepared, post-incident-learning-disciplined, effectiveness-monitoring-disciplined, portfolio-aware, capacity-aware, schema-conformant, datacube-indexed, query-bounded progress** over simple file-count expansion. A proposed next revision should usually do at least one of the following:

1. **Tighten a control file** — especially `00`, `01`, `03`, `04`, or `144` through `171` — when the archive's overview, synthesis, method rules, frontier questions, family map, stress-test protocol, case ledger, update-propagation rules, terminology register, claim-status register, application-dossier protocol, precedent-reuse protocol, transmission protocol, reception/correction-loop protocol, release-gate / maintenance-ledger protocol, version-lineage / compatibility protocol, provenance / custody / reproducibility protocol, review-authority / certification / claim-warrant protocol, public-reliance / citation / dispute / withdrawal / retraction protocol, or stewardship / obligation / delegated-authority / accountability protocol, or operational-register / watch-queue / continuity-memory protocol, validation-harness / invariant-check protocol, or release-workflow / runbook / handoff protocol, automation-boundary protocol, semantic-fidelity protocol, deployment-boundary protocol, incident-response protocol, post-incident-learning protocol, effectiveness-monitoring protocol, risk-portfolio protocol, or capacity-allocation / backlog / WIP / deferral protocol have fallen behind the detailed operator files.
2. **Clarify a live contrast class** where neighboring operators or commitment levels are too easy to confuse: substitution versus turnover, migration versus duplication, hosting versus embedding, enclosure versus wrapping, sealing versus valving, clamping versus latching, meshing versus gripping, support versus guiding, guidance versus regulated passage, canonical term versus alias, or working default versus live rival.
3. **Improve a diagnostic test** by making target, family, nearest rival files, grain, basis, continuity consequence, failure mode, comparison class, artifact-risk, calibration status, update footprint, term status, commitment status, dossier verdict, non-verdict, future-use permission, transfer condition, and appeal trigger, transmission level, required warning, return path, reception status, severity level, correction action, non-action result, release class, gate outcome, open debt, deprecation status, migration note, rollback trigger, version identity, lineage relation, compatibility class, fork status, merge rule, cross-version reuse permission, provenance status, custody path, build evidence, reproducibility limit, review scope, certification status, permitted claim language, public-use status, citation form, dispute class, withdrawal class, reliance warning, obligation class, steward role, delegated authority, update/watch duty, warning duty, correction duty, accountability consequence, continuity-register entry, watch trigger, queue status, notice path, closure evidence, and successor-memory field, monitoring status, effectiveness class, residual-risk trend, sunset condition, portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, and priority/treatment class, capacity status, backlog-admission class, work-in-progress class, deferral/resource-debt class, resource basis, owner or declined responsibility, and next action explicit before adding another first-order distinction.
4. **Consolidate a family of operators, terms, or statuses** when several files, aliases, examples, or commitments are doing adjacent work and the archive needs a higher-level grammar: stock/flow, access/evidence, identity/continuity, interface/retention, routed-passage/control, terminology crosswalks, claim-status registers, application dossiers, precedent-reuse registers, transmission packets, reception packets, errata classes, release packets, maintenance ledgers, deprecation registers, rollback triggers, lineage packets, compatibility classes, fork registers, migration packets, merge protocols, control-layer governance, provenance packets, custody records, build recipes, reproducibility statuses, import/recovery records, artifact-trust rules, review packets, certification statuses, claim-warrant language, stale-review triggers, public-use statuses, citation templates, dispute classes, withdrawal classes, reliance packets, retraction notices, stewardship packets, obligation ledgers, handoff records, accountability matrices, operational registers, watch queues, notice paths, closure evidence, source-watch tables, teaching-derivative registries, public errata queues, fork declarations, machine-readable duty ledgers, successor-memory records, validation transcripts, workflow traces, runbooks, handoff packets, deployment-boundary packets, incident-response records, harm-review registers, near-miss queues, recovery packets, closure evidence, residual-risk ledgers, post-incident learning packets, root-cause profiles, CAPA records, recurrence-risk registers, verification tests, prevention-debt ledgers, monitoring packets, effectiveness reviews, sunset records, portfolio packets, exposure maps, correlation/common-cause registers, cumulative-burden records, or priority/treatment ledgers, capacity packets, backlog registers, work-in-progress limits, deferral records, resource-basis records, owner/declined-owner ledgers, or stop-condition registers.
5. **Use `docs/144-operator-family-map-and-triage-grid.md` before promoting a new operator**: the candidate must pass nearest-three, basis, grain, failure-mode, continuity-consequence, and artifact-risk tests.
6. **Use `docs/145-adversarial-stress-tests-and-revision-protocol.md` before stabilizing the verdict**: the candidate must survive same-word/changed-basis, same-basis/changed-word, wrong-grain, proxy-artifact, and failure-mode variations.
7. **Use `docs/146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md` before making a hard case precedential**: the candidate should have positive controls, negative controls, hard positives, hard negatives, boundary cases, regression instructions, defeaters, and update debt recorded when the verdict will guide later work.
8. **Use `docs/147-revision-dependency-graph-update-propagation-and-drift-control.md` before packaging a revision**: accepted changes must be propagated, explicitly declined, or ledgered as open debt across the archive's dependency graph.
9. **Use `docs/148-terminology-register-synonym-control-and-crosswalk-protocol.md` before letting a term carry doctrine**: canonical terms, aliases, family umbrellas, neighboring rivals, source-specific terms, deprecated terms, quarantined metaphors, and unsafe shortcuts must be distinguished.
10. **Use `docs/149-claim-status-register-maturity-levels-and-commitment-governance.md` before letting a claim carry commitment**: kernel commitments, working defaults, mature diagnostics, calibrated precedents, domain-local rules, live rivals, provisional probes, quarantined analogies, source-dependent commitments, deprecated items, and open debts must be distinguished.
11. **Use `docs/150-application-dossier-decision-record-and-verdict-report-protocol.md` before letting a verdict travel**: reusable applications should record target, route, rivals, basis, grain, source role, hostile variants, artifact risks, defeaters, terminology status, commitment status, non-verdict, action result, review trigger, and future-use permission.
12. **Use `docs/151-precedent-reuse-appeal-transfer-and-review-governance.md` before reusing a verdict as precedent**: later uses must state precedent status, allowed and forbidden uses, transfer conditions, appeal triggers, supersession rules, and whether the case is only an illustration, controlled precedent, calibration, regression warning, source-bound example, live rival, deprecated caution, appeal-pending item, or do-not-reuse item.
13. **Use `docs/152-transmission-excerpt-compression-and-pedagogical-governance.md` before turning licensed material into a summary, excerpt, teaching example, diagram, table, prompt answer, paper section, rubric, or derivative artifact**: the output must state compression level, audience/use, minimum retained limits, omitted material, do-not-upgrade warning, and return path when the material will travel.
14. **Use `docs/153-reception-feedback-errata-and-correction-loop-governance.md` when transmitted material is received, misunderstood, challenged, cited, taught, operationalized, corrected, or turned into feedback for future revisions**: the archive should classify the reception event, severity level, fault hypothesis, correction action, non-action result, propagation result, and escalation trigger before treating feedback as doctrinal pressure.
15. **Use `docs/154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md` before publishing a new package, patch, hotfix, source refresh, deprecation, rollback, or supersession**: the release should state its class, affected files, gate outcomes, open debts, migration notes, rollback triggers, source implications, verification evidence, and release verdict.

16. **Use `docs/155-version-lineage-compatibility-forking-and-migration-governance.md` before citing, comparing, forking, migrating, merging, teaching from, or historically retaining archive versions**: the relation should state source artifact, target artifact, relation type, scope, compatibility dimensions, changed and retained items, migration rule, allowed reuse, forbidden reuse, open lineage debt, and review trigger.
17. **Use `docs/156-provenance-custody-build-evidence-and-reproducibility-governance.md` before trusting, importing, recovering, publishing, rebuilding, or citing an artifact as a controlled package**: the artifact should state claimed version identity, source artifacts, custody path, edit intent, transformation actions, touched files, generated material, tools/procedures, verification evidence, manifest/hash evidence, reproducibility status, tamper signals checked, known omissions, allowed trust, and review trigger.
18. **Use `docs/157-review-authority-audit-certification-and-claim-warrant-governance.md` before saying a result is reviewed, audited, certified, validated, approved, source-reviewed, externally reviewed, or release-warranted**: the claim should state reviewer role, authority basis, independence status, scope reviewed, out-of-scope limits, evidence inspected, controls run, findings, certification status, allowed wording, forbidden wording, conflicts, expiry triggers, and return path.
19. **Use `docs/158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md` before letting a reviewed, released, transmitted, or taught result function as a public reliance object**: the public use should state public-use status, intended audience, permitted use, forbidden use, required warnings, citation form, dispute path, update/notice path, expiry trigger, and withdrawal or retraction rule.
20. **Use `docs/159-stewardship-obligations-delegated-authority-and-accountability-governance.md` before treating a public or derivative use as responsibly stewarded**: identify steward role, authority basis, accepted and declined duties, obligation class, delegation or handoff, update/watch trigger, warning duty, correction path, accountability consequence, and high-stakes/domain boundary.
21. **Use `docs/160-operational-registers-watch-queues-and-continuity-memory-governance.md` before treating an accepted duty as operationally maintained**: identify register type, controlled artifact, controlling packets, responsible role, obligation class, continuity status, watch trigger, next review, notice path, closure evidence, open debt, and successor-memory field.
22. **Use `docs/161-validation-harness-invariant-checks-and-machine-readable-governance.md` before describing a package, packet, register, fork, derivative, or public artifact as validation-backed**: identify schema/checklist, invariant family, check mode, pass/fail/not-run results, exceptions, human-review boundary, allowed wording, forbidden wording, and next validation trigger.
23. **Use `docs/162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` before describing a release as workflow-controlled, runbook-executed, handoff-ready, or repeatably produced**: identify runbook, stage order, entry and exit criteria, evidence artifacts, validation point, packaging point, fresh-extraction result, skipped stages, handoff limits, allowed claims, forbidden claims, and open workflow debt.
24. **Add a new operator only when compression, adversarial testing, calibration, propagation analysis, terminology audit, commitment-status assignment, application-dossier reporting, precedent-reuse / appeal review, transmission-safety review, reception audit, release-gate review, lineage-compatibility review, provenance/reproducibility review, review-warrant analysis, public-reliance analysis, stewardship analysis, continuity-register analysis, validation analysis, and workflow analysis all support it**: the case must not be handled well by existing files even after applying the method-selection rules, family map, comparison classes, artifact-risk filters, counterexample ledger, calibration controls, update-footprint worksheet, term-status crosswalk, claim-status register, decision-record protocol, precedent-reuse / appeal protocol, transmission-packet protocol, reception-packet protocol, release-packet, lineage-packet, provenance-packet, review-packet, public-reliance-packet, stewardship-packet, continuity-register protocol, validation transcript, and workflow runbook protocols.

If a new addition does none of these, it is probably archive bloat.

## What this revision still does not do

- It does **not** reduce metaphysics to current physics, semantics, or conceptual engineering.
- It does **not** assume that all dependence is one relation with one logic.
- It does **not** assume that numerical identity, individuality, and haecceity are one problem with one answer across all domains.
- It does **not** treat higher-level reality as either magical independence or mere shorthand.
- It does **not** store large source artifacts; it cites them.
- It does **not** treat public availability, repeated citation, teaching uptake, or review wording as permission for public reliance outside the claim's stated version, status, audience, source scope, review warrant, and public-use packet.
- It does **not** treat permission to cite, teach, fork, summarize, adapt, or rely as proof that someone has accepted update, warning, source-watch, correction, migration, high-stakes, or handoff duties.
- It does **not** treat a named stewardship duty as operationally maintained unless there is a register entry, watch trigger, notice path, closure condition, and successor-memory field appropriate to the claim.
- It does **not** treat a local schema, validation transcript, automated script, YAML register, manifest, runbook, workflow trace, automation record, semantic-fidelity record, deployment-boundary record, or dashboard-like file as philosophical review, source authority, public infrastructure, independent certification, public CI, public semantic certification, operational deployment authority, domain advice, or proof that no conceptual drift remains.
- It does **not** treat monitoring status, effectiveness class, residual-risk trend, sunset condition, or a local monitoring register as active public monitoring, source-watch automation, derivative ecosystem coverage, independent effectiveness audit, domain compliance, or proof that future failures have been prevented.
- It does **not** treat a risk-portfolio packet, exposure map, correlation class, priority table, heatmap, or burden inventory as public risk management, independent portfolio audit, domain certification, source-watch coverage, derivative ecosystem monitoring, compliance assurance, or proof that cumulative risk is low.
- It does **not** treat a capacity packet, backlog item, WIP class, deferral class, queue, owner label, or runbook step as public project management, staffing, service-level commitment, public issue tracking, source-watch coverage, operational maintenance, domain authority, or proof that priority work is handled.
- It does **not** treat generated summaries, diagrams, tables, teaching handouts, prompt answers, source digests, or derivative excerpts as faithful merely because they are clear, authorized, validated, or well formatted; semantic fidelity still requires target, basis, status, warning, non-verdict, source, version, and public-use retention.
- It does **not** treat manifest validity as proof of provenance, and it does not yet include a public repository, independent rebuild transcript, public issue tracker, public continuity dashboard, public derivative registry, source-watch automation, public release pipeline, public CI service, independent workflow re-execution, or external validation service.
- It does **not** pretend the basal layer is settled once and for all.
- It does **not** assume every property predicate tracks a real repeatable.
- It does **not** infer a heavy ontology of possible worlds merely from the usefulness of modal semantics.
- It does **not** assume that facts, events, objects, and relations are interchangeable ontological categories.
- It does **not** assume that all relations are either reducible to intrinsic features or equally fundamental as a flat class.
- It does **not** assume that arbitrary sums, vague margins, or co-located material bases already settle what counts as one serious thing.
- It does **not** assume that causal language can float free of whether the case is about production, difference-making, intervention, sustaining, prevention, or omission.
- It does **not** assume that the metaphysics of time is already settled by choosing, without argument, among presentism, eternalism, or a growing-block picture.
- It does **not** assume that a verdict on absolute vs. relational space, or on spatial co-location, can be read straight off from ordinary occupancy talk without further category, constitution, and boundary analysis.
- It does **not** assume that every existential idiom or indispensable discourse automatically earns the same ontological status, or that derivative reality and merely representational convenience are the same thing.
- It does **not** assume that every “I/here/now/actual/current” fact can be flattened without loss into one impersonal description, or that the need for a center automatically implies subjectivism or relativism.
- It does **not** assume that all teleology reduces either to conscious design or to empty as-if description, or that local purposive order automatically scales up to a cosmic design thesis.
- It does **not** assume that every objective, formal, or truth-bearing discourse forces one and the same heavyweight ontology of abstract entities, or that paraphrase and eliminativism are automatically cheaper.
- It does **not** assume that mere possibility, standing power, readiness, becoming, and fulfilled actuality are one flat status, or that every “can” claim tracks a real potency.
- It does **not** assume that every use of “higher” and “lower” names one global ontological ladder, or that explanatory autonomy and metaphysical fundamentality always coincide.
- It does **not** assume that every true, useful, or indispensable predicate tracks an equally natural property or kind, or that one final vocabulary must serve every legitimate domain equally well.
- It does **not** assume that the finest available description is automatically the deepest metaphysical description, or that broader determinables are always mere shorthand for narrower determinates.
- It does **not** assume that no-difference-without-difference claims already settle identity, realization, grounding, reduction, or explanatory sufficiency, or that supervenience is the same thing as the deeper relation that may explain it.
- It does **not** assume that every circular or feedback-rich case is therefore anti-foundational, or that every acceptable metaphysical architecture must be a simple terminating ladder.
- It does **not** assume that social reality is either a free-floating supra-human substance or a mere verbal overlay on brute physical events.
- It does **not** assume that information, content, and representation are one flat ontological kind, or that every meaningful vehicle requires the same semantics or the same ontology.
- It does **not** assume that every action-like or control-like pattern is equally genuine agency, or that the metaphysics of agency is settled either by flat event-causation or by a blanket appeal to freedom.
- It does **not** assume that every center of experience or self-reference is already a full person, or that every person must be a hidden inner ego detached from embodiment, history, and social position.
- It does **not** assume that every reportable, attended, or information-rich state is already conscious experience, or that the difficulty of explaining consciousness automatically forces a detached mental substance.
- It does **not** assume that every happening is the same kind of process, that every dynamic case implies a global doctrine of passage, or that process realism requires dissolving all individuals into undifferentiated flux.
- It does **not** assume that whatever is manifestly given is therefore metaphysically basic, or that whatever is theory-mediated is therefore less real.
- It does **not** assume that every coordinated pattern is already an organized whole, that every organized whole is just a mechanism, or that mechanism-talk by itself settles the ontology of organisms, institutions, or other maintained systems.
- It does **not** assume that every true sentence automatically requires its own fact, that every fact is fundamental, or that facts, events, propositions, and states of affairs are one flat category.
- It does **not** assume that an attractive distinction, analogy, family route, or ordinary-language label has earned promotion until hostile variations have tried to break it.

## File map

- `ARCHIVE_INDEX.md` — compact index.
- `docs/00-start-here.md` — archive orientation.
- `docs/01-working-synthesis-layered-process-realism.md` — current best synthesis.
- `docs/02-comparative-map-of-live-options.md` — nearby theories and fault lines.
- `docs/03-method-selection-and-compression-rules.md` — archive discipline.
- `docs/04-open-questions-and-discriminating-tests.md` — research frontier.
- `docs/05-source-citations.md` — minimal bibliography and anchor citations.
- `docs/06-kernel-operators.md` — minimal operator set for the archive.
- `docs/07-real-emergence-admission-test.md` — stricter criterion for emergence.
- `docs/08-dependence-relations-map.md` — relations not to collapse.
- `docs/09-basal-options-scorecard.md` — compact adjudication matrix for the fundamental level.
- `docs/10-laws-powers-and-structure.md` — current answer on lawfulness and modality.
- `docs/11-objections-and-replies.md` — pressure profile for the default view.
- `docs/12-unity-sortals-and-persistence.md` — entityhood, counting, and persistence discipline.
- `docs/13-truthmakers-absences-and-privation.md` — truth, negation, omission, and lack without ontology blow-up.
- `docs/14-properties-universals-tropes-and-kinds.md` — repeatability, particularized features, and kind realism.
- `docs/15-essence-possibility-and-necessity.md` — modal discipline, essence, and the status of world-talk.
- `docs/16-category-discipline-objects-events-facts-relations.md` — category profile across objects, events, facts, relations, and kinds.
- `docs/17-mereology-composition-and-boundaries.md` — part-whole, boundary, and integrated-whole discipline.
- `docs/18-causation-production-counterfactuals-and-intervention.md` — causal discipline across production, difference-making, models, and omissions.
- `docs/19-time-change-tense-and-passage.md` — temporal discipline across order, persistence, tense, passage, and asymmetry.
- `docs/20-space-place-location-and-co-location.md` — spatial discipline across region, place, location, overlap, co-location, and distributed presence.
- `docs/21-being-existence-and-ontological-commitment.md` — metaontological discipline across existence, fundamentality, commitment, and ontological seriousness.
- `docs/22-teleology-function-and-directedness.md` — teleological discipline across function, purposiveness, role, malfunction, and directed organization.
- `docs/23-abstracta-propositions-numbers-and-structures.md` — abstracta discipline across mathematical entities, propositions, structures, and idealized models.
- `docs/24-potentiality-actuality-and-actualization.md` — potentiality discipline across powers, readiness, actualization, fulfillment, and frustration.
- `docs/25-relations-internality-externality-and-holism.md` — relation discipline across internality, externality, order, direction, and typed holism.
- `docs/26-levels-scales-and-cross-level-explanation.md` — levels discipline across fundamentality, scale, mechanism, autonomy, and cross-level linkage.
- `docs/27-vagueness-indeterminacy-and-borderline-ontology.md` — indeterminacy discipline across vagueness, borderlines, counting, and unsettled cases.
- `docs/28-substance-bearers-and-substrata.md` — substance discipline across bearers, bundles, substrata, and process-stabilized individuals.
- `docs/29-identity-individuality-and-haecceity.md` — identity discipline across sameness, individuality, reidentification, and thisness.
- `docs/30-naturalness-joint-carving-and-ontic-selectivity.md` — naturalness discipline across elite properties, kinds, variables, and joint-carving profiles.
- `docs/31-determinables-determinates-and-explanatory-grain.md` — grain discipline across determinables, determinates, thresholds, structured ranges, and proportionate explanation.
- `docs/32-supervenience-realization-and-modal-covariance.md` — supervenience discipline across no-difference constraints, realization, stronger dependence, and cross-level covariance.
- `docs/33-well-foundedness-loops-and-architectural-direction.md` — architectural discipline across hierarchy, bounded descent, feedback, reciprocity, and coherentist pressure.
- `docs/34-nonexistents-fiction-and-merely-possible-objects.md` — nonexistent-object discipline across fiction, possibility, intentional targets, and typed reference.
- `docs/35-constitution-coincidence-and-material-constitution.md` — constitution discipline across coincidence, material basis, derivative objecthood, and typed divergence.
- `docs/36-things-stuff-fields-and-distributed-being.md` — distributed-being discipline across thinghood, stuffhood, fields, media, and spread-out concrete modes.
- `docs/37-social-ontology-status-functions-and-institutional-reality.md` — social-ontology discipline across institutions, statuses, offices, organizations, records, and dependent-yet-real social order.
- `docs/38-information-representation-and-aboutness.md` — representation discipline across signals, semantic content, propositions, models, records, and typed aboutness.
- `docs/39-symmetry-invariance-and-surplus-structure.md` — symmetry discipline across invariance, transformation, gauge-style redundancy, broken symmetry, and surplus structure.
- `docs/40-chance-probability-and-objective-uncertainty.md` — chance discipline across credence, frequency, propensity, single-case chance, effective probability, and typed objective uncertainty.
- `docs/41-continuity-discreteness-and-granularity.md` — granularity discipline across continuity, discreteness, quantization, threshold structure, sampling, and typed resolution.
- `docs/42-indexicality-self-location-and-centered-reality.md` — indexicality discipline across self-location, centered facts, role-position, and situated actuality.
- `docs/43-agency-control-and-self-governance.md` — agency discipline across behavior, intentional action, organized control, self-governance, delegated or distributed agency, and freedom-loaded cases.
- `docs/44-normativity-reasons-and-deontic-structure.md` — normativity discipline across reasons, permissions, requirements, correctness conditions, authority structures, and typed objective norm-governed order.
- `docs/45-persons-selves-and-first-personal-subjects.md` — person discipline across organism, subject, self, person, persona, role, first-personal integration, and typed personal reality.
- `docs/46-life-organisms-and-living-form.md` — life discipline across organism, biological individuality, self-maintenance, living form, dormancy, and typed organismality.
- `docs/47-consciousness-experience-and-phenomenal-subjectivity.md` — consciousness discipline across phenomenality, access, report, subjecthood, self-consciousness, mental causation pressure, and typed conscious reality.
- `docs/48-fundamentality-grounding-and-metaphysical-explanation.md` — grounding/fundamentality discipline across priority, basis, metaphysical explanation, ontological dependence, and typed depth claims.
- `docs/49-matter-form-and-hylomorphic-organization.md` — matter/form discipline across material basis, organizational form, composite unity, hylomorphism, and persistence through turnover.
- `docs/50-processes-activities-and-becoming.md` — process discipline across events, activities, accomplishments, achievements, states, maintenance, and process-sustained being.
- `docs/51-worldhood-totality-and-priority-monism.md` — disciplined treatment of the actual world, totality, whole/part priority, and the relation between cosmic ontology and possible-worlds apparatus.
- `docs/52-appearance-manifestation-and-the-manifest-image.md` — appearance discipline across perceptual presentation, phenomenal manifestation, manifest/scientific-image fit, mediated disclosure, and typed reality-answerability.
- `docs/53-organization-constraints-and-mechanisms.md` — organization discipline across aggregates, mechanisms, constraints, autonomous systems, institutions, networks, and maintained coordination.
- `docs/54-powers-dispositions-abilities-and-manifestation.md` — power discipline across dispositions, abilities, susceptibilities, authorities, manifestation, masking, and typed modal capacities.
- `docs/55-structure-patterns-networks-and-relational-constitution.md` — structure discipline across relation, pattern, network, symmetry-linked order, model-structure, and relational constitution.
- `docs/56-facts-states-of-affairs-and-obtaining.md` — fact discipline across facts, states of affairs, obtaining, truthmaking pressure, and typed factual realism.
- `docs/57-truth-correspondence-and-reality-answerability.md` — truth discipline across truthbearers, truthmakers, broad correspondence, deflationary uses of truth, approximate scientific truth, and typed reality-answerability.
- `docs/58-ontological-status-robustness-and-derivative-reality.md` — status discipline across fundamentality, derivative but robust reality, thin dependence, idealized world-tracking posits, and merely representational or fictional cases.
- `docs/59-objectivity-mind-independence-and-response-dependence.md` — objectivity discipline across mind-independence, observer-sensitivity, response-dependence, institutional objectivity, centered facts, and merely private or projective seeming.
- `docs/60-indispensability-representation-and-ontological-promotion.md` — promotion discipline across explanatory indispensability, target/vehicle distinction, plural successful models, world-tracking idealization, representational scaffolding, and earned ontological promotion.
- `docs/61-measurement-detection-and-operationalization.md` — measurement discipline across setup, detection, readout, proxy tracking, operational criteria, calibration, theory-ladenness, and typed world-disclosure.
- `docs/62-directness-mediation-and-world-contact.md` — directness discipline across presentation, representation, interface mediation, instrument access, perspective, and typed world-contact.
- `docs/63-evidence-confirmation-and-underdetermination.md` — evidence discipline across data, support, confirmation, underdetermination, theory change, and typed ontological promotion.
- `docs/64-abduction-explanatory-virtues-and-ontological-inference.md` — abduction discipline across inference to the best explanation, explanatory virtues, no-miracles pressure, selective realism, and typed ontological inference.
- `docs/65-robustness-triangulation-and-convergent-access.md` — convergence discipline across repetition, reproducibility, triangulation, family-of-model robustness, plural partial access, and typed convergent realism.
- `docs/66-artifact-risk-distortion-and-failure-modes.md` — artifact discipline across illusion, distortion, proxy mismatch, setup effects, model-imposed patterns, correction regimes, and typed failure-mode realism.
- `docs/67-access-architecture-disclosure-correction-and-ontological-discipline.md` — access-architecture discipline across disclosure, registration, correction, support, and ontological promotion.
- `docs/68-reference-designation-and-target-fixation.md` — reference discipline across naming, denotation, target-fixation, centered anchoring, institutional designation, proxy capture, and typed reference failure.
- `docs/69-ontological-revision-retention-and-elimination.md` — revision discipline across preservation, reinterpretation, target-splitting, target-merging, status change, approximate retention, and elimination under theory change.
- `docs/70-contrast-classes-rival-carvings-and-comparative-ontological-choice.md` — contrast discipline across genuine rivalry, recarving, scale-shift, layered coexistence, and typed comparative ontological choice.
- `docs/71-idealization-approximation-and-limit-cases.md` — idealization discipline across abstraction, approximation, controlled distortion, ideal limits, effective-regime realism, and merely heuristic scaffolding.
- `docs/72-equivalence-reformulation-and-duality.md` — equivalence discipline across empirical sameness, formal reformulation, gauge redundancy, duality, preserved structure, and underdetermined ontology.
- `docs/73-regimes-domains-and-scope-conditions.md` — regime discipline across ceteris-paribus laws, effective theories, bounded domains of validity, phase transitions, cross-regime linkage, and typed scope realism.
- `docs/74-metametaphysics-substantiveness-verbalism-and-worldly-difference.md` — a filter for when an apparent ontology dispute is substantive, status-level, scope-relative, or merely verbal.
- `docs/75-autonomy-closure-self-maintenance-and-self-governance.md` — a filter for when closure, self-maintenance, self-governance, or local autonomy are real without being metaphysical exemption.
- `docs/76-scaffolding-support-niche-construction-and-environmental-enablement.md` — a filter for when support, scaffolding, niche construction, and constitutive inclusion are being confused.
- `docs/77-porous-boundaries-selective-exchange-and-regulated-openness.md` — a filter for when openness, permeability, and traffic across a boundary preserve one target rather than dissolving it.
- `docs/78-repair-resilience-plasticity-and-adaptive-reorganization.md` — a filter for when recovery, resilience, and adaptive change preserve one target rather than replacing it.
- `docs/79-dormancy-latency-standby-and-suspended-activity.md` — a filter for when inactivity, sleep, standby, and suspended exercise preserve one target rather than collapsing into loss.
- `docs/80-delegation-proxying-handoff-and-distributed-enactment.md` — a filter for when action through delegates, proxies, offices, and distributed relays preserves one target rather than dissolving into many or inflating into one giant bearer.
- `docs/81-malfunction-pathology-deviance-and-misfire.md` — a filter for when deviation, dysfunction, pathology, social mismatch, corruption, and misfire are being confused.
- `docs/82-masking-inhibition-suppression-and-blocked-manifestation.md` — a filter for when blocked display, suppression, masking, inhibition, and genuine loss are being confused.
- `docs/83-onset-activation-threshold-crossing-and-phase-entry.md` — a filter for when beginnings, activations, threshold crossings, and phase-entries are being confused.
- `docs/84-cessation-deactivation-offlining-and-terminal-ending.md` — a filter for when stoppage, revocation, dissolution, death, and going offline are being confused.
- `docs/85-reactivation-recurrence-restart-and-return.md` — a filter for when resumption, reactivation, recurrence, reinstatement, restart, and reconstruction are being confused.
- `docs/86-succession-inheritance-descent-and-lineage-continuity.md` — a filter for when persistence, office succession, lineage continuity, charter continuity, design inheritance, and tradition transmission are being confused.
- `docs/87-duplication-copying-fission-and-branching-continuity.md` — a filter for when persistence, duplication, fission, branching continuation, archive-based restoration, and repeatable-type multiplicity are being confused.
- `docs/88-fusion-merger-coalescence-and-convergent-unity.md` — a filter for when coalition, composition, incorporation, higher-order integration, and merger are being confused.
- `docs/89-overlap-shared-parts-interpenetration-and-partial-commonality.md` — a filter for when shared parts, shared basis, interpenetration, and partial commonality are being confused.
- `docs/90-exclusion-incompatibility-occupancy-limits-and-mutual-blocking.md` — a filter for when contradiction, incompatibility, one-slot conflict, competition, and blocked manifestation are being confused.
- `docs/91-counteraction-cancellation-neutralization-and-net-suppression.md` — a filter for when net-zero outcomes, compensation, neutralization, and countervailing balance are being confused.
- `docs/92-overdetermination-redundancy-backup-and-failover.md` — a filter for when co-sufficient causes, backup pathways, redundancy, degeneracy, and failover are being confused.
- `docs/93-amplification-synergy-catalysis-and-positive-feedback.md` — a filter for when stronger-together gain, catalytic enablement, self-reinforcing loops, recruitment cascades, and runaway amplification are being confused.
- `docs/94-negative-feedback-buffering-homeostasis-and-stabilizing-control.md` — a filter for when damping, buffering, negative feedback, homeostatic range-maintenance, and adaptive retuning are being confused.
- `docs/95-synchronization-entrainment-rhythm-and-phase-locking.md` — a filter for when coincidence, pacing, entrainment, synchronization, phase locking, resonance, and gating are being confused.
- `docs/96-desynchronization-phase-drift-phase-slip-and-decoherence.md` — a filter for when drift, phase slips, cluster fracture, decoherence, and collapse are being confused.
- `docs/97-gating-coupling-tuning-and-selective-responsiveness.md` — a filter for when standing receptivity, gating, tuning, coupling, selective coherence, and missed-window nonresponse are being confused.
- `docs/98-saturation-overload-refractory-periods-and-capacity-limits.md` — a filter for when saturation, refractory nonresponse, bottlenecks, overload, depletion, and protective throttling are being confused.
- `docs/99-habituation-sensitization-desensitization-and-response-recalibration.md` — a filter for when habituation, sensitization, desensitization, tolerance, and allostatic retuning are being confused.
- `docs/100-attractors-basins-metastability-and-landscape-constraint.md` — a filter for when attractors, basins, metastability, hysteresis, and structured wandering are being confused.
- `docs/101-history-sensitivity-traces-records-and-sedimented-constraint.md` — a filter for when traces, records, scars, trained dispositions, and path-dependent carryover are being confused.
- `docs/102-critical-transitions-bifurcation-resilience-loss-and-landscape-reorganization.md` — a filter for when threshold entry, resilience loss, bifurcation, tipping, and landscape reorganization are being confused.
- `docs/103-attrition-wear-fatigue-degradation-and-reserve-erosion.md` — a filter for when wear, fatigue, cumulative degradation, reserve erosion, compensated continuity, and maintenance-dependent persistence are being confused.
- `docs/104-irreversibility-hysteresis-ratcheting-and-return-asymmetry.md` — a filter for when irreversibility, hysteresis, ratcheting, plastic change, commitment, and repair-dependent return are being confused.
- `docs/105-fragility-brittleness-vulnerability-and-cascade-susceptibility.md` — a filter for when fragility, brittleness, vulnerability, chokepoint dependence, cascade propagation, and robust-yet-fragile organization are being confused.
- `docs/106-compartmentalization-modularity-insulation-and-firebreaks.md` — a filter for when modularity, compartmentalization, insulation, quarantine, and firebreak architecture are being confused.
- `docs/107-delay-lag-aftereffect-and-temporal-decoupling.md` — a filter for when delay, lag, queueing, phase offset, staged production, and reporting lag are being confused.
- `docs/108-inertia-momentum-coasting-and-overshoot.md` — a filter for when inertia, coasting, overshoot, oscillatory settling, and transient carry-through are being confused.
- `docs/109-friction-drag-viscosity-impedance-and-dissipative-resistance.md` — a filter for when friction, drag, viscosity, impedance mismatch, damping, and stick-slip are being confused.
- `docs/110-elasticity-compliance-strain-storage-and-prestressed-potential.md` — a filter for when reversible deformation, compliance, stored strain, prestress, springback, and viscoelastic relaxation are being confused.
- `docs/111-slack-tolerance-bands-deadband-backlash-and-clearance.md` — a filter for when slack, tolerance bands, deadband, backlash, clearance, and excess play are being confused.
- `docs/112-interference-noise-crosstalk-and-parasitic-coupling.md` — a filter for when noise, interference, crosstalk, parasitic coupling, cancellation, and channel capture are being confused.
- `docs/113-attenuation-filtering-screening-and-shielding.md` — a filter for when attenuation, filtering, screening, shielding, and selective passage are being confused.
- `docs/114-sequestration-binding-trapping-and-selective-retention.md` — a filter for when sequestration, binding, trapping, selective retention, and absence are being confused.
- `docs/115-release-discharge-unloading-and-mobilization.md` — a filter for when release, discharge, unloading, mobilization, and first activation are being confused.
- `docs/116-leakage-seepage-permeation-and-uncontrolled-escape.md` — a filter for when leakage, seepage, permeation, uncontrolled escape, and controlled release are being confused.
- `docs/117-accumulation-pooling-deposition-and-localized-buildup.md` — a filter for when accumulation, pooling, deposition, localized burden, and residue are being confused.
- `docs/118-depletion-drawdown-consumption-and-stock-exhaustion.md` — a filter for when depletion, drawdown, consumption, stock exhaustion, and ending are being confused.
- `docs/119-replenishment-recharge-restocking-and-stock-reconstitution.md` — a filter for when replenishment, recharge, restocking, reserve reconstitution, and repair are being confused.
- `docs/120-turnover-renewal-exchange-and-constituent-cycling.md` — a filter for when turnover, renewal, exchange, component replacement, and bearer replacement are being confused.
- `docs/121-circulation-throughput-recirculation-and-organized-throughflow.md` — a filter for when circulation, throughput, recirculation, flushing, and organized throughflow are being confused.
- `docs/122-bottlenecks-congestion-backpressure-and-chokepoints.md` — a filter for when bottlenecks, congestion, spillback, backpressure, and chokepoint dependence are being confused.
- `docs/123-rerouting-diversion-bypass-and-shunting.md` — a filter for when rerouting, diversion, bypass, shunting, repair, leakage, and duplication are being confused.
- `docs/124-substitution-replacement-stand-ins-and-functional-equivalence.md` — a filter for when functional equivalence, part replacement, stand-ins, prosthetic support, and successor replacement are being confused.
- `docs/125-migration-transplantation-porting-and-redeployment.md` — a filter for when migration, transplantation, porting, redeployment, copying, and successor formation are being confused.
- `docs/126-hosting-lodging-carriage-and-guest-occupancy.md` — a filter for when hosting, lodging, carriage, tenancy, platform support, parasitic residence, and incorporation are being confused.
- `docs/127-attachment-anchoring-tethering-mooring-and-docking.md` — a filter for when attachment, anchoring, tethering, mooring, docking, mounting, and incorporation are being confused.
- `docs/128-embedding-insertion-implantation-and-insetting.md` — a filter for when insertion, embedding, implantation, insetting, hosting, and constitutive incorporation are being confused.
- `docs/129-enclosure-encasement-casing-housing-and-encapsulation.md` — a filter for when enclosure, encasement, casing, housing, encapsulation, hosting, and embedding are being confused.
- `docs/130-coating-cladding-lining-surfacing-and-veneering.md` — a filter for when coating, cladding, lining, surfacing, veneering, wrapping, and mere appearance are being confused.
- `docs/131-wrapping-sheathing-draping-shrouding-and-bandaging.md` — a filter for when wrapping, sheathing, draping, shrouding, bandaging, coating, and enclosure are being confused.
- `docs/132-lamination-interleaving-sandwiching-and-stratified-stacking.md` — a filter for when lamination, interleaving, sandwiching, stratified stacking, composite integration, and mere layering are being confused.
- `docs/133-sealing-closure-plugging-gasketing-and-caulking.md` — a filter for when sealing, closure, plugging, gasketing, caulking, valving, and leakage control are being confused.
- `docs/134-joining-bonding-welding-brazing-and-soldering.md` — a filter for when joining, bonding, welding, brazing, soldering, attachment, clamping, and fusion are being confused.
- `docs/135-articulation-hinging-pivoting-and-socketed-coupling.md` — a filter for when articulation, hinging, pivoting, socketed coupling, support, guiding, and joining are being confused.
- `docs/136-clamping-compression-locking-cinching-crimping-and-press-fit-retention.md` — a filter for when clamping, compression locking, cinching, crimping, press-fit retention, joining, and gripping are being confused.
- `docs/137-latching-capture-keying-detents-and-positive-lock-engagement.md` — a filter for when latching, capture, keying, detents, positive-lock engagement, clamping, and attachment are being confused.
- `docs/138-threading-screwing-bolting-nutting-and-helical-fastening.md` — a filter for when threading, screwing, bolting, nutting, helical fastening, preload, clamping, and joining are being confused.
- `docs/139-meshing-gearing-splining-interdigitation-and-toothed-engagement.md` — a filter for when meshing, gearing, splining, interdigitation, toothed engagement, gripping, and articulation are being confused.
- `docs/140-gripping-traction-friction-drive-and-slip-limited-engagement.md` — a filter for when gripping, traction, friction-drive, slip-limited engagement, clamping, support, and meshing are being confused.
- `docs/141-support-bearing-suspension-hanging-bracing-and-load-path-carriage.md` — a filter for when support, bearing, suspension, hanging, bracing, scaffolding, hosting, and load-path carriage are being confused.
- `docs/142-guiding-channeling-conduiting-ducting-and-rail-guided-passage.md` — a filter for when guidance, channeling, conduiting, ducting, rail-guided passage, support, hosting, and valving are being confused.
- `docs/143-valving-throttling-metering-and-aperture-control.md` — a filter for when valving, throttling, metering, aperture control, guidance, sealing, bottlenecking, and generic gating are being confused.
- `docs/144-operator-family-map-and-triage-grid.md` — a family map and triage grid for routing cases across existing operators before adding another first-order distinction.
- `docs/145-adversarial-stress-tests-and-revision-protocol.md` — a red-team protocol for testing preferred diagnoses against hostile variations before promotion, demotion, or consolidation.
- `docs/146-diagnostic-case-ledger-calibration-set-and-benchmark-protocol.md` — a diagnostic case ledger and calibration benchmark protocol for preserving reusable hard cases, negative controls, regression cases, and update debt.
- `docs/147-revision-dependency-graph-update-propagation-and-drift-control.md` — a dependency graph and drift-control protocol for propagating accepted changes through the archive before packaging a revision.
- `docs/148-terminology-register-synonym-control-and-crosswalk-protocol.md` — a terminology register, synonym-control, metaphor-quarantine, and crosswalk protocol for preventing vocabulary from doing unearned operator-work.
- `docs/149-claim-status-register-maturity-levels-and-commitment-governance.md` — a claim-status register, maturity ladder, and commitment-governance protocol for preventing useful distinctions, files, examples, terms, or source-local rules from becoming stronger doctrine than the archive has earned.
- `docs/150-application-dossier-decision-record-and-verdict-report-protocol.md` — an application dossier, decision-record schema, and verdict-report protocol for turning routed, stress-tested, status-assigned results into auditable, reusable verdicts.
- `docs/151-precedent-reuse-appeal-transfer-and-review-governance.md` — a precedent-reuse, appeal, transfer, supersession, and teaching-governance protocol for preventing dossiered verdicts from becoming unbounded slogans.
- `docs/152-transmission-excerpt-compression-and-pedagogical-governance.md` — a transmission, excerpt-compression, pedagogical, and output-governance protocol for preventing responsible verdicts from becoming stronger, flatter, or more current-sounding when summarized or exported.
- `docs/153-reception-feedback-errata-and-correction-loop-governance.md` — a reception, feedback, errata, and correction-loop protocol for classifying downstream uptake, misreadings, criticisms, teaching failures, source-boundary failures, operational failures, and package-drift signals before feedback revises doctrine.
- `docs/154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md` — a release-gate, maintenance-ledger, deprecation, migration, hotfix, rollback, and package-readiness protocol for deciding when a change may become a versioned archive package.
- `docs/155-version-lineage-compatibility-forking-and-migration-governance.md` — a version-lineage, compatibility, fork, merge, citation, and migration-governance protocol for deciding how released packages, older versions, forks, derivative artifacts, citations, and migrations relate without false continuity.
- `docs/156-provenance-custody-build-evidence-and-reproducibility-governance.md` — a provenance, custody, build-evidence, artifact-trust, import/recovery, source-dependent, derivative, and reproducibility-governance protocol for deciding whether a package or related artifact can be trusted, rebuilt, cited, imported, or quarantined.
- `docs/157-review-authority-audit-certification-and-claim-warrant-governance.md` — a review-authority, audit-certification, and claim-warrant governance protocol for deciding what kind of review has occurred and what claim language that review permits.
- `docs/158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md` — a public-reliance, citation, dispute, withdrawal, and retraction governance protocol for deciding what a reviewed or released claim permits once it circulates publicly.
- `docs/159-stewardship-obligations-delegated-authority-and-accountability-governance.md` — a stewardship, obligation, delegated-authority, handoff, and accountability-governance protocol for deciding who must preserve, monitor, route, correct, migrate, refuse, or hand off the duties created by public and derivative use.
- `docs/160-operational-registers-watch-queues-and-continuity-memory-governance.md` — an operational-register, watch-queue, notice-path, closure-evidence, and continuity-memory protocol for deciding where accepted duties are recorded, awakened, closed, inherited, or marked as open debt.
- `docs/161-validation-harness-invariant-checks-and-machine-readable-governance.md` — a validation-harness, invariant-check, schema, failure-severity, local-register, and automation-boundary protocol for deciding what a package, packet, register, script, or transcript may honestly claim to have checked.
- `docs/162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` — a release-workflow, runbook, execution-trace, stage-gate, validation-point, package-point, and handoff-governance protocol for deciding whether a release process itself was executed in a controlled, repeatable, successor-readable order.
- `docs/163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md` — an automation-boundary, delegated-agent, scheduled-execution, and tool-permission governance protocol for deciding what tool-assisted or scheduled action may honestly claim.
- `docs/164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md` — a semantic-fidelity, generated-output-audit, and warning-retention protocol for deciding whether summaries, diagrams, generated answers, teaching outputs, source digests, release notes, or derivative excerpts preserve the source's target, basis, status, warnings, non-verdicts, source boundaries, version limits, and public-use permissions.
- `docs/165-operational-reliance-deployment-boundaries-and-action-use-governance.md` — an operational-reliance, deployment-boundary, and action-use protocol for deciding whether faithful archive-derived material may be used as policy, procedure, classifier, decision support, automated trigger, operational guidance, or high-stakes domain advice.
- `docs/166-incident-response-harm-review-near-miss-and-recovery-governance.md` — an incident-response, harm-review, near-miss, evidence-preservation, recovery, and closure protocol for deciding what must happen when archive-derived action-use or attempted action-use goes wrong.
- `docs/167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` — a post-incident learning, root-cause, corrective/preventive action, recurrence-risk, and verification protocol for deciding what must change after recovery so the same failure pattern does not recur.
- `docs/168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md` — a longitudinal monitoring, effectiveness-review, residual-risk trend, and sunset/renewal protocol for deciding whether learned controls remain effective, when residual risk changes, and when controls should be renewed, escalated, migrated, or retired.
- `docs/169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` — a cross-case risk-portfolio, systemic-exposure, correlation/common-cause, cumulative-burden, and prioritization protocol for deciding whether individually bounded risks combine into a portfolio that must be monitored, consolidated, blocked, escalated, domain-reviewed, or release-stopped.
- `docs/170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` — a capacity-planning, resource-allocation, backlog-admission, WIP-limit, and deferral/resource-debt protocol for deciding whether priority items are actually resourced, assigned, scheduled, blocked, deferred, or unsafe to claim as handled.
- `REGISTERS/README.md` — local-register scope note.
- `REGISTERS/schemas/validation-record-v1.yml` — local validation-record schema vocabulary.
- `REGISTERS/schemas/workflow-run-record-v1.yml` — local workflow-run record schema vocabulary.
- `REGISTERS/schemas/automation-boundary-record-v1.yml` — local automation-boundary record schema vocabulary.
- `REGISTERS/schemas/semantic-fidelity-record-v1.yml` — local semantic-fidelity and warning-retention record schema vocabulary.
- `REGISTERS/schemas/deployment-boundary-record-v1.yml` — local operational-reliance and deployment-boundary record schema vocabulary.
- `REGISTERS/schemas/incident-response-record-v1.yml` — local incident-response, harm-review, near-miss, recovery, and closure record schema vocabulary.
- `REGISTERS/schemas/post-incident-learning-record-v1.yml` — local post-incident learning, root-cause, CAPA, recurrence-risk, and verification record schema vocabulary.
- `REGISTERS/schemas/effectiveness-monitoring-record-v1.yml` — local longitudinal monitoring, effectiveness-review, residual-risk trend, and sunset/renewal record schema vocabulary.
- `REGISTERS/schemas/risk-portfolio-record-v1.yml` — local risk-portfolio, systemic-exposure, correlation/common-cause, cumulative-burden, and prioritization record schema vocabulary.
- `REGISTERS/schemas/capacity-allocation-record-v1.yml` — local capacity-planning, backlog-admission, work-in-progress, and deferral/resource-debt record schema vocabulary.
- `REGISTERS/rev0155-release-validation.yml` — historical local release-validation transcript for rev0155.
- `REGISTERS/rev0156-release-validation.yml` — historical local release-validation transcript for rev0156.
- `REGISTERS/rev0156-release-workflow.yml` — historical local release-workflow execution trace for rev0156.
- `REGISTERS/rev0157-release-validation.yml` — historical local release-validation transcript for rev0157.
- `REGISTERS/rev0157-release-workflow.yml` — historical local release-workflow execution trace for rev0157.
- `REGISTERS/rev0157-automation-boundary.yml` — historical local automation-boundary record for rev0157.
- `REGISTERS/rev0158-release-validation.yml` — historical local release-validation transcript for rev0158.
- `REGISTERS/rev0158-release-workflow.yml` — historical local release-workflow execution trace for rev0158.
- `REGISTERS/rev0158-automation-boundary.yml` — historical local automation-boundary record for rev0158.
- `REGISTERS/rev0158-semantic-fidelity.yml` — historical local semantic-fidelity and warning-retention record for rev0158.
- `REGISTERS/rev0159-release-validation.yml` — historical local release-validation transcript for rev0159.
- `REGISTERS/rev0159-release-workflow.yml` — historical local release-workflow execution trace for rev0159.
- `REGISTERS/rev0159-automation-boundary.yml` — historical local automation-boundary record for rev0159.
- `REGISTERS/rev0159-semantic-fidelity.yml` — historical local semantic-fidelity and warning-retention record for rev0159.
- `REGISTERS/rev0159-deployment-boundary.yml` — historical local operational-reliance and deployment-boundary record for rev0159.
- `REGISTERS/rev0160-release-validation.yml` — historical local release-validation transcript for rev0160.
- `REGISTERS/rev0160-release-workflow.yml` — historical local release-workflow execution trace for rev0160.
- `REGISTERS/rev0160-automation-boundary.yml` — historical local automation-boundary record for rev0160.
- `REGISTERS/rev0160-semantic-fidelity.yml` — historical local semantic-fidelity and warning-retention record for rev0160.
- `REGISTERS/rev0160-deployment-boundary.yml` — historical local operational-reliance and deployment-boundary record for rev0160.
- `REGISTERS/rev0160-incident-response.yml` — historical local incident-response, near-miss, harm-review, and recovery record for rev0160.
- `REGISTERS/rev0161-release-validation.yml` — local release-validation transcript for this package.
- `REGISTERS/rev0161-release-workflow.yml` — local release-workflow execution trace for this package.
- `REGISTERS/rev0161-automation-boundary.yml` — local automation-boundary record for this package.
- `REGISTERS/rev0161-semantic-fidelity.yml` — local semantic-fidelity and warning-retention record for this package.
- `REGISTERS/rev0161-deployment-boundary.yml` — local operational-reliance and deployment-boundary record for this package.
- `REGISTERS/rev0161-incident-response.yml` — local incident-response, near-miss, harm-review, and recovery record for this package.
- `REGISTERS/rev0161-post-incident-learning.yml` — historical local post-incident learning, root-cause, CAPA, recurrence-risk, and verification record for rev0161.
- `REGISTERS/rev0162-release-validation.yml` — local release-validation transcript for this package.
- `REGISTERS/rev0162-release-workflow.yml` — local release-workflow execution trace for this package.
- `REGISTERS/rev0162-automation-boundary.yml` — local automation-boundary record for this package.
- `REGISTERS/rev0162-semantic-fidelity.yml` — local semantic-fidelity and warning-retention record for this package.
- `REGISTERS/rev0162-deployment-boundary.yml` — local operational-reliance and deployment-boundary record for this package.
- `REGISTERS/rev0162-incident-response.yml` — local incident-response, near-miss, harm-review, and recovery record for this package.
- `REGISTERS/rev0162-post-incident-learning.yml` — local post-incident learning, root-cause, CAPA, recurrence-risk, and verification record for this package.
- `REGISTERS/rev0162-effectiveness-monitoring.yml` — historical local longitudinal monitoring, effectiveness-review, residual-risk trend, and sunset/renewal record for rev0162.
- `REGISTERS/rev0163-release-validation.yml` — local release-validation transcript for this package.
- `REGISTERS/rev0163-release-workflow.yml` — local release-workflow execution trace for this package.
- `REGISTERS/rev0163-automation-boundary.yml` — local automation-boundary record for this package.
- `REGISTERS/rev0163-semantic-fidelity.yml` — local semantic-fidelity and warning-retention record for this package.
- `REGISTERS/rev0163-deployment-boundary.yml` — local operational-reliance and deployment-boundary record for this package.
- `REGISTERS/rev0163-incident-response.yml` — local incident-response, near-miss, harm-review, and recovery record for this package.
- `REGISTERS/rev0163-post-incident-learning.yml` — local post-incident learning, root-cause, CAPA, recurrence-risk, and verification record for this package.
- `REGISTERS/rev0163-effectiveness-monitoring.yml` — local longitudinal monitoring, effectiveness-review, residual-risk trend, and sunset/renewal record for this package.
- `REGISTERS/rev0163-risk-portfolio.yml` — local cross-case risk-portfolio, systemic-exposure, correlation, cumulative-burden, and prioritization record for the prior package.
- `REGISTERS/rev0164-release-validation.yml` — local validation transcript for this package.
- `REGISTERS/rev0164-release-workflow.yml` — local release-workflow trace for this package.
- `REGISTERS/rev0164-automation-boundary.yml` — local automation-boundary record for this package.
- `REGISTERS/rev0164-semantic-fidelity.yml` — local semantic-fidelity / warning-retention record for this package.
- `REGISTERS/rev0164-deployment-boundary.yml` — local deployment-boundary record for this package.
- `REGISTERS/rev0164-incident-response.yml` — local incident-response record for this package.
- `REGISTERS/rev0164-post-incident-learning.yml` — local post-incident learning record for this package.
- `REGISTERS/rev0164-effectiveness-monitoring.yml` — local effectiveness-monitoring record for this package.
- `REGISTERS/rev0164-risk-portfolio.yml` — local risk-portfolio record for this package.
- `REGISTERS/rev0164-capacity-allocation.yml` — local capacity-planning, backlog, WIP, and deferral record for this package.
- `RUNBOOKS/release-workflow-v1.md` — local release workflow runbook.
- `RUNBOOKS/automation-delegation-v1.md` — local automation delegation and tool-permission runbook.
- `RUNBOOKS/semantic-fidelity-review-v1.md` — local semantic-fidelity and warning-retention review runbook.
- `RUNBOOKS/deployment-boundary-review-v1.md` — local operational-reliance and deployment-boundary review runbook.
- `RUNBOOKS/incident-response-review-v1.md` — local incident-response, harm-review, near-miss, recovery, and closure review runbook.
- `RUNBOOKS/post-incident-learning-review-v1.md` — local post-incident learning, root-cause, CAPA, recurrence-risk, and verification review runbook.
- `RUNBOOKS/effectiveness-monitoring-review-v1.md` — local longitudinal monitoring, effectiveness-review, residual-risk, and sunset/renewal review runbook.
- `RUNBOOKS/risk-portfolio-review-v1.md` — local cross-case risk-portfolio, systemic-exposure, correlation, cumulative-burden, and prioritization review runbook.
- `RUNBOOKS/capacity-allocation-review-v1.md` — local capacity-planning, backlog-admission, WIP-limit, and deferral/resource-debt review runbook.
- `tools/validate_archive.py` — minimal local package-structure, expected artifact, and manifest validator.
- `VERSION` — revision marker.
- `MANIFEST.sha256` — integrity manifest.

## Revision note

This revision is a **capacity-planning, resource-allocation, backlog-admission, work-in-progress-limit, and deferral/resource-debt governance revision**. It does not add another first-order metaphysical operator. Instead, it governs the layer after risk-portfolio prioritization: when a portfolio review says some work is important, what must be stated before the archive says that work is assigned, scheduled, manageable, monitored, safe to defer, release-compatible, or handled?

This revision classifies `rev0164` as a local capacity-allocation governance release with CAP2/CAP3 local capacity for the package build, BL4 release-candidate backlog admission, WIP7 completion with local evidence, and DEF2/DEF4 warning/release-debt discipline for future capacity gaps. It adds no new external source anchors, no new first-order operator, no public project-management system, no public issue tracker, no staffing, no service-level commitment, no source-watch operation, no external review capacity, no domain authority, and no operational maintenance. Its purpose is to prevent future work from confusing portfolio priority with executable capacity or treating deferred duties as silently handled.


Rev0165 schema/datacube front-door artifacts: `EXTERNAL_CROSSWALK.yml`, `RUNBOOKS/schema-conformance-datacube-review-v1.md`, `REGISTERS/schemas/schema-conformance-report-v1.yml`, `REGISTERS/schemas/control-stack-record-v1.yml`, `REGISTERS/schemas/datacube-index-record-v1.yml`, `REGISTERS/rev0166-schema-conformance.yml`, `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, and `tools/query_cube.py`.

Rev0165 standalone conformance report: `REGISTERS/schema-conformance-report-rev0166.yml`.


## Rev0166 addendum: status vocabulary, reference integrity, query regression, claim language, and provenance

Final numbered document: `docs/172-status-vocabulary-reference-integrity-query-regression-claim-language-and-provenance-governance.md`.

New required artifacts: `STATUS_VOCABULARY.yml`, `REFERENCE_MAP.yml`, `QUERY_REGRESSION_SUITE.yml`, `CLAIM_LANGUAGE_LEDGER.yml`, `PROVENANCE_LEDGER.yml`, `RUNBOOKS/status-reference-query-regression-review-v1.md`, `tools/check_reference_integrity.py`, and `tools/run_query_regression.py`.

The package may claim local status-token checks, local path-reference checks over declared surfaces, local query-regression execution, claim-language boundary recording, local unsigned provenance rows, and fresh-extraction validator success. It must not claim public RDF/DCAT/RO-Crate/Frictionless/JSON Schema/SHACL/PROV/SKOS/FAIR/SPDX/SLSA/in-toto/NIST compliance, external audit, public monitoring, source currency, or operational readiness.

## Rev0167 addendum: invariants, traceability, change impact, migration, and fixtures

Final numbered document: `docs/173-invariant-catalog-traceability-matrix-change-impact-migration-and-fixture-governance.md`.

New required artifacts: `INVARIANT_CATALOG.yml`, `TRACEABILITY_MATRIX.yml`, `CHANGE_IMPACT_MATRIX.yml`, `MIGRATION_LEDGER.yml`, `FIXTURE_CORPUS.yml`, `RUNBOOKS/invariant-traceability-migration-fixture-review-v1.md`, `tools/check_invariants.py`, `tools/check_traceability.py`, and `tools/run_fixture_corpus.py`.

The package may claim local invariant cataloging, local traceability rows, local change-impact recording, local migration/deprecation classification, local representative fixture pressure, local current-record/schema/status/reference/query/provenance checks, and fresh-extraction validator success. It must not claim formal verification, semantic truth validation, exhaustive QA, public CI, public issue tracking, Semantic Versioning compliance, OpenLineage emission, Great Expectations deployment, ODRL publication, external audit, source currency, domain review, or operational readiness.


## Rev0168 addendum: claim graph, evidence packets, contradiction, freshness, and defeasance

Final numbered document: `docs/174-claim-graph-evidence-packets-contradiction-freshness-and-defeasance-governance.md`.

New required artifacts: `CLAIM_GRAPH.yml`, `EVIDENCE_PACKET_INDEX.yml`, `CONTRADICTION_LEDGER.yml`, `FRESHNESS_POLICY.yml`, `DEFEASANCE_PROPAGATION.yml`, `RUNBOOKS/claim-evidence-defeasance-review-v1.md`, `tools/check_claim_evidence.py`, `REGISTERS/claim-graph-report-rev0168.yml`, `REGISTERS/evidence-packet-report-rev0168.yml`, `REGISTERS/contradiction-report-rev0168.yml`, `REGISTERS/freshness-report-rev0168.yml`, and `REGISTERS/defeasance-report-rev0168.yml`.

The package may claim local claim-node governance, local evidence-packet indexing, local contradiction-state recording, local freshness-window policy, local defeasance-propagation rules, local query/fixture pressure for these rows, and fresh-extraction validator success. It must not claim public nanopublication, public RDF/knowledge-graph publication, evidence-ontology conformance, source-watch automation, current external fact review, independent fact-checking, domain authority, public QA, or operational readiness.


## Rev0169 addendum: release gate policy, acceptance criteria, risk acceptance, waivers, decisions, and assurance case skeleton

Final numbered document: `docs/175-release-gate-policy-acceptance-criteria-risk-acceptance-and-assurance-case-governance.md`.

New required artifacts: `RELEASE_GATE_POLICY.yml`, `ACCEPTANCE_CRITERIA_MATRIX.yml`, `RELEASE_DECISION_LEDGER.yml`, `WAIVER_EXCEPTION_LEDGER.yml`, `RISK_ACCEPTANCE_LEDGER.yml`, `ASSURANCE_CASE_SKELETON.yml`, `RUNBOOKS/release-gate-decision-assurance-review-v1.md`, `tools/check_release_gates.py`, `REGISTERS/release-gate-report-rev0169.yml`, `REGISTERS/acceptance-criteria-report-rev0169.yml`, `REGISTERS/release-decision-report-rev0169.yml`, `REGISTERS/waiver-exception-report-rev0169.yml`, `REGISTERS/risk-acceptance-report-rev0169.yml`, and `REGISTERS/assurance-case-report-rev0169.yml`.

The package may claim local release-gate policy, local acceptance-criteria rows, local waiver/exception review, local residual-risk acceptance boundaries, local release-decision recording, and a local assurance-case skeleton checked by `tools/check_release_gates.py`. It must not claim OPA/Rego policy-as-code conformance, OSCAL assessment publication, SACM assurance-case conformance, independent approval, signed attestation, external audit, secure software certification, public CI, operational release authority, or public deployment readiness.

Bet 99: a claim can be warranted, fresh, queryable, and defeasible while still failing the question that matters for release: which gates passed, which risks were accepted, which waivers were refused or bounded, and which decision language is allowed after the gate result?


## Rev0170 update: reproducibility, attestation boundary, custody, execution log, rollback, and public-release packet governance

Rev0170 adds `docs/176-reproducibility-attestation-evidence-chain-custody-rollback-and-public-release-boundary-governance.md`, `BUILD_REPRODUCIBILITY_LEDGER.yml`, `ATTESTATION_BOUNDARY_LEDGER.yml`, `EVIDENCE_CHAIN_CUSTODY.yml`, `EXECUTION_LOG_LEDGER.yml`, `ROLLBACK_RETRACTION_PLAN.yml`, `PUBLIC_RELEASE_ATTESTATION.yml`, and `tools/check_repro_attestation.py`.

The new layer records a local build recipe, explicit unsigned-attestation boundary, package-internal evidence custody rows, local execution-log expectations, rollback/retraction triggers, and a bounded public-release packet. It does not claim bit-for-bit reproducibility, hermetic builds, independent rebuild, signed provenance, SLSA level, Sigstore/cosign signature, in-toto attestation, SCITT transparency receipt, legal chain of custody, public CI, external approval, operational deployment readiness, or source-current/domain-authoritative review.

## Rev0171 post-release observability, audit, feedback, reliance, drift, and exercise layer

Current final document: `docs/177-post-release-observability-audit-sampling-feedback-reliance-drift-and-exercise-governance.md`.

New current-release artifacts: `OBSERVABILITY_MONITORING_PLAN.yml`, `AUDIT_SAMPLING_PLAN.yml`, `FEEDBACK_INTAKE_LEDGER.yml`, `DOWNSTREAM_RELIANCE_LEDGER.yml`, `DRIFT_ANOMALY_LEDGER.yml`, `EXERCISE_INCIDENT_DRILL_LEDGER.yml`, and `tools/check_observability_feedback.py`.

Rev0171 keeps rev0170's unsigned/local attestation boundary and adds post-release accountability surfaces. It does not claim public monitoring, public support, continuous telemetry, downstream recall authority, independent audit, legal attestation, or operational deployment readiness.

## Rev0172 remediation, severity, local objectives, corrective action, escalation, and closure layer

Current final document: `docs/178-remediation-triage-severity-service-objectives-corrective-action-escalation-and-closure-governance.md`.

New current-release artifacts: `REMEDIATION_TRIAGE_POLICY.yml`, `SEVERITY_CLASSIFICATION_MATRIX.yml`, `SERVICE_OBJECTIVE_LEDGER.yml`, `CORRECTIVE_ACTION_REGISTER.yml`, `COMMUNICATION_ESCALATION_LEDGER.yml`, `CLOSURE_VERIFICATION_LEDGER.yml`, `RUNBOOKS/remediation-triage-corrective-action-closure-review-v1.md`, and `tools/check_remediation_closure.py`.

Rev0172 keeps rev0171's post-release observability boundary and adds local remediation accountability. It does not claim public support, service-level commitments, legal incident response, external notification duty, public recall authority, independently audited remediation, or operational deployment readiness.


## Rev0175 addition — accountability and authority governance

This revision adds `docs/179-role-authority-accountability-assignment-segregation-delegation-approval-and-review-governance.md` plus the local accountability surfaces `ROLE_AUTHORITY_MATRIX.yml`, `ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml`, `SEGREGATION_OF_DUTIES_POLICY.yml`, `DELEGATION_HANDOFF_LEDGER.yml`, `APPROVAL_CONSENT_LEDGER.yml`, `ACCOUNTABILITY_REVIEW_LEDGER.yml`, `RUNBOOKS/accountability-authority-review-v1.md`, and `tools/check_accountability_authority.py`.  The added layer prevents local role labels, assignment rows, approvals, warnings, handoffs, and delegated execution from being upgraded into external review, public consent, legal authority, public support, or operational deployment permission.


## rev0177 security/abuse-resistance governance layer

Rev0176 adds `docs/182-security-threat-model-abuse-misuse-vulnerability-hardening-trust-boundary-and-secret-governance.md`, `SECURITY_THREAT_MODEL.yml`, `ABUSE_MISUSE_CASE_REGISTER.yml`, `VULNERABILITY_DISCLOSURE_INTAKE.yml`, `SECURITY_HARDENING_BASELINE.yml`, `TRUST_BOUNDARY_LEDGER.yml`, `SECRET_KEY_MATERIAL_POLICY.yml`, `tools/check_security_abuse.py`, and `RUNBOOKS/security-abuse-threatmodel-review-v1.md`. The layer records local security/abuse boundaries only. It does not claim secure deployment, penetration testing, SAST/DAST, dependency scanning, secret scanning, public vulnerability disclosure, bug bounty, PSIRT/CERT, key management, code signing, or cybersecurity compliance.


## rev0177 lifecycle sustainability, preservation, portability, succession, and sunset layer

Rev0177 adds `docs/183-maintainership-dependency-preservation-portability-succession-and-end-of-life-governance.md`, `MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml`, `DEPENDENCY_UPDATE_POLICY.yml`, `PRESERVATION_ARCHIVAL_PLAN.yml`, `PORTABILITY_INTEROPERABILITY_MATRIX.yml`, `SUCCESSION_CONTINUITY_PLAN.yml`, `SUNSET_END_OF_LIFE_LEDGER.yml`, `RUNBOOKS/lifecycle-sustainability-preservation-review-v1.md`, and `tools/check_lifecycle_sustainability.py`.

The layer records local maintainership, dependency-update, preservation, portability, succession, and sunset/end-of-life boundaries. It does not claim public support, maintenance SLA, automated dependency scanning, archival preservation, public hosting, certified interoperability, legal succession, downstream migration, public EOL notice service, or operational continuity.


## rev0179 ethics/public-interest, affected-party, fairness/bias, misuse-sensitive release, and benefit/harm layer

Rev0179 adds `docs/185-ethical-impact-public-interest-affected-party-fairness-misuse-sensitive-and-benefit-harm-governance.md`, `ETHICAL_IMPACT_ASSESSMENT.yml`, `PUBLIC_INTEREST_BALANCING_LEDGER.yml`, `AFFECTED_PARTY_ANALYSIS.yml`, `FAIRNESS_BIAS_REVIEW_LEDGER.yml`, `MISUSE_SENSITIVE_RELEASE_POLICY.yml`, `BENEFIT_HARM_REGISTER.yml`, `RUNBOOKS/ethics-public-interest-review-v1.md`, and `tools/check_ethics_public_interest.py`.

The layer records local ethical-impact, public-interest, affected-party, fairness/bias, misuse-sensitive-release, and benefit/harm boundaries. It does not claim ethics approval, IRB review, stakeholder consultation, social license, democratic mandate, fairness audit, bias-free status, unrestricted-release clearance, public safety certification, net-benefit proof, or legal/public authority.


## rev0180 accessibility, comprehension, localization, guidance, and inclusive-access layer

Rev0180 adds `docs/186-accessibility-readability-discoverability-localization-onboarding-and-inclusive-access-governance.md`, `ACCESSIBILITY_REVIEW_PLAN.yml`, `READABILITY_PLAIN_LANGUAGE_LEDGER.yml`, `DISCOVERABILITY_NAVIGATION_MAP.yml`, `LOCALIZATION_TRANSLATION_BOUNDARY.yml`, `USER_GUIDANCE_ONBOARDING_LEDGER.yml`, `INCLUSIVE_ACCESS_RISK_REGISTER.yml`, `RUNBOOKS/accessibility-comprehension-inclusion-review-v1.md`, and `tools/check_accessibility_comprehension.py`.

The layer records local accessibility, readability/plain-language, discoverability/navigation, localization/translation-boundary, onboarding/guidance, and inclusive-access risk controls. It does not claim WCAG conformance, accessibility certification, assistive-technology testing, legal accessibility compliance, plain-language certification, comprehension testing, complete findability, public discovery service, official translation, localization completion, multilingual support, public training, public support, equitable access, barrier elimination, public accommodation, or external usability/accessibility review.


## rev0182 additional required cube artifacts

- `CONCEPT_FAMILY_MAP.yml`
- `CONCEPT_RELATION_MAP.yml`
- `CUBE_AUDIT_LEDGER.yml`
- `CUBE/observations/concept_relations.yml`
- `CUBE/observations/cube_audit.yml`

## Carried-forward source-cube refactor surfaces

- `SOURCE_CROSSWALK_NORMALIZED.yml`
- `SOURCE_CITATION_INDEX.yml`
- `SOURCE_FAMILY_MAP.yml`
- `SOURCE_RELATION_MAP.yml`
- `SOURCE_AUDIT_LEDGER.yml`



## rev0185 debt-cube refactor artifacts

- DEBT_OBSERVATION_INDEX.yml
- DEBT_LIFECYCLE_POLICY.yml
- DEBT_RELATION_MAP.yml
- DEBT_AUDIT_LEDGER.yml
- CUBE/observations/debt_relations.yml
- CUBE/observations/debt_audit.yml
- tools/check_debt_cube_refactor.py
- tools/check_debt_audit.py
- docs/191-debt-cube-lifecycle-prioritization-remediation-audit-governance.md
