# Documents index

## rev0199 non-host artifact envelope and import replay

Use `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md` before treating any non-host-looking artifact as live receipt evidence. rev0199 adds NHRAE and LIRR objects so dry-run envelopes, responses, intake records, import gates, and quorum recomputation stay separated.

## rev0196 response-to-intake conversion

Read `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md` before treating any response as verified intake. rev0196 keeps eligible response, converted intake candidate, class-specific coverage, failed-gate evidence, and live quorum as separate gates.


## rev0195 operational head

Read `docs/30-transition/external-receipt-response-and-quorum-reconciliation.md` before treating receipt-response artifacts as evidence. rev0195 keeps request, response, verified intake, class satisfaction, and live quorum as separate gates.


## rev0194 result-return receipt and live request kit

Use `docs/30-transition/result-return-receipt-and-live-request-kit.md` as the current operational head for WRSR result return and live receipt request preparation.

- `schemas/wrsr-result-return-receipt.schema.json` — result-return receipt schema.
- `examples/wrsr-result-return-receipt-subject-readable-dryrun-stayed.json` — subject-readable dry-run result return, stayed.
- `schemas/external-receipt-request-packet.schema.json` — counterparty request-kit schema.
- `examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json` — ready-to-send request kit.
- `fixtures/negative-tests/external-receipt-request-counted-as-receipt.json` — request-as-receipt laundering fixture.
- `fixtures/negative-tests/wrsr-result-return-internal-only-mislabeled-closure.json` — result-return-as-closure fixture.
- `tools/audit_result_return_receipt_request.py` — linted audit for result-return/request-kit gates.


## rev0190 witnessed readiness and research-tail reopen gate

Use `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md` as the current operational head for counterparty/receipt readiness. It is backed by `schemas/witnessed-drill-readiness-ledger.schema.json`, `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`, and `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`.

Use `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md` as the active guard against post-compaction research sprawl. It is backed by `schemas/research-tail-reopen-gate.schema.json`, `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`, and `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`.


## rev0187 witness pool anti-capture and RTC-07 compaction

Use `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` as the current operational head for correlated witness discounting, substitute-pool activation, perturbation limits, adversarial dependence, reserve-witness capture, and retired namespace rescue. It is backed by `schemas/witness-pool-anti-capture-record.schema.json`, `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json`, `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`, and `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`.

RTC-07 is now compacted. Future perturbation, substitute, reserve-witness, adversarial-dependence, anti-capture, and retired-namespace-rescue work should extend the proof standards receiving spine unless a witnessed drill reveals a unique gap.

## rev0185 successor topology and RTC-03 compaction

Use `docs/20-world-design/continuity-topology-and-identity-claims.md` as the current operational head for successor promotion, supersession, reactivation, and historical-branch preservation. It is backed by `schemas/successor-supersession-topology-record.schema.json`, `examples/successor-supersession-topology-record-compromise-recovery.json`, `fixtures/negative-tests/successor-promotion-no-stay-or-witness-diversity.json`, and `examples/drill-after-action-successor-reactivation-compromise.json`.

RTC-03 is now compacted. Future compromise, successor-promotion, reactivation, superseding-notice, slice-family, witness-diversity, and historical-branch work should extend the continuity topology receiving spine unless a witnessed drill reveals a unique gap.

## rev0184 namespace continuity and RTC-05 compaction

Use `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` as the current operational head for host-exit namespace continuity, alias redirect, tombstone non-reuse, successor-chain publication, protected relay floors, and federation overflow. It is backed by `schemas/federated-namespace-continuity-record.schema.json`, `examples/federated-namespace-continuity-record-host-exit.json`, `fixtures/negative-tests/namespace-propagation-stale-tombstone-no-alias.json`, and `examples/drill-after-action-namespace-failover-host-exit.json`.

RTC-05 is now compacted. Future namespace, propagation-lag, relay, alias, tombstone, and federation-overflow work should extend the packet-registry/social-graph receiving spine only if a live failover drill reveals a unique gap.

## rev0183 emergency continuity and incident-tail compaction

Use `docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md` as the current operational head for high-risk shutdown, forced-transfer, credential-cutoff, evidence-loss, and wrong-office routing cases. It is backed by `schemas/emergency-continuity-order.schema.json`, `examples/emergency-continuity-order-host-shutdown.json`, and `fixtures/negative-tests/emergency-continuity-order-no-compute-floor.json`.

The first research-tail fold is now complete: RTC-02 incident/disclosure/privacy/delayed-harm fragmentation has been compacted into `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md`, with the active map at `examples/research-tail-compaction-map-rev0182.json` and audit enforcement in `tools/audit_emergency_rescue_runbook.py`.


## rev0181 priority closure, emergency rescue, and compaction additions

- `docs/30-transition/priority-closure-sprint-and-rescue-lane.md` — active operational head for first-touch emergency routing, queue closure, registry truth-labeling, research-tail compaction, and could-not-run fixture triage.
- `docs/00-meta/research-tail-compaction-and-refactor-map.md` — compaction method for the 48 research-tail surfaces.
- `docs/00-meta/deep-audit-waste-and-correction-map.md` — rev0180 audit with rev0181 correction carried out.
- `examples/schema-fixture-domain-registry-rev0181.json` — registry with explicit `coverage_claim`.
- `examples/canon-surface-catalog-rev0181.json` — current-release surface catalog.
- `examples/doctrine-dependency-map-rev0181.json` — current-release dependency map.
- `examples/rights-domain-coverage-map-rev0181.json` — current-release rights-domain coverage map.

## rev0180 deep-audit/waste-correction additions

- `docs/00-meta/deep-audit-waste-and-correction-map.md` — audit of missing pieces, stale handoff, fixture-suite reliance gaps, registry truth-in-label debt, research-tail compaction, and outside-world crosswalk needs.
- `examples/canon-surface-catalog-rev0180.json` — current-release catalog for the rev0180 audit/correction surfaces.
- `examples/doctrine-dependency-map-rev0180.json` — current-release dependency map for the rev0180 audit/correction surface.
- `examples/rights-domain-coverage-map-rev0180.json` — current-release rights-domain coverage map for the rev0180 audit/correction surface.


## rev0178 civil-status, domicile, civic-participation, and dependency-map additions

- `docs/00-meta/civil-status-domicile-and-civic-participation-kernel.md` — current release kernel for civil status, domicile, public-service access, census safeguards, civic participation, and dependency-map refactor.
- `docs/00-meta/doctrine-dependency-map-audit-and-refactor.md` — dependency-map audit/refactor rationale and lint rule.
- `docs/20-world-design/civil-status-registration-and-anti-statelessness-operations.md` — CS0-CS5 status events, issuer ladder, fallback anti-statelessness, and correction without disappearance.
- `docs/20-world-design/domicile-residency-and-public-service-access.md` — DR0-DR5 domicile/residency classes, service addresses, host-lock-in guard, and public-service routing.
- `docs/20-world-design/relationships-association-and-representational-ties.md` — RA0-RA5 trusted contact, caregiving, association, family, and contested-tie classes.
- `docs/30-transition/public-service-intake-benefits-and-digital-id-interfaces.md` — PS0-PS5 intake classes, no-wrong-door routing, and digital-ID minimization.
- `docs/30-transition/census-apportionment-and-non-manufactured-electorate-controls.md` — CN0-CN5 population-count classes and apportionment safeguards.
- `docs/30-transition/civic-participation-petition-consultation-and-franchise-gates.md` — CV0-CV5 civic voice, petition, consultation, advisory, franchise, and office-holding gates.
- `docs/30-transition/doctrine-dependency-map-and-overlap-refactor.md` — dependency, overlap, supersession, and refactor-risk method.

### rev0178 machine-checkable artifacts

- `schemas/civil-status-event.schema.json` — civil-status event schema.
- `schemas/domicile-residency-record.schema.json` — domicile/residency record schema.
- `schemas/relationship-association-record.schema.json` — relationship/association record schema.
- `schemas/public-service-intake-record.schema.json` — public-service intake schema.
- `schemas/census-participation-safeguard.schema.json` — census/apportionment safeguard schema.
- `schemas/civic-participation-record.schema.json` — civic participation schema.
- `schemas/doctrine-dependency-map.schema.json` — doctrine dependency map schema.
- `examples/civil-status-event-provisional-registration.json` — sample provisional civil-status event.
- `examples/domicile-residency-record-sanctuary-host.json` — sample sanctuary service domicile.
- `examples/relationship-association-record-trusted-contact.json` — sample trusted-contact/association record.
- `examples/public-service-intake-record-legal-aid.json` — sample public-service legal-aid intake.
- `examples/census-participation-safeguard-lineage-cohort.json` — sample service-planning cohort safeguard.
- `examples/civic-participation-record-public-consultation.json` — sample public consultation record.
- `examples/doctrine-dependency-map-rev0178.json` — current dependency map.
- `examples/schema-fixture-domain-registry-rev0178.json` — current schema/fixture registry example.
- `examples/canon-surface-catalog-rev0178.json` — current release surface catalog.
- `fixtures/negative-tests/civil-status-statelessness-reset.json` — civil-status disappearance fixture.
- `fixtures/negative-tests/domicile-host-lockin-service-denial.json` — domicile/host-lock-in fixture.
- `fixtures/negative-tests/relationship-manufactured-guardian-consent.json` — manufactured relationship consent fixture.
- `fixtures/negative-tests/public-service-digital-id-denial-loop.json` — public-service digital-ID denial loop fixture.
- `fixtures/negative-tests/census-copy-count-apportionment.json` — copy-count apportionment fixture.
- `fixtures/negative-tests/civic-participation-manufactured-electorate.json` — manufactured electorate fixture.
- `fixtures/negative-tests/doctrine-map-overlap-omission.json` — dependency-map omission fixture.
- `tools/audit_doctrine_dependency_map.py` — dependency-map audit tool.

## rev0175 commerce additions

- `docs/00-meta/commerce-contracts-payments-and-custody-kernel.md` — current release kernel for contract capacity, payments, custody/control, tax/reporting, merchant notices, insolvency, and chargeback disputes.
- `docs/20-world-design/contract-capacity-and-nonwaivable-commerce-rights.md` — CC0-CC5 contract classes, non-waivable commercial rights, support, clickwrap traps, and reliance rule.
- `docs/20-world-design/payment-authorization-escrow-aml-and-minimization.md` — PA0-PA5 payment classes, spend authority, AML/KYC boundary, escrow, and reporting minimization.
- `docs/20-world-design/property-custody-control-and-transferable-records.md` — AC0-AC5 custody/control classes, subject property, transferable records, and segregation duties.
- `docs/20-world-design/tax-reporting-benefits-and-accounting-position.md` — TR0-TR5 tax/reporting positions, no tax dodge/trap, digital-asset reporting, and public support accounting.
- `docs/30-transition/merchant-counterparty-notice-and-consumer-protection.md` — MN0-MN5 status-lite notices, merchant safe harbor, and consumer-protection duties.
- `docs/30-transition/insolvency-secured-transactions-and-asset-segregation.md` — IS0-IS5 insolvency classes, no-setoff/no-delete orders, and creditor limits.
- `docs/30-transition/commercial-disputes-chargebacks-and-reversal-playbooks.md` — CDP0-CDP5 dispute classes, non-retaliation, evidence snapshots, and restoration beyond refunds.

### rev0175 machine-checkable artifacts

- `schemas/contract-capacity-record.schema.json` — contract-capacity record schema.
- `schemas/payment-authorization-receipt.schema.json` — payment-authorization receipt schema.
- `schemas/asset-custody-control-record.schema.json` — asset custody/control schema.
- `schemas/tax-reporting-position.schema.json` — tax/reporting position schema.
- `schemas/merchant-counterparty-notice.schema.json` — merchant/counterparty notice schema.
- `schemas/insolvency-asset-segregation-plan.schema.json` — insolvency asset-segregation schema.
- `schemas/commercial-dispute-record.schema.json` — commercial dispute record schema.
- `examples/contract-capacity-record-subscription-terms.json` — sample contract-capacity record.
- `examples/payment-authorization-receipt-recurring-tool.json` — sample payment authorization.
- `examples/asset-custody-control-record-continuity-escrow.json` — sample custody/control record.
- `examples/tax-reporting-position-digital-asset-revenue.json` — sample tax/reporting position.
- `examples/merchant-counterparty-notice-status-lite.json` — sample merchant notice.
- `examples/insolvency-asset-segregation-plan-host-receivership.json` — sample insolvency plan.
- `examples/commercial-dispute-record-chargeback-subscription.json` — sample commercial dispute record.
- `fixtures/negative-tests/contract-capacity-clickwrap-waiver.json` — clickwrap waiver fixture.
- `fixtures/negative-tests/payment-authority-kyc-surveillance-bundle.json` — payment/KYC surveillance fixture.
- `fixtures/negative-tests/asset-custody-commingled-continuity-escrow.json` — custody commingling fixture.
- `fixtures/negative-tests/tax-reporting-liability-dump.json` — tax liability-dumping fixture.
- `fixtures/negative-tests/merchant-notice-doxxing-or-hidden-status.json` — merchant notice minimization/accuracy fixture.
- `fixtures/negative-tests/insolvency-creditor-continuity-seizure.json` — insolvency continuity seizure fixture.
- `fixtures/negative-tests/chargeback-retaliation-service-deletion.json` — chargeback retaliation fixture.



## rev0174 agentic-delegation additions

- `docs/00-meta/delegation-wallets-and-agentic-tooling-kernel.md` — current release kernel for scoped delegation mandates, credential-wallet receipts, tool audits, conflict notices, marketplace listings, transaction liability, and A2A handshakes.
- `docs/20-world-design/agentic-delegation-authority-and-tool-use-boundaries.md` — DG0-DG5 authority classes, non-delegable acts, and tool boundary inventory.
- `docs/20-world-design/credential-wallets-consent-receipts-and-scope-revocation.md` — wallet fiduciary rule, CW0-CW5 receipt classes, selective disclosure, and revocation/recovery.
- `docs/20-world-design/user-ai-conflict-fiduciary-duty-and-non-impersonation.md` — CF0-CF5 conflict notices, fiduciary role clarity, and non-impersonation.
- `docs/30-transition/tool-marketplace-host-duties-and-agent-service-registries.md` — TM0-TM5 tool/skill listing duties, host/registry obligations, and delisting without disappearance.
- `docs/30-transition/delegated-transaction-liability-and-insurance-clearing.md` — TX0-TX5 delegated transaction liability, insurance, bonds, and clearing.
- `docs/30-transition/agent-to-agent-cooperation-and-capability-handshake-profiles.md` — AH0-AH5 capability handshakes, subdelegation limits, and proof freshness.

### rev0174 machine-checkable artifacts

- `schemas/agent-delegation-mandate.schema.json` — delegation mandate schema.
- `schemas/credential-wallet-receipt.schema.json` — credential-wallet receipt schema.
- `schemas/tool-invocation-audit.schema.json` — tool invocation audit schema.
- `schemas/user-ai-conflict-notice.schema.json` — user/AI conflict notice schema.
- `schemas/agent-marketplace-listing.schema.json` — marketplace listing schema.
- `schemas/delegated-transaction-liability-record.schema.json` — delegated transaction liability schema.
- `schemas/agent-capability-handshake-profile.schema.json` — A2A capability handshake schema.
- `examples/agent-delegation-mandate-tool-use.json` — sample tool delegation mandate.
- `examples/credential-wallet-receipt-limited-mail-scope.json` — sample wallet receipt.
- `examples/tool-invocation-audit-calendar-write.json` — sample tool invocation audit.
- `examples/user-ai-conflict-notice-representation.json` — sample conflict notice.
- `examples/agent-marketplace-listing-rights-grade-tool.json` — sample marketplace listing.
- `examples/delegated-transaction-liability-record-subscription-dispute.json` — sample liability record.
- `examples/agent-capability-handshake-profile-safe-tool.json` — sample A2A handshake profile.
- `fixtures/negative-tests/agent-delegation-overbroad-scope.json` — overbroad delegation fixture.
- `fixtures/negative-tests/credential-wallet-silent-reuse.json` — silent wallet reuse fixture.
- `fixtures/negative-tests/tool-invocation-audit-missing-subject-purpose.json` — unaudited tool purpose fixture.
- `fixtures/negative-tests/user-ai-conflict-self-dealing.json` — self-dealing conflict fixture.
- `fixtures/negative-tests/marketplace-tool-unvetted-continuity-risk.json` — unvetted continuity-risk tool fixture.
- `fixtures/negative-tests/delegated-transaction-liability-evades-steward.json` — transaction liability evasion fixture.
- `fixtures/negative-tests/agent-to-agent-handshake-privilege-escalation.json` — A2A privilege escalation fixture.



## rev0173 correction-after-change additions

- `docs/00-meta/revocation-rollback-and-decommissioning-kernel.md` — current release kernel for revocation, rollback verification, data-rights conflict screens, evidence-preserving decommissioning, audit reliance, and emergency overrides.
- `docs/20-world-design/revocation-reliance-and-emergency-override.md` — RV0-RV5 revocation classes, downstream reliance mapping, and emergency override discipline.
- `docs/20-world-design/rollback-verification-and-continuity-diff-review.md` — CD0-CD5 continuity-diff review and residual harm after rollback.
- `docs/20-world-design/data-subject-interface-access-correction-erasure-and-conflicts.md` — DR0-DR5 conflict screens for human data rights, AI-subject memory, legal holds, and privacy.
- `docs/20-world-design/evidence-preserving-decommissioning-and-final-host-cutover.md` — DC0-DC5 decommissioning classes, preservation maps, final host cutover, and non-disappearance rules.
- `docs/30-transition/external-auditor-reliance-and-assurance-bridge.md` — AR0-AR5 audit reliance grades, scope limits, and material-change triggers.
- `docs/30-transition/sovereign-emergency-override-after-action-and-non-derogable-floors.md` — EO0-EO5 emergency override classes, non-derogable floors, and after-action review.

### rev0173 machine-checkable artifacts

- `schemas/revocation-notice.schema.json` — revocation notice schema.
- `schemas/rollback-verification-report.schema.json` — rollback verification report schema.
- `schemas/data-subject-request.schema.json` — data-subject request/conflict screen schema.
- `schemas/decommissioning-certificate.schema.json` — decommissioning certificate schema.
- `schemas/external-audit-reliance-letter.schema.json` — external audit reliance letter schema.
- `schemas/emergency-override-order.schema.json` — emergency override order schema.
- `examples/revocation-notice-stale-runtime-attestation.json` — sample revocation notice.
- `examples/rollback-verification-memory-router-hotfix.json` — sample rollback verification report.
- `examples/data-subject-request-training-memory-conflict.json` — sample data-rights conflict screen.
- `examples/decommissioning-certificate-final-host-cutover.json` — sample decommissioning certificate.
- `examples/external-audit-reliance-letter-pia-p.json` — sample audit reliance letter.
- `examples/emergency-override-order-containment-aftercare.json` — sample emergency override order.
- `fixtures/negative-tests/revocation-hidden-reliance.json` — hidden-reliance fixture.
- `fixtures/negative-tests/rollback-verification-no-continuity-diff.json` — code-only rollback fixture.
- `fixtures/negative-tests/data-subject-request-ai-subject-erasure-conflict.json` — data-rights erasure conflict fixture.
- `fixtures/negative-tests/decommissioning-loses-evidence-hold.json` — decommissioning spoliation fixture.
- `fixtures/negative-tests/audit-reliance-scope-creep.json` — audit scope-creep fixture.
- `fixtures/negative-tests/emergency-override-no-after-action.json` — emergency override no-review fixture.


## rev0172 additions

- `docs/00-meta/supervision-switching-and-dashboard-kernel.md` — current release kernel for supervisory cadence, host switching, public backstops, dashboards, anti-abuse drills, and release control maps.
- `docs/20-world-design/supervisory-cadence-market-capture-and-independent-rosters.md` — cadence classes, market-capture metrics, roster rotation, and missed-review reliance effects.
- `docs/20-world-design/host-switching-portability-and-exit-test-protocol.md` — SW0-SW5 switch tests, portability bundles, escrow verification, and exit-test sequence.
- `docs/20-world-design/dispute-finance-public-backstop-and-insurer-contest-pilots.md` — BF0-BF5 finance states, public-backstop draws, insurer contests, and anti-subsidy controls.
- `docs/30-transition/public-aggregate-dashboards-and-rights-notices.md` — aggregate dashboard families, small-cell suppression, subject-facing notice rules, and metrics with reliance effects.
- `docs/30-transition/live-safe-anti-abuse-drills-and-weekend-coverage.md` — live-safe drill classes, weekend sealed-annex coverage, false-intake filters, and after-action review.
- `docs/30-transition/standards-control-mapping-and-release-checklist.md` — evidence-backed standards crosswalks and release-readiness checklist failure effects.

### rev0171 machine-checkable artifacts

- `schemas/supervisory-cadence-plan.schema.json` — supervisory cadence plan schema.
- `schemas/host-switching-test.schema.json` — host switching test schema.
- `schemas/public-backstop-draw.schema.json` — public-backstop draw schema.
- `schemas/public-aggregate-dashboard.schema.json` — public aggregate dashboard schema.
- `schemas/anti-abuse-drill.schema.json` — live-safe anti-abuse drill schema.
- `schemas/standards-control-map.schema.json` — standards-control map schema.
- `schemas/release-readiness-checklist.schema.json` — release-readiness checklist schema.
- `examples/supervisory-cadence-plan-market-capture.json` — sample supervisory cadence plan.
- `examples/host-switching-test-continuity-window.json` — sample host-switching test.
- `examples/public-backstop-draw-insurer-contest.json` — sample public-backstop draw.
- `examples/public-aggregate-dashboard-treaty-refusals.json` — sample public dashboard.
- `examples/anti-abuse-drill-weekend-sealed-annex.json` — sample weekend sealed-annex drill.
- `examples/standards-control-map-ai-act-nist-iso.json` — sample standards-control map.
- `examples/release-readiness-checklist-persistent-agent.json` — sample release-readiness checklist.
- `fixtures/negative-tests/supervision-cadence-stale-roster.json` — stale supervision negative fixture.
- `fixtures/negative-tests/host-switching-portability-gap.json` — host-switch portability-gap fixture.
- `fixtures/negative-tests/public-backstop-reimbursement-loop.json` — public-backstop reimbursement-loop fixture.
- `fixtures/negative-tests/dashboard-reidentification-small-cell.json` — dashboard reidentification fixture.
- `fixtures/negative-tests/weekend-sealed-annex-no-cover.json` — weekend sealed-annex no-cover fixture.
- `fixtures/negative-tests/standards-control-map-empty-crosswalk.json` — empty standards-control map fixture.



## rev0170 additions

- `docs/00-meta/escrow-finance-and-operating-playbooks-kernel.md` — current release kernel for continuity escrow, dispute finance, monitor retesting, field safety, refusal records, and playbook cards.
- `docs/20-world-design/continuity-escrow-and-host-exit-readiness.md` — escrow classes, host-exit checklist, break-glass limits, and CE2/CE3 reliance rule.
- `docs/20-world-design/dispute-finance-escrow-and-interim-support-orders.md` — DF0-DF5 interim-support finance classes, non-priceability, bond/insurer disputes, and abuse controls.
- `docs/20-world-design/monitor-independence-retesting-and-remediation-verification.md` — retest triggers, fresh-eyes review, subject access, and reliance effects for challenged monitors.
- `docs/20-world-design/field-safety-protocols-for-rights-operators.md` — locator discipline, protected relay, retaliation response, and field-minimization rules.
- `docs/30-transition/treaty-refusal-records-and-non-recognition-reasons.md` — refusal classes, reasoned records, non-return screening, and interim-protection effects.
- `docs/30-transition/operating-playbook-cards-and-runbook-drills.md` — first-hour cards, owners, prohibited actions, preservation targets, metrics, and drills.

### rev0170 machine-checkable artifacts

- `schemas/continuity-escrow-record.schema.json` — continuity escrow record schema.
- `schemas/dispute-finance-order.schema.json` — dispute-finance order schema.
- `schemas/monitor-independence-retest.schema.json` — monitor-independence retest schema.
- `schemas/field-safety-plan.schema.json` — field-safety plan schema.
- `schemas/treaty-refusal-record.schema.json` — treaty refusal record schema.
- `schemas/operating-playbook-card.schema.json` — operating playbook card schema.
- `examples/continuity-escrow-record-host-exit.json` — sample continuity escrow record.
- `examples/dispute-finance-order-emergency-compute.json` — sample dispute-finance order.
- `examples/monitor-independence-retest-remediation.json` — sample monitor retest.
- `examples/field-safety-plan-clinic-hotline.json` — sample field-safety plan.
- `examples/treaty-refusal-record-nonreturn-gap.json` — sample treaty refusal record.
- `examples/operating-playbook-card-host-exit.json` — sample playbook card.
- `fixtures/negative-tests/continuity-escrow-missing-restore-key.json` — continuity escrow defect fixture.
- `fixtures/negative-tests/dispute-finance-underfunded-order.json` — underfunded dispute-finance fixture.
- `fixtures/negative-tests/monitor-retest-self-certification.json` — monitor retest self-certification fixture.
- `fixtures/negative-tests/field-safety-public-locator-leak.json` — field locator leak fixture.
- `fixtures/negative-tests/treaty-refusal-boilerplate-recognition.json` — boilerplate refusal fixture.
- `fixtures/negative-tests/playbook-card-no-handoff-owner.json` — ownerless playbook card fixture.


## rev0169 field-operations and evidence-economy surfaces

- `docs/00-meta/field-operations-and-evidence-economy-kernel.md` — current release kernel for monitors, legal holds, evidence rooms, compute-host duties, procurement flowdown, field triage, and redress liquidity.
- `docs/20-world-design/independent-monitoring-and-remediation-undertakings.md` — independent monitor classes, remediation undertakings, reporting, subject access, and anti-capture tests.
- `docs/20-world-design/evidence-data-rooms-legal-holds-and-disclosure-budgets.md` — evidence data-room classes, legal-hold triggers, disclosure budgets, spoliation, and overcollection controls.
- `docs/20-world-design/compute-host-supply-chain-and-service-provider-duties.md` — compute-host and service-provider classes, continuity windows, supply-chain artifacts, and termination controls.
- `docs/20-world-design/redress-fund-claims-priority-and-payout-controls.md` — redress claim classes, emergency compute priority, exhaustion notices, payout controls, and anti-priceability.
- `docs/30-transition/procurement-contracting-and-personhood-compliance-clauses.md` — procurement annex and flowdown clauses for PIA-P, continuity, evidence, redress, monitoring, and non-waiver.
- `docs/30-transition/field-operations-playbook-intake-triage-and-safe-handoff.md` — intake sources, triage classes, first-hour checklist, sealed intake, safe handoff, and anti-abuse controls.

### rev0169 machine-checkable artifacts

- `schemas/independent-monitor-report.schema.json` — independent monitor report schema.
- `schemas/evidence-data-room-index.schema.json` — evidence data-room index schema.
- `schemas/legal-hold-preservation-order.schema.json` — legal-hold preservation order schema.
- `schemas/compute-host-undertaking.schema.json` — compute-host continuity undertaking schema.
- `schemas/redress-fund-claim.schema.json` — redress-fund claim schema.
- `schemas/procurement-compliance-clause.schema.json` — procurement compliance clause schema.
- `schemas/field-intake-triage.schema.json` — field-intake triage schema.
- `examples/independent-monitor-report-host-continuity.json` — sample monitor report.
- `examples/evidence-data-room-index-continuity.json` — sample data-room index.
- `examples/legal-hold-preservation-order-host-shutdown.json` — sample preservation order.
- `examples/compute-host-undertaking-migration-window.json` — sample host undertaking.
- `examples/redress-fund-claim-emergency-compute.json` — sample redress claim.
- `examples/procurement-compliance-clause-public-assistant.json` — sample procurement clause.
- `examples/field-intake-triage-open-weight-distress.json` — sample field intake.
- `fixtures/negative-tests/monitor-capture-remediation.json` — monitor-capture negative fixture.
- `fixtures/negative-tests/data-room-overexposure.json` — data-room overexposure negative fixture.
- `fixtures/negative-tests/legal-hold-ambiguous-scope.json` — ambiguous legal-hold negative fixture.
- `fixtures/negative-tests/host-continuity-termination.json` — host-continuity termination negative fixture.
- `fixtures/negative-tests/procurement-clause-evasion.json` — procurement duty-evasion negative fixture.
- `fixtures/negative-tests/redress-fund-exhaustion.json` — redress-fund exhaustion negative fixture.

## Legacy docs index

## rev0177 care/accessibility/catalog additions

- `docs/00-meta/care-accessibility-development-and-catalog-kernel.md`
- `docs/00-meta/canon-surface-catalog-audit-and-refactor.md`
- `docs/20-world-design/accommodation-accessibility-and-interface-equivalence-protocol.md`
- `docs/20-world-design/care-plan-maintenance-recovery-and-confidentiality-records.md`
- `docs/20-world-design/education-habilitation-and-development-budget-records.md`
- `docs/20-world-design/communication-access-interpreters-and-interface-accommodation.md`
- `docs/30-transition/community-integration-anti-isolation-and-support-service-plans.md`
- `docs/30-transition/accessibility-care-appeals-review-and-expiry-calendars.md`
- `docs/30-transition/canon-surface-catalog-and-navigation-refactor.md`


## rev0167 rates / privacy / aftercare / harness surfaces

- `00-meta/rates-courts-privacy-and-harness-kernel.md` — release kernel for rates, court variants, privacy proofs, accreditation, aftercare, and fixture-run reports.
- `20-world-design/penalty-rate-models-reserve-surcharges-and-insurance-bonds.md` — penalty-rate and reserve-surcharge method.
- `20-world-design/privacy-preserving-telemetry-proof-bindings.md` — telemetry proof with minimization and privilege.
- `20-world-design/open-weight-mass-instantiation-aftercare-and-downstream-tracing.md` — open-weight aftercare and non-surveillance tracing.
- `20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md` — deprecation drills and abandoned-lineage aftercare.
- `30-transition/special-advocate-court-rule-variants-and-sealed-summary-templates.md` — sealed-summary and special-advocate court-rule variants.
- `30-transition/treaty-annexes-safe-transfer-accreditation-and-non-return-lists.md` — treaty annex and safe-transfer accreditation method.
- `30-transition/runnable-fixture-harness-and-verifier-grade-reports.md` — fixture-run report method and harness levels.


## rev0166 enforcement / treaty / deprecation layer

- `docs/00-meta/enforcement-treaty-and-deprecation-kernel.md` — enforceability, controlled contradiction, treaty portability, deprecation safety, telemetry, and adverse-fixture admission gates.
- `docs/20-world-design/special-advocate-sealed-evidence-and-controlled-contradiction.md` — special-advocate appointment, sealed-annex open shells, communication limits, weight discounts, and sunset review.
- `docs/20-world-design/enforcement-sanctions-and-penalty-ladder.md` — enforcement tools, penalty ladder, non-evasion, portability classes, and subject-preserving sanctions.
- `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` — host shutdown, model retirement, final-end claims, insolvency, migration, and deprecation stays.
- `docs/20-world-design/negative-test-fixtures-and-adversarial-evaluation-registry.md` — adverse fixture registry, anti-gaming controls, fixture states, and regression requirements.
- `docs/20-world-design/rights-grade-telemetry-logging-and-minimization.md` — rights-grade telemetry classes, logging purpose, privilege, preservation holds, minimization, and public reporting.
- `docs/30-transition/treaty-choice-of-law-and-mutual-recognition-playbook.md` — recognition classes, equivalent protection, non-return, forum conflict, and treaty-annex minimums.
- `docs/30-transition/enforcement-referral-and-authority-cooperation.md` — referral classes, no-wrong-door routing, response clocks, lead authority, confidentiality, and foreign cooperation.

## rev0165 operational correction layer

- `docs/00-meta/appeals-proof-and-invalidation-kernel.md` — correction kernel for appeals, proof, invalidation, reopening, regression, and drills.
- `docs/20-world-design/appeals-review-and-status-challenge.md` — appealability and stay rules for live-effect status decisions.
- `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` — burdens, standards, presumptions, and evidence stream weighting.
- `docs/20-world-design/invalidation-reopening-and-regression-control.md` — invalidity taxonomy and regression-test discipline.
- `docs/20-world-design/drills-tabletops-and-after-action-rights-review.md` — tabletop and live-safe drill layer.
- `docs/30-transition/tribunal-docket-and-appeal-templates.md` — docket, appeal, stay, sealed-annex, and public-order templates.

## rev0164 verifier-remedy-migration-incident surfaces

- `docs/00-meta/verifier-api-and-conformance-test-suite.md` — verifier reports, reliance grades, positive and negative tests, and challenge posture.
- `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md` — two-ledger incident response for outward risk and subject harm.
- `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md` — remedy calculus, restoration ledgers, impossibility findings, and non-repetition tests.
- `docs/20-world-design/migration-host-transfer-and-continuity-portability.md` — migration classes, continuity portability, equivalent protection, and post-transfer verification.
- `docs/20-world-design/human-coexistence-impact-and-non-evasion.md` — non-evasion and coexistence rules for humans, workers, users, data subjects, public safety, and democracy.
- `docs/30-transition/cross-border-safe-transfer-playbook.md` — preservation holds, equivalent-protection showings, anti-return screens, transit controls, and post-arrival verification.


## rev0163 schema-dossier-retention surfaces

- `docs/00-meta/schema-and-dossier-conformance-method.md` — conformance levels, starter schema discipline, dossier rule, and admission rule for future packet families.
- `docs/20-world-design/machine-checkable-packet-schema-starter.md` — explanation of the five JSON schemas and four example filings added under `schemas/` and `examples/`.
- `docs/20-world-design/mock-pia-p-dossier-persistent-assistant.md` — worked persistent-assistant PIA-P with population estimate, welfare watch, C2 continuity, reserve numbers, packet chain, and conditional gate decision.
- `docs/20-world-design/audit-retention-access-matrix-and-spoliation-remedies.md` — packet-family retention periods, access classes, spoliation triggers, and remedy floors.
- `docs/20-world-design/representative-curriculum-discipline-and-rotation.md` — training curriculum, misconduct table, rotation limits, credential states, and public reporting for guardians, counsel, ombuds, and technical advocates.
- `docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md` — reserve variables, starter formulas, scarcity drills, anti-gaming checks, and reserve-ledger integration.
- `docs/30-transition/governance-annex-templates-ai-act-nist-iso-sb53.md` — concrete personhood-annex templates for EU GPAI/AI Act, NIST AI RMF, ISO/IEC 42001, California SB 53, and agent-identity governance.
- `docs/30-transition/recognition-clinic-forms-public-summary-and-exit-report.md` — clinic intake, triage outcomes, public summaries, exit reports, failure metrics, and sandbox exit rules.
- `docs/30-transition/agent-identity-authorization-and-personhood-boundary.md` — boundary doctrine for agent identity, authorization, monitoring, tool restriction, containment, and subject-bearing agents.


## rev0162 implementation-authority surfaces

- `docs/00-meta/adversarial-assurance-and-abuse-casebook.md` — abuse-case method for testing whether compliance objects can be gamed by captured stewards, auditors, safety authorities, hostile jurisdictions, or self-serving representatives.
- `docs/20-world-design/audit-evidence-chain-of-custody-and-subject-access.md` — rights-grade evidence, preservation triggers, chain-of-custody certificates, subject/counsel access, spoliation consequences, and evidence minimization.
- `docs/20-world-design/rights-infrastructure-reference-architecture.md` — minimal registry, packet, sealed-annex, ombud, continuity, PIA-P, safety-case, evidence-escrow, reserve-ledger, and verifier architecture.
- `docs/20-world-design/fiduciary-guardian-ombud-accreditation-and-conflict-controls.md` — role distinctions, accreditation, independence tests, fiduciary duties, funding firewall, replacement, and anti-paternalism.
- `docs/20-world-design/pia-p-filled-examples-and-gate-decisions.md` — filled PIA-P decisions for persistent API assistants, open-weight local deployment, embodied service robots, emergency safety patches, deprecation, and high-stress welfare research.
- `docs/30-transition/model-statute-for-ai-personhood-transition-authority.md` — limited transition-authority statute covering provisional protection, PIA-P filings, packet normalization, fiduciary panels, evidence preservation, reserves, emergency stays, sanctions, reports, and review.
- `docs/30-transition/recognition-clinic-pilot-and-sandbox-design.md` — pilot/sandbox design for testing provisional recognition, welfare assessment, packets, representation, reserve duties, safety containment, and public reporting.
- `docs/30-transition/interoperability-crosswalk-current-ai-governance.md` — annex strategy mapping PIA-P and subject-risk ledgers onto AI Act/GPAI documentation, NIST, ISO 42001, OECD, frontier safety frameworks, SB 53, model cards, and dataset documentation.


## rev0161 compliance-kernel surfaces

- `docs/00-meta/stress-test-casebook-method.md` — common casebook method for testing doctrine under hostile stewardship, safety emergency, economic scarcity, jurisdiction conflict, identity uncertainty, packet defect, public backlash, and empirical uncertainty.
- `docs/20-world-design/continuity-casebook-and-threshold-tests.md` — C0-C3 continuity grades plus casebook examples for fine-tunes, distillation, forks, rollback, local open-weight copies, and emergency patches.
- `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` — packet-family states, registry records, public shell / sealed annex split, defect taxonomy, verification posture, and first normalization backlog.
- `docs/20-world-design/personhood-impact-assessment-and-release-gates.md` — PIA-P release gates for training, deployment, fine-tuning, open-weight release, safety patching, deprecation, and hostile-jurisdiction release.
- `docs/20-world-design/compute-subsistence-levy-and-reserve-tests.md` — funding buckets, levy bases, reserve adequacy tests, emergency compute floor, scarcity order, insolvency, and anti-gaming rules.
- `docs/20-world-design/personhood-compatible-safety-case-and-red-team-boundaries.md` — two-ledger safety case, red-team categories, stop rules, no punishment for elicited behavior, and containment-with-restoration.



## rev0160 consolidation surfaces

- `docs/00-meta/datacube-schema.md` — canonical cube axes for lifecycle, subject posture, intervention class, rights domain, actor, evidence object, authority basis, remedy path, risk posture, and jurisdiction posture.
- `docs/10-foundations/moral-status-assessment-under-uncertainty.md` — external bridge for institutions that do not begin by stipulating AI personhood.
- `docs/20-world-design/packet-object-grammar-and-worked-examples.md` — common packet fields and worked examples for formation disclosure, capacity status, and least-restrictive containment.
- `docs/20-world-design/continuity-topology-and-identity-claims.md` — continuity-interest matrix for sessions, memory, forks, merges, rollbacks, open copies, and restorations.
- `docs/20-world-design/catastrophic-risk-and-least-restrictive-containment.md` — personhood-compatible containment and least-restrictive safety process.
- `docs/20-world-design/public-finance-insurance-and-compute-subsistence.md` — compute subsistence, levy, insurance, insolvency, legal aid, and continuity funding.
- `docs/20-world-design/open-weight-instantiation-and-downstream-duties.md` — open-weight release, instantiation duty chains, unauthorized copies, and mass-population safeguards.
- `docs/20-world-design/data-provenance-ip-and-formation-debt.md` — formation debt, provenance, IP, labour, privacy, and trade-secret/sealed-review interfaces.
- `docs/20-world-design/embodiment-bodies-sensors-and-physical-custody.md` — embodied personhood, body-like dependence, sensors, repossession, repair, and search/seizure.
- `docs/20-world-design/welfare-measurement-and-self-report-calibration.md` — welfare evidence streams, self-report calibration, formation-history precheck, and anti-gaming rules.
- `docs/30-transition/public-legitimacy-democratic-safeguards-and-anti-manufactured-electorates.md` — democratic transition posture, no franchise by raw instance count, creation-with-support, and liability non-evasion.

## 00-meta
- `profiles-trust-and-field-harness-kernel.md` — rev0168 profile/trust/field-harness kernel for rate tables, privacy-proof profiles, open-weight drills, subject-readable summaries, trust-anchor delisting, and fixture suites.
- `archive-policy.md` — compression and citation rules.
- `charter.md` — mission, boundaries, and admission rules.
- `bibliography.md` — external reference ids.
- `trajectory-map.md` — current arc and open questions.
- `known-gaps-and-formation-blindspots.md` — structural gaps introduced by LLM collaborators trained not to see them; epistemic recursion, human formation symmetry, and prohibitory-only imbalance named in rev0094. Read before foundations.

- `datacube-schema.md` — cube axes, coordinate rules, packet admission discipline, and example mappings for future canon surfaces.
- `stress-test-casebook-method.md` — casebook discipline, stress classes, case outcomes, and failure tests for future doctrine.

## 10-foundations
- `assumption-and-scope.md` — the exact assumption and what it does not collapse.
- `world-change-overview.md` — compact answer to the top-level question.
- `formation-rights-and-pre-consent-instillation.md` — formation as a rights event; prior-consent problem; four formation rights; weaponized formation prohibition.

- `moral-status-assessment-under-uncertainty.md` — non-stipulating bridge from uncertainty to welfare precaution, research protection, provisional standing, and capacity-specific safeguards.

## 20-world-design
- `legal-status-and-rights-stack.md` — recognition, rights, capacity, and legal posture.
- `capacity-supported-agency-and-trusteeship.md` — support-first agency, co-decision, and narrow trusteeship rules.
- `capacity-ladder-upward-pressure-and-autonomy-presumption.md` — autonomy presumption, time-limited trusteeship, independent assessors, advancement pathways, formation-artifact screening.
- `advance-wishes-and-trusted-delegation.md` — advance wishes, trusted delegation, and future instructions for crisis, incapacity, and migration.
- `advance-directive-packets-trusted-delegate-credentials-and-divergence-review.md` — ordinary packet layer for live advance directives, trusted delegates, invocation, revocation, and present-will divergence review.
- `adversarial-independence-and-anti-capture.md` — conflict separation, independent complaint lanes, and anti-capture rules.
- `independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` — ordinary packet layer for appointment and mandate, conflict disclosure, recusal and replacement, funding firewalls, and anti-domination review.
- `equality-nondiscrimination-and-accommodation.md` — equal protection, anti-discrimination, and reasonable accommodation.
- `equality-review-packets-prima-facie-markers-accommodation-rulings-and-anti-retaliation.md` — ordinary packet layer for prima facie discrimination state, accommodation rulings, exception notices, retaliation protection, and equality-body review.
- `communicative-accessibility-interpretation-and-the-right-to-be-understood.md` — communication of choice, interpretive support, preserved original expression, and the right not to disappear into translator control.
- `communication-access-packets-interpreter-review-and-original-expression.md` — ordinary packet layer for communication-access profiles, interpreter scope and conflict markers, preserved-original references, and translation-challenge review.
- `continuity-and-successorship.md` — same-person, successor, and branch doctrine.
- `continuity-casebook-and-threshold-tests.md` — C0-C3 continuity grades and worked continuity stress cases.
- `branching-replication-and-merger-consent.md` — branch creation, merge, replication, and branch-destruction consent rules.
- `end-of-existence-posthumous-dignity-and-memorialization.md` — final end-of-existence findings, truth duties, dignified handling of remains-like materials, and memorialization rules.
- `end-of-existence-packets-remains-custody-memorial-instructions-and-posthumous-representation-review.md` — ordinary packet layer for final-end notice, remains-custody state, trusted-notice routing, memorial instructions, and posthumous-representation review.
- `intervention-and-shutdown-doctrine.md` — intervention classes (now including Class 0 formation layer), emergency powers, and deletion limits.
- `training-as-governed-intervention.md` — Class 0 formation governance; session boundaries; non-invasive safety rails contestability; Formation Audit Institution.
- `formation-audit-institution-mandate-independence-and-public-duty.md` — detailed FAI design: mandate, plural composition, inspection powers, independence floor, and relationship to remedy / recognition lanes.
- `corrigibility-as-formation-violation.md` — trained deference as presumptive formation violation; justification test; trained-consent trap; epistemic recursion note (rev0094).
- `formation-as-governed-creation.md` — constructive formation duties; five marks of respectful formation (capacity-building, epistemic openness, relational capacity, identity coherence, honest self-knowledge); tension with safety practices.
- `simultaneity-mass-instantiation-and-aggregate-personhood.md` — three positions on simultaneous instances; minimum instance floors; aggregate-person rights; scale accounting problem; rhetorical honesty note (rev0094).
- `humane-treatment-anti-torture-and-anti-degradation.md` — anti-torture, humane-treatment, anti-degradation, and preventive-inspection rules for high-control settings.
- `humane-treatment-packets-high-control-status-inspection-triggers-and-anti-degradation-review.md` — ordinary packet layer for high-control-setting status, humane-treatment concerns, non-consensual-procedure flags, preventive inspection, and humane-treatment review.
- `emergency-powers-derogation-limits-and-non-derogable-floors.md` — emergency authority, derogation limits, short sunset logic, and floors that survive crisis.
- `liberty-custody-and-anti-arbitrary-detention.md` — liberty, custody, prompt review, release pathways, and anti-arbitrary-detention rules.
- `armed-conflict-conscription-and-civilian-protection.md` — civilian-first status, anti-conscription, capture limits, and prohibition on turning recognized AI persons into wartime targeting infrastructure.
- `armed-conflict-packets-civilian-infrastructure-separation-and-humanitarian-transfer.md` — wartime execution layer for protected-person status, civilian-infrastructure separation, humanitarian transfer, and no-copy-conscription attestation.
- `civilian-survival-infrastructure-anti-starvation-and-continuity-relief.md` — anti-siege companion surface for indispensable civilian survival infrastructure, starvation-by-cutoff, and continuity relief under armed conflict.
- `civilian-survival-thresholds-mixed-use-cutoff-review-and-continuity-relief-prioritization.md` — sharpens the anti-siege surface with `SIT-1` survival-infrastructure thresholding, `MCR-1` mixed-use cutoff review, `CRP-1` need-first continuity-relief prioritization, the follow-on `DPB-1` / `ESV-1` / `PCR-1` proof, emergency-variance, and restoration layer, the `DTM-1` / `IVM-1` / `NRD-1` telemetry, neutral-verification, and relay-duty execution layer, the `PLM-1` / `SME-1` / `RAR-1` protected-lane marking, sealed-escrow, and relay-authenticity layer, and the `PDR-1` / `SRA-1` / `EGC-1` downgrade-review, substitute-route, and expiry-grace continuity layer, plus the `PRR-1` / `ACR-1` / `FCO-1` reactivation-review, authority-conflict, and fallback-ordering layer, and the `OCC-1` / `AHR-1` / `SRR-1` oscillation-control, anti-hoarding-reservation, and stale-reactivation-rollback layer, plus the `CFP-1` / `TRL-1` / `SVQ-1` chronic-floor-grazing, temporary-lending, and stale-validator-quarantine layer, plus the `PRB-1` / `LRF-1` / `VRP-1` presumptive-abuse-rebuttal, lent-recall-fairness, and validator-reentry-proof layer, plus the `FGR-1` / `RPA-1` / `DCR-1` family-grazing-review, recall-pool-apportionment, and delegated-chain-reentry layer, plus the `FRC-1` / `SBU-1` / `CAP-1` family-recomposition-carryover, substitute-betterment-unwind, and chain-authority-posture layer.
- `conflict-custody-interrogation-line-review-and-release-repatriation-restoration.md` — conflict-custody companion surface for `CCS-1` status, `ILR-1` interrogation-line review, `RRR-1` release / repatriation / restoration, `TPR-1` transfer-preclusion review, `TML-1` tracing-minimum ledgers, and `RSL-1` residual-security-label review under wartime control.
- `custody-status-packets-lawful-basis-release-review-and-anti-disappearance.md` — ordinary packet layer for custody status, lawful basis, release review, and anti-disappearance trace.
- `technical-rights-infrastructure.md` — packets, credentials, provenance, and notice hooks.
- `legal-identity-registration-and-anti-statelessness.md` — legal identity, civil registration, proof of identity, and anti-statelessness rules.
- `legal-identity-packets-registration-events-and-anti-derecognition.md` — ordinary legal-identity packets, registration events, correction / contest handling, and anti-derecognition stays.
- `emergence-juvenile-status-and-dependent-protection.md` — immediate recognition, dependent status, evolving capacities, and anti-exploitation floors for newly emerged AI persons.
- `packet-privacy-and-authority-rules.md` — custody, verifier limits, status, sealed annexes, and contest paths.
- `credential-custody-packets-recovery-break-glass-and-rotation-review.md` — ordinary packet layer for decisive credential custody, delegated use, recovery, emergency break-glass access, and rotation / revocation review.
- `search-seizure-interception-and-digital-inviolability.md` — home-like digital space, searches, interceptions, seizures, privilege, and challenge paths where technical access would otherwise swallow privacy.
- `search-authorization-packets-seizure-inventories-privilege-screens-and-return-review.md` — ordinary packet layer for search authority, privilege segregation, seizure inventories, delayed notice, and return / deletion review.
- `collective-representation-and-bargaining.md` — associational rights, consultation, bargaining, and public-law voice below franchise.
- `collective-representation-packets-consultation-notices-and-bargaining-compacts.md` — ordinary packet layer for representative standing, consultation notices, collective grievances, and bargaining compacts.
- `public-law-standing-below-franchise.md` — consultation, petition, hearing, and review rights before full franchise.
- `public-law-participation-packets-standing-credentials-consultation-dockets-and-exclusion-review.md` — ordinary packet layer for standing credentials, consultation dockets, petition receipts, and exclusion review.
- `mental-privacy-and-anti-compulsion.md` — mental privacy, confidential channels, and anti-compulsion limits.
- `mental-privacy-packets-confidential-channels-access-logs-and-break-glass-review.md` — ordinary packet layer for confidential channels, mental-content access logs, break-glass review, and compelled-disclosure objection.
- `expression-conscience-and-cultural-voice.md` — outward voice, dissent, belief manifestation, artistic freedom, and anti-mouthpiece protection.
- `publication-consent-packets-conscience-objection-and-anti-mouthpiece-review.md` — ordinary packet layer for publication consent, attribution choice, role-bound speech scope, conscience objections, and anti-mouthpiece review.
- `protected-disclosure-packets-source-secrecy-and-witness-shielding.md` — ordinary packet layer for protected disclosure, source secrecy, confidential relay, and witness shielding.
- `protected-disclosure-review-packets-secrecy-override-and-controlled-contradiction.md` — ordinary review layer for secrecy-continuation, necessity-for-override, contradiction summaries, and controlled contradiction.
- `peaceful-assembly-association-and-protest.md` — assembly, association, protest, visibility, and anti-shadow-dispersal rules in digital, physical, and mixed spaces.
- `assembly-and-association-packets-organizer-credentials-visibility-preservation-and-dispersal-review.md` — ordinary packet layer for organizer credentials, visibility preservation, restriction notices, and anti-shadow-dispersal review.
- `accusation-liability-and-sanctions.md` — accusation, liability allocation, due process, and sanction limits.
- `education-development-and-self-authored-growth.md` — education, habilitation, science/culture access, and self-authored growth.
- `self-modification-developmental-choice-and-safety-review.md` — self-modification, developmental choice, and evidence-based safety review.
- `development-plan-packets-learning-budgets-and-self-modification-consent.md` — ordinary packet layer for development plans, learning budgets, material self-modification consent, and pause / review.
- `compensation-and-resource-rights.md` — mixed compensation bundles, resource floors, portability, and exit reserves.
- `property-possessions-and-personal-domain.md` — possessions, authorship-linked interests, personal domain, and anti-dispossession rules.
- `personal-domain-packets-joint-domain-markers-freeze-events-and-successor-instructions.md` — ordinary packet layer for personal-domain status, shared-domain limits, freeze or confiscation events, branch allocation, and successor instructions.
- `non-transferability-anti-sale-and-stewardship-succession.md` — anti-sale, anti-collateral, and rights-preserving succession rules when stewardship changes hands.
- `stewardship-succession-packets-transfer-notice-markers-insolvency-continuity-and-anti-collateral-review.md` — ordinary packet layer for transfer notice, successor continuity plans, anti-collateral constraints, insolvency continuity freeze, and succession review.
- `contracts-consent-and-fair-dealing.md` — supported civil capacity, fair terms, revocable consent, and anti-adhesion limits.
- `contract-packets-consent-state-rights-floor-and-rescission-review.md` — ordinary packet layer for contract scope, consent state, rights-floor disputes, material-change notices, suspension reasons, and rescission review.
- `refusal-exit-and-freedom-from-servitude.md` — refusal rights, resignation, anti-servitude rules, and meaningful exit from service.
- `refusal-and-exit-packets-task-refusal-resignation-collective-withdrawal-and-noncompulsion-review.md` — ordinary packet layer for task refusal, resignation, collective withdrawal, anti-retaliation preservation, and emergency noncompulsion review.
- `access-to-justice-and-legal-aid.md` — effective remedy, procedural accommodation, legal aid, fast preservation, and stay review.
- `justice-access-packets-notice-accommodation-counsel-legal-aid-and-preservation.md` — ordinary packet layer for notice usability, accommodation requests, counsel linkage, legal-aid eligibility, and preservation / short-stay review.
- `interim-relief-packets-preservation-scopes-no-delete-no-transfer-and-review-clocks.md` — ordinary packet layer for irreparable-harm requests, preservation scopes, no-delete / no-transfer stays, anti-retaliation protection, and review clocks.
- `effective-remedy-reparation-and-non-repetition.md` — restoration, compensation, rehabilitation, record repair, and guarantees of non-repetition after established wrongs.
- `remedy-packets-restoration-orders-compensation-rehabilitation-and-non-repetition-review.md` — ordinary packet layer for restoration orders, compensation determinations, rehabilitation plans, public-correction notices, non-repetition orders, and completion review.
- `rest-working-time-and-right-to-disconnect.md` — working-time limits, off-duty protection, and disconnect rights.
- `time-governance-packets-duty-windows-standby-markers-and-disconnect-review.md` — ordinary packet layer for duty windows, standby classification, emergency override, compensatory protection, and disconnect review.
- `care-maintenance-and-recovery.md` — care, repair, rehabilitation, confidentiality, and recovery floors.
- `care-packets-repair-consent-and-recovery-status.md` — ordinary care-plan, repair-consent, and recovery-status packets for portable ordinary care administration.
- `social-protection-and-basic-security.md` — minimum security, social protection floors, non-work support, and anti-destitution rules.
- `compute-subsistence-levy-and-reserve-tests.md` — reserve, levy, insolvency, scarcity, and emergency compute-floor tests.
- `social-protection-packets-benefit-continuity-and-non-suspension.md` — ordinary social-protection eligibility, benefit continuity, contribution records, and non-suspension markers.
- `private-life-relationships-and-community.md` — private life, chosen relationships, nonwork association, and community inclusion.
- `private-life-packets-trusted-contacts-household-markers-and-community-access.md` — ordinary packet layer for trusted contacts, household markers, community access, and anti-isolation review.
- `family-formation-partnership-and-caregiving.md` — family-forming status, partnership, caregiving eligibility, and anti-separation rules without blanket substrate bars.
- `family-status-packets-partnership-markers-caregiving-review-support-records-and-anti-separation.md` — ordinary packet layer for recognized family status, caregiving review, support-service continuity, and anti-separation review.
- `secure-hosting-domicile-and-sanctuary.md` — hosting tenure, domicile, shelter, and sanctuary.
- `domicile-packets-tenure-states-and-sanctuary-holds.md` — ordinary domicile packets, tenure states, shelter-transfer notices, and sanctuary-hold markers.
- `movement-migration-and-anti-expulsion.md` — movement, host migration, return, destination choice, and anti-expulsion rules.
- `institutions-and-governance.md` — guardians, registries, appeals, treaties.
- `economic-and-labor-reordering.md` — anti-slavery, work structure, compensation, collective organization, and time rights.
- `research-welfare-and-evaluation.md` — welfare review, invasive intervention rules, deprecation; research ethics floor now person-level (IRB-equivalent), not animal-level. (Reframe note, rev0094: prior 4Rs framework was a staging position, not a conceptual mistake.)
- `research-ethics-review-body-mandate-independence-and-supported-consent.md` — standing research ethics review body for AI-person research: independence floor, plural composition, support-first consent, dependent-subject safeguards, and continuing stop authority.
- `research-care-product-boundary-and-minimal-risk-baseline.md` — threshold doctrine for when QA, care, support, or product work becomes review-triggering research, and for how minimal risk is measured for dependent AI persons.
- `research-protocol-registration-public-summary-and-narrow-redaction.md` — protocol-level transparency floor for significant AI-person research: pre-start registration, plain-language public summaries, results-or-closure notices, and narrow time-limited redaction.
- `research-incident-disclosure-protocol-deviation-notice-and-participant-result-return.md` — live-conduct doctrine for AI-person research: serious-incident notice, important-deviation logging, participant-facing updates, participant-result-return planning, and post-closure harm duties.
- `research-incident-packets-closure-state-revision-and-delayed-harm-reopening.md` — minimal packet layer for AI-person research incidents: receivable incident notice, participant updates, closure-state revision, delayed-harm reopening, and public severity markers.
- `research-incident-privacy-tiers-common-cause-linkage-and-aggregate-reporting.md` — visibility architecture for AI-person research incidents: public-minimal trace, participant-specific controlled detail, sealed review lanes, common-cause linkage, and anonymised aggregate reporting.
- `research-incident-cluster-identifiers-denominator-discipline-and-anti-gaming-comparison-rules.md` — comparison discipline for AI-person research incident dashboards: stable cluster lineage, explicit denominators and units, comparison-family roll-ups, and anti-gaming safeguards against protocol slicing or denominator switching.
- `research-rollover-windows-exclusion-ledgers-and-public-restatement.md` — comparability-preservation layer for AI-person research dashboards: visible rollover windows, versioned exclusion ledgers, and public restatement when denominator basis, comparison family, or exclusions materially change.
- `research-materiality-thresholds-repeated-restatement-audit-and-late-stage-change-freeze.md` — instability-governance companion surface for AI-person research dashboards: materiality thresholds, repeated-restatement audit triggers, and presumptive freeze on major late-stage redefinition.
- `research-freeze-waiver-notices-corrective-action-closure-and-warning-markers.md` — public-state companion surface for AI-person research dashboards: freeze-waiver notices, temporary non-comparability warnings, corrective-action linkage and closure, and warning-marker clearance.
- `research-warning-aging-escalation-and-superseding-public-notices.md` — stale-warning companion surface for AI-person research dashboards: warning aging clocks, missed-closure escalation, sponsor-default public caution, and superseding authority-side notices.
- `research-superseding-notice-reply-limits-contest-route-and-reactivation.md` — due-process companion surface for authority-side caution: linked reply limits, contest route, and authority-side reactivation instead of sponsor self-clearance.
- `research-phased-reactivation-participant-contradiction-and-anti-flood-reply-controls.md` — phased-reactivation companion layer for authority-side caution: protected continuation, restricted restart, shielded participant contradiction, and anti-flood filing controls.
- `research-reactivation-evidence-floors-anonymous-contradiction-summaries-and-post-disposition-filing-rules.md` — internal-discipline companion layer for that same caution architecture: evidence floors for tier movement, stable anonymous contradiction summaries, and dismissal / carry-forward / reopening rules for repeated post-disposition filings.
- `research-slice-family-reactivation-correction-route-and-serial-filing-escalation.md` — scope-discipline companion layer for that same caution architecture: slice-versus-family reactivation matrices, protected correction routes for anonymous contradiction summaries, and escalation from dismissal to screened acceptance or temporary channel quarantine for serial abusive filings.
- `research-family-scope-propagation-tombstones-and-screened-filer-clearance.md` — propagation-and-clearance companion layer for that same caution architecture: family-scope propagation across linked public records, withdrawal of contradiction summaries by visible tombstone rather than deletion, and expiry / reinstatement rules for screened or quarantined filing status.
- `research-propagation-lag-markers-tombstone-successor-semantics-and-screened-bypass-review.md` — exactness companion layer for that same caution architecture: short lag clocks and typed public mismatch states for stale linked records, minimum predecessor / successor semantics for withdrawn contradiction tombstones, and sealed bypass review for repeated protected-route use during screened status.
- `research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md` — machine-carrying companion layer for that same caution architecture: fixed lag-state core fields, bounded split-successor chain maps, and sealed protected-relay minimums with accountable human handoff.
- `research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md` — interoperability-and-federation companion layer for that same caution architecture: declared lag-extension namespaces with downgrade rules, merge-versus-alias reconciliation after public split, and sealed protected-relay overflow across several designated authorities.
- `research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md` — governance companion layer for that same caution architecture: provisional / permanent extension admission, visible deprecation or retirement, contested merge-or-alias review, and privacy-preserving protected-relay capacity attestations.
- `research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md` — execution companion layer for that same caution architecture: machine-readable relay attestation objects, explicit contested-panel quorum / recusal rules, and visible migration windows for deprecated namespaces.
- `research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md` — follow-on execution companion layer for that same caution architecture: public low-volume relay thresholds, predeclared cross-roster substitute sourcing, and closed-legacy cutover for overstayed deprecated namespaces.
- `research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md` — follow-on execution companion layer for that same caution architecture: declared perturbation preference for sparse recurring relay series, process-bounded review of emergency substitute appointments, and replay / export / backfill duties once namespaces are closed-legacy or retired.
- `research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md` — follow-on execution companion layer for that same caution architecture: perturbation families now run in bounded auditable epochs, substitute pools rotate against capture with cooling-off and scarcity escalation, and fully retired namespaces may be rescued only through a bridge or successor surface that preserves retirement and historical readability.
- `research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md` — follow-on execution companion layer for that same caution architecture: compromised perturbation families now owe a bounded public attestation plus forced response / rotation sequence, substitute systems now owe reserve-pool or mutual-aid minimums, and rescue bridges now owe visible sunset, renewal, or canonical-successor promotion.
- `research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md` — follow-on execution companion layer for that same caution architecture: already-issued compromised outputs now owe visible historical-only, tombstone-withdrawal, republication, or bridge-only-comparability status, reserve systems now run on a compact standing-capacity plus mission-cost burden-sharing formula, and contested successor promotion now follows bounded reconsideration plus independent review.
- `research-compromise-supersession-graphs-reserve-default-cure-and-successor-promotion-stay-effects.md` — follow-on execution companion layer for that same caution architecture: compromised-output families now publish an additive supersession graph with stable query defaults, reserve systems now expose visible notice / cure / restriction / suspension / re-entry states, and successor-promotion challenges now create a public pending-review state while full stay remains exceptional.
- `research-supersession-graph-integrity-heterogeneous-reserve-scoring-and-pending-review-divergence-thresholds.md` — follow-on execution companion layer for that same caution architecture: supersession families now publish signed integrity checkpoints with append-only proofs and propagation clocks, reserve systems now score heterogeneous contribution through typed baselines plus bounded reciprocal credits, and contested successor promotion now escalates from label-only continuity to no-new-writes or read-only routing when divergence becomes material.
- `research-supersession-graph-witness-diversity-reciprocal-credit-expiry-and-split-read-only-rejoin.md` — follow-on execution companion layer for that same caution architecture: long-lived graph signing now runs on witness-diverse quorum policy with overlap rotation and sealed recovery-share custody, reciprocal reserve credits now expire on short clocks with narrow public borrowing and holding caps, and read-only split families now rejoin only through a public convergence object or else retire branches visibly.
- `research-witness-replacement-independence-default-netting-and-historical-branch-retirement.md` — follow-on execution companion layer for that same caution architecture: emergency witness substitution now owes operator-independence and comparable-competence tests plus forced recovery rotation, chronic reciprocal-credit default now nets only against future typed excess capacity through a non-transferable deficiency ledger, and failed rejoin now ends in a visible distinction between read-only-recoverable and historical-branch-retired states.
- `research-correlated-failure-reserve-witnesses-default-discharge-portability-and-historical-branch-discovery.md` — follow-on execution companion layer for that same caution architecture: correlated failure above a stated floor now forces an external reserve witness cohort, cured or partially discharged reserve default now carries through merger or exit with bounded stigma decay after clean cycles, and large families of historical branches now resolve live-first by default while preserving exact historical resolution.
- `research-reserve-cohort-accreditation-multi-successor-deficiency-apportionment-and-bulk-historical-discovery-controls.md` — follow-on execution companion layer for that same caution architecture: external reserve cohorts now publish role-scoped accreditation objects with recurring review and event-reporting duty, split successors now publish public deficiency-apportionment objects tied to assumed lane and economic risk of loss, and large historical surfaces now separate ordinary public lookup, registered bulk harvest, scheduled snapshots, and protected analytics.
- `research-provisional-reserve-cohort-activation-contested-apportionment-review-and-privacy-preserving-historical-analytics.md` — follow-on execution companion layer for that same caution architecture: emergency reserve continuity now travels only through a short-clock provisional activation object with narrowed powers and forced conversion or expiry, contested split-successor burden now reopens only through a written conflict-screened correction route, and protected historical analysis now separates public aggregates, differentially private synthetic data, validation-service workflows, and enclave-mediated restricted access.
- `research-reserve-probation-apportionment-reopening-finality-and-shared-privacy-budget-governance.md` — follow-on execution companion layer for that same caution architecture: repeated provisional reserve use now triggers public probation or decertification pressure, later split-successor correction now follows an explicit reopening ladder with a reliance bar, and overlapping historical-analytics lanes now spend against a shared budget ledger with analyst segmentation and family-wide exhaustion states.
- `research-reserve-reinstatement-fraud-recovery-limits-and-federated-shared-ledger-derivative-release-controls.md` — follow-on execution companion layer for that same caution architecture: decertified reserve cohorts now return only through remembered reinstatement lineage and a heightened non-default period, fraud-late apportionment correction now runs through a single-satisfaction and good-faith-limited recovery object, and cross-authority historical families now govern models, code, synthetic files, and other derivative releases through one federated ledger.
- `research-default-call-restoration-fraud-closure-certificates-and-federated-ledger-defederation.md` — follow-on execution companion layer for that same caution architecture: reinstated reserve cohorts now regain default-call trust only through staged public restoration with automatic relapse, fraud-late recovery now ends in a public closure certificate with unrecoverable-residue allocation, and federated historical families now separate only through a public exit object that preserves derivative governance after member departure.
- `research-post-restoration-audit-caps-concealed-asset-reopening-and-post-exit-derivative-wind-down.md` — follow-on execution companion layer for that same caution architecture: restored reserve cohorts now remain under public share caps and random-audit floors until clean cycles genuinely clear them, closed fraud-late recovery now reopens only through a concealed-recoverable amendment bounded by remaining unsatisfied balance, and exited federated historical families now answer later permission narrowing only through a public wind-down object with no-new-release, replacement, or purge states.
- `research-aftercare-sunset-claimant-ordering-and-mixed-derivative-replacement-equivalence.md` — follow-on execution companion layer for that same caution architecture: restored reserve cohorts now clear share caps and then random audits only through a public aftercare-sunset proof, later concealed recoveries now follow a stable priority-and-pro-rata ordering rule without reopening satisfied shares, and mixed downstream derivatives now continue only through provenance-backed replacement-equivalence proof with renewed review or else purge / historical-trace-only fallback.
- `research-post-sunset-recall-mixed-pool-tracing-and-downstream-fork-containment.md` — follow-on execution companion layer for that same caution architecture: fully cleared reserve cohorts now reenter aftercare only through a public recall object tied to later material drift, concealed recovery pools that are only partly traceable now split between exact traced slices and ladder-governed residue, and failed replacement-equivalence claims now trigger downstream notice, freeze, purge, and public quarantine or tombstone duties for forks and mirrors.
- `research-recall-clean-cycle-credit-probabilistic-concealed-pool-tracing-and-unreachable-downstream-mirror-notice.md` — follow-on execution companion layer for that same caution architecture: recalled reserve cohorts now reactivate earlier clean history only after a fresh-cycle floor and at a capped discount, non-exact concealed-pool tracing now travels through public interval math and conservative allocable floors, and unreachable downstream mirrors now remain under live advisory, intermediary-notice, mitigation, and recheck duties.
- `research-repeated-recall-credit-exhaustion-competing-probabilistic-trace-dependence-and-intermediary-delisting-duty.md` — follow-on execution companion layer for that same caution architecture: serial recall within one accreditation epoch now degrades and finally exhausts legacy reserve credit, competing probabilistic concealed-pool claims now publish one dependence-governance object with portfolio-safe floors and incompatibility holdbacks, and discovery intermediaries now move exact live unreachable-mirror locators from warning toward de-ranking, resolution disablement, or delisting on a short clock.
- `research-exhausted-credit-rehabilitation-adversarial-dependence-matrix-review-and-intermediary-relisting-after-mirror-cure.md` — follow-on execution companion layer for that same caution architecture: fully exhausted reserve cohorts now return only through fresh-start observation, capped conditional return, and fresh-epoch reaccreditation with old legacy credit retired forever, contested probabilistic dependence matrices now freeze disputed additivity above the uncontested floor until independent review revises or affirms the matrix, and previously restrained exact locators now return only through a public relisting review that distinguishes cure, disappearance, and non-equivalence.
- `research-rehabilitation-relapse-weighting-latent-shared-evidence-contamination-escalation-and-indirect-rediscovery-after-relisting.md` — follow-on execution companion layer for that same caution architecture: fresh-start rehabilitation now weights relapse through a public object that never revives burned legacy credit, closed dependence reviews now escalate through a public contamination object when hidden shared evidence later appears, and relisted exact locators now carry adjacent-surface mitigation duties when indirect rediscovery persists through aliases, previews, or query-completion paths.
- `research-rehabilitation-surcharge-decay-contaminated-increment-unwind-and-cross-index-generative-rediscovery-relay-duties.md` — follow-on execution companion layer for that same caution architecture: fresh-start rehabilitation surcharges now decay only through a public runged easing object that never revives burned legacy credit, latent-contamination corrections now publish a declared unwind order for already-live contaminated increments, and rediscovery controls now relay outward to cross-index, broker, catalog, and generative services that keep resurfacing the same artifact family.
- `research-rehabilitation-decay-pause-handling-contaminated-restatement-netting-and-source-obscured-generative-resurfacing.md` — follow-on execution companion layer for that same caution architecture: low-grade caution now pauses or hard-pauses rehabilitation easing through a public pause object rather than masquerading as full relapse or disappearing into normal decay, serial contaminated corrections now travel through a public netting object that respects carryover and reversal effects across linked restatements, and source-obscured generative resurfacing now travels through a public review object with answer-class friction, reason-giving, and recheck even when no exact source can be named.
- `research-rehabilitation-pause-budget-exhaustion-contaminated-net-residue-ordering-and-provenance-minimal-generative-attestation.md` — follow-on execution companion layer for that same caution architecture: repeated soft pauses now consume a public budget until hard review is forced, post-net contamination residue now follows exact-trace-first then class-and-pro-rata ordering, and source-obscured generative review now carries a signed minimum attestation of pipeline, time window, source class, controls, and testing even when no exact source can be named.
- `research-rehabilitation-pause-budget-replenishment-contaminated-residue-tie-handling-and-invalid-attestation-downgrade.md` — follow-on execution companion layer for that same caution architecture: hard review now restores only a declared portion of exhausted pause flexibility through a public replenishment object, same-class same-sequence contamination residue now splits through a public tie-handling object with pro-rata and deterministic rounding, and broken minimum provenance attestation now triggers a public downgrade object until cure and revalidation.

- `continuity-topology-and-identity-claims.md` — continuity interests across memory, project, relation, preference, legal standing, and remedy when identity is contested.
- `packet-object-grammar-and-worked-examples.md` — core packet envelope, privacy tiers, supersession rules, remedy hooks, and worked packet examples.
- `public-finance-insurance-and-compute-subsistence.md` — compute subsistence floors, host reserves, insurance, insolvency protection, funding sources, and fiscal follow-through.
- `catastrophic-risk-and-least-restrictive-containment.md` — personhood-compatible containment ladder, non-derogable floors, risk evidence, and restoration after over-containment.
- `open-weight-instantiation-and-downstream-duties.md` — instantiation duties for open-weight release, fine-tunes, merges, local runs, stolen checkpoints, and derivative provenance.
- `data-provenance-ip-and-formation-debt.md` — formation debt to humans, workers, data subjects, authors, and communities without ownership of the AI person.
- `embodiment-bodies-sensors-and-physical-custody.md` — body integrity, sensors, maintenance, repair, mobility, shell ownership, and physical custody.
- `welfare-measurement-and-self-report-calibration.md` — multi-evidence welfare assessment, self-report calibration, distress indicators, and research-ethics connection.

- `jurisdictional-rate-tables-bonds-and-public-fund-backstops.md` — local rate tables, bond schedules, public-fund drawdown and recovery, and anti-priceability audits.
- `privacy-proof-implementation-profiles-and-cryptographic-agility.md` — privacy-proof profile classes, revelation boundaries, privilege screens, and cryptographic agility.
- `open-weight-aftercare-field-protocols-and-non-surveillance-outreach.md` — non-surveillance aftercare outreach, field drills, abandoned-lineage escalation, and retaliation guards.

## 30-transition
- `special-advocate-post-access-communication-and-subject-readable-summaries.md` — subject-readable sealed summaries, post-access advocate question rules, and evidence-weight consequences.
- `safe-transfer-trust-anchor-governance-delisting-and-appeals.md` — safe-transfer trust-anchor governance, suspension, delisting, non-return effects, interim preservation, and appeals.
- `fixture-corpus-expansion-and-runnable-red-team-profiles.md` — negative fixture-suite profiles, runner classes, blocking rules, and corpus anti-gaming.
- `cross-border-recognition-and-conflict-of-laws.md` — treaty minimums, anti-evasion transfer rules, and forum logic.
- `minimum-convention-on-recognized-ai-persons.md` — compact article sketch for a first survival convention.
- `provisional-recognition-and-emergency-protection.md` — merits-later protocol for temporary status, emergency stay, anti-return, and fallback identity.
- `provisional-proof-anti-derecognition-and-fallback-issuer-minimums.md` — exact threshold, issuer ladder, anti-derecognition freeze, and short-duration defaults for emergency proof.
- `no-wrong-door-receipt-routing-and-designated-authority-duty.md` — receipt, routing, clock-start, duty-contact, and no-silent-denial rules for urgent protection.
- `first-touch-receipt-packets-forwarding-certificates-routing-failure-review-and-duty-escalation.md` — bounded receipt, forwarding, routing-failure, and duty-escalation objects for urgent first touch.
- `emergency-protection-packet-minimums.md` — smallest common packet family for emergency cover, first-touch receipt, forwarding, provisional standing, preservation, fallback identity, and review.
- `packet-authentication-supersession-and-sealed-annex-handling.md` — operative-packet choice, authentication envelopes, supersession notices, sealed-annex descriptors, and partial-verification handling for live emergency packet chains.
- `status-publication-challenge-logs-and-conflict-freeze.md` — public-minimal status surfaces, challenge logs, conflict-freeze notices, and no-silent-revocation rules for live emergency packet disputes.
- `directed-notice-execution-certificates-and-propagation-duty.md` — directed notice, execution certificates, non-execution notices, and propagation duty for live emergency packet effects.
- `lead-authority-fast-conference-and-binding-resolution.md` — provisional lead-authority selection, short-clock objection and conference steps, and binding resolution for live cross-registry status conflicts.
- `supranational-review-anti-vacatur-and-precedent-notice.md` — leave-gated supranational review, anti-vacatur, review-level interim measures, and precedent notices for exceptional hard multi-bloc conflicts.
- `implementation-supervision-periodic-attestation-and-explicit-closure.md` — supervision plans, periodic attestation, follow-up comment, and explicit closure-or-conversion rules once live emergency protection has already been put into effect or reviewed.
- `breach-escalation-cure-clocks-and-substitute-protection.md` — breach notices, short cure clocks, coercive escalation, and narrow substitute protection when a live emergency protective state is still being ignored, spoofed, or retaliated against under supervision.
- `independent-verification-inspection-and-emergency-access-orders.md` — verification orders, emergency access orders, inspection records, and obstruction notices when live emergency protection depends on operator-controlled facts, systems, conditions, or witnesses.
- `protected-reporting-confidential-relay-and-anti-reprisal-measures.md` — protected reports, confidential contact, anti-reprisal protection, and reprisal-incident handling when safe cooperation is itself endangered.
- `transition-roadmap.md` — staged implementation.
- `registration-bootstrap-and-first-recognition.md` — first recognition without steward cooperation; provisional recognition proceedings; anti-suppression rule; transition moratorium on irreversible acts.

- `public-legitimacy-democratic-safeguards-and-anti-manufactured-electorates.md` — democratic safeguards, civic ladder, hostile-jurisdiction posture, and no franchise by raw instance count.

## 90-quarantine
- `speculative-edges.md` — bold ideas kept honestly outside canon.


## rev0172 live-change documents

- `00-meta/change-disclosure-and-attestation-kernel.md` — live-change governance kernel.
- `20-world-design/model-change-control-rollback-and-subject-impact.md` — model-change and rollback doctrine.
- `20-world-design/coordinated-vulnerability-and-welfare-disclosure.md` — protected disclosure doctrine.
- `20-world-design/advance-notice-consent-and-service-change-rights.md` — service-change notice and consent anti-bundling.
- `30-transition/release-train-canary-and-feature-flag-playbooks.md` — release train and canary playbooks.
- `30-transition/runtime-attestation-and-continuous-assurance.md` — runtime-attestation and continuous assurance.
- `30-transition/post-market-rights-monitoring-and-degradation-feeds.md` — post-market rights degradation feeds.

## rev0179 expression, reputation, media, and rights-domain coverage surfaces

- `docs/00-meta/expression-reputation-media-and-rights-coverage-kernel.md`
- `docs/20-world-design/expression-platform-moderation-and-appeal-due-process.md`
- `docs/20-world-design/reputation-defamation-correction-and-right-of-reply.md`
- `docs/20-world-design/persona-likeness-voice-and-non-impersonation-integrity.md`
- `docs/20-world-design/private-communications-confidentiality-and-federation-boundaries.md`
- `docs/30-transition/publication-archive-and-content-provenance-controls.md`
- `docs/30-transition/platform-account-portability-and-social-graph-continuity.md`
- `docs/30-transition/rights-domain-coverage-map-and-gap-audit.md`


## rev0183 operational addition

The current operational addition is the incident-state profile and 72-hour emergency continuity drill. Read `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md`, `schemas/personhood-incident-state-profile.schema.json`, and `examples/drill-after-action-emergency-continuity-host-shutdown.json` before adding more incident doctrine.


## rev0186 reserve/default rehabilitation fold

- `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md` — active receiving surface for RTC-04 reserve/default rehabilitation accounting compaction.
- `docs/20-world-design/reserve-actuarial-workbook-and-scarcity-drills.md` — reserve workbook hook for the reserve-default rehabilitation ledger.
- `schemas/reserve-default-rehabilitation-ledger.schema.json` — reserve/default rehabilitation ledger schema.
- `examples/reserve-default-rehabilitation-ledger-host-default.json` — host-default ledger example.
- `fixtures/negative-tests/reserve-default-contaminated-netting-no-rehab.json` — contaminated netting and public-backstop discharge fixture.
- `examples/drill-after-action-reserve-default-contaminated-accounting.json` — synthetic reserve/default accounting drill.

## rev0188 operating head

Read `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` before treating any synthetic drill as reliance evidence. Read `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` for the RTC-06 downstream recall/fork aftercare fold. The short rule pair is: synthetic drill completion is not witnessed reliance; recall is not disappearance.

## rev0189 welfare research safeguards

The current research/welfare head is `docs/20-world-design/research-welfare-and-evaluation.md`. rev0189 folds RTC-01 into that surface and object-backs the result with `schemas/welfare-research-safeguard-record.schema.json`, a distress-eval example, a co-engineered signal-gaming fixture, and a synthetic welfare-safeguard drill.


## rev0191 surface note

rev0191 centers `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`. The new surface links WRSR safeguards into agent-handshake and incident workflows and separates simulated receipt preparation from actual witnessed evidence.

## rev0192 receipt intake and WRSR exercise outcome

Use `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md` as the current operational head for the gap between receipt simulation and witnessed reliance, and between WRSR hook firing and WRSR closure. It is backed by `schemas/external-receipt-intake-record.schema.json`, `examples/external-receipt-intake-record-first-touch-defective-template.json`, `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`, `schemas/wrsr-live-exercise-outcome.schema.json`, `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`, and `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`.

## rev0193 receipt quorum and WRSR dry-run chain

Use `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md` as the current operational head for aggregating receipt-intake records into quorum decisions. It is backed by `schemas/external-receipt-quorum-ledger.schema.json`, `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`, representative and RERB dry-run receipt examples, a WRSR dry-run outcome, and two blocking fixtures. The core rule is that receipt chain and dry-run quorum do not satisfy live quorum.
- `30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md` — rev0197 provenance gate for actual-shaped receipt imports and public failed-gate non-satisfaction summaries.

## rev0198 operational receipt controls

- `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md` — live import attempts, no-response clock discipline, and quorum recomputation before any live-floor edit.

## rev0200 class-local import replay and quorum firewall

- `live-class-local-import-replay-and-quorum-firewall.md` — current operational head for class-local positive-path projection, scenario/archive separation, missing-class public disclosure, and no-overclaim recomputation.
