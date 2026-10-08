# Audit — rev0167

## Scope

The audit focused on the replicated scenario-capsule and bundle layers introduced before rev0167. The question was whether primary blind ratings, method-identifiability guesses, block seals, and unblinding order were cleanly separated enough for a recipient to evaluate Lacuna without accidentally measuring “which method was recognizable” as though it were ordinary story quality.

## Finding A167-01 — primary ratings and method recognition were not separate artifacts

**Risk.** A blind rater could score transcripts and then make method-recognition observations in prose, but the run had no typed boundary saying whether those guesses happened before or after unblinding and after which ratings were frozen.

**Repair.** Added `lacuna.scenario-masking-assessment.v1` and the run status `awaiting-masking`. A run now accepts masking assessments only after every primary rating is retained and before unblinding. The artifact binds the blind packet digest and all primary rating digests.

**Evidence.** `tests.test_scenarios` now verifies that unblinding refuses after primary rating alone, accepts a separate masking artifact, and reports method-identifiability summary only after unblinding.

## Finding A167-02 — correctness of method guesses could be joined too early

**Risk.** If guessed methods and true condition labels were joined before unblinding, a coordinator or rater could contaminate the remaining evaluation.

**Repair.** Masking artifacts record guesses, cues, confidence, familiarity, and recognition flags without correctness. Scenario report v3 computes correctness only after the report is built from the unblinded assignment.

**Evidence.** The report builder now receives both primary ratings and masking artifacts; the method-identifiability confusion table is generated only inside the unblind path.

## Finding A167-03 — bundle block seals did not bind masking evidence

**Risk.** A bundle could seal primary ratings while post-rating method guesses remained mutable or absent, weakening the public “seal before unblind” claim.

**Repair.** Bundle block-seal v3 includes masking artifact SHA-256s. The active block cannot be sealed until its child is `ready-to-unblind`, which now requires all primary ratings and all masking assessments.

**Evidence.** `tests.test_scenario_bundles` exercises the full block flow, including bundle masking templates, block seal creation, unblinding, bundle report publication, and rater-level CSV export.

## Finding A167-04 — direct child unblind could bypass the bundle parent

**Risk.** A bundle parent could later detect that a child had been prematurely unblinded, but the child operation itself was still callable once its own ratings were complete.

**Repair.** Bundle-staged children now carry a closed unblind gate in the scenario run manifest. The bundle parent opens that gate only during all-block unblinding and binds the opening to the block-seal digest. Direct child unblind now fails closed before report creation.

**Evidence.** A direct child unblind attempt before all blocks are sealed now refuses with `scenario-unblind-gate-closed`; bundle-managed unblinding opens each gate and remains idempotent after partial completion.

## Residual risks

- Method-identifiability scoring is descriptive evidence, not a causal model or rater-bias correction.
- A dishonest host can still run unrecorded model or rater calls outside Lacuna.
- A recognizable method may or may not explain primary ratings; that analysis remains external.
- The new unblind gate is a cooperative sidecar control, not cryptographic remote attestation.
- Fresh-context and provider-isolation claims remain host declarations unless independently evidenced.

## Acceptance disposition

The revision is acceptable when scenario, scenario-bundle, schema, CLI, release-surface, compile, manifest, and clean-extraction smoke checks pass; the artifact reports rev0167 / 0.167.0 consistently; and scenario schema count rises to 72 exchange schemas.
