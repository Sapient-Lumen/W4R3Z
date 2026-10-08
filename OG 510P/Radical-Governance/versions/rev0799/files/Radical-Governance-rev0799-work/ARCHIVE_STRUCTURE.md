# Archive structure

Current revision: `rev0799`  
Current codename: `stewardhandoff-ownerclock-securitycontact-nocustodybyzip`

## Current revision route

- `archive/997-stewardship-no-custody.md` — stewardship handoff and no custody by ZIP.
- `metadata/archive_stewardship_handoff_controls.json` — canonical non-approved stewardship surface for license, maintainers, contribution, security, route retirement, source preservation, release signing, and succession.
- `generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md` — reader surface for handoff status, gap blockers, source-claim receipts, required documents, role classes, handoff clocks, private-artifact exclusions, and next actions.
- `metadata/source_claim_receipts.json` — adds stewardship receipts as method floors, not owner/legal/security approval.
- `tools/fieldwork_lint_helpers.py` — now includes a bounded archive-stewardship validator alongside fieldwork-chain validators.
- `metadata/gap_ledger.json` — all five live gaps preserved; GAP-032 is in-progress through handoff controls, not repaired.

## Generated routes to inspect after build

- `generated/ARCHIVE_STEWARDSHIP_HANDOFF_CONTROLS.md` — must show stewardship controls as non-approved blockers, not custody or owner decisions.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show stewardship receipts as locator/method floors, not license grants or maintainer appointments.
- `generated/GAP_LEDGER.md` — must keep stewardship, source preservation, route/taxonomy, affected-person validation, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `997`, the stewardship metadata/schema/tool files, and generated surfaces.

## Guardrail

A ZIP is not a custodian. No custody by ZIP.

## Previous structure

## Archive structure

Current revision: `rev0798`  
Current codename: `postclosurewatch-reopenclock-driftguard-noclosureforever`

## Current revision route

- `archive/996-cloudtainer-post-closure-monitoring-reopen-clocks-drift-guards-and-no-closure-forever.md` — post-closure monitoring, reopen clocks, drift guards, and no closure forever.
- `metadata/fieldwork_postclosure_monitoring_controls.json` — canonical post-closure monitoring surface with non-active UI/housing controls for recurrence, drift, source-receipt recheck, limitation, and reopen decisions.
- `generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md` — reader surface for monitoring status, gap blockers, closure-dossier inheritance, source-claim receipt dependencies, drift triggers, cadence classes, and next actions.
- `metadata/source_claim_receipts.json` — adds OMB/GAO monitoring and continuous-improvement receipts as method floors for future post-closure rechecks.
- `tools/fieldwork_lint_helpers.py` — fieldwork follow-on chain helper now validates closure-dossier inheritance for post-closure monitoring controls.
- `metadata/gap_ledger.json` — all five live gaps preserved; post-closure controls move future drift/reopen discipline forward without monitoring authorization, private data, source snapshots, or permanent closure.

## Generated routes to inspect after build

- `generated/FIELDWORK_POSTCLOSURE_MONITORING_CONTROLS.md` — must show monitoring controls as non-active blockers, not verified outcomes or permanent closures.
- `generated/FIELDWORK_CLOSURE_DOSSIERS.md` — must remain the closure-dossier predecessor, not a timeless closure proof surface.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show monitoring receipts as locator-level and non-closing.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `996`, the post-closure monitoring metadata/schema/tool files, and generated surfaces.

## Guardrail

Closure is not finality. Monitoring is not surveillance authority. Reopen triggers are not failure; they are accountability. No closure forever.


## Previous structure


## Archive structure

Current revision: `rev0797`  
Current codename: `closuredossier-attestationmatrix-gapreopen-noattestationoutcome`

## Current revision route

- `archive/995-cloudtainer-closure-dossiers-attestation-matrix-gap-reopen-triggers-and-no-outcome-by-attestation.md` — closure dossiers, attestation matrix, gap reopen triggers, and no outcome by attestation.
- `metadata/fieldwork_closure_dossiers.json` — canonical post-redress closure-dossier surface with non-ready UI/housing controls for material outcome fields, evidence package contents, attestation requirements, unresolved exceptions, and reopen triggers.
- `generated/FIELDWORK_CLOSURE_DOSSIERS.md` — reader surface for closure readiness, gap blockers, redress-control inheritance, source-claim receipt dependencies, material outcome fields, exception classes, and next actions.
- `metadata/source_claim_receipts.json` — adds OMB/GAO evaluation and evidence-building receipts as method floors for future closure packages.
- `tools/fieldwork_lint_helpers.py` — fieldwork follow-on chain helper now validates redress-verification inheritance for closure-dossier surfaces.
- `metadata/gap_ledger.json` — all five live gaps preserved; closure dossiers move future closure discipline forward without private data, owner attestation, remedy custody, or closure.

## Generated routes to inspect after build

- `generated/FIELDWORK_CLOSURE_DOSSIERS.md` — must show closure dossiers as not-ready blockers, not verified outcomes.
- `generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md` — must remain the redress-verification predecessor, not a closure proof surface.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show evidence/evaluation receipts as locator-level and non-closing.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `995`, the closure-dossier metadata/schema/tool files, and generated surfaces.

## Guardrail

Attestations are not outcomes. Closure dossiers are not private evidence rooms. Independent review statements are not claimant payment or household stability. No outcome by attestation.


## Previous structure

Current revision: `rev0796`  
Current codename: `redressverify-followthrough-internalcontrol-noledgeroutcome`

## Current revision route

- `archive/994-cloudtainer-redress-verification-controls-follow-through-ledgers-internal-control-repair-and-no-outcome-by-redress-route.md` — redress verification controls, follow-through ledgers, internal-control repair, and no outcome by redress route.
- `metadata/fieldwork_redress_verification_controls.json` — canonical post-correction redress-verification surface with non-verified UI/housing controls for actual remedy proof, unresolved exceptions, escalation, and public-safe ledger boundaries.
- `generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md` — reader surface for verification status, gap blockers, correction-control inheritance, source-claim receipt dependencies, material outcome fields, and next actions.
- `metadata/source_claim_receipts.json` — adds OMB A-123 and GAO Green Book receipts as corrective-action follow-through supports.
- `tools/fieldwork_lint_helpers.py` — fieldwork follow-on chain helper now validates correction-control inheritance for redress-verification surfaces.
- `metadata/gap_ledger.json` — all five live gaps preserved; redress verification moves follow-through discipline forward without private data, remedy custody, or closure.

## Generated routes to inspect after build

- `generated/FIELDWORK_REDRESS_VERIFICATION_CONTROLS.md` — must show redress verification controls as blockers, not verified outcomes.
- `generated/FIELDWORK_CORRECTION_CONTROLS.md` — must remain the correction-layer predecessor, not a remedy proof surface.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show A-123/Green Book receipts as locator-level and non-closing.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.

## Previous structure

## Archive structure

Current revision: `rev0795`  
Current codename: `correctiongate-redressledger-withdrawalclock-nocorrigendumoutcome`

## Current revision route

- `archive/993-cloudtainer-fieldwork-correction-controls-errata-withdrawal-redress-ledgers-and-no-outcome-by-corrigendum.md` — fieldwork correction controls, errata/withdrawal/redress ledgers, and no outcome by corrigendum.
- `metadata/fieldwork_correction_controls.json` — canonical post-release correction surface with non-activated UI/housing controls for error intake, correction requests, withdrawal/retraction, notification/redress, versioning/citation hygiene, and harm review.
- `generated/FIELDWORK_CORRECTION_CONTROLS.md` — reader surface for correction status, gap blockers, release-control inheritance, source-claim receipt dependencies, and next actions.
- `metadata/source_claim_receipts.json` — adds information-quality and self-review receipts as correction-route supports.
- `tools/fieldwork_lint_helpers.py` — fieldwork follow-on chain helper now validates release-control inheritance for correction surfaces.
- `metadata/gap_ledger.json` — all five live gaps preserved; post-release correction controls move public-output safety forward without closure.

## Generated routes to inspect after build

- `generated/FIELDWORK_CORRECTION_CONTROLS.md` — must show correction controls as blockers, not corrected outcomes.
- `generated/FIELDWORK_RELEASE_CONTROLS.md` — must remain the release-layer predecessor, not a public-output proof surface.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show IQA/SPD4 receipts as locator-level and non-closing.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `993`, the correction-control metadata/schema/tool files, and generated surfaces.

## Guardrail

Errata are not remedies. Withdrawals are not outcomes. Correction requests are not proof of material repair. No outcome by corrigendum.


## Previous archive structure

## Archive structure

Current revision: `rev0794`  
Current codename: `releasegate-disclosurecontrol-publicaudit-nooutputbyrelease`

## Current revision route

- `archive/992-cloudtainer-fieldwork-release-controls-disclosure-limitation-public-output-audit-and-no-outcome-by-release-packet.md` — fieldwork release controls, disclosure limitation, public-output audit, and no outcome by release packet.
- `metadata/fieldwork_release_controls.json` — canonical non-closing UI/housing release-control surface for disclosure limitation, de-identification, public narrative, quality/integrity, harm review, errata/retraction, and release blockers.
- `generated/FIELDWORK_RELEASE_CONTROLS.md` — reader surface for release status, gap blockers, source-claim receipt dependencies, prohibited public outputs, pause conditions, and next actions.
- `metadata/source_claim_receipts.json` — adds public-output, de-identification, and statistical disclosure-limitation method receipts.
- `tools/fieldwork_lint_helpers.py` — shared fieldwork-chain helper now validates follow-on release controls against execution controls.
- `metadata/gap_ledger.json` — all five live gaps preserved; release controls move work forward without public output or closure.

## Generated routes to inspect after build

- `generated/FIELDWORK_RELEASE_CONTROLS.md` — must show release controls as blockers, not field results.
- `generated/FIELDWORK_EXECUTION_CONTROLS.md` — must still show execution controls as non-executed.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show release-control receipts as locator-level and non-closing.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `992`, the release-control metadata/schema/tool files, and the fieldwork lint helper.

## Guardrail

A release packet is not an outcome. Disclosure review is not field validation. De-identification is not disappearance. No outcome by release packet.


## Previous archive structure

## Archive structure

Current revision: `rev0790`  
Current codename: `samplinggate-preservationcontrols-linthelper-noplanclosure`

## Current revision route

- `archive/988-cloudtainer-tail-sampling-gates-nonresponse-bias-preservation-controls-metadata-surface-refactor-and-no-closure-by-sampling-plan.md` — tail-sampling gates, nonresponse-bias floors, preservation controls, metadata-surface refactor, and no closure by sampling plan.
- `metadata/tail_sampling_gates.json` — canonical non-closing UI/housing gate surface with target populations, sample frames, cohort requirements, nonresponse-bias plans, privacy controls, source-preservation controls, and disqualifiers.
- `generated/TAIL_SAMPLING_GATES.md` — reader surface for gate status, gap blockers, source-claim receipt dependencies, cohort requirements, and next actions.
- `metadata/source_claim_receipts.json` — adds sampling, nonresponse-bias, evaluation-planning, and privacy-risk method receipts.
- `tools/metadata_surface.py` — shared helper for receipt/tail generated surfaces.
- `metadata/gap_ledger.json` — all five live gaps preserved; sampling gates and preservation controls move work forward without closure.

## Generated routes to inspect after build

- `generated/TAIL_SAMPLING_GATES.md` — must show gates as design-ready blockers, not field results.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show method/source receipts as locator-level and non-closing.
- `generated/OUTCOME_TAIL_PLANS.md` — must still show UI and housing outcome-tail cohorts and closure floors.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `988`, the tail-gate metadata/schema/tool files, and the shared metadata-surface helper.

## Guardrail

Sampling gates are not samples. Nonresponse-bias plans are not nonresponse-bias evidence. Privacy controls are not permission to store private records. No closure by sampling plan.


## Previous archive structure

## Archive structure

Current revision: `rev0789`  
Current codename: `passagereceipt-tailplan-taxonomyalias-nosourcebyurl`

## Current revision route

- `archive/987-cloudtainer-claim-passage-receipts-outcome-tail-plans-source-health-taxonomy-alias-refactor-and-no-source-by-url.md` — claim-passage receipts, outcome-tail sampling plans, source-health taxonomy alias refactor, and no source by URL.
- `metadata/source_claim_receipts.json` — locator-level public source claim receipts; no snapshots, long quotations, or private records.
- `generated/SOURCE_CLAIM_RECEIPTS.md` — reader surface for source keys, anchors, evidence limits, preservation statuses, and closure blockers.
- `metadata/outcome_tail_plans.json` — privacy-bounded UI and housing case-tail plans with denominator cohorts and material outcome fields.
- `generated/OUTCOME_TAIL_PLANS.md` — reader surface for cohort coverage, gap coverage, and closure floors.
- `metadata/source_health_taxonomy.json` — editable alias map for generated source-health normalization.
- `generated/SOURCE_HEALTH.md` — source-health dependency surface using metadata-defined taxonomy aliases.
- `metadata/gap_ledger.json` — all five live gaps preserved; source preservation and affected-person validation move forward without closure.

## Generated routes to inspect after build

- `generated/SOURCE_CLAIM_RECEIPTS.md` — must show locator-level receipts as blockers, not preservation-complete evidence.
- `generated/OUTCOME_TAIL_PLANS.md` — must show UI and housing cohorts, privacy exclusions, and closure floors.
- `generated/SOURCE_HEALTH.md` — must show normalized taxonomy output sourced from `metadata/source_health_taxonomy.json`.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must include note `987`, the new metadata/schema/tool files, and generated surfaces.

## Guardrail

Claim locators are not source snapshots. Tail plans are not field validation. Taxonomy aliases are not an owner-approved controlled vocabulary. No source by URL.


## Previous archive structure

## Archive structure

Current revision: `rev0788`  
Current codename: `fieldsignal-materialfloor-taxonomypressure-noaggregateclosure`

## Current revision route

- `archive/986-cloudtainer-field-signal-material-outcome-floor-source-receipt-triage-taxonomy-pressure-and-no-closure-by-aggregate.md` — field-signal and material-outcome audit; no closure by aggregate.
- `metadata/evidence_receipts.json` — canonical receipt spine with proof floors, material-outcome dimensions, field-sample requirements, source-receipt levels, denominator gaps, closure blockers, and `can_close_gap`.
- `generated/EVIDENCE_RECEIPTS.md` — proof-floor, material-dimension, source-receipt-level, and closure-blocker surface.
- `generated/SOURCE_HEALTH.md` — source-health dependency surface plus normalized taxonomy-pressure counts.
- `metadata/gap_ledger.json` — all five live gaps preserved; material-outcome theory moves to in-progress rather than repaired.
- `metadata/note_metadata.json` — note `465` remains historical-preserved with current-revision review.
- `tools/lint_archive.py` — receipt material-field and source-health normalization guards.

## Generated routes to inspect after build

- `generated/EVIDENCE_RECEIPTS.md` — must show aggregate feedback/outcome receipts as blockers, not closures.
- `generated/SOURCE_HEALTH.md` — must show normalized health-status and volatility counts.
- `generated/GAP_LEDGER.md` — must keep field validation, route/taxonomy, source preservation, stewardship, and material-outcome gaps live or in progress.
- `generated/MANIFEST.json` — must preserve note `465` and include note `986`.

## Guardrail

Field signals and household aggregates are evidence, not closure. Source-health normalization is an audit, not a destructive taxonomy rewrite. Historical preservation is not deletion authorization.


## Previous archive structure

## Archive structure

Current revision: `rev0787`  
Current codename: `closuregate-fieldfloor-routedemotion-noreceiptclosure`

## Current revision route

- `archive/985-cloudtainer-closure-gates-for-affected-person-proof-evidence-receipt-floors-route-demotion-pilot-and-no-closure-by-receipt-row.md` — evidence-receipt closure gates, proof floors, and no closure by receipt row.
- `metadata/evidence_receipts.json` — canonical receipt spine with proof floors, denominator gaps, closure blockers, and `can_close_gap`.
- `generated/EVIDENCE_RECEIPTS.md` — human surface showing proof-floor counts and closure-blocker maps.
- `metadata/note_metadata.json` — `historical_preserved` status and note `465` demotion review.
- `tools/lint_archive.py` — closure and route-demotion guards.

## Generated routes to inspect after build

- `generated/EVIDENCE_RECEIPTS.md` — must show `GAP-029` and `GAP-031` blocked by below-field receipts.
- `generated/NOTE_STATUS.json` — must show one `historical_preserved` note.
- `generated/GAP_LEDGER.md` — must keep all five live gaps open or in progress.
- `generated/MANIFEST.json` — must preserve note `465` and include note `985`.

## Guardrail

No evidence receipt in this revision can close a gap. No historical-preserved status authorizes deletion. The revision proves closure resistance and route demotion, not field validation or full retirement governance.


## Previous archive structure

## Archive structure

Current revision: `rev0786`  
Current codename: `personproof-receiptpilot-buildregistry-noclosuresurface`

## Current revision route

- `archive/984-cloudtainer-affected-person-evidence-pilot-ui-housing-receipt-tests-source-receipt-spine-build-registry-refactor-and-no-proof-by-official-surface.md` — affected-person evidence pilot and **no proof by official surface**.
- `metadata/evidence_receipts.json` — source-receipt pilot; records proof status and remaining affected-person gap without storing personal data.
- `generated/EVIDENCE_RECEIPTS.md` — reader surface for the receipt pilot.
- `metadata/unemployment_insurance_tests.json` and generated `UNEMPLOYMENT_INSURANCE_TESTS.md` — claimant-burden and remedy-completion additions.
- `metadata/housing_continuity_tests.json` and generated `HOUSING_CONTINUITY_TESTS.md` — household-outcome and durable-stability additions.
- `tools/build_steps.py` — full build-step registry used by `tools/build_all.py`.
- `metadata/gap_ledger.json` — affected-person and source-receipt gaps remain live as in-progress.

## Generated routes to inspect after build

- `generated/EVIDENCE_RECEIPTS.md` — must not claim field validation.
- `generated/UNEMPLOYMENT_INSURANCE_TESTS.md` — must include `UI-11` and `UI-12`.
- `generated/HOUSING_CONTINUITY_TESTS.md` — must include `HC-11` and `HC-12`.
- `generated/GAP_LEDGER.md` — must still show live gaps, including the two now in-progress pilots.
- `generated/MANIFEST.json` — must include the new metadata, schema, generated surfaces, and tool scripts.

## Guardrail

This revision is a pilot, not completion. An OMB burden rule, a DOL claim-status page, an eviction filing dataset, a right-to-counsel report, or a tenant-screening page can justify a test; none proves that a claimant was paid, a household remained housed, or a remedy was completed.


## Previous archive structure

## Archive structure

Current revision: `rev0785`  
Current codename: `missionkernel-reproschema-noroutegravity`

## Current revision route

- `MISSION.md` — compact human front door, proof ladder, doctrine families, and current red flags.
- `archive/983-cloudtainer-mission-kernel-reproducible-build-schema-completeness-route-gravity-affected-person-proof-and-no-governance-by-self-consistent-cube.md` — mission-kernel deep-read and no governance by self-consistent cube.
- `tools/schema_validation.py` — validates every canonical JSON file under `metadata/` and `sources/` against its declared schema.
- `tools/check_reproducible_build.py` — rebuilds and compares all generated hashes.
- `metadata/gap_ledger.json` — contains live gaps; lint forbids an all-repaired ledger.

## Generated routes to inspect after build

- `generated/GAP_LEDGER.md` — must show five live rev0785 gaps.
- `generated/SOURCE_HEALTH.md` — must include the six mission-audit comparison sources without treating them as outcome proof.
- `generated/GENERATED_SURFACE_AUDIT.md` — must remain warning-free.
- `generated/MANIFEST.json` — must remain byte-stable across the reproducibility check.

## Guardrail

A green lint result is necessary but not sufficient. The revision must not describe schema coverage, source-health row coverage, route completeness, or generated agreement as proof of public outcomes, completed remedies, or a complete theory of power.


## Previous archive structure

## Archive structure

Current revision: `rev0784`  
Current codename: `decisionpacketmerge720-nooutcomeletter`

## Current revision route

- `archive/982-cloudtainer-decision-packet-merge-review-for-note-720-interoperable-europe-assessment-forms-and-no-decision-packet-by-assessment-record.md` — decision-packet merge review and **no decision packet by assessment record**.
- `metadata/route_merge_packets.json` — `MP-004-720-to-857-858` keeps note `720` active until a real decision-packet successor or schema extension exists.
- `tools/build_retirement_candidates.py` and `tools/lint_archive.py` — merge-review packet pointers are now generated and validated.

## Generated routes to inspect after build

- `generated/RETIREMENT_CANDIDATES.md` — must list `MP-004-720-to-857-858`, show review packet `982`, and remove note `720` from the raw priority queue.
- `generated/SOURCE_HEALTH.md` — source posture remains stable.
- `generated/GENERATED_SURFACE_AUDIT.md` — must remain warning-free.

## Guardrail

The current revision must not imply that note `720` is deletion-ready. Note `858` is a procedural digital-waist case packet and note `857` is a claim-ledger route; neither preserves the full decision-packet grammar until a future absorption patch explicitly carries determination classes, reason-giving, effect dates, implementation duties, review clocks, and correction/supersession lineage.


## Previous archive structure

## Archive structure

Current revision: `rev0783`  
Current codename: `mycityservicehome-localdigitalparity-noportalservice`

## Current revision route

- `archive/981-applied-local-digital-service-home-case-packet-for-nyc-mycity-common-services-childcare-business-benefits-and-no-service-home-by-portal.md` — local digital service-home application and **no service home by portal**.
- `metadata/service_home_tests.json` — note `981` is now service-home test parity for an applied local digital case.
- `metadata/route_redirect_ledger.json` — note `981` is a reader-visible applied example for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — local digital parity is partially repaired without changing note `615` to deletion-ready.
- `sources/source_keys.json`, `sources/source_catalog.json`, and `metadata/source_health.json` — bounded NYC MyCity source routes.

## Generated routes to inspect after build

- `generated/SERVICE_HOME_TESTS.md` — includes note `981` as a service-home applied case example.
- `generated/ROUTE_REDIRECT_LEDGER.md` — surfaces note `981` as an applied example and reader-visible local digital route.
- `generated/RETIREMENT_CANDIDATES.md` — must still report no deletion-ready candidate for note `615`.
- `generated/SOURCE_HEALTH.md` — must include new MyCity source-health rows.
- `generated/GENERATED_SURFACE_AUDIT.md` — must remain warning-free.

## Guardrail

The current revision must not imply that note `615` is deletion-ready. Note `981` reduces local digital thinness; it does not prove completed one-stop service, agency accountability, fallback sufficiency, business/benefit/childcare outcome, or person-level continuity.


## Previous archive structure

## Archive structure

Current revision: `rev0782`  
Current codename: `oneloginservicehome-digitaladminparity-noservicebyaccount`

## Current revision route

- `archive/980-applied-digital-administrative-service-home-case-packet-for-govuk-one-login-hmrc-dwp-relying-services-and-no-service-home-by-shared-account.md` — digital-administrative service-home application and **no service home by shared account**.
- `metadata/service_home_tests.json` — note `980` is now service-home test parity for an applied digital-administrative case.
- `metadata/route_redirect_ledger.json` — note `980` is a reader-visible applied example for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — digital-administrative parity is partially repaired without changing note `615` to deletion-ready.
- `sources/source_keys.json`, `sources/source_catalog.json`, and `metadata/source_health.json` — bounded GOV.UK One Login source routes.

## Generated routes to inspect after build

- `generated/SERVICE_HOME_TESTS.md` — includes note `980` as a service-home applied case example.
- `generated/ROUTE_REDIRECT_LEDGER.md` — surfaces note `980` as an applied example and reader-visible digital-administrative route.
- `generated/RETIREMENT_CANDIDATES.md` — must still report no deletion-ready candidate for note `615`.
- `generated/SOURCE_HEALTH.md` — must include new One Login source-health rows.
- `generated/GENERATED_SURFACE_AUDIT.md` — must remain warning-free.

## Guardrail

The current revision must not imply that note `615` is deletion-ready. Note `980` reduces administrative/digital thinness; it does not prove non-identity administrative service homes, local digital shared-service families, fallback sufficiency, delegated access, or person-level continuity.


## Previous archive structure

## Radical Governance Archive Structure

Current revision: `rev0781`  
Timestamp: `2026-06-18 03:07 EDT` / `2026-06-18 07:07 UTC`  
Codename: `ng911servicehome-emergencyparity-noplatformrescue`

## Current revision files

- `archive/979-applied-emergency-service-home-case-packet-for-ng911-psap-esinet-gis-cad-outage-handoff-and-no-rescue-by-platform-waist.md` — emergency-communications service-home application and **no rescue by platform waist**.
- `metadata/service_home_tests.json` — note `979` is now service-home test parity for an applied emergency-communications case.
- `metadata/route_redirect_ledger.json` — note `979` is a reader-visible applied example for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — cross-sector emergency-service residue is partially repaired while note `615` remains active.
- `sources/source_keys.json`, `sources/source_catalog.json`, and `metadata/source_health.json` — bounded California NG911 project/reporting source routes.
- `archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md`, `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md`, `archive/977-cloudtainer-final-preservation-review-for-service-home-route-615-route-residue-ledger-and-no-retirement-by-complete-redirect-path.md`, and `archive/978-applied-service-home-case-packet-for-lahsa-homelessness-services-jpa-provider-chain-transition-and-no-service-home-by-grant-waist.md` — reader-facing status patches.

## Current generated surfaces

- `generated/SERVICE_HOME_TESTS.md` — includes note `979` as a service-home applied case example.
- `generated/ROUTE_REDIRECT_LEDGER.md` — surfaces note `979` as an applied example and reader-visible emergency route.
- `generated/RETIREMENT_CANDIDATES.md` — continues to block deletion while showing improved cross-sector applied coverage.


## Previous structure

## Radical Governance Archive Structure

Current revision: `rev0780`  
Timestamp: `2026-06-18 02:32 EDT` / `2026-06-18 06:32 UTC`  
Codename: `lahsaservicehome-crosssectorparity-nograntwaist`

## Current revision files

- `archive/978-applied-service-home-case-packet-for-lahsa-homelessness-services-jpa-provider-chain-transition-and-no-service-home-by-grant-waist.md` — social-service service-home application and **no service home by grant waist**.
- `metadata/service_home_tests.json` — note `978` is now service-home test parity for an applied social-service case.
- `metadata/route_redirect_ledger.json` — note `978` is a reader-visible applied example for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — cross-sector social-service residue is partially repaired while note `615` remains active.
- `archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md`, `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md`, and `archive/977-cloudtainer-final-preservation-review-for-service-home-route-615-route-residue-ledger-and-no-retirement-by-complete-redirect-path.md` — reader-facing status patches.

## Current generated surfaces

- `generated/SERVICE_HOME_TESTS.md` — includes note `978` as a service-home applied case example.
- `generated/ROUTE_REDIRECT_LEDGER.md` — surfaces note `978` as an applied example and reader-visible route.
- `generated/RETIREMENT_CANDIDATES.md` — continues to block deletion while showing improved cross-sector applied coverage.


## Previous structure

## Radical Governance Archive Structure

Current revision: `rev0779`  
Timestamp: `2026-06-18 01:48 EDT` / `2026-06-18 05:48 UTC`  
Codename: `preservationreview615-routestatusguard-noretirebycompletepath`

## Current revision files

- `archive/977-cloudtainer-final-preservation-review-for-service-home-route-615-route-residue-ledger-and-no-retirement-by-complete-redirect-path.md` — final preservation review for note `615` and **no route retirement by complete redirect path**.
- `archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md` — old service-home route now points to the final preservation review while remaining active.
- `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md` — successor route now records the final-review result and remaining route residue.
- `archive/976-cloudtainer-reader-visible-service-home-redirects-retirement-surface-parity-and-no-route-retirement-by-hidden-metadata.md` — reader redirect patch now notes that final review was completed without deletion authorization.
- `metadata/route_merge_packets.json` — final preservation-review fields, retirement blockers, and keep-active status.
- `metadata/route_redirect_ledger.json` — final review note linked as a reader-visible redirect surface.
- `tools/build_route_redirect_ledger.py`, `tools/build_retirement_candidates.py`, and `tools/lint_archive.py` — generated/audit/lint support for final-review status.

## Current generated surfaces

- `generated/ROUTE_REDIRECT_LEDGER.md` — protected-element redirect ledger with final preservation-review status.
- `generated/RETIREMENT_CANDIDATES.md` — merge-reviewed candidate audit with final preservation-review and blocker counts.
- `generated/SERVICE_HOME_TESTS.md` — executable service-home tests that remain necessary but not sufficient for retirement.


## Previous structure

## Radical Governance Archive Structure

Current revision: `rev0778`  
Timestamp: `2026-06-18 01:15 EDT` / `2026-06-18 05:15 UTC`  
Codename: `readerredirect-visibleledger-noretirebymetadata`

## Current revision files

- `archive/976-cloudtainer-reader-visible-service-home-redirects-retirement-surface-parity-and-no-route-retirement-by-hidden-metadata.md` — reader-visible service-home redirect patch and **no route retirement by hidden metadata**.
- `archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md` — old route now carries reader redirect status while remaining active.
- `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md` — successor route now names the redirect ledger and keeps deletion blocked.
- `metadata/route_redirect_ledger.json` — reader-visible redirect surfaces for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — reader redirect status for the note-`615` merge packet.
- `tools/build_route_redirect_ledger.py`, `tools/build_retirement_candidates.py`, and `tools/lint_archive.py` — generated/audit/lint support for reader-route parity.

## Current generated surfaces

- `generated/ROUTE_REDIRECT_LEDGER.md` — protected-element redirect ledger with reader-visible route surfaces.
- `generated/RETIREMENT_CANDIDATES.md` — merge-reviewed candidate audit with reader redirect status.
- `generated/SERVICE_HOME_TESTS.md` — executable service-home tests used by the redirect.


## Previous structure

## Archive structure

Current revision: `rev0777`  
Timestamp: `2026-06-18 00:44 EDT` / `2026-06-18 04:44 UTC`  
Codename: `redirectledger615-servicehomeparity-noretirebytarget`

## Current packet

- `archive/975-cloudtainer-service-home-redirect-ledger-source-test-parity-and-no-route-retirement-by-successor-target.md` — service-home protected-element redirect ledger and **no route retirement by successor target**.
- `metadata/route_redirect_ledger.json` and generated `ROUTE_REDIRECT_LEDGER.*` — machine-readable and reader-visible redirect parity for `MP-003-615-to-974`.
- `metadata/route_merge_packets.json` — `MP-003-615-to-849` now records redirect-ledger progress while keeping note `615` active.
- `tools/build_route_redirect_ledger.py` — builds the generated redirect ledger.
- `tools/lint_archive.py` — validates redirect ledger rows, source keys, test IDs, examples, and merge-packet references.
- `tools/build_retirement_candidates.py` — includes redirect-ledger counts in the retirement audit.

## Refactor guard

A successor route cannot retire an older route by existing. Redirect-ledger rows must map protected elements into successor sections, tests, source keys, and applied examples; deletion remains blocked until reader-visible redirects and final preservation review exist.

## Previous structure

## Archive structure

Current revision: `rev0776`  
Timestamp: `2026-06-18 00:13 EDT` / `2026-06-18 04:13 UTC`  
Codename: `servicehomesuccessor-mergeguard-sourceparity`

## Current packet

- `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md` — successor service-home route and **no service government by case example**.
- `metadata/route_merge_packets.json` — `MP-003-615-to-849` now has a real successor route target, source-parity keys, and a still-not-deletion-ready posture.
- `metadata/service_home_tests.json` and generated `SERVICE_HOME_TESTS.*` — note `974` is now inside service-home test parity.
- `tools/lint_archive.py` — successor-route and source-parity validation for merge packets.
- `tools/build_retirement_candidates.py` — successor routes are visible in the retirement audit.

## Refactor guard

A merge packet cannot claim successor-route progress unless the successor note exists, is listed as a target, has a valid note number, and carries source-parity keys that exist in the source-key registry. Test parity is not deletion authorization; note `615` remains active until a redirect ledger maps protected elements into note `974` and generated service-home surfaces.

## Previous structure

## Archive structure

Current revision: `rev0775`  
Timestamp: `2026-06-17 23:43 EDT` / `2026-06-18 03:43 UTC`  
Codename: `capturequeueclosed-servicehometests-reliancelimits`

## Current packet

- `archive/973-cloudtainer-capture-queue-closure-service-home-test-parity-and-no-reliance-by-clean-source-count.md` — capture queue closure, limited-reliance source tier, service-home test parity, and **no reliance by clean-source count**.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — no capture-required rows remain, but limited-reliance rows remain visible.
- `tools/build_source_health.py` — separates direct review, clean direct review, limited-reliance direct review, and capture-required follow-up.
- `metadata/service_home_tests.json` and generated `SERVICE_HOME_TESTS.*` — test scaffold for service-home route absorption.
- `metadata/route_merge_packets.json` — records `MP-003-615-to-849` test parity progress while keeping note `615` active.

## Refactor guard

Capture closure cannot be treated as reliance closure. Limited-reliance rows are excluded from clean direct-review counts, and service-home route retirement remains blocked until source/test/redirect parity exists.

## Previous structure

Current revision: `rev0774`  
Timestamp: `2026-06-17 22:37 EDT` / `2026-06-18 02:37 UTC`  
Codename: `followupcapturetrim-reviewclocksplit-nocleanbyclock`

## Current packet

- `archive/972-cloudtainer-followup-capture-trim-source-health-clock-split-and-no-clean-source-by-review-clock.md` — follow-up capture trim, review-clock/capture-risk split, and **no clean source by review clock**.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — capture-required rows are now limited to explicit capture failures, not ordinary review clocks.
- `tools/build_source_health.py` — separates clean direct review from capture-required warnings with stricter signal terms.
- `metadata/route_merge_packets.json` — records further `MP-003-615-to-849` absorption progress without making note `615` deletion-ready.

## Refactor guard

A source can have a review clock without being capture-defective. Capture-required warnings now require explicit blocked, page-level, search-only, PDF/search, or `direct_refresh_attempted_needs_followup_capture` signals.

## Previous structure

Current revision: `rev0773`  
Timestamp: `2026-06-17 22:10 EDT` / `2026-06-18 02:10 UTC`  
Codename: `catalogqueueclosed-followupcapture-absorptionpatch`

## Current packet

- `archive/971-cloudtainer-catalog-queue-closure-followup-capture-service-home-absorption-patch-and-no-reliance-by-direct-review-percent.md` — catalog-triage queue closure, follow-up capture lane, service-home partial absorption patch, and **no reliance by direct-review percent**.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — direct-review posture is now separated from clean direct-review and follow-up capture.
- `metadata/route_merge_packets.json` — `MP-003-615-to-849` has a recorded partial absorption patch but note `615` remains active pending source/test parity.
- `tools/build_source_health.py` — emits clean direct-review and follow-up capture counts.
- `tools/lint_archive.py` — validates optional partial absorption patch fields when a merge packet claims absorption progress.
- `tools/build_retirement_candidates.py` — exposes partial absorption patch counts in the generated retirement audit.

## Refactor guard

The archive can no longer claim source reliability from direct-review coverage alone, and a route-merge packet cannot claim partial absorption unless the patch file, note number, and absorption progress are valid.

## Previous structure


Current revision: `rev0772`  
Timestamp: `2026-06-17 21:36 EDT` / `2026-06-18 01:36 UTC`  
Codename: `directrefresh-mergepacket3-absorptionguard`

## Current packet

- `archive/970-cloudtainer-direct-refresh-tranche-absorption-guard-and-no-route-absorption-by-preservation-gesture.md` — direct-refresh tranche, third merge packet, absorption-requirements guard, and **no route absorption by preservation gesture**.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — another high-risk catalog-triaged tranche moved into direct-review or explicit follow-up-capture posture.
- `metadata/route_merge_packets.json` — third preservation-first merge packet, `MP-003-615-to-849`, plus absorption requirements for all packets.
- `tools/lint_archive.py` — validates route-merge packet source/target integrity and absorption-requirements presence.
- `tools/build_retirement_candidates.py` — exposes absorption-requirement counts in the generated retirement audit.

## Refactor guard

Route merge packets now have to say what a real absorption patch must preserve. The archive can still keep a note when deletion is unsafe, but it can no longer pass off a preservation gesture as an absorption plan.

## Previous structure

## Prior structure snapshot

Current revision: `rev0771`  
Timestamp: `2026-06-17 20:58 EDT` / `2026-06-18 00:58 UTC`  
Codename: `directrefresh-mergepacket2-nopercentcompletion`

## Current packet

- `archive/969-cloudtainer-direct-refresh-tranche-second-merge-packet-and-no-completion-by-refresh-percentage.md` — direct-refresh tranche, second route merge packet, and **no completion by refresh percentage**.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — another high-risk catalog-triaged tranche moved into direct-review posture while blocked/official-search cases stay explicit.
- `metadata/route_merge_packets.json` — second preservation-first merge packet, `MP-002-811-to-857`, protecting note 811 from deletion-by-overcompression.
- `tools/build_retirement_candidates.py` — removes merge-reviewed notes from raw review-only pressure as well as priority pressure.
- `tools/lint_archive.py` — validates route-merge packet source/target integrity.

## Refactor guard

The source-health ledger now distinguishes direct review, official-search/blocked attempts, and catalog-only posture. Route merge packets are linted against archive files and metadata note numbers so a preservation packet cannot silently point at a missing or mismatched note.

## Previous structure

Current revision: `rev0769`  
Timestamp: `2026-06-17 19:52 EDT` / `2026-06-17 23:52 UTC`  
Codename: `sourcehealthclosure-retirementqueue-directrefresh`

## Current packet

- `archive/967-cloudtainer-source-health-closure-catalog-triage-retirement-queue-and-no-completion-by-catalog-posture.md` — source-health closure and retirement-queue audit under **no completion by catalog posture**.
- `tools/build_source_health.py` — separates direct review from catalog triage and emits a direct-refresh priority queue.
- `tools/build_retirement_candidates.py` — emits a bounded zero-dependency merge-packet priority queue without making any note deletion-ready.
- `metadata/source_health.json` and generated `SOURCE_HEALTH.*` — every source key now has a manual posture; catalog-triaged rows remain visible for future direct refresh.
- `metadata/gap_ledger.json` and generated `GAP_LEDGER.*` — `GAP-027` repaired for generated-surface and unclassified source-health scope.

## Refactor guard

The source-health generated surface now distinguishes manual posture coverage from direct-review coverage. The retirement audit now gives maintainers a small action queue for merge packets while keeping automatic deletion at zero.

## Previous structure

## Radical Governance Archive Structure

Current revision: `rev0768`  
Timestamp: `2026-06-17 19:25 EDT` / `2026-06-17 23:25 UTC`  
Codename: `testsurfacebudget-healthtranche3-warningfree`

## Current packet

- `archive/966-cloudtainer-test-surface-budget-priority-source-health-third-tranche-and-no-substance-by-matrix-sprawl.md` — role-aware generated-surface audit and source-health third tranche under **no substance by matrix sprawl**.
- `tools/build_generated_surface_audit.py` — classifies generated files as reader route, machine route, machine support, or leaf test-matrix render.
- `metadata/source_health.json` — fifty high-priority unchecked source keys added with volatility, class, cadence, and source-boundary notes.
- `metadata/gap_ledger.json` and generated gap ledger — `GAP-027` further partially repaired and still open for staged source-health backfill.

## Refactor guard

The generated-surface audit now reports raw file count, reader-route budget count, leaf test-matrix render count, role bytes, and package warnings separately. This prevents test-matrix coverage from being misread as front-door sprawl while preserving the raw package facts.

## Previous structure

Current revision: `rev0767`  
Timestamp: `2026-06-17 18:54 EDT` / `2026-06-17 22:54 UTC`  
Codename: `sourceindexcompact-healthtranche-warningclosed`

## Current packet

- `archive/965-cloudtainer-source-index-compaction-priority-source-health-second-tranche-and-no-completion-by-unresolved-warning.md` — source-index compaction and source-health second tranche under **no completion by unresolved warning**.
- `tools/build_sources_index.py` — compact generated source JSON route with current notes, registry snapshot, counts, and hashes; full history remains in `sources/source_catalog.json`.
- `tools/lint_archive.py` — compact budget, scope, count, hash, and current-note guard for `generated/SOURCES.json`.
- `metadata/source_health.json` — twenty-three high-priority source-health rows added from the unchecked queue.
- `metadata/gap_ledger.json` and generated gap ledger — `GAP-027` further partially repaired and still open for package-count and remaining source-health work.

## Refactor guard

`tools/lint_archive.py` now fails if `generated/SOURCES.json` regresses into a full historical source duplicate. `generated/SOURCES.json` is a current-revision route and registry snapshot; `sources/source_catalog.json` remains the complete editable historical source map.

## Previous structure

Current revision: `rev0766`  
Timestamp: `2026-06-17 18:24 EDT` / `2026-06-17 22:24 UTC`  
Codename: `risktriage-threadsourcecompact-sourcehealthbackfill`

## Current packet

- `archive/964-cloudtainer-risk-triage-thread-route-compaction-source-health-backfill-and-no-forward-motion-by-new-docket.md` — risk-triage maintenance packet under **no forward motion by new docket**.
- `metadata/source_health.json` — twelve high-priority source-health rows added from the unchecked queue.
- `tools/build_threads.py` — compact thread reader route; full detail remains in machine surfaces.
- `tools/build_source_health.py` — compact source-health summary JSON writer.
- `tools/build_note_index.py`, `tools/build_control_surfaces.py`, `tools/build_lifecycle_gates.py` — compact machine/debug JSON writers.
- `tools/lint_archive.py` — compact-reader budget guard for refactored generated surfaces.
- `metadata/gap_ledger.json` and generated gap ledger — `GAP-027` further partially repaired.

## Refactor guard

`tools/lint_archive.py` now fails if the refactored generated reader/machine surfaces regress past their compact budgets. `generated/THREADS.md` no longer republishes every tag-to-note edge; `generated/SOURCE_HEALTH.json` no longer duplicates full source titles, URLs, manual notes, and dependent membership that already live in canonical source/metadata files.

## Previous structure

Current revision: `rev0765`  
Timestamp: `2026-06-17 17:57 EDT` / `2026-06-17 21:57 UTC`  
Codename: `missiondeepread-stalefrontdoor-sourcecompact`

## Current packet

- `archive/963-cloudtainer-mission-deep-read-stale-front-door-generated-source-surface-source-health-backlog-and-no-mission-by-route-mass.md` — mission deep-read and maintenance audit under **no mission by route mass**.
- `ARCHIVE_STRUCTURE.md` — restored as a current front door rather than a stale `rev0763` route.
- `tools/lint_archive.py` — current-revision and current-note guard for this front door.
- `tools/build_sources_index.py` — compact generated source Markdown reader; full history remains in `sources/source_catalog.json`; `generated/SOURCES.json` is now a compact current-route and registry snapshot.
- `metadata/gap_ledger.json` and generated gap ledger — `GAP-027` further partially repaired; remaining work stays explicit.

## Refactor guard

`tools/lint_archive.py` now fails if `ARCHIVE_STRUCTURE.md` omits the current revision or any current archive note. `generated/SOURCES.md` now exposes the current revision's source route without republishing the complete historical source catalog as Markdown.

## Previous structure

Current revision: `rev0763`  
Timestamp: `2026-06-13 13:19 EDT` / `2026-06-13 17:19 UTC`  
Codename: `cloudtainerlineage-schemafailguard`

## Current packet

- `archive/960-cloudtainer-release-lineage-schema-gap-generated-surface-and-maintenance-revision-audit-no-maintenance-by-green-lint.md` — cloudtainer maintenance audit under **no maintenance by green lint**.
- `meta-0464-cloudtainer-release-lineage-schema-gap-and-maintenance-revision-guard-note.md` — maintenance/audit note.
- `tools/lint_archive.py` — release-lineage completeness guard, gap-ledger affected-party guard, and maintenance-safe current matrix scoping.
- `metadata/gap_ledger.json` and generated `GAP_LEDGER.*` — repaired schema completeness and maintenance queue entries.

## Refactor guard

`tools/lint_archive.py` now fails if archive-index revisions are missing from the release ledger, if release rows list the wrong archive files, or if gap-ledger rows omit affected parties. Current operational-matrix coverage now applies only to current substantive notes.

## Previous structure

Rev0762 added consumer-finance continuity and the newest operational service-continuity packet.

## Current source additions

- `archive/954...` and `archive/955...` define the immigration/asylum/status continuity docket and applied case packet.
- `metadata/immigration_status_tests.json` and `schema/immigration_status_tests.schema.json` define the newest operational test matrix.
- `generated/IMMIGRATION_STATUS_TESTS.*` renders the matrix through the common registry builder.
- `tools/lint_archive.py` includes a current claim/case source-key parity guard.

## Previous structure

## Current revision (rev0759)

- `archive/952-veterans-benefits-health-care-claims-appeals-community-care-housing-education-and-caregiver-continuity-dockets-no-veteran-support-by-claim-row.md` — veterans benefits / care / support continuity docket under **no veteran support by claim row**.
- `archive/953-applied-veterans-continuity-case-packet-for-va-claims-pact-act-health-care-community-care-appeals-ehrm-hud-vash-gi-bill-caregivers-and-no-veteran-support-by-claim-row.md` — applied VA/VBA/VHA/Board/GAO/HUD/GI Bill/caregiver veterans-continuity source packet.
- `metadata/veterans_continuity_tests.json`, `schema/veterans_continuity_tests.schema.json`, and `generated/VETERANS_CONTINUITY_TESTS.*` — operational tests for veterans support continuity.
- `tools/lint_archive.py` — common test-matrix schema registry guard for `$id` and metadata `schema` const drift.

## Previous structure


## Current revision (rev0758)

- `archive/950-broadband-telecommunications-connectivity-digital-access-lifeline-acp-bead-outage-and-portal-continuity-dockets-no-access-by-coverage-polygon.md` — broadband/connectivity continuity docket under **no access by coverage polygon**.
- `archive/951-applied-broadband-connectivity-continuity-case-packet-for-fcc-national-broadband-map-bdc-lifeline-acp-bead-nors-labels-and-no-access-by-coverage-polygon.md` — applied FCC/USAC/NTIA broadband-connectivity source packet.
- `metadata/broadband_connectivity_tests.json`, `schema/broadband_connectivity_tests.schema.json`, and `generated/BROADBAND_CONNECTIVITY_TESTS.*` — operational tests for connectivity continuity.
- `tools/lint_archive.py` — source-catalog value guard for current revision source rows.

## Archive structure — rev0757

## Current revision overlay

- `archive/948-...` and `archive/949-...` add the transportation/mobility continuity docket and applied case packet.
- `metadata/transportation_mobility_tests.json` and `schema/transportation_mobility_tests.schema.json` define the newest operational test matrix.
- `generated/TRANSPORTATION_MOBILITY_TESTS.*` renders the matrix through the common registry builder.
- `tools/lint_archive.py` includes a current-matrix case-example guard for fresh packets.

## Previous structure

## Archive structure

This archive separates authored sources from generated routing surfaces.

## Source layer

- `archive/` — numbered Radical-Governance notes.
- `README.md`, `CHANGELOG.md`, and `INDEX.md` — hand-maintained release and navigation surfaces.
- `sources/source_catalog.json` — canonical note-to-source catalog.
- `sources/source_keys.json` — canonical source-key registry used by note metadata and applied-case packets.
- `metadata/note_metadata.json` — canonical note metadata spine: note class, status, canon role, explicit tags, dependencies, dispatchers, source keys, and reserved notes.
- `metadata/case_packets.json` — canonical applied-case matrix input for cross-boundary form tests.
- `metadata/claims.json` — canonical claim ledger input for claim status, evidence lanes, currentness labels, opposition, falsifiers, affected parties, capture channels, and review clocks.
- `metadata/defeat_tests.json` — canonical defeat-test matrix input for no-trigger, lower-form-sufficiency, handback, sunset, waist-capture, soft-law-hardening, database-alert-rights, plural-order-flattening, supplier-dependency exit-proof, municipal-distress handback, and claim-falsifier tests.
- `metadata/handback_tests.json` — canonical handback review matrix input for fiscal distress, receivership, emergency-manager, waiver, devolution, final-release, and sunset cases.
- `metadata/supplier_dependency_tests.json` — canonical supplier-dependency review matrix input for cloud, SaaS, AI, identity, analytics, support, benefit-claim, redress, opposition, and exit-proof tests.
- `metadata/symbolic_authority_tests.json` — canonical symbolic-authority review matrix input for visible bodies, JPAs, boards, secretariats, hubs, commissions, departments, and partnerships whose public mission may outrun their operative levers.
- `metadata/capacity_tests.json` — canonical capacity-floor review matrix input for fragile-jurisdiction, emergency-support, donor-dependent, peace-support, stabilization, and technical-assistance arrangements.
- `metadata/model_decision_tests.json` — canonical model-mediated decision review matrix input for automated decisions, evidence proxies, rule engines, risk scores, and legal-effect workflows.
- `metadata/generative_assistant_tests.json` — canonical generative-assistant review matrix input for public chatbots, RAG guidance assistants, service bots, source grounding, reliance boundaries, correction clocks, incident thresholds, and withdrawal / transition receipts.
- `metadata/staff_copilot_tests.json` — canonical staff-copilot review matrix input for internal AI copilots, correspondence drafters, case-intake parsers, vulnerability scanners, report drafters, queue effects, release gates, and shadow-action controls.
- `metadata/transition_receipt_tests.json` — canonical transition-receipt review matrix input for rollback, withdrawal, conversion, absorption, migration, waiver, reprocurement, sunset, relaunch, public-AI closure, emergency-platform conversion, affected-user tails, record / data closeout, contract closeout, residual dependency, and successor gates.
- `metadata/platform_migration_tests.json` — canonical platform-migration review matrix input for public platform replacement, SaaS migration, portal migration, account migration, payroll / HR transition, digital status proof, data-hub migration, parallel runs, cutover / rollback gates, legacy fallback, supplier exit, and post-migration value audits.
- `metadata/ecological_personhood_tests.json` — canonical ecological-personhood review matrix input for rights-of-nature, legal-person ecosystems, guardian commissions, Tutoría bodies, community authority, scientific indicators, remedy budgets, standing routes, liability boundaries, ordinary-regime non-displacement, and failure routes.
- `metadata/entitlement_continuity_tests.json` — canonical entitlement-continuity review matrix input for renewals, redeterminations, managed migrations, ex parte proof, migration notices, procedural closures, transitional protection, payment / coverage continuity, appeal / reinstatement tails, assisted routes, and churn learning loops.
- `metadata/payment_redress_tests.json` — canonical payment-redress review matrix input for compensation, redress, refunds, refundable credits, support-scheme transitions, interim / final payments, fixed-sum offers, evidence burden, fraud controls, review clocks, and payment-state publication.
- `metadata/credential_access_tests.json` — canonical credential-access review matrix input for login, identity proofing, federation, delegated authority, account recovery, biometric / non-biometric routes, relying-party boundaries, standards-currentness, outages, and public-service access gates.
- `metadata/representative_access_tests.json` — canonical representative-access review matrix input for payees, appointees, guardians, tax professionals, appeal representatives, helpers, caregivers, delegated users, notices, payment control, revocation, scope, and proxy-action boundaries.
- `metadata/disaster_assistance_tests.json` — canonical disaster-assistance review matrix input for declaration scope, survivor proof, denial cure, appeals, insurance / duplication, program handoffs, accessibility, fraud-control harm, payment receipt, recovery outcomes, and fragmentation reporting.
- `metadata/unemployment_insurance_tests.json` — canonical unemployment-insurance review matrix input for claim-state split, identity proofing, payment holds, fraud false positives, employer / separation issue routing, overpayment classification, waivers, appeals, identity-theft victim remediation, state IT performance, and paired integrity / access metrics.
- `metadata/watchlist_border_tests.json` — canonical watchlist / border / law-enforcement automation review matrix input for watchlist hits, biometric candidates, border screening, nonfederal alerts, officer reliance, DHS TRIP redress, correction propagation, AI inventories, and no enforcement by match.
- `metadata/public_ai_register_tests.json`, `metadata/subnational_ai_tests.json`, `metadata/global_south_source_tests.json`, `metadata/health_benefit_tests.json`, and `metadata/climate_utility_tests.json` — registry-built common matrices for public AI register maintenance, subnational/local AI implementation, non-English / Global South official-source governance, health-benefit transition continuity, climate / utility medical-baseline continuity, and housing continuity / eviction / rental assistance. `tools/test_matrix_registry.py` is the source of truth for these recent matrix builders.
- `metadata/source_health.json` — manual health ledger for source-key currentness, volatility, supersession, review cadence, retrieval result, and fallback source keys.
- `metadata/gap_ledger.json` — small prioritized backlog of substantive and maintenance gaps, with nearest notes, source anchors, next artifacts, and why-not-now notes.
- `metadata/custody_reentry_tests.json` — custody / corrections / release / reentry continuity tests for legal custody, health, deaths, IDs, housing, and supervision tails.
- `metadata/water_sanitation_tests.json` — drinking-water, wastewater, lead, PFAS, public notice, emergency supply, cyber/OT, affordability, and sanitation continuity tests.
- `metadata/food_nutrition_tests.json` — SNAP, WIC, school-meal, Summer EBT, D-SNAP, EBT/eWIC, retailer-access, theft/replacement, disaster feeding, and food-security continuity tests.
- `metadata/emergency_response_tests.json` — 911, NG911, EMS, 988, IPAWS, WEA/EAS, outage, dispatch, location, crisis-care, and public-warning continuity tests.
- `schema/note_metadata.schema.json`, `schema/source_keys.schema.json`, `schema/case_packets.schema.json`, `schema/claims.schema.json`, `schema/defeat_tests.schema.json`, `schema/handback_tests.schema.json`, `schema/supplier_dependency_tests.schema.json`, `schema/symbolic_authority_tests.schema.json`, `schema/capacity_tests.schema.json`, `schema/model_decision_tests.schema.json`, `schema/generative_assistant_tests.schema.json`, `schema/staff_copilot_tests.schema.json`, `schema/transition_receipt_tests.schema.json`, `schema/platform_migration_tests.schema.json`, `schema/ecological_personhood_tests.schema.json`, `schema/entitlement_continuity_tests.schema.json`, `schema/payment_redress_tests.schema.json`, `schema/credential_access_tests.schema.json`, `schema/representative_access_tests.schema.json`, `schema/disaster_assistance_tests.schema.json`, `schema/unemployment_insurance_tests.schema.json`, `schema/watchlist_border_tests.schema.json`, `schema/source_health.schema.json`, and `schema/gap_ledger.schema.json` — schemas for the editable metadata and source layers.
- `tools/` and `Makefile` — rebuild and lint machinery.

## Generated layer

- `generated/SOURCES.json` and `generated/SOURCES.md` — rendered source surfaces.
- `generated/ARCHIVE_INDEX.json` — rendered note index with metadata.
- `generated/NOTE_STATUS.json` — rendered status and front-door map.
- `generated/CASE_PACKET_MATRIX.json` and `generated/CASE_PACKET_MATRIX.md` — rendered comparison matrix for applied case packets.
- `generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json` and `generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md` — rendered recurrence audit for the `812`–`824` cross-boundary chain after applied packets.
- `generated/CLAIMS.json` and `generated/CLAIMS.md` — rendered claim ledger for holdings, evidence lanes, source keys, currentness labels, opposition, falsifiers, affected parties, capture channels, and review clocks.
- `generated/DEFEAT_TESTS.json` and `generated/DEFEAT_TESTS.md` — rendered defeat-test matrix for case packets, consolidation passes, and no-authority / handback / sunset findings.
- `generated/HANDBACK_TESTS.json` and `generated/HANDBACK_TESTS.md` — rendered handback tests for fiscal-distress, receivership, waiver, devolution, and final-release cases.
- `generated/SUPPLIER_DEPENDENCY_TESTS.json` and `generated/SUPPLIER_DEPENDENCY_TESTS.md` — rendered supplier-dependency review tests for public cloud, SaaS, AI, identity, data-platform, and managed-support dependencies.
- `generated/SYMBOLIC_AUTHORITY_TESTS.json` and `generated/SYMBOLIC_AUTHORITY_TESTS.md` — rendered symbolic-authority review tests for mandate-capacity mismatch, attribution boundaries, transition receipts, and recharter choices.
- `generated/CAPACITY_TESTS.json` and `generated/CAPACITY_TESTS.md` — rendered capacity-floor tests for mandate-capacity match, donor pledge-to-deployment, access classes, civilian-harm accountability, humanitarian boundaries, justice-chain continuity, private-force clarity, emergency records, and handback ladders.
- `generated/MODEL_DECISION_TESTS.json` and `generated/MODEL_DECISION_TESTS.md` — rendered model-decision tests for legal authority, evidentiary proxies, burden of proof, notice / explanation, review, vulnerability, business-rule scrutiny, and remediation loops.
- `generated/GENERATIVE_ASSISTANT_TESTS.json` and `generated/GENERATIVE_ASSISTANT_TESTS.md` — rendered generative-assistant tests for public owner, canonical corpus, source trace, reliance warnings, hallucination / consistency, accessibility, correction clocks, incident disclosure, supplier / model change, handoff, and transition receipts.
- `generated/STAFF_COPILOT_TESTS.json` and `generated/STAFF_COPILOT_TESTS.md` — rendered staff-copilot tests for public owner, use-case register, input/source lineage, output capture, human-review quality, queue / priority effects, public-communication release gates, sensitive-data boundaries, model / supplier changes, and feedback loops.
- `generated/TRANSITION_RECEIPT_TESTS.json` and `generated/TRANSITION_RECEIPT_TESTS.md` — rendered transition-receipt tests for terminal status, successor function map, affected-user / remedy tail, record preservation, data closeout, procurement / contract closeout, incident lessons, cost / benefit separation, residual dependency, and relaunch / expansion gates.
- `generated/PLATFORM_MIGRATION_TESTS.json` and `generated/PLATFORM_MIGRATION_TESTS.md` — rendered platform-migration tests for old/new authority, data / identity / entitlement mapping, backlog and remedy tails, rule / configuration readiness, interface dependencies, parallel-run reconciliation, wave cutover / rollback, affected-user continuity, contract / supplier exit, legacy fallback, and post-migration value / harm audits.
- `generated/ECOLOGICAL_PERSONHOOD_TESTS.json` and `generated/ECOLOGICAL_PERSONHOOD_TESTS.md` — rendered ecological-personhood tests for subject and rights boundaries, guardian spines, community authority, scientific indicators, remedy budgets, enforcement / standing, liability / impracticability, ordinary-regime non-displacement, public records, and ecological-effect / failure routes.
- `generated/ENTITLEMENT_CONTINUITY_TESTS.json` and `generated/ENTITLEMENT_CONTINUITY_TESTS.md` — rendered entitlement-continuity tests for entitlement owner, renewal window, ex parte proof, notice comprehension, deadline gates, procedural-loss denominators, payment / coverage continuity, assisted routes, appeal / reinstatement, transitional protection, and churn learning loops.
- `generated/PAYMENT_REDRESS_TESTS.json` and `generated/PAYMENT_REDRESS_TESTS.md` — rendered payment-redress tests for claimant owner, legal or harm basis, calculation, payment-state ladders, interim / final / fixed-sum boundaries, lost records, review clocks, fraud controls, family / support tails, publication costs, and learning loops.
- `generated/CREDENTIAL_ACCESS_TESTS.json` and `generated/CREDENTIAL_ACCESS_TESTS.md` — rendered credential-access tests for service action consequence, assurance-level fit, proofing-route inclusion, delegated authority, relying-party owner boundary, account recovery, privacy / biometric / supplier controls, outage fallback, standards reapproval, and public metrics.
- `generated/REPRESENTATIVE_ACCESS_TESTS.json` and `generated/REPRESENTATIVE_ACCESS_TESTS.md` — rendered representative-access tests for authority type, capacity / consent, credential separation, payment-fiduciary control, notice / deadline routing, revocation / restoration, conflict / misuse, cross-system portability, appeal / health-information boundaries, and public metrics.
- `generated/DISASTER_ASSISTANCE_TESTS.json` and `generated/DISASTER_ASSISTANCE_TESTS.md` — rendered disaster-assistance tests for household proof, denial cure, appeal clocks, insurance / duplication, handoff receipts, accessibility routes, fraud-control harm, payment receipt, and recovery outcome.
- `generated/UNEMPLOYMENT_INSURANCE_TESTS.json` and `generated/UNEMPLOYMENT_INSURANCE_TESTS.md` — rendered unemployment-insurance tests for identity routes, payment holds, fraud flags, false positives, overpayment / waiver states, appeals, identity-theft repair, state IT performance, and paired integrity / access metrics.
- `generated/WATCHLIST_BORDER_TESTS.json` and `generated/WATCHLIST_BORDER_TESTS.md` — rendered watchlist / border tests for match-state decomposition, nomination and deletion evidence, screening-context boundaries, officer call-back controls, redress propagation, biometric lead limits, nonfederal user governance, disclosure lanes, AI / privacy / civil-rights evidence, and paired utility / harm metrics.
- `generated/PUBLIC_AI_REGISTER_TESTS.*`, `generated/SUBNATIONAL_AI_TESTS.*`, `generated/GLOBAL_SOUTH_SOURCE_TESTS.*`, `generated/HEALTH_BENEFIT_TESTS.*`, `generated/CLIMATE_UTILITY_TESTS.*`, `generated/HOUSING_CONTINUITY_TESTS.*`, `generated/CUSTODY_REENTRY_TESTS.*`, `generated/WATER_SANITATION_TESTS.*`, and `generated/FOOD_NUTRITION_TESTS.*` — rendered registry-built matrices for public AI register maintenance, local/subnational implementation, non-English / Global South source-language governance, health-benefit / prescription-drug transition continuity, climate / utility medical-baseline continuity, and housing continuity / eviction / rental assistance.
- `generated/SOURCE_HEALTH.json` and `generated/SOURCE_HEALTH.md` — rendered source-health dependency map across source keys, notes, claims, case packets, volatility, review cadence, risk flags, and unchecked keys.
- `generated/GAP_LEDGER.json` and `generated/GAP_LEDGER.md` — rendered prioritized gap ledger for missing domains and next artifacts.
- `generated/GENERATED_SURFACE_AUDIT.json` and `generated/GENERATED_SURFACE_AUDIT.md` — rendered generated-surface size and reader-cost audit.
- `generated/CANON_MAP.json` — rendered front-door, first-citation, dispatcher, and applied-case routing map.
- `generated/THREADS.md` and `generated/THREAD_SUMMARY.json` — tag/thread crosswalks; `THREADS.md` is intentionally compact and filename-only per tag, while richer theses remain in `ARCHIVE_INDEX.json`.
- `generated/RELEASES.json` — release lineage from `INDEX.md` and `CHANGELOG.md`.
- `generated/CONTROL_SURFACES.json`, `generated/ASSURANCE_ARTIFACTS.json`, and `generated/LIFECYCLE_GATES.json` — heuristic control crosswalks.
- `generated/MANIFEST.json` — hashed manifest of source, generated, metadata, archive, meta, and tool files.

Delete `generated/` and run `make lint` to rebuild the generated layer. Use `RG_GENERATED_AT` or `SOURCE_DATE_EPOCH` to pin generated timestamps for deterministic comparison.



## rev0751 custody/reentry additions

- `archive/936-detention-corrections-health-release-and-reentry-continuity-dockets-booking-custody-medication-deaths-ids-housing-and-no-liberty-by-custody-row.md`
- `archive/937-applied-custody-and-reentry-continuity-case-packet-for-bjs-jails-prisons-cms-reentry-1115-dcra-gao-bop-samhsa-moud-fulton-jail-and-no-liberty-by-custody-row.md`
- `metadata/custody_reentry_tests.json`
- `schema/custody_reentry_tests.schema.json`
- `generated/CUSTODY_REENTRY_TESTS.json`
- `generated/CUSTODY_REENTRY_TESTS.md`
- `meta-0452-custody-reentry-continuity-and-front-door-guard-note.md`
- `tools/lint_archive.py` current-packet front-door guard


## rev0748 housing-continuity additions

- `archive/928-housing-stability-eviction-rental-assistance-tenant-screening-and-possession-continuity-dockets-no-housing-stability-by-portal-status.md`
- `archive/929-applied-housing-continuity-case-packet-for-eviction-lab-era-closeout-cfpb-tenant-screening-nyc-right-to-counsel-illinois-cbrap-and-no-stability-by-portal-status.md`
- `metadata/housing_continuity_tests.json`
- `schema/housing_continuity_tests.schema.json`
- `generated/HOUSING_CONTINUITY_TESTS.json`
- `generated/HOUSING_CONTINUITY_TESTS.md`
- `meta-0448-housing-continuity-case-and-source-health-triage-refactor-note.md`
- `tools/build_source_health.py` source-health triage score / reason refactor



## rev0746 cloudtainer deep-read audit additions

- `archive/927-cloudtainer-deep-read-audit-schema-drift-source-health-coverage-generated-surface-budgets-housing-gap-and-no-maintenance-by-green-lint.md`
- `schema/climate_utility_tests.schema.json` `$id` corrected to the climate / utility artifact identity
- `tools/lint_archive.py` now rejects note statuses outside the declared metadata vocabulary
- `tools/build_generated_surface_audit.py` now uses tighter generated-surface budgets and package-level warnings
- `metadata/gap_ledger.json`, `sources/source_keys.json`, and `metadata/source_health.json` now seed the housing / eviction / rental-assistance / tenant-screening next candidate with current source anchors

## rev0742 subnational-AI additions

- `archive/919-subnational-digital-government-and-local-ai-implementation-procurement-benefits-schools-courts-policing-permitting-and-no-accountability-by-local-pilot.md`
- `archive/920-applied-subnational-ai-case-packet-for-nyc-algorithmic-tools-california-ads-inventory-colorado-ai-act-courts-schools-local-records-and-no-public-service-by-local-pilot.md`
- `metadata/subnational_ai_tests.json`
- `schema/subnational_ai_tests.schema.json`
- `tools/build_subnational_ai_tests.py`
- `tools/test_matrix_registry.py`
- `tools/build_test_matrices.py`
- `generated/SUBNATIONAL_AI_TESTS.json`
- `generated/SUBNATIONAL_AI_TESTS.md`



## rev0743 non-English / Global South source additions

- `archive/921-non-english-global-south-official-source-governance-language-version-drift-translation-currentness-and-no-rule-by-english-summary.md`
- `archive/922-applied-non-english-global-south-source-case-packet-for-brazil-cadunico-govbr-bolsa-familia-ai-plan-lgpd-india-aadhaar-digilocker-and-no-benefit-by-translated-summary.md`
- `metadata/global_south_source_tests.json`
- `schema/global_south_source_tests.schema.json`
- `generated/GLOBAL_SOUTH_SOURCE_TESTS.json`
- `generated/GLOBAL_SOUTH_SOURCE_TESTS.md`
- lint now uses `tools/test_matrix_registry.py` for common matrix validation.


## rev0745 climate / utility medical-baseline continuity additions

- `archive/925-utility-shutoff-medical-baseline-and-climate-continuity-dockets-arrears-outage-cooling-electricity-dependent-equipment-and-no-life-safety-by-account-code.md`
- `archive/926-applied-utility-shutoff-and-medical-baseline-case-packet-for-eia-disconnection-data-liheap-hhs-empower-connecticut-winter-protection-california-psps-and-no-safety-by-medical-certificate.md`
- `metadata/climate_utility_tests.json`
- `schema/climate_utility_tests.schema.json`
- `generated/CLIMATE_UTILITY_TESTS.json`
- `generated/CLIMATE_UTILITY_TESTS.md`
- gap-ledger cleanup: `GAP-009` repaired and stale duplicate `GAP-008` removed
- lint / build refactor: common matrix front-door, manifest, and H1 checks stay registry-driven

## rev0744 health-benefit transition additions

- `archive/923-health-benefit-and-prescription-drug-coverage-transition-dockets-payer-handoff-formulary-clocks-prior-authorization-and-no-treatment-continuity-by-enrollment-row.md`
- `archive/924-applied-health-coverage-and-prescription-transition-case-packet-for-medicaid-chip-marketplace-and-medicare-part-d-renewals-seps-formulary-exceptions-and-no-medication-continuity-by-plan-card.md`
- `metadata/health_benefit_tests.json`
- `schema/health_benefit_tests.schema.json`
- `generated/HEALTH_BENEFIT_TESTS.json`
- `generated/HEALTH_BENEFIT_TESTS.md`
- `tools/test_matrix_registry.py` and `Makefile` carry the registry/common-matrix refactor for this pass.


## rev0748 structure note

- `archive/930-cyber-incident-software-provenance-and-public-service-continuity-dockets-runtime-sbom-supplier-access-recovery-and-no-resilience-by-attestation.md` and `archive/931-applied-cyber-software-continuity-case-packet-for-change-healthcare-synnovis-british-library-omb-nist-cisa-and-no-resilience-by-attestation.md` extend the active archive with a cyber/software public-service continuity docket and applied case packet.
- `metadata/software_cyber_continuity_tests.json`, `schema/software_cyber_continuity_tests.schema.json`, and `generated/SOFTWARE_CYBER_CONTINUITY_TESTS.*` add the operational test surface.
- `tools/build_case_packet_matrix.py` now builds compact merge guidance from `metadata/gap_ledger.json` rather than carrying stale hard-coded text.

## rev0750 structure note

- `archive/932-election-administration-continuity-dockets-registration-ballot-mail-accessibility-canvass-audit-certification-and-no-suffrage-by-status-row.md` and `archive/933-applied-election-continuity-case-packet-for-eac-eavs-cisa-election-security-usps-postmarks-fvap-uocava-ada-accessibility-nyc-calendar-and-no-election-by-certified-total.md` extend the active archive with an election-administration continuity docket and applied case packet.
- `metadata/election_continuity_tests.json`, `schema/election_continuity_tests.schema.json`, and `generated/ELECTION_CONTINUITY_TESTS.*, CHILD_WELFARE_TESTS.*` add the operational test surface.
- `generated/RETIREMENT_CANDIDATES.*` is the generated review-only queue for GAP-007. It does not authorize deletion.
- `generated/CASE_PACKET_MATRIX.*` now includes chain-note recurrence counts so `generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.*` no longer sees all `812`–`824` fields as latent.

## rev0750 child-welfare continuity additions

- `archive/934-child-protection-foster-care-placement-and-family-continuity-dockets-safety-permanency-health-education-missing-from-care-and-no-child-safety-by-placement-row.md` and `archive/935-applied-child-welfare-continuity-case-packet-for-acf-afcars-ncands-family-first-gao-congregate-care-oig-missing-care-ct-dcf-and-no-safety-by-placement-row.md` add the child protection / foster care continuity packet.
- `metadata/child_welfare_tests.json`, `schema/child_welfare_tests.schema.json`, and `generated/CHILD_WELFARE_TESTS.*` add ten operational tests for safety, prevention, court authority, placement suitability, health, education, missing-from-care, voice, permanency, and public oversight denominators.
- `tools/build_retirement_candidates.py` now produces review-only merge candidates from lexical and tag overlap while preserving the rule that no note is deletion-ready from metadata alone.

- `metadata/long_term_care_tests.json` — canonical long-term services/supports, nursing-home, HCBS, APS, ombudsman, guardianship, discharge, emergency, and care-continuity matrix input.
## rev0753 special-education additions

- `archive/940-*` and `archive/941-*` add the special education / IEP / Section 504 continuity docket and applied case packet.
- `metadata/special_education_tests.json`, `schema/special_education_tests.schema.json`, and generated `SPECIAL_EDUCATION_TESTS.*` add the special-education test surface.
- `tools/build_note_status.py` now auto-routes current canon roles; `tools/lint_archive.py` checks that front-door targets exist.



## rev0756 food/nutrition additions

- `archive/944-food-and-nutrition-assistance-continuity-dockets-snap-wic-school-meals-summer-ebt-dsnap-ebt-security-retailers-and-no-food-security-by-benefit-row.md`
- `archive/945-applied-food-and-nutrition-continuity-case-packet-for-snap-timeliness-wic-modernization-school-meals-summer-ebt-dsnap-ebt-theft-retailers-and-no-food-security-by-benefit-row.md`
- `metadata/food_nutrition_tests.json`
- `schema/food_nutrition_tests.schema.json`
- `generated/FOOD_NUTRITION_TESTS.json`
- `generated/FOOD_NUTRITION_TESTS.md`
- `meta-0456-food-nutrition-continuity-and-source-crosscheck-note.md`
- `tools/lint_archive.py` current-source crosscheck guard

### Rev0793 fieldwork execution-control surface

- `metadata/fieldwork_execution_controls.json` is the editable non-closing operating-control layer after fieldwork authorization gates.
- `generated/FIELDWORK_EXECUTION_CONTROLS.*` renders execution statuses, gap blockers, authorization links, source-claim dependencies, and prohibited private artifacts.
- `tools/fieldwork_lint_helpers.py` centralizes fieldwork-chain link validation so new fieldwork surfaces do not each invent slightly different cross-reference checks.


rev0793 execution-control note: the current revision adds `FIELDWORK_EXECUTION_CONTROLS.*` and keeps the fieldwork execution layer non-closing.

Current rev0793 note file: `991-cloudtainer-fieldwork-execution-controls-incident-clocks-audit-logs-retention-release-and-no-outcome-by-operating-log.md`.

