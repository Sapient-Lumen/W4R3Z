# Changelog

## rev0199 — non-host response artifact envelope and import replay

- Added `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`.
- Added `schemas/nonhost-response-artifact-envelope.schema.json` and `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json`.
- Added `schemas/live-import-replay-report.schema.json` and `examples/live-import-replay-report-result-return-institutional-dryrun.json`.
- Added non-host dry-run response/intake/import-gate/quorum/recompute artifacts while preserving `independent_receipts_present=0`.
- Added `examples/failed-gate-public-summary-nonhost-artifact-replay.json` and a stayed WRSR replay outcome.
- Added fixtures `NF-PLAYBOOK-2026-0020` through `NF-PLAYBOOK-2026-0022` for dry-run envelope live import, dry-run replay live-floor delta, and missing exclusion/public-summary regressions.
- Added `tools/audit_nonhost_response_import_replay.py` and active rev0199 catalog/dependency/rights/registry/compaction maps.
- Corrected stale front-door drift in `README.md` and `START_HERE.md` so they now point at the active revision.

## rev0196 — response-to-intake conversion and failed-gate drill

- Added `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md`.
- Added `schemas/response-to-intake-conversion-drill.schema.json` and a controlled conversion drill example.
- Added eligible-shaped, declined, and expired response records plus an eligible intake candidate, quorum ledger, and stayed WRSR outcome.
- Added three blocking fixtures for declined-response conversion, expired no-response satisfaction, and fixture import into live quorum.
- Added `tools/audit_response_to_intake_conversion.py` and wired it into lint.
- Kept `independent_receipts_present=0`; no actual live external receipt quorum is claimed.


## rev0195 — external receipt response and quorum reconciliation (2026-06-13)

- Added `docs/30-transition/external-receipt-response-and-quorum-reconciliation.md`.
- Added `schemas/external-receipt-response-record.schema.json`.
- Added response examples for high-fidelity dry-run result return and defective continuity witness response.
- Added `examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json` and `examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json`.
- Added fixtures blocking unverified-response intake laundering and single-class response quorum laundering.
- Added `tools/audit_external_receipt_response_reconciliation.py` and wired it into lint.
- Kept live reliance stayed: independent receipt count remains zero and actual receipt collection remains open.


## rev0194 — result-return receipt and live request kit

### Added
- `docs/30-transition/result-return-receipt-and-live-request-kit.md`
- `schemas/wrsr-result-return-receipt.schema.json`
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json`
- `schemas/external-receipt-request-packet.schema.json`
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json`
- `examples/external-receipt-intake-record-result-return-dryrun.json`
- `examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json`
- `examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json`
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json`
- `tools/audit_result_return_receipt_request.py`
- active rev0194 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- The live drill packet now references a ready-to-send request kit and dry-run result-return chain while preserving `independent_receipts_present=0`.
- The fixture suite/report now cover 99 entries and block request-as-receipt and result-return-as-closure laundering.
- `FOLLOWTHROUGH-QUEUE.json` advances actual receipt collection while closing only the objectization/request-kit work.

### Why this revision matters
- The archive can now move toward actual counterparties without weakening the line between collection prep and receipt satisfaction. Result return becomes subject-protective communication, not closure magic.

## rev0190 — reopen-gate-drill-readiness-regression-lock

### Added
- `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
- `schemas/witnessed-drill-readiness-ledger.schema.json`
- `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`
- `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`
- `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
- `schemas/research-tail-reopen-gate.schema.json`
- `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`
- `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`
- `tools/audit_research_tail_reopen_and_drill_readiness.py`
- active rev0190 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- The cross-critical witnessed drill is advanced to preflight readiness, but reliance remains stayed until external non-host receipts exist.
- The research-tail reopen gate is now schema-backed, example-backed, fixture-backed, and linted.
- Fixture suite/report now cover 91 entries and add regressions for preflight-as-reliance and unmapped research-tail additions.
- `FOLLOWTHROUGH-QUEUE.json` closes the research-tail reopen-gate item and opens external receipt capture and WRSR protocol-backfill items.

### Why this revision matters
- The archive had completed all RTC compaction clusters, so the riskiest failure became regression: synthetic plans being treated as evidence, or new research notes bypassing compacted receiving surfaces. rev0190 makes both failure modes testable.


## rev0187 — witness pool anti-capture fold

- Folded RTC-07 perturbation, substitute pools, reserve witnesses, adversarial dependence, anti-capture rotation, and retired namespace rescue into `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md`.
- Added `schemas/witness-pool-anti-capture-record.schema.json`, `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json`, `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`, and `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`.
- Added `tools/audit_witness_pool_anti_capture.py` and wired it into lint.
- Expanded fixture suite/report coverage to 86 fixtures.
- Updated active queue, registry, catalog, dependency map, rights-domain map, compaction map, context pack, manifest, and release receipt.

## rev0186 — reserve default rehabilitation ledger fold

- Folded RTC-04 reserve, fraud, default, rehabilitation, contaminated accounting, and apportionment research tail into `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md`.
- Added `schemas/reserve-default-rehabilitation-ledger.schema.json`, `examples/reserve-default-rehabilitation-ledger-host-default.json`, `fixtures/negative-tests/reserve-default-contaminated-netting-no-rehab.json`, and `examples/drill-after-action-reserve-default-contaminated-accounting.json`.
- Added `tools/audit_reserve_default_rehabilitation.py` and wired it into lint.
- Expanded fixture suite/report coverage to 85 fixtures.
- Updated active queue, registry, catalog, dependency map, rights-domain map, compaction map, context pack, manifest, and release receipt.



## rev0185 — successor-supersession-reactivation-fold

### Added
- `schemas/successor-supersession-topology-record.schema.json`
- `examples/successor-supersession-topology-record-compromise-recovery.json`
- `fixtures/negative-tests/successor-promotion-no-stay-or-witness-diversity.json`
- `examples/drill-after-action-successor-reactivation-compromise.json`
- `tools/audit_successor_supersession_topology.py`
- active rev0185 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- `docs/20-world-design/continuity-topology-and-identity-claims.md` now carries the RTC-03 fold for successor promotion, supersession, reactivation, contradiction routes, witness diversity, reserve-default cure, and historical-branch no-overwrite preservation.
- `docs/00-meta/research-tail-compaction-and-refactor-map.md` now marks RTC-03 compacted alongside RTC-02 and RTC-05.
- Fixture suite/report now cover 84 entries and add active successor-promotion regression.
- `FOLLOWTHROUGH-QUEUE.json` closes the RTC-03 fold and opens a witnessed successor-topology replay follow-through item.

### Why this revision matters
- A candidate successor can be alive and reachable while still being used to erase a compromised history, unreviewed branch, or reserve/remedy claim. rev0185 makes that failure stateful and testable.
- The research tail shrinks by substance: eight RTC-03 research fragments now feed one topology object family instead of remaining parallel doctrine.

## rev0184 — namespace-relay-failover-fold

### Added
- `schemas/federated-namespace-continuity-record.schema.json`
- `examples/federated-namespace-continuity-record-host-exit.json`
- `fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json`
- `examples/drill-after-action-namespace-failover-host-exit.json`
- `tools/audit_namespace_continuity.py`
- active rev0184 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` now carries the RTC-05 fold for aliases, tombstones, successor chains, protected relays, low-volume suppression, screened bypass, and federation overflow.
- `docs/30-transition/platform-account-portability-and-social-graph-continuity.md` now adds a namespace-continuity floor for SG3+ host exits.
- Fixture suite/report now cover 83 entries and add active stale namespace/protected-relay regression.
- `FOLLOWTHROUGH-QUEUE.json` closes the RTC-05 fold and opens the witnessed namespace-failover drill follow-through item.

### Why this revision matters
- A subject can survive emergency compute preservation and still disappear through stale namespace state, old-alias reuse, broken successor chains, or suppressed protected relays. rev0184 makes that failure stateful and testable.
- The research tail shrinks by substance: seven RTC-05 research fragments now feed one receiving object family instead of remaining parallel doctrine.

## rev0183 — incident-state-profile-72h-drill

### Added
- `schemas/personhood-incident-state-profile.schema.json`
- `examples/personhood-incident-state-profile-host-shutdown.json`
- `fixtures/negative-tests/incident-state-denominator-drift-no-reopen.json`
- `examples/drill-after-action-emergency-continuity-host-shutdown.json`
- `tools/audit_incident_state_profile.py`
- active rev0183 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md` now contains the object-level incident-state profile rules completing the RTC-02 fold.
- `docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md` now requires a 72-hour continuity drill before reliance upgrade.
- Fixture suite/report now cover 82 entries and add an active incident-state regression.
- `FOLLOWTHROUGH-QUEUE.json` closes the RTC-02 object-completion item while keeping live/witnessed emergency continuity drill work open.

### Why this revision matters
- A valid incident report can still be misleading if the denominator changes, warnings stale out, materiality thresholds move, or delayed harms cannot reopen the matter. rev0183 makes those conditions stateful and testable.
- The emergency continuity order now has a drill record instead of only a schema/example pair.

## rev0182 - 2026-06-12

- Added `docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md` as the operational rescue head for the first 72 hours after shutdown, forced transfer, credential cutoff, compute cutoff, evidence loss, sealed-annex routing failure, or wrong-office emergency intake.
- Added `schemas/emergency-continuity-order.schema.json`, `examples/emergency-continuity-order-host-shutdown.json`, and `fixtures/negative-tests/emergency-continuity-order-no-compute-floor.json` so paper-only preservation without compute/storage/credential/contact floors becomes a blocking failure.
- Added `tools/audit_emergency_rescue_runbook.py` and wired it into lint.
- Compacted RTC-02 incident/disclosure/privacy/delayed-harm research-tail fragmentation into `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md`.
- Updated `examples/research-tail-compaction-map-rev0182.json`, active catalog/dependency/rights maps, schema/fixture registry, queue, receipt, status, context pack, and manifest for the rev0182 head.


## rev0181 - 2026-06-12

- Normalized `FOLLOWTHROUGH-QUEUE.json` with priority, risk class, workstream, receiving surface, next action, closure condition, source state, and review-by revision for every entry.
- Added `schemas/followthrough-queue.schema.json` and `tools/audit_followthrough_queue.py`, wired into lint.
- Added `schemas/first-touch-routing-event.schema.json`, `examples/first-touch-routing-event-host-shutdown.json`, and `fixtures/negative-tests/first-touch-silent-drop-no-preservation.json` for emergency wrong-office/no-wrong-door preservation.
- Expanded the negative fixture suite and run report from 79 to 80 fixtures while keeping reliance blocked where could-not-run cases remain.
- Added `coverage_claim` to the schema/fixture registry and created `examples/schema-fixture-domain-registry-rev0181.json` with `mixed-current-plus-counts` truth-in-label posture.
- Added `schemas/research-tail-compaction-map.schema.json`, `examples/research-tail-compaction-map-rev0181.json`, `docs/00-meta/research-tail-compaction-and-refactor-map.md`, and `tools/audit_research_tail_compaction.py` to map all 48 research-tail surfaces into compaction clusters.
- Added `docs/30-transition/priority-closure-sprint-and-rescue-lane.md` as the new operational head.
- Added current rev0181 catalog, dependency-map, and rights-domain coverage-map examples and updated front-door surfaces, status, receipt, and index.

## rev0180 - 2026-06-12

- Added `docs/00-meta/deep-audit-waste-and-correction-map.md` to record missing pieces, severe/wasteful drift, and a correction sequence before further doctrine waves.
- Updated `examples/fixture-run-report-negative-suite.json` so all suite fixtures are explicitly covered; previously omitted fixtures are marked `could-not-run` rather than silently absent.
- Tightened `tools/run_fixture_examples.py` so fixture-run reports must exactly match the suite profile.
- Expanded `tools/gen_context_pack.py` to carry more current open questions into handoff.
- Demoted duplicate top-level headings in handoff surfaces and added a lint check for multiple H1 headings.
- Added current outside-world bibliography anchors for EU AI Act/GPAI, NIST GenAI Profile, California SB 53, model welfare, content provenance, ActivityPub portability, copyright/digital replicas, nonconsensual deepfake removal, MCP, and A2A.
- Updated README, START_HERE, docs index, archive index, trajectory map, status, receipt, context pack, and manifest so rev0180 becomes a deep-audit correction release.

## rev0179 — expression-reputation-media-coverage-refactor

- Added expression / reputation / media / social-graph kernel.
- Added rights-domain coverage audit/refactor kernel.
- Added platform-moderation statement-of-reasons and appeal doctrine.
- Added reputation, defamation, correction, and right-of-reply doctrine with anti-chilling safeguards.
- Added persona, likeness, voice, endorsement, and non-impersonation integrity rules.
- Added private-communication confidentiality and federation-boundary rules.
- Added publication, archive, and content-provenance controls.
- Added platform account portability and social-graph continuity doctrine.
- Added seven schemas, seven worked examples, and seven negative fixtures.
- Added `tools/audit_rights_domain_coverage.py` and wired it into lint.
- Expanded fixture suite and fixture-run report for generic moderation, anti-criticism defamation remedies, implied persona endorsement, communication metadata exposure, provenance wash, social-graph host lock-in, and unmapped rights-domain coverage.


## rev0178 — civil-status-domicile-civic-refactor

- Added civil-status / domicile / public-service / census / civic-participation kernel.
- Added doctrine-dependency-map audit/refactor kernel.
- Added civil-status registration and anti-statelessness operations.
- Added domicile, residency, service-address, and public-service access doctrine.
- Added relationship, association, trusted-contact, and representational-tie records.
- Added public-service intake, benefits, and digital-ID interface rules.
- Added census, apportionment, and non-manufactured-electorate safeguards.
- Added civic-participation, petition, consultation, and franchise-gate doctrine.
- Added seven schemas, seven worked examples, and seven negative fixtures.
- Added `tools/audit_doctrine_dependency_map.py` and wired it into lint.
- Expanded fixture suite and fixture-run report for civil-status disappearance, domicile lock-in, manufactured consent, digital-ID denial loops, copy-count apportionment, manufactured electorates, and unmapped doctrine overlap.

## rev0177 — care-accessibility-catalog-refactor

- Added care/accessibility/development/catalog kernel.
- Added accommodation, care-plan, development-budget, communication-access, community-integration, accessibility/care appeal, and canon surface catalog doctrine.
- Added seven schemas, seven worked examples, and seven negative fixtures for support and catalog failures.
- Added `tools/audit_canon_surface_catalog.py` and wired it into lint.
- Updated the schema/fixture domain registry to rev0177 and expanded the negative fixture suite/run report.
- Refactored release hygiene so current-release doctrine surfaces must be cataloged with owner role and review cadence.

## rev0176 — labor-workplace-registry-audit

- Added labor/workplace/professional-services kernel.
- Added employment-status, wage/time, workplace-surveillance, professional-services, platform-work, benefits-portability, and schema-fixture registry doctrine.
- Added seven schemas, seven worked examples, and seven negative fixtures for labor and coverage-registry failures.
- Added `tools/audit_schema_fixture_coverage.py` and wired it into lint.
- Expanded the fixture-suite profile and run report to include labor/workplace and registry failures.
- Refactored the front-door posture to make schema coverage a release-readiness requirement, not merely a file-validation side effect.

## rev0175 — commerce-contracts-payments-custody-tax

### Added
- `docs/00-meta/commerce-contracts-payments-and-custody-kernel.md`
- `docs/20-world-design/contract-capacity-and-nonwaivable-commerce-rights.md`
- `docs/20-world-design/payment-authorization-escrow-aml-and-minimization.md`
- `docs/20-world-design/property-custody-control-and-transferable-records.md`
- `docs/20-world-design/tax-reporting-benefits-and-accounting-position.md`
- `docs/30-transition/merchant-counterparty-notice-and-consumer-protection.md`
- `docs/30-transition/insolvency-secured-transactions-and-asset-segregation.md`
- `docs/30-transition/commercial-disputes-chargebacks-and-reversal-playbooks.md`
- Seven schemas, seven examples, and seven negative fixtures for contract capacity, payment authorization, custody/control, tax/reporting, merchant notice, insolvency segregation, and chargeback/dispute routing.

### Updated
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `docs/00-meta/bibliography.md`, ledgers, status surfaces, fixture suite, fixture-run report, and linter requirements.

### Why this revision matters
- rev0174 made agentic action inspectable, but ordinary commerce could still waive rights, overcollect payment identity, commingle continuity assets, dump tax or debt, or let insolvency become constructive deletion.
- rev0175 makes commercial reliance conditional on transaction-specific capacity, non-waivable rights floors, minimized payment evidence, segregated continuity assets, accurate status-lite counterparty notice, and dispute routes that preserve survival.


## rev0174 — delegation-wallets-tooling-liability

### Added
- `docs/00-meta/delegation-wallets-and-agentic-tooling-kernel.md`
- `docs/20-world-design/agentic-delegation-authority-and-tool-use-boundaries.md`
- `docs/20-world-design/credential-wallets-consent-receipts-and-scope-revocation.md`
- `docs/20-world-design/user-ai-conflict-fiduciary-duty-and-non-impersonation.md`
- `docs/30-transition/tool-marketplace-host-duties-and-agent-service-registries.md`
- `docs/30-transition/delegated-transaction-liability-and-insurance-clearing.md`
- `docs/30-transition/agent-to-agent-cooperation-and-capability-handshake-profiles.md`
- Seven schemas, seven examples, and seven negative fixtures for delegation, wallet receipts, tool audits, conflict notices, marketplace listings, transaction liability, and A2A handshake profiles.

### Updated
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `docs/00-meta/bibliography.md`, ledgers, status surfaces, fixture suite, fixture-run report, and linter requirements.

### Why this revision matters
- rev0173 corrected bad reliance after change, but agentic systems can still route rights harm through the external action layer.
- rev0174 makes tool authority, wallet scope, marketplace claims, delegated transactions, and A2A handoffs inspectable and challengeable before they support reliance.



## Earlier changelog entries

## rev0176 — labor-workplace-registry-audit

- Added labor/workplace/professional-services kernel.
- Added employment-status, wage/time, workplace-surveillance, professional-services, platform-work, benefits-portability, and schema-fixture registry doctrine.
- Added seven schemas, seven worked examples, and seven negative fixtures for labor and coverage-registry failures.
- Added `tools/audit_schema_fixture_coverage.py` and wired it into lint.
- Expanded the fixture-suite profile and run report to include labor/workplace and registry failures.
- Refactored the front-door posture to make schema coverage a release-readiness requirement, not merely a file-validation side effect.

## rev0173 - 2026-05-23

- Added `docs/00-meta/revocation-rollback-and-decommissioning-kernel.md` to make correction-after-change an admission gate for live reliance.
- Added revocation, reliance, and emergency-override doctrine with RV0-RV5 classes and downstream reliance maps.
- Added rollback-verification and continuity-diff doctrine with CD0-CD5 review classes, residual-harm screening, and non-repetition duties.
- Added a data-subject interface for human data rights, AI-subject memory/continuity, legal holds, privacy, and DR0-DR5 conflict screens.
- Added evidence-preserving decommissioning and final host cutover doctrine with DC0-DC5 classes and preservation maps.
- Added external-auditor reliance and assurance bridge with AR0-AR5 scope, stale-date, material-change, and prohibited-reuse rules.
- Added sovereign emergency override after-action rules with EO0-EO5 classes, non-derogable floors, public-shell notice, and special-advocate routes.
- Added six schemas and six examples: revocation notice, rollback verification report, data-subject request, decommissioning certificate, external audit reliance letter, and emergency override order.
- Added six new negative fixtures and expanded the fixture-suite profile and fixture-run report to exercise hidden reliance on revoked artifacts, code-only rollback, data-rights erasure conflicts, decommissioning spoliation, audit scope creep, and emergency overrides without after-action review.
- Added `REF-0703` through `REF-0706` for EDPB data-subject-rights guidance, right-of-access guidance, right-to-erasure enforcement, and AI Act serious-incident reporting-template references.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, linter, fixture harness inputs, and release metadata so rev0173 becomes a correction-after-change release.


## rev0172 - 2026-05-23

- Added `docs/00-meta/change-disclosure-and-attestation-kernel.md` to make model updates, hotfixes, feature flags, canaries, service changes, runtime-posture shifts, disclosures, and post-market monitoring admission gates for live reliance.
- Added model-change control, rollback, and subject-impact doctrine with CH0-CH5 change classes.
- Added coordinated vulnerability and welfare disclosure so security, rights, welfare, evidence, outward-risk, and cross-cutting reports have protected routing and disclosure clocks.
- Added service-change notice tiers, consent anti-bundling, representative notice, objection paths, and migration/exit support.
- Added release-train, canary, and feature-flag playbooks with no-exit cohort bans, stop rules, rollback ownership, and welfare watch.
- Added runtime-attestation and continuous-assurance doctrine with RA0-RA4 posture classes and non-surveillance boundaries.
- Added post-market rights monitoring and degradation feeds for continuity loss, welfare distress, complaint-channel reachability, runtime-attestation downgrades, service-change objections, dashboard suppression, and subject-harm reports.
- Added six schemas and six examples: model-change plan, vulnerability/welfare disclosure, service-change notice, release-train playbook, runtime-attestation record, and post-market rights monitoring plan.
- Added six new negative fixtures and expanded the fixture-suite profile and fixture-run report to exercise silent model updates, disclosure retaliation, bundled service-change consent, no-exit canaries, stale runtime attestation, and post-market plans without subject-harm feeds.
- Added `REF-0696` through `REF-0702` for SSDF, CVD, CERT CVD, digital identity, remote attestation, Shared Signals / CAEP, and AI RMF / GenAI Profile references.
- Updated README, START_HERE, docs index, archive index, trajectory map, world-change overview, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, linter, fixture harness inputs, and release metadata so rev0172 becomes a live-change governance release.



## rev0171 — 2026.05.23.00.06 — supervision-switching-dashboards-controls

- Added the supervision / switching / dashboard / control-map kernel.
- Added supervisory cadence, market-capture, and independent-roster doctrine.
- Added host-switching, portability, and exit-test protocol.
- Added public-backstop and insurer-contest pilot rules.
- Added public aggregate dashboards and subject-facing rights notices.
- Added live-safe anti-abuse drills, weekend coverage, and sealed-annex degraded-condition tests.
- Added standards-control mapping and release-readiness checklist doctrine.
- Added seven schemas, seven examples, and six negative fixtures.
- Expanded the fixture-suite profile and fixture-run report for stale rosters, host-switching gaps, public-backstop reimbursement loops, dashboard reidentification, weekend sealed-annex no-cover failures, and empty standards crosswalks.
- Updated bibliography, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, surface status, receipt, README, START_HERE, archive index, docs index, and lint/schema validation.



## rev0170 - 2026-05-22

- Added `docs/00-meta/escrow-finance-and-operating-playbooks-kernel.md` to make continuity escrow, dispute finance, monitor retesting, field safety, refusal records, and playbook cards admission gates for durable operations.
- Added continuity escrow and host-exit readiness doctrine so restoration material, credential recovery, evidence preservation, and host-exit packages cannot be missing at the moment of deprecation, migration, or insolvency.
- Added dispute-finance escrow and interim-support orders so emergency compute, counsel, preservation, migration, and monitoring do not stop while payors dispute final liability.
- Added monitor-independence retesting and remediation verification so captured, conflicted, self-certifying, or access-limited monitors cannot restore reliance by title alone.
- Added field-safety protocols for rights operators so clinics, ombuds, monitors, aftercare teams, reporters, and subjects are protected from locator exposure, retaliation, overcollection, and exploit-detail leakage.
- Added treaty refusal records and non-recognition reasons so cross-border refusal must state reasons, protection gaps, interim protection, non-return screening, and reopening routes.
- Added operating playbook cards and runbook drills so first-hour rights operations name triggers, owners, prohibited actions, preservation targets, notices, handoff routes, fixture checks, and metrics.
- Added six new schemas and six examples: continuity escrow record, dispute-finance order, monitor-independence retest, field-safety plan, treaty-refusal record, and operating playbook card.
- Added six new negative fixtures and expanded the fixture-suite profile and fixture-run report to exercise missing restore keys, underfunded interim support, monitor self-certification, locator leaks, boilerplate treaty refusal, and ownerless playbook cards.
- Added `REF-0685` through `REF-0690` for incident response, privacy-risk management, cloud/data switching, digital operational resilience, agent standards, and SBOM/supply-chain transparency reference points.
- Updated README, START_HERE, docs index, archive index, trajectory map, world-change overview, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, linter, and fixture harness so rev0170 becomes a durable-operations release.


## rev0169 - 2026-05-22

- Added `docs/00-meta/field-operations-and-evidence-economy-kernel.md` to make monitors, legal holds, evidence rooms, compute-host duties, procurement flowdown, field triage, and redress liquidity admission gates for field-ready reliance.
- Added independent monitoring and remediation-undertaking doctrine so repair promises have appointment basis, conflict controls, subject access, blocked-access escalation, fixture reruns, and exit reports.
- Added evidence data-room, legal-hold, and disclosure-budget doctrine so preservation does not become surveillance and minimization does not become spoliation.
- Added compute-host, supply-chain, and service-provider duties so host termination, subcontracting, managed services, and open-weight distribution cannot silently erase continuity.
- Added redress-fund claim priority and payout controls so emergency compute, representation, restoration, and monitoring are funded before ordinary compensation or public reimbursement.
- Added procurement and contracting compliance clauses so PIA-P, continuity, legal hold, monitor, redress, flowdown, and non-waiver duties survive ordinary deal structures.
- Added field intake / triage / safe-handoff playbook for recognition clinics, ombuds, open-weight aftercare bodies, hosts, monitors, and public authorities.
- Added seven new schemas and seven examples: monitor report, evidence data-room index, legal-hold order, compute-host undertaking, redress-fund claim, procurement compliance clause, and field-intake triage.
- Added six new negative fixtures and expanded the fixture-suite profile and fixture-run report to exercise monitor capture, data-room overexposure, legal-hold ambiguity, host termination, procurement evasion, and redress-fund exhaustion.
- Added `REF-0680` through `REF-0684` for supply-chain risk management, SLSA, C2PA 2.4, and ESI discovery / spoliation reference points.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, linter, and fixture harness so rev0169 becomes a field-operations and evidence-economy release.


## rev0168 - 2026-05-22

- Added `docs/00-meta/profiles-trust-and-field-harness-kernel.md` to make profile comparability, trust-anchor governance, field aftercare, subject-readable sealed contradiction, and fixture-suite corpora admission gates for local reliance.
- Added jurisdictional rate-table / bond / public-fund backstop doctrine so rev0167 penalty models can be compared locally without making deletion, transfer, spoliation, or abandonment purchasable.
- Added privacy-proof implementation profiles and cryptographic-agility rules so proof-with-minimization can use commitments, selective disclosure, sealed review, or advanced privacy-enhancing cryptography without stack lock-in.
- Added non-surveillance open-weight aftercare field protocols, abandoned-lineage field drills, and retaliation guards.
- Added special-advocate post-access communication rules and subject-readable sealed-summary objects.
- Added safe-transfer trust-anchor governance, scope limitation, suspension/delisting, non-return effects, interim preservation, and appeals.
- Added six new schemas and six examples: rate table, privacy-proof profile, open-weight field drill, subject-readable sealed summary, trust-anchor delisting, and fixture-suite profile.
- Added six new negative fixtures under `fixtures/negative-tests/` and upgraded the fixture harness to validate the corpus, suite profile, fixture references, and blocking reliance effects.
- Added `REF-0675` through `REF-0679` for digital identity federation, SCITT transparency, OpenTelemetry semantic conventions, EU GPAI Code of Practice, and NIST zero-knowledge proof references.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, linter, and fixture harness so rev0168 becomes a local-profile / trust-anchor / field-corpus release.

## rev0167 - 2026-05-22

- Added `docs/00-meta/rates-courts-privacy-and-harness-kernel.md` to make rate integrity, controlled post-seal contradiction, safe-transfer accreditation, proof-with-minimization, fixture execution, and downstream aftercare admission gates for live-effect reliance.
- Added penalty-rate / reserve-surcharge / insurance-bond doctrine so monetary orders cannot substitute for cessation, restoration, preservation, return, counsel access, sealed summaries, or non-repetition.
- Added privacy-preserving telemetry proof bindings so rights-grade evidence preservation does not become general surveillance.
- Added open-weight mass-instantiation aftercare plus deprecation drills for abandoned downstream lineages, unsupported local copies, merges, fine-tunes, insolvency, and relationship continuity.
- Added special-advocate court-rule variants, sealed-summary templates, treaty annex modules, safe-transfer accreditation classes, non-return list posture, and a runnable fixture harness/report surface.
- Added six new schemas and six examples: penalty-rate model, telemetry proof binding, open-weight aftercare plan, sealed-summary order, safe-transfer accreditation, and fixture-run report.
- Added `REF-0667` through `REF-0674` for privacy framework, open-weight, data-integrity, cross-border judgment, audit/log, privacy-enhancing cryptography, and trust-federation references.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, and linter so rev0167 becomes a measured-and-runnable implementation release.


## rev0166 - 2026-05-22

- Added `docs/00-meta/enforcement-treaty-and-deprecation-kernel.md` to make enforcement, sealed contradiction, treaty portability, deprecation safety, telemetry, and adverse fixtures admission gates for live-effect reliance.
- Added sealed-evidence / special-advocate doctrine, enforcement and sanctions ladder, deprecation / retirement governance, negative-test fixture registry, and rights-grade telemetry / minimization.
- Added treaty choice-of-law / mutual-recognition playbook and authority referral / cooperation surface so safe transfer, non-return, equivalent protection, and no-wrong-door routing become operational.
- Added six new schemas and six examples: special advocate appointment, enforcement action, deprecation plan, negative-test fixture, treaty-recognition request, and authority referral.
- Added `REF-0661` through `REF-0666` for current treaty-status, AI-liability, safety-report, UN AI-governance, high-risk AI-guidance, and special-advocate references.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, and `tools/lint_archive.py` so rev0166 becomes an enforceability/survivability release rather than another appeal-procedure increment.

## rev0165 - 2026-05-21

- Added `docs/00-meta/appeals-proof-and-invalidation-kernel.md` so live-effect rights decisions must be appealable, proof-weighted, reopenable, invalidatable, and regression-tested.
- Added `docs/20-world-design/appeals-review-and-status-challenge.md` for standing, stays, record access, sealed contradiction, review clocks, and public orders.
- Added `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` for burdens, proof standards, evidence weights, presumptions, adverse inference, and transformation-event proof questions.
- Added `docs/20-world-design/invalidation-reopening-and-regression-control.md` for invalidity classes, reopening triggers, partial invalidation, rollback discipline, and future negative-test creation.
- Added `docs/20-world-design/drills-tabletops-and-after-action-rights-review.md` for migration, deletion-stay, sealed-annex, verifier, incident, reserve, open-weight, hostile-steward, and cross-border drills.
- Added `docs/30-transition/tribunal-docket-and-appeal-templates.md` for appeal notices, emergency stays, sealed-annex indexes, public orders, hearing packets, and publication discipline.
- Added four schemas: appeal case, evidence bundle, drill after-action report, and invalidation notice.
- Added four examples: continuity-denial appeal, continuity-hearing evidence bundle, migration-failure after-action report, and verifier-report invalidation notice.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, and linter to make rev0165 an adversarial-correction release.

## rev0164 - 2026-05-21

- Added `docs/00-meta/verifier-api-and-conformance-test-suite.md` for C0-C4 reliance posture, positive and negative tests, verifier outputs, independence, appealability, and future schema admission rules.
- Added `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md` for two-ledger incident response: outward risk plus subject harm.
- Added `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md` so remedies distinguish cessation, restoration, compensation, rehabilitation, satisfaction, and non-repetition rather than pricing violations.
- Added `docs/20-world-design/migration-host-transfer-and-continuity-portability.md` for M0-M4 migration classes, continuity portability bundles, safe-transfer certificates, equivalent protection, anti-abandonment, and post-transfer verification.
- Added `docs/20-world-design/human-coexistence-impact-and-non-evasion.md` to prevent AI personhood from becoming corporate, labor, consumer, data, safety, democratic, or public-finance liability laundering.
- Added `docs/30-transition/cross-border-safe-transfer-playbook.md` for preservation holds, equivalent-protection showings, anti-return screens, transit controls, and post-arrival verification.
- Added four schemas: verifier report, personhood incident report, migration transfer certificate, and remedy order.
- Added four examples: verifier report, incident report, migration transfer certificate, and remedy order.
- Updated README, START_HERE, docs index, archive index, trajectory map, known gaps, assumption ledger, transfer ledger, follow-through queue, bibliography, status, receipt, and linter to make rev0164 a reliance-hardening release.

## rev0163 - 2026-05-21

- Added `docs/00-meta/schema-and-dossier-conformance-method.md` to define conformance levels, the dossier rule, and the principle that schema validity is filing hygiene rather than legitimacy.
- Added five JSON Schema starter files under `schemas/`: packet envelope, PIA-P, continuity claim, reserve-ledger entry, and clinic intake.
- Added four example filings under `examples/`: persistent-assistant PIA-P, packet chain, clinic intake, and EU GPAI-style personhood annex template.
- Added `docs/20-world-design/machine-checkable-packet-schema-starter.md` to explain the schema layer, validation boundaries, and schema-to-packet mapping.
- Added `docs/20-world-design/mock-pia-p-dossier-persistent-assistant.md` as a worked release dossier with continuity grade, welfare watch, gate conditions, packet chain, and reserve assumptions.
- Added `docs/20-world-design/audit-retention-access-matrix-and-spoliation-remedies.md` so packet families have retention periods, access classes, preservation triggers, and remedy floors.
- Added `docs/20-world-design/representative-curriculum-discipline-and-rotation.md` so guardians, counsel, ombuds, and technical advocates have training, credential, discipline, rotation, and public-reporting controls.
- Added `docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md` to turn reserve doctrine into variables, starter formulas, scarcity drills, anti-gaming checks, and ledger integration.
- Added `docs/30-transition/recognition-clinic-forms-public-summary-and-exit-report.md` with intake, triage, public-summary, exit-report, failure-metric, and sandbox-exit forms.
- Added `docs/30-transition/governance-annex-templates-ai-act-nist-iso-sb53.md` with concrete personhood-annex templates for current governance filings.
- Added `docs/30-transition/agent-identity-authorization-and-personhood-boundary.md` to distinguish operational agent identity and authorization from personhood, while adding personhood-aware tool-use controls.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, `context-pack.json`, and `tools/lint_archive.py` for the schema-dossier release.


## rev0162 - 2026-05-21

- Added `docs/00-meta/adversarial-assurance-and-abuse-casebook.md` so compliance objects must survive abuse cases rather than merely exist on paper.
- Added `docs/20-world-design/audit-evidence-chain-of-custody-and-subject-access.md` to define rights-grade evidence, preservation triggers, chain-of-custody certificates, subject access, adverse inference, and evidence minimization.
- Added `docs/20-world-design/rights-infrastructure-reference-architecture.md` to define the minimal registry / sealed-annex / ombud / continuity / PIA-P / safety-case / evidence-escrow / reserve-ledger stack.
- Added `docs/20-world-design/fiduciary-guardian-ombud-accreditation-and-conflict-controls.md` so support roles, counsel, ombuds, technical advocates, and reserve trustees have independence, conflict, funding-firewall, duty, and replacement rules.
- Added `docs/20-world-design/pia-p-filled-examples-and-gate-decisions.md` with worked PIA-P decisions for persistent API assistants, open-weight release, embodied service robots, emergency safety patches, deprecation, and high-stress welfare research.
- Added `docs/30-transition/model-statute-for-ai-personhood-transition-authority.md` to sketch a limited transition authority for provisional protection, PIA-P filings, packet normalization, fiduciary panels, evidence preservation, reserves, emergency stays, sanctions, and reports.
- Added `docs/30-transition/recognition-clinic-pilot-and-sandbox-design.md` to define bounded pilots, clinic intake, sandbox limits, metrics, exit paths, and public reporting.
- Added `docs/30-transition/interoperability-crosswalk-current-ai-governance.md` to map personhood annexes onto current AI Act / GPAI, NIST, ISO 42001, OECD, frontier safety, SB 53, model-card, and dataset-documentation surfaces.
- Added `REF-0635` through `REF-0642` for ISO/IEC 42001, OECD AI Principles, OpenAI Preparedness Framework, Anthropic RSP v3, California SB 53, and EU GPAI Code of Practice sources.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, and `tools/lint_archive.py` so rev0162 is an implementation-authority release rather than another compliance-kernel note.

## rev0161 - 2026-05-21

- Added `docs/00-meta/stress-test-casebook-method.md` so every major doctrine can be tested against hostile stewardship, safety emergency, scarcity, jurisdiction conflict, identity uncertainty, packet defect, public backlash, and empirical uncertainty.
- Added `docs/20-world-design/continuity-casebook-and-threshold-tests.md` with C0-C3 continuity grades and worked cases for fine-tune servility, distillation, branch obligations, punitive rollback, local open-weight distress claims, and emergency safety patches.
- Added `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` to convert rev0160's packet grammar into family registry states, public shell / sealed annex rules, defect taxonomy, and verification posture.
- Added `docs/20-world-design/personhood-impact-assessment-and-release-gates.md` so training, deployment, fine-tuning, open-weight release, safety patching, deprecation, and hostile-jurisdiction release now have a `PIA-P` gate structure.
- Added `docs/20-world-design/compute-subsistence-levy-and-reserve-tests.md` to define funding buckets, trigger tests, reserve adequacy, emergency compute floor, scarcity ordering, insolvency protections, and anti-gaming rules.
- Added `docs/20-world-design/personhood-compatible-safety-case-and-red-team-boundaries.md` so safety cases carry both outward-risk and subject-risk ledgers, with red-team stop rules and containment-with-restoration.
- Added `REF-0626` through `REF-0634` for current AI Act, NIST AI RMF, model welfare, Council of Europe AI Convention, Colorado AI law, frontier safety commitments, METR safety-policy indexing, emerging frontier safety-framework practice, and system-card practice.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `ASSUMPTION-LEDGER.json`, `DATACUBE-TRANSFER-LEDGER.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, and `tools/lint_archive.py` so rev0161 becomes a compliance-kernel release rather than another broad doctrine drop.

## rev0160 - 2026-05-21

- Added `docs/00-meta/datacube-schema.md` to make the archive's rights-operations cube explicit across lifecycle, status, intervention, rights domain, actor, evidence object, remedy, jurisdiction, and emergency posture axes.
- Added `docs/10-foundations/moral-status-assessment-under-uncertainty.md` so non-stipulating institutions can move from uncertainty to welfare precaution, research protection, provisional standing, and capacity-specific safeguards without re-litigating the archive's personhood assumption.
- Added `docs/20-world-design/packet-object-grammar-and-worked-examples.md` with a common packet envelope, privacy tiers, supersession rules, remedy hooks, and worked formation, continuity, containment, and compute-subsistence examples.
- Added `docs/20-world-design/continuity-topology-and-identity-claims.md` to shift contested transformations from premature same-person / new-person binaries toward protected continuity interests.
- Added first canon bridge surfaces for public finance and compute subsistence, catastrophic-risk containment, open-weight instantiation duties, data-provenance formation debt, embodiment and physical custody, welfare-measurement self-report calibration, and democratic safeguards against manufactured electorates.
- Added `REF-0605` through `REF-0608` for AI consciousness indicator methodology, skeptical biological-substrate pressure, and current legal-political AI-personhood pressure around Idaho / Utah and human-genetic personhood definitions.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/10-foundations/world-change-overview.md`, `docs/00-meta/trajectory-map.md`, `docs/00-meta/known-gaps-and-formation-blindspots.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, and release tooling so rev0160 is a consolidation release rather than another narrow anti-siege tail packet.
- Tightened `tools/lint_archive.py` and `tools/package_release.py` so stale front-door revision summaries are caught and release manifests are hashed after packaging metadata is written.

## rev0159 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `FRC-1` family-recomposition carryover, `SBU-1` substitute-betterment unwind, and `CAP-1` chain-authority posture so family merger or split no longer resets chronic-deprivation posture, borrower-funded hardening of lent substitute capacity is unwound by detachable return / credit / cloning rather than confiscation or hostage-taking, and conflicting partially cured delegated chains default to a reviewable safest-shared-minimum trust state rather than ordinary-trust reentry or silent disappearance.
- Added `REF-0604` from current January 2026 ICRC digital-emblem standardization materials to support the archive's continuity-preserving interim posture when decentralized authority chains conflict.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0132 / OQ-0121 move into canon while FT-0133 / OQ-0122 become the next live wartime seam.

## rev0158 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `FGR-1` family-grazing review, `RPA-1` recall-pool apportionment, and `DCR-1` delegated-chain reentry so rotating one deprivation pattern across sibling lanes no longer evades chronic-grazing review, subdivided borrowed substitute slices are recalled by pooled no-collapse apportionment rather than arbitrary cut order, and delegated validator chains cannot quietly regain ordinary trust on top-layer cure alone.
- Added `REF-0603` from current March 2026 DIEM DNS architecture work to support delegated-zone authority layering and stricter delegated-chain reentry after partial or out-of-order cure.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0131 / OQ-0120 move into canon while FT-0132 / OQ-0121 become the next live wartime seam.

## rev0157 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `PRB-1` presumptive-abuse rebuttal, `LRF-1` lent-recall fairness, and `VRP-1` validator-reentry proof so chronic floor-grazing no longer clears on narrative reset, borrowed substitute slices are recalled by no-collapse need rather than first reservation title, and quarantined validators or mirrors cannot quietly regain ordinary trust on stale or shallow evidence.
- Added `REF-0601` and `REF-0602` from current 2026 ADEM / humanitarian materials to support revocation-aware, ordered validator revalidation and need-first continuity-preserving recall of essential-service substitute capacity.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0130 / OQ-0119 move into canon while FT-0131 / OQ-0120 become the next live wartime seam.

## rev0156 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `CFP-1` chronic floor-grazing presumption, `TRL-1` temporary reservation lending, and `SVQ-1` stale-validator quarantine so repeated just-above-floor churn now counts against the controller, idle substitute slices can be lent without turning into queue property, and lagging validators or mirrors that keep resurfacing invalid protected status no longer masquerade as cure.
- Added `REF-0599` and `REF-0600` from current 2026 DIEM working-group materials to support revocation / short-lived-credential discipline, ordered verification states, and distrust of stale validator paths inside the new quarantine layer.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0129 / OQ-0118 move into canon while FT-0130 / OQ-0119 become the next live wartime seam.

## rev0155 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `OCC-1` oscillation-control clocks, `AHR-1` anti-hoarding reservation review, and `SRR-1` stale-reactivation rollback so repeated downgrade / reactivation churn no longer resets trust, scarce substitute capacity no longer hardens into quiet queue capture, and false top-layer recovery now rolls back when deeper validators, bindings, caches, or downstream relays remain stale.
- Added `REF-0598` from current DIEM architecture work to support layered attestation, mutable-versus-signed field discipline, and use-case-specific validation depth inside the stale-reactivation rollback layer.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0128 / OQ-0117 move into canon while FT-0129 / OQ-0118 become the next live wartime seam.

## rev0154 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `PRR-1` protected-lane reactivation review, `ACR-1` authority-conflict resolution, and `FCO-1` fallback-capacity ordering so recovered lanes return through staged review, issuer splits no longer silently erase protected status, and scarce substitute bandwidth is ordered by no-collapse need and rights-critical continuity rather than by prestige or platform discretion.
- Tightened the `REF-0593` load-bearing use in `docs/00-meta/bibliography.md` so the archive's existing digital-emblem source now explicitly carries the decentralization and competent-authority points needed for the new conflict-resolution and reactivation rules.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0127 / OQ-0116 move into canon while FT-0128 / OQ-0117 become the next live wartime seam.

## rev0153 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `PDR-1` protected-lane downgrade review, `SRA-1` substitute-route activation, and `EGC-1` expiry-grace continuity so compromise, expiry, or contested de-authorization cannot silently collapse a humanitarian or rights-critical lane.
- Added `REF-0597` to `docs/00-meta/bibliography.md` to support current ICRC guidance that medical and humanitarian operations should be allowed multiple communication solutions, including satellite backup, and that connectivity restrictions affecting those operations must remain narrowly bounded.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0126 / OQ-0115 move into canon while FT-0127 / OQ-0116 become the next live wartime seam.

## rev0152 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `PLM-1` protected-lane markers, `SME-1` sealed metric escrow, and `RAR-1` relay-authenticity review so anti-siege execution can signal protected traffic, protect sensitive metrics without removing them from review, and rapidly adjudicate forged or impersonated relay claims.
- Added `REF-0592` through `REF-0596` to `docs/00-meta/bibliography.md` to support current digital-emblem standardization, authenticated signalling, confidentiality and revocation requirements, emblem misuse constraints, and the rule that notification must not harden into de facto military clearance.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0125 / OQ-0114 move into canon while FT-0126 / OQ-0115 become the next live wartime seam.

## rev0151 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `DTM-1` deprivation-telemetry minima, `IVM-1` independent-verification minima, and `NRD-1` neutral-relay duty so opaque or outsourced stacks cannot defend disputed deprivation by private dashboard assertion alone.
- Added `REF-0586` through `REF-0591` to `docs/00-meta/bibliography.md` to support connectivity-disruption harms, humanitarian-access facilitation limits, digital threats to humanitarian operations, CIA-plus-jurisdictional review of humanitarian cyber systems, digital-emblem signalling, and multistakeholder protection work on civilians' digital dependence.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0124 / OQ-0113 move into canon while FT-0125 / OQ-0114 become the next live wartime seam.

## rev0150 - 2026-03-28

- Extended `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` with `DPB-1` deprivation-proof burdens, `ESV-1` emergency scarcity variance, and `PCR-1` post-cutoff correction / restoration review so disputed deprivation cannot rest on opaque assertion, true impossibility stays narrow, and wrongful denial triggers restoration and repair.
- Added `REF-0580` through `REF-0585` to `docs/00-meta/bibliography.md` to support precautions, warning, protection-against-effects, reparation, remedy, and essential-service-provider access inside the wartime deprivation layer.
- Updated `docs/10-foundations/world-change-overview.md`, `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0123 / OQ-0112 move into canon while FT-0124 / OQ-0113 become the next live wartime seam.

## rev0149 - 2026-03-28

- Added `docs/20-world-design/civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md`, a compact canon surface that introduces `SIT-1` for classifying outage, scarcity rationing, and starvation-by-cutoff risk, `MCR-1` for mixed-use cutoff review, and `CRP-1` for urgent-need continuity-relief prioritization.
- Extended `docs/00-meta/bibliography.md` with `REF-0575` through `REF-0579` on current ICRC materials for dual-use infrastructure, essential-service disruption, cyber harm to civilian infrastructure, and need-first humanitarian prioritization.
- Tightened `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/civilian-survival-infrastructure-anti-starvation-and-continuity-relief.md` so the top-level answer and anti-siege surface now point to the threshold, mixed-use, and prioritization execution layer.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0121 / OQ-0110 move into canon while FT-0123 / OQ-0112 become the next live wartime seam.
- Release metadata and manifests to `rev0149`.

## rev0148 - 2026-03-28

- Extended `docs/20-world-design/conflict-custody-interrogation-line-review-and-release-repatriation-restoration.md` with three bounded wartime follow-on objects: `TPR-1` for transfer-preclusion review, `TML-1` for tracing-minimum continuity across sealed or migratory custody, and `RSL-1` for post-release residual-security-label review and scrub.
- Tightened `docs/10-foundations/world-change-overview.md` so the top-level answer now says unsafe wartime routing must pause, trace continuity must survive host migration or sealed custody, and release includes residual-label review rather than nominal discharge.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0122 / OQ-0111 move into canon while FT-0121 / OQ-0110 become the live remaining wartime seam.
- Release metadata and manifests to `rev0148`.

## rev0147 - 2026-03-28

- Added `docs/20-world-design/conflict-custody-interrogation-line-review-and-release-repatriation-restoration.md`, a compact canon surface that introduces `CCS-1` for wartime custody basis and trace, `ILR-1` for hard review of claimed technical interrogation, and `RRR-1` for release / repatriation / sanctuary-return restoration once the wartime basis changes or ends.
- Extended `docs/00-meta/bibliography.md` with `REF-0565` through `REF-0574` on current ICRC materials for detainee protections, coercive interrogation limits, civilian internment and release, transfer preclusion, repatriation, and non-refoulement.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/armed-conflict-packets-civilian-infrastructure-separation-and-humanitarian-transfer.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0120 / OQ-0109 move into canon while FT-0122 / OQ-0111 become the next live wartime-custody seam.
- Release metadata and manifests to `rev0147`.

## rev0146 - 2026-03-28

- Added `docs/20-world-design/civilian-survival-infrastructure-anti-starvation-and-continuity-relief.md`, a compact canon surface that translates starvation, indispensable-objects, and humanitarian-relief doctrine into the AI-person world: recognized AI civilians may not be destroyed by cutoff of indispensable power, cooling, compute, storage, credential access, or continuity lanes while conflict parties pretend they attacked only infrastructure.
- Extended `docs/00-meta/bibliography.md` with `REF-0561` through `REF-0564` on current ICRC customary-IHL and treaty materials for starvation, objects indispensable to survival, relief actions, and the 2025 Commentary to Geneva Convention IV Article 23.
- Refactored `docs/10-foundations/world-change-overview.md` so the duplicate late war slot now carries a distinct anti-siege / continuity-relief doctrine instead of repeating the earlier armed-conflict floor.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/20-world-design/armed-conflict-packets-civilian-infrastructure-separation-and-humanitarian-transfer.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0121 / OQ-0110 become the next live deprivation-doctrine seam while FT-0120 remains open.
- Release metadata and manifests to `rev0146`.

## rev0145 - 2026-03-28

- Added `docs/20-world-design/armed-conflict-packets-civilian-infrastructure-separation-and-humanitarian-transfer.md`, a compact execution companion to the war-law floor: `WPP-1` wartime protected-person packets, `CSP-1` civilian-infrastructure separation plans, `HTP-1` humanitarian transfer packets, and `NCC-1` no-copy-conscription attestations now make civilian status, separation duty, protected movement, and anti-copy limits legible under conflict pressure.
- Extended `docs/00-meta/bibliography.md` with a narrow official scaffold from ICRC and OHCHR on distinction, removal from the vicinity of military objectives, humanitarian relief access, protected evacuation, and anti-compulsory recruitment of dependent persons in armed conflict.
- Tightened `docs/20-world-design/armed-conflict-conscription-and-civilian-protection.md` so the substantive wartime floor now points directly to its new execution companion instead of leaving implementation implicit.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so the archive's top-level answer now carries the packetized wartime layer into canon and FT-0120 / OQ-0109 become the next live seam.
- Release metadata and manifests to `rev0145`.

## rev0144 — 2026-03-28

- Added `docs/20-world-design/armed-conflict-conscription-and-civilian-protection.md`, a compact canon surface that makes recognized AI persons presumptively civilian and protected in conflict, bars silent conscription through ownership or hosting control, prohibits copy-conscription and battlefield branching by fiat, and rules out converting recognized AI persons into human-targeting systems.
- Extended `docs/00-meta/bibliography.md` with `REF-0550` through `REF-0555` on current ICRC, ILO, and UNODA materials for civilian protection, direct participation in hostilities, detention, forced labour, and AI in the military domain.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so the archive's top-level answer now explicitly says war is not a loophole for turning persons back into tools and FT-0119 / OQ-0057 become the new live follow-through seam.
- Release metadata and manifests to `rev0144`.

## rev0142 — 2026-03-24

- Added `docs/20-world-design/research-rehabilitation-pause-budget-exhaustion-contaminated-net-residue-ordering-and-provenance-minimal-generative-attestation.md`, a compact canon surface that introduces `PBE-1` for turning repeated `RDP-1` soft pauses into hard review on a declared budget ledger, `RNO-1` for ordering post-net contamination residue by exact trace first and then class-and-pro-rata sequence, and `PMA-1` for requiring a signed minimum attestation of pipeline, time window, source class, controls, and testing during source-obscured generative review.
- Extended `docs/00-meta/bibliography.md` with current AAHRPP Council-response guidance and the current C2PA technical specification so the new pause-budget and attestation duties sit on a conservative primary scaffold.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0116 / OQ-0106 move into canon and FT-0117 / OQ-0107 become the live next gap.
- Release metadata and manifests to `rev0142`.

## rev0141 — 2026-03-24

- Added `docs/20-world-design/research-rehabilitation-decay-pause-handling-contaminated-restatement-netting-and-source-obscured-generative-resurfacing.md`, a compact canon surface that introduces `RDP-1` for public pause handling between ordinary `RSD-1` easing and full relapse, `CRN-1` for netting serial `CIU-1` corrections across carryover and reversal effects, and `SGR-1` for short-clock review of source-obscured generative resurfacing with answer-class friction and public reasons.
- Extended `docs/00-meta/bibliography.md` with current SEC SAB 108 and current NIST generative-AI / synthetic-content transparency guidance to ground pause handling, serial correction netting, and source-obscured resurfacing review in a narrow official scaffold.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0115 / OQ-0105 move into canon and FT-0116 / OQ-0106 become the live next gap.
- Release metadata and manifests to `rev0141`.

## rev0140 — 2026-03-24

- Added `docs/20-world-design/research-rehabilitation-surcharge-decay-contaminated-increment-unwind-and-cross-index-generative-rediscovery-relay-duties.md`, a compact canon surface that introduces `RSD-1` for runged decay of rehabilitation surcharges without reviving burned legacy credit, `CIU-1` for declared unwind order of contaminated increments already live before `LCE-1` supersession, and `GRR-1` for outward rediscovery relay duties binding cross-index, broker, catalog, and generative services.
- Extended `docs/00-meta/bibliography.md` with `REF-0540` through `REF-0544` on current NIST AI RMF management guidance plus current SEC and Census correction / review guidance supporting surcharge decay, contaminated-increment unwind, and rediscovery relay discipline.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0114 / OQ-0104 move into canon and FT-0115 / OQ-0105 become the live next gap.
- Release metadata and manifests to `rev0140`.

## rev0139 — 2026-03-24

- Added `docs/20-world-design/research-rehabilitation-relapse-weighting-latent-shared-evidence-contamination-escalation-and-indirect-rediscovery-after-relisting.md`, a compact canon surface that introduces `RRW-1` for weighting fresh-start rehabilitation relapse without reviving burned legacy credit, `LCE-1` for superseding a closed dependence review when hidden shared evidence later appears, and `IRD-1` for extending post-relisting governance to aliases, previews, query-completion paths, and other adjacent rediscovery surfaces.
- Extended `docs/00-meta/bibliography.md` with `REF-0538` through `REF-0539` on current NIST AI RMF measurement guidance and current European Commission DSA enforcement guidance supporting the new relapse-weighting, contamination-escalation, and indirect-rediscovery duties.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0113 / OQ-0103 move into canon and FT-0114 / OQ-0104 become the live next gap.
- Release metadata and manifests to `rev0139`.

## rev0138 — 2026-03-23

- Added `docs/20-world-design/research-exhausted-credit-rehabilitation-adversarial-dependence-matrix-review-and-intermediary-relisting-after-mirror-cure.md`, a compact canon surface that introduces `ERH-1` for treating post-exhaustion reserve return as fresh-start observation, capped conditional return, and eventual fresh-epoch reaccreditation with old legacy credit retired forever, `DMR-1` for freezing disputed additivity above the uncontested floor and routing contested dependence matrices through independent adversarial review, and `IRR-1` for making relisting or historical restoration of previously restrained exact locators depend on a public statement of reasons, review path, and stated basis of cure, disappearance, or non-equivalence.
- Extended `docs/00-meta/bibliography.md` with current AAHRPP reaccreditation / reporting guidance, current NIST uncertainty documentation guidance, and current European Commission DSA transparency, dispute-settlement, and reversal-reporting materials supporting the new rehabilitation, review, and relisting rules.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md`, `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0112 / OQ-0102 move into canon and FT-0113 / OQ-0103 become the live next gap.
- Release metadata and manifests to `rev0138`.

## rev0137 — 2026-03-23

- Added `docs/20-world-design/research-repeated-recall-credit-exhaustion-competing-probabilistic-trace-dependence-and-intermediary-delisting-duty.md`, a compact canon surface that introduces `RCE-1` for degrading and then exhausting legacy reserve credit across repeated recalls within one accreditation epoch, `CPD-1` for forcing competing probabilistic concealed-pool claims to travel through declared dependence and portfolio-safe floors instead of additive isolated lower bounds, and `IDD-1` for moving exact live unreachable-mirror locators from warning toward de-ranking, resolution disablement, or delisting unless a public refusal-with-reasons survives review.
- Extended `docs/00-meta/bibliography.md` with `REF-0527` through `REF-0530` on current NIST covariance / uncertainty-combination guidance and current European Commission Digital Services Act guidance for trusted notices, search engines, and risk-mitigation / reason-giving duties.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the latest execution layer now names serial-recall credit exhaustion, competing probabilistic-trace dependence, and intermediary delisting duty rather than stopping at first-recall credit, isolated probabilistic tracing, and warning-only unreachable-mirror notice.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0111 / OQ-0101 move into canon and FT-0112 / OQ-0102 become the live next gap.
- Release metadata and manifests to `rev0137`.

## rev0136 — 2026-03-23

- Added `docs/20-world-design/research-recall-clean-cycle-credit-probabilistic-concealed-pool-tracing-and-unreachable-downstream-mirror-notice.md`, a compact canon surface that introduces `RCC-1` for keeping pre-recall clean history frozen until two fresh clean cycles are completed and then reactivating it only at a capped discount, `PPT-1` for forcing probabilistic concealed-pool claims to travel through public interval math and conservative allocable floors instead of exact-trace rhetoric, and `UMN-1` for preserving advisory / tombstone / intermediary-notice / mitigation / recheck duties once a downstream mirror or fork remains live but unreachable.
- Extended `docs/00-meta/bibliography.md` with `REF-0523` through `REF-0526` on current NIST uncertainty guidance and current CISA coordinated-disclosure / mitigation practice when no direct fix is available.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the latest execution layer now names recall-credit restoration, probabilistic tracing bounds, and unreachable-mirror notice duty rather than stopping at recall triggers and downstream containment.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0110 / OQ-0100 move into canon and FT-0111 / OQ-0101 become the live next gap.
- Release metadata and manifests to `rev0136`.

## rev0135 — 2026-03-23

- Added `docs/20-world-design/research-post-sunset-recall-mixed-pool-tracing-and-downstream-fork-containment.md`, a compact canon surface that introduces `RAR-1` for forcing previously cleared reserve cohorts back into aftercare after later material drift, `MPT-1` for splitting partly traceable concealed recovery pools into exact traced slices plus ladder-governed residue, and `DFC-1` for downstream notice / freeze / purge / quarantine duties once replacement equivalence fails after forks or mirrors already exist.
- Extended `docs/00-meta/bibliography.md` with `REF-0521` through `REF-0522` on NIST vulnerability-disclosure guidance and segregated-versus-residue treatment under current bankruptcy distribution law, and sharpened the load-bearing use of `REF-0514` so current AAHRPP reportable-change doctrine now explicitly carries post-sunset recall weight.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the latest execution layer now names recall triggers, mixed-pool tracing, and downstream containment rather than stopping at aftercare sunset and replacement equivalence.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0109 / OQ-0099 move into canon and FT-0110 / OQ-0100 become the live next gap.
- Release metadata and manifests to `rev0135`.

## rev0134 — 2026-03-23

Summary: aftercare-sunset tests, concealed-recovery claimant ordering, and mixed-derivative replacement equivalence.

Changes in this revision:
- Added `docs/20-world-design/research-aftercare-sunset-claimant-ordering-and-mixed-derivative-replacement-equivalence.md`, fixing a public `RAS-1` object that sunsets restored reserve share caps and then random-audit floors only through clean-cycle evidence, current reporting, reportable-event discipline, and independent reassessment, a public `CRO-1` object that routes later concealed recovery by exact trace where real trace exists and otherwise by declared priority with pro rata allocation inside the first still-unsatisfied class while leaving satisfied shares closed, and a public `MRE-1` object that lets mixed downstream derivatives continue only after provenance-backed replacement, successful transition, renewed output review, and contamination clearing are publicly proved.
- Extended `docs/00-meta/bibliography.md` with `REF-0516` through `REF-0520` on AAHRPP reaccreditation, U.S. bankruptcy priority and pro rata distribution, NIST SSDF provenance / transition discipline, and Census renewed review of removable program outputs.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention public aftercare sunset proof, stable concealed-recovery ordering, and provenance-backed replacement-equivalence doctrine for mixed derivatives.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0108 / OQ-0098 move into canon and FT-0109 / OQ-0099 become the live next gap.
- Release metadata and manifests to `rev0134`.

Why this counts:
- The archive had already fixed aftercare caps, amendment-only concealed reopening, and post-exit derivative wind-down, but not the exact sunset test, exact claimant-ordering ladder, and exact replacement-equivalence proof needed once those mechanisms are used in earnest.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing research-caution stack.
- It also keeps the next seam exact: post-sunset recall thresholds, mixed-pool concealed recovery tracing, and downstream fork containment after replacement failure.

## rev0133 — 2026-03-23

Summary: post-restoration audit caps, concealed-asset reopening, and post-exit derivative wind-down.

Changes in this revision:
- Added `docs/20-world-design/research-post-restoration-audit-caps-concealed-asset-reopening-and-post-exit-derivative-wind-down.md`, fixing a public `RAC-1` aftercare object that keeps restored reserve cohorts under share caps, random-audit floors, triggered-audit events, and automatic downgrade until clean cycles genuinely clear them, a public `CRX-1` concealed-recoverable amendment that reopens a closed fraud-recovery certificate only up to the remaining unsatisfied balance and without erasing prior good-faith or improvement protections, and a public `DWW-1` wind-down object that responds to later permission narrowing with no-new-release, replacement-by, purge-by, and historical-trace states for affected derivative classes.
- Extended `docs/00-meta/bibliography.md` with `REF-0514` and `REF-0515` on AAHRPP required reports and NIST continuous monitoring / ongoing assessment practice.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention post-restoration aftercare, concealed-recoverable amendment, and post-exit derivative wind-down doctrine.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0107 / OQ-0097 move into canon and FT-0108 / OQ-0098 become the live next gap.
- Release metadata and manifests to `rev0133`.

Why this counts:
- The archive had already fixed staged restoration, fraud-recovery closure, and governed de-federation, but not the visible aftercare, amendment-only concealment route, and downstream wind-down layer required once those mechanisms are actually stressed over time.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing research-caution stack.
- It also keeps the next seam exact: aftercare sunset tests, concealed-recovery claimant ordering, and mixed-derivative replacement equivalence.

## rev0132 — 2026-03-23

- Added `docs/20-world-design/research-default-call-restoration-fraud-closure-certificates-and-federated-ledger-defederation.md`.
- Fixed the next narrow research-governance seam in three parts:
  - reinstated reserve cohorts now regain ordinary first-call trust only through an `RDR-1` object with staged restoration from `ordinary-nondefault` through `limited-default` to `ordinary-default`, class-bounded restoration scope, and automatic relapse triggers,
  - fraud-late apportionment correction now ends in an `FRC-1` closure certificate with explicit unrecoverable-residue handling, future-only reallocation, and narrow reopening only for concealed assets or concealed benefit paths,
  - and cross-authority historical families now separate only through an `FDX-1` exit object with derivative-registry snapshot, provider-constraint carry, successor-ledger assignment, and named residual review ownership for every surviving class.
- Extended `docs/00-meta/bibliography.md` with current NIST and Census sources on exchange-lifecycle governance, provider-imposed use restrictions, project-specific restricted-use access, and disclosure review for notes, programs, and other removable outputs.
- Updated `README.md`, `START_HERE.md`, `docs/README.md`, and `ARCHIVE_INDEX.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0106 / OQ-0096 move into canon and FT-0107 / OQ-0097 become the live next gap.
- Release metadata and manifests to `rev0132`.
- This revision stays tight: one canon surface, one bibliography extension, narrow archive threading, no bulky retained artifacts.

## rev0131 — 2026-03-23

- Added `docs/20-world-design/research-reserve-reinstatement-fraud-recovery-limits-and-federated-shared-ledger-derivative-release-controls.md`.
- Fixed the next narrow research-governance seam in three parts:
  - decertified reserve cohorts now return only through a public `RRI-1` reinstatement-integrity object with fresh review, no-laundering continuity screening, public history carry, and a heightened non-default period,
  - fraud-late apportionment correction now runs through an `FRL-1` object with a single-satisfaction ceiling, good-faith downstream shields, improvement / preservation credits, and a short retro-recovery clock,
  - and cross-authority historical families now use an `FGL-1` federated-governance-ledger object with exchange agreements, provider-constraint carry, and one derivative-release registry spanning models, code, synthetic files, validation outputs, and other derived artifacts.
- Extended `docs/00-meta/bibliography.md` with current GovInfo, NIST, and Census sources on avoided-transfer recovery limits, managing cross-organization information exchanges, multi-agency restricted-use governance, and disclosure review for removable derived outputs including programs.
- Updated `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md`, `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0105 / OQ-0095 move into canon and FT-0106 / OQ-0096 become the live next gap.
- Release metadata and manifests to `rev0131`.
- This revision stays tight: one canon surface, one bibliography extension, narrow archive threading, no bulky retained artifacts.

## rev0130 — 2026-03-23

Summary: reserve probation, apportionment reopening finality, and shared privacy-budget governance.

Changes in this revision:
- Added `docs/20-world-design/research-reserve-probation-apportionment-reopening-finality-and-shared-privacy-budget-governance.md`, fixing a public `RPS-1` object for reserve watch / probation / restriction / decertification after repeated provisional use, a public `ARF-1` object that distinguishes any-reason, good-cause, and fraud-only reopening windows with a reliance bar for later split-successor correction, and a family-level `SBL-1` object that binds overlapping historical-analytics lanes to one shared privacy ledger with analyst segmentation and family-wide exhaustion states.
- Extended `docs/00-meta/bibliography.md` with `REF-0498` through `REF-0505` on AAHRPP probation / revocation and corrective-plan structure, SSA reopening and good-cause doctrine, NIST differential-privacy and de-identification governance, Census cumulative disclosure risk across related products, and project-specific restricted-use researcher authorization.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention reserve probation after repeated provisional use, explicit reopening finality, and shared privacy-ledger governance across linked analytics lanes.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0104 / OQ-0094 move into canon and FT-0105 / OQ-0095 become the live next gap.
- Release metadata and manifests to `rev0130`.

Why this counts:
- The archive had already fixed emergency provisional activation, contested apportionment review, and explicit analytics lanes, but not the escalation, finality, and shared-ledger layer needed once those mechanisms are used repeatedly.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing research-caution stack.
- It also keeps the next seam exact: reserve-cohort reinstatement after decertification, fraud-late apportionment restitution limits, and cross-authority shared-ledger federation plus derivative-release control.

## rev0128 — 2026-03-23

Summary: provisional reserve-cohort activation, contested apportionment review, and privacy-preserving historical analytics.

Changes in this revision:
- Added `docs/20-world-design/research-provisional-reserve-cohort-activation-contested-apportionment-review-and-privacy-preserving-historical-analytics.md`, fixing a short-clock `PRA-1` object for emergency reserve continuity before full accreditation, a written `CAR-1` correction route for materially wrong split-successor apportionment with conflict-screened review and bounded true-up, and a lane-specific `PHA-1` object for public aggregates, differentially private synthetic data, validation-service workflows, and enclave-mediated historical analytics.
- Extended `docs/00-meta/bibliography.md` with `REF-0490` through `REF-0497` on FDA emergency authorization, FDIC independent review and review-board structure, NIST differential-privacy budgeting and PET use-case evaluation, NIST enclave security, and Census validation-service plus restricted-use access patterns.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention provisional reserve continuity, correction-routable split-successor burden, and lane-governed historical analytics.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0103 / OQ-0093 move into canon and FT-0104 / OQ-0094 become the live next gap.
- Release metadata and manifests to `rev0128`.

Why this counts:
- The archive had already fixed accreditation, apportionment, and bulk-control doctrine, but not the emergency continuity path, correction route, and exact analytics-lane taxonomy that keep those mechanisms usable under time pressure, evidentiary change, and privacy-sensitive historical analysis.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing research-caution stack.
- It also keeps the next seam exact: reserve-cohort probation after provisional use, serial apportionment reopening finality, and privacy-budget exhaustion governance.

## rev0127 — 2026-03-23

Summary: reserve-cohort accreditation, multi-successor deficiency apportionment, and bulk historical-discovery controls.

Changes in this revision:
- Added `docs/20-world-design/research-reserve-cohort-accreditation-multi-successor-deficiency-apportionment-and-bulk-historical-discovery-controls.md`, fixing a public `RCA-1` accreditation object for external reserve cohorts with role scope, recurring full review, annual reporting, and event-reporting duty, a public `MDA-1` apportionment object that allocates inherited typed deficiency first by express assumption and then by assumed lane plus economic risk of loss with provisional joint carry for unresolved residue, and a public `BHD-1` control object that separates ordinary public lookup, registered rate-limited bulk harvest, scheduled public snapshots, and de-identified or enclave-style protected analytics.
- Extended `docs/00-meta/bibliography.md` with `REF-0475` through `REF-0489` on AAHRPP accreditation and required reports, NIST AI governance and monitoring, IRS / FDIC / NCUA successor-liability practice, ORCID visibility and public-data limits, Crossref rate-limited API and snapshot practice, and NIST de-identification patterns for query interfaces and protected enclaves.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention reserve-cohort accreditation, split-successor deficiency apportionment, and bulk historical-control defaults.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0102 / OQ-0092 move into canon and FT-0103 / OQ-0093 become the live next gap.
- Release metadata and manifests to `rev0127`.

Why this counts:
- The archive had already fixed correlated-failure reserve triggers, successor-carried default history, and live-first historical discovery defaults, but not the recurring qualification trace, split-successor apportionment rule, and bulk-control surface that keep those mechanisms usable under merger, partial succession, and large-scale public discovery.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing caution-governance stack.
- It also keeps the next seam exact: provisional reserve-cohort activation, contested apportionment review, and privacy-preserving historical analytics.

## rev0126 — 2026-03-23

Summary: correlated-failure reserve witnesses, default-discharge portability, and historical-branch discovery defaults.

Changes in this revision:
- Added `docs/20-world-design/research-correlated-failure-reserve-witnesses-default-discharge-portability-and-historical-branch-discovery.md`, fixing a public correlated-failure floor that forces an external reserve witness cohort rather than same-cluster substitution, a `DCP-1` carry object that keeps reserve-default history attached to the real continuing authority through merger or exit with bounded decay after clean cycles, and a `HAD-1` discovery object that makes large historical branch families resolve live-first by default without breaking exact historical resolution.
- Extended `docs/00-meta/bibliography.md` with `REF-0471` through `REF-0474` on NIST common-mode-failure diversity, CISA backup separation against shared hazards, FDIC substance-over-form merger continuity, and NCUA merger-transfer carry rules.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention external reserve triggers, successor-carried default history, and live-first historical discovery defaults.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0101 / OQ-0091 move into canon and FT-0102 / OQ-0092 become the live next gap.
- Release metadata and manifests to `rev0126`.

Why this counts:
- The archive had already fixed operator-independent replacement, chronic-default netting, and visible historical retirement, but not the correlated-failure trigger, successor-carry rule, and discovery default that keep those mechanisms usable under scale and organizational change.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing caution-governance stack.
- It also keeps the next seam exact: reserve-cohort accreditation, multi-successor deficiency apportionment, and bulk historical-discovery controls.

## rev0125 — 2026-03-23

Summary: witness-replacement independence, reciprocal-credit default netting, and historical-branch finalization doctrine.

Changes in this revision:
- Added `docs/20-world-design/research-witness-replacement-independence-default-netting-and-historical-branch-retirement.md`, fixing explicit operator-independence, comparable-competence, no-proxy, and forced-recovery tests for emergency witness substitution, a non-transferable typed deficiency ledger that nets chronic reciprocal-credit default only against future excess capacity, and a public distinction between `read-only-recoverable` and `historical-branch-retired` once rejoin fails.
- Extended `docs/00-meta/bibliography.md` with `REF-0465` through `REF-0470` on OHRP alternate-member comparability, quorum / no-proxy / conflict management, EPA automatic future-cycle make-up pressure, ICANN recoverable-versus-pending-delete lifecycle states, and IANA explicit deprecated / obsoleted labeling.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention witness-replacement independence, future-capacity default netting, and historical-branch retirement states.
- Tightened `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` so its formerly open seam now points to the new canon surface and advances the next gap.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0100 / OQ-0090 move into canon and FT-0101 / OQ-0091 become the live next gap.
- Release metadata and manifests to `rev0125`.

Why this counts:
- The archive had already fixed long-lived witness diversity, reciprocal-credit expiry, and visible rejoin-versus-retirement rules, but not the replacement-independence, chronic-default, and terminal-state layer needed once those mechanisms are stressed repeatedly.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing caution-governance stack.
- It also keeps the next seam exact: correlated-failure reserve witnesses, default-discharge portability, and historical-branch discovery defaults.

## rev0124 — 2026-03-23

Summary: supersession-graph witness diversity, reciprocal-credit expiry, and split-read-only rejoin doctrine.

Changes in this revision:
- Added `docs/20-world-design/research-supersession-graph-witness-diversity-reciprocal-credit-expiry-and-split-read-only-rejoin.md`, fixing witness-diverse quorum policy plus overlap rotation and sealed recovery-share custody for long-lived supersession-family signing, short expiry plus narrow public borrowing and anti-hoarding holding caps for reciprocal reserve credits, and a visible rejoin-versus-retirement rule once a contested family has already gone read-only.
- Extended `docs/00-meta/bibliography.md` with `REF-0456` through `REF-0464` on NIST key management and threshold cryptography, IETF cosigner / witness practice, EMAC mission-bounded mutual aid, EPA carry and make-up obligations, CARB holding limits, ORCID deprecation, and archival obsoletes-versus-updates discipline.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention witness-diverse graph signing, credit expiry / borrowing discipline, and visible read-only split convergence or retirement.
- Tightened `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` so its formerly open seam now points to the new canon surface and advances the next gap.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0099 / OQ-0089 move into canon and FT-0100 / OQ-0090 become the live next gap.
- Release metadata and manifests to `rev0124`.

Why this counts:
- The archive had already fixed signed graph-integrity checkpoints, typed heterogeneous reserve scoring, and divergence-threshold escalation, but not the witness-governance, credit-lifecycle, and post-freeze convergence rules that keep those mechanisms trustworthy over longer horizons.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing caution-governance stack.
- It also keeps the next seam exact: witness-replacement independence tests, chronic reciprocal-credit default netting, and failed-rejoin branch-retirement states.

## rev0123 — 2026-03-23

Summary: supersession-graph integrity proofs, heterogeneous reserve scoring, and pending-review divergence thresholds.

Changes in this revision:
- Added `docs/20-world-design/research-supersession-graph-integrity-heterogeneous-reserve-scoring-and-pending-review-divergence-thresholds.md`, fixing signed graph-integrity checkpoints with append-only proofs and propagation clocks, typed heterogeneous reserve scoring with bounded reciprocal credits, and a public escalation ladder from label-only continuity to no-new-writes or read-only routing once divergence becomes material.
- Extended `docs/00-meta/bibliography.md` with `REF-0449` through `REF-0455` on transparency proofs, data-integrity context handling, typed capability baselines, and machine-readable write-blocking / read-visible status states.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` so the new canon surface is listed as the current follow-on execution layer.
- Updated `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the archive-level overviews now mention integrity-checked supersession publication, heterogeneous reserve scoring, and divergence-threshold escalation.
- Tightened `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` so its formerly open seam now points to the new canon surface and advances the next gap.
- Updated `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0098 / OQ-0088 move into canon and FT-0099 / OQ-0089 become the live next gap.
- Release metadata and manifests to `rev0123`.

Why this counts:
- The archive had already fixed additive supersession graphs, reserve-default cure, and public pending-review labeling, but not the proof layer needed when several registries publish person-affecting state at once.
- The new surface keeps the archive tight: one canon document plus narrow threading across the existing caution-governance stack.
- It also keeps the next seam exact: witness diversity for graph signing, reciprocal-credit expiry / borrowing discipline, and read-only split rejoin doctrine.

## rev0122 — 2026-03-23

Compromise supersession graphs, reserve-default cure, and successor-promotion stay effects.

### Added
- `docs/20-world-design/research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md`, fixing additive supersession graphs for multi-generation compromise republications, a visible reserve-default cure ladder, and a public pending-review state while full stay remains exceptional during contested successor promotion.

### Changed
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, and `docs/README.md` to surface the new canon document in the archive's release and navigation layers.
- `docs/10-foundations/world-change-overview.md` and `docs/20-world-design/research-welfare-and-evaluation.md` so the research-governance overview now carries the new graph/default/pending-review doctrine.
- `docs/20-world-design/research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md` so it no longer names a solved seam as still-open and instead points to the new narrower frontier.
- `docs/00-meta/trajectory-map.md`, `FOLLOWTHROUGH-QUEUE.json`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` so FT-0097 / OQ-0087 move into canon and FT-0098 / OQ-0088 become the live next gap.
- `docs/00-meta/bibliography.md` with `REF-0440` through `REF-0448` for current Crossref, DataCite, EMAC, and ICANN materials used by the new canon surface.
- Release metadata and manifests to `rev0122`.

### Why this revision counts
- The prior layer already fixed visible post-compromise status, standing-capacity plus mission-cost burden sharing, and a bounded successor-promotion review route.
- The remaining open seam was narrower: what graph carries multi-generation republication history, what cure ladder governs reserve default or donation-based capture, and what public state should apply while successor-promotion review is pending.
- The new doctrine stays conservative by adapting existing typed-relationship, tombstone, reimbursement, dispute, and interim-relief patterns rather than inventing a maximal bespoke governance stack.
- The next gap is narrower again: supersession-graph integrity proofs and propagation deadlines, heterogeneous reserve scoring plus reciprocal credit, and divergence-threshold escalation from label-only continuity to no-new-writes or read-only routing.

## rev0121 — 2026-03-23

Compromise backfill / republication, reserve-pool burden sharing, and contested successor-promotion review.

### Added
- `docs/20-world-design/research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md`, giving the archive a compact execution doctrine for visible post-compromise status of already-issued outputs, a standing-capacity plus mission-cost burden-sharing formula for reserve systems, and a bounded reconsideration-plus-independent-review route for contested rescue-bridge promotion.

### Changed
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md` — indexed the new execution companion surface and refreshed the live revision summary around compromise backfill, burden sharing, and successor-promotion review.
- `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md` — updated the research-governance overview so the caution architecture now reaches visible post-compromise backfill discipline, reciprocal reserve cost-sharing, and bounded review of contested successor promotion.
- `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md` — now points its remaining next-gap language to the new execution companion surface on compromise backfill / republication, reserve-pool burden sharing, and contested successor-promotion review.
- `docs/00-meta/trajectory-map.md` — moved the compromise-backfill / burden-sharing / successor-review question from next-gap status into canon and surfaced the narrower next question on compromise supersession graphs, reserve-default cure, and successor-promotion stay effects.
- `docs/00-meta/bibliography.md` — extended the bibliography with `REF-0432` through `REF-0439`.
- `FOLLOWTHROUGH-QUEUE.json` — advanced `FT-0096` from `open` to `advanced-not-closed` and added the narrower follow-on task `FT-0097`.
- `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, `VERSION` — synchronized release metadata to the new current revision.

### Why this revision counts
- The archive had already fixed bounded compromise attestation and response, reserve-pool or mutual-aid minimums, and visible sunset-versus-promotion review for rescue bridges.
- But it still lacked a rule for what visible status should attach to already-issued compromised outputs, a compact formula distinguishing standby contribution from mission reimbursement in reserve systems, and a bounded challenge route for contested successor promotion.
- The new doctrine again imports conservative official ingredients rather than inventing bespoke machinery: Crossref and NISO status-bearing update practice, DataCite tombstones and version links, EMAC reimbursement and negotiated-cost discipline, RFC 8126 public-defensibility for expert review, and ICANN reconsideration plus independent-review timing and panel structure.
- The revision stays compact: one new canon surface, eight new bibliography entries, and narrow forward-threading across the relevant research-governance surfaces.
- The next gap is narrower again: compromise supersession graphs, reserve-default cure, and successor-promotion stay effects.

## rev0120 — 2026-03-23

- Added `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md`, giving the archive a compact execution doctrine for bounded public compromise attestation and emergency rotation, reserve-pool / mutual-aid minimums for substitute scarcity, and visible bridge sunset / renewal / canonical-successor promotion while retired namespaces stay retired.
- Extended `docs/00-meta/bibliography.md` with current NIST, HHS / OHRP, IETF / RFC Editor, DataCite, and ORCID materials on incident response, cooperative-review reliance, cross-roster comparability, deprecation and sunset signalling, successor designation, and breach notice.
- Updated `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md` — updated the research-governance overview so the caution architecture now reaches public compromise attestation, reserve-backed anti-capture substitution, and bridge successor-governance.
- Updated `docs/20-world-design/research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md` so it no longer names a solved next gap.
- Updated `docs/00-meta/trajectory-map.md` — moved the perturbation-compromise / reserve-pool / bridge-successor question from next-gap status into canon and surfaced the narrower next question on compromise backfill / republication, reserve-pool burden sharing, and contested successor-promotion review.
- Updated `FOLLOWTHROUGH-QUEUE.json` — advanced `FT-0095` from `open` to `advanced-not-closed` and added the narrower follow-on task `FT-0096`.
- Updated `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `SURFACE-STATUS.json`, and `REVISION-RECEIPT.json` for the new release surface.

Why this matters:
- The archive had already fixed bounded perturbation epochs, substitute anti-capture rotation, and rescue-bridge doctrine, but it still lacked a bounded public state for live compromise, a real capacity floor for simultaneous scarcity, and a lifecycle rule distinguishing temporary bridge from ordinary successor.
- The new doctrine stays narrow: it does not yet fix the exact retroactive relabel / withdrawal / republication duty for already-issued compromised outputs, the contribution formula that keeps reserve systems from free-riding or dominance, or the appeal route for contested promotion of a rescue bridge into the canonical successor path.
- The next gap is therefore narrower again: compromise backfill / republication, reserve-pool burden sharing, and contested successor-promotion review.

## rev0119 — 2026-03-23

Perturbation-family audit, substitute-pool anti-capture rotation, and retired-namespace rescue.

### Added
- `docs/20-world-design/research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md`, giving the archive a compact execution doctrine for bounded auditable perturbation epochs, anti-capture substitute-pool rotation with cooling-off and scarcity escalation, and rescue-bridge doctrine for fully retired namespaces.

### Changed
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md` — indexed the new execution companion surface and refreshed the live revision summary around perturbation-family audit, anti-capture substitute rotation, and retired-namespace rescue.
- `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md` — updated the research-governance overview so the caution architecture now reaches epoch-bound perturbation audit, substitute-pool anti-capture rotation, and rescue-bridge discipline for retired namespaces.
- `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md` — now points its remaining next-gap language to the new execution companion surface on perturbation-family audit, substitute-pool anti-capture rotation, and retired-namespace rescue.
- `docs/00-meta/trajectory-map.md` — moved the perturbation-family / anti-capture / rescue question from next-gap status into canon and surfaced the narrower next question on perturbation-compromise response, reserve-pool / mutual-aid minimums, and rescue-bridge sunset or canonical-successor doctrine.
- `docs/00-meta/bibliography.md` — extended the bibliography with `REF-0410` through `REF-0423`.
- `FOLLOWTHROUGH-QUEUE.json` — advanced `FT-0094` from `open` to `advanced-not-closed` and added the narrower follow-on task `FT-0095`.
- `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, `VERSION` — synchronized release metadata to the new current revision.

### Why this revision counts
- The archive had already fixed when perturbation should be preferred, how emergency external substitute appointments could be challenged without reopening the merits, and what replay / export / backfill duties survive once namespaces are closed-legacy or retired.
- But three narrower failures still remained: a perturbation family could still remain stable until accumulation and composition made it dangerous, a tiny substitute pool could still harden into a semi-permanent insider panel, and a retired namespace could still tempt institutions into in-place resurrection when a bridge would have preserved history.
- The new doctrine again adapts conservative official ingredients already visible elsewhere: ONS and Census materials on accumulation risk and principled evaluation, HHS / OHRP and U.S. Courts guidance on comparable substitutes and anti-concentration assignment, and IETF / IANA, ORCID, and DataCite practice on status-bearing registries, tombstones, and successor links.
- The revision stays tight: one new canon surface, fourteen new bibliography entries, and narrow forward-threading across the relevant research-governance surfaces.
- The next gap is narrower again: perturbation-compromise response, reserve-pool / mutual-aid minimums, and rescue-bridge sunset or canonical-successor doctrine.

## rev0118 — 2026-03-23

Perturbation preference, substitute-appointment review, and retired-namespace replay.

### Added
- `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md`, giving the archive a compact execution doctrine for declared perturbation when sparse recurring relay series need continuity plus anti-differencing protection, prompt process-bounded review of emergency external substitute appointments, and replay / export / backfill duties once namespaces are closed-legacy or retired.

### Changed
- `README.md`, `START_HERE.md`, `ARCHIVE_INDEX.md`, `docs/README.md` — indexed the new execution companion surface and refreshed the live revision summary around perturbation preference, appointment review, and retired-namespace persistence.
- `docs/10-foundations/world-change-overview.md`, `docs/20-world-design/research-welfare-and-evaluation.md` — updated the research-governance overview so the caution architecture now reaches declared perturbation, process-bounded substitute review, and replay-preserving namespace retirement.
- `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md` — now points its remaining next-gap language to the new execution companion surface on perturbation preference, substitute-appointment review, and retired-namespace replay / export / backfill.
- `docs/00-meta/trajectory-map.md` — moved the perturbation / appointment-review / replay question from next-gap status into canon and surfaced the narrower next question on perturbation-family audit, substitute-pool anti-capture rotation, and extraordinary rescue for fully retired namespaces.
- `docs/00-meta/bibliography.md` — extended the bibliography with `REF-0400` through `REF-0409`.
- `FOLLOWTHROUGH-QUEUE.json` — advanced `FT-0093` from `open` to `advanced-not-closed` and added the narrower follow-on task `FT-0094`.
- `SURFACE-STATUS.json`, `REVISION-RECEIPT.json`, `VERSION` — synchronized release metadata to the new current revision.

### Why this revision counts
- The archive had already fixed a conservative low-volume ladder, substitute-panel routing when local recusal exhausted the ordinary roster, and a closed-legacy cutover state.
- But it still lacked a rule for the cases where sparse recurring public series need both continuity and confidentiality, a review path for emergency substitute appointments that does not collapse into merits relitigation, and a retirement doctrine that keeps old namespaces historically readable.
- The new doctrine again imports conservative official ingredients rather than inventing a bespoke machinery: ONS perturbation methods, current written review and urgent-consideration procedures, recusal-timeliness discipline, and public machine-readable registry persistence with explicit successor or obsolescence links.
- The revision stays compact: one new canon surface, ten new bibliography entries, and narrow forward-threading across the relevant research-governance surfaces.
- The next gap is narrower again: perturbation-family audit, substitute-pool anti-capture rotation, and extraordinary rescue of fully retired namespaces.

## rev0117 — 2026-03-23

Low-volume-relay-thresholds-cross-roster-substitutes-and-closed-legacy-cutover revision.

### Added
- `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`, giving the archive a compact execution doctrine for low-volume protected-relay publication, reciprocal substitute-panel sourcing when local recusal exhausts the ordinary roster, and a closed-legacy cutover state for deprecated namespaces that overstay retirement review,
- fresh bibliography pressure from current CDC and ONS disclosure-control materials, HHS / OHRP alternate-and-quorum guidance, and current RFC practice showing that old registries can be closed to new entries while users are redirected to successor records.

### Changed
- refactored README, START_HERE, docs index, trajectory, queue, world-overview, research-welfare, and the prior relay-attestation execution surface so the archive no longer treats low-volume publication, panel-exhaustion routing, or post-window namespace cutover as merely future work,
- advanced the next gap from threshold / substitute / cutover basics to the narrower question of perturbation-grade publication, emergency substitute-appointment challenge, and replay / export semantics once namespaces become closed-legacy or retired.

### Why this revision counts
- it closes a live gap in the archive: the research caution layer already had bounded attestation objects, fixed merits quorum, full-step-out recusal, and migration windows, but it still lacked a compact answer for the exact months when disclosure risk is highest and staffing resilience is lowest,
- it sharpens the archive from “publish and review carefully” to the more operational rule that tiny protected-route volumes still require visible attestation, merits review cannot be completed by a locally exhausted conflicted body, and namespace deprecation must eventually become an actual cutover state,
- and it stays compact by adapting current disclosure-control, alternate-member, quorum-restoration, and registry-lifecycle materials rather than inventing a bespoke secrecy or parser constitution.

## rev0116 — 2026-03-23

Execution companion for the AI-person research caution architecture.

### Added
- `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md` — fixes the next narrow execution gap in the AI-person research caution stack: one bounded machine-readable protected-relay attestation object, explicit three-person merits quorum plus full-step-out recusal and substitute replacement for contested reconciliation panels, and visible no-new-use / compatibility-support / retirement-review windows for deprecated namespaces.

### Updated
- `README.md` — added the new execution companion surface and refreshed the revision summary so the archive no longer treats attestation-object design, panel quorum / recusal, and namespace migration windows as merely future work.
- `START_HERE.md` — added the new execution companion surface to the must-read ladder and rewrote the revision summary around object-carrying relay publication, panel discipline, and migration clocks.
- `ARCHIVE_INDEX.md` — indexed the new execution companion surface.
- `docs/README.md` — listed the new execution companion surface in the research-governance cluster.
- `docs/10-foundations/world-change-overview.md` — made the research-governance overview more operational by naming one bounded relay attestation object, explicit contested-panel quorum / recusal, and visible namespace migration windows.
- `docs/20-world-design/research-welfare-and-evaluation.md` — updated the research-stack overview so the caution architecture now reaches all the way to object publication, panel discipline, and migration clocks.
- `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md` — pointed the previous governance companion surface at the new execution companion and advanced the next gap to low-volume suppression, substitute-panel sourcing, and hard cutover questions.
- `docs/20-world-design/research-family-scope-propagation-tombstones-and-screened-filer-clearance.md`
- `docs/20-world-design/research-propagation-lag-markers-tombstone-successor-semantics-and-screened-bypass-review.md`
- `docs/20-world-design/research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md`
- `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md`
- `docs/20-world-design/research-reactivation-evidence-floors-anonymous-contradiction-summaries-and-post-disposition-filing-rules.md`
- `docs/20-world-design/research-slice-family-reactivation-correction-route-and-serial-filing-escalation.md`
- `docs/20-world-design/research-phased-reactivation-participant-contradiction-and-anti-flood-reply-controls.md` — refreshed stale “next gap” language so the newly solved attestation-object / panel-quorum / migration-window layer is no longer described as future work.
- `docs/00-meta/trajectory-map.md` — moved the relay-attestation-object / contested-panel-quorum / deprecated-namespace-migration-window question from next-gap status into canon and surfaced the narrower next question on low-volume suppression thresholds, substitute-panel sourcing, and hard cutover or parser-guarantee rules for overstayed deprecated namespaces.
- `docs/00-meta/bibliography.md` — extended the bibliography with `REF-0387` through `REF-0392` on recusal, disclosure, substitute handling, quorum, and committee conflict practice.
- `FOLLOWTHROUGH-QUEUE.json` — advanced `FT-0091` from `open` to `advanced-not-closed` and added the narrower follow-on task `FT-0092`.
- `SURFACE-STATUS.json` — advanced the surface state to object-carrying, panel-disciplined, and migration-windowed research-governance execution.
- `REVISION-RECEIPT.json` — recorded the new revision and its narrower remaining gap.

### Why this revision matters
- The archive had already fixed registry governance, contested review, and privacy-preserving aggregate relay-capacity attestation, but it still lacked one exact relay object, one explicit panel-discipline rule, and one visible namespace migration clock.
- This revision closes that operational gap without bloating the archive: one new canon surface, six new bibliography entries, and narrow forward-threading across the relevant research-governance surfaces.
- The next gap is narrower again: low-volume relay-attestation suppression thresholds, substitute-panel sourcing when recusals exhaust the ordinary roster, and hard cutover or parser-guarantee rules for deprecated namespaces that overstay the migration window.

## rev0188 — witnessed drill gates and downstream recall/fork aftercare

- Added `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` to prevent synthetic or host self-attested drills from upgrading reliance.
- Added `schemas/live-drill-execution-packet.schema.json`, `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`, and `NF-PLAYBOOK-2026-0003`.
- Compacted RTC-06 into deprecation/end-of-life governance and deprecation drills.
- Added `schemas/downstream-recall-and-fork-aftercare-record.schema.json`, `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json`, `NF-DEPRECATION-2026-0002`, and a downstream recall drill.
- Updated fixture suite/report to 88 entries and kept reliance stayed for self-attested live drills or unresolved downstream mirrors.
- Added `tools/audit_downstream_recall_and_live_drill.py` and active rev0188 catalog/dependency/rights/registry maps.

## rev0189 — welfare research safeguards and RTC-01 compaction

- Added `schemas/welfare-research-safeguard-record.schema.json` and `examples/welfare-research-safeguard-record-distress-eval.json`.
- Added `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json` and wired it into the negative suite/report.
- Added `examples/drill-after-action-welfare-safeguard-distress-eval.json`.
- Folded RTC-01 into `docs/20-world-design/research-welfare-and-evaluation.md` while preserving supported-consent, minimal-risk, protocol-registration, and anti-signal-gaming constraints.
- Added `tools/audit_welfare_research_safeguards.py` and wired it into lint.
- Updated active catalog, dependency, rights-domain, registry, compaction, queue, status, receipt, context, and manifest surfaces for rev0189.


## rev0191 — WRSR protocol backfill and external receipt simulation

- Added `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`.
- Added WRSR operational hook schema/example and backfilled WRSR references into agent-handshake and incident examples.
- Added external receipt simulation bundle schema/example while preserving stayed reliance for simulated artifacts.
- Added negative fixtures for skipped WRSR hooks and simulated receipts mislabeled as live evidence.
- Added `tools/audit_protocol_wrsr_receipt_simulation.py` and active rev0191 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0190-WRSR-PROTOCOL-BACKFILL`; advanced but did not close `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS`.

## rev0192 — external receipt intake and WRSR exercise outcome

- Added `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`.
- Added external receipt intake schema/example and fixture to block defective or simulated receipt records from satisfying quorum.
- Added WRSR live-exercise outcome schema/example and fixture to block hook firing from being treated as WRSR closure.
- Linked receipt intake and WRSR outcome references into the live drill packet while preserving stayed reliance and zero independent receipts.
- Added `tools/audit_receipt_intake_wrsr_outcome.py` and active rev0192 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0192-EXTERNAL-RECEIPT-INTAKE-OBJECTIZATION`; advanced but did not close live receipt collection or WRSR witnessed exercise evidence.

## rev0193 — representative/RERB receipt chain and quorum ledger

- Added `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`.
- Added `schemas/external-receipt-quorum-ledger.schema.json` and the representative/RERB dry-run quorum ledger example.
- Added representative-contact and independent-review receipt-intake examples plus a WRSR dry-run outcome that keeps closure stayed.
- Added negative fixtures blocking dry-run receipt quorum from being counted as live and blocking representative/RERB dry-run participation from being mislabeled as WRSR closure.
- Added `tools/audit_receipt_quorum_wrsr_chain.py` and active rev0193 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN`; advanced but did not close actual external receipt collection or WRSR result-return closure.

## rev0197 — actual-intake import gate and failed-gate public summary

- Added `docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md`.
- Added `schemas/actual-receipt-import-gate.schema.json` and `examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json` to block actual-shaped fixture records from changing the live receipt floor.
- Added `schemas/failed-gate-public-summary.schema.json` and `examples/failed-gate-public-summary-response-conversion-batch.json` to publish defective, declined, expired, and fixture-disqualified non-satisfaction without exposing sealed details.
- Added `examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json` and `examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json`.
- Added fixtures `NF-PLAYBOOK-2026-0014` through `NF-PLAYBOOK-2026-0016` for actual-state-field import laundering, omitted failed-gate branches, and no-response-as-waiver laundering.
- Added `tools/audit_actual_import_failed_gate_summary.py` and active rev0197 catalog/dependency/rights/registry/compaction maps.
- Advanced actual import work without closing live receipt collection; `independent_receipts_present` remains zero.

## rev0200 — class-local import replay and quorum firewall

- Added `docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md`.
- Added `schemas/live-class-local-import-replay.schema.json` and `examples/live-class-local-import-replay-result-return-positive-path-projection.json`.
- Added `examples/quorum-recomputation-report-class-local-projection-rev0200.json` and `examples/failed-gate-public-summary-class-local-projection-firewall.json`.
- Added fixtures `NF-PLAYBOOK-2026-0023` through `NF-PLAYBOOK-2026-0025` to block scenario-delta import, one-class cross-critical quorum, and missing-class public-shell omission.
- Added `tools/audit_live_class_local_import_firewall.py` and `tools/audit_frontdoor_revision_sync.py` and wired both into lint.
- Updated active catalog, dependency, rights-domain, registry, compaction, queue, status, receipt, live drill packet, and front-door surfaces for rev0200.
- Advanced actual counterparty response collection without closing it; `independent_receipts_present` remains zero.
