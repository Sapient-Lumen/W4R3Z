# Archive index

## rev0289 update — black-hole horizon / thermodynamics / evaporation controls

rev0289 adds executable black-hole horizon-structure, thermodynamics/microstate, and evaporation/radiation controls, plus a generated source-reference usage audit. These additions make horizon recovery, entropy/microstate, generalized-second-law, Hawking-radiation, evaporation-endpoint, Page-curve, and black-hole-information language auditable without promoting any route.

## Top-level control surfaces

- `README.md` — project overview and stable orientation surface.
- `START_HERE.md` — human-readable mirror of the canonical entry surfaces, current release identity, current revision delta, canonical restart tiers, compact live posture, compact public-head status, compact restart-priority open-question slice, compact operator-warning subset, compact followthrough / standby-state summary, compact assumption-state summary, and compact rebuild-command subset; exact restart mirrors should be tool-rendered and lint-enforced.
- `AGENTS.md` — future-editor operating posture.
- `CHANGELOG.md` — terse revision history; details live in revision receipts and canonical surfaces.
- `RELEASE-MANIFEST.json` — canonical bundle identity for the current release; mirrored compactly in `START_HERE.md`.
- `REVISION-RECEIPT.json` — canonical current-revision rationale; mirrored compactly in `START_HERE.md`.
- `SURFACE-STATUS.json` — bundle / scientific-current / release-control / operational / citation head status and warning line.
- `context-pack.json` — canonical machine handoff with authoritative restart tiers, posture, restart-priority open-question slice, compact operator-warning subset, compact followthrough / standby-state summary, compact assumption-state summary, and compact rebuild-command subset.
- `ASSUMPTION-LEDGER.json` — revisionless durable assumption states: live assumptions, standby thresholds, and grouped retired phase history.
- `FOLLOWTHROUGH-QUEUE.json` — active next tasks only; may be empty when only stop rules remain.
- `WITNESS-VOCABULARY.json` — revisionless durable status, authority-state, move, queue, and head-label vocabulary.
- `DATACUBE-TRANSFER-LEDGER.json` — revisionless bounded record of imported machinery.
- `FOREIGN-PRESSURE-LEDGER.json` — revisionless external pressure preserved explicitly.
- `CANDIDATE-ROUTE-STATE-LEDGER.json` — executable current `OQ-0057` route-state rows with denominator fields, blockers, caps, and score codes.
- `NEGATIVE-CONTROL-LEDGER.json` — executable adversarial controls referenced by route rows.
- `EMPIRICAL-DELTA-LEDGER.json` — executable evidence-delta rows with route effects and caps.
- `DECISION-EXPERIMENT-LEDGER.json` — executable outcome-to-route rows for forecasts, possible observations, benchmarks, nulls, and public records.
- `PUBLIC-RECORD-CARRIER-LEDGER.json` — executable public-record carrier rows with custody, provenance, replay, challenge, versioning, and maximum-credit fields.
- `ACQUISITION-PROTOCOL-LEDGER.json` — executable acquisition/replay protocols attached to route, forecast, and decision rows.
- `CLAIM-ROUTE-BINDING-LEDGER.json` — executable claim-language bindings for high-risk `CL`/`OQ` exports.
- `EPISTEMIC-DEFEATER-LEDGER.json` — executable defeater rows for authority-loss conditions.
- `ROLLBACK-PROPAGATION-LEDGER.json` — executable rollback and repair rules for triggered defeaters.
- `EVIDENCE-SEVERITY-LEDGER.json` — executable severe-test rows for route-local positive evidence.
- `EVIDENCE-UNIT-LEDGER.json` — executable route-local evidence-unit rows for no-double-counting support accounting.
- `INDEPENDENCE-ASSUMPTION-LEDGER.json` — executable independence/correlation assumptions for evidence aggregation.
- `CREDIT-ALLOCATION-LEDGER.json` — executable route-local credit-allocation and non-compensation rows.
- `DOMAIN-OF-VALIDITY-LEDGER.json` — executable source/target validity-domain rows for route support.
- `TRANSPORTABILITY-LEDGER.json` — executable source-to-target support-transfer rows.
- `EXTRAPOLATION-FENCE-LEDGER.json` — executable forbidden-inference rows for local-to-global extrapolation control.
- `CAUSAL-MECHANISM-LEDGER.json` — executable route-local causal-structure and mechanism-denominator rows.
- `INTERVENTION-PROTOCOL-LEDGER.json` — executable direct / indirect / formal / simulation / natural-experiment / observational intervention-status rows.
- `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json` — executable alternative-world, model-intervention, invariance, and failure-mode rows.
- `AUTHORITY-DEPENDENCY-GRAPH.json` — generated support/attack edge graph for rollback propagation and evidence-credit dependencies.
- `RECORD-DENOMINATOR-TEMPLATES.json` — compact field template and vocabulary for route denominators.
- `PROOF-OBLIGATION-LEDGER.json` — executable proof / theorem / derivation obligation rows.
- `ASSUMPTION-DISCHARGE-LEDGER.json` — executable assumption inventory and discharge rows.
- `FORMALIZATION-COVERAGE-LEDGER.json` — executable proof-assistant / proof-certificate / formalized-fragment coverage rows.
- `IDEALIZATION-LEDGER.json` — executable ideal-model / simplified-target rows.
- `APPROXIMATION-ERROR-LEDGER.json` — executable approximation-error budget and propagation rows.
- `LIMIT-INTERCHANGE-LEDGER.json` — executable limit-sequence, commutation, singularity, and finite-recovery rows.
- `REGULARIZATION-SCHEME-LEDGER.json` — executable regulator, cutoff, subtraction, basis, simulator, survey, pipeline, and package-scheme rows.
- `RENORMALIZATION-FLOW-LEDGER.json` — executable RG-flow, running-parameter, fixed-point, universality, and scale-setting rows.
- `MATCHING-CONDITION-LEDGER.json` — executable source-to-target scale, EFT, threshold, counterterm, Wilson-coefficient, and public-record matching rows.
- `INFORMATION-FLOW-LEDGER.json` — executable information-carrier/channel/recovery/loss rows for route-local information-flow language.
- `ENTROPY-ACCOUNTING-LEDGER.json` — executable entropy-budget, generalized-entropy, mutual-information, and entropy-inequality rows.
- `NO-GO-COMPLIANCE-LEDGER.json` — executable no-cloning/no-signalling/data-processing/entropy-inequality compliance rows.

## Documentation spine

### `docs/00-meta`
- Charter and archive-control surfaces: `charter.md`, `archive-policy.md`, `canonical-homes.md`, `trajectory-map.md`, `llm-runbook.md`, `router-topology-and-scope-map.md`, `ROUTER-TOPOLOGY.json`.
- Support surfaces: `bibliography.md`, `id-conventions.md`, `head-semantics-and-citation-policy.md`, `ref-id-retirement-ledger.md`, `session-working-queue.md`.

### `docs/10-method`
- Method and compression surfaces: `method-overview.md`, `salience-first-research-method.md`, `cross-scale-bridge-rules.md`, `claim-ladder-and-promotion-rules.md`, `compression-and-deduping-protocol.md`, `router-economy-and-demotion-rules.md`, `source-admission-and-eviction-sieve.md`, `candidate-identifiability-state-machine.md`, `identifiability-theory-import-map.md`, `negative-control-discipline.md`, `record-denominator-and-route-ledger-schema.md`, `public-record-carrier-and-acquisition-protocol.md`, `claim-route-binding-and-authority-propagation.md`, `nonmonotonic-defeat-and-rollback-propagation.md`, `evidence-severity-and-severe-test-discipline.md`, `evidence-unit-and-credit-accounting.md`, `independence-and-double-counting-control.md`, `validity-domain-and-transportability-discipline.md`, `extrapolation-fence-and-domain-shift-control.md`, `causal-mechanism-and-intervention-discipline.md`, `counterfactual-robustness-and-mechanism-transfer.md`, `residual-deficiency-scorecard.md`, `duality-and-underdetermination-adjudication.md`, `idealization-and-approximation-error-discipline.md`, `limit-interchange-and-singular-limit-control.md`, `regularization-renormalization-matching-discipline.md`, and `scheme-dependence-and-rg-invariant-observable-control.md`, plus `information-flow-entropy-no-go-discipline.md` and `no-go-theorem-and-information-recovery-stop-rule.md`.

### `docs/20-constitution`
- Core registries: `claim-registry.md`, `open-question-registry.md`, `invariant-registry.md`, `move-registry.md`, plus `operational-record-language.md` as the neutral public-record vocabulary surface.

### `docs/30-program`
- Program state: `research-frontiers.md`, `workstreams.md`, `bridge-experiments.md`, `identifiability-worked-example-battery.md`, `executable-route-ledger.md`, `empirical-delta-roadmap.md`, and `route-state-summary.generated.md`, plus `decision-experiment-ledger.md`, `decision-experiment-summary.generated.md`, `public-record-carrier-ledger.md`, `acquisition-protocol-ledger.md`, `claim-route-binding-ledger.md`, `record-replay-harness.md`, `epistemic-defeater-ledger.md`, `authority-dependency-graph.md`, `rollback-propagation-ledger.md`, `evidence-severity-ledger.md`, `evidence-unit-ledger.md`, `independence-assumption-ledger.md`, `credit-allocation-ledger.md`, `evidence-credit-summary.generated.md`, `validity-transport-summary.generated.md`, `causal-mechanism-ledger.md`, `intervention-protocol-ledger.md`, `counterfactual-robustness-ledger.md`, `causal-mechanism-summary.generated.md`, `defeat-rollback-summary.generated.md`, `record-carrier-and-acquisition-summary.generated.md`, `idealization-ledger.md`, `approximation-error-ledger.md`, `limit-interchange-ledger.md`, `idealization-limit-summary.generated.md`, `regularization-scheme-ledger.md`, `renormalization-flow-ledger.md`, `matching-condition-ledger.md`, and `renormalization-matching-summary.generated.md`, plus `information-flow-ledger.md`, `entropy-accounting-ledger.md`, `no-go-compliance-ledger.md`, and `information-entropy-summary.generated.md`.

### `docs/40-model`
- Core model routers: the current-head control router, the cross-family pressure router, `spine.md`, the empirical-contact burden router, the broad ToE credit router, the completion-bid credit router family, the witness-router family, the current-family readout router, the family-B and family-C burden router families, the vacuum-energy burden router, the candidate-native identifiability worksheet family now semantically compressed by `docs/10-method/candidate-identifiability-state-machine.md`, the gravitational-locality / locally-covariant / QES-island / frame-transport public-record pressure surfaces, gravity witness taxonomy, lab discriminator roadmap, cosmology / primordial-tensor discriminator roadmaps, forecast-to-update discipline, cross-family scorecards, duality-versus-candidate-identity audit, causal-mechanism risk taxonomy, intervention-versus-observation audit, counterfactual-robustness crosswalk, and the burden-split / discriminator routers.
- Subordinate family, cosmological, and witness audits live alongside these routers; use `ARCHIVE_INDEX.generated.md` for the full file-level map.

### `docs/90-quarantine`
- `speculative-branches.md` — live but unpromoted bold ideas.

### `schemas`
- Executable schema surfaces for route denominators, route-state rows, negative-control rows, empirical-delta rows, decision-experiment rows, public-record-carrier rows, acquisition-protocol rows, claim-route-binding rows, epistemic-defeater rows, rollback-propagation rows, evidence-severity rows, evidence-unit rows, independence-assumption rows, credit-allocation rows, and generated authority-dependency edge rows, domain-of-validity rows, transportability rows, extrapolation-fence rows, causal-mechanism rows, intervention-protocol rows, and counterfactual-robustness rows.

## Tooling

- `tools/sync_generated_surfaces.py` — rebuild generated restart handoff surfaces and the raw filesystem index.
- `tools/restart_mirror_family.py` — shared declarative restart-mirror family spec / renderer used by sync and lint.
- `tools/lint_archive.py` — archive integrity checks.
- `tools/package_release.py` — build a zip release with a manifest-derived canonical root and predictable naming.
- `Makefile` — execution source for the compact rebuild-command subset mirrored in the restart handoffs.

## rev0262 executable additions

- `PROMOTION-GATE-LEDGER.json` — machine-readable no-compensation gate rows.
- `OBSERVED-SECTOR-RECOVERY-LEDGER.json` — high-state observed-sector recovery obligations.
- `DISCRIMINATOR-FORECAST-LEDGER.json` — future artifact semantics for route updates.
- `docs/30-program/promotion-and-recovery-summary.generated.md` — generated summary of the new ledgers.
- `docs/40-model/single-graviton-statistics-discriminator-roadmap.md` — route home for the single-graviton / graviton-statistics corridor.

## rev0263 executable additions

- `PUBLIC-RECORD-CARRIER-LEDGER.json` — machine-readable publicness / custody / replay / challenge carrier rows.
- `ACQUISITION-PROTOCOL-LEDGER.json` — machine-readable acquisition, calibration, nuisance, replay, fresh-host, and failure-effect rows.
- `CLAIM-ROUTE-BINDING-LEDGER.json` — machine-readable claim-language propagation and rollback rows.
- `docs/30-program/record-carrier-and-acquisition-summary.generated.md` — generated summary of carrier/protocol/binding coverage.


## rev0264 executable additions

- `EPISTEMIC-DEFEATER-LEDGER.json` — machine-readable undercutting / rebutting / custody / replay / quotient / model-misspecification / subsystem defeat rows.
- `ROLLBACK-PROPAGATION-LEDGER.json` — machine-readable triggered rollback floors, public-notice wording, repair conditions, and no-silent-repromotion rules.
- `EVIDENCE-SEVERITY-LEDGER.json` — machine-readable severe-test rows for route-local positive evidence.
- `AUTHORITY-DEPENDENCY-GRAPH.json` — generated support/attack graph used to trace authority propagation and loss.
- `docs/30-program/defeat-rollback-summary.generated.md` — generated summary of defeater, rollback, severity, and dependency coverage.


## rev0265 executable additions

- `EVIDENCE-UNIT-LEDGER.json` — machine-readable support packets used for route-local credit accounting.
- `INDEPENDENCE-ASSUMPTION-LEDGER.json` — machine-readable independence/correlation assumptions for aggregating evidence units.
- `CREDIT-ALLOCATION-LEDGER.json` — machine-readable no-double-counting and no-compensation rules per route.
- `docs/30-program/evidence-credit-summary.generated.md` — generated summary of evidence units, shared-support clusters, independence assumptions, and credit rows.


## rev0266 executable additions

- `CONTRAST-CLASS-LEDGER.json` — live rival sets, null/decoy families, quotient policies, and contrast-completeness status for route-local support claims.
- `LIKELIHOOD-UPDATE-LEDGER.json` — route-local update objects, outcome classes, nuisance/model-class controls, and maximum authority effects.
- `PRIOR-SENSITIVITY-LEDGER.json` — prior, nuisance, model-class, and scoring stress tests that cap update language.
- `docs/30-program/contrast-update-summary.generated.md` — generated summary of contrast/update/prior coverage.
- `docs/10-method/contrast-class-and-update-denominator.md` and `docs/10-method/prior-sensitivity-and-likelihood-update-discipline.md` — method owners for OQ-0063.

- Measurement/systematics control: `MEASUREMENT-MODEL-LEDGER.json`, `SYSTEMATIC-UNCERTAINTY-LEDGER.json`, `CALIBRATION-TRACEABILITY-LEDGER.json`, and `docs/30-program/measurement-systematics-summary.generated.md`.

## rev0268 executable additions

- `DOMAIN-OF-VALIDITY-LEDGER.json` — machine-readable source/target validity domain, preserved-invariant, boundary-condition, and exclusion rows.
- `TRANSPORTABILITY-LEDGER.json` — machine-readable source-to-target support transfer rows with shift variables and stress tests.
- `EXTRAPOLATION-FENCE-LEDGER.json` — machine-readable forbidden-inference and escalation-condition rows.
- `docs/30-program/validity-transport-summary.generated.md` — generated summary of validity/transport/fence coverage.


## rev0270 executable additions

- `CAUSAL-MECHANISM-LEDGER.json` — machine-readable causal-question, proposed-structure, mechanism-class, excluded-decoy, failure-mode, and maximum-authority rows.
- `INTERVENTION-PROTOCOL-LEDGER.json` — machine-readable intervention, perturbation, formal-variation, simulation-ablation, natural-experiment, observational, and custody-only status rows.
- `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json` — machine-readable alternative-world / model-intervention / invariance / robustness / rollback rows.
- `docs/30-program/causal-mechanism-summary.generated.md` — generated summary of causal-mechanism, intervention-protocol, and counterfactual-robustness coverage.
- `docs/10-method/causal-mechanism-and-intervention-discipline.md` and `docs/10-method/counterfactual-robustness-and-mechanism-transfer.md` — method owners for `OQ-0066`.


## rev0270 selection/multiplicity/reporting-bias layer

This revision adds `SELECTION-FUNCTION-LEDGER.json`, `MULTIPLICITY-CONTROL-LEDGER.json`, and `REPORTING-BIAS-LEDGER.json` so selected-positive, look-elsewhere, surprise, discovery, anomaly, benchmark-win, and file-drawer-insensitive language is blocked unless the route declares its search denominator and maximum authority effect. No route is promoted to `S4` or `S5`.


### Semantic / ontology / language-permission controls

- `SEMANTIC-TERM-LEDGER.json`
- `ONTOLOGY-COMMITMENT-LEDGER.json`
- `CLAIM-LANGUAGE-PERMISSION-LEDGER.json`
- `docs/10-method/semantic-binding-and-term-stability-discipline.md`
- `docs/10-method/ontology-commitment-and-claim-language-permission.md`
- `docs/30-program/semantic-binding-summary.generated.md`
- `docs/40-model/semantic-drift-and-equivocation-risk-taxonomy.md`
- `docs/40-model/ontology-identity-versus-structural-equivalence-audit.md`

- Computational evidence controls: `docs/10-method/computational-reproducibility-and-artifact-replay.md`, `docs/10-method/numerical-stability-and-solver-tolerance-discipline.md`, `docs/10-method/software-supply-chain-and-provenance-discipline.md`, and `docs/30-program/computational-reproducibility-summary.generated.md`.

- Formal proof controls: `PROOF-OBLIGATION-LEDGER.json`, `ASSUMPTION-DISCHARGE-LEDGER.json`, `FORMALIZATION-COVERAGE-LEDGER.json`, `docs/10-method/formal-proof-obligation-and-assumption-discharge.md`, `docs/10-method/formalization-coverage-and-kernel-trust.md`, and `docs/30-program/formal-proof-summary.generated.md`.


## Rev0274 computational artifact control

This revision adds `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json`, `NUMERICAL-STABILITY-LEDGER.json`, and `SOFTWARE-SUPPLY-CHAIN-LEDGER.json` so runnable code, containers, workflow replay, solver output, generated summaries, dependency locks, software citation, and supply-chain polish cannot be laundered into route promotion or candidate-native closure.


## Rev0275 formal proof control

This revision adds `PROOF-OBLIGATION-LEDGER.json`, `ASSUMPTION-DISCHARGE-LEDGER.json`, and `FORMALIZATION-COVERAGE-LEDGER.json` so theorem, derivation, no-go, uniqueness, proof assistant, proof certificate, axiom-boundary, mechanized-formalization, and assumption-discharge language cannot be laundered into route promotion or candidate-native closure.


## Rev0276 idealization / approximation / limit control

This revision adds `IDEALIZATION-LEDGER.json`, `APPROXIMATION-ERROR-LEDGER.json`, and `LIMIT-INTERCHANGE-LEDGER.json` so exact-in-the-model, asymptotic, continuum, large-N, semiclassical, thermodynamic, regulator-removal, zero-noise, and deidealized-support language cannot be laundered into route promotion or candidate-native closure.


## rev0278 gauge / constraint / observable quotient addition

This revision adds `GAUGE-SYMMETRY-LEDGER.json`, `CONSTRAINT-CLOSURE-LEDGER.json`, `OBSERVABLE-QUOTIENT-LEDGER.json`, and `docs/30-program/gauge-constraint-summary.generated.md`. These surfaces block promotion from gauge-fixed representatives, unclosed constraint algebras, anomaly-contaminated quantization, BRST-exact or pure-gauge artifacts, unreduced coordinates, and metadata wrappers. No route is promoted.


## rev0279 regularization / renormalization / matching addition

This revision adds `REGULARIZATION-SCHEME-LEDGER.json`, `RENORMALIZATION-FLOW-LEDGER.json`, `MATCHING-CONDITION-LEDGER.json`, and `docs/30-program/renormalization-matching-summary.generated.md`. These surfaces block promotion from regulator-specific calculations, scheme-dependent couplings, RG-trajectory-local fixed points, running parameters, threshold matches, EFT matches, naturalness stories, counterterm choices, and metadata wrappers. No route is promoted.


## rev0280 composition / interface / global-consistency addition

- `COMPOSITION-LAW-LEDGER.json`
- `INTERFACE-COMPATIBILITY-LEDGER.json`
- `GLOBAL-CONSISTENCY-LEDGER.json`
- `docs/30-program/composition-consistency-summary.generated.md`
- `docs/10-method/composition-interface-global-consistency-discipline.md`
- `docs/10-method/local-to-global-gluing-and-obstruction-control.md`
- `docs/40-model/composition-gluing-risk-taxonomy.md`
- `docs/40-model/local-success-versus-global-theory-audit.md`

## rev0286 note

rev0286 adds executable measure/ensemble/typicality controls (`OQ-0084`) and a binding-control-ledger coverage audit so probability, ensemble-average, naturalness, anthropic, observer-weighted, and prediction language cannot bypass route denominators.

## rev0286 subsystem/algebra controls

- `ALGEBRAIC-LOCALITY-LEDGER.json`, `SUBSYSTEM-FACTORIZATION-LEDGER.json`, `EDGE-MODE-CENTER-LEDGER.json` — executable OQ-0083 subsystem/algebra/edge-center controls.
- `docs/30-program/subsystem-algebra-summary.generated.md` — generated mirror.
- `docs/30-program/ledger-family-surface-audit.generated.md` — generated registry/ledger/schema/summary audit.

- Black-hole-sector controls: `docs/10-method/black-hole-horizon-thermodynamics-discipline.md`, `docs/10-method/black-hole-sector-recovery-stop-rule.md`, and generated `docs/30-program/black-hole-sector-summary.generated.md`.

rev0292 adds classical-GR recovery controls and row-count parity auditing: see `docs/30-program/classical-gr-recovery-summary.generated.md` and `docs/30-program/ledger-row-count-parity-audit.generated.md`.

## rev0293 route-support additions

- `STATE-PREPARATION-LEDGER.json`, `DETECTOR-RESPONSE-LEDGER.json`, and `DECOHERENCE-POINTER-LEDGER.json` add executable quantum-record denominator controls under `OQ-0091`.
- `docs/30-program/schema-envelope-audit.generated.md` audits registered ledger-family schema/envelope coverage.

## rev0294 asymptotic / IR / scattering controls

rev0294 adds `OQ-0092` plus `ASYMPTOTIC-STATE-LEDGER.json`, `INFRARED-DRESSING-LEDGER.json`, and `SCATTERING-OBSERVABLE-LEDGER.json`. S-matrix, IR-finite, soft-theorem, memory, BMS-charge, inclusive-rate, finite-time scattering, and asymptotic-completeness language now requires route-local rows and remains non-promotional. The revision also adds a candidate-route schema field coverage audit.

## rev0295 discretization / finite-volume / continuum controls

rev0295 adds `OQ-0093` plus `DISCRETIZATION-REGIME-LEDGER.json`, `FINITE-VOLUME-SCALING-LEDGER.json`, and `CONTINUUM-EXTRAPOLATION-LEDGER.json`. Lattice, Regge/simplicial, triangulation, Monte Carlo, benchmark-discretization, finite-volume, finite-size scaling, thermodynamic-limit, continuum-extrapolation, and nonperturbative-definition language now requires route-local rows and remains non-promotional. The revision also adds a generated ledger row-id uniqueness audit.

## rev0296 correlator / operator / bootstrap controls

rev0296 adds `OQ-0094` plus `CORRELATION-FUNCTION-LEDGER.json`, `OPERATOR-INSERTION-LEDGER.json`, and `BOOTSTRAP-DATA-LEDGER.json`. Correlator, n-point, generating-functional, operator-dictionary, OPE, conformal-block, crossing, bootstrap-island, CFT-data, and bulk-boundary-correlator language now requires route-local rows and remains non-promotional. The revision also adds a generated claim-route binding schema-field audit.

## rev0298 routing note

Hilbert-space, representation-map, and spectral-reconstruction controls live in `HILBERT-SPACE-LEDGER.json`, `REPRESENTATION-MAP-LEDGER.json`, `SPECTRAL-RECONSTRUCTION-LEDGER.json`, and `docs/30-program/hilbert-representation-spectrum-summary.generated.md`. The registered-ledger schema audit lives at `docs/30-program/registered-ledger-schema-property-audit.generated.md`.
