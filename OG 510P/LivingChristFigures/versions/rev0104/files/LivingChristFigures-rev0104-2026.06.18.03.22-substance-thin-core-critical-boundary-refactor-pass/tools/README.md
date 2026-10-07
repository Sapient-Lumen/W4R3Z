# tools

`qa_cube.py` runs package-level structural checks for rev0024+ packages:

```bash
python tools/qa_cube.py .
```

It checks no archive directories or bundled zips, required front matter, current ledger/index counts, public/longform infrastructure files, live-referral safety fields, final SHA256SUMS verification, and rev0025+ identity-coherence checks across candidate front matter, Candidate-Ledger, Claim-Ledger, Evidence-Debt, public index, Candidate-Index, and CUBE-MAP labels.

rev0026 adds checks for candidate office_ids pointing to existing office cards, claim source IDs pointing to Source-Registry rows, duplicate source IDs, and duplicate candidate IDs.

rev0027: qa_cube.py now checks source candidate references, evidence-debt candidate references, refresh related-candidate references, source seen-in-files paths, and front-matter office_ids agreement.


`redaction_scan.py` was added in rev0030:

```bash
python tools/redaction_scan.py . --write-report --fail-on-high
```

It scans the working cube for configured public-export hazards: contact digits near helpline/hotline/toll-free/contact language, email-like strings, exact coordinate pairs, address-like strings, and grave/case/Medical-Examiner-number-like identifiers. It is deliberately conservative about operational digits and deliberately incomplete about narrative privacy; manual review remains required.

rev0030: qa_cube.py now calls the redaction-risk scan and fails on open configured high-risk findings.

## schema_validate.py

Added in rev0031. Validates the schema/contract layer:

```bash
python tools/schema_validate.py . --write-report --fail-on-high
```

It checks front-matter contracts, ledger headers, CSV/JSON mirror parity,
source-type controlled vocabulary, and public-manifest revision agreement.
`tools/qa_cube.py` imports and runs this validator as part of normal QA.

## evidence_lifecycle.py

Added in rev0032. Generates `META/Claim-Evidence-Strength-current.*` and `META/Refresh-Priority-Queue-current.*`. These reports route refresh/caution labor; they are not truth scores.

Usage:

```bash
python tools/evidence_lifecycle.py . --write-report
```


## rev0033 meta-instrument checks

`qa_cube.py` now also checks that the negative-case ledger, online-research intake, and operator-update audit files exist, have unique IDs, and contain the fields needed for behavior-change/source-promotion review.

## rev0034 QA extensions

`qa_cube.py` now checks the source-promotion decision ledger, public-claim quarantine, refresh-sprint matrix, and rules 31-32 coverage. It also verifies that quarantine claim IDs are drawn from lifecycle rows classified as `now_or_before_any_public_claim`.


## rev0035 QA extensions

`qa_cube.py` now checks the source-promotion transaction audit, public-claim release ledger, and rule 33 coverage. It also verifies that released claims are not still present in `META/Public-Claim-Quarantine-current.*` and that release source IDs exist in `Source-Registry-current.csv`.


## rev0036 QA extensions

`qa_cube.py` now checks boundary-rule coverage through rule 34. Rev0036 promotes a counterevidence source without releasing any public current-capacity claim, so QA continues to require transaction source IDs to exist and quarantine coverage to match lifecycle-now claims.


## rev0037-0038 QA extensions

rev0037 checks boundary-rule coverage through rule 35 for conflict-zone mutual-aid no-map gates. Rev0038 extends boundary-rule coverage through rule 36 for border counterpressure / no-route observation gates.


## rev0039 QA extensions

rev0039 extends boundary-rule coverage through rule 37 for survivor-service standards/funding no-referral gates.

## rev0040 QA addition
QA now expects boundary-rule coverage through rule 38, the family-led missing-person search / no-field-map rule.


## rev0041 QA note

`qa_cube.py` now requires boundary-rule coverage through rule 39, including the protection-order / legal-framework is not a survivor-service door rule.


## rev0041 lifecycle note

`evidence_lifecycle.py` now treats explicit public-claim quarantine rows as safety overrides, keeping those claims in the now-or-before-public-claim lane even when new source counts would otherwise lower derived freshness risk.

## rev0049 tools

- `public_contract_check.py` verifies that files in `PUBLIC/` exactly match the package release contract.
- `rule46_scan.py` performs a focused MMIWG2S+ no-case-list/no-vigil-map extraction scan.
- `render_public_safe_index.py` regenerates the scrubbed public candidate index from the current candidate ledger.
- `evidence_lifecycle.py` now reads claim-type taxonomy hints and source harm/link policy fields rather than relying only on a fixed boundary-type list.


## rev0050 tools

- `public_export_eligibility.py` generates `META/Public-Export-Eligibility-current.*`; it classifies the safest current public shape for every candidate and names URL, capacity, image, case-detail, and governance review gates.
- `render_public_safe_index.py` now reads the eligibility ledger before regenerating the scrubbed public index, adding `public_export_tier` and `public_shape_template` to the public CSV/JSON/Markdown outputs.
- `schema_validate.py` and `qa_cube.py` now check eligibility coverage, allowed tiers/templates, governance-decision files, and rule 50 coverage.


- `public_source_link_review.py` generates `META/Public-Source-Link-Review-current.*`, one row per Source Registry URL, so public URL exposure is separately gated from internal source use.


## rev0051 tools

- `public_release_lint.py` scans only `PUBLIC/` files and writes `META/Public-Release-Lint-current.*`; high findings block public handoff. It catches raw URLs, images, emails, coordinates, contact shortcodes/digits near hotline/helpline/lifeline language, and un-negated case/route/capacity phrases.
- `sensitive_surface_inventory.py` writes `META/Sensitive-Surface-Inventory-current.*`, an internal inventory of configured contact, route, case-record, image/event, current-capacity, URL, and implementation-scorecard surfaces across the working package.
- `candidate_governance_snapshot.py` writes `META/Candidate-Governance-Snapshot-current.*` and `META/Governance-Review-Queue-current.*`, joining public eligibility, source-link review, lifecycle, consent/governance, and refresh posture.
- `qa_cube.py` now fails if `__pycache__` artifacts are shipped, if public lint has high findings, if candidate governance snapshot coverage drifts, or if rule 51/52 coverage is missing.


## rev0052 tools

- `row_validate.py` reads `SCHEMA/Row-Validation-Contract-current.json` and writes `SCHEMA/Row-Validation-Report-current.*`; it checks row-level required values, unique ids, dates, controlled values, paths, and cross-ledger references.
- `generated_artifact_provenance.py` writes `META/Generated-Artifact-Provenance-current.*`, recording generator scripts, inputs, artifact hashes, input fingerprints, and row counts for key generated reports.
- `revision_surface_audit.py` writes `META/Revision-Surface-Audit-current.*`, catching stale current-revision headers and JSON package-revision fields in front-door files.
- `release_gate_attestation.py` writes `META/Release-Gate-Attestation-current.*`, joining the current handoff gates into one pass/fail bundle.
- `qa_cube.py` and `schema_validate.py` now enforce these reports before clean extraction handoff.

## rev0053 dependency/public/governance hardening tools

- `public_index_parity.py` checks public CSV/JSON/Markdown mirror parity, public manifest count parity, eligibility tier/template parity, non-release sentinel values, and absence of raw URL/email contact surfaces in the public index.
- `governance_consistency_audit.py` checks agreement across candidate ledger, public eligibility, governance snapshot, review queue, consent/case-name ledger, source-link review, public index, and governance decision rows.
- `package_dependency_graph.py` records generated-artifact, public-contract, ledger-mirror, frontmatter-contract, and tool-inventory dependency edges.
- `release_gate_attestation.py` now includes gates for public-index parity, governance consistency, and package dependency graph coverage.


## rev0054 mirror/schema/inventory tools

- `csv_json_mirror_audit.py` writes `META/CSV-JSON-Mirror-Audit-current.*` and compares sibling CSV/JSON pairs by row count, header/key order, row order, and exact cell values.
- `schema_coverage_audit.py` writes `META/Schema-Coverage-Audit-current.*` and separates blocking mirror/companion failures from non-blocking schema-backlog rows.
- `package_file_inventory.py` writes `META/Package-File-Inventory-current.*`, classifying stable files by zone, role, currentness, generator, and public-release scope.
- `release_gate_attestation.py` now includes gates for mirror audit, schema coverage, and package file inventory.
- `field_schema_consistency.py`: checks `SCHEMA/*-Fields-current.csv` companions and exact target-header parity; added rev0056.


## rev0056 traceability/path-reference tools

- `path_reference_audit.py` writes `META/Path-Reference-Audit-current.*` and checks current handoff/governance/public/schema/meta path references for resolvable package-relative targets.
- `rule_gate_traceability.py` writes `META/Rule-Gate-Traceability-current.*` and maps rules 15+ to coverage rows, release gates, tools, and reports.
- `tool_run_matrix.py` writes `META/Tool-Run-Matrix-current.*` and classifies packaged tools by role, provenance coverage, dependency graph coverage, release-gate participation, and QA visibility.
- `required_document_coverage.py` writes `META/Required-Document-Coverage-current.*` and verifies front-door/README files, revision-bearing surfaces, public contract file sets, governance contract paths, and generated-report companions.


## rev0057 audit selftest / deterministic rebuild-readiness tools

- `audit_selftest.py` writes `META/Audit-Selftest-current.*`; it creates temporary package copies, injects controlled defects, and confirms selected auditors fail as intended. The self-tests cover public URL leakage, CSV/JSON mirror drift, stale revision surfaces, missing package-relative paths, row-contract breaks, and PUBLIC/ allowlist drift.
- `rebuild_readiness_audit.py` writes `META/Rebuild-Readiness-Audit-current.*`; it reads the generated-artifact spec, checks generators, inputs, output companions, duplicate artifact declarations, CLI/write modes, and obvious nondeterministic primitives before handoff.


## rev0058 release proof tools

- `policy_assertion_matrix.py`: maps handoff/release claims to policy surfaces, gates, tools, and evidence reports.
- `regeneration_sequence_plan.py`: emits a deterministic, plan-only command sequence for regenerating tracked artifacts.
- `archive_build_manifest.py`: records archive-build assumptions, root/export alignment, public allowlist equality, and deterministic ZIP/checksum policy.
- `selftest_coverage_matrix.py`: maps critical release gates to controlled-mutation selftests.


## rev0059 release-closure tools

- `checksum_scope_audit.py`: verifies that `SHA256SUMS.txt` covers the complete stable package scope and contains no out-of-scope paths.
- `public_negative_corpus.py`: runs controlled public-release lint fixtures for URLs, images, email, coordinates, contact digits, case phrases, route/map phrases, capacity phrases, and boundary-language demotion.
- `release_evidence_closure.py`: checks that release gates, policy assertions, selftest coverage, generated-artifact provenance, and package-file inventory close against each other.
## rev0060 packaging-identity tools

`archive_member_manifest.py`, `unicode_path_audit.py`, and `package_identity_audit.py` add handoff packaging checks for intended ZIP member paths, Unicode filename normalization/mojibake hazards, and root/manifest/refresh/checksum identity closure.

## rev0062 lineage/delta/reference tools

- `version_lineage_audit.py` checks manifest/public/contract/root/refresh lineage against the previous-release fingerprint.
- `package_delta_manifest.py` compares current stable files to `META/Previous-Release-Fingerprint-current.json`.
- `cross_report_reference_audit.py` checks that stale previous-release identity does not present as current.
- `handoff_review_digest.py` emits a compact reviewer digest of release-readiness signals.


## rev0062 tools

- `tools/dependency_cycle_audit.py` — checks generated-artifact dependency cycles.
- `tools/handoff_notice_audit.py` — checks use-limit notice coverage in front-door surfaces.
- `tools/current_surface_registry.py` — classifies all `*-current.csv` package surfaces.


## rev0063 manifest/review-boundary tools

- `json_key_uniqueness_audit.py` scans package JSON for duplicate object keys that would be parser-dependent.
- `manifest_semantic_coherence_audit.py` checks that manifest semantics, pass type, release notes, root export name, public manifest, release contract, current refresh note, and counts agree with the current pass.
- `review_role_boundary_audit.py` checks that the package has explicit review-role boundaries and that front-door surfaces do not convert review into consent, referral, public URL release, or reuse permission.


## rev0064 helper/refactor tools

- `tools/lib_cube.py` provides small deterministic helpers for CSV/JSON/Markdown report writing and common row/path utilities. Generator scripts that import it set or rely on `PYTHONDONTWRITEBYTECODE=1` during regeneration to avoid shipping bytecode artifacts.
- `tools/helper_adoption_audit.py` writes `META/Helper-Adoption-Audit-current.*` and checks helper presence, helper function inventory, selected refactored tool imports, removal of duplicated companion-writer blocks, companion output continuity, and CSV parseability.
- `csv_json_mirror_audit.py`, `schema_coverage_audit.py`, `field_schema_consistency.py`, and `checksum_scope_audit.py` now use the shared helper for report companion emission.

## rev0065 archive/governance/metadata tools

rev0065 adds archive round-trip and current-pointer coherence tools, plus a governance-surface generator for evidence sprint, source freshness/preservation, permission-state, controlled-vocabulary normalization, helper-adoption scope, and office-accountability reports. Helper adoption remains selected-scope, not full-package migration.

## rev0065 additional hardening tools

- `clean_extract_archive_qa.py`: after final ZIP creation, extracts the archive into a fresh directory and runs `tools/qa_cube.py` from the extracted root.
- `helper_golden_output_audit.py`: selected-scope report-shape/golden-output audit for helper-migrated tools; does not claim full helper migration.


## rev0066 report-contract registry tools

- `tools/report_contract_registry.py` writes `META/Report-Contract-Registry-current.*` and `META/Report-Contract-Audit-current.*`. It discovers every `*-current.csv` surface, records the expected CSV/JSON/Markdown companion policy, schema or ledger-contract basis, generator/manual owner, public-boundary classification, and row-count parity.
- `tools/lib_cube.py` now includes shared report-surface helpers (`current_csv_surfaces`, `expected_field_schema_path`, `csv_row_count`, and `read_generated_artifact_specs`) so future report audits do not duplicate surface-discovery logic.
- `release_gate_attestation.py` now includes gate 57 for report-contract registry/audit closure.


## rev0067 boundary-inheritance / tool-executability tools

- `tools/boundary_domain_map.py` writes `META/Boundary-Domain-Registry-current.*`, `META/Candidate-Boundary-Domain-Map-current.*`, and `META/Boundary-Domain-Coverage-Audit-current.*`. It derives explicit boundary domains from candidate sensitivity, public eligibility, permission-state, office-accountability, source, and claim signals. The output is an audit/refactor layer, not public-release permission.
- `tools/tool_executability_audit.py` writes `META/Tool-Executability-Audit-current.*`. It parses every packaged `tools/*.py` file and records syntax status, CLI/main-guard posture, argparse posture, bytecode-policy signal, helper-import signal, and generated-output declarations without executing the toolchain.
- `release_gate_attestation.py` now includes gates 058 and 059 for these surfaces.
- `qa_cube.py` now treats both surfaces as package-level release checks.

- `identifier_namespace_audit.py` — builds `META/Identifier-Registry-current.*` and `META/Identifier-Convention-Audit-current.*`, checking identifier namespace patterns, uniqueness, and crosslink coherence across candidates, offices, sources, claims, debt, refresh notes, boundary domains, and release gates.


## rev0068 identifier namespace / crosslink tools

- `tools/identifier_namespace_audit.py` writes `META/Identifier-Registry-current.*` and `META/Identifier-Convention-Audit-current.*`. It checks identifier namespace patterns, uniqueness, known-kind coverage, and selected reciprocal crosslinks across candidates, offices, sources, claims, evidence debt, refresh notes, boundary domains, and release gates.
- `release_gate_attestation.py` now includes gate 060 for identifier namespace/crosslink closure.
- `qa_cube.py` now treats the identifier namespace audit as a package-level release check.


## rev0069 claim-source boundary matrix tools

- `tools/claim_source_boundary_audit.py` writes `META/Claim-Source-Boundary-Matrix-current.*` and `META/Claim-Source-Boundary-Audit-current.*`. It joins every claim evidence source to Source Registry harm/link posture, source/candidate reciprocity, candidate canonical-source inclusion, public-use posture, and capacity/referral boundary signals.
- `release_gate_attestation.py` now includes gate 061 for claim-source boundary matrix/audit closure.
- `qa_cube.py` now treats the claim-source boundary audit as a package-level release check.

## rev0070 candidate-discovery intake tools

- `tools/candidate_discovery_intake_audit.py` writes `META/Candidate-Discovery-Intake-Audit-current.*` from `META/Candidate-Discovery-Log-current.*`, checking that every session attempts candidate discovery, distinguishes promoted candidates from parked scouts/context-only findings, requires promoted candidates to exist in the Candidate Ledger, and blocks high-risk public expansion signals.
- `release_gate_attestation.py` now includes gate 062 for candidate-discovery intake closure.
- `qa_cube.py` now treats the candidate-discovery intake audit as a package-level release check.


## rev0071 candidate-discovery current-revision audit refactor

`tools/candidate_discovery_intake_audit.py` now reads `manifest.json` and fails when the candidate-discovery log has no row for the current manifest revision. This preserves the session rule that each pass must attempt new-candidate discovery without forcing unsafe promotion.


## rev0072 candidate-promotion completeness refactor

`tools/candidate_discovery_intake_audit.py` now checks that promoted discovery candidates are fully wired into candidate files, claims, source registry, evidence debt, permission state, office accountability, family/case-name governance when harm-near, and public-claim quarantine for high-risk claims. This keeps candidate discovery primary while preventing shallow promotions.


## rev0073 candidate-source diversity tool

- `tools/candidate_source_diversity_audit.py` writes `META/Candidate-Source-Diversity-Audit-current.*` and checks promoted discovery candidates for resolvable, diverse, claim-used, boundary-aware source packs. It is an internal promotion-quality gate, not public URL release permission.

## rev0075 public-index semantic guardrail / QA refactor

- `tools/public_template_policy.py` centralizes public-safe template dispatch and template-specific broad boundary overrides. Governance quarantine remains a public no-expansion tier; it no longer implies the MMIWG family-led template.
- `tools/public_index_semantic_audit.py` writes `META/Public-Index-Semantic-Audit-current.*` and checks that sentinel rows for MMIWG, identity restitution, migrant-threshold accompaniment, forensic return, and genocide-memory accountability keep their own public templates and broad locations.
- `tools/audit_selftest.py` now includes `selftest_007`, which mutates a non-MMIWG public row into the old MMIWG/Canada shape and requires the semantic audit to fail.
- `release_gate_attestation.py` now includes gate 064 for this semantic audit, and `qa_cube.py` treats it as a release-blocking package check.
## rev0076 source-health tools

`source_maintenance_priority.py`, `source_preservation_status.py`, and `source_freshness_preservation.py` split source-health work into action queue, archive/preservation status, and freshness status. They intentionally do not crawl sources or contact anyone. Gate 065 verifies coverage and prevents the preservation report from becoming a duplicate of the freshness report again.

## rev0086 risk-reduction refactor

This revision adds `source_backfill_coverage_audit.py` so the cumulative backfill ledger can be interpreted as action history while still proving one coverage row per Source Registry source. It also hardens `archive_roundtrip_audit.py` to fail no-compression ZIP regressions and extends `manifest_semantic_coherence_audit.py` to test front-door prose for current-pass alignment.
- `family_profile_consent_audit.py` generates `META/Border-Route-Referral-Boundary-Audit-current.*`, checking family-profile/interview/testimony-near source rows so public visibility is not treated as general consent or public URL permission.
- `border_route_referral_audit.py` generates `META/Border-Route-Referral-Boundary-Audit-current.*`, checking Calais/border-route claims and sources for no-route, no-referral, no-contact, no-camp/site, no-live-aid, no-image, and no-current-capacity leakage.

## rev0094 freshness and transfer-readiness tools

- `tools/current_surface_freshness_audit.py` writes `META/Current-Surface-Freshness-Audit-current.*` and checks that current identity/proof surfaces match the manifest revision/export, front-door text names the current pass shape, the handoff digest is current, and the QA transcript has no fail lines.
- `tools/preservation_transfer_readiness.py` writes `META/Preservation-Transfer-Readiness-current.*` and checks closed fixity/signature surfaces, RO-Crate transfer metadata, PREMIS-lite/PROV-style preservation/provenance surfaces, public-release containment, and external BagIt helper presence.
- `tools/make_bagit_transfer_copy.py` creates an external BagIt-style transfer copy of the package without moving the linked datacube root or converting public-boundary metadata into public-release permission.
- `release_gate_attestation.py` now includes gates 076 and 077 for freshness/readiness closure, and `qa_cube.py` treats both reports as package-level checks.

## rev0095 regeneration coverage refactor

`tools/regeneration_coverage_audit.py` blocks unmanaged `*-current.csv` surfaces by requiring each current report or ledger to be classified as generated/provenance-tracked, regeneration-plan-covered, curated seed/core ledger, schema/governance contract, public generated index, or an explicit late-closure exception. `tools/current_surface_freshness_audit.py` also cross-checks the previous-release fingerprint Markdown against its JSON baseline so reviewer-facing release summaries cannot drift from machine truth.

- `public_export_surface_audit.py` generates `META/Public-Export-Surface-Audit-current.*` and `PUBLIC/PUBLIC-BUNDLE-MANIFEST-current.json`; it distinguishes actual PUBLIC-only payload from reviewer-support evidence so internal ledgers/reports are not accidentally exported.
