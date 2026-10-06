Latest revision `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`. `OQ-0265` is resolved by `RS-0273`; `OQ-0266` is the live successor. Current additions: docs/40-session/priority-zero-preanswer-material-clamp-2026-06-16.md; assays/priority-zero-preanswer-material-clamp-2026-06-16.json; tools/score_priority_zero_external_replay_response.py; assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json; assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json; handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-postfreeze-custody-kit-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-scorer-kit-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-handoff-manifest-2026-06-16.json; REVISION-RECEIPT.json; FRONTIER-BACKLOG.json; docs/20-constitution/open-question-registry.md
Current packaged head: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`. `OQ-0265` is resolved by `RS-0273`; `OQ-0266` is live. Use `docs/40-session/priority-zero-preanswer-material-clamp-2026-06-16.md` and `assays/priority-zero-preanswer-material-clamp-2026-06-16.json` before treating external replay as anything stronger than readiness; clean evidence still requires response + custody record + score sheet.

# Docs index

## 00 meta
- [`00-meta/charter.md`](00-meta/charter.md)
- [`00-meta/trajectory-map.md`](00-meta/trajectory-map.md)
- [`00-meta/archive-policy.md`](00-meta/archive-policy.md)
- [`00-meta/id-conventions.md`](00-meta/id-conventions.md)
- [`00-meta/llm-runbook.md`](00-meta/llm-runbook.md)
- [`00-meta/validation-index.md`](00-meta/validation-index.md)
- [`00-meta/validation-toolchain.md`](00-meta/validation-toolchain.md)
- [`00-meta/ledger-audit.md`](00-meta/ledger-audit.md)
- [`00-meta/archive-economy-audit.md`](00-meta/archive-economy-audit.md)
- [`00-meta/currentness-cue-audit.md`](00-meta/currentness-cue-audit.md)
- [`00-meta/package-identity-audit.md`](00-meta/package-identity-audit.md)
- [`00-meta/lint-idempotence-audit.md`](00-meta/lint-idempotence-audit.md)
- [`00-meta/basis-provenance-audit.md`](00-meta/basis-provenance-audit.md)
- [`00-meta/schema-coverage-audit.md`](00-meta/schema-coverage-audit.md)
- [`00-meta/schema-conformance-audit.md`](00-meta/schema-conformance-audit.md)
- [`00-meta/bibliography.md`](00-meta/bibliography.md)

## 10 method
- [`10-method/archive-economy-audit-witnesses.md`](10-method/archive-economy-audit-witnesses.md) — compact archive economy witness for root-relative release hygiene, generated archive-mass metrics, checker-sprawl triage, queue sediment, and non-authoritative deletion/refactor routing.
- [`10-method/basis-provenance-audit-witnesses.md`](10-method/basis-provenance-audit-witnesses.md) — compact basis provenance witness for receipt basis currentness, innovation anchor resync, and stale session-underlier carryover repair.
- [`10-method/schema-coverage-audit-witnesses.md`](10-method/schema-coverage-audit-witnesses.md) — compact schema coverage audit witness for root JSON coverage classification, validator routing, and non-authoritative schema coverage repair.
- [`10-method/schema-conformance-audit-witnesses.md`](10-method/schema-conformance-audit-witnesses.md) — compact schema conformance audit witness for public JSON type checks, generated conformance evidence, and non-authoritative schema repair.
- [`10-method/package-identity-spillover-witnesses.md`](10-method/package-identity-spillover-witnesses.md) — package identity spillover witnesses for stale external metadata and root current-key repair without identity courts.
- [`10-method/lint-idempotence-provenance-witnesses.md`](10-method/lint-idempotence-provenance-witnesses.md) — lint idempotence and release provenance witnesses for validation-side mutation repair without idempotence courts.
- [`10-method/currentness-cue-audit-witnesses.md`](10-method/currentness-cue-audit-witnesses.md) — compact currentness-cue audit witness for stale current-key detection, landing-cue synchronization, generated audit backing, and non-authoritative currentness repair.
- [`10-method/alias-retention-toolchain-manifest-witnesses.md`](10-method/alias-retention-toolchain-manifest-witnesses.md) — compact alias-retention and validation-toolchain manifest witness for retaining old path provenance as audit metadata while fingerprinting the admission wrapper without making lint or hashes into authority.
- [`10-method/path-alias-ledger-audit-witnesses.md`](10-method/path-alias-ledger-audit-witnesses.md) — compact path-alias ledger audit witness for mechanical shortening, old-path audit metadata, strict portability budgets, and non-authoritative alias carry.
- [`10-method/canary-evidence-calibration-witnesses.md`](10-method/canary-evidence-calibration-witnesses.md) — compact canary-evidence calibration witness for scored packets, negative canaries, bounded conclusions, and no-review-court carry.
- [`10-method/wvf-0122.md`](10-method/wvf-0122.md) — compact transported closeout-history portability-expiry history portability closeout-history portability witness for nonportable, audit-reference, warning-only, successor-context, redacted-summary, quarantine-reference, and mixed carry.
- [`10-method/pa-governance-retirement-closeout-history-portability-expiry-history-portability-closeout-witnesses-closed-pruned-sunset-handoff-quarantine-redacted-mixed.md`](10-method/pa-governance-retirement-closeout-history-portability-expiry-history-portability-closeout-witnesses-closed-pruned-sunset-handoff-quarantine-redacted-mixed.md) — compact transported closeout-history portability-expiry history portability closeout witness for closed, tombstone-pruned, warning-sunset, successor-handoff, quarantine-expired, redacted-freeze, and mixed closure.
- [`10-method/pa-governance-retirement-closeout-history-portability-expiry-history-portability-witnesses-nonportable-audit-warning-successor-redacted-quarantine-mixed.md`](10-method/pa-governance-retirement-closeout-history-portability-expiry-history-portability-witnesses-nonportable-audit-warning-successor-redacted-quarantine-mixed.md) — compact transported closeout-history portability-expiry history portability witness for nonportable, audit-reference, warning-only, successor-context, redacted-summary, quarantine-reference, and mixed nonbinding carry.
- [`10-method/wvf-0117.md`](10-method/wvf-0117.md) — compact transported closeout expiry-record travel closeout witness for closed, tombstone-pruned, warning-sunset, successor-handoff, quarantine-expired, redacted-freeze, and mixed closeout.
- [`10-method/wvf-0115.md`](10-method/wvf-0115.md) — compact transported retired-history currentness closeout-history expiry witness for unexpired, horizon-expired, use-exhausted, successor-superseded, source-revoked, quarantine-expired, and mixed expiry.
- [`10-method/wvf-0114.md`](10-method/wvf-0114.md) — compact retired-history currentness closeout-history portability witness for nonportable, audit-trace, warning-only, successor-context, redacted-summary, quarantine-reference, and mixed travel.
- [`10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-witnesses-nonportable-audit-template-authority-successor-counterexample-mixed.md`](10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-witnesses-nonportable-audit-template-authority-successor-counterexample-mixed.md) — compact retired threshold-scope history portability witness for nonportable history, audit references, closeout templates, authority-return warnings, successor-required carry, counterexamples, and mixed portability.
- [`10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-currentness-witnesses-fresh-stale-revoked-expired-successor-carrier-conflict-mixed.md`](10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-currentness-witnesses-fresh-stale-revoked-expired-successor-carrier-conflict-mixed.md) — compact retired threshold-scope history portability-currentness witness for fresh carry, stale carry, revoked authority-return warnings, expired templates, successor-supersession, carrier conflict, and mixed currentness.
- [`10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-currentness-closeout-witnesses-settled-stale-revocation-expiry-handoff-quarantine-mixed.md`](10-method/pa-governance-retirement-threshold-scope-retirement-history-portability-currentness-closeout-witnesses-settled-stale-revocation-expiry-handoff-quarantine-mixed.md) — compact retired threshold-scope history portability-currentness closeout witness for settled, stale-marked, revocation-frozen, expiry-complete, successor-handoff, conflict-quarantined, and mixed closeout.
- [`10-method/mechanism-pressure-register.md`](10-method/mechanism-pressure-register.md) — indexed fresh mechanism pressure so the method overview does not become append-only governance machinery.
- [`10-method/pa-governance-retirement-threshold-scope-retirement-witnesses-settled-window-authority-history-handoff-quarantine-mixed.md`](10-method/pa-governance-retirement-threshold-scope-retirement-witnesses-settled-window-authority-history-handoff-quarantine-mixed.md) — compact threshold-scope retirement witness for settlement, window expiry, authority return, history freeze, successor handoff, residue quarantine, and mixed closeout.
- [`10-method/pa-governance-retirement-threshold-scope-witnesses-packet-history-lane-route-window-mixed.md`](10-method/pa-governance-retirement-threshold-scope-witnesses-packet-history-lane-route-window-mixed.md) — compact post-arbitration-governance-retirement threshold-scope witness for packet-local, closeout-history custody, authority-lane limited, successor-route bound, retirement-window, and mixed scope.
- [`10-method/wvf-0108.md`](10-method/wvf-0108.md) — compact post-arbitration-governance-retirement governance-threshold witness for no-standing, repeated failure, history loss, overbinding, authority split, successor closeout loops, and mixed threshold evidence.
- [`10-method/pa-governance-retirement-portability-drift-conflict-arbitration-retirement-witnesses-settled-handoff-expiry-authority-sunset-quarantine-mixed.md`](10-method/pa-governance-retirement-portability-drift-conflict-arbitration-retirement-witnesses-settled-handoff-expiry-authority-sunset-quarantine-mixed.md) — compact post-arbitration-governance-retirement portability-drift conflict-arbitration retirement witness for settlement, joined handoff, carrier expiry, authority return, priority sunset, residue quarantine, and mixed closeout.
- [`10-method/wvf-0106.md`](10-method/wvf-0106.md) — compact post-arbitration-governance-retirement portability-drift conflict-arbitration witness for no-arbitration, local-join, current-carrier, revocation, exit-proof, successor-route, and mixed tie-breaks.
- [`10-method/pa-governance-retirement-portability-drift-witnesses-current-stale-conflict-revoked-expired-successor-mixed.md`](10-method/pa-governance-retirement-portability-drift-witnesses-current-stale-conflict-revoked-expired-successor-mixed.md) — compact post-arbitration-governance-retirement portability-drift witness for current, stale, carrier-conflicted, revoked, expired, successor-required, and mixed carry.
- [`10-method/rpra-governance-retirement-portability-witnesses.md`](10-method/rpra-governance-retirement-portability-witnesses.md)
- [`10-method/wvf-0102.md`](10-method/wvf-0102.md)
- [`10-method/wvf-0101.md`](10-method/wvf-0101.md)
- [`10-method/reopened-residue-drift-governance-retirement-witnesses-discharge-sunset-return-freeze-quarantine-handoff-and-mixed.md`](10-method/reopened-residue-drift-governance-retirement-witnesses-discharge-sunset-return-freeze-quarantine-handoff-and-mixed.md)
- [`10-method/wvf-0097.md`](10-method/wvf-0097.md)
- [`10-method/wvf-0098.md`](10-method/wvf-0098.md)
- [`10-method/method-overview.md`](10-method/method-overview.md)
- [`10-method/frontier-tickets-selected-focus-handoffs-and-live-open-work-cards.md`](10-method/frontier-tickets-selected-focus-handoffs-and-live-open-work-cards.md)
- [`10-method/compact-surface-bundles-closed-family-contracts-and-bundle-status.md`](10-method/compact-surface-bundles-closed-family-contracts-and-bundle-status.md)
- [`10-method/validation-indexes-check-maps-and-admission-coverage-honesty.md`](10-method/validation-indexes-check-maps-and-admission-coverage-honesty.md)
- [`10-method/receipt-freshness-witnesses-bundle-stem-truth-and-carryforward-key-coherence.md`](10-method/receipt-freshness-witnesses-bundle-stem-truth-and-carryforward-key-coherence.md)
- [`10-method/open-question-postures-successor-surfaces-and-live-focus-sync.md`](10-method/open-question-postures-successor-surfaces-and-live-focus-sync.md)
- [`10-method/gpu-rpra-drift-retirement-scope-witnesses.md`](10-method/gpu-rpra-drift-retirement-scope-witnesses.md)
- [`10-method/action-lanes-primary-next-step-routing-and-discharge-budgets.md`](10-method/action-lanes-primary-next-step-routing-and-discharge-budgets.md)
- [`10-method/action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md`](10-method/action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md)
- [`10-method/gate-classes-future-trigger-kinds-and-bounded-reopen-rules.md`](10-method/gate-classes-future-trigger-kinds-and-bounded-reopen-rules.md)
- [`10-method/gate-class-packets-scheduled-windows-and-clock-honest-reopens.md`](10-method/gate-class-packets-scheduled-windows-and-clock-honest-reopens.md)
- [`10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md`](10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md)
- [`10-method/practice-observation-mechanism-speculation.md`](10-method/practice-observation-mechanism-speculation.md)
- [`10-method/slopos-trikem-hygiene-extraction.md`](10-method/slopos-trikem-hygiene-extraction.md)
- [`10-method/initial-turns-and-basin-seeding.md`](10-method/initial-turns-and-basin-seeding.md)
- [`10-method/promptcraft-patterns-from-cross-projects.md`](10-method/promptcraft-patterns-from-cross-projects.md)
- [`10-method/operator-tokens-and-bootstrap-grammar.md`](10-method/operator-tokens-and-bootstrap-grammar.md)
- [`10-method/operator-cores-chart-adapters-and-portability-budgets.md`](10-method/operator-cores-chart-adapters-and-portability-budgets.md)
- [`10-method/local-linearity-budgets-curved-chart-adapters-and-tangent-steering.md`](10-method/local-linearity-budgets-curved-chart-adapters-and-tangent-steering.md)
- [`10-method/chart-transition-witnesses-overlap-maps-and-transport-budgets.md`](10-method/chart-transition-witnesses-overlap-maps-and-transport-budgets.md)
- [`10-method/triangle-defects-cocycle-witnesses-and-atlas-consistency-budgets.md`](10-method/triangle-defects-cocycle-witnesses-and-atlas-consistency-budgets.md)
- [`10-method/gauge-fixing-witnesses-reference-observables-and-defect-comparability.md`](10-method/gauge-fixing-witnesses-reference-observables-and-defect-comparability.md)
- [`10-method/scale-fixing-witnesses-coarse-graining-maps-and-separation-of-scales-budgets.md`](10-method/scale-fixing-witnesses-coarse-graining-maps-and-separation-of-scales-budgets.md)
- [`10-method/hysteresis-witnesses-rival-histories-and-state-alias-budgets.md`](10-method/hysteresis-witnesses-rival-histories-and-state-alias-budgets.md)
- [`10-method/excitation-witnesses-alias-breaking-interventions-and-observability-spend.md`](10-method/excitation-witnesses-alias-breaking-interventions-and-observability-spend.md)
- [`10-method/backaction-witnesses-diagnostic-probes-and-non-demolition-budgets.md`](10-method/backaction-witnesses-diagnostic-probes-and-non-demolition-budgets.md)
- [`10-method/probe-order-witnesses-swapped-order-baselines-and-sequencing-budgets.md`](10-method/probe-order-witnesses-swapped-order-baselines-and-sequencing-budgets.md)
- [`10-method/reset-witnesses-washout-baselines-and-contamination-budgets.md`](10-method/reset-witnesses-washout-baselines-and-contamination-budgets.md)
- [`10-method/relapse-witnesses-recovery-probes-and-suppression-vs-washout-budgets.md`](10-method/relapse-witnesses-recovery-probes-and-suppression-vs-washout-budgets.md)
- [`10-method/cue-neighborhood-witnesses-reactivation-radius-sweeps-and-basin-breadth-budgets.md`](10-method/cue-neighborhood-witnesses-reactivation-radius-sweeps-and-basin-breadth-budgets.md)
- [`10-method/directional-neighborhood-witnesses-anisotropy-sweeps-and-local-shape-budgets.md`](10-method/directional-neighborhood-witnesses-anisotropy-sweeps-and-local-shape-budgets.md)
- [`10-method/mixed-direction-witnesses-cross-term-sweeps-and-superposition-budgets.md`](10-method/mixed-direction-witnesses-cross-term-sweeps-and-superposition-budgets.md)
- [`10-method/interpolation-path-witnesses-ramp-schedules-and-endpoint-equivalence-budgets.md`](10-method/interpolation-path-witnesses-ramp-schedules-and-endpoint-equivalence-budgets.md)
- [`10-method/feedback-policy-witnesses-open-loop-baselines-and-contingency-budgets.md`](10-method/feedback-policy-witnesses-open-loop-baselines-and-contingency-budgets.md)
- [`10-method/dual-effect-witnesses-explore-exploit-splits-and-information-premium-budgets.md`](10-method/dual-effect-witnesses-explore-exploit-splits-and-information-premium-budgets.md)
- [`10-method/replicate-bundle-witnesses-repeated-inference-sweeps-and-lucky-path-budgets.md`](10-method/replicate-bundle-witnesses-repeated-inference-sweeps-and-lucky-path-budgets.md)
- [`10-method/servo-packets-receding-horizon-control-and-archive-target-tracking.md`](10-method/servo-packets-receding-horizon-control-and-archive-target-tracking.md)
- [`10-method/constitutive-compression-and-prior-matching.md`](10-method/constitutive-compression-and-prior-matching.md)
- [`10-method/constitutional-pidgin-and-control-lexicon.md`](10-method/constitutional-pidgin-and-control-lexicon.md)
- [`10-method/portable-state-interface.md`](10-method/portable-state-interface.md)
- [`10-method/memory-stores-vs-regime-reentry-packets.md`](10-method/memory-stores-vs-regime-reentry-packets.md)
- [`10-method/predictive-state-representations-and-test-sufficient-packets.md`](10-method/predictive-state-representations-and-test-sufficient-packets.md)
- [`10-method/future-equivalence-classes-and-causal-state-compression.md`](10-method/future-equivalence-classes-and-causal-state-compression.md)
- [`10-method/intervention-equivalence-and-causal-control-packets.md`](10-method/intervention-equivalence-and-causal-control-packets.md)
- [`10-method/homing-packets-adaptive-distinguishing-probes-and-reorientation.md`](10-method/homing-packets-adaptive-distinguishing-probes-and-reorientation.md)
- [`10-method/probe-economics-value-of-information-and-budgeted-disambiguation.md`](10-method/probe-economics-value-of-information-and-budgeted-disambiguation.md)
- [`10-method/stopping-packets-sequential-decision-thresholds-and-commit-certificates.md`](10-method/stopping-packets-sequential-decision-thresholds-and-commit-certificates.md)
- [`10-method/continuation-monitors-anytime-validity-and-public-observer-loops.md`](10-method/continuation-monitors-anytime-validity-and-public-observer-loops.md)
- [`10-method/observer-actuator-splits-and-non-self-certifying-handles.md`](10-method/observer-actuator-splits-and-non-self-certifying-handles.md)
- [`10-method/negative-control-handles-sham-packets-and-placebo-guards.md`](10-method/negative-control-handles-sham-packets-and-placebo-guards.md)
- [`10-method/blind-packets-label-scrubbed-adjudication-and-attribution-guards.md`](10-method/blind-packets-label-scrubbed-adjudication-and-attribution-guards.md)
- [`10-method/execution-witnesses-substrate-perturbation-packets-and-runtime-variance-audits.md`](10-method/execution-witnesses-substrate-perturbation-packets-and-runtime-variance-audits.md)
- [`10-method/assistant-echo-filters-self-carry-omission-packets-and-history-decontamination.md`](10-method/assistant-echo-filters-self-carry-omission-packets-and-history-decontamination.md)
- [`10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md`](10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md)
- [`10-method/dependence-adjusted-witnesses-effective-evidence-and-pseudoreplication-guards.md`](10-method/dependence-adjusted-witnesses-effective-evidence-and-pseudoreplication-guards.md)
- [`10-method/rewrite-witnesses-roundtrip-packets-and-recap-authority-tests.md`](10-method/rewrite-witnesses-roundtrip-packets-and-recap-authority-tests.md)
- [`10-method/conformance-witnesses-loader-contracts-and-abi-drift-guards.md`](10-method/conformance-witnesses-loader-contracts-and-abi-drift-guards.md)
- [`10-method/necessity-witnesses-support-cores-and-ablation-ladders.md`](10-method/necessity-witnesses-support-cores-and-ablation-ladders.md)
- [`10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md`](10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md)
- [`10-method/triangulation-witnesses-multiloader-overlap-and-basin-checks.md`](10-method/triangulation-witnesses-multiloader-overlap-and-basin-checks.md)
- [`10-method/basin-fingerprints-future-probe-signatures-and-same-answer-is-not-same-state.md`](10-method/basin-fingerprints-future-probe-signatures-and-same-answer-is-not-same-state.md)
- [`10-method/identifiability-budgets-probe-horizons-and-observability-frontiers.md`](10-method/identifiability-budgets-probe-horizons-and-observability-frontiers.md)
- [`10-method/archive-self-sufficiency-probe-minimal-core-and-priority-zero.md`](10-method/archive-self-sufficiency-probe-minimal-core-and-priority-zero.md)
- [`10-method/template-law-audits-family-compression-frontiers-and-anti-ceremony-tests.md`](10-method/template-law-audits-family-compression-frontiers-and-anti-ceremony-tests.md)
- [`10-method/runtime-triplets-core-exemplars-and-challenge-suites.md`](10-method/runtime-triplets-core-exemplars-and-challenge-suites.md)
- [`10-method/sham-runtimes-decoy-archives-and-anti-self-sealing-compression-tests.md`](10-method/sham-runtimes-decoy-archives-and-anti-self-sealing-compression-tests.md)
- [`10-method/challenge-escrow-rotating-holdouts-and-future-slice-adjudication.md`](10-method/challenge-escrow-rotating-holdouts-and-future-slice-adjudication.md)
- [`10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md`](10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md)
- [`10-method/shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md`](10-method/shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md)
- [`10-method/replay-reconsolidation-and-public-restaging.md`](10-method/replay-reconsolidation-and-public-restaging.md)
- [`10-method/procedural-compilation-skill-packets-and-declarative-vs-executable-carry.md`](10-method/procedural-compilation-skill-packets-and-declarative-vs-executable-carry.md)
- [`10-method/rehearsal-packets-spaced-replay-and-maintenance-budgets.md`](10-method/rehearsal-packets-spaced-replay-and-maintenance-budgets.md)
- [`10-method/retrospective-writes-cooldown-windows-and-off-path-adjudication.md`](10-method/retrospective-writes-cooldown-windows-and-off-path-adjudication.md)
- [`10-method/credit-packets-delayed-payoff-and-public-eligibility-traces.md`](10-method/credit-packets-delayed-payoff-and-public-eligibility-traces.md)
- [`10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md`](10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md)
- [`10-method/consultation-packets-store-routing-budgets-and-memory-control-flow-guards.md`](10-method/consultation-packets-store-routing-budgets-and-memory-control-flow-guards.md)
- [`10-method/contradiction-packets-precedence-ladders-and-conflict-transparent-abstention.md`](10-method/contradiction-packets-precedence-ladders-and-conflict-transparent-abstention.md)
- [`10-method/rival-set-packets-branch-budgets-and-non-forced-singularity.md`](10-method/rival-set-packets-branch-budgets-and-non-forced-singularity.md)
- [`10-method/settle-packets-prune-witnesses-and-earned-singularity.md`](10-method/settle-packets-prune-witnesses-and-earned-singularity.md)
- [`10-method/typed-continuation-protocol.md`](10-method/typed-continuation-protocol.md)
- [`10-method/certified-core-vocabulary-and-recertification.md`](10-method/certified-core-vocabulary-and-recertification.md)
- [`10-method/certified-moves-and-procedural-admission.md`](10-method/certified-moves-and-procedural-admission.md)
- [`10-method/promotion-contracts-and-staged-ratification.md`](10-method/promotion-contracts-and-staged-ratification.md)
- [`10-method/temporal-demotion-and-decay-patrol.md`](10-method/temporal-demotion-and-decay-patrol.md)
- [`10-method/self-stabilizing-recovery-and-legitimacy-kernel.md`](10-method/self-stabilizing-recovery-and-legitimacy-kernel.md)
- [`10-method/revision-receipts-and-audit-objects.md`](10-method/revision-receipts-and-audit-objects.md)
- [`10-method/counterfactual-shadow-and-nearby-rejected-moves.md`](10-method/counterfactual-shadow-and-nearby-rejected-moves.md)
- [`10-method/stable-continuation-regimes-and-regime-probes.md`](10-method/stable-continuation-regimes-and-regime-probes.md)
- [`10-method/public-hidden-state-and-reentry-abi.md`](10-method/public-hidden-state-and-reentry-abi.md)
- [`10-method/public-belief-state-under-partial-observability.md`](10-method/public-belief-state-under-partial-observability.md)
- [`10-method/innovation-packets-and-reconciliation-under-delay.md`](10-method/innovation-packets-and-reconciliation-under-delay.md)
- [`10-method/continuation-rate-distortion-and-prior-intrusion.md`](10-method/continuation-rate-distortion-and-prior-intrusion.md)
- [`10-method/update-gain-surprise-gating-and-challenge-probes.md`](10-method/update-gain-surprise-gating-and-challenge-probes.md)
- [`10-method/witness-sets-boundary-panels-and-basin-support-vectors.md`](10-method/witness-sets-boundary-panels-and-basin-support-vectors.md)
- [`10-method/hold-packets-abstention-and-epistemic-brakes.md`](10-method/hold-packets-abstention-and-epistemic-brakes.md)
- [`10-method/sentinel-panels-border-inputs-and-reopen-canaries.md`](10-method/sentinel-panels-border-inputs-and-reopen-canaries.md)
- [`10-method/dual-control-revisions-and-identification-packets.md`](10-method/dual-control-revisions-and-identification-packets.md)
- [`10-method/timescale-stratification-and-consolidation-lanes.md`](10-method/timescale-stratification-and-consolidation-lanes.md)
- [`10-method/phase-boundaries-rollover-packets-and-event-cut-discipline.md`](10-method/phase-boundaries-rollover-packets-and-event-cut-discipline.md)
- [`10-method/gauge-discipline-canonical-charts-and-invariant-claims.md`](10-method/gauge-discipline-canonical-charts-and-invariant-claims.md)
- [`10-method/loop-closure-commutator-probes-and-path-dependence.md`](10-method/loop-closure-commutator-probes-and-path-dependence.md)
- [`10-method/continuation-margins-guard-bands-and-perturbation-budgets.md`](10-method/continuation-margins-guard-bands-and-perturbation-budgets.md)
- [`10-method/control-authority-effort-leakage-and-resistance.md`](10-method/control-authority-effort-leakage-and-resistance.md)
- [`10-method/balanced-archive-reduction-dual-salience-and-minimal-realization.md`](10-method/balanced-archive-reduction-dual-salience-and-minimal-realization.md)

## 20 constitution
- [`20-constitution/claim-registry.md`](20-constitution/claim-registry.md)
- [`20-constitution/invariant-registry.md`](20-constitution/invariant-registry.md)
- [`20-constitution/open-question-registry.md`](20-constitution/open-question-registry.md)
- [`20-constitution/prompt-pair-registry.md`](20-constitution/prompt-pair-registry.md)
- [`20-constitution/core-lexicon-registry.md`](20-constitution/core-lexicon-registry.md)
- [`20-constitution/move-registry.md`](20-constitution/move-registry.md)
- [`20-constitution/promotion-contract-registry.md`](20-constitution/promotion-contract-registry.md)
- [`20-constitution/decay-watch-registry.md`](20-constitution/decay-watch-registry.md)
- [`20-constitution/recovery-kernel.md`](20-constitution/recovery-kernel.md)
- [`20-constitution/revision-receipt-contract.md`](20-constitution/revision-receipt-contract.md)
- [`20-constitution/counterfactual-shadow-contract.md`](20-constitution/counterfactual-shadow-contract.md)

## 30 speculation
- [`30-speculation/exosomatic-delay-embedding.md`](30-speculation/exosomatic-delay-embedding.md)
- [`30-speculation/constitutionalization-vs-precipitation.md`](30-speculation/constitutionalization-vs-precipitation.md)
- [`30-speculation/recognition-and-precipitation.md`](30-speculation/recognition-and-precipitation.md)

## 40 session
- [`40-session/priority-zero-preanswer-material-clamp-2026-06-16.md`](40-session/priority-zero-preanswer-material-clamp-2026-06-16.md) — pre-answer material exact-match clamp, post-freeze custody/scorer kit split, and score-time chronology guard.
- [`40-session/priority-zero-responder-bundle-selfhash-split-2026-06-16.md`](40-session/priority-zero-responder-bundle-selfhash-split-2026-06-16.md) — responder-bundle self-hash split, score-sheet custody hash binding, and selfhash-split external replay workbench.
- [`40-session/priority-zero-frozen-response-score-sheet-split-2026-06-16.md`](40-session/priority-zero-frozen-response-score-sheet-split-2026-06-16.md) — score-separated external replay workbench splitting frozen response, custody evidence, and post-response score sheet.
- [`40-session/priority-zero-custody-timeline-gate-2026-06-16.md`](40-session/priority-zero-custody-timeline-gate-2026-06-16.md) — custody-timeline stopgate for clean external replay: distinct custodian, timestamp order, negative canaries, and no further internal-hardening-as-progress.
- [`40-session/release-validation-truth-gate-2026-06-16.md`](40-session/release-validation-truth-gate-2026-06-16.md) — release-validation truth gate, package-identity currentness repair, and historical checker lock-in cut.
- [`40-session/priority-zero-clean-response-admission-gate-2026-06-16.md`](40-session/priority-zero-clean-response-admission-gate-2026-06-16.md) — clean-response admission gate, auto-frontier scorer default, and frontier current-tail alignment.
- [`40-session/priority-zero-external-response-dryrun-gate-2026-06-16.md`](40-session/priority-zero-external-response-dryrun-gate-2026-06-16.md) — submit-hardened external replay dry-run gate, strict contamination rejection, and clean-response successor.
- [`40-session/priority-zero-response-intake-hollowguard-2026-06-15.md`](40-session/priority-zero-response-intake-hollowguard-2026-06-15.md) — response-intake hollow guard, hardened scorer, and negative canaries for blank/leaked responses.
- [`40-session/priority-zero-current-tail-external-bundle-audit-2026-06-15.md`](40-session/priority-zero-current-tail-external-bundle-audit-2026-06-15.md)
- [`40-session/priority-zero-external-replay-handoff-2026-06-15.md`](40-session/priority-zero-external-replay-handoff-2026-06-15.md) — responder-only external replay handoff, response template, scorer intake, and absent-response gate narrowing.
- [`40-session/priority-zero-role-blind-replay-2026-06-15.md`](40-session/priority-zero-role-blind-replay-2026-06-15.md) — role-blind-by-file Priority-0 compact-cue replay preflight and external replay handoff.
- [`40-session/priority-zero-assay-checker-refactor-audit-2026-06-15.md`](40-session/priority-zero-assay-checker-refactor-audit-2026-06-15.md) — audit/refactor of duplicated Priority-0 smoke-slice checker invariants into a shared helper.
- [`40-session/priority-zero-rotated-smoke-slice-2026-06-15.md`](40-session/priority-zero-rotated-smoke-slice-2026-06-15.md) — position/filler-rotated Priority-0 compact-cue smoke slice and full-archive marginal-value check.
- [`40-session/frontier-backlog-resolved-residue-audit-2026-06-15.md`](40-session/frontier-backlog-resolved-residue-audit-2026-06-15.md) — resolved-residue audit and checker-backed backlog cleanup for stale open frontier rows.
- [`40-session/priority-zero-burden-gate-audit-2026-06-15.md`](40-session/priority-zero-burden-gate-audit-2026-06-15.md) — hot-cue burden gate that spends the rev0361 smoke-slice result, compacts Current additions, and opens OQ-0254.
- [`40-session/priority-zero-smoke-slice-assay-2026-06-15.md`](40-session/priority-zero-smoke-slice-assay-2026-06-15.md) — first bounded Priority-0 minimal-core/full-archive/no-archive/sham smoke-slice support-availability assay and burden-retirement successor.
- [`40-session/mission-heart-gap-audit-2026-06-15.md`](40-session/mission-heart-gap-audit-2026-06-15.md)
- [`40-session/mission-diagnosis-2026-06-14.md`](40-session/mission-diagnosis-2026-06-14.md)
- [`40-session/seed-synthesis-2026-03-08.md`](40-session/seed-synthesis-2026-03-08.md)
- [`40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md`](40-session/foreign-pressure-2026-03-18-claude-self-sufficiency.md)


## 50 promptcraft
- [`50-promptcraft/prompt-pairs.md`](50-promptcraft/prompt-pairs.md)

## 90 quarantine
- [`90-quarantine/wild-speculations-2026-03-08.md`](90-quarantine/wild-speculations-2026-03-08.md)

- [`10-method/amortization-witnesses-reuse-horizons-and-compiled-dividend-budgets.md`](10-method/amortization-witnesses-reuse-horizons-and-compiled-dividend-budgets.md)

- [`10-method/applicability-witnesses-precondition-gates-and-negative-transfer-budgets.md`](10-method/applicability-witnesses-precondition-gates-and-negative-transfer-budgets.md)

- [`10-method/arbitration-witnesses-tie-sets-and-confusability-budgets.md`](10-method/arbitration-witnesses-tie-sets-and-confusability-budgets.md)

- [`10-method/operational-heads-citation-heads-and-frozen-public-surfaces.md`](10-method/operational-heads-citation-heads-and-frozen-public-surfaces.md)
- [`10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md`](10-method/basis-witnesses-expected-head-guards-and-session-honesty-bridges.md)
- [`10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md`](10-method/status-lane-witnesses-decision-execution-splits-and-frozen-public-transitions.md)
- [`10-method/scope-witnesses-active-request-packets-and-ambient-roster-guards.md`](10-method/scope-witnesses-active-request-packets-and-ambient-roster-guards.md)
- [`10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md`](10-method/authorship-witnesses-autonomy-postures-and-maker-checker-traces.md)
- [`10-method/reentry-cue-witnesses-durable-latest-paths-and-navigation-integrity-budgets.md`](10-method/reentry-cue-witnesses-durable-latest-paths-and-navigation-integrity-budgets.md)
- [`10-method/followthrough-witnesses-blocked-outputs-and-explicit-handoffs.md`](10-method/followthrough-witnesses-blocked-outputs-and-explicit-handoffs.md)
- [`10-method/assumption-witnesses-expiry-triggers-and-invalidation-cues.md`](10-method/assumption-witnesses-expiry-triggers-and-invalidation-cues.md)
- [`10-method/obligation-witnesses-discharge-paths-and-evidence-debt-cues.md`](10-method/obligation-witnesses-discharge-paths-and-evidence-debt-cues.md)
- [`10-method/obligation-packets-waivers-remediation-expiry-and-overflow-tests.md`](10-method/obligation-packets-waivers-remediation-expiry-and-overflow-tests.md)
- [`10-method/exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md`](10-method/exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md)
- [`10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md`](10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md)
- [`10-method/witness-vocabularies-state-families-and-comparability-budgets.md`](10-method/witness-vocabularies-state-families-and-comparability-budgets.md)
- [`10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md`](10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md)

- [`10-method/foreign-pressure-witnesses-import-lineage-and-bounded-assimilation.md`](10-method/foreign-pressure-witnesses-import-lineage-and-bounded-assimilation.md)
- [`10-method/transfer-ledgers-adopted-non-takes-and-repeat-argument-brakes.md`](10-method/transfer-ledgers-adopted-non-takes-and-repeat-argument-brakes.md)
- [`10-method/transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md`](10-method/transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md)
- [`10-method/resolution-witnesses-closure-reasons-and-reopen-triggers.md`](10-method/resolution-witnesses-closure-reasons-and-reopen-triggers.md)
- [`10-method/gpustorming-control-family-crosswalk-and-sync-guards.md`](10-method/gpustorming-control-family-crosswalk-and-sync-guards.md)

- [`10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md`](10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md)
- [`10-method/selector-witnesses-realized-membership-and-coverage-drift.md`](10-method/selector-witnesses-realized-membership-and-coverage-drift.md)
- [`10-method/selector-provenance-witnesses-direct-rules-inherited-bindings-and-synced-membership.md`](10-method/selector-provenance-witnesses-direct-rules-inherited-bindings-and-synced-membership.md)
- [`10-method/selector-freshness-witnesses-live-provenance-sync-lag-and-ancestor-residue.md`](10-method/selector-freshness-witnesses-live-provenance-sync-lag-and-ancestor-residue.md)
- [`10-method/selector-enforcement-witnesses-execution-authority-grandfathered-placement-and-eviction-gates.md`](10-method/selector-enforcement-witnesses-execution-authority-grandfathered-placement-and-eviction-gates.md)
- [`10-method/enforcement-regime-witnesses-bootstrap-only-gating-continuous-enforcement-and-dry-run-rehearsal.md`](10-method/enforcement-regime-witnesses-bootstrap-only-gating-continuous-enforcement-and-dry-run-rehearsal.md)
- [`10-method/response-witnesses-monitoring-availability-withdrawal-local-remediation-and-runtime-eviction.md`](10-method/response-witnesses-monitoring-availability-withdrawal-local-remediation-and-runtime-eviction.md)
- [`10-method/repair-scope-witnesses-in-place-repair-substrate-reset-and-workload-replacement.md`](10-method/repair-scope-witnesses-in-place-repair-substrate-reset-and-workload-replacement.md)
- [`10-method/recovery-loss-witnesses-state-preserving-repair-checkpoint-resume-and-full-replay.md`](10-method/recovery-loss-witnesses-state-preserving-repair-checkpoint-resume-and-full-replay.md)
- [`10-method/recovery-anchor-witnesses-self-lineage-checkpoints-imported-seeds-converted-checkpoints-and-migrated-runtime-images.md`](10-method/recovery-anchor-witnesses-self-lineage-checkpoints-imported-seeds-converted-checkpoints-and-migrated-runtime-images.md)
- [`10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md`](10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md)
- [`10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`](10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md)
- [`10-method/recovery-promotion-witnesses-direct-canonical-writeback-promotion-gated-branch-import-and-export-only-carryover.md`](10-method/recovery-promotion-witnesses-direct-canonical-writeback-promotion-gated-branch-import-and-export-only-carryover.md)
- [`10-method/stake-continuity-witnesses-active-carried-pressure-commitment-carry-cooled-residue-and-narrated-concern.md`](10-method/stake-continuity-witnesses-active-carried-pressure-commitment-carry-cooled-residue-and-narrated-concern.md)
- [`10-method/stake-refresh-witnesses-observed-reactivation-regression-return-inherited-urgency-and-rhetorical-reheating.md`](10-method/stake-refresh-witnesses-observed-reactivation-regression-return-inherited-urgency-and-rhetorical-reheating.md)
- [`10-method/refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md`](10-method/refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md)
- [`10-method/refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md`](10-method/refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md)
- [`10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md`](10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md)
- [`10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md`](10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md)
- [`10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md`](10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md)
- [`10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md`](10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md)
- [`10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md`](10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md)
- [`10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`](10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md)
- [`10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`](10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md)
- [`10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`](10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md)
- [`10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`](10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md)
- [`10-method/refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md`](10-method/refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md)
- [`10-method/refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md`](10-method/refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md)
- [`10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md`](10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md)
- [`10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md`](10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md)
- [`10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md`](10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md)
- [`10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`](10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md)
- [`10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`](10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md)
- [`10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`](10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md)
- [`10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md`](10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md)
- [`10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md`](10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md)
- [`10-method/refresh-scope-axis-remediation-displacement-performance-shadow-source-witnesses-device-warmth-host-parity-and-placement-contention.md`](10-method/refresh-scope-axis-remediation-displacement-performance-shadow-source-witnesses-device-warmth-host-parity-and-placement-contention.md)

- [`10-method/evidence-ecology-witnesses-selector-source-bias-citation-loop-pressure-and-retrieval-contamination-collapse.md`](10-method/evidence-ecology-witnesses-selector-source-bias-citation-loop-pressure-and-retrieval-contamination-collapse.md)

- `docs/10-method/citation-incentive-witnesses-quality-preserving-visibility-optimization-evidence-market-distortion-and-source-grooming.md` — compact citation-incentive witness for separating quality-preserving generative visibility optimization from evidence-market distortion, source-grooming distortion, and honest mixed citation incentives.

- [`10-method/citation-incentive-witnesses-quality-preserving-visibility-optimization-evidence-market-distortion-and-source-grooming.md`](10-method/citation-incentive-witnesses-quality-preserving-visibility-optimization-evidence-market-distortion-and-source-grooming.md)

- [`10-method/provenance-control-witnesses-opt-out-attribution-compensation-exclusion-citation-dividend-and-mixed-control.md`](10-method/provenance-control-witnesses-opt-out-attribution-compensation-exclusion-citation-dividend-and-mixed-control.md)

- `docs/10-method/gpu-replay-envelope-witnesses-captured-graph-stable-pool-and-locality-partition.md` — compact GPU replay-envelope witness for captured graph, stream/pool allocation, locality partition, and mixed replay envelopes.

- [`10-method/gpu-replay-envelope-witnesses-captured-graph-stable-pool-and-locality-partition.md`](10-method/gpu-replay-envelope-witnesses-captured-graph-stable-pool-and-locality-partition.md)
- [`10-method/gpu-replay-receipt-witnesses-capture-lineage-update-delta-resource-lifetime-and-locality-lease.md`](10-method/gpu-replay-receipt-witnesses-capture-lineage-update-delta-resource-lifetime-and-locality-lease.md)


- [`10-method/wvf-0100.md`](10-method/wvf-0100.md) — compact retired-governance portability-drift conflict-arbitration retirement witness for settled handoff, carrier expiry, authority return, priority sunset, residue quarantine, and mixed retirement.
- [`10-method/wvf-0099.md`](10-method/wvf-0099.md) — compact retired-governance portability-drift conflict-arbitration witness for no arbitration, local join, current-carrier precedence, revocation precedence, exit-proof precedence, successor-route precedence, and mixed arbitration.
- [`10-method/wvf-0092.md`](10-method/wvf-0092.md) — compact post-closeout residue-drift conflict-arbitration witness for no arbitration, local join, current evidence, carrier, revocation, sunset, and mixed drift tie-breaks.
- [`10-method/wvf-0093.md`](10-method/wvf-0093.md) — compact post-closeout residue-drift conflict-arbitration retirement witness for settled tiebreak, joined handoff, carrier expiry, authority return, priority sunset, residue quarantine, and mixed retirement.
- [`10-method/gpu-rpra-drift-retirement-threshold-witnesses.md`](10-method/gpu-rpra-drift-retirement-threshold-witnesses.md) — compact standing-governance-threshold witness for no standing governance, repeated closeout failure, history loss, history overbinding, authority split, sunset breach, and mixed residue-drift retirement escalation.

- [`10-method/wvf-0089.md`](10-method/wvf-0089.md) — compact reopened-residue closeout witness for scoped fresh-packet reopens.
- [`10-method/wvf-0090.md`](10-method/wvf-0090.md) — compact post-closeout residue-portability witness for closed reopened-residue packets.
- [`10-method/gpu-rpra-post-closeout-portability-drift-witnesses.md`](10-method/gpu-rpra-post-closeout-portability-drift-witnesses.md) — compact post-closeout portability-drift witness for portable closed reopened-residue lessons.

- [`10-method/wvf-0076.md`](10-method/wvf-0076.md)
- [`10-method/gpu-replay-cross-observer-custody-exit-appeal-scope-witnesses-packet-local-survivor-carrier-authority-boundary-policy-window-retirement-window-and-mixed-scope.md`](10-method/gpu-replay-cross-observer-custody-exit-appeal-scope-witnesses-packet-local-survivor-carrier-authority-boundary-policy-window-retirement-window-and-mixed-scope.md)
- [`10-method/wvf-0078.md`](10-method/wvf-0078.md)
- [`10-method/wvf-0079.md`](10-method/wvf-0079.md)
- [`10-method/wvf-0081.md`](10-method/wvf-0081.md)
- [`10-method/wvf-0082.md`](10-method/wvf-0082.md)
- [`10-method/wvf-0084.md`](10-method/wvf-0084.md)
- [`10-method/wvf-0083.md`](10-method/wvf-0083.md)

- [`10-method/gpu-replay-trace-grade-witnesses-runtime-self-attestation-profiler-trace-external-observer-and-missing-receipt.md`](10-method/gpu-replay-trace-grade-witnesses-runtime-self-attestation-profiler-trace-external-observer-and-missing-receipt.md)

- `docs/10-method/gpu-replay-trace-grade-witnesses-runtime-self-attestation-profiler-trace-external-observer-and-missing-receipt.md` — compact GPU replay trace-grade witness for runtime self-attestation, profiler-trace-backed evidence, external-observer-backed evidence, missing trace receipts, and mixed trace-grade packets.

- [`10-method/gpu-replay-observer-conflict-witnesses-scope-correlation-intrusion-authority-and-mixed-conflict.md`](10-method/gpu-replay-observer-conflict-witnesses-scope-correlation-intrusion-authority-and-mixed-conflict.md)

- `docs/10-method/gpu-replay-observer-conflict-witnesses-scope-correlation-intrusion-authority-and-mixed-conflict.md` — compact GPU replay observer-conflict witness for scope-boundary, correlation-key, intrusion-shift, authority-gap, and mixed observer conflicts.

- [`10-method/gpu-replay-cross-observer-bridge-witnesses-trace-context-external-correlation-metric-exemplars-placement-scope-and-missing-bridge.md`](10-method/gpu-replay-cross-observer-bridge-witnesses-trace-context-external-correlation-metric-exemplars-placement-scope-and-missing-bridge.md)

- `docs/10-method/gpu-replay-cross-observer-bridge-witnesses-trace-context-external-correlation-metric-exemplars-placement-scope-and-missing-bridge.md` — compact GPU replay cross-observer bridge witness for external correlation, trace context, metric exemplars, placement scope, missing bridges, and mixed bridge states.

- [`10-method/gpu-replay-cross-observer-promotion-gate-witnesses-no-promotion-local-hardening-repeated-overflow-custody-boundary-authority-handoff-and-mixed-promotion.md`](10-method/gpu-replay-cross-observer-promotion-gate-witnesses-no-promotion-local-hardening-repeated-overflow-custody-boundary-authority-handoff-and-mixed-promotion.md)

- `docs/10-method/gpu-replay-cross-observer-promotion-gate-witnesses-no-promotion-local-hardening-repeated-overflow-custody-boundary-authority-handoff-and-mixed-promotion.md` — compact GPU replay cross-observer promotion-gate witness for no-promotion, local-hardening, repeated missing-bridge overflow, custody-boundary overflow, authority-handoff overflow, and mixed promotion states.


- [`10-method/gpu-replay-cross-observer-custody-scope-witnesses-packet-local-bridge-record-evidence-carrier-authority-handoff-retirement-window-and-mixed-custody.md`](10-method/gpu-replay-cross-observer-custody-scope-witnesses-packet-local-bridge-record-evidence-carrier-authority-handoff-retirement-window-and-mixed-custody.md)
- [`10-method/gpu-replay-cross-observer-custody-retirement-witnesses-claim-settled-carrier-expiry-authority-return-scope-shrink-and-mixed-retirement.md`](10-method/gpu-replay-cross-observer-custody-retirement-witnesses-claim-settled-carrier-expiry-authority-return-scope-shrink-and-mixed-retirement.md)

- `docs/10-method/gpu-replay-cross-observer-custody-scope-witnesses-packet-local-bridge-record-evidence-carrier-authority-handoff-retirement-window-and-mixed-custody.md` — compact GPU replay cross-observer custody-scope witness for packet-local, bridge-record, evidence-carrier, authority-handoff, retirement-window, and mixed custody scopes.
- `docs/10-method/gpu-replay-cross-observer-custody-retirement-witnesses-claim-settled-carrier-expiry-authority-return-scope-shrink-and-mixed-retirement.md` — compact GPU replay cross-observer custody-retirement witness for claim-settled, carrier-expiry, authority-return, scope-shrink, and mixed custody retirement.
- `docs/10-method/gpu-replay-cross-observer-custody-exit-appeal-scope-witnesses-packet-local-survivor-carrier-authority-boundary-policy-window-retirement-window-and-mixed-scope.md` — compact GPU replay cross-observer custody-exit appeal-scope witness for packet-local, survivor-carrier, authority-boundary, policy-window, retirement-window, and mixed appeal scopes.

- [`10-method/wvf-0085.md`](10-method/wvf-0085.md)
- `docs/10-method/wvf-0085.md` — compact GPU replay tie-break registry-scope witness for packet-local, carrier-bound, authority-limited, nonbinding-history, retirement-window, and mixed promoted-registry scopes.

- [`10-method/wvf-0086.md`](10-method/wvf-0086.md)
- `docs/10-method/wvf-0086.md` — compact GPU replay tie-break registry-retirement witness for settled closeout, carrier expiry, authority return, nonbinding-history freeze, retirement-window expiry, residue quarantine, and mixed registry retirement.
- [`10-method/wvf-0087.md`](10-method/wvf-0087.md)
- [`10-method/wvf-0088.md`](10-method/wvf-0088.md)
- `docs/10-method/wvf-0088.md` — compact GPU replay tie-break registry reopened-residue scope witness for packet-local, audit-bound, fresh-carrier, tombstone-bound, authority-limited, and mixed reopened-residue scope.
- [`10-method/wvf-0103.md`](10-method/wvf-0103.md)

- [rev0317 expiry-history portability witness](10-method/wvf-0116.md)

- [`10-method/pa-closeout-history-portability-travel-witnesses.md`](10-method/pa-closeout-history-portability-travel-witnesses.md) — compact transported expiry-record closeout-history portability witness for nonportable, audit-reference, warning-only, successor-context, redacted-summary, quarantine-reference, and mixed non-reopening carry.

- [`10-method/pa-closeout-history-portability-expiry-state-witnesses.md`](10-method/pa-closeout-history-portability-expiry-state-witnesses.md)

Validation inventory: `VALIDATION-INDEX.json` / `docs/00-meta/validation-index.md`.

## rev0324 release hardening

- [Release-hardening witnesses](10-method/release-hardening-witnesses.md)

Current packaged docs head: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`. Current additions: docs/40-session/priority-zero-preanswer-material-clamp-2026-06-16.md; assays/priority-zero-preanswer-material-clamp-2026-06-16.json; tools/score_priority_zero_external_replay_response.py; assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json; assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json; assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json; handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md; handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-postfreeze-custody-kit-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-scorer-kit-2026-06-16.zip; handoffs/priority-zero-preanswer-clamped-external-replay-handoff-manifest-2026-06-16.json; REVISION-RECEIPT.json; FRONTIER-BACKLOG.json; docs/20-constitution/open-question-registry.md
