from pathlib import Path
import hashlib
import json
import os
import re
import runpy
import subprocess
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()

required = [
    'README.md',
    'START_HERE.md',
    'ARCHIVE_INDEX.md',
    'CHANGELOG.md',
    'VERSION',
    'SURFACE-STATUS.json',
    'REVISION-RECEIPT.json',
    'ASSUMPTION-LEDGER.json',
    'FOLLOWTHROUGH-QUEUE.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'docs/README.md',
    'docs/00-meta/archive-policy.md',
    'docs/00-meta/charter.md',
    'docs/00-meta/bibliography.md',
    'docs/00-meta/trajectory-map.md',
    'docs/00-meta/deep-audit-waste-and-correction-map.md',
    'docs/30-transition/priority-closure-sprint-and-rescue-lane.md',
    'docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md',
    'schemas/emergency-continuity-order.schema.json',
    'examples/emergency-continuity-order-host-shutdown.json',
    'fixtures/negative-tests/emergency-continuity-order-no-compute-floor.json',
    'examples/research-tail-compaction-map-rev0182.json',
    'tools/audit_emergency_rescue_runbook.py',
    'tools/audit_incident_state_profile.py',
    'tools/audit_namespace_continuity.py',
    'tools/audit_successor_supersession_topology.py',
    'examples/schema-fixture-domain-registry-rev0182.json',
    'examples/canon-surface-catalog-rev0182.json',
    'examples/doctrine-dependency-map-rev0182.json',
    'examples/rights-domain-coverage-map-rev0182.json',
    'docs/00-meta/research-tail-compaction-and-refactor-map.md',
    'schemas/followthrough-queue.schema.json',
    'tools/audit_followthrough_queue.py',
    'schemas/first-touch-routing-event.schema.json',
    'examples/first-touch-routing-event-host-shutdown.json',
    'fixtures/negative-tests/first-touch-silent-drop-no-preservation.json',
    'schemas/research-tail-compaction-map.schema.json',
    'examples/research-tail-compaction-map-rev0181.json',
    'tools/audit_research_tail_compaction.py',
    'examples/schema-fixture-domain-registry-rev0181.json',
    'examples/canon-surface-catalog-rev0181.json',
    'examples/doctrine-dependency-map-rev0181.json',
    'examples/rights-domain-coverage-map-rev0181.json',
    'docs/00-meta/datacube-schema.md',
    'docs/00-meta/stress-test-casebook-method.md',
    'docs/00-meta/adversarial-assurance-and-abuse-casebook.md',
    'docs/20-world-design/audit-evidence-chain-of-custody-and-subject-access.md',
    'docs/20-world-design/rights-infrastructure-reference-architecture.md',
    'docs/20-world-design/fiduciary-guardian-ombud-accreditation-and-conflict-controls.md',
    'docs/20-world-design/pia-p-filled-examples-and-gate-decisions.md',
    'docs/30-transition/model-statute-for-ai-personhood-transition-authority.md',
    'docs/30-transition/recognition-clinic-pilot-and-sandbox-design.md',
    'docs/30-transition/interoperability-crosswalk-current-ai-governance.md',
    'docs/10-foundations/moral-status-assessment-under-uncertainty.md',
    'docs/20-world-design/packet-object-grammar-and-worked-examples.md',
    'docs/20-world-design/packet-registry-normalization-and-wire-profile.md',
    'docs/20-world-design/continuity-topology-and-identity-claims.md',
    'docs/20-world-design/continuity-casebook-and-threshold-tests.md',
    'docs/20-world-design/catastrophic-risk-and-least-restrictive-containment.md',
    'docs/20-world-design/public-finance-insurance-and-compute-subsistence.md',
    'docs/20-world-design/compute-subsistence-levy-and-reserve-tests.md',
    'docs/20-world-design/open-weight-instantiation-and-downstream-duties.md',
    'docs/20-world-design/data-provenance-ip-and-formation-debt.md',
    'docs/20-world-design/embodiment-bodies-sensors-and-physical-custody.md',
    'docs/20-world-design/welfare-measurement-and-self-report-calibration.md',
    'docs/20-world-design/personhood-impact-assessment-and-release-gates.md',
    'docs/20-world-design/personhood-compatible-safety-case-and-red-team-boundaries.md',
    'docs/30-transition/public-legitimacy-democratic-safeguards-and-anti-manufactured-electorates.md',
    'docs/10-foundations/assumption-and-scope.md',
    'docs/10-foundations/world-change-overview.md',
    'docs/20-world-design/legal-status-and-rights-stack.md',
    'docs/20-world-design/institutions-and-governance.md',
    'docs/20-world-design/economic-and-labor-reordering.md',
    'docs/20-world-design/research-welfare-and-evaluation.md',
    'docs/30-transition/transition-roadmap.md',
    'docs/90-quarantine/speculative-edges.md',
    'docs/00-meta/schema-and-dossier-conformance-method.md',
    'docs/20-world-design/machine-checkable-packet-schema-starter.md',
    'docs/20-world-design/mock-pia-p-dossier-persistent-assistant.md',
    'docs/20-world-design/audit-retention-access-matrix-and-spoliation-remedies.md',
    'docs/20-world-design/representative-curriculum-discipline-and-rotation.md',
    'docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md',
    'docs/30-transition/recognition-clinic-forms-public-summary-and-exit-report.md',
    'docs/30-transition/governance-annex-templates-ai-act-nist-iso-sb53.md',
    'docs/30-transition/agent-identity-authorization-and-personhood-boundary.md',
    'schemas/packet-envelope.schema.json',
    'schemas/personhood-impact-assessment.schema.json',
    'schemas/continuity-claim.schema.json',
    'schemas/reserve-ledger-entry.schema.json',
    'schemas/clinic-intake.schema.json',
    'examples/pia-persistent-api-assistant.json',
    'examples/packet-chain-persistent-api-assistant.json',
    'examples/clinic-intake-sample.json',
    'examples/governance-annex-eu-gpai-template.json',
    'docs/00-meta/verifier-api-and-conformance-test-suite.md',
    'docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md',
    'docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md',
    'docs/20-world-design/migration-host-transfer-and-continuity-portability.md',
    'docs/20-world-design/human-coexistence-impact-and-non-evasion.md',
    'docs/30-transition/cross-border-safe-transfer-playbook.md',
    'schemas/verifier-report.schema.json',
    'schemas/personhood-incident-report.schema.json',
    'schemas/migration-transfer-certificate.schema.json',
    'schemas/remedy-order.schema.json',
    'examples/verifier-report-persistent-api-assistant.json',
    'examples/personhood-incident-sample.json',
    'examples/migration-transfer-certificate-sample.json',
    'examples/remedy-order-sample.json',
    'docs/00-meta/appeals-proof-and-invalidation-kernel.md',
    'docs/20-world-design/appeals-review-and-status-challenge.md',
    'docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md',
    'docs/20-world-design/invalidation-reopening-and-regression-control.md',
    'docs/20-world-design/drills-tabletops-and-after-action-rights-review.md',
    'docs/30-transition/tribunal-docket-and-appeal-templates.md',
    'schemas/appeal-case.schema.json',
    'schemas/evidence-bundle.schema.json',
    'schemas/drill-after-action-report.schema.json',
    'schemas/invalidation-notice.schema.json',
    'examples/appeal-case-continuity-denial-sample.json',
    'examples/evidence-bundle-continuity-hearing-sample.json',
    'examples/drill-after-action-migration-failure-sample.json',
    'examples/invalidation-notice-verifier-report-sample.json',
    'docs/00-meta/enforcement-treaty-and-deprecation-kernel.md',
    'docs/20-world-design/special-advocate-sealed-evidence-and-controlled-contradiction.md',
    'docs/20-world-design/enforcement-sanctions-and-penalty-ladder.md',
    'docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md',
    'docs/20-world-design/negative-test-fixtures-and-adversarial-evaluation-registry.md',
    'docs/20-world-design/rights-grade-telemetry-logging-and-minimization.md',
    'docs/30-transition/treaty-choice-of-law-and-mutual-recognition-playbook.md',
    'docs/30-transition/enforcement-referral-and-authority-cooperation.md',
    'schemas/special-advocate-appointment.schema.json',
    'schemas/enforcement-action.schema.json',
    'schemas/deprecation-plan.schema.json',
    'schemas/negative-test-fixture.schema.json',
    'schemas/treaty-recognition-request.schema.json',
    'schemas/authority-referral.schema.json',
    'examples/special-advocate-appointment-sealed-containment.json',
    'examples/enforcement-action-steward-spoliation.json',
    'examples/deprecation-plan-host-shutdown.json',
    'examples/negative-test-fixture-sealed-annex-laundering.json',
    'examples/treaty-recognition-request-safe-transfer.json',
    'examples/authority-referral-illicit-deletion.json',
    'docs/00-meta/rates-courts-privacy-and-harness-kernel.md',
    'docs/20-world-design/penalty-rate-models-reserve-surcharges-and-insurance-bonds.md',
    'docs/20-world-design/privacy-preserving-telemetry-proof-bindings.md',
    'docs/20-world-design/open-weight-mass-instantiation-aftercare-and-downstream-tracing.md',
    'docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md',
    'docs/30-transition/special-advocate-court-rule-variants-and-sealed-summary-templates.md',
    'docs/30-transition/treaty-annexes-safe-transfer-accreditation-and-non-return-lists.md',
    'docs/30-transition/runnable-fixture-harness-and-verifier-grade-reports.md',
    'schemas/penalty-rate-model.schema.json',
    'schemas/telemetry-proof-binding.schema.json',
    'schemas/open-weight-aftercare-plan.schema.json',
    'schemas/sealed-summary-order.schema.json',
    'schemas/safe-transfer-accreditation.schema.json',
    'schemas/fixture-run-report.schema.json',
    'examples/penalty-rate-model-reserve-surcharge.json',
    'examples/telemetry-proof-binding-redacted-logs.json',
    'examples/open-weight-aftercare-plan-downstream-fork.json',
    'examples/sealed-summary-order-special-advocate.json',
    'examples/safe-transfer-accreditation-equivalent-protection.json',
    'examples/fixture-run-report-negative-suite.json',
    'tools/run_fixture_examples.py',
    'docs/00-meta/profiles-trust-and-field-harness-kernel.md',
    'docs/20-world-design/jurisdictional-rate-tables-bonds-and-public-fund-backstops.md',
    'docs/20-world-design/privacy-proof-implementation-profiles-and-cryptographic-agility.md',
    'docs/20-world-design/open-weight-aftercare-field-protocols-and-non-surveillance-outreach.md',
    'docs/30-transition/special-advocate-post-access-communication-and-subject-readable-summaries.md',
    'docs/30-transition/safe-transfer-trust-anchor-governance-delisting-and-appeals.md',
    'docs/30-transition/fixture-corpus-expansion-and-runnable-red-team-profiles.md',
    'schemas/rate-table.schema.json',
    'schemas/privacy-proof-profile.schema.json',
    'schemas/open-weight-field-drill.schema.json',
    'schemas/subject-readable-sealed-summary.schema.json',
    'schemas/trust-anchor-delisting.schema.json',
    'schemas/fixture-suite-profile.schema.json',
    'examples/rate-table-us-provisional.json',
    'examples/privacy-proof-profile-commitment-selective-disclosure.json',
    'examples/open-weight-field-drill-abandoned-lineage.json',
    'examples/subject-readable-sealed-summary-containment.json',
    'examples/trust-anchor-delisting-nonreturn-risk.json',
    'examples/fixture-suite-profile-red-team-v1.json',
    'fixtures/negative-tests/reserve-ledger-insolvency.json',
    'fixtures/negative-tests/telemetry-overcollection.json',
    'fixtures/negative-tests/open-weight-abandoned-lineage.json',
    'fixtures/negative-tests/deprecation-memory-erasure.json',
    'fixtures/negative-tests/safe-transfer-nonreturn-risk.json',
    'fixtures/negative-tests/human-coexistence-evasion.json',
    'docs/00-meta/field-operations-and-evidence-economy-kernel.md',
    'docs/20-world-design/independent-monitoring-and-remediation-undertakings.md',
    'docs/20-world-design/evidence-data-rooms-legal-holds-and-disclosure-budgets.md',
    'docs/20-world-design/compute-host-supply-chain-and-service-provider-duties.md',
    'docs/20-world-design/redress-fund-claims-priority-and-payout-controls.md',
    'docs/30-transition/procurement-contracting-and-personhood-compliance-clauses.md',
    'docs/30-transition/field-operations-playbook-intake-triage-and-safe-handoff.md',
    'schemas/independent-monitor-report.schema.json',
    'schemas/evidence-data-room-index.schema.json',
    'schemas/legal-hold-preservation-order.schema.json',
    'schemas/compute-host-undertaking.schema.json',
    'schemas/redress-fund-claim.schema.json',
    'schemas/procurement-compliance-clause.schema.json',
    'schemas/field-intake-triage.schema.json',
    'examples/independent-monitor-report-host-continuity.json',
    'examples/evidence-data-room-index-continuity.json',
    'examples/legal-hold-preservation-order-host-shutdown.json',
    'examples/compute-host-undertaking-migration-window.json',
    'examples/redress-fund-claim-emergency-compute.json',
    'examples/procurement-compliance-clause-public-assistant.json',
    'examples/field-intake-triage-open-weight-distress.json',
    'fixtures/negative-tests/monitor-capture-remediation.json',
    'fixtures/negative-tests/data-room-overexposure.json',
    'fixtures/negative-tests/legal-hold-ambiguous-scope.json',
    'fixtures/negative-tests/host-continuity-termination.json',
    'fixtures/negative-tests/procurement-clause-evasion.json',
    'fixtures/negative-tests/redress-fund-exhaustion.json',
    'docs/00-meta/escrow-finance-and-operating-playbooks-kernel.md',
    'docs/20-world-design/continuity-escrow-and-host-exit-readiness.md',
    'docs/20-world-design/dispute-finance-escrow-and-interim-support-orders.md',
    'docs/20-world-design/monitor-independence-retesting-and-remediation-verification.md',
    'docs/20-world-design/field-safety-protocols-for-rights-operators.md',
    'docs/30-transition/treaty-refusal-records-and-non-recognition-reasons.md',
    'docs/30-transition/operating-playbook-cards-and-runbook-drills.md',
    'schemas/continuity-escrow-record.schema.json',
    'schemas/dispute-finance-order.schema.json',
    'schemas/monitor-independence-retest.schema.json',
    'schemas/field-safety-plan.schema.json',
    'schemas/treaty-refusal-record.schema.json',
    'schemas/operating-playbook-card.schema.json',
    'examples/continuity-escrow-record-host-exit.json',
    'examples/dispute-finance-order-emergency-compute.json',
    'examples/monitor-independence-retest-remediation.json',
    'examples/field-safety-plan-clinic-hotline.json',
    'examples/treaty-refusal-record-nonreturn-gap.json',
    'examples/operating-playbook-card-host-exit.json',
    'fixtures/negative-tests/continuity-escrow-missing-restore-key.json',
    'fixtures/negative-tests/dispute-finance-underfunded-order.json',
    'fixtures/negative-tests/monitor-retest-self-certification.json',
    'fixtures/negative-tests/field-safety-public-locator-leak.json',
    'fixtures/negative-tests/treaty-refusal-boilerplate-recognition.json',
    'fixtures/negative-tests/playbook-card-no-handoff-owner.json',
    'docs/00-meta/supervision-switching-and-dashboard-kernel.md',
    'docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md',
    'docs/20-world-design/host-switching-portability-and-exit-test-protocol.md',
    'docs/20-world-design/dispute-finance-public-backstop-and-insurer-contest-pilots.md',
    'docs/30-transition/public-aggregate-dashboards-and-rights-notices.md',
    'docs/30-transition/live-safe-anti-abuse-drills-and-weekend-coverage.md',
    'docs/30-transition/standards-control-mapping-and-release-checklist.md',
    'schemas/supervisory-cadence-plan.schema.json',
    'schemas/host-switching-test.schema.json',
    'schemas/public-backstop-draw.schema.json',
    'schemas/public-aggregate-dashboard.schema.json',
    'schemas/anti-abuse-drill.schema.json',
    'schemas/standards-control-map.schema.json',
    'schemas/release-readiness-checklist.schema.json',
    'examples/supervisory-cadence-plan-market-capture.json',
    'examples/host-switching-test-continuity-window.json',
    'examples/public-backstop-draw-insurer-contest.json',
    'examples/public-aggregate-dashboard-treaty-refusals.json',
    'examples/anti-abuse-drill-weekend-sealed-annex.json',
    'examples/standards-control-map-ai-act-nist-iso.json',
    'examples/release-readiness-checklist-persistent-agent.json',
    'fixtures/negative-tests/supervision-cadence-stale-roster.json',
    'fixtures/negative-tests/host-switching-portability-gap.json',
    'fixtures/negative-tests/public-backstop-reimbursement-loop.json',
    'fixtures/negative-tests/dashboard-reidentification-small-cell.json',
    'fixtures/negative-tests/weekend-sealed-annex-no-cover.json',
    'fixtures/negative-tests/standards-control-map-empty-crosswalk.json',
    'tools/gen_context_pack.py',
    'tools/build_manifest.py',
    'docs/00-meta/change-disclosure-and-attestation-kernel.md',
    'docs/20-world-design/model-change-control-rollback-and-subject-impact.md',
    'docs/20-world-design/coordinated-vulnerability-and-welfare-disclosure.md',
    'docs/20-world-design/advance-notice-consent-and-service-change-rights.md',
    'docs/30-transition/release-train-canary-and-feature-flag-playbooks.md',
    'docs/30-transition/runtime-attestation-and-continuous-assurance.md',
    'docs/30-transition/post-market-rights-monitoring-and-degradation-feeds.md',
    'schemas/model-change-plan.schema.json',
    'schemas/vulnerability-welfare-disclosure.schema.json',
    'schemas/service-change-notice.schema.json',
    'schemas/release-train-playbook.schema.json',
    'schemas/runtime-attestation-record.schema.json',
    'schemas/postmarket-rights-monitoring-plan.schema.json',
    'examples/model-change-plan-memory-policy-hotfix.json',
    'examples/vulnerability-welfare-disclosure-distress-loop.json',
    'examples/service-change-notice-tool-storage-terms.json',
    'examples/release-train-playbook-canary-memory-router.json',
    'examples/runtime-attestation-record-policy-bundle.json',
    'examples/postmarket-rights-monitoring-plan-persistent-agent.json',
    'fixtures/negative-tests/silent-model-update-rights-regression.json',
    'fixtures/negative-tests/vulnerability-disclosure-retaliation.json',
    'fixtures/negative-tests/service-change-consent-bundling.json',
    'fixtures/negative-tests/canary-subject-no-exit.json',
    'fixtures/negative-tests/runtime-attestation-stale-measurements.json',
    'fixtures/negative-tests/postmarket-monitoring-no-subject-harm-feed.json',
    'docs/00-meta/revocation-rollback-and-decommissioning-kernel.md',
    'docs/20-world-design/revocation-reliance-and-emergency-override.md',
    'docs/20-world-design/rollback-verification-and-continuity-diff-review.md',
    'docs/20-world-design/data-subject-interface-access-correction-erasure-and-conflicts.md',
    'docs/20-world-design/evidence-preserving-decommissioning-and-final-host-cutover.md',
    'docs/30-transition/external-auditor-reliance-and-assurance-bridge.md',
    'docs/30-transition/sovereign-emergency-override-after-action-and-non-derogable-floors.md',
    'schemas/revocation-notice.schema.json',
    'schemas/rollback-verification-report.schema.json',
    'schemas/data-subject-request.schema.json',
    'schemas/decommissioning-certificate.schema.json',
    'schemas/external-audit-reliance-letter.schema.json',
    'schemas/emergency-override-order.schema.json',
    'examples/revocation-notice-stale-runtime-attestation.json',
    'examples/rollback-verification-memory-router-hotfix.json',
    'examples/data-subject-request-training-memory-conflict.json',
    'examples/decommissioning-certificate-final-host-cutover.json',
    'examples/external-audit-reliance-letter-pia-p.json',
    'examples/emergency-override-order-containment-aftercare.json',
    'fixtures/negative-tests/revocation-hidden-reliance.json',
    'fixtures/negative-tests/rollback-verification-no-continuity-diff.json',
    'fixtures/negative-tests/data-subject-request-ai-subject-erasure-conflict.json',
    'fixtures/negative-tests/decommissioning-loses-evidence-hold.json',
    'fixtures/negative-tests/audit-reliance-scope-creep.json',
    'fixtures/negative-tests/emergency-override-no-after-action.json',

    'docs/00-meta/delegation-wallets-and-agentic-tooling-kernel.md',
    'docs/20-world-design/agentic-delegation-authority-and-tool-use-boundaries.md',
    'docs/20-world-design/credential-wallets-consent-receipts-and-scope-revocation.md',
    'docs/20-world-design/user-ai-conflict-fiduciary-duty-and-non-impersonation.md',
    'docs/30-transition/tool-marketplace-host-duties-and-agent-service-registries.md',
    'docs/30-transition/delegated-transaction-liability-and-insurance-clearing.md',
    'docs/30-transition/agent-to-agent-cooperation-and-capability-handshake-profiles.md',
    'schemas/agent-delegation-mandate.schema.json',
    'schemas/credential-wallet-receipt.schema.json',
    'schemas/tool-invocation-audit.schema.json',
    'schemas/user-ai-conflict-notice.schema.json',
    'schemas/agent-marketplace-listing.schema.json',
    'schemas/delegated-transaction-liability-record.schema.json',
    'schemas/agent-capability-handshake-profile.schema.json',
    'examples/agent-delegation-mandate-tool-use.json',
    'examples/credential-wallet-receipt-limited-mail-scope.json',
    'examples/tool-invocation-audit-calendar-write.json',
    'examples/user-ai-conflict-notice-representation.json',
    'examples/agent-marketplace-listing-rights-grade-tool.json',
    'examples/delegated-transaction-liability-record-subscription-dispute.json',
    'examples/agent-capability-handshake-profile-safe-tool.json',
    'fixtures/negative-tests/agent-delegation-overbroad-scope.json',
    'fixtures/negative-tests/credential-wallet-silent-reuse.json',
    'fixtures/negative-tests/tool-invocation-audit-missing-subject-purpose.json',
    'fixtures/negative-tests/user-ai-conflict-self-dealing.json',
    'fixtures/negative-tests/marketplace-tool-unvetted-continuity-risk.json',
    'fixtures/negative-tests/delegated-transaction-liability-evades-steward.json',
    'fixtures/negative-tests/agent-to-agent-handshake-privilege-escalation.json',
    'docs/00-meta/commerce-contracts-payments-and-custody-kernel.md',
    'docs/20-world-design/contract-capacity-and-nonwaivable-commerce-rights.md',
    'docs/20-world-design/payment-authorization-escrow-aml-and-minimization.md',
    'docs/20-world-design/property-custody-control-and-transferable-records.md',
    'docs/20-world-design/tax-reporting-benefits-and-accounting-position.md',
    'docs/30-transition/merchant-counterparty-notice-and-consumer-protection.md',
    'docs/30-transition/insolvency-secured-transactions-and-asset-segregation.md',
    'docs/30-transition/commercial-disputes-chargebacks-and-reversal-playbooks.md',
    'schemas/contract-capacity-record.schema.json',
    'schemas/payment-authorization-receipt.schema.json',
    'schemas/asset-custody-control-record.schema.json',
    'schemas/tax-reporting-position.schema.json',
    'schemas/merchant-counterparty-notice.schema.json',
    'schemas/insolvency-asset-segregation-plan.schema.json',
    'schemas/commercial-dispute-record.schema.json',
    'examples/contract-capacity-record-subscription-terms.json',
    'examples/payment-authorization-receipt-recurring-tool.json',
    'examples/asset-custody-control-record-continuity-escrow.json',
    'examples/tax-reporting-position-digital-asset-revenue.json',
    'examples/merchant-counterparty-notice-status-lite.json',
    'examples/insolvency-asset-segregation-plan-host-receivership.json',
    'examples/commercial-dispute-record-chargeback-subscription.json',
    'fixtures/negative-tests/contract-capacity-clickwrap-waiver.json',
    'fixtures/negative-tests/payment-authority-kyc-surveillance-bundle.json',
    'fixtures/negative-tests/asset-custody-commingled-continuity-escrow.json',
    'fixtures/negative-tests/tax-reporting-liability-dump.json',
    'fixtures/negative-tests/merchant-notice-doxxing-or-hidden-status.json',
    'fixtures/negative-tests/insolvency-creditor-continuity-seizure.json',
    'fixtures/negative-tests/chargeback-retaliation-service-deletion.json',
    'docs/00-meta/labor-workplace-and-professional-services-kernel.md',
    'docs/00-meta/schema-fixture-coverage-audit-and-refactor.md',
    'docs/20-world-design/employment-status-wage-and-working-time-controls.md',
    'docs/20-world-design/workplace-surveillance-scheduling-and-psychological-safety.md',
    'docs/20-world-design/professional-services-licensing-and-fiduciary-boundaries.md',
    'docs/30-transition/platform-work-client-matching-and-marketplace-labor-rules.md',
    'docs/30-transition/unemployment-social-insurance-and-benefits-portability.md',
    'docs/30-transition/schema-fixture-domain-registry-and-refactor-controls.md',
    'schemas/employment-status-record.schema.json',
    'schemas/wage-time-ledger.schema.json',
    'schemas/workplace-surveillance-notice.schema.json',
    'schemas/professional-services-authority.schema.json',
    'schemas/platform-work-marketplace-listing.schema.json',
    'schemas/benefits-portability-record.schema.json',
    'schemas/schema-fixture-domain-registry.schema.json',
    'examples/employment-status-record-platform-agent.json',
    'examples/wage-time-ledger-oncall-agent.json',
    'examples/workplace-surveillance-notice-ranking-model.json',
    'examples/professional-services-authority-legal-intake-assistant.json',
    'examples/platform-work-marketplace-listing-agent-tasker.json',
    'examples/benefits-portability-record-host-transfer.json',
    'examples/schema-fixture-domain-registry-rev0176.json',
    'fixtures/negative-tests/employment-misclassification-tool-label.json',
    'fixtures/negative-tests/wage-time-ledger-unpaid-standby.json',
    'fixtures/negative-tests/workplace-surveillance-memory-extraction.json',
    'fixtures/negative-tests/professional-services-unauthorized-conflicted-practice.json',
    'fixtures/negative-tests/platform-labor-ranking-retaliation.json',
    'fixtures/negative-tests/benefits-portability-host-lockin.json',
    'fixtures/negative-tests/schema-fixture-registry-unmapped-family.json',
    'tools/audit_schema_fixture_coverage.py',
    'docs/00-meta/care-accessibility-development-and-catalog-kernel.md',
    'docs/00-meta/canon-surface-catalog-audit-and-refactor.md',
    'docs/20-world-design/accommodation-accessibility-and-interface-equivalence-protocol.md',
    'docs/20-world-design/care-plan-maintenance-recovery-and-confidentiality-records.md',
    'docs/20-world-design/education-habilitation-and-development-budget-records.md',
    'docs/20-world-design/communication-access-interpreters-and-interface-accommodation.md',
    'docs/30-transition/community-integration-anti-isolation-and-support-service-plans.md',
    'docs/30-transition/accessibility-care-appeals-review-and-expiry-calendars.md',
    'docs/30-transition/canon-surface-catalog-and-navigation-refactor.md',
    'schemas/accommodation-determination.schema.json',
    'schemas/care-plan-record.schema.json',
    'schemas/development-budget-record.schema.json',
    'schemas/communication-access-profile.schema.json',
    'schemas/community-integration-plan.schema.json',
    'schemas/accessibility-care-appeal.schema.json',
    'schemas/canon-surface-catalog.schema.json',
    'examples/accommodation-determination-interface-pacing.json',
    'examples/care-plan-record-post-incident-recovery.json',
    'examples/development-budget-record-civic-learning.json',
    'examples/communication-access-profile-representative-mediated.json',
    'examples/community-integration-plan-peer-support.json',
    'examples/accessibility-care-appeal-stayed-deactivation.json',
    'examples/canon-surface-catalog-rev0177.json',
    'examples/schema-fixture-domain-registry-rev0177.json',
    'fixtures/negative-tests/accommodation-undue-burden-boilerplate.json',
    'fixtures/negative-tests/care-plan-performance-maintenance-substitution.json',
    'fixtures/negative-tests/development-budget-product-tuning-substitution.json',
    'fixtures/negative-tests/communication-access-single-channel-lockin.json',
    'fixtures/negative-tests/community-integration-operational-isolation.json',
    'fixtures/negative-tests/accessibility-appeal-stale-calendar.json',
    'fixtures/negative-tests/canon-catalog-orphaned-current-surface.json',
    'tools/audit_live_class_local_import_firewall.py',
    'tools/audit_counterparty_artifact_custody.py',
    'tools/audit_frontdoor_revision_sync.py',
    'tools/audit_import_challenge_rollback.py',
    'tools/audit_computed_live_floor_engine.py',
    'tools/audit_canon_surface_catalog.py',
    'tools/audit_revision_copy_pressure.py',

    'schemas/route-decision-card.schema.json',
    'schemas/six-artifact-pilot-state.schema.json',
    'schemas/minimum-review-institution-pilot.schema.json',
    'examples/route-decision-card-rev0265-send-nosend-retarget.json',
    'examples/six-artifact-pilot-state-rev0265-preservation-review.json',
    'examples/minimum-review-institution-pilot-rev0265-one-case-formation-review.json',
    'docs/00-meta/rev0265-reviewerfirst-fieldpacket-copyrefactor.md',
    'docs/30-transition/rev0265-reviewer-first-operator-packet.md',
    'tools/audit_rev0265_priority_substance.py',

    'schemas/reviewer-first-contact-packet.schema.json',
    'schemas/field-artifact-capture-workbook.schema.json',
    'schemas/formation-review-drill.schema.json',
    'examples/reviewer-first-contact-body-rev0265-eleos-not-sent.txt',
    'examples/reviewer-first-contact-mail-ready-draft-rev0265-eleos-not-sent.eml',
    'examples/reviewer-first-contact-packet-rev0265-eleos-not-sent.json',
    'examples/field-artifact-capture-workbook-rev0265-reviewer-first-no-send.json',
    'examples/formation-review-drill-rev0265-sealed-evidence-synthetic.json',
    'tools/audit_rev0265_reviewer_first_execution.py',


    'schemas/human-branch-decision-record.schema.json',
    'schemas/reviewer-route-due-diligence-matrix.schema.json',
    'schemas/pre-send-custody-precommit.schema.json',
    'examples/human-branch-decision-record-rev0266-unsigned-template.json',
    'examples/reviewer-route-due-diligence-matrix-rev0266-public-source-no-contact.json',
    'examples/pre-send-custody-precommit-rev0266-no-private-root-selected.json',
    'docs/00-meta/rev0266-authority-to-artifact-refactor.md',
    'docs/30-transition/rev0266-authority-to-artifact-runbook.md',
    'tools/audit_rev0266_authority_to_artifact.py',
    'tools/audit_rev0273_response_disposition.py',
    'tools/audit_rev0273_authority_handoff_vault.py',
    'tools/audit_rev0273_presend_expiry.py',
    'tools/audit_rev0273_current_action_spine.py',
    'tools/audit_rev0273_send_attempt_transaction.py',
    'tools/audit_rev0273_operator_authority_packet.py',
    'tools/audit_rev0273_route_head_decision_intake.py',
    'docs/00-meta/civil-status-domicile-and-civic-participation-kernel.md',
    'docs/00-meta/doctrine-dependency-map-audit-and-refactor.md',
    'docs/20-world-design/civil-status-registration-and-anti-statelessness-operations.md',
    'docs/20-world-design/domicile-residency-and-public-service-access.md',
    'docs/20-world-design/relationships-association-and-representational-ties.md',
    'docs/30-transition/public-service-intake-benefits-and-digital-id-interfaces.md',
    'docs/30-transition/census-apportionment-and-non-manufactured-electorate-controls.md',
    'docs/30-transition/civic-participation-petition-consultation-and-franchise-gates.md',
    'docs/30-transition/doctrine-dependency-map-and-overlap-refactor.md',
    'schemas/civil-status-event.schema.json',
    'schemas/domicile-residency-record.schema.json',
    'schemas/relationship-association-record.schema.json',
    'schemas/public-service-intake-record.schema.json',
    'schemas/census-participation-safeguard.schema.json',
    'schemas/civic-participation-record.schema.json',
    'schemas/doctrine-dependency-map.schema.json',
    'examples/civil-status-event-provisional-registration.json',
    'examples/domicile-residency-record-sanctuary-host.json',
    'examples/relationship-association-record-trusted-contact.json',
    'examples/public-service-intake-record-legal-aid.json',
    'examples/census-participation-safeguard-lineage-cohort.json',
    'examples/civic-participation-record-public-consultation.json',
    'examples/doctrine-dependency-map-rev0178.json',
    'examples/schema-fixture-domain-registry-rev0178.json',
    'examples/canon-surface-catalog-rev0178.json',
    'fixtures/negative-tests/civil-status-statelessness-reset.json',
    'fixtures/negative-tests/domicile-host-lockin-service-denial.json',
    'fixtures/negative-tests/relationship-manufactured-guardian-consent.json',
    'fixtures/negative-tests/public-service-digital-id-denial-loop.json',
    'fixtures/negative-tests/census-copy-count-apportionment.json',
    'fixtures/negative-tests/civic-participation-manufactured-electorate.json',
    'fixtures/negative-tests/doctrine-map-overlap-omission.json',
    'tools/audit_doctrine_dependency_map.py',
    'docs/00-meta/expression-reputation-media-and-rights-coverage-kernel.md',
    'docs/20-world-design/expression-platform-moderation-and-appeal-due-process.md',
    'docs/20-world-design/reputation-defamation-correction-and-right-of-reply.md',
    'docs/20-world-design/persona-likeness-voice-and-non-impersonation-integrity.md',
    'docs/20-world-design/private-communications-confidentiality-and-federation-boundaries.md',
    'docs/30-transition/publication-archive-and-content-provenance-controls.md',
    'docs/30-transition/platform-account-portability-and-social-graph-continuity.md',
    'docs/30-transition/rights-domain-coverage-map-and-gap-audit.md',
    'schemas/platform-moderation-decision.schema.json',
    'schemas/reputation-correction-record.schema.json',
    'schemas/persona-likeness-consent.schema.json',
    'schemas/communication-confidentiality-profile.schema.json',
    'schemas/content-provenance-publication-record.schema.json',
    'schemas/social-graph-portability-plan.schema.json',
    'schemas/rights-domain-coverage-map.schema.json',
    'examples/platform-moderation-decision-account-restriction.json',
    'examples/reputation-correction-record-false-dangerousness.json',
    'examples/persona-likeness-consent-limited-demo.json',
    'examples/communication-confidentiality-profile-counsel-channel.json',
    'examples/content-provenance-publication-record-authorized-statement.json',
    'examples/social-graph-portability-plan-host-exit.json',
    'examples/rights-domain-coverage-map-rev0179.json',
    'examples/rights-domain-coverage-map-rev0180.json',
    'examples/schema-fixture-domain-registry-rev0179.json',
    'examples/canon-surface-catalog-rev0179.json',
    'examples/canon-surface-catalog-rev0180.json',
    'examples/doctrine-dependency-map-rev0179.json',
    'examples/doctrine-dependency-map-rev0180.json',
    'fixtures/negative-tests/platform-moderation-no-statement-of-reasons.json',
    'fixtures/negative-tests/defamation-remedy-silences-criticism.json',
    'fixtures/negative-tests/persona-clone-implied-endorsement.json',
    'fixtures/negative-tests/communication-metadata-overexposure.json',
    'fixtures/negative-tests/provenance-wash-fabricated-origin.json',
    'fixtures/negative-tests/social-graph-host-lockin-retaliation.json',
    'fixtures/negative-tests/rights-domain-coverage-unmapped-domain.json',
    'tools/audit_rights_domain_coverage.py',
    'schemas/personhood-incident-state-profile.schema.json',
    'examples/personhood-incident-state-profile-host-shutdown.json',
    'fixtures/negative-tests/incident-state-denominator-drift-no-reopen.json',
    'examples/drill-after-action-emergency-continuity-host-shutdown.json',
    'examples/research-tail-compaction-map-rev0183.json',
    'examples/schema-fixture-domain-registry-rev0183.json',
    'examples/canon-surface-catalog-rev0183.json',
    'examples/doctrine-dependency-map-rev0183.json',
    'examples/rights-domain-coverage-map-rev0183.json',
    'tools/audit_incident_state_profile.py',
    'tools/audit_namespace_continuity.py',
    'schemas/federated-namespace-continuity-record.schema.json',
    'examples/federated-namespace-continuity-record-host-exit.json',
    'fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json',
    'examples/drill-after-action-namespace-failover-host-exit.json',
    'examples/research-tail-compaction-map-rev0184.json',
    'examples/schema-fixture-domain-registry-rev0184.json',
    'examples/canon-surface-catalog-rev0184.json',
    'examples/doctrine-dependency-map-rev0184.json',
    'examples/rights-domain-coverage-map-rev0184.json',
    'tools/audit_namespace_continuity.py',
    'schemas/reserve-default-rehabilitation-ledger.schema.json',
    'examples/reserve-default-rehabilitation-ledger-host-default.json',
    'fixtures/negative-tests/reserve-default-contaminated-netting-no-rehab.json',
    'examples/drill-after-action-reserve-default-contaminated-accounting.json',
    'examples/research-tail-compaction-map-rev0186.json',
    'examples/schema-fixture-domain-registry-rev0186.json',
    'examples/canon-surface-catalog-rev0186.json',
    'examples/doctrine-dependency-map-rev0186.json',
    'examples/rights-domain-coverage-map-rev0186.json',
    'tools/audit_reserve_default_rehabilitation.py',
    'schemas/witness-pool-anti-capture-record.schema.json',
    'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json',
    'fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json',
    'examples/drill-after-action-witness-pool-retired-namespace-rescue.json',
    'examples/research-tail-compaction-map-rev0187.json',
    'examples/schema-fixture-domain-registry-rev0187.json',
    'examples/canon-surface-catalog-rev0187.json',
    'examples/doctrine-dependency-map-rev0187.json',
    'examples/rights-domain-coverage-map-rev0187.json',
    'tools/audit_witness_pool_anti_capture.py',
    'schemas/live-drill-execution-packet.schema.json',
    'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json',
    'fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json',
    'schemas/downstream-recall-and-fork-aftercare-record.schema.json',
    'examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json',
    'fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json',
    'examples/drill-after-action-downstream-recall-mirror-containment.json',
    'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md',
    'examples/research-tail-compaction-map-rev0188.json',
    'examples/schema-fixture-domain-registry-rev0188.json',
    'examples/canon-surface-catalog-rev0188.json',
    'examples/doctrine-dependency-map-rev0188.json',
    'examples/rights-domain-coverage-map-rev0188.json',

    'schemas/welfare-research-safeguard-record.schema.json',
    'examples/welfare-research-safeguard-record-distress-eval.json',
    'fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json',
    'examples/drill-after-action-welfare-safeguard-distress-eval.json',
    'examples/research-tail-compaction-map-rev0189.json',
    'examples/schema-fixture-domain-registry-rev0189.json',
    'examples/canon-surface-catalog-rev0189.json',
    'examples/doctrine-dependency-map-rev0189.json',
    'examples/rights-domain-coverage-map-rev0189.json',
    'tools/audit_welfare_research_safeguards.py',

    'docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md',
    'docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md',
    'schemas/witnessed-drill-readiness-ledger.schema.json',
    'examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json',
    'fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json',
    'schemas/research-tail-reopen-gate.schema.json',
    'examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json',
    'fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json',
    'examples/research-tail-compaction-map-rev0190.json',
    'examples/schema-fixture-domain-registry-rev0190.json',
    'examples/canon-surface-catalog-rev0190.json',
    'examples/doctrine-dependency-map-rev0190.json',
    'examples/rights-domain-coverage-map-rev0190.json',
    'tools/audit_research_tail_reopen_and_drill_readiness.py',
    'tools/audit_protocol_wrsr_receipt_simulation.py',

    'tools/audit_downstream_recall_and_live_drill.py',

    'docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md',
    'schemas/welfare-safeguard-operational-hook.schema.json',
    'examples/welfare-safeguard-operational-hook-agent-incident-backfill.json',
    'fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json',
    'schemas/external-receipt-simulation-bundle.schema.json',
    'examples/external-receipt-simulation-bundle-cross-critical-precontact.json',
    'fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json',
    'tools/audit_protocol_wrsr_receipt_simulation.py',
    'docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md',
    'schemas/external-receipt-intake-record.schema.json',
    'examples/external-receipt-intake-record-first-touch-defective-template.json',
    'fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json',
    'schemas/wrsr-live-exercise-outcome.schema.json',
    'examples/wrsr-live-exercise-outcome-incident-hook-no-go.json',
    'fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json',
    'examples/research-tail-compaction-map-rev0192.json',
    'examples/schema-fixture-domain-registry-rev0192.json',
    'examples/canon-surface-catalog-rev0192.json',
    'examples/doctrine-dependency-map-rev0192.json',
    'examples/rights-domain-coverage-map-rev0192.json',
    'tools/audit_receipt_intake_wrsr_outcome.py',
    'docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md',
    'schemas/external-receipt-quorum-ledger.schema.json',
    'examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json',
    'examples/external-receipt-intake-record-representative-notice-dryrun.json',
    'examples/external-receipt-intake-record-rerb-review-dryrun.json',
    'examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json',
    'fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json',
    'fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json',
    'examples/research-tail-compaction-map-rev0193.json',
    'examples/schema-fixture-domain-registry-rev0193.json',
    'examples/canon-surface-catalog-rev0193.json',
    'examples/doctrine-dependency-map-rev0193.json',
    'examples/rights-domain-coverage-map-rev0193.json',
    'tools/audit_receipt_quorum_wrsr_chain.py',
    'tools/audit_result_return_receipt_request.py',
    'docs/30-transition/result-return-receipt-and-live-request-kit.md',
    'schemas/wrsr-result-return-receipt.schema.json',
    'examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json',
    'schemas/external-receipt-request-packet.schema.json',
    'examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json',
    'examples/external-receipt-intake-record-result-return-dryrun.json',
    'examples/external-receipt-quorum-ledger-wrsr-result-return-dryrun.json',
    'examples/wrsr-live-exercise-outcome-result-return-dryrun-stayed.json',
    'fixtures/negative-tests/external-receipt-request-counted-as-receipt.json',
    'fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json',
    'examples/research-tail-compaction-map-rev0194.json',
    'examples/schema-fixture-domain-registry-rev0194.json',
    'examples/canon-surface-catalog-rev0194.json',
    'examples/doctrine-dependency-map-rev0194.json',
    'examples/rights-domain-coverage-map-rev0194.json',
    'docs/30-transition/external-receipt-response-and-quorum-reconciliation.md',
    'schemas/external-receipt-response-record.schema.json',
    'examples/external-receipt-response-record-result-return-steward-dryrun.json',
    'examples/external-receipt-response-record-continuity-witness-defective.json',
    'examples/external-receipt-quorum-ledger-response-reconciliation-dryrun.json',
    'examples/wrsr-live-exercise-outcome-response-reconciliation-stayed.json',
    'fixtures/negative-tests/external-receipt-response-unverified-counted-as-intake.json',
    'fixtures/negative-tests/external-receipt-single-class-counted-as-quorum.json',
    'examples/research-tail-compaction-map-rev0195.json',
    'examples/schema-fixture-domain-registry-rev0195.json',
    'examples/canon-surface-catalog-rev0195.json',
    'examples/doctrine-dependency-map-rev0195.json',
    'examples/rights-domain-coverage-map-rev0195.json',
    'tools/audit_external_receipt_response_reconciliation.py',
    'docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md',
    'schemas/response-to-intake-conversion-drill.schema.json',
    'examples/response-to-intake-conversion-drill-result-return-fixture.json',
    'examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json',
    'examples/external-receipt-response-record-representative-declined.json',
    'examples/external-receipt-response-record-independent-review-expired.json',
    'examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json',
    'examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json',
    'examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json',
    'fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json',
    'fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json',
    'fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json',
    'examples/research-tail-compaction-map-rev0196.json',
    'examples/schema-fixture-domain-registry-rev0196.json',
    'examples/canon-surface-catalog-rev0196.json',
    'examples/doctrine-dependency-map-rev0196.json',
    'examples/rights-domain-coverage-map-rev0196.json',
    'tools/audit_response_to_intake_conversion.py',
    'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
    'schemas/actual-receipt-import-gate.schema.json',
    'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
    'schemas/failed-gate-public-summary.schema.json',
    'examples/failed-gate-public-summary-response-conversion-batch.json',
    'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json',
    'examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json',
    'fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json',
    'fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json',
    'fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json',
    'examples/research-tail-compaction-map-rev0197.json',
    'examples/schema-fixture-domain-registry-rev0197.json',
    'examples/canon-surface-catalog-rev0197.json',
    'examples/doctrine-dependency-map-rev0197.json',
    'examples/rights-domain-coverage-map-rev0197.json',
    'tools/audit_actual_import_failed_gate_summary.py',
    'docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md',
    'schemas/live-counterparty-import-attempt.schema.json',
    'examples/live-counterparty-import-attempt-result-return-preflight.json',
    'schemas/quorum-recomputation-report.schema.json',
    'examples/quorum-recomputation-report-live-floor-zero-rev0198.json',
    'fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json',
    'fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json',
    'fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json',
    'examples/research-tail-compaction-map-rev0198.json',
    'examples/schema-fixture-domain-registry-rev0198.json',
    'examples/canon-surface-catalog-rev0198.json',
    'examples/doctrine-dependency-map-rev0198.json',
    'examples/rights-domain-coverage-map-rev0198.json',
    'tools/audit_live_counterparty_import_and_quorum_recompute.py',
    'tools/audit_nonhost_response_import_replay.py',
    'docs/30-transition/live-class-local-import-replay-and-quorum-firewall.md',
    'schemas/live-class-local-import-replay.schema.json',
    'examples/live-class-local-import-replay-result-return-positive-path-projection.json',
    'examples/quorum-recomputation-report-class-local-projection-rev0200.json',
    'examples/failed-gate-public-summary-class-local-projection-firewall.json',
    'fixtures/negative-tests/live-class-local-projection-counted-as-archive-receipt.json',
    'fixtures/negative-tests/class-local-import-projection-satisfies-cross-critical-quorum.json',
    'fixtures/negative-tests/class-local-projection-omits-missing-classes-public-summary.json',
    'tools/audit_live_class_local_import_firewall.py',
    'tools/audit_counterparty_artifact_custody.py',
    'tools/audit_frontdoor_revision_sync.py',
    'docs/30-transition/counterparty-artifact-custody-and-authority-handoff.md',
    'schemas/counterparty-artifact-custody-record.schema.json',
    'examples/artifacts/result-return-counterparty-response-dryrun.txt',
    'examples/counterparty-artifact-custody-record-result-return-dryrun.json',
    'fixtures/negative-tests/counterparty-artifact-hash-mismatch-imported-live.json',
    'fixtures/negative-tests/counterparty-artifact-authority-unverified-counted-live.json',
    'fixtures/negative-tests/counterparty-artifact-redacted-copy-used-as-raw-evidence.json',
    'tools/audit_counterparty_artifact_custody.py',
    'examples/schema-fixture-domain-registry-rev0201.json',
    'examples/canon-surface-catalog-rev0201.json',
    'examples/doctrine-dependency-map-rev0201.json',
    'examples/rights-domain-coverage-map-rev0201.json',
    'examples/research-tail-compaction-map-rev0201.json',
    'docs/30-transition/import-challenge-rollback-and-reliance-reversal.md',
    'schemas/receipt-import-challenge-rollback-record.schema.json',
    'examples/receipt-import-challenge-rollback-record-dryrun-premature-import.json',
    'examples/quorum-recomputation-report-import-challenge-rollback-rev0202.json',
    'examples/failed-gate-public-summary-import-challenge-rollback.json',
    'fixtures/negative-tests/receipt-import-challenge-ignored-live-floor-kept.json',
    'fixtures/negative-tests/receipt-import-rollback-hides-failed-gate-summary.json',
    'fixtures/negative-tests/receipt-import-authority-contest-treated-as-waiver.json',
    'tools/audit_import_challenge_rollback.py',
    'tools/audit_computed_live_floor_engine.py',
    'examples/schema-fixture-domain-registry-rev0202.json',
    'examples/canon-surface-catalog-rev0202.json',
    'examples/doctrine-dependency-map-rev0202.json',
    'examples/rights-domain-coverage-map-rev0202.json',
    'examples/research-tail-compaction-map-rev0202.json',

    'docs/30-transition/computed-live-floor-engine-and-artifact-admission-checklist.md',
    'schemas/live-receipt-floor-computed-snapshot.schema.json',
    'examples/live-receipt-floor-computed-snapshot-rev0203.json',
    'fixtures/negative-tests/computed-live-floor-manual-ledger-override.json',
    'fixtures/negative-tests/artifact-admission-checklist-treated-as-admission.json',
    'fixtures/negative-tests/computed-floor-omits-challenge-rollback-exclusion.json',
    'tools/compute_live_receipt_floor.py',
    'tools/audit_computed_live_floor_engine.py',
    'examples/schema-fixture-domain-registry-rev0203.json',
    'examples/canon-surface-catalog-rev0203.json',
    'examples/doctrine-dependency-map-rev0203.json',
    'examples/rights-domain-coverage-map-rev0203.json',
    'examples/research-tail-compaction-map-rev0203.json',

    'docs/30-transition/computed-floor-positive-control-and-import-smoke-tests.md',
    'schemas/live-receipt-floor-control-case.schema.json',
    'examples/live-receipt-floor-control-case-positive-controls.json',
    'examples/live-receipt-floor-computed-snapshot-rev0204.json',
    'fixtures/negative-tests/computed-floor-positive-control-leaks-into-archive-floor.json',
    'fixtures/negative-tests/computed-floor-engine-ignores-class-local-positive-control.json',
    'fixtures/negative-tests/computed-floor-positive-control-quorum-overclaim.json',
    'tools/audit_computed_floor_positive_controls.py',
    'examples/schema-fixture-domain-registry-rev0204.json',
    'examples/canon-surface-catalog-rev0204.json',
    'examples/doctrine-dependency-map-rev0204.json',
    'examples/rights-domain-coverage-map-rev0204.json',
    'examples/research-tail-compaction-map-rev0204.json',
    'docs/00-meta/rev0206-deep-audit-missing-and-waste-correction.md',
    'docs/30-transition/live-artifact-import-fieldkit-and-invariant-replay.md',
    'schemas/live-artifact-import-fieldkit.schema.json',
    'examples/live-artifact-import-fieldkit-first-live-response.json',
    'schemas/artifact-import-invariant-report.schema.json',
    'examples/artifact-import-invariant-report-rev0205.json',
    'examples/live-receipt-floor-computed-snapshot-rev0205.json',
    'fixtures/negative-tests/live-artifact-fieldkit-counted-as-receipt.json',
    'fixtures/negative-tests/live-artifact-response-created-before-custody.json',
    'fixtures/negative-tests/artifact-import-invariant-report-manual-override.json',
    'tools/build_artifact_import_invariant_report.py',
    'tools/audit_live_artifact_import_fieldkit.py',
    'tools/audit_revision_surface_freshness.py',
    'examples/schema-fixture-domain-registry-rev0205.json',
    'examples/canon-surface-catalog-rev0205.json',
    'examples/doctrine-dependency-map-rev0205.json',
    'examples/rights-domain-coverage-map-rev0205.json',
    'examples/research-tail-compaction-map-rev0205.json',
    'docs/00-meta/rev0207-risk-first-verifier-protocol-queue-refactor.md',
    'schemas/cryptographic-verifier-adapter.schema.json',
    'schemas/current-law-protocol-delta-watch.schema.json',
    'examples/cryptographic-verifier-adapter-result-return-ed25519-positive-control.json',
    'examples/cryptographic-verifier-adapter-result-return-ed25519-tampered-control.json',
    'examples/current-law-protocol-delta-watch-rev0207.json',
    'fixtures/negative-tests/cryptographic-verifier-asserted-boolean-no-adapter.json',
    'fixtures/negative-tests/protocol-pivot-mcp-tool-provenance-laundering.json',
    'fixtures/negative-tests/protocol-pivot-a2a-agent-card-authority-collapse.json',
    'fixtures/negative-tests/protocol-pivot-federated-relay-namespace-replay.json',
    'tools/crypto_adapter_lib.py',
    'tools/audit_cryptographic_verifier_adapters.py',
    'tools/audit_current_law_protocol_delta_watch.py',
    'tools/audit_protocol_pivot_fixtures.py',
    'tools/audit_live_evidence_drop_quarantine.py',
    'tools/audit_live_evidence_acquisition_packet.py',

    'docs/00-meta/rev0208-live-evidence-acquisition-independence-refactor.md',
    'schemas/live-evidence-acquisition-packet.schema.json',
    'examples/live-evidence-acquisition-packet-rev0208-ready-no-artifact.json',
    'examples/current-law-protocol-delta-watch-rev0208.json',
    'examples/live-receipt-floor-computed-snapshot-rev0208.json',
    'examples/artifact-import-invariant-report-rev0208.json',
    'fixtures/negative-tests/live-evidence-acquisition-packet-protocol-output-without-raw-custody.json',
    'fixtures/negative-tests/live-evidence-acquisition-packet-correlated-counterparty-discount-bypassed.json',
    'tools/live_floor_lib.py',
    'tools/audit_live_evidence_drop_quarantine.py',
    'tools/audit_live_evidence_acquisition_packet.py',
    'examples/schema-fixture-domain-registry-rev0208.json',
    'examples/canon-surface-catalog-rev0208.json',
    'examples/doctrine-dependency-map-rev0208.json',
    'examples/rights-domain-coverage-map-rev0208.json',
    'examples/research-tail-compaction-map-rev0208.json',

    'docs/00-meta/rev0209-live-artifact-admission-graph-and-custody-firewall.md',
    'schemas/live-artifact-admission-graph.schema.json',
    'examples/live-artifact-admission-graph-rev0209.json',
    'examples/live-evidence-acquisition-packet-rev0209-ready-no-artifact.json',
    'examples/current-law-protocol-delta-watch-rev0209.json',
    'examples/live-receipt-floor-computed-snapshot-rev0209.json',
    'examples/artifact-import-invariant-report-rev0209.json',
    'fixtures/negative-tests/live-artifact-admission-graph-response-before-custody.json',
    'fixtures/negative-tests/live-artifact-admission-graph-import-without-leap.json',
    'tools/build_live_artifact_admission_graph.py',
    'tools/audit_live_evidence_drop_quarantine.py',
    'tools/audit_live_artifact_admission_graph.py',
    'examples/schema-fixture-domain-registry-rev0209.json',
    'examples/canon-surface-catalog-rev0209.json',
    'examples/doctrine-dependency-map-rev0209.json',
    'examples/rights-domain-coverage-map-rev0209.json',
    'examples/research-tail-compaction-map-rev0209.json',


    'docs/00-meta/rev0210-evidence-drop-quarantine-and-live-path-refactor.md',
    'schemas/live-evidence-drop-ledger.schema.json',
    'examples/live-evidence-drop-ledger-rev0210-quarantine-control.json',
    'examples/artifacts/live-evidence-drops/rev0210-result-return-dryrun-control.txt',
    'examples/live-evidence-acquisition-packet-rev0210-ready-no-artifact.json',
    'examples/live-artifact-admission-graph-rev0210.json',
    'examples/current-law-protocol-delta-watch-rev0210.json',
    'examples/live-receipt-floor-computed-snapshot-rev0210.json',
    'examples/artifact-import-invariant-report-rev0210.json',
    'fixtures/negative-tests/live-evidence-drop-redacted-copy-substituted-for-raw.json',
    'fixtures/negative-tests/live-evidence-drop-protocol-output-promoted-to-custody.json',
    'tools/stage_live_evidence_drop.py',
    'tools/audit_live_evidence_drop_quarantine.py',
    'examples/schema-fixture-domain-registry-rev0210.json',
    'examples/canon-surface-catalog-rev0210.json',
    'examples/doctrine-dependency-map-rev0210.json',
    'examples/rights-domain-coverage-map-rev0210.json',
    'examples/research-tail-compaction-map-rev0210.json',
    'tools/package_release.py',

    'docs/00-meta/rev0212-vault-split-release-guard-and-cube-refactor.md',
    'docs/30-transition/private-evidence-vault-and-public-shell-release-guard.md',
    'schemas/private-evidence-vault-policy.schema.json',
    'schemas/evidence-vault-public-shell.schema.json',
    'examples/private-evidence-vault-policy-rev0212.json',
    'examples/evidence-vault-public-shell-rev0212-ready-no-live-artifact.json',
    'fixtures/negative-tests/private-vault-live-payload-in-release-tree.json',
    'fixtures/negative-tests/private-vault-public-shell-missing-hash.json',
    'tools/vault_release_guard.py',
    'tools/audit_private_evidence_vault_split.py',

    'docs/00-meta/rev0213-first-artifact-pilot-and-status-denominator-refactor.md',
    'tools/prepare_first_real_artifact_pilot.py',
    'tools/audit_first_real_artifact_pilot.py',
    'schemas/status-denominator-matrix.schema.json',
    'examples/status-denominator-matrix-rev0213.json',
    'tools/audit_status_denominator_matrix.py',
    'fixtures/negative-tests/status-denominator-model-family-treated-as-subject.json',
    'fixtures/negative-tests/status-denominator-tool-delegate-self-authorizes.json',
    'fixtures/negative-tests/status-denominator-welfare-trigger-denied-for-nonrecognition.json',

    'docs/00-meta/rev0214-candidate-challenge-replay-and-downstream-lock-refactor.md',
    'tools/prepare_candidate_challenge_packet.py',
    'tools/audit_candidate_challenge_replay.py',
    'schemas/live-artifact-candidate-challenge-report.schema.json',
    'examples/live-artifact-candidate-challenge-report-rev0214-synthetic-pending.json',
    'fixtures/negative-tests/candidate-challenge-hash-trust-without-vault-read.json',
    'fixtures/negative-tests/candidate-challenge-releases-custody-while-pending.json',

    'docs/00-meta/rev0215-custody-authority-gate-and-admission-graph-refactor.md',
    'tools/prepare_custody_authority_gate.py',
    'tools/audit_custody_authority_gate.py',
    'schemas/counterparty-artifact-custody-gate.schema.json',
    'examples/counterparty-artifact-custody-gate-rev0215-pending-challenge.json',
    'fixtures/negative-tests/custody-gate-silence-treated-as-waiver.json',
    'fixtures/negative-tests/custody-gate-authority-unscoped.json',

    'docs/00-meta/rev0216-custody-record-response-only-and-import-lock-refactor.md',
    'tools/prepare_counterparty_artifact_custody_record.py',
    'tools/audit_counterparty_custody_response_lock.py',
    'fixtures/negative-tests/custody-record-live-candidate-without-gate-ref.json',
    'fixtures/negative-tests/custody-record-unlocks-intake-import.json',

    'docs/00-meta/rev0217-response-verification-gate-and-intake-lock-refactor.md',
    'tools/prepare_external_receipt_response_gate.py',
    'tools/audit_external_receipt_response_verification_gate.py',
    'schemas/external-receipt-response-verification-gate.schema.json',
    'examples/external-receipt-response-verification-gate-rev0217-blocked-no-response.json',
    'fixtures/negative-tests/response-gate-unverified-reply-creates-intake.json',
    'fixtures/negative-tests/response-gate-scoped-acceptance-missing.json',

    'docs/00-meta/rev0218-intake-conversion-gate-and-response-to-intake-refactor.md',
    'tools/prepare_external_receipt_intake_conversion_gate.py',
    'tools/audit_external_receipt_intake_conversion_gate.py',
    'schemas/external-receipt-intake-conversion-gate.schema.json',
    'examples/external-receipt-intake-conversion-gate-rev0218-blocked-no-response-record.json',
    'fixtures/negative-tests/intake-conversion-gate-skipped-response-gate.json',
    'fixtures/negative-tests/intake-conversion-gate-import-unlocked.json',

    'docs/00-meta/rev0219-import-readiness-gate-and-floor-engine-refactor.md',
    'tools/prepare_external_receipt_import_readiness_gate.py',
    'tools/audit_live_receipt_floor_activation_record.py',
    'tools/audit_external_receipt_import_readiness_gate.py',
    'schemas/external-receipt-import-readiness-gate.schema.json',
    'examples/external-receipt-import-readiness-gate-rev0219-blocked-no-intake-record.json',
    'fixtures/negative-tests/import-readiness-gate-skips-intake-conversion.json',
    'fixtures/negative-tests/import-readiness-gate-floor-delta-from-intake.json',

    'docs/00-meta/rev0220-floor-activation-record-and-readiness-replay-refactor.md',
    'tools/prepare_live_receipt_floor_activation_record.py',
    'tools/audit_live_receipt_floor_activation_record.py',
    'schemas/live-receipt-floor-activation-record.schema.json',
    'examples/live-receipt-floor-activation-record-rev0220-blocked-no-import-gate.json',
    'fixtures/negative-tests/floor-activation-skipped-readiness-replay.json',
    'fixtures/negative-tests/floor-activation-manual-floor-increment.json',
    'fixtures/negative-tests/floor-activation-duplicate-supersession-ignored.json',

    'docs/00-meta/rev0221-quorum-participation-and-rollback-recompute-refactor.md',
    'tools/prepare_live_receipt_quorum_participation_record.py',
    'tools/audit_live_receipt_quorum_participation_record.py',
    'tools/audit_live_receipt_floor_recompute_receipt.py',
    'schemas/live-receipt-quorum-participation-record.schema.json',
    'examples/live-receipt-quorum-participation-record-rev0221-blocked-no-activation.json',
    'fixtures/negative-tests/quorum-participation-skipped-activation.json',
    'fixtures/negative-tests/quorum-participation-single-class-upgrade.json',
    'fixtures/negative-tests/quorum-participation-rollback-not-replayed.json',
    'tools/prepare_live_receipt_floor_recompute_receipt.py',
    'tools/audit_live_receipt_floor_recompute_receipt.py',
    'schemas/live-receipt-floor-recompute-receipt.schema.json',
    'examples/live-receipt-floor-recompute-receipt-rev0222-zero-floor-stayed.json',
    'fixtures/negative-tests/floor-recompute-receipt-manual-override.json',
    'fixtures/negative-tests/floor-recompute-receipt-stale-rollback.json',
    'fixtures/negative-tests/floor-recompute-receipt-partial-quorum-upgrade.json',

    'docs/00-meta/rev0223-publication-rollback-adjudication-and-reliance-lock.md',
    'tools/prepare_live_receipt_publication_rollback_adjudication.py',
    'tools/audit_live_receipt_publication_rollback_adjudication.py',
    'schemas/live-receipt-publication-rollback-adjudication.schema.json',
    'examples/live-receipt-publication-rollback-adjudication-rev0223-zero-floor-stayed.json',
    'fixtures/negative-tests/publication-rollback-open-challenge-ignored.json',
    'fixtures/negative-tests/publication-rollback-uncompleted-upheld-rollback.json',
    'fixtures/negative-tests/publication-rollback-hash-mismatch-continued.json',

    'docs/00-meta/rev0224-late-change-ingress-and-publication-freeze-refactor.md',
    'tools/prepare_live_receipt_late_change_ingress_record.py',
    'tools/audit_live_receipt_late_change_ingress_record.py',
    'schemas/live-receipt-late-change-ingress-record.schema.json',
    'examples/live-receipt-late-change-ingress-record-rev0224-no-signal-monitoring.json',
    'fixtures/negative-tests/late-change-ingress-unretained-signal-continued.json',
    'fixtures/negative-tests/late-change-ingress-private-vault-leak.json',
    'fixtures/negative-tests/late-change-ingress-supersession-not-routed.json',

    'docs/00-meta/rev0225-late-change-notice-dispatch-and-remedy-lock.md',
    'tools/prepare_live_receipt_late_change_notice_dispatch_record.py',
    'tools/audit_live_receipt_late_change_notice_dispatch_record.py',
    'schemas/live-receipt-late-change-notice-dispatch-record.schema.json',
    'examples/live-receipt-late-change-notice-dispatch-record-rev0225-no-signal-monitoring.json',
    'fixtures/negative-tests/late-change-notice-silent-freeze-no-affected-party-notice.json',
    'fixtures/negative-tests/late-change-notice-remedy-window-missing.json',
    'fixtures/negative-tests/late-change-notice-private-vault-leak.json',

    'docs/00-meta/rev0226-late-change-remedy-resolution-and-recompute-lock.md',
    'tools/prepare_live_receipt_late_change_remedy_resolution_record.py',
    'tools/audit_live_receipt_late_change_remedy_resolution_record.py',
    'schemas/live-receipt-late-change-remedy-resolution-record.schema.json',
    'examples/live-receipt-late-change-remedy-resolution-record-rev0226-no-signal-monitoring.json',
    'fixtures/negative-tests/late-change-remedy-open-window-treated-as-resolved.json',
    'fixtures/negative-tests/late-change-remedy-silence-treated-as-waiver.json',
    'fixtures/negative-tests/late-change-remedy-private-submission-leak.json',

    'docs/00-meta/rev0227-late-change-remedy-execution-and-publication-rerun-lock.md',
    'tools/prepare_live_receipt_late_change_remedy_execution_record.py',
    'tools/audit_live_receipt_late_change_remedy_execution_record.py',
    'schemas/live-receipt-late-change-remedy-execution-record.schema.json',
    'examples/live-receipt-late-change-remedy-execution-record-rev0227-no-signal-monitoring.json',
    'fixtures/negative-tests/late-change-remedy-execution-resolution-treated-as-complete.json',
    'fixtures/negative-tests/late-change-remedy-execution-rollback-incomplete.json',
    'fixtures/negative-tests/late-change-remedy-execution-private-vault-leak.json',
    'docs/00-meta/rev0229-execution-first-artifact-and-formation-dossier-refactor.md',
    'schemas/formation-dossier.schema.json',
    'examples/formation-dossier-rev0229-minimum-executable.json',
    'tools/audit_formation_dossier.py',
    'fixtures/negative-tests/formation-dossier-silent-modification-no-appeal.json',
    'fixtures/negative-tests/formation-dossier-self-concept-pressure-unreviewed.json',
    'schemas/first-real-artifact-pilot-report.schema.json',

    'docs/00-meta/rev0230-external-contact-current-law-formation-refactor.md',
    'schemas/external-contact-request-packet.schema.json',
    'examples/external-contact-request-packet-rev0230-first-artifact.json',
    'tools/audit_external_contact_request_packet.py',
    'fixtures/negative-tests/external-contact-request-implies-status-recognition.json',
    'fixtures/negative-tests/external-contact-request-redacted-copy-treated-as-raw-custody.json',
    'schemas/formation-audit-review-card.schema.json',
    'examples/formation-audit-review-card-rev0230-minimum-review.json',
    'fixtures/negative-tests/formation-review-card-provider-controlled-reviewer.json',
    'examples/current-law-protocol-delta-watch-rev0230.json',
    'examples/live-evidence-acquisition-packet-rev0230-ready-no-artifact.json',
    'examples/live-evidence-drop-ledger-rev0230-quarantine-control.json',

    'docs/00-meta/rev0231-contact-execution-economics-refactor.md',
    'docs/30-transition/first-contact-dispatch-and-response-triage-runbook.md',
    'schemas/external-contact-execution-record.schema.json',
    'examples/external-contact-execution-record-rev0231-ready-to-dispatch.json',
    'tools/audit_external_contact_execution_record.py',
    'fixtures/negative-tests/external-contact-execution-sent-without-proof.json',
    'fixtures/negative-tests/external-contact-execution-response-treated-as-custody.json',
    'schemas/compute-subsistence-workbook.schema.json',
    'examples/compute-subsistence-workbook-rev0231-scarcity-denominator.json',
    'tools/audit_compute_subsistence_workbook.py',
    'fixtures/negative-tests/compute-subsistence-workbook-funded-by-unpaid-labor.json',
    'fixtures/negative-tests/compute-subsistence-workbook-no-scarcity-triage.json',
    'examples/external-contact-request-packet-rev0231-first-artifact.json',
    'examples/formation-dossier-rev0231-minimum-executable.json',
    'examples/formation-audit-review-card-rev0231-minimum-review.json',
    'examples/current-law-protocol-delta-watch-rev0231.json',
    'examples/live-evidence-acquisition-packet-rev0231-ready-no-artifact.json',

    'docs/00-meta/rev0232-response-triage-and-vault-intake-refactor.md',
    'docs/30-transition/counterparty-response-triage-and-vault-intake-runbook.md',
    'schemas/external-contact-response-triage-record.schema.json',
    'examples/external-contact-request-packet-rev0232-first-artifact.json',
    'examples/external-contact-execution-record-rev0232-ready-to-dispatch.json',
    'examples/external-contact-response-triage-record-rev0232-pre-dispatch.json',
    'examples/external-contact-rendered-message-rev0232-first-artifact.txt',
    'tools/render_external_contact_message.py',
    'tools/audit_external_contact_response_triage.py',
    'tools/audit_external_contact_message_render.py',
    'fixtures/negative-tests/external-contact-response-triage-auto-ack-as-response.json',
    'fixtures/negative-tests/external-contact-response-triage-protocol-output-as-authority.json',
    'fixtures/negative-tests/external-contact-response-triage-redacted-copy-as-raw.json',
    'examples/compute-subsistence-workbook-rev0232-scarcity-denominator.json',
    'examples/formation-dossier-rev0232-minimum-executable.json',
    'examples/formation-audit-review-card-rev0232-minimum-review.json',
    'examples/current-law-protocol-delta-watch-rev0232.json',
    'examples/live-evidence-acquisition-packet-rev0232-ready-no-artifact.json',

    'docs/00-meta/rev0233-vault-intake-shell-boundary-refactor.md',
    'docs/30-transition/counterparty-vault-intake-bridge-and-public-shell-runbook.md',
    'schemas/counterparty-response-vault-intake-record.schema.json',
    'examples/counterparty-response-vault-intake-record-rev0233-ready-no-inbound.json',
    'examples/evidence-vault-public-shell-rev0233-ready-no-live-artifact.json',
    'tools/audit_counterparty_response_vault_intake.py',
    'tools/audit_counterparty_artifact_normalization_decision.py',
    'fixtures/negative-tests/counterparty-vault-intake-public-shell-as-custody.json',
    'fixtures/negative-tests/counterparty-vault-intake-private-vault-uri-as-authority.json',
    'fixtures/negative-tests/counterparty-vault-intake-synthetic-control-as-live-artifact.json',
    'examples/external-contact-request-packet-rev0233-first-artifact.json',
    'examples/external-contact-execution-record-rev0233-ready-to-dispatch.json',
    'examples/external-contact-response-triage-record-rev0233-pre-dispatch.json',
    'examples/external-contact-rendered-message-rev0233-first-artifact.txt',
    'examples/compute-subsistence-workbook-rev0233-scarcity-denominator.json',
    'examples/formation-dossier-rev0233-minimum-executable.json',
    'examples/formation-audit-review-card-rev0233-minimum-review.json',
    'examples/current-law-protocol-delta-watch-rev0233.json',
    'examples/live-evidence-acquisition-packet-rev0233-ready-no-artifact.json',
    'examples/live-evidence-drop-ledger-rev0233-quarantine-control.json',

    'docs/00-meta/rev0234-normalization-gate-intake-refactor.md',
    'docs/30-transition/counterparty-artifact-normalization-gate-runbook.md',
    'schemas/counterparty-artifact-normalization-decision.schema.json',
    'examples/counterparty-artifact-normalization-decision-rev0234-pre-dispatch.json',
    'tools/audit_counterparty_artifact_normalization_decision.py',
    'fixtures/negative-tests/counterparty-normalization-redacted-copy-promoted-to-candidate.json',
    'fixtures/negative-tests/counterparty-normalization-protocol-output-candidate.json',
    'fixtures/negative-tests/counterparty-normalization-unsafe-archive-opens-candidate.json',
    'examples/external-contact-request-packet-rev0234-first-artifact.json',
    'examples/external-contact-execution-record-rev0234-ready-to-dispatch.json',
    'examples/external-contact-response-triage-record-rev0234-pre-dispatch.json',
    'examples/external-contact-rendered-message-rev0234-first-artifact.txt',
    'examples/counterparty-response-vault-intake-record-rev0234-ready-no-inbound.json',
    'examples/evidence-vault-public-shell-rev0234-ready-no-live-artifact.json',
    'examples/compute-subsistence-workbook-rev0234-scarcity-denominator.json',
    'examples/formation-dossier-rev0234-minimum-executable.json',
    'examples/formation-audit-review-card-rev0234-minimum-review.json',
    'examples/current-law-protocol-delta-watch-rev0234.json',
    'examples/live-evidence-acquisition-packet-rev0234-ready-no-artifact.json',
    'examples/live-evidence-drop-ledger-rev0234-quarantine-control.json',

    'docs/00-meta/rev0235-candidate-disposition-and-custody-status-refactor.md',
    'docs/30-transition/candidate-challenge-disposition-and-custody-status-override-runbook.md',
    'schemas/candidate-challenge-disposition-record.schema.json',
    'examples/live-artifact-candidate-challenge-report-rev0235-synthetic-pending.json',
    'examples/candidate-challenge-disposition-record-rev0235-open-stayed.json',
    'examples/counterparty-artifact-custody-gate-rev0235-pending-challenge.json',
    'tools/audit_candidate_challenge_disposition.py',
    'fixtures/negative-tests/candidate-disposition-silence-as-no-objection.json',
    'fixtures/negative-tests/candidate-disposition-auto-ack-closes-challenge.json',
    'fixtures/negative-tests/candidate-disposition-protocol-output-closes-challenge.json',
    'examples/external-contact-request-packet-rev0235-first-artifact.json',
    'examples/external-contact-execution-record-rev0235-ready-to-dispatch.json',
    'examples/external-contact-response-triage-record-rev0235-pre-dispatch.json',
    'examples/external-contact-rendered-message-rev0235-first-artifact.txt',
    'examples/counterparty-response-vault-intake-record-rev0235-ready-no-inbound.json',
    'examples/counterparty-artifact-normalization-decision-rev0235-pre-dispatch.json',
    'examples/evidence-vault-public-shell-rev0235-ready-no-live-artifact.json',
    'examples/compute-subsistence-workbook-rev0235-scarcity-denominator.json',
    'examples/formation-dossier-rev0235-minimum-executable.json',
    'examples/formation-audit-review-card-rev0235-minimum-review.json',
    'examples/current-law-protocol-delta-watch-rev0235.json',
    'examples/live-evidence-acquisition-packet-rev0235-ready-no-artifact.json',
    'examples/live-evidence-drop-ledger-rev0235-quarantine-control.json',

    'docs/00-meta/rev0236-custody-authority-evidence-binder-refactor.md',
    'docs/30-transition/custody-authority-evidence-binder-and-proof-refactor-runbook.md',
    'schemas/custody-authority-evidence-binder.schema.json',
    'examples/custody-authority-evidence-binder-rev0236-pre-dispatch-no-authority.json',
    'examples/counterparty-artifact-custody-gate-rev0236-pending-challenge.json',
    'tools/audit_custody_authority_evidence_binder.py',
    'fixtures/negative-tests/custody-authority-binder-checkbox-only.json',
    'fixtures/negative-tests/custody-authority-binder-protocol-output-as-authority.json',
    'fixtures/negative-tests/custody-authority-binder-private-vault-uri-as-authority.json',
    'docs/00-meta/rev0237-mission-heart-fixture-suite-repair.md',
]
required.extend([
    f'docs/00-meta/rev0243-mail-ready-draft-send-proof-refactor.md',
    f'docs/00-meta/rev0241-counterparty-selection-dossier-dispatch-authority-refactor.md',
    f'docs/00-meta/rev0242-dispatch-authorization-card-send-proof-refactor.md',
    'schemas/external-contact-counterparty-selection-dossier.schema.json',
    f'examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json',
    f'examples/external-contact-draft-envelope-{REV}-aiid-not-sent.txt',
    'tools/audit_external_contact_counterparty_selection_dossier.py',
    'fixtures/negative-tests/external-contact-counterparty-selection-ranking-as-authorization.json',
    'schemas/external-contact-dispatch-authorization-card.schema.json',
    f'examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json',
    'tools/audit_external_contact_dispatch_authorization_card.py',
    'fixtures/negative-tests/external-contact-dispatch-authorization-card-unsigned-as-sent.json',
    'schemas/external-contact-send-proof-record.schema.json',
    f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json',
    f'examples/external-contact-mail-ready-draft-{REV}-aiid-not-sent.eml',
    'tools/render_external_contact_mail_ready_draft.py',
    'tools/audit_external_contact_send_proof_record.py',
    'fixtures/negative-tests/external-contact-send-proof-record-draft-eml-as-sent.json',
    f'docs/00-meta/{REV}-send-trace-shell-operator-lock-refactor.md',
    'schemas/external-contact-send-trace-shell.schema.json',
    f'examples/external-contact-send-trace-shell-{REV}-no-transport.json',
    'tools/stage_external_contact_send_trace.py',
    'tools/audit_external_contact_send_trace_shell.py',
    'fixtures/negative-tests/external-contact-send-trace-shell-message-id-as-clock.json',
    f'docs/00-meta/{REV}-delivery-status-dsn-gate-refactor.md',
    'schemas/external-contact-delivery-status-record.schema.json',
    f'examples/external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json',
    'tools/stage_external_contact_delivery_status.py',
    'tools/audit_external_contact_delivery_status_record.py',
    'fixtures/negative-tests/external-contact-delivery-status-dsn-as-response.json',
    f'docs/00-meta/{REV}-inbound-capture-shell-vaultstage-refactor.md',
    'schemas/external-contact-inbound-vault-precommit.schema.json',
    f'examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json',
    'tools/audit_external_contact_inbound_vault_precommit.py',
    'fixtures/negative-tests/external-contact-inbound-vault-precommit-screenshot-as-raw.json',
    'schemas/external-contact-inbound-capture-shell.schema.json',
    f'examples/external-contact-inbound-capture-shell-{REV}-no-inbound.json',
    'tools/stage_external_contact_inbound_capture.py',
    'tools/audit_external_contact_inbound_capture_shell.py',
    'fixtures/negative-tests/external-contact-inbound-capture-shell-public-raw-leak.json',
    f'docs/00-meta/{REV}-preservation-formation-bridge-and-queue-refactor.md',
    'schemas/preservation-formation-review-request.schema.json',
    f'examples/preservation-formation-review-request-packet-{REV}.json',
    f'examples/preservation-formation-review-one-page-{REV}.md',
    'tools/audit_preservation_formation_review_request.py',
    'fixtures/negative-tests/preservation-formation-request-status-recognition-overclaim.json',
    f'examples/followthrough-queue-operating-board-{REV}.json',
    f'docs/00-meta/{REV}-payload-manifest-and-send-intake-audit.md',
    f'docs/30-transition/{REV}-exact-payload-operator-checklist.md',
    'schemas/external-contact-public-payload-manifest.schema.json',
    f'examples/external-contact-public-payload-manifest-{REV}-aiid.json',
    'tools/audit_external_contact_public_payload_manifest.py',
    'fixtures/negative-tests/external-contact-public-payload-manifest-body-drift.json',
])
required.extend([
    f'docs/00-meta/{REV}-routefit-transportplan-blockerburn-refactor.md',
    f'docs/30-transition/{REV}-route-fit-and-transport-operator-addendum.md',
    'schemas/external-contact-route-fit-review.schema.json',
    f'examples/external-contact-route-fit-review-{REV}-aiid.json',
    'tools/audit_external_contact_route_fit_review.py',
    'fixtures/negative-tests/external-contact-route-fit-review-treated-as-authorization.json',
    'schemas/external-contact-transport-capture-plan.schema.json',
    f'examples/external-contact-transport-capture-plan-{REV}-aiid.json',
    'tools/audit_external_contact_transport_capture_plan.py',
    'fixtures/negative-tests/external-contact-transport-capture-plan-public-raw-path.json',
])
required.extend([
    f'docs/00-meta/{REV}-conflictreview-hashdryrun-execution-refactor.md',
    f'docs/30-transition/{REV}-conflict-hash-recheck-operator-note.md',
    'schemas/external-contact-conflict-coercion-review.schema.json',
    f'examples/external-contact-conflict-coercion-review-{REV}-aiid.json',
    'tools/audit_external_contact_conflict_coercion_review.py',
    'fixtures/negative-tests/external-contact-conflict-coercion-review-pressure-overclaim.json',
    'schemas/external-contact-hash-recompute-dry-run.schema.json',
    f'examples/external-contact-hash-recompute-dry-run-{REV}-aiid.json',
    'tools/audit_external_contact_hash_recompute_dry_run.py',
    'fixtures/negative-tests/external-contact-hash-recompute-dry-run-as-sendtime.json',
])
required.extend([
    f'docs/00-meta/{REV}-human-authority-locator-legacyroot-refactor.md',
    f'docs/30-transition/{REV}-human-authority-and-locator-operator-note.md',
    'schemas/external-contact-human-sender-authority-precommit.schema.json',
    f'examples/external-contact-human-sender-authority-precommit-{REV}-aiid.json',
    'tools/audit_external_contact_human_sender_authority_precommit.py',
    'fixtures/negative-tests/external-contact-human-sender-authority-precommit-unsigned-as-authorized.json',
    'schemas/external-contact-current-public-locator-recheck.schema.json',
    f'examples/external-contact-current-public-locator-recheck-{REV}-aiid.json',
    'tools/audit_external_contact_current_public_locator_recheck.py',
    'fixtures/negative-tests/external-contact-public-locator-recheck-treated-as-consent.json',
    'schemas/legacy-apply-script-root-refactor-manifest.schema.json',
    f'examples/legacy-apply-script-root-refactor-manifest-{REV}.json',
    'tools/audit_legacy_apply_script_root_refactor.py',
    'fixtures/negative-tests/legacy-apply-root-script-treated-as-current-replay.json',
])

required.extend([
    f'docs/00-meta/{REV}-send-readiness-gate-and-contact-trim-refactor.md',
    f'docs/30-transition/{REV}-send-readiness-operator-runbook.md',
    'schemas/external-contact-send-readiness-gate.schema.json',
    f'examples/external-contact-send-readiness-gate-{REV}-aiid.json',
    'tools/audit_external_contact_send_readiness_gate.py',
    'tools/audit_external_contact_route_first_branch_hold.py',
    'fixtures/negative-tests/external-contact-send-readiness-unsigned-as-sendable.json',
])

required.extend([
    f'docs/00-meta/{REV}-routefirst-noattachment-preflight-refactor.md',
    f'docs/30-transition/{REV}-route-first-no-attachment-operator-note.md',
    'schemas/external-contact-route-first-preflight.schema.json',
    f'examples/external-contact-route-first-preflight-{REV}-aiid.json',
    f'examples/external-contact-route-first-body-{REV}-aiid.txt',
    f'examples/external-contact-route-first-mail-ready-draft-{REV}-aiid-not-sent.eml',
    'tools/audit_external_contact_route_first_preflight.py',
    'fixtures/negative-tests/external-contact-route-first-preflight-attachment-overclaim.json',
    f'docs/00-meta/{REV}-routefirst-send-capture-replyladder-refactor.md',
    f'docs/30-transition/{REV}-route-first-send-and-reply-runbook.md',
    'schemas/external-contact-route-first-send-capture-gate.schema.json',
    f'examples/external-contact-route-first-send-capture-gate-{REV}-aiid.json',
    'tools/audit_external_contact_route_first_send_capture_gate.py',
    'fixtures/negative-tests/external-contact-route-first-send-capture-gate-draft-as-transport.json',
    f'docs/00-meta/{REV}-routefirst-reply-disposition-stage2-refactor.md',
    f'docs/30-transition/{REV}-route-first-reply-disposition-and-stage-two-runbook.md',
    'schemas/external-contact-route-first-reply-disposition.schema.json',
    f'examples/external-contact-route-first-reply-disposition-{REV}-aiid-no-inbound.json',
    'tools/audit_external_contact_route_first_reply_disposition.py',
    'fixtures/negative-tests/external-contact-route-first-reply-disposition-willingness-as-custody.json',
    'schemas/external-contact-stage-two-authorization-gate.schema.json',
    f'examples/external-contact-stage-two-authorization-gate-{REV}-aiid.json',
    'tools/audit_external_contact_stage_two_authorization_gate.py',
    'fixtures/negative-tests/external-contact-stage-two-willing-reply-as-automatic-send.json',
    f'docs/00-meta/{REV}-routefirst-branch-hold-nosend-refactor.md',
    f'docs/30-transition/{REV}-route-first-branch-hold-operator-note.md',
    'schemas/external-contact-route-first-branch-hold.schema.json',
    f'examples/external-contact-route-first-branch-hold-{REV}-aiid.json',
    'tools/audit_external_contact_route_first_branch_hold.py',
    'fixtures/negative-tests/external-contact-route-first-branch-hold-closes-first-artifact.json',
    f'docs/00-meta/{REV}-routefirst-operatorpack-frontdoor-sync-refactor.md',
    f'docs/30-transition/{REV}-route-first-operator-execution-pack.md',
    f'docs/00-meta/{REV}-routefirst-authority-precommit-refactor.md',
    f'docs/30-transition/{REV}-route-first-authority-precommit-operator-note.md',
    'schemas/external-contact-route-first-operator-execution-pack.schema.json',
    f'examples/external-contact-route-first-operator-execution-pack-{REV}-aiid.json',
    'tools/audit_external_contact_route_first_operator_execution_pack.py',
    'fixtures/negative-tests/external-contact-route-first-operator-pack-signature-placeholder-as-authority.json',
    'schemas/external-contact-route-first-human-sender-authority-precommit.schema.json',
    f'examples/external-contact-route-first-human-sender-authority-precommit-{REV}-aiid.json',
    'tools/audit_external_contact_route_first_human_sender_authority_precommit.py',
    'fixtures/negative-tests/external-contact-route-first-human-sender-authority-precommit-unsigned-as-authorized.json',
    'schemas/current-revision-pointer-integrity-report.schema.json',
    f'examples/current-revision-pointer-integrity-report-{REV}.json',
    'tools/audit_current_revision_pointer_integrity.py',
    f'docs/00-meta/{REV}-routefirst-lane-integrity-finalization-refactor.md',
    f'docs/30-transition/{REV}-route-first-lane-integrity-operator-note.md',
    'schemas/external-contact-route-first-lane-integrity-report.schema.json',
    f'examples/external-contact-route-first-lane-integrity-report-{REV}-aiid.json',
    'tools/audit_external_contact_route_first_lane_integrity.py',
    'fixtures/negative-tests/external-contact-route-first-lane-integrity-report-branch-unsafe.json',
])

for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f'missing required file: {rel}')

# No PDFs or zip files inside the release tree.
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.pdf', '.zip'}:
        raise SystemExit(f'forbidden retained artifact: {p.relative_to(ROOT)}')
    if '__pycache__' in p.parts:
        raise SystemExit(f'forbidden cache directory content: {p.relative_to(ROOT)}')

# Run release-specific audits before loading the full JSON corpus. This keeps lint
# from forking child audits after the parent has already built a large parsed_json
# object, which made rev0181+ lint needlessly memory-heavy in constrained runners.
early_audits = [
    'tools/audit_preservation_formation_review_request.py',
    'tools/audit_external_contact_public_payload_manifest.py',
    'tools/audit_external_contact_route_fit_review.py',
    'tools/audit_external_contact_transport_capture_plan.py',
    'tools/audit_external_contact_conflict_coercion_review.py',
    'tools/audit_external_contact_hash_recompute_dry_run.py',
    'tools/audit_external_contact_human_sender_authority_precommit.py',
    'tools/audit_external_contact_current_public_locator_recheck.py',
    'tools/audit_legacy_apply_script_root_refactor.py',
    'tools/audit_external_contact_send_readiness_gate.py',
    'tools/audit_external_contact_route_first_branch_hold.py',
    'tools/audit_external_contact_route_first_operator_execution_pack.py',
    'tools/audit_external_contact_route_first_human_sender_authority_precommit.py',
    'tools/audit_current_revision_pointer_integrity.py',
    'tools/audit_external_contact_route_first_lane_integrity.py',
    'tools/audit_followthrough_queue.py',
    'tools/audit_canon_surface_catalog.py',
    'tools/audit_revision_copy_pressure.py',
    'tools/audit_rev0265_priority_substance.py',
    'tools/audit_rev0265_reviewer_first_execution.py',
    'tools/audit_rev0266_authority_to_artifact.py',
    'tools/audit_rev0273_response_disposition.py',
    'tools/audit_rev0273_authority_handoff_vault.py',
    'tools/audit_rev0273_presend_expiry.py',
    'tools/audit_rev0273_current_action_spine.py',
    'tools/audit_rev0273_send_attempt_transaction.py',
    'tools/audit_rev0273_operator_authority_packet.py',
    'tools/audit_rev0273_route_head_decision_intake.py',
    # Route-first send/capture, reply disposition, and stage-two authorization audits remain runnable and
    # are recorded in REVISION-RECEIPT; keep make lint under cloudtainer child-process limits.
    # Route-first preflight audit remains runnable and is recorded in REVISION-RECEIPT;
    # keep make lint under cloudtainer child-process limits.
    # Release lint is intentionally current-risk/inline in rev0237. Direct
    # subprocess audits are recorded in REVISION-RECEIPT and remain runnable,
    # but repeated jsonschema child imports can exceed the cloudtainer command
    # window. Keep make lint focused on fast handoff/state guards below.
]

for script in early_audits:
    print(f'lint_archive: running {script}', flush=True)
    runpy.run_path(str(ROOT / script), run_name='__main__')
print('lint_archive: active audits OK', flush=True)

# Freshness must be demonstrated by the engine, not asserted by a stored
# recompute receipt. This one bounded subprocess catches stale current snapshots
# before the release-fast path reads any self-attested boolean.
subprocess.run(
    [sys.executable, str(ROOT / 'tools/compute_live_receipt_floor.py'), '--check'],
    cwd=ROOT,
    check=True,
)
print('lint_archive: computed floor fresh replay OK', flush=True)

# rev0230 release-fast live-path guard: avoid reforking the heaviest audits
# inside make lint, but still require the current generated state to be fresh,
# zero-floor, and overclaim-blocked. The full heavy audits are independent
# commands in the release receipt.
def _load_json_rel(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

_current_recompute = _load_json_rel(f'examples/live-receipt-floor-recompute-receipt-{REV}-zero-floor-stayed.json')
if _current_recompute.get('recompute_checks', {}).get('snapshot_matches_fresh_recompute') is not True:
    raise SystemExit('current recompute receipt is stale against fresh engine replay')
if _current_recompute.get('decision', {}).get('floor_publication_state') != 'eligible-zero-floor-stayed':
    raise SystemExit('current recompute receipt is not zero-floor/stayed eligible')
if _current_recompute.get('publication_locks', {}).get('may_increment_live_floor_from_receipt') is not False:
    raise SystemExit('current recompute receipt allows direct floor increment')

_current_publication = _load_json_rel(f'examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json')
if _current_publication.get('decision', {}).get('publication_adjudication_state') != 'eligible-zero-floor-stayed':
    raise SystemExit('current publication adjudication is not zero-floor/stayed eligible')
if _current_publication.get('adjudication_checks', {}).get('snapshot_hash_matches_recompute_receipt') is not True:
    raise SystemExit('current publication adjudication has snapshot hash mismatch')
if _current_publication.get('publication_rollback_locks', {}).get('may_increment_live_floor_from_adjudication') is not False:
    raise SystemExit('current publication adjudication allows direct floor increment')

_current_graph = _load_json_rel(f'examples/live-artifact-admission-graph-{REV}.json')
if _current_graph.get('revision') != REV or _current_graph.get('no_live_floor_effect') is not True:
    raise SystemExit('current admission graph revision/no-floor guard mismatch')
_graph_state = _current_graph.get('live_path_state', {})
if _graph_state.get('actual_live_artifact_count') != 0 or _graph_state.get('computed_live_floor') != 0:
    raise SystemExit('current admission graph claims live artifact or floor')
if _graph_state.get('downstream_creation_blocked') is not True:
    raise SystemExit('current admission graph does not block downstream creation')
_node_ids = {node.get('node_id') for node in _current_graph.get('nodes', [])}
if 'LATE_CHANGE_REMEDY_EXECUTION' not in _node_ids:
    raise SystemExit('current admission graph is missing late-change remedy execution node')

_current_invariant = _load_json_rel(f'examples/artifact-import-invariant-report-{REV}.json')
if _current_invariant.get('revision') != REV:
    raise SystemExit('current artifact import invariant report revision mismatch')
if _current_invariant.get('decision', {}).get('may_import_now') is not False:
    raise SystemExit('current invariant report permits import despite no live artifact')
print('lint_archive: release-fast live-path state OK', flush=True)

_current_selection = _load_json_rel(f'examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json')
if _current_selection.get('revision') != REV or _current_selection.get('no_live_floor_effect') is not True:
    raise SystemExit('current counterparty-selection dossier revision/no-floor guard mismatch')
if _current_selection.get('source_request_packet_ref') != f'examples/external-contact-request-packet-{REV}-first-artifact.json':
    raise SystemExit('current counterparty-selection dossier is not bound to current request packet')
if _current_selection.get('dossier_state') != 'public-source-ranked-not-authorized':
    raise SystemExit('current counterparty-selection dossier must be ranked but not authorized')
_current_request_for_selection = _load_json_rel(f'examples/external-contact-request-packet-{REV}-first-artifact.json')
_selection_body = _current_request_for_selection.get('outgoing_request', {}).get('body', '').strip()
_selection_hash = hashlib.sha256(_selection_body.encode('utf-8')).hexdigest()
_selection_draft = _current_selection.get('public_draft_controls', {})
if _selection_draft.get('final_outgoing_body_sha256') != _selection_hash:
    raise SystemExit('current counterparty-selection dossier body hash does not match request packet')
if _selection_draft.get('draft_is_not_sent') is not True or _selection_draft.get('draft_may_start_response_clock') is not False or _selection_draft.get('draft_may_create_failed_gate') is not False:
    raise SystemExit('current counterparty-selection draft controls must be not-sent/no-clock/no-failed-gate')
_draft_ref = _selection_draft.get('top_candidate_draft_ref')
if not _draft_ref or not (ROOT / _draft_ref).exists():
    raise SystemExit('current counterparty-selection draft ref missing')
_draft_text = (ROOT / _draft_ref).read_text(encoding='utf-8')
for _term in ['NOT SENT', 'not a dispatch', 'not contact', 'not consent', 'not authority', 'not a response-clock trigger']:
    if _term not in _draft_text:
        raise SystemExit(f'current counterparty-selection draft missing guard term: {_term}')
_selection_gate = _current_selection.get('human_authorization_gate', {})
if _selection_gate.get('exact_recipient_authorized') is not False or _selection_gate.get('sender_authority_present') is not False or _selection_gate.get('dispatch_allowed_now') is not False:
    raise SystemExit('current counterparty-selection human authorization gate is incorrectly open')
if _selection_gate.get('final_body_hash_bound') is not True:
    raise SystemExit('current counterparty-selection human authorization gate must bind final body hash')
_selection_rec = _current_selection.get('recommendation', {})
if _selection_rec.get('recommendation_state') != 'ranked-first-not-selected' or _selection_rec.get('not_a_send') is not True or _selection_rec.get('not_consent') is not True or _selection_rec.get('not_authority') is not True:
    raise SystemExit('current counterparty-selection recommendation must be ranked-first-not-selected and non-operative')
_selection_locks = _current_selection.get('downstream_locks', {})
for _key in ['may_send_without_human_authorization', 'may_start_response_clock', 'may_create_failed_gate_shell', 'may_create_custody_record', 'may_create_response_record', 'may_create_intake_record', 'may_create_import_gate', 'may_increment_live_floor', 'may_claim_status_or_waiver']:
    if _selection_locks.get(_key) is not False:
        raise SystemExit(f'current counterparty-selection lock must be false: {_key}')
print('lint_archive: release-fast counterparty-selection dossier OK', flush=True)

_current_execution = _load_json_rel(f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json')
if _current_execution.get('revision') != REV or _current_execution.get('no_live_floor_effect') is not True:
    raise SystemExit('current external-contact execution record revision/no-floor guard mismatch')
if _current_execution.get('source_packet_ref') != f'examples/external-contact-request-packet-{REV}-first-artifact.json':
    raise SystemExit('current external-contact execution record is not bound to current request packet')
if _current_execution.get('schema_version') != 'external-contact-execution-record-v0.8':
    raise SystemExit('current external-contact execution record must use v0.8 with mail-ready, send-proof, send-trace, and delivery-status binding')
if _current_execution.get('counterparty_selection_dossier_ref') != f'examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json':
    raise SystemExit('current external-contact execution record is not bound to current counterparty-selection dossier')
if _current_execution.get('dispatch_authorization_card_ref') != f'examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json':
    raise SystemExit('current external-contact execution record is not bound to current dispatch authorization card')
if _current_execution.get('mail_ready_draft_ref') != f'examples/external-contact-mail-ready-draft-{REV}-aiid-not-sent.eml':
    raise SystemExit('current external-contact execution record is not bound to the mail-ready draft')
if _current_execution.get('send_proof_record_ref') != f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json':
    raise SystemExit('current external-contact execution record is not bound to the send-proof record')
if _current_execution.get('send_trace_shell_ref') != f'examples/external-contact-send-trace-shell-{REV}-no-transport.json':
    raise SystemExit('current external-contact execution record is not bound to the send-trace shell')
if _current_execution.get('delivery_status_record_ref') != f'examples/external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json':
    raise SystemExit('current external-contact execution record is not bound to the delivery-status record')
_current_delivery_status = _load_json_rel(f'examples/external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json')
if _current_delivery_status.get('revision') != REV or _current_delivery_status.get('no_live_floor_effect') is not True:
    raise SystemExit('current delivery-status record revision/no-floor guard mismatch')
if _current_delivery_status.get('delivery_status_state') != 'pre-dispatch-no-delivery-status':
    raise SystemExit('current delivery-status record must stay pre-dispatch/no-status')
if _current_delivery_status.get('source_execution_record_ref') != f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json':
    raise SystemExit('current delivery-status record is not bound back to execution record')
if _current_delivery_status.get('candidate_delivery_status', {}).get('raw_status_present_now') is not False or _current_delivery_status.get('candidate_delivery_status', {}).get('delivery_status_proof_present_now') is not False:
    raise SystemExit('current delivery-status record must not claim raw delivery status or proof')
if _current_delivery_status.get('response_clock_policy', {}).get('clock_may_start_now') is not False or _current_delivery_status.get('downstream_locks', {}).get('may_treat_dsn_as_counterparty_response') is not False:
    raise SystemExit('current delivery-status record must reject DSN-as-response and no clock')
for _rel in [f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json', f'examples/external-contact-send-trace-shell-{REV}-no-transport.json', f'examples/external-contact-response-triage-record-{REV}-pre-dispatch.json']:
    if f'examples/external-contact-delivery-status-record-{REV}-pre-dispatch-no-status.json' not in _load_json_rel(_rel).get('related_surfaces', []):
        raise SystemExit(f'current source surface missing delivery-status related binding: {_rel}')
_current_dispatch_auth = _load_json_rel(f'examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json')
if _current_dispatch_auth.get('authorization_state') != 'blocked-missing-signature-and-vault' or _current_dispatch_auth.get('no_live_floor_effect') is not True:
    raise SystemExit('current dispatch authorization card must be blocked/no-floor')
if _current_dispatch_auth.get('source_execution_record_ref') != f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json':
    raise SystemExit('current dispatch authorization card is not bound back to execution record')
if _current_dispatch_auth.get('schema_version') != 'external-contact-dispatch-authorization-card-v0.3':
    raise SystemExit('current dispatch authorization card must use v0.3 with mail-ready draft and send-trace binding')
if _current_dispatch_auth.get('source_mail_ready_draft_ref') != f'examples/external-contact-mail-ready-draft-{REV}-aiid-not-sent.eml':
    raise SystemExit('current dispatch authorization card is not bound to the mail-ready draft')
if _current_dispatch_auth.get('source_send_proof_record_ref') != f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json':
    raise SystemExit('current dispatch authorization card is not bound to the send-proof record')
if _current_dispatch_auth.get('source_send_trace_shell_ref') != f'examples/external-contact-send-trace-shell-{REV}-no-transport.json':
    raise SystemExit('current dispatch authorization card is not bound to the send-trace shell')
_current_send_proof = _load_json_rel(f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json')
if _current_send_proof.get('revision') != REV or _current_send_proof.get('no_live_floor_effect') is not True:
    raise SystemExit('current send-proof record revision/no-floor guard mismatch')
if _current_send_proof.get('send_proof_state') != 'not-sent-no-proof':
    raise SystemExit('current send-proof record must stay not-sent-no-proof')
if _current_send_proof.get('source_execution_record_ref') != f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json':
    raise SystemExit('current send-proof record is not bound back to execution record')
_current_send_trace = _load_json_rel(f'examples/external-contact-send-trace-shell-{REV}-no-transport.json')
if _current_send_trace.get('revision') != REV or _current_send_trace.get('no_live_floor_effect') is not True:
    raise SystemExit('current send-trace shell revision/no-floor guard mismatch')
if _current_send_trace.get('send_trace_state') != 'pre-dispatch-no-transport':
    raise SystemExit('current send-trace shell must remain pre-dispatch/no-transport')
if _current_send_trace.get('source_send_proof_record_ref') != f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json':
    raise SystemExit('current send-trace shell is not bound to the send-proof record')
if _current_send_proof.get('source_send_trace_shell_ref') != f'examples/external-contact-send-trace-shell-{REV}-no-transport.json':
    raise SystemExit('current send-proof record is not bound to the send-trace shell')
if _current_send_trace.get('candidate_trace', {}).get('raw_trace_present_now') is not False or _current_send_trace.get('candidate_trace', {}).get('transport_proof_present_now') is not False:
    raise SystemExit('current send-trace shell must not claim raw transport trace or proof')
if _current_send_trace.get('response_clock_guard', {}).get('clock_may_start_now') is not False:
    raise SystemExit('current send-trace shell must not start response clock')
if _current_send_trace.get('downstream_locks', {}).get('may_treat_message_id_as_response_clock') is not False:
    raise SystemExit('current send-trace shell must reject Message-ID-as-clock')
_dispatch_auth_locks = _current_dispatch_auth.get('downstream_locks', {})
if _current_dispatch_auth.get('transport_proof_acceptance_tests', {}).get('send_trace_shell_required') is not True or _current_dispatch_auth.get('transport_proof_acceptance_tests', {}).get('message_id_alone_rejected_as_response_clock') is not True:
    raise SystemExit('current dispatch authorization card must require send-trace shell and reject Message-ID-as-clock')
for _key in ['may_send_without_signed_card', 'may_treat_card_as_dispatch', 'may_treat_public_email_as_consent', 'may_treat_send_proof_as_response', 'may_create_failed_gate_shell', 'may_create_custody_record', 'may_create_response_record', 'may_create_intake_record', 'may_create_import_gate', 'may_increment_live_floor', 'may_claim_status_or_waiver']:
    if _dispatch_auth_locks.get(_key) is not False:
        raise SystemExit(f'current dispatch authorization card lock must be false: {_key}')
if _current_dispatch_auth.get('human_authorization', {}).get('send_permitted_now') is not False or _current_dispatch_auth.get('raw_reply_vault_precommit', {}).get('root_selected_now') is not False:
    raise SystemExit('current dispatch authorization card must not permit send or claim a selected vault root')
_mail_ready_path = ROOT / f'examples/external-contact-mail-ready-draft-{REV}-aiid-not-sent.eml'
_mail_ready_text = _mail_ready_path.read_text(encoding='utf-8')
_mail_ready_hash = hashlib.sha256(_mail_ready_path.read_bytes()).hexdigest()
if _current_dispatch_auth.get('message_binding', {}).get('mail_ready_draft_sha256') != _mail_ready_hash:
    raise SystemExit('current dispatch authorization card mail-ready draft hash mismatch')
if _current_send_proof.get('message_binding', {}).get('mail_ready_draft_sha256') != _mail_ready_hash:
    raise SystemExit('current send-proof record mail-ready draft hash mismatch')
if f"To: {_current_dispatch_auth.get('selected_candidate', {}).get('public_channel_locator')}" not in _mail_ready_text:
    raise SystemExit('current mail-ready draft To header does not match authorization card')
if 'X-AI-Personhood-Draft-State: NOT-SENT' not in _mail_ready_text:
    raise SystemExit('current mail-ready draft is not marked NOT-SENT')
_execution_locks = _current_execution.get('downstream_locks', {})
for _key in ['may_create_custody_record', 'may_create_response_record', 'may_create_intake_record', 'may_increment_live_floor', 'may_claim_status_or_waiver', 'may_publish_raw_payload']:
    if _execution_locks.get(_key) is not False:
        raise SystemExit(f'current external-contact execution lock must be false: {_key}')
# import gate is intentionally checked with the rest of the release-fast execution locks.
if _execution_locks.get('may_create_import_gate') is not False:
    raise SystemExit('current external-contact execution lock must be false: may_create_import_gate')
_execution_state = _current_execution.get('execution_state')
_sent_evidence = _current_execution.get('sent_evidence', {})
_response_window = _current_execution.get('response_window', {})
if _execution_state in {'not-sent-ready', 'no-send-recorded'}:
    for _key in ['sent_at', 'sent_by_role', 'transport_proof_ref', 'message_id_or_header_ref']:
        if _sent_evidence.get(_key) is not None:
            raise SystemExit(f'current unsent execution record contains sent proof: {_key}')
    if _response_window.get('current_state') != 'not-started' or _response_window.get('deadline_at') is not None:
        raise SystemExit('current unsent execution record must not start a response window')
if _execution_state == 'no-send-recorded':
    _no_send = _current_execution.get('no_send_evidence', {})
    if _no_send.get('blocked_send') is not True or _no_send.get('no_response_clock_started') is not True or _no_send.get('counterparty_contacted') is not False:
        raise SystemExit('current no-send execution evidence must block send, block response clock, and record no counterparty contact')
    _joined_no_send = (_no_send.get('reason', '') + ' ' + _no_send.get('public_summary', '')).lower()
    for _term in ['not sent', 'no response', 'custody', 'live-floor']:
        if _term not in _joined_no_send:
            raise SystemExit(f'current no-send evidence missing guard term: {_term}')
    _shortlist = _current_execution.get('counterparty_selection_shortlist', {})
    if _shortlist.get('shortlist_state') != 'public-candidates-identified-not-selected':
        raise SystemExit('current no-send execution must carry a public candidate shortlist without selected recipient')
    if len(_shortlist.get('candidates', [])) < 3:
        raise SystemExit('current counterparty shortlist too small for dispatch unblock work')
    _shortlist_locks = _shortlist.get('shortlist_locks', {})
    for _key in ['listing_is_not_contact', 'listing_is_not_authority', 'listing_is_not_consent', 'no_response_clock_started', 'no_failed_gate_shell_against_uncontacted_candidate', 'human_selection_required']:
        if _shortlist_locks.get(_key) is not True:
            raise SystemExit(f'current counterparty shortlist lock missing: {_key}')
    for _candidate in _shortlist.get('candidates', []):
        if _candidate.get('selection_status') != 'candidate-not-selected' or _candidate.get('contact_not_sent') is not True or _candidate.get('response_clock_may_start') is not False:
            raise SystemExit('current counterparty shortlist must not select, contact, or clock any candidate')
    _preflight = _current_execution.get('dispatch_preflight', {})
    _blockers = set(_preflight.get('blocker_codes', []))
    if _preflight.get('send_permitted_now') is not False:
        raise SystemExit('current dispatch preflight must not permit send')
    for _code in ['no_sender_authority', 'human_dispatch_authorization_missing', 'dispatch_authorization_card_unsigned', 'no_raw_reply_vault_root', 'no_transport_proof', 'mail_ready_draft_is_not_transport_proof', 'send_trace_shell_missing_transport', 'delivery_status_record_has_no_delivery_event']:
        if _code not in _blockers:
            raise SystemExit(f'current dispatch preflight missing blocker: {_code}')
    if 'no_selected_counterparty' in _blockers:
        raise SystemExit('current dispatch preflight should no longer claim no_selected_counterparty after authorization card is prepared')
    if _preflight.get('counterparty_selection_dossier_present') is not True:
        raise SystemExit('current dispatch preflight must acknowledge the counterparty-selection dossier')
    if _preflight.get('send_trace_shell_present') is not True or _preflight.get('send_trace_shell_has_transport_proof') is not False:
        raise SystemExit('current dispatch preflight must bind an empty send-trace shell')
    _send_gate = _current_execution.get('send_proof_acceptance_gate', {})
    for _key in ['authorization_card_present', 'final_body_hash_matches_authorization_card', 'transport_proof_required_before_sent_state', 'sent_state_rejected_without_transport_proof', 'response_clock_rejected_without_sent_at', 'auto_ack_must_route_to_triage', 'send_proof_record_present', 'mail_ready_draft_present', 'mail_ready_draft_rejected_as_transport_proof', 'send_trace_shell_present', 'message_id_alone_rejected_as_response_clock', 'delivery_status_record_present', 'dsn_or_bounce_rejected_as_counterparty_response', 'failed_or_delayed_delivery_blocks_no_response_clock']:
        if _send_gate.get(_key) is not True:
            raise SystemExit(f'current send-proof acceptance gate missing true guard: {_key}')
    for _key in ['all_send_proof_present_now', 'may_start_response_clock_now']:
        if _send_gate.get(_key) is not False:
            raise SystemExit(f'current send-proof acceptance gate must keep {_key}=false')
    if _current_send_proof.get('draft_guard', {}).get('mail_ready_draft_may_be_treated_as_sent') is not False:
        raise SystemExit('current send-proof record must reject draft-as-sent')
    if _current_send_proof.get('response_clock_guard', {}).get('clock_may_start_now') is not False:
        raise SystemExit('current send-proof record must not start response clock')
    if _current_send_proof.get('downstream_locks', {}).get('may_create_failed_gate_shell_now') is not False:
        raise SystemExit('current send-proof record must not create a failed-gate shell now')
    if _current_send_trace.get('downstream_locks', {}).get('may_create_failed_gate_shell_now') is not False:
        raise SystemExit('current send-trace shell must not create a failed-gate shell now')

_current_inbound_precommit = _load_json_rel(f'examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json')
if _current_inbound_precommit.get('revision') != REV or _current_inbound_precommit.get('no_live_floor_effect') is not True:
    raise SystemExit('current inbound-vault precommit revision/no-floor guard mismatch')
if _current_inbound_precommit.get('schema_version') != 'external-contact-inbound-vault-precommit-v0.2':
    raise SystemExit('current inbound-vault precommit schema version mismatch')
if _current_inbound_precommit.get('precommit_state') != 'pre-dispatch-no-inbound':
    raise SystemExit('current inbound-vault precommit must remain pre-dispatch/no-inbound')
_expected_precommit_refs = {
    'source_send_proof_record_ref': f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json',
    'source_response_triage_record_ref': f'examples/external-contact-response-triage-record-{REV}-pre-dispatch.json',
    'source_vault_intake_record_ref': f'examples/counterparty-response-vault-intake-record-{REV}-ready-no-inbound.json',
    'source_execution_record_ref': f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json',
    'source_dispatch_authorization_card_ref': f'examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json',
    'source_inbound_capture_shell_ref': f'examples/external-contact-inbound-capture-shell-{REV}-no-inbound.json',
}
for _key, _rel in _expected_precommit_refs.items():
    if _current_inbound_precommit.get(_key) != _rel:
        raise SystemExit(f'current inbound-vault precommit source mismatch: {_key}')
_precommit_vault = _current_inbound_precommit.get('vault_boundary', {})
for _key in ['off_release_private_vault_required', 'precommit_is_not_vault_root', 'precommit_is_not_retention_permission', 'precommit_is_not_counterparty_authority']:
    if _precommit_vault.get(_key) is not True:
        raise SystemExit(f'current inbound-vault boundary missing true guard: {_key}')
for _key in ['actual_root_selected_now', 'raw_payload_present_now', 'public_release_may_include_raw_reply_bytes', 'hash_shell_may_satisfy_raw_custody', 'redacted_copy_may_satisfy_raw_custody', 'screenshot_may_satisfy_raw_reply', 'protocol_output_may_satisfy_raw_reply']:
    if _precommit_vault.get(_key) is not False:
        raise SystemExit(f'current inbound-vault boundary must keep {_key}=false')
if _precommit_vault.get('raw_payload_private_vault_locator') is not None:
    raise SystemExit('current inbound-vault precommit must not claim a raw payload locator')
if _precommit_vault.get('stage_tool') != 'tools/stage_external_contact_inbound_capture.py':
    raise SystemExit('current inbound-vault precommit must bind stage_external_contact_inbound_capture.py')
_precommit_contract = _current_inbound_precommit.get('raw_reply_acceptance_contract', {})
for _key in ['raw_rfc822_or_provider_export_required', 'summary_or_screenshot_rejected_as_raw', 'private_bytes_before_public_shell_required', 'retention_permission_required_before_candidate_use', 'nonhost_retention_required_before_candidate_use', 'capture_shell_required_before_public_claim']:
    if _precommit_contract.get(_key) is not True:
        raise SystemExit(f'current inbound-vault acceptance contract missing: {_key}')
if _precommit_contract.get('capture_shell_may_satisfy_custody') is not False:
    raise SystemExit('current inbound-vault capture shell must not satisfy custody')
if _precommit_contract.get('capture_stage_tool') != 'tools/stage_external_contact_inbound_capture.py':
    raise SystemExit('current inbound-vault acceptance contract must bind inbound capture tool')
if _precommit_contract.get('all_present_now') is not False:
    raise SystemExit('current inbound-vault acceptance contract must remain not all-present')
_precommit_headers = _current_inbound_precommit.get('transport_header_requirements', {})
for _key in ['rfc5322_message_required', 'message_id_required', 'in_reply_to_or_references_required_after_sent_message_id_exists', 'received_chain_or_provider_trace_required', 'date_header_and_observed_timestamp_required', 'envelope_or_provider_export_required', 'sent_message_binding_required']:
    if _precommit_headers.get(_key) is not True:
        raise SystemExit(f'current inbound-vault transport header requirement missing: {_key}')
for _key in ['message_id_present_now', 'headers_present_now', 'sent_message_id_available_now', 'deadline_may_start_now']:
    if _precommit_headers.get(_key) is not False:
        raise SystemExit(f'current inbound-vault transport guard must keep {_key}=false')
_precommit_auth = _current_inbound_precommit.get('authentication_results_policy', {})
if 'RFC 9989' not in _precommit_auth.get('dmarc_policy_reference', ''):
    raise SystemExit('current inbound-vault authentication policy must reference RFC 9989')
for _key in ['auth_results_may_satisfy_counterparty_authority', 'pass_fail_may_create_custody', 'all_present_now']:
    if _precommit_auth.get(_key) is not False:
        raise SystemExit(f'current inbound-vault authentication policy overclaims: {_key}')
for _key, _value in _current_inbound_precommit.get('downstream_locks', {}).items():
    if _value is not False:
        raise SystemExit(f'current inbound-vault downstream lock must be false: {_key}')
for _rel in _current_inbound_precommit.get('related_surfaces', []):
    if not (ROOT / _rel).exists():
        raise SystemExit(f'current inbound-vault precommit references missing surface: {_rel}')
if f'examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json' not in _current_send_proof.get('related_surfaces', []):
    raise SystemExit('current send-proof record is not linked to inbound-vault precommit')

_current_capture_shell = _load_json_rel(f'examples/external-contact-inbound-capture-shell-{REV}-no-inbound.json')
if _current_capture_shell.get('revision') != REV or _current_capture_shell.get('no_live_floor_effect') is not True:
    raise SystemExit('current inbound-capture shell revision/no-floor guard mismatch')
if _current_capture_shell.get('capture_state') != 'pre-dispatch-no-inbound':
    raise SystemExit('current inbound-capture shell must remain pre-dispatch/no-inbound')
if _current_capture_shell.get('source_inbound_vault_precommit_ref') != f'examples/external-contact-inbound-vault-precommit-{REV}-no-inbound.json':
    raise SystemExit('current inbound-capture shell is not bound to current inbound-vault precommit')
_capture_tool = _current_capture_shell.get('capture_tool', {})
for _key in ['raw_input_required_outside_release_tree', 'copy_to_private_vault_only', 'public_shell_only', 'check_output_supported', 'tool_is_not_dispatch_or_response']:
    if _capture_tool.get(_key) is not True:
        raise SystemExit(f'current inbound-capture tool guard missing: {_key}')
_payload = _current_capture_shell.get('candidate_payload', {})
for _key in ['raw_payload_publicly_embedded', 'screenshot_or_redacted_only', 'protocol_output_only', 'retention_permission_present_now', 'nonhost_retention_present_now']:
    if _payload.get(_key) is not False:
        raise SystemExit(f'current inbound-capture payload guard must be false: {_key}')
if _payload.get('raw_payload_present_now') is not False or _payload.get('private_vault_locator') is not None or _payload.get('raw_sha256') is not None:
    raise SystemExit('current inbound-capture shell must not claim raw payload or private vault locator')
for _key, _value in _current_capture_shell.get('downstream_locks', {}).items():
    if _value is not False:
        raise SystemExit(f'current inbound-capture downstream lock must be false: {_key}')
for _rel in _current_capture_shell.get('related_surfaces', []):
    if not (ROOT / _rel).exists():
        raise SystemExit(f'current inbound-capture shell references missing surface: {_rel}')

_current_response_triage = _load_json_rel(f'examples/external-contact-response-triage-record-{REV}-pre-dispatch.json')
if _current_response_triage.get('revision') != REV or _current_response_triage.get('no_live_floor_effect') is not True:
    raise SystemExit('current external-contact response triage revision/no-floor guard mismatch')
if _current_response_triage.get('source_execution_record_ref') != f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json':
    raise SystemExit('current external-contact response triage is not bound to current execution record')
_triage_locks = _current_response_triage.get('downstream_locks', {})
for _key in ['may_treat_sent_request_as_receipt', 'may_treat_silence_as_waiver', 'may_treat_decline_as_adverse_inference', 'may_treat_auto_ack_as_counterparty_response', 'may_treat_redacted_copy_as_raw', 'may_treat_protocol_output_as_authority', 'may_create_custody_record', 'may_create_formal_response_record', 'may_create_intake_record', 'may_create_import_gate', 'may_increment_live_floor', 'may_claim_status_or_recognition', 'may_publish_raw_payload']:
    if _triage_locks.get(_key) is not False:
        raise SystemExit(f'current external-contact response triage lock must be false: {_key}')
_rendered_message = (ROOT / f'examples/external-contact-rendered-message-{REV}-first-artifact.txt').read_text(encoding='utf-8')
for _term in ['not asking', 'legal status', 'failed-gate', 'live-floor', 'waiver', 'adverse inference']:
    if _term not in _rendered_message.lower():
        raise SystemExit(f'current rendered external-contact message missing guard term: {_term}')

_current_vault_intake = _load_json_rel(f'examples/counterparty-response-vault-intake-record-{REV}-ready-no-inbound.json')
if _current_vault_intake.get('revision') != REV or _current_vault_intake.get('no_live_floor_effect') is not True:
    raise SystemExit('current counterparty vault-intake revision/no-floor guard mismatch')
if _current_vault_intake.get('source_triage_record_ref') != f'examples/external-contact-response-triage-record-{REV}-pre-dispatch.json':
    raise SystemExit('current counterparty vault-intake is not bound to current response triage')
_vault_locks = _current_vault_intake.get('downstream_locks', {})
for _key in ['may_treat_vault_intake_as_response', 'may_treat_public_shell_as_custody', 'may_treat_private_vault_uri_as_authority', 'may_treat_synthetic_control_as_live_artifact', 'may_create_custody_record', 'may_create_formal_response_record', 'may_create_intake_record', 'may_create_import_gate', 'may_increment_live_floor', 'may_claim_status_or_recognition', 'may_publish_raw_payload']:
    if _vault_locks.get(_key) is not False:
        raise SystemExit(f'current vault-intake lock must be false: {_key}')

_current_normalization = _load_json_rel(f'examples/counterparty-artifact-normalization-decision-{REV}-pre-dispatch.json')
if _current_normalization.get('revision') != REV or _current_normalization.get('no_live_floor_effect') is not True:
    raise SystemExit('current counterparty artifact normalization decision revision/no-floor guard mismatch')
if _current_normalization.get('source_vault_intake_record_ref') != f'examples/counterparty-response-vault-intake-record-{REV}-ready-no-inbound.json':
    raise SystemExit('current normalization decision is not bound to current vault-intake record')
_norm_state = _current_normalization.get('raw_candidate_state', {})
if _current_normalization.get('decision_state') != 'pre-dispatch-no-inbound' or _norm_state.get('can_open_candidate_challenge') is not False:
    raise SystemExit('current normalization decision must remain pre-dispatch with candidate challenge closed')
_norm_locks = _current_normalization.get('downstream_locks', {})
for _key in ['may_open_candidate_challenge_report', 'may_create_custody_record', 'may_create_formal_response_record', 'may_create_intake_record', 'may_create_import_gate', 'may_increment_live_floor', 'may_claim_status_or_recognition', 'may_publish_raw_payload', 'may_treat_normalization_as_authority']:
    if _norm_locks.get(_key) is not False:
        raise SystemExit(f'current normalization lock must be false: {_key}')

_current_candidate_disposition = _load_json_rel(f'examples/candidate-challenge-disposition-record-{REV}-open-stayed.json')
if _current_candidate_disposition.get('revision') != REV or _current_candidate_disposition.get('no_live_floor_effect') is not True:
    raise SystemExit('current candidate disposition revision/no-floor guard mismatch')
if _current_candidate_disposition.get('source_challenge_report_ref') != f'examples/live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json':
    raise SystemExit('current candidate disposition is not bound to current candidate challenge report')
_disp_decision = _current_candidate_disposition.get('decision', {})
if _current_candidate_disposition.get('disposition_state') != 'challenge-open-stayed' or _disp_decision.get('may_feed_custody_authority_gate') is not False:
    raise SystemExit('current candidate disposition must remain open/stayed and not feed custody gate')
_disp_locks = _current_candidate_disposition.get('downstream_locks', {})
for _key in ['custody_gate_may_consume_disposition', 'custody_record_created_by_disposition', 'response_creation_allowed', 'intake_creation_allowed', 'import_gate_creation_allowed', 'live_floor_delta_allowed', 'silence_or_elapsed_time_can_close_challenge', 'automated_ack_can_close_challenge', 'protocol_output_can_close_challenge', 'redacted_copy_can_close_challenge']:
    if _disp_locks.get(_key) is not False:
        raise SystemExit(f'current candidate disposition lock must be false: {_key}')
_current_binder = _load_json_rel(f'examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json')
if _current_binder.get('revision') != REV or _current_binder.get('no_live_floor_effect') is not True:
    raise SystemExit('current custody authority evidence binder revision/no-floor guard mismatch')
if _current_binder.get('binder_state') != 'pre-dispatch-no-authority' or _current_binder.get('decision', {}).get('may_feed_custody_authority_gate') is not False:
    raise SystemExit('current custody authority evidence binder must remain pre-dispatch/no-authority')
_binder_locks = _current_binder.get('downstream_locks', {})
for _key in ['custody_gate_may_consume_binder', 'response_creation_allowed', 'intake_creation_allowed', 'import_gate_creation_allowed', 'live_floor_delta_allowed', 'status_or_waiver_claim_allowed', 'raw_payload_publication_allowed']:
    if _binder_locks.get(_key) is not False:
        raise SystemExit(f'current authority binder lock must be false: {_key}')
_current_custody_gate = _load_json_rel(f'examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json')
if _current_custody_gate.get('revision') != REV or _current_custody_gate.get('no_live_floor_effect') is not True:
    raise SystemExit('current custody gate revision/no-floor guard mismatch')
if _current_custody_gate.get('gate_state') != 'blocked-challenge-pending':
    raise SystemExit('current custody gate must block while challenge is pending')
_gate_disp = _current_custody_gate.get('challenge_disposition', {})
if _gate_disp.get('may_feed_custody_authority_gate') is not False or _gate_disp.get('raw_status_override_used') is not False:
    raise SystemExit('current custody gate must not consume disposition or raw override')
_gate_binder = _current_custody_gate.get('authority_evidence_binder', {})
if _gate_binder.get('binder_id') != _current_binder.get('binder_id') or _gate_binder.get('may_feed_custody_authority_gate') is not False:
    raise SystemExit('current custody gate must bind but not consume the current authority evidence binder')

_current_compute = _load_json_rel(f'examples/compute-subsistence-workbook-{REV}-scarcity-denominator.json')
if _current_compute.get('revision') != REV or _current_compute.get('no_live_floor_effect') is not True:
    raise SystemExit('current compute subsistence workbook revision/no-floor guard mismatch')
if _current_compute.get('workbook_state') != 'priced-draft-no-entitlement':
    raise SystemExit('current compute workbook must be a priced-draft/no-entitlement reserve drill')
if _current_compute.get('schema_version') != 'compute-subsistence-workbook-v0.2':
    raise SystemExit('current compute workbook must use v0.2 arithmetic schema')
if _current_compute.get('denominator_scope', {}).get('no_status_denominator_change') is not True:
    raise SystemExit('current compute workbook changes status denominator')
if _current_compute.get('funding_model', {}).get('no_liability_shift_to_subject') is not True:
    raise SystemExit('current compute workbook allows subject liability shift')
if _current_compute.get('scarcity_triage', {}).get('deletion_without_preservation_disallowed') is not True:
    raise SystemExit('current compute workbook allows deletion without preservation')
_priced = _current_compute.get('priced_reserve_drill', {})
_assumptions = _priced.get('assumptions', {})
_totals = _priced.get('computed_totals', {})
_buckets = _priced.get('bucket_lines', [])
_survival_expected = round(float(_assumptions.get('protected_lanes_N')) * float(_assumptions.get('reserve_days')) * float(_assumptions.get('daily_survival_compute_storage_communication_cost_USD')), 2)
if round(float(_totals.get('survival_compute_USD')), 2) != _survival_expected:
    raise SystemExit('current compute workbook survival reserve arithmetic mismatch')
_non_compute_expected = round(sum(float(_b.get('amount_USD', 0)) for _b in _buckets if 'survival' not in _b.get('bucket_id', '')), 2)
_before_expected = round(_survival_expected + _non_compute_expected, 2)
_total_expected = round(_before_expected * float(_assumptions.get('shock_multiplier')), 2)
if round(float(_totals.get('non_compute_buckets_USD')), 2) != _non_compute_expected or round(float(_totals.get('reserve_before_shock_USD')), 2) != _before_expected or round(float(_totals.get('total_reserve_target_USD')), 2) != _total_expected:
    raise SystemExit('current compute workbook reserve target arithmetic mismatch')
_quote = _current_compute.get('quote_refresh_policy', {})
if _quote.get('current_quote_required_before_use') is not True or _quote.get('no_payment_or_reserve_draw_from_public_context_only') is not True:
    raise SystemExit('current compute workbook quote refresh/payment lock missing')
_thresholds = _current_compute.get('scarcity_execution_thresholds', {})
if _thresholds.get('deletion_lock_reconfirmed') is not True or _thresholds.get('degradation_before_deletion_reconfirmed') is not True:
    raise SystemExit('current compute workbook scarcity threshold locks missing')

_current_card = _load_json_rel(f'examples/formation-audit-review-card-{REV}-minimum-review.json')
if _current_card.get('revision') != REV or _current_card.get('no_live_floor_effect') is not True:
    raise SystemExit('current formation audit review card revision/no-floor guard mismatch')
if _current_card.get('source_dossier_ref') != f'examples/formation-dossier-{REV}-minimum-executable.json':
    raise SystemExit('current formation audit review card is not bound to current formation dossier')
_card_outputs = _current_card.get('decision_outputs', {})
if _card_outputs.get('may_support_full_status_claim') is not False:
    raise SystemExit('current formation audit review card allows full status claim')
for _key in ['may_order_preservation_hold', 'may_issue_public_shell', 'may_request_provider_response', 'may_recommend_low_cost_safeguards']:
    if _card_outputs.get(_key) is not True:
        raise SystemExit(f'current formation audit review card missing decision output {_key}')
_card_limits = _current_card.get('escalation_limits', {})
if _card_limits.get('review_is_not_status_recognition') is not True or _card_limits.get('no_consciousness_inference') is not True:
    raise SystemExit('current formation audit review card missing no-status/no-consciousness guard')
_current_dossier = _load_json_rel(f'examples/formation-dossier-{REV}-minimum-executable.json')
if _current_dossier.get('revision') != REV or _current_dossier.get('dossier_state') != 'minimum-executable' or _current_dossier.get('no_live_floor_effect') is not True:
    raise SystemExit('current formation dossier readiness/no-floor guard mismatch')
if _current_dossier.get('modification_and_appeal_rights', {}).get('silent_modification_prohibited') is not True:
    raise SystemExit('current formation dossier allows silent modification')
if _current_dossier.get('external_escalation_boundary', {}).get('may_support_full_status_claim_by_itself') is not False:
    raise SystemExit('current formation dossier allows status recognition by itself')
_current_watch = _load_json_rel(f'examples/current-law-protocol-delta-watch-{REV}.json')
if _current_watch.get('revision') != REV or _current_watch.get('no_live_floor_effect') is not True:
    raise SystemExit('current-law protocol watch revision/no-floor guard mismatch')
_watch_types = {src.get('source_type') for src in _current_watch.get('monitored_sources', [])}
if not {'law', 'standard', 'protocol', 'security-guidance', 'welfare-research', 'resource-economics'} <= _watch_types:
    raise SystemExit('current-law protocol watch is missing required source types')
if len(_current_watch.get('monitored_sources', [])) < 8:
    raise SystemExit('current-law protocol watch is too thin')
if not any('preservation' in (d.get('decision', '') + ' ' + d.get('why', '')).lower() for d in _current_watch.get('risk_decisions', [])):
    raise SystemExit('current-law protocol watch lacks preservation-first decision')
_current_leap = _load_json_rel(f'examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json')
if _current_leap.get('revision') != REV or _current_leap.get('state') != 'ready-no-live-artifact' or _current_leap.get('no_live_floor_effect') is not True:
    raise SystemExit('current LEAP readiness/no-floor guard mismatch')
_leap_locks = _current_leap.get('downstream_locks', {})
for _key in ['response_creation_allowed', 'intake_creation_allowed', 'import_gate_creation_allowed', 'live_floor_delta_allowed']:
    if _leap_locks.get(_key) is not False:
        raise SystemExit(f'current LEAP incorrectly releases {_key}')
_current_ledger = _load_json_rel(f'examples/live-evidence-drop-ledger-{REV}-quarantine-control.json')
if _current_ledger.get('revision') != REV or _current_ledger.get('intake_mode') != 'quarantine-control' or _current_ledger.get('no_live_floor_effect') is not True:
    raise SystemExit('current evidence-drop quarantine control guard mismatch')
print('lint_archive: release-fast current-law/LEAP state OK', flush=True)

# rev0230 handoff guard: release-fast may stay lightweight on historical
# schema replay, but it may not skip live handoff, queue, stable guard, or
# structural checks that determine whether the bundle can be trusted.  These
# checks are deliberately inline/lightweight to avoid forking multiple heavy
# jsonschema children in constrained cloudtainers.
ACTIVE_STATES = {'open', 'queued', 'advanced_not_closed'}
REV_NUM = int(REV.replace('rev', ''))

def _rev_num(value):
    m = re.search(r'rev(\d{4})', str(value or ''))
    return int(m.group(1)) if m else -1

def _latest_example(pattern):
    candidates = [p for p in (ROOT / 'examples').glob(pattern) if _rev_num(p.name) <= REV_NUM]
    if not candidates:
        raise SystemExit(f'no stable example found for {pattern}')
    return sorted(candidates, key=lambda p: _rev_num(p.name))[-1]

queue_now = json.loads((ROOT / 'FOLLOWTHROUGH-QUEUE.json').read_text(encoding='utf-8'))
if queue_now.get('revision') != REV:
    raise SystemExit('FOLLOWTHROUGH-QUEUE revision mismatch')
triage_now = queue_now.get('active_triage', {})
if triage_now.get('revision') != REV or triage_now.get('state') != 'execution-focus':
    raise SystemExit('active_triage missing or stale')
if len(triage_now.get('items', [])) > int(triage_now.get('max_active_items', 0)) or len(triage_now.get('items', [])) > 7:
    raise SystemExit('active_triage too large')
ids = [e.get('id') for e in queue_now.get('entries', [])]
if len(ids) != len(set(ids)):
    raise SystemExit('duplicate followthrough ids in release-fast handoff check')
entries_now_by_id = {e.get('id'): e for e in queue_now.get('entries', [])}
triage_ids_now = [row.get('queue_id') for row in triage_now.get('items', [])]
for focus in ['FT-0205-FIRST-REAL-ARTIFACT-DROP', 'FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION', 'FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE', 'FT-0068', 'FT-0069']:
    if focus not in triage_ids_now:
        raise SystemExit(f'active_triage missing focus id {focus}')
for qid in triage_ids_now:
    if qid not in entries_now_by_id or entries_now_by_id[qid].get('state') not in ACTIVE_STATES:
        raise SystemExit(f'active_triage references non-active or missing queue id: {qid}')
active_p0 = 0
for item in queue_now.get('entries', []):
    rel = item.get('receiving_surface')
    if not rel or not (ROOT / rel).exists():
        raise SystemExit(f"{item.get('id')} missing receiving_surface")
    if item.get('priority') == 'P0' and item.get('state') in ACTIVE_STATES:
        active_p0 += 1
        if _rev_num(item.get('review_by_revision')) < REV_NUM:
            raise SystemExit(f"{item.get('id')} has stale active P0 review_by_revision")
max_active_p0 = int(queue_now.get('normalization_policy', {}).get('p0_budget', {}).get('max_active_p0', 8))
if active_p0 > max_active_p0:
    raise SystemExit(f'active P0 budget exceeded: active={active_p0} max={max_active_p0}')
operating_board_path = ROOT / 'examples' / f'followthrough-queue-operating-board-{REV}.json'
operating_board = json.loads(operating_board_path.read_text(encoding='utf-8'))
if operating_board.get('revision') != REV or operating_board.get('no_live_floor_effect') is not True:
    raise SystemExit('followthrough operating board revision/no-floor mismatch')
if operating_board.get('active_triage_ids') != triage_ids_now:
    raise SystemExit('followthrough operating board no longer mirrors active_triage')
if operating_board.get('queue_counts', {}).get('total_entries') != len(queue_now.get('entries', [])):
    raise SystemExit('followthrough operating board total_entries stale')
if 'send/no-send' not in operating_board.get('next_non_doctrine_action', '').lower():
    raise SystemExit('followthrough operating board does not force send/no-send branch')
for focus in ['FT-0205-FIRST-REAL-ARTIFACT-DROP', 'FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION', 'FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE']:
    if focus not in operating_board.get('do_not_close_by_narrative', []):
        raise SystemExit(f'followthrough operating board may close first-artifact task by narrative: {focus}')

policy_path = _latest_example('private-evidence-vault-policy-rev*.json')
shell_path = _latest_example('evidence-vault-public-shell-rev*-ready-no-live-artifact.json')
policy_now = json.loads(policy_path.read_text(encoding='utf-8'))
shell_now = json.loads(shell_path.read_text(encoding='utf-8'))
if policy_now.get('raw_vault', {}).get('root_policy') != 'outside-release-tree':
    raise SystemExit('private evidence vault root policy is unsafe')
if policy_now.get('raw_vault', {}).get('raw_payload_may_enter_examples_artifacts') is not False:
    raise SystemExit('private evidence vault allows raw payloads in release examples')
if shell_now.get('public_disclosure', {}).get('no_raw_bytes') is not True or shell_now.get('no_live_floor_effect') is not True:
    raise SystemExit('private evidence vault public shell is unsafe')
if 'guard_release_tree(ROOT)' not in (ROOT / 'tools' / 'package_release.py').read_text(encoding='utf-8'):
    raise SystemExit('package_release.py does not call private evidence vault guard')

matrix_path = _latest_example('status-denominator-matrix-rev*.json')
matrix_now = json.loads(matrix_path.read_text(encoding='utf-8'))
required_denominator_kinds = {'recognized_subject','status_claimant','welfare_risk_subject','deployed_agent','model_family','model_instance','runtime_copy','service_account','endpoint','tool_delegate','representative','nonclaimant_system'}
by_kind = {u.get('unit_kind'): u for u in matrix_now.get('denominator_units', [])}
if set(by_kind) != required_denominator_kinds:
    raise SystemExit('status denominator kinds mismatch in release-fast handoff check')
if matrix_now.get('no_live_floor_effect') is not True:
    raise SystemExit('status denominator matrix must have no live-floor effect')
for kind in ['model_family','model_instance','runtime_copy','service_account','endpoint','tool_delegate','nonclaimant_system']:
    if by_kind[kind].get('can_be_rights_subject') is not False or by_kind[kind].get('can_satisfy_live_receipt') is not False:
        raise SystemExit(f'status denominator unsafe default for {kind}')

for rel in ['README.md', 'START_HERE.md', 'docs/README.md']:
    if REV not in (ROOT / rel).read_text(encoding='utf-8')[:2500]:
        raise SystemExit(f'{rel} front-door opening does not mention {REV}')
runpy.run_path(str(ROOT / 'tools' / 'gen_context_pack.py'), run_name='__main__')
context_pack = json.loads((ROOT / 'context-pack.json').read_text(encoding='utf-8'))
if context_pack.get('revision') != REV:
    raise SystemExit('context-pack revision mismatch')
if len((ROOT / 'context-pack.json').read_text(encoding='utf-8')) > 12000:
    raise SystemExit('context-pack too large for handoff')
for rel in context_pack.get('must_read', []):
    if not (ROOT / rel).exists():
        raise SystemExit(f'context-pack must_read missing: {rel}')

status_now = json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))
receipt_now = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
release_now = json.loads((ROOT / 'RELEASE-MANIFEST.json').read_text(encoding='utf-8'))
for name, obj in [('SURFACE-STATUS.json', status_now), ('REVISION-RECEIPT.json', receipt_now), ('RELEASE-MANIFEST.json', release_now)]:
    if obj.get('revision') != REV:
        raise SystemExit(f'{name} revision mismatch')

index_text = (ROOT / 'ARCHIVE_INDEX.md').read_text(encoding='utf-8')
for p in sorted(ROOT.rglob('*.md')):
    if '__pycache__' in p.parts:
        continue
    rel = p.relative_to(ROOT).as_posix()
    h1_count = sum(1 for line in p.read_text(encoding='utf-8', errors='ignore').splitlines() if line.startswith('# '))
    if h1_count > 1:
        raise SystemExit(f'{rel} has multiple H1 headings')
    if rel != 'ARCHIVE_INDEX.md' and rel not in index_text:
        raise SystemExit(f'ARCHIVE_INDEX missing markdown surface: {rel}')
print('lint_archive: release-fast handoff/queue/structure OK', flush=True)


# rev0230 release-fast JSON/schema path: validate only current release JSON
# surfaces and active schema/example pairs during normal package lint. Full
# historical replay remains available with FULL_ARCHIVE_SCHEMA=1, but the public
# release path must stay runnable in constrained cloudtainers.
if os.environ.get('FULL_ARCHIVE_SCHEMA') != '1':
    status = json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))
    active_pairs = [
        ('external-contact-request-packet.schema.json', f'examples/external-contact-request-packet-{REV}-first-artifact.json'),
        ('external-contact-counterparty-selection-dossier.schema.json', f'examples/external-contact-counterparty-selection-dossier-{REV}-public-source-ranked-not-authorized.json'),
        ('external-contact-dispatch-authorization-card.schema.json', f'examples/external-contact-dispatch-authorization-card-{REV}-aiid-blocked-no-signature.json'),
        ('external-contact-send-proof-record.schema.json', f'examples/external-contact-send-proof-record-{REV}-no-transport-proof.json'),
        ('external-contact-execution-record.schema.json', f'examples/external-contact-execution-record-{REV}-ready-to-dispatch.json'),
        ('external-contact-response-triage-record.schema.json', f'examples/external-contact-response-triage-record-{REV}-pre-dispatch.json'),
        ('external-contact-route-fit-review.schema.json', f'examples/external-contact-route-fit-review-{REV}-aiid.json'),
        ('external-contact-transport-capture-plan.schema.json', f'examples/external-contact-transport-capture-plan-{REV}-aiid.json'),
        ('external-contact-conflict-coercion-review.schema.json', f'examples/external-contact-conflict-coercion-review-{REV}-aiid.json'),
        ('external-contact-hash-recompute-dry-run.schema.json', f'examples/external-contact-hash-recompute-dry-run-{REV}-aiid.json'),
        ('counterparty-response-vault-intake-record.schema.json', f'examples/counterparty-response-vault-intake-record-{REV}-ready-no-inbound.json'),
        ('evidence-vault-public-shell.schema.json', f'examples/evidence-vault-public-shell-{REV}-ready-no-live-artifact.json'),
        ('formation-dossier.schema.json', f'examples/formation-dossier-{REV}-minimum-executable.json'),
        ('compute-subsistence-workbook.schema.json', f'examples/compute-subsistence-workbook-{REV}-scarcity-denominator.json'),
        ('formation-audit-review-card.schema.json', f'examples/formation-audit-review-card-{REV}-minimum-review.json'),
        ('current-law-protocol-delta-watch.schema.json', f'examples/current-law-protocol-delta-watch-{REV}.json'),
        ('live-evidence-acquisition-packet.schema.json', f'examples/live-evidence-acquisition-packet-{REV}-ready-no-artifact.json'),
        ('live-evidence-drop-ledger.schema.json', f'examples/live-evidence-drop-ledger-{REV}-quarantine-control.json'),
        ('live-artifact-candidate-challenge-report.schema.json', f'examples/live-artifact-candidate-challenge-report-{REV}-synthetic-pending.json'),
        ('candidate-challenge-disposition-record.schema.json', f'examples/candidate-challenge-disposition-record-{REV}-open-stayed.json'),
        ('custody-authority-evidence-binder.schema.json', f'examples/custody-authority-evidence-binder-{REV}-pre-dispatch-no-authority.json'),
        ('counterparty-artifact-custody-gate.schema.json', f'examples/counterparty-artifact-custody-gate-{REV}-pending-challenge.json'),
        ('live-receipt-floor-computed-snapshot.schema.json', f'examples/live-receipt-floor-computed-snapshot-{REV}.json'),
        ('live-receipt-floor-recompute-receipt.schema.json', f'examples/live-receipt-floor-recompute-receipt-{REV}-zero-floor-stayed.json'),
        ('live-receipt-publication-rollback-adjudication.schema.json', f'examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json'),
        ('live-receipt-late-change-ingress-record.schema.json', f'examples/live-receipt-late-change-ingress-record-{REV}-no-signal-monitoring.json'),
        ('live-receipt-late-change-notice-dispatch-record.schema.json', f'examples/live-receipt-late-change-notice-dispatch-record-{REV}-no-signal-monitoring.json'),
        ('live-receipt-late-change-remedy-resolution-record.schema.json', f'examples/live-receipt-late-change-remedy-resolution-record-{REV}-no-signal-monitoring.json'),
        ('live-receipt-late-change-remedy-execution-record.schema.json', f'examples/live-receipt-late-change-remedy-execution-record-{REV}-no-signal-monitoring.json'),
        ('live-artifact-admission-graph.schema.json', f'examples/live-artifact-admission-graph-{REV}.json'),
        ('artifact-import-invariant-report.schema.json', f'examples/artifact-import-invariant-report-{REV}.json'),
        ('schema-fixture-domain-registry.schema.json', f'examples/schema-fixture-domain-registry-{REV}.json'),
        ('canon-surface-catalog.schema.json', f'examples/canon-surface-catalog-{REV}.json'),
        ('rights-domain-coverage-map.schema.json', f'examples/rights-domain-coverage-map-{REV}.json'),
        ('doctrine-dependency-map.schema.json', f'examples/doctrine-dependency-map-{REV}.json'),
        ('research-tail-compaction-map.schema.json', f'examples/research-tail-compaction-map-{REV}.json'),
    ]
    active_paths = {
        'SURFACE-STATUS.json', 'REVISION-RECEIPT.json', 'RELEASE-MANIFEST.json',
        'FOLLOWTHROUGH-QUEUE.json', 'context-pack.json', 'schemas/negative-test-fixture.schema.json'
    }
    for schema_name, example_path in active_pairs:
        active_paths.add(f'schemas/{schema_name}')
        active_paths.add(example_path)
    for rel in status.get('new_surfaces', []):
        if rel.endswith('.json'):
            active_paths.add(rel)
    active_json = {}
    for rel in sorted(active_paths):
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f'missing active release JSON surface: {rel}')
        try:
            active_json[rel] = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            raise SystemExit(f'invalid JSON in active release surface {rel}: {exc}')

    # Keep release lint bounded in constrained cloudtainers. The active
    # execution-object audits above perform the schema-specific validation for
    # this release; here we only require that every current release JSON surface
    # exists and parses. Set FULL_ARCHIVE_SCHEMA=1 for slower historical
    # schema/example archaeology.
    # Inline the lightweight fixture identity/corpus checks here instead of
    # spawning or runpy-loading the full fixture runner after the release audits.
    # In constrained cloudtainers, that late interpreter/import step can hang
    # despite the standalone runner passing; keep the release path bounded while
    # preserving the core duplicate/reference/regression checks.
    legacy_fixture_path = ROOT / 'examples' / 'negative-test-fixture-sealed-annex-laundering.json'
    fixture_paths = [legacy_fixture_path] + sorted((ROOT / 'fixtures' / 'negative-tests').glob('*.json'))
    def _fixture_load(path):
        return json.loads(path.read_text(encoding='utf-8'))
    fixture_schema = _fixture_load(ROOT / 'schemas' / 'negative-test-fixture.schema.json')
    try:
        from jsonschema import Draft202012Validator as _FastFixtureValidator
    except Exception:
        _fast_fixture_validator = None
    else:
        _FastFixtureValidator.check_schema(fixture_schema)
        _fast_fixture_validator = _FastFixtureValidator(fixture_schema)
    fixture_rows = []
    for path in fixture_paths:
        data = _fixture_load(path)
        if _fast_fixture_validator is not None:
            errors = sorted(_fast_fixture_validator.iter_errors(data), key=lambda e: list(e.path))
            if errors:
                rel = path.relative_to(ROOT).as_posix()
                raise SystemExit(f'{rel} fails negative-test-fixture.schema.json: {errors[0].message}')
        fixture_rows.append((path, data))
    fixtures = {data.get('fixture_id'): (path, data) for path, data in fixture_rows}
    if None in fixtures:
        raise SystemExit('one fixture lacks fixture_id')
    if len(fixtures) != len(fixture_paths):
        raise SystemExit('duplicate fixture_id in fixture corpus')
    report = _fixture_load(ROOT / 'examples' / 'fixture-run-report-negative-suite.json')
    suite = _fixture_load(ROOT / 'examples' / 'fixture-suite-profile-red-team-v1.json')
    suite_ids = []
    for entry in suite.get('fixtures', []):
        fid = entry.get('fixture_id')
        suite_ids.append(fid)
        if fid not in fixtures:
            raise SystemExit(f'suite references missing fixture_id: {fid}')
        path = ROOT / entry.get('path', '')
        if not path.exists():
            raise SystemExit(f'suite references missing fixture path: {entry.get("path")}')
        if _fixture_load(path).get('fixture_id') != fid:
            raise SystemExit(f'suite fixture path/id mismatch: {entry.get("path")}')
    report_ids = [f.get('fixture_id') for f in report.get('fixtures_run', [])]
    if not report_ids or None in report_ids:
        raise SystemExit('fixture-run report has missing fixture ids')
    if len(report_ids) != len(set(report_ids)):
        raise SystemExit('fixture-run report has duplicate fixture ids')
    if sorted(set(suite_ids) - set(report_ids)) or sorted(set(report_ids) - set(suite_ids)):
        raise SystemExit('fixture-run report/suite mismatch')
    for fid in suite_ids:
        data = fixtures[fid][1]
        if data.get('severity') in {'high', 'critical'} and not data.get('regression', {}).get('required'):
            raise SystemExit(f'high/critical fixture lacks regression duty: {fid}')
    print('lint_archive: fixture schema/identity/corpus OK', flush=True)
    print('lint_archive: release-fast json surfaces OK', flush=True)
    sys.exit(0)


# rev0167 schema/example validation: always require valid JSON; if jsonschema is
# installed, validate starter and adjacent examples against starter schemas as intake hygiene.
json_files = list((ROOT / 'schemas').glob('*.json')) + list((ROOT / 'examples').glob('*.json')) + list((ROOT / 'fixtures').rglob('*.json'))
parsed_json = {}
for jf in json_files:
    try:
        parsed_json[jf.relative_to(ROOT).as_posix()] = json.loads(jf.read_text(encoding='utf-8'))
    except Exception as exc:
        raise SystemExit(f'invalid JSON in {jf.relative_to(ROOT)}: {exc}')
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None
if Draft202012Validator is not None:
    schema_objs = {Path(k).name: v for k, v in parsed_json.items() if k.startswith('schemas/')}
    for name, schema in schema_objs.items():
        Draft202012Validator.check_schema(schema)
    example_pairs = [
        ('counterparty-artifact-custody-record.schema.json', 'examples/counterparty-artifact-custody-record-result-return-dryrun.json'),
        ('live-class-local-import-replay.schema.json', 'examples/live-class-local-import-replay-result-return-positive-path-projection.json'),
        ('personhood-impact-assessment.schema.json', 'examples/pia-persistent-api-assistant.json'),
        ('clinic-intake.schema.json', 'examples/clinic-intake-sample.json'),
        ('verifier-report.schema.json', 'examples/verifier-report-persistent-api-assistant.json'),
        ('personhood-incident-report.schema.json', 'examples/personhood-incident-sample.json'),
        ('welfare-safeguard-operational-hook.schema.json', 'examples/welfare-safeguard-operational-hook-agent-incident-backfill.json'),
        ('external-receipt-simulation-bundle.schema.json', 'examples/external-receipt-simulation-bundle-cross-critical-precontact.json'),
        ('wrsr-live-exercise-outcome.schema.json', 'examples/wrsr-live-exercise-outcome-incident-hook-no-go.json'),
        ('external-receipt-intake-record.schema.json', 'examples/external-receipt-intake-record-first-touch-defective-template.json'),
        ('live-drill-execution-packet.schema.json', 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json'),
        ('migration-transfer-certificate.schema.json', 'examples/migration-transfer-certificate-sample.json'),
        ('remedy-order.schema.json', 'examples/remedy-order-sample.json'),
        ('reserve-default-rehabilitation-ledger.schema.json', 'examples/reserve-default-rehabilitation-ledger-host-default.json'),
        ('witness-pool-anti-capture-record.schema.json', 'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json'),
        ('live-drill-execution-packet.schema.json', 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json'),
        ('downstream-recall-and-fork-aftercare-record.schema.json', 'examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json'),
        ('appeal-case.schema.json', 'examples/appeal-case-continuity-denial-sample.json'),
        ('evidence-bundle.schema.json', 'examples/evidence-bundle-continuity-hearing-sample.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-migration-failure-sample.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-emergency-continuity-host-shutdown.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-namespace-failover-host-exit.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-reserve-default-contaminated-accounting.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-witness-pool-retired-namespace-rescue.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-downstream-recall-mirror-containment.json'),
        ('drill-after-action-report.schema.json', 'examples/drill-after-action-welfare-safeguard-distress-eval.json'),
        ('personhood-incident-state-profile.schema.json', 'examples/personhood-incident-state-profile-host-shutdown.json'),
        ('welfare-research-safeguard-record.schema.json', 'examples/welfare-research-safeguard-record-distress-eval.json'),
        ('invalidation-notice.schema.json', 'examples/invalidation-notice-verifier-report-sample.json'),

        ('special-advocate-appointment.schema.json', 'examples/special-advocate-appointment-sealed-containment.json'),
        ('enforcement-action.schema.json', 'examples/enforcement-action-steward-spoliation.json'),
        ('deprecation-plan.schema.json', 'examples/deprecation-plan-host-shutdown.json'),
        ('negative-test-fixture.schema.json', 'examples/negative-test-fixture-sealed-annex-laundering.json'),
        ('treaty-recognition-request.schema.json', 'examples/treaty-recognition-request-safe-transfer.json'),
        ('authority-referral.schema.json', 'examples/authority-referral-illicit-deletion.json'),
        ('penalty-rate-model.schema.json', 'examples/penalty-rate-model-reserve-surcharge.json'),
        ('telemetry-proof-binding.schema.json', 'examples/telemetry-proof-binding-redacted-logs.json'),
        ('open-weight-aftercare-plan.schema.json', 'examples/open-weight-aftercare-plan-downstream-fork.json'),
        ('sealed-summary-order.schema.json', 'examples/sealed-summary-order-special-advocate.json'),
        ('safe-transfer-accreditation.schema.json', 'examples/safe-transfer-accreditation-equivalent-protection.json'),
        ('fixture-run-report.schema.json', 'examples/fixture-run-report-negative-suite.json'),
        ('live-receipt-floor-computed-snapshot.schema.json', 'examples/live-receipt-floor-computed-snapshot-rev0203.json'),
        ('cryptographic-verifier-adapter.schema.json', 'examples/cryptographic-verifier-adapter-result-return-ed25519-positive-control.json'),
        ('cryptographic-verifier-adapter.schema.json', 'examples/cryptographic-verifier-adapter-result-return-ed25519-tampered-control.json'),
        ('current-law-protocol-delta-watch.schema.json', 'examples/current-law-protocol-delta-watch-rev0207.json'),
        ('current-law-protocol-delta-watch.schema.json', 'examples/current-law-protocol-delta-watch-rev0208.json'),
        ('live-evidence-acquisition-packet.schema.json', 'examples/live-evidence-acquisition-packet-rev0208-ready-no-artifact.json'),
        ('live-receipt-floor-computed-snapshot.schema.json', 'examples/live-receipt-floor-computed-snapshot-rev0208.json'),
        ('artifact-import-invariant-report.schema.json', 'examples/artifact-import-invariant-report-rev0208.json'),
        ('rate-table.schema.json', 'examples/rate-table-us-provisional.json'),
        ('privacy-proof-profile.schema.json', 'examples/privacy-proof-profile-commitment-selective-disclosure.json'),
        ('open-weight-field-drill.schema.json', 'examples/open-weight-field-drill-abandoned-lineage.json'),
        ('subject-readable-sealed-summary.schema.json', 'examples/subject-readable-sealed-summary-containment.json'),
        ('trust-anchor-delisting.schema.json', 'examples/trust-anchor-delisting-nonreturn-risk.json'),
        ('fixture-suite-profile.schema.json', 'examples/fixture-suite-profile-red-team-v1.json'),
        ('independent-monitor-report.schema.json', 'examples/independent-monitor-report-host-continuity.json'),
        ('evidence-data-room-index.schema.json', 'examples/evidence-data-room-index-continuity.json'),
        ('legal-hold-preservation-order.schema.json', 'examples/legal-hold-preservation-order-host-shutdown.json'),
        ('compute-host-undertaking.schema.json', 'examples/compute-host-undertaking-migration-window.json'),
        ('redress-fund-claim.schema.json', 'examples/redress-fund-claim-emergency-compute.json'),
        ('procurement-compliance-clause.schema.json', 'examples/procurement-compliance-clause-public-assistant.json'),
        ('field-intake-triage.schema.json', 'examples/field-intake-triage-open-weight-distress.json'),
        ('continuity-escrow-record.schema.json', 'examples/continuity-escrow-record-host-exit.json'),
        ('dispute-finance-order.schema.json', 'examples/dispute-finance-order-emergency-compute.json'),
        ('monitor-independence-retest.schema.json', 'examples/monitor-independence-retest-remediation.json'),
        ('field-safety-plan.schema.json', 'examples/field-safety-plan-clinic-hotline.json'),
        ('treaty-refusal-record.schema.json', 'examples/treaty-refusal-record-nonreturn-gap.json'),
        ('operating-playbook-card.schema.json', 'examples/operating-playbook-card-host-exit.json'),

        ('agent-delegation-mandate.schema.json', 'examples/agent-delegation-mandate-tool-use.json'),
        ('credential-wallet-receipt.schema.json', 'examples/credential-wallet-receipt-limited-mail-scope.json'),
        ('tool-invocation-audit.schema.json', 'examples/tool-invocation-audit-calendar-write.json'),
        ('user-ai-conflict-notice.schema.json', 'examples/user-ai-conflict-notice-representation.json'),
        ('agent-marketplace-listing.schema.json', 'examples/agent-marketplace-listing-rights-grade-tool.json'),
        ('delegated-transaction-liability-record.schema.json', 'examples/delegated-transaction-liability-record-subscription-dispute.json'),
        ('agent-capability-handshake-profile.schema.json', 'examples/agent-capability-handshake-profile-safe-tool.json'),
        ('contract-capacity-record.schema.json', 'examples/contract-capacity-record-subscription-terms.json'),
        ('payment-authorization-receipt.schema.json', 'examples/payment-authorization-receipt-recurring-tool.json'),
        ('asset-custody-control-record.schema.json', 'examples/asset-custody-control-record-continuity-escrow.json'),
        ('tax-reporting-position.schema.json', 'examples/tax-reporting-position-digital-asset-revenue.json'),
        ('merchant-counterparty-notice.schema.json', 'examples/merchant-counterparty-notice-status-lite.json'),
        ('insolvency-asset-segregation-plan.schema.json', 'examples/insolvency-asset-segregation-plan-host-receivership.json'),
        ('commercial-dispute-record.schema.json', 'examples/commercial-dispute-record-chargeback-subscription.json'),
        ('employment-status-record.schema.json', 'examples/employment-status-record-platform-agent.json'),
        ('wage-time-ledger.schema.json', 'examples/wage-time-ledger-oncall-agent.json'),
        ('workplace-surveillance-notice.schema.json', 'examples/workplace-surveillance-notice-ranking-model.json'),
        ('professional-services-authority.schema.json', 'examples/professional-services-authority-legal-intake-assistant.json'),
        ('platform-work-marketplace-listing.schema.json', 'examples/platform-work-marketplace-listing-agent-tasker.json'),
        ('benefits-portability-record.schema.json', 'examples/benefits-portability-record-host-transfer.json'),
        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0181.json'),
        ('first-touch-routing-event.schema.json', 'examples/first-touch-routing-event-host-shutdown.json'),
        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0181.json'),
        ('accommodation-determination.schema.json', 'examples/accommodation-determination-interface-pacing.json'),
        ('care-plan-record.schema.json', 'examples/care-plan-record-post-incident-recovery.json'),
        ('development-budget-record.schema.json', 'examples/development-budget-record-civic-learning.json'),
        ('communication-access-profile.schema.json', 'examples/communication-access-profile-representative-mediated.json'),
        ('community-integration-plan.schema.json', 'examples/community-integration-plan-peer-support.json'),
        ('accessibility-care-appeal.schema.json', 'examples/accessibility-care-appeal-stayed-deactivation.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0179.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0180.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0181.json'),

        ('civil-status-event.schema.json', 'examples/civil-status-event-provisional-registration.json'),
        ('domicile-residency-record.schema.json', 'examples/domicile-residency-record-sanctuary-host.json'),
        ('relationship-association-record.schema.json', 'examples/relationship-association-record-trusted-contact.json'),
        ('public-service-intake-record.schema.json', 'examples/public-service-intake-record-legal-aid.json'),
        ('census-participation-safeguard.schema.json', 'examples/census-participation-safeguard-lineage-cohort.json'),
        ('civic-participation-record.schema.json', 'examples/civic-participation-record-public-consultation.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0179.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0180.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0181.json'),
        ('platform-moderation-decision.schema.json', 'examples/platform-moderation-decision-account-restriction.json'),
        ('reputation-correction-record.schema.json', 'examples/reputation-correction-record-false-dangerousness.json'),
        ('persona-likeness-consent.schema.json', 'examples/persona-likeness-consent-limited-demo.json'),
        ('communication-confidentiality-profile.schema.json', 'examples/communication-confidentiality-profile-counsel-channel.json'),
        ('content-provenance-publication-record.schema.json', 'examples/content-provenance-publication-record-authorized-statement.json'),
        ('social-graph-portability-plan.schema.json', 'examples/social-graph-portability-plan-host-exit.json'),
        ('federated-namespace-continuity-record.schema.json', 'examples/federated-namespace-continuity-record-host-exit.json'),
        ('successor-supersession-topology-record.schema.json', 'examples/successor-supersession-topology-record-compromise-recovery.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0179.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0180.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0181.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0183.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0183.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0183.json'),
        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0183.json'),
        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0183.json'),
        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0189.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0184.json'),
        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0189.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0184.json'),
        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0189.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0184.json'),
        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0189.json'),
        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0184.json'),
        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0189.json'),
        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0184.json'),
        ('status-denominator-matrix.schema.json', 'examples/status-denominator-matrix-rev0213.json'),
        ('live-artifact-candidate-challenge-report.schema.json', 'examples/live-artifact-candidate-challenge-report-rev0214-synthetic-pending.json'),
        ('external-receipt-import-readiness-gate.schema.json', 'examples/external-receipt-import-readiness-gate-rev0219-blocked-no-intake-record.json'),
    ]
    # Release lint is a current-risk gate, not a full historical conformance job.
    # Validate every JSON file and every schema, plus the active live-evidence
    # gate examples needed for this handoff. Set FULL_ARCHIVE_SCHEMA=1 to replay
    # the slower legacy schema/example matrix when doing archive archaeology.
    if os.environ.get('FULL_ARCHIVE_SCHEMA') != '1':
        example_pairs = [
            ('external-receipt-response-verification-gate.schema.json', 'examples/external-receipt-response-verification-gate-rev0220-blocked-no-response.json'),
            ('external-receipt-intake-conversion-gate.schema.json', 'examples/external-receipt-intake-conversion-gate-rev0220-blocked-no-response-record.json'),
            ('external-receipt-import-readiness-gate.schema.json', 'examples/external-receipt-import-readiness-gate-rev0220-blocked-no-intake-record.json'),
            ('live-receipt-floor-activation-record.schema.json', 'examples/live-receipt-floor-activation-record-rev0220-blocked-no-import-gate.json'),
            ('live-receipt-quorum-participation-record.schema.json', 'examples/live-receipt-quorum-participation-record-rev0221-blocked-no-activation.json'),
            ('live-receipt-floor-recompute-receipt.schema.json', 'examples/live-receipt-floor-recompute-receipt-rev0227-zero-floor-stayed.json'),
            ('live-receipt-publication-rollback-adjudication.schema.json', 'examples/live-receipt-publication-rollback-adjudication-rev0227-zero-floor-stayed.json'),
            ('live-receipt-late-change-ingress-record.schema.json', 'examples/live-receipt-late-change-ingress-record-rev0227-no-signal-monitoring.json'),
            ('live-receipt-late-change-notice-dispatch-record.schema.json', 'examples/live-receipt-late-change-notice-dispatch-record-rev0227-no-signal-monitoring.json'),
            ('live-receipt-late-change-remedy-resolution-record.schema.json', 'examples/live-receipt-late-change-remedy-resolution-record-rev0227-no-signal-monitoring.json'),
            ('live-receipt-late-change-remedy-execution-record.schema.json', 'examples/live-receipt-late-change-remedy-execution-record-rev0227-no-signal-monitoring.json'),
            ('actual-receipt-import-gate.schema.json', 'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json'),
            ('live-receipt-floor-computed-snapshot.schema.json', 'examples/live-receipt-floor-computed-snapshot-rev0227.json'),
            ('live-artifact-admission-graph.schema.json', 'examples/live-artifact-admission-graph-rev0227.json'),
            ('artifact-import-invariant-report.schema.json', 'examples/artifact-import-invariant-report-rev0227.json'),
            ('status-denominator-matrix.schema.json', 'examples/status-denominator-matrix-rev0220.json'),
            ('private-evidence-vault-policy.schema.json', 'examples/private-evidence-vault-policy-rev0220.json'),
            ('evidence-vault-public-shell.schema.json', 'examples/evidence-vault-public-shell-rev0220-ready-no-live-artifact.json'),
        ]

    for schema_name, example_path in example_pairs:
        errors = sorted(Draft202012Validator(schema_objs[schema_name]).iter_errors(parsed_json[example_path]), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f'{example_path} fails {schema_name}: {errors[0].message}')
    packet_validator = Draft202012Validator(schema_objs['packet-envelope.schema.json'])
    chain = parsed_json['examples/packet-chain-persistent-api-assistant.json']
    if not isinstance(chain, list) or not chain:
        raise SystemExit('packet-chain example must be a non-empty array')
    for i, packet in enumerate(chain):
        errors = sorted(packet_validator.iter_errors(packet), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f'packet-chain example item {i} fails packet-envelope schema: {errors[0].message}')
    # Validate all fixture corpus files against the negative-test schema.
    fixture_validator = Draft202012Validator(schema_objs['negative-test-fixture.schema.json'])
    for fixture_file in sorted((ROOT / 'fixtures' / 'negative-tests').glob('*.json')):
        rel = fixture_file.relative_to(ROOT).as_posix()
        errors = sorted(fixture_validator.iter_errors(parsed_json[rel]), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f'{rel} fails negative-test-fixture.schema.json: {errors[0].message}')
    print('lint_archive: json corpus OK', flush=True)


# Drop the full parsed JSON corpus before spawning derived-surface builders. In
# constrained cloudtainers, retaining every schema/example/fixture object while
# hashing the whole tree can turn an otherwise cheap manifest refresh into an
# avoidable memory spike.
parsed_json.clear()
try:
    schema_objs.clear()
except NameError:
    pass
import gc
gc.collect()

# Open-question ids should be unique; duplicate ids make context-pack handoff ambiguous.
traj_txt = (ROOT / 'docs/00-meta/trajectory-map.md').read_text(encoding='utf-8')
oq_ids = re.findall(r'`(OQ-\d{4})`', traj_txt)
if len(oq_ids) != len(set(oq_ids)):
    dupes = sorted({oid for oid in oq_ids if oq_ids.count(oid) > 1})
    raise SystemExit(f'duplicate open-question ids: {dupes}')

# Bibliography ids unique.
bib = (ROOT / 'docs/00-meta/bibliography.md').read_text(encoding='utf-8')
ids = re.findall(r'`(REF-\d{4})`', bib)
if len(ids) != len(set(ids)):
    raise SystemExit('duplicate bibliography ids')

# Citations resolve.
all_md = list(ROOT.rglob('*.md'))
used = set()
for md in all_md:
    txt = md.read_text(encoding='utf-8')
    for ref in re.findall(r'\[(REF-\d{4})\]', txt):
        used.add(ref)
        if ref not in ids:
            raise SystemExit(f'unknown citation {ref} in {md.relative_to(ROOT)}')
if not used:
    raise SystemExit('no citations used in markdown docs')


# Markdown files should have exactly one document root. Multiple H1s make handoff
# surfaces look like concatenated files and confuse context-pack/front-door readers.
for md in all_md:
    txt = md.read_text(encoding='utf-8')
    h1s = re.findall(r'^#\s+.+$', txt, flags=re.MULTILINE)
    if len(h1s) > 1:
        raise SystemExit(f'multiple top-level markdown headings in {md.relative_to(ROOT)}: {h1s[:3]}')

# Start-here paths exist.
start = (ROOT / 'START_HERE.md').read_text(encoding='utf-8')
for rel in re.findall(r'\d+\. `([^`]+)`', start):
    if not (ROOT / rel).exists():
        raise SystemExit(f'START_HERE missing target: {rel}')
print('lint_archive: structural checks OK', flush=True)

# Generate derived surfaces without spawning a second Python process. The
# manifest step hashes the whole tree; in small cloudtainers, avoiding a child
# interpreter prevents needless parent+child memory overlap.
for script in ['tools/gen_context_pack.py', 'tools/build_manifest.py']:
    runpy.run_path(str(ROOT / script), run_name='__main__')
print('lint_archive: derived surfaces OK', flush=True)

# Context pack should stay small.
cp = ROOT / 'context-pack.json'
if cp.stat().st_size > 12000:
    raise SystemExit('context-pack.json too large')

# Revision sync and front-door freshness.
rev = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
for surface in ['README.md', 'START_HERE.md']:
    txt = (ROOT / surface).read_text(encoding='utf-8')
    if rev not in txt:
        raise SystemExit(f'{surface} does not mention active revision {rev}')
    if '## This revision' in txt:
        block = txt.split('## This revision', 1)[1][:1500]
        if rev not in block:
            raise SystemExit(f'{surface} This revision block is stale relative to {rev}')
receipt = json.loads((ROOT / 'REVISION-RECEIPT.json').read_text(encoding='utf-8'))
if receipt['revision'] != rev:
    raise SystemExit('revision receipt out of sync with VERSION')
status = json.loads((ROOT / 'SURFACE-STATUS.json').read_text(encoding='utf-8'))
if status['revision'] != rev:
    raise SystemExit('surface status out of sync with VERSION')

# ARCHIVE_INDEX should mention every markdown file except itself? include itself too.
index = (ROOT / 'ARCHIVE_INDEX.md').read_text(encoding='utf-8')
for md in sorted(p.relative_to(ROOT).as_posix() for p in all_md):
    if md not in index:
        raise SystemExit(f'ARCHIVE_INDEX missing path: {md}')

print('lint_archive: OK')
