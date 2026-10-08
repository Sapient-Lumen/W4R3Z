# TimeSync changelog

## rev0132 — 2026-06-17 23:59 America/New_York

- Corrected multi-source adjudication freshness so `freshness.max_staleness_ms` is the maximum admitted input value, not the minimum.
- Carried input `source_diversity_posture` summaries into multi-source output so same-root/common-mode evidence is not upgraded by interval overlap.
- Added executable expectations for freshness, dependency class, and common-mode risk in `tests/multisource-adjudication.yaml`.
- Added generated example `examples/evaluator/multisource-p1-stale-freshnessmax-commonmode-fallback.json` and semantic vector `TV-132-001`.
- Added `evaluator/MULTISOURCE-ADJUDICATOR-REV0132.md` and `AUDIT-2026.06.17-rev0132.md`.

## rev0131 — 2026-06-17 23:41 America/New_York

- Added `tools/multisource_adjudicator.py` to combine already-assessed local states for one current-use decision.
- Added `tests/multisource-adjudication.yaml` with overlap/intersection, weak-lane/no-upgrade, and disjoint/fail-closed cases.
- Added generated example `examples/evaluator/multisource-p1-overlap-intersection-satisfied.json` and semantic vector `TV-131-001`.
- Integrated the multi-source adjudicator self-test into archive validation.
- Documented that cross-adapter agreement is not evidence of independent roots, cryptographic verification, named UTC realization, leap-smear discovery, or PTP interoperability.

## rev0130 — 2026-06-17 23:00 America/New_York

This revision continues FT-0121 by adding shared NTP-family bound arithmetic and an executable chrony-vs-ntpq equivalence harness.

### Added

- `tools/ntp_bound.py` for exact age, conservative root-bound arithmetic, negative-root-delay clamping, holdover growth, and interval endpoint generation.
- `tools/adapter_equivalence.py` and `tests/adapter-equivalence.yaml`.
- paired chrony/ntpq equivalent-state fixtures under `examples/chrony/` and `examples/ntpq/`.
- generated example `examples/evaluator/cross-adapter-p1-equivalent-state.json`.
- semantic vector `TV-130-001`.
- `evaluator/NTP-ADAPTER-EQUIVALENCE-REV0130.md`.

### Changed

- primary chrony evaluation, independent chrony observation evaluation, and ntpq evaluation now use the shared bound engine.
- validation now fails if equivalent chrony and ntpq evidence produces divergent interval endpoints, source posture, applicability, actionability, or P1 conformance.

### Not done

- No live chronyd/ntpd capture, NTS verification, symmetric-key MAC verification, named UTC realization, leap-smear discovery, or PTP comparison is claimed.

## rev0129 — 2026-06-17 22:59 America/New_York

This revision continues FT-0121 by adding a second, non-chrony operational-state replay adapter for ntpq.

### Added

- `tools/ntpq_adapter.py` for `ntpq -c rv` plus `ntpq -pn` replay text.
- `examples/ntpq/` fixtures for normal, leap-alarm, high-distance, and missing-field paths.
- `tests/ntpq-adapter-golden.yaml` and semantic vector `TV-129-001`.
- `tests/rfc9249-ntpq-observation-crosswalk.yaml`.
- `evaluator/NTPQ-REFERENCE-EVALUATOR-REV0129.md`.

### Changed

- `tools/rfc9249_crosswalk.py` now validates both chrony and ntpq crosswalks.
- `tools/validate_archive.py` now runs ntpq adapter self-tests.
- `evaluator/p1-chrony-policy.json` now carries explicit adapter-family policy IDs.

### Not done

- No live ntpd/NTPsec host capture, NTS verification, named UTC realization, leap-smear discovery, or PTP comparison is claimed.

## rev0128 — 2026-06-17 22:22 America/New_York

This revision continues FT-0121 by adding chrony authentication-report capture and no-overclaim evaluator guards.

### Added

- `chronyc authdata -a` and `chronyc -n ntpdata` capture roles.
- `authentication_summary` in chrony observations.
- `authentication_posture` extension hook for local assessed states.
- `CHRONY-P1-AUTH-REPORTED-NO-OVERCLAIM` and semantic vector `TV-128-001`.
- `evaluator/CHRONY-AUTHPOSTURE-REV0128.md`.

### Changed

- The primary and independent chrony evaluators now surface reported authentication without using it for profile strengthening.
- The RFC 9249 crosswalk now marks authentication telemetry as adapter-local and forbidden for core promotion.

### Not done

- TimeSync still does not verify NTS, symmetric-key MACs, TLS identity, cookies, AEAD tags, or packet transcripts.

## rev0127 — 2026-06-17 21:47 America/New_York

This revision continues FT-0121 by hardening the exact capture instant used to age replayed chrony evidence.

### Added

- `effective_tracking_collected_at(...)` in `tools/chrony_capture.py`
- `tests/fixtures/chrony/capture-delayed-tracking.json`
- `CHRONY-P1-CAPTURE-TRACKING-INSTANT-AGE-GUARD`
- `examples/evaluator/chrony-p1-capture-instant-ageguard-satisfied.json`
- semantic vector `TV-127-001`
- `evaluator/CHRONY-CAPTURE-INSTANT-AGEGUARD-REV0127.md`
- `archive/REV0126-TO-REV0127-MIGRATION-MAP.md`

### Tightened

- replay `collected_at` for command transcripts now comes from the conservative tracking command start, not the collector's final wall time
- capture context now retains both `effective_collected_at` and `collector_collected_at`
- delayed diagnostic commands can no longer make a tracking observation look younger or narrow the interval

### Character of the revision

- capture-age-conservative
- executable boundary regression
- no new registry surface
- small refactor with interval-safety payoff

This revision continues FT-0121 by hardening the chrony live-capture pathway and completing the tracking/sources/sourcestats evidence surface without expanding the TimeState core.

### Added

- fake-live subprocess harness in `tools/chrony_capture.py --self-test`
- required `chronyc -n sourcestats` capture role
- `examples/chrony/sourcestats-normal.txt`
- `examples/chrony/observation-sourcestats-normal.json`
- `examples/evaluator/chrony-p1-sourcestats-captured-satisfied.json`
- `CHRONY-P1-SOURCESTATS-DIAGNOSTIC-CAPTURED` golden case
- `TV-126-001` semantic vector
- `evaluator/CHRONY-LIVE-HARNESS-SOURCESTATS-REV0126.md`
- `archive/REV0125-TO-REV0126-MIGRATION-MAP.md`

### Tightened

- retained capture envelopes now include `sourcestats` alongside version, tracking, and sources
- sourcestats estimator fields are crosswalked as adapter-local/gap evidence, not core TimeState fields
- generated chrony examples and capture fixture carry rev0126 receipt-derived identity

### Character of the revision

- live-glue-tested
- estimator-diagnostics-captured
- core-preserving
- risk-cut over registry expansion

# Changelog

## rev0125 — policyacceptance-boundaryrefactor-riskcut — 2026-06-17

- Added `evaluator/p1-chrony-policy.json`, a machine-readable P1 chrony lane table for satisfied, coarse-logging fallback, display fallback, and diagnostic-only decisions.
- Added `tools/chrony_policy.py` to validate/apply that policy and refactored both chrony evaluator paths to load it instead of carrying duplicated threshold literals.
- Added `tests/profile-decision-acceptance.yaml` and `tools/profile_decision_acceptance.py` for executable exact-boundary and one-nanosecond-after-boundary acceptance cases.
- Added generated example `chrony-p1-after-display-limit-unsatisfied.json` plus semantic vector `TV-125-001`; the suite now has 367 semantic vectors.
- Added `evaluator/CHRONY-P1-POLICY-DECISION-REV0125.md`, `AUDIT-2026.06.17-rev0125.md`, and rev0125 migration/refactor notes while keeping FT-0121 open for live-host capture, NTS verification, named UTC traceability, leap-smear discovery, and non-chrony comparison.

## rev0124 — independentcompare-displayfallback-rfcguard — 2026-06-17

- Added `tools/chrony_observation_eval.py`, an independent evaluator over typed `chrony_observation` JSON that does not import the primary adapter and compares every successful chrony golden case.
- Added `CHRONY-P1-DISPLAY-HOLDOVER-FALLBACK`, generated example `chrony-p1-display-holdover-fallback.json`, and semantic vector `TV-124-001`; the suite now has 366 semantic vectors.
- Added `tests/rfc9249-chrony-observation-crosswalk.yaml` and `tools/rfc9249_crosswalk.py` to keep chrony-specific observation fields out of the six-field core until another adapter proof justifies promotion.
- Made generated chrony policy references and capture-version strings derive from `REVISION-RECEIPT.json` rather than hard-coded release literals.
- Added `evaluator/CHRONY-INDEPENDENT-EVALUATOR-REV0124.md`, `evaluator/RFC9249-CROSSWALK-REV0124.md`, `AUDIT-2026.06.17-rev0124.md`, and rev0124 migration/refactor notes while keeping FT-0121 open for live-host exercise, NTS verification, named UTC traceability, leap-smear discovery, and PTP comparison.

## rev0123 — captureanchor-negdelay-evalhardening — 2026-06-17

- Added `tools/chrony_capture.py` for validated `chronyc -v`, `chronyc -n tracking`, and `chronyc -n sources` command transcripts with wall-clock and monotonic brackets.
- Added `examples/chrony/capture-normal.json` and `tools/chrony_adapter.py --capture`; `--live` now routes through the capture envelope instead of raw command text.
- Hardened the conservative bound so negative root delay contributes zero rather than shrinking the interval.
- Added `examples/chrony/tracking-negative-root-delay.txt`, golden case `CHRONY-P1-NEGATIVE-ROOT-DELAY-CONSERVATIVE`, generated example `chrony-p1-negative-root-delay-conservative.json`, and semantic vector `TV-123-001`; the suite now has 365 semantic vectors.
- Regenerated chrony-derived examples and explanation output with the rev0123 policy reference and formula basis.
- Added `evaluator/CHRONY-CAPTURE-EVALUATOR-REV0123.md`, `AUDIT-2026.06.17-rev0123.md`, and rev0123 migration/refactor notes while keeping FT-0121 open for live-host exercise, RFC 9249 comparison, NTS verification, and independent evaluator comparison.

## rev0122 — chronyadapter-referenceeval-riskcut — 2026-06-17

- Added `tools/chrony_adapter.py`, an executable chrony replay parser and P1 reference evaluator that emits a typed observation, conservative TimeState, profile assessment, and machine-readable explanation.
- Added sanitized `chronyc tracking`/`chronyc sources` fixtures for normal, stale, unsynchronised, leap-insert, high-distance, and missing-field cases.
- Added `tests/chrony-adapter-golden.yaml` and wired the chrony adapter self-test into `tools/validate_archive.py`.
- Added generated chrony-derived local-assessed-state examples and semantic vectors `TV-122-001` and `TV-122-002`; the suite now has 364 semantic vectors.
- Added `evaluator/CHRONY-REFERENCE-EVALUATOR-REV0122.md`, `evaluator/chrony-p1-general-explanation.json`, and rev0122 audit/migration notes.
- Kept FT-0121 open: rev0122 proves replayed chrony-to-P1 evaluation, not live capture, NTS verification, named UTC traceability, PTP, or cross-vendor interoperability.

## rev0121 — missioncompass-exacttime-releaseintegrity — 2026-06-17

- Re-centered the project on time-use admission control and documented the missing real adapter/reference evaluator in `MISSION-COMPASS-2026.06.17-rev0121.md`.
- Replaced microsecond-truncating `datetime.fromisoformat` comparisons with exact RFC 3339 fractional arithmetic; leap-second arithmetic now fails closed pending an explicit policy.
- Added `TV-N343`, `DF-0121-001`, and `examples/negative/local-assessment-submicrosecond-interval-inverted-invalid.json`.
- Made `REVISION-RECEIPT.json` the source of release identity and added `tools/release_integrity.py`.
- Added manifest v2 and `tools/build_release.py` for deterministic member ordering, timestamps, and permissions.
- Removed 31 generated `.pyc` files and stopped excluding generated caches from manifest/accountability checks.
- Closed FT-0090 and opened FT-0121 around one real timing capture, parser, evaluator, explanation, and failure corpus.
- Clarified that the 124 YAML acceptance records are documentary scenarios while 362 semantic vectors are executed assertions.

## rev0120 — challengereceipt-portability-refactor — 2026-06-13

- Added `tools/authorized_verifier_result_semantics.py` for non-temporal authorized-verifier challenge/result consistency.
- Closed mutation survivors where result-bearing records could be relabelled as bare challenges, matched results could carry non-matched disclosure rows, salt/preimage receipts could be rebound or reinterpreted, not-portable boundaries could advertise replay, and disclosure rows could point away from the attached receipt digest.
- Added seven derivation-checked negative fixtures and semantic vectors `TV-N336` through `TV-N342`.
- Extended mutation-survivor audit probes from 22 to 29.
- Added `AUDIT-2026.06.13-rev0120.md`, `archive/REV0119-TO-REV0120-MIGRATION-MAP.md`, and `archive/REV0120-AUDIT-CHALLENGE-RECEIPT-PORTABILITY-REFACTOR.md`.

## rev0119 — currentclaim-mutator-refactor — 2026-06-13

- Tightened satisfied evidence-summary minimum coverage so `assessment.validity_horizon` must remain `current_at_assessment` when it supports a satisfied minimum-summary claim.
- Rejected `profile_conformance: unsatisfied` when policy acceptance or validity-horizon state still claims actionable or conditional current use.
- Rejected `policy_acceptance.status: accepted` with conditional actionability; conditional use must remain `accepted_with_conditions`.
- Rejected non-fallback profile assessments that still carry `evaluation_summary.fallback_mapping`.
- Extended `tools/mutation_survivor_audit.py` from 18 to 22 probes.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N332` through `TV-N335`; the suite now has 354 semantic vectors.
- Added `AUDIT-2026.06.13-rev0119.md`, `archive/REV0118-TO-REV0119-MIGRATION-MAP.md`, and `archive/REV0119-AUDIT-CURRENT-CLAIM-MUTATOR-REFACTOR.md`.

## rev0118 — minimumwitness-mutator-refactor — 2026-06-13

- Tightened satisfied evidence-summary minimum coverage: matching `minimum_summary_items` by name is no longer enough when the input item is ignored, conflicting, not used, stale, non-current, or forbidden for satisfied evidence.
- Preserved unsatisfied/failed summaries that carry absent or conflicting minimum items to explain why a profile did not satisfy.
- Tightened replay witness/monitor posture so positive witness/monitor bases with `independent_threshold_met` cannot be downgraded to `not_checked`, `unknown`, or `not_used`.
- Required positive witness/monitor consistent postures to carry `split_view_signal.status: none_observed`.
- Extended `tools/mutation_survivor_audit.py` from 14 to 18 probes.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N328` through `TV-N331`; the suite now has 350 semantic vectors.
- Added `AUDIT-2026.06.13-rev0118.md`, `archive/REV0117-TO-REV0118-MIGRATION-MAP.md`, and `archive/REV0118-AUDIT-EVIDENCE-WITNESS-MUTATOR-REFACTOR.md`.

## rev0117 — lifecyclemutator-rowseal-refactor — 2026-06-13

- Added `tools/aggregate_lifecycle_decision_semantics.py` and moved aggregate lifecycle decision-table row semantics plus `expected_lifecycle_decision` out of `tools/validate_archive.py`.
- Pinned required aggregate lifecycle decision-table row ids to their canonical semantic posture.
- Rejected actionable/conditional current actionability when `profile_lifecycle_state` is `superseded`, `deprecated`, `revoked`, or `unknown`.
- Rejected `none_known` lifecycle-authority compromise responses that assert a suppressing or contested `replay_visibility_effect`.
- Rejected `retained_operator_record` digest-binding rules promoted to current use.
- Extended `tools/mutation_survivor_audit.py` from 10 to 14 probes.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N324` through `TV-N327`; the suite now has 346 semantic vectors.
- Added `AUDIT-2026.06.13-rev0117.md`, `archive/REV0116-TO-REV0117-MIGRATION-MAP.md`, and `archive/REV0117-AUDIT-LIFECYCLE-MUTATOR-ROWSEAL-REFACTOR.md`.

## rev0116 — mutationaudit-driftseal-refactor — 2026-06-13

- Added `tools/mutation_survivor_audit.py` and wired 10 focused wrong-bind mutation probes into normal validation.
- Tightened current discovery result `digest_binding.digest` expectations for known returned result items.
- Added nested validation for discovery-returned `profile_compatibility_drift_decision` values.
- Rejected wrong-bind policy lifecycle-equivalence revocation digests and lifecycle-authority renewal hint digests.
- Required aggregate lifecycle rollups to carry an `aggregate_correction_authority_lifecycle_summary` digest binding.
- Required scope-composition decision-matrix temporal observations to match `matrix_digest`.
- Added six derivation-checked negative fixtures and semantic vectors `TV-N318` through `TV-N323`; the suite now has 342 semantic vectors.
- Added `AUDIT-2026.06.13-rev0116.md`, `archive/REV0115-TO-REV0116-MIGRATION-MAP.md`, and `archive/REV0116-AUDIT-MUTATION-SURVIVOR-AUDIT-REFACTOR.md`.

## rev0115 — cloudtainer-mutation-survivor-triage — 2026-06-13

- Added `tools/replay_digest_semantics.py`, `tools/aggregate_correction_digest_semantics.py`, and `tools/transparency_policy_digest_semantics.py`.
- Rejected replay receipt core digest fields that bind unrelated artifact classes.
- Rejected aggregate verifier audit `integrity_binding.digest` values that do not bind `aggregate_verifier_audit_summary`.
- Rejected aggregate correction-authority digest fields that bind unrelated retained/export/profile artifacts except for the explicit compatibility-statement authorization case.
- Rejected transparency trust-policy lifecycle/revocation/drift digest fields that bind unrelated artifact classes.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N314` through `TV-N317`; the suite now has 336 semantic vectors.
- Added `AUDIT-2026.06.13-rev0115.md`, `archive/REV0114-TO-REV0115-MIGRATION-MAP.md`, and `archive/REV0115-AUDIT-CLOUDTAINER-MUTATION-SURVIVOR-TRIAGE.md`.

## rev0114 — policy-authority-digest-binding-refactor — 2026-06-13

- Added `tools/policy_authority_digest_semantics.py` and wired it into policy lifecycle-authority reference and recovery-attestation validation.
- Rejected policy lifecycle-authority anti-rollback `status_record_digest` values that do not bind `transparency_trust_policy_lifecycle_status`.
- Rejected lifecycle-authority rotation `rotation_statement_digest` values that do not bind `transparency_trust_policy_lifecycle_authority_rotation`.
- Rejected planned successor authority metadata whose `successor_authority_digest` does not bind `transparency_trust_policy_lifecycle_authority`.
- Added `examples/negative/policy-lifecycle-authority-sequence-status-wrong-bind-invalid.json`, `examples/negative/policy-lifecycle-authority-rotation-statement-wrong-bind-invalid.json`, and `examples/negative/policy-lifecycle-authority-successor-authority-wrong-bind-invalid.json`.
- Added derivations `DF-0114-001` through `DF-0114-003` and semantic vectors `TV-N311` through `TV-N313`; the suite now has 332 semantic vectors.
- Added `AUDIT-2026.06.13-rev0114.md`, `archive/REV0113-TO-REV0114-MIGRATION-MAP.md`, and `archive/REV0114-AUDIT-POLICY-AUTHORITY-DIGEST-REFACTOR.md`.

## rev0113 — scope-composition-source-binding-refactor — 2026-06-13

- Added `tools/scope_composition_semantics.py` and moved scope-composition matrix/guard semantic checks out of `tools/validate_archive.py`.
- Rejected current scope-composition surfaces whose `source_digest` binds the wrong artifact class.
- Rejected current scope-composition temporal observations whose `source_time_digest` does not match the corresponding current surface `source_digest`.
- Normalized existing scope-composition fixtures so `aggregate_lifecycle_rollup` temporal evidence cites the same lifecycle-summary digest as the composed surface.
- Added `examples/negative/scope-composition-surface-source-wrong-bind-invalid.json`, `examples/negative/scope-composition-temporal-source-mismatch-invalid.json`, and `examples/negative/scope-composition-surface-temporal-digest-mismatch-invalid.json`.
- Added semantic vectors `TV-N308` through `TV-N310` and fixture derivations `DF-0113-001` through `DF-0113-003`.
- Added `AUDIT-2026.06.13-rev0113.md`, `archive/REV0112-TO-REV0113-MIGRATION-MAP.md`, and `archive/REV0113-AUDIT-SCOPE-COMPOSITION-REFACTOR.md`.

# TimeSync changelog

## rev0112 — profile-drift-equivalence-refactor — 2026-06-13

- Added `tools/profile_drift_semantics.py` and moved profile compatibility drift matrix/decision semantics out of `tools/validate_archive.py`.
- Rejected current profile drift decisions with no digest equivalence or unknown/redacted digest relation.
- Rejected current digest-distinct drift decisions that omit `compatibility_statement_digest` binding `profile_compatibility_statement`.
- Rejected current digest-rollover-compatible decisions that omit bound prior/current profile digests or successor compatibility statement digest.
- Added three derivation-checked negative fixtures and semantic vectors `TV-N305` through `TV-N307`; the suite now has 326 semantic vectors.
- Added `AUDIT-2026.06.13-rev0112.md`, `archive/REV0111-TO-REV0112-MIGRATION-MAP.md`, and `archive/REV0112-AUDIT-PROFILE-DRIFT-REFACTOR.md`.

## rev0111 — external-receipt-binding-refactor — 2026-06-13

- Added `tools/external_receipt_semantics.py` and moved external transparency receipt boundary/digest semantics out of `tools/validate_archive.py`.
- Rejected validated external receipt references whose `statement_digest`, `checkpoint_digest`, or `receipt_digest` binds the wrong artifact class.
- Added discovery-result semantic validation for returned `external_transparency_receipt_reference` values.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N301` through `TV-N304`.
- Added `AUDIT-2026.06.13-rev0111.md`, `archive/REV0110-TO-REV0111-MIGRATION-MAP.md`, and `archive/REV0111-AUDIT-EXTERNAL-RECEIPT-REFACTOR.md`.

# Changelog

## rev0110 — aggregate-privacy-digest-refactor — 2026-06-13

- Added `tools/aggregate_privacy_semantics.py` and moved aggregate privacy controls, compromise-era suppression, and recovery-audit rollup semantics out of `tools/validate_archive.py`.
- Rejected profile-compatibility/cross-operator suppression-threshold metadata without `compatibility_statement_digest` binding `profile_compatibility_statement`.
- Rejected noisy aggregate counts whose `privacy_policy_digest` does not bind `aggregate_privacy_policy_rules`.
- Added `aggregate-threshold-compatibility-wrong-bind-invalid.json`, `aggregate-threshold-profile-basis-missing-compat-invalid.json`, and `aggregate-noise-policy-wrong-bind-invalid.json`.
- Added derivations `DF-0110-001` through `DF-0110-003` and semantic vectors `TV-N298` through `TV-N300`; the suite now has 319 semantic vectors.
- Added `AUDIT-2026.06.13-rev0110.md`, `archive/REV0109-TO-REV0110-MIGRATION-MAP.md`, and `archive/REV0110-AUDIT-AGGREGATE-PRIVACY-REFACTOR.md`.

# TimeSync changelog

## rev0109 — aggregate-lineage-cadence-refactor — 2026-06-13

- Added `tools/aggregate_lineage_semantics.py` and wired it into aggregate verifier audit summary validation.
- Moved aggregate revision-lineage boundary, status, sequence, digest, and reconciliation checks out of `tools/validate_archive.py`.
- Rejected aggregate revision lineage whose `publication_sequence` disagrees with `aggregate_privacy_controls.publication_cadence.publication_sequence`.
- Rejected immediate-predecessor correction lineage where `prior_aggregate_digest` disagrees with `publication_cadence.previous_publication_digest`.
- Rejected present `revision_chain_digest` metadata that does not bind `aggregate_publication_revision_chain`.
- Normalized existing aggregate-lineage fixtures whose immediate-predecessor prior digest and publication-cadence previous digest were inconsistent.
- Added `examples/negative/aggregate-lineage-publication-sequence-mismatch-invalid.json`, `examples/negative/aggregate-lineage-immediate-predecessor-digest-mismatch-invalid.json`, and `examples/negative/aggregate-lineage-revision-chain-wrong-bind-invalid.json`.
- Added derivations `DF-0109-001` through `DF-0109-003` and semantic vectors `TV-N295` through `TV-N297`; the suite now has 316 semantic vectors.
- Added `AUDIT-2026.06.13-rev0109.md`, `archive/REV0108-TO-REV0109-MIGRATION-MAP.md`, and `archive/REV0109-AUDIT-AGGREGATE-LINEAGE-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0108 — transport-capability-claim-refactor — 2026-06-13

- Added `tools/transport_capability_semantics.py` and wired it into transport capability validation.
- Moved capability adapter/message-type and negative-result-status checks out of `tools/validate_archive.py`.
- Rejected capability advertisements whose `supported_profiles` entries do not resolve in the profile catalog.
- Rejected capability `requestable_items` outside the TimeSync assessment/request vocabulary, including private materials such as source rosters.
- Rejected capability advertisements that claim `supported_profiles` for adapters whose catalog policy forbids profile references.
- Added `examples/negative/transport-capability-unknown-profile-invalid.json`, `examples/negative/transport-capability-unknown-request-item-invalid.json`, and `examples/negative/transport-capability-profile-ref-forbidden-adapter-invalid.json`.
- Added derivations `DF-0108-001` through `DF-0108-003` and semantic vectors `TV-N292` through `TV-N294`; the suite now has 313 semantic vectors.
- Added `AUDIT-2026.06.13-rev0108.md`, `archive/REV0107-TO-REV0108-MIGRATION-MAP.md`, and `archive/REV0108-AUDIT-TRANSPORT-CAPABILITY-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0107 — discovery-binding-current-use-refactor — 2026-06-13

- Added `tools/discovery_binding_semantics.py` and wired it into discovery-result validation.
- Moved semantic-version parsing, downgrade-proof checks, and digest-binding metadata checks out of `tools/validate_archive.py`.
- Rejected current-use discovery results that omit `digest_binding` metadata.
- Rejected disagreement between `version_negotiation.current_use_allowed` and `digest_binding.current_use_allowed`.
- Added `examples/negative/discovery-current-result-missing-digest-binding-invalid.json`, `examples/negative/discovery-current-result-digest-not-current-invalid.json`, `examples/negative/discovery-current-result-version-not-current-invalid.json`, and `examples/negative/discovery-current-result-missing-version-current-invalid.json`.
- Added derivations `DF-0107-001` through `DF-0107-004` and semantic vectors `TV-N288` through `TV-N291`; the suite now has 310 semantic vectors.
- Added `AUDIT-2026.06.13-rev0107.md`, `archive/REV0106-TO-REV0107-MIGRATION-MAP.md`, and `archive/REV0107-AUDIT-DISCOVERY-BINDING-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0106 — evidence-summary-obligation-refactor — 2026-06-13

- Added `tools/evidence_summary_semantics.py` and wired it into evaluator evidence-summary validation.
- Moved evidence-class catalog and evidence-summary obligation/non-provenance checks out of `tools/validate_archive.py`.
- Rejected met evidence-summary obligations that rely on non-present evidence items.
- Rejected met evidence-summary obligations that rely on `ignored`, `conflicting`, or `withdrawn` evidence values.
- Rejected met evidence-summary obligations that rely on `not_used` evidence items or redacted evidence without a salted commitment.
- Added `examples/negative/evidence-summary-met-obligation-absent-item-invalid.json`, `examples/negative/evidence-summary-met-obligation-ignored-item-invalid.json`, and `examples/negative/evidence-summary-redacted-obligation-without-commitment-invalid.json`.
- Added derivations `DF-0106-001` through `DF-0106-003` and semantic vectors `TV-N285` through `TV-N287`; the suite now has 306 semantic vectors.
- Added `AUDIT-2026.06.13-rev0106.md`, `archive/REV0105-TO-REV0106-MIGRATION-MAP.md`, and `archive/REV0106-AUDIT-EVIDENCE-SUMMARY-REFACTOR.md`.

## rev0105 — profile-reference-binding-refactor — 2026-06-13

- Added `tools/profile_reference_binding.py` for signed `assessed_profile` reference coverage and artifact-time checks.
- Rejected profile-reference bindings signed after the assessment, evidence summary, or authorized-verifier challenge that relies on them.
- Rejected digest-bearing profile references whose signed binding omits `digest` from `binding.covers`.
- Added `examples/negative/local-assessment-profile-binding-after-assessment-invalid.json`, `examples/negative/local-assessment-profile-binding-missing-digest-cover-invalid.json`, and `examples/negative/authorized-verifier-profile-binding-after-issued-invalid.json`.
- Added derivations `DF-0105-001` through `DF-0105-003` and semantic vectors `TV-N282` through `TV-N284`; the suite now has 303 semantic vectors.
- Added `AUDIT-2026.06.13-rev0105.md`, `archive/REV0104-TO-REV0105-MIGRATION-MAP.md`, and `archive/REV0105-AUDIT-PROFILE-REFERENCE-BINDING-REFACTOR.md`.


## rev0104 — assessment-temporal-validity-refactor — 2026-06-13

- Added `tools/assessment_temporal.py` and wired it into local profile-assessment validation.
- Moved `check_policy_acceptance` and `check_validity_horizon` out of `tools/validate_archive.py`.
- Rejected profile assessments whose `assessment_time` is after `policy_acceptance.checked_at`.
- Rejected profile assessments whose `assessment_time` is after `validity_horizon.evaluated_at`.
- Rejected `assessment_time_binding: profile_assessment_time` horizons whose window does not cover the profile `assessment_time`.
- Added three derivation-checked local-assessment negative fixtures and semantic vectors `TV-N279` through `TV-N281`, bringing the suite to 300 semantic vectors.
- Added `AUDIT-2026.06.13-rev0104.md`, `archive/REV0103-TO-REV0104-MIGRATION-MAP.md`, and `archive/REV0104-AUDIT-ASSESSMENT-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0103 — transport-integrity-binding-refactor — 2026-06-13

- Added `tools/transport_integrity.py` and wired it into transport envelope validation.
- Rejected `signed_payload` envelope binding claims unless the integrity block uses `signed_payload` or `detached_signature` protection.
- Rejected signed-payload binding that does not cover `semantic_payload` or `semantic_payload_digest`.
- Rejected `authenticated_transport` binding that authenticates only envelope metadata rather than `semantic_payload`.
- Rejected `profile_reference`-only integrity coverage so envelope signatures cannot substitute for payload profile digest obligations.
- Added three derivation-checked transport negative fixtures and semantic vectors `TV-N276` through `TV-N278`.
- Added `AUDIT-2026.06.13-rev0103.md`, `archive/REV0102-TO-REV0103-MIGRATION-MAP.md`, and `archive/REV0103-AUDIT-TRANSPORT-INTEGRITY-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0102 — policy-equivalence-temporal-fixture-refactor — 2026-06-13

- Added `tools/policy_equivalence_temporal.py` and wired it into profile compatibility statement validation.
- Moved policy lifecycle equivalence interval/window checks out of `tools/validate_archive.py`.
- Rejected policy-equivalence `revocation_check.checked_at` and `drift_check.checked_at` values after the lifecycle-equivalence `evaluated_at` they support.
- Rejected lifecycle-equivalence `evaluated_at` values after the compatibility statement `binding.signed_at` or `expires_at`.
- Corrected `profiles/compatibility/p3-replay-transparency-policy-equivalence.json` and copied negative fixtures whose statement signature predated the policy-equivalence evidence it covered.
- Added three derivation-checked negative fixtures and semantic vectors `TV-N273` through `TV-N275`.
- Removed generated `__pycache__` bytecode from the packaged artifact to reduce cloudtainer/archive noise.
- Added `AUDIT-2026.06.13-rev0102.md`, `archive/REV0101-TO-REV0102-MIGRATION-MAP.md`, and `archive/REV0102-AUDIT-POLICY-EQUIVALENCE-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0101 — replay-transparency-temporal-derivation-refactor — 2026-06-13

- Added `tools/replay_transparency_temporal.py` and wired it into replay-transparency audit validation.
- Moved anchor freshness arithmetic, checkpoint-consistency timing, and witness-observation timing out of `tools/validate_archive.py`.
- Rejected `replay_event.replayed_at` values after `anchor_evaluation.evaluated_at`.
- Rejected `transparency_anchor.logged_at` values after `anchor_evaluation.evaluated_at`.
- Rejected `anchor_freshness.basis_time` values that do not match `transparency_anchor.logged_at` when `basis: logged_at` is declared.
- Added three derivation-checked replay-transparency negative fixtures and semantic vectors `TV-N270` through `TV-N272`.
- Added `AUDIT-2026.06.13-rev0101.md`, `archive/REV0100-TO-REV0101-MIGRATION-MAP.md`, and `archive/REV0101-AUDIT-REPLAY-TRANSPARENCY-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0100 — authorized-verifier-temporal-fixture-refactor — 2026-06-13

- Added `tools/authorized_verifier_temporal.py` and wired it into authorized-verifier challenge validation.
- Moved challenge issue/expiry, response, portable-result state, revocation-check, and replay-window timestamp checks out of `tools/validate_archive.py`.
- Removed the authorized-verifier replay check from the general-purpose `tools/temporal_coherence.py` helper so that helper returns to shared timestamp primitives plus discovery/scope/replay-transparency uses.
- Rejected `challenge_result.responded_at` values before challenge `issued_at`.
- Rejected `portable_result_state.revocation_check.checked_at` values before the challenge response they qualify.
- Normalized replay-positive and copied replay-transparency fixtures that still had pre-response revocation checks.
- Added two derivation-checked negative fixtures and semantic vectors `TV-N268` and `TV-N269`.
- Added `AUDIT-2026.06.13-rev0100.md`, `archive/REV0099-TO-REV0100-MIGRATION-MAP.md`, and `archive/REV0100-AUDIT-AUTHORIZED-VERIFIER-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0099 — profile-compatibility-temporal-derivation-refactor — 2026-06-13

- Added `tools/profile_compatibility_temporal.py` and wired it into profile compatibility statement validation.
- Rejected compatibility statements whose `binding.signed_at` is after `expires_at`.
- Rejected compatibility statements whose `issued_at` is after `binding.signed_at`.
- Rejected compatibility statements whose `compatibility_drift.evaluated_at` is after the statement signature or expiry.
- Added two profile-compatibility negative fixtures and semantic vectors `TV-N266` and `TV-N267`.
- Added derivations `DF-0099-001` through `DF-0099-003`, including a derivation check for the older challenge-portability weaker-policy fixture.
- Added `AUDIT-2026.06.13-rev0099.md`, `archive/REV0098-TO-REV0099-MIGRATION-MAP.md`, and `archive/REV0099-AUDIT-PROFILE-COMPATIBILITY-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0098 — aggregate-artifact-temporal-derivation-refactor — 2026-06-12

- Added `tools/aggregate_temporal.py` and wired it into replay-transparency aggregate verifier audit validation.
- Rejected aggregate verifier audit summaries whose `issued_at` is later than `aggregate_record_created_at`.
- Moved aggregate period interval ordering from the monolithic validator into the aggregate temporal helper.
- Tightened `tools/fixture_derivations.py` to reject duplicate derivation IDs and duplicate rendered-output targets.
- Added one derivation-checked negative fixture and semantic vector `TV-N265`.
- Added `AUDIT-2026.06.12-rev0098.md`, `archive/REV0097-TO-REV0098-MIGRATION-MAP.md`, and `archive/REV0098-AUDIT-AGGREGATE-TEMPORAL-FIXTURE-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

## rev0097 — policy-lifecycle-temporal-fixture-refactor — 2026-06-12

- Added `tools/policy_lifecycle_temporal.py` and wired it into lifecycle-authority and recovery-attestation validation.
- Rejected anti-rollback freeze status whose `basis_time` is after `anti_rollback_sequence.checked_at`.
- Rejected lifecycle-authority and recovery-attestation events that occur after the trust-policy lifecycle status or current replay evaluation that relies on them.
- Rejected contained-compromise recovery attestations whose issuance, verification, containment, or portability check occurs after the compromise response `checked_at`.
- Added three derivation-checked negative fixtures and vectors `TV-N262` through `TV-N264`.
- Added `AUDIT-2026.06.12-rev0097.md`, `archive/REV0096-TO-REV0097-MIGRATION-MAP.md`, and `archive/REV0097-AUDIT-POLICY-LIFECYCLE-TEMPORAL-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-family conversion.

# Changelog

## rev0096 — transport-envelope-temporal-semantic-runner-refactor — 2026-06-12

- Added `tools/transport_envelope_temporal.py` to reject payload semantic event timestamps that occur after an envelope `sent_at`.
- Added three transport-envelope negative fixtures and semantic vectors for discovery freshness after send, local assessment after send, and retained export after send.
- Added those transport negatives to `tests/fixture-derivations.yaml` so rendered fixtures are reproducible from positive bases plus explicit mutations.
- Added `tools/semantic_vectors.py` and moved semantic-vector ID checking, fixture coverage, and vector pass/fail execution out of `tools/validate_archive.py`.
- Added `AUDIT-2026.06.12-rev0096.md`, `archive/REV0095-TO-REV0096-MIGRATION-MAP.md`, and `archive/REV0096-AUDIT-TRANSPORT-SEMANTIC-RUNNER-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and fixture-volume reduction, with a bias toward executable checks over registry growth.

## rev0095 — retained-export-fixture-derivation-refactor — 2026-06-12

- Added `tools/retained_export_temporal.py` for retained-export artifact-time and current-policy recheck semantics.
- Rejected retained exports whose profile assessment time, policy acceptance check, validity-horizon evaluation, or evidence-summary assessment time occurs after `export_context.exported_at`.
- Rejected `purpose: current_policy_recheck` unless `export_context.current_policy_checked` is true.
- Rejected current-policy recheck exports that claim actionable/conditional assessment state outside the assessment validity horizon at export time.
- Added `tools/fixture_derivations.py` and `tests/fixture-derivations.yaml` to verify selected bulky negative fixtures against positive bases plus explicit patch operations.
- Added three retained-export negative fixtures and semantic vectors TV-N256 through TV-N258.
- Added `AUDIT-2026.06.12-rev0095.md`, `archive/REV0094-TO-REV0095-MIGRATION-MAP.md`, and `archive/REV0095-AUDIT-RETAINED-EXPORT-FIXTURE-REFACTOR.md`.
- Kept FT-0090 open for further validator decomposition and gradual fixture-family conversion.

## rev0094 — discovery-freshness-replay-window-refactor — 2026-06-12

- Added discovery-result `freshness` metadata and semantic checks requiring it for current-use discovery interpretation.
- Required current discovery freshness basis timestamps to be no later than local observation time, within `max_age_seconds`, and equal to the returned object timestamp when one exists.
- Added authorized-verifier replay-window checks for revocation status timing, replay-before-response, replay-before-status-evaluation, and replay-without-usable-status.
- Corrected the standalone authorized-verifier positive fixture so portable-result status evaluation occurs after the revocation check it relies on.
- Added seven negative vectors for stale/missing/mismatched discovery freshness and invalid authorized-verifier replay timing/state.
- Extended `tools/temporal_coherence.py` with discovery/replay helper functions and self-tests instead of adding a new registry.
- Added `AUDIT-2026.06.12-rev0094.md`, `archive/REV0093-TO-REV0094-MIGRATION-MAP.md`, and `archive/REV0094-AUDIT-DISCOVERY-REPLAY-REFACTOR.md`.
- Kept FT-0090 open for validator decomposition and fixture-volume reduction.

## rev0092 — jcs-digest-hardening-audit-refactor — 2026-06-12

- Added `tools/jcs.py`, a dedicated TimeSync JCS/RFC 8785 subset canonicalizer with self-tests.
- Replaced profile-rule digest computation with canonical bytes from `tools/jcs.py` rather than Python sort-keys serialization.
- Made JSON loading reject duplicate object member names, non-I-JSON constants, and lone-surrogate strings before schema validation.
- Corrected digest-policy object-member ordering from ambiguous codepoint order to RFC 8785-compatible UTF-16 code-unit order.
- Required current TimeSync-owned digest surfaces to use the safe-integer/I-JSON subset and reject unsafe numbers fail-closed.
- Added negative vectors for wrong member-order policy, unsafe digest-bound profile-rule number, and duplicate JSON member names.
- Added `AUDIT-2026.06.12-rev0092.md`, `archive/REV0091-TO-REV0092-MIGRATION-MAP.md`, and `archive/REV0092-AUDIT-JCS-DIGEST-REFACTOR.md`.
- Left FT-0090 open for temporal-coherence generalization and further validator decomposition.

## rev0091 — format-temporal-window-cloudtainer-triage — 2026-06-12

- Enabled JSON Schema `format: date-time` assertion with `jsonschema.FormatChecker()`.
- Added semantic vector ID uniqueness checking and corrected duplicate `TV-111` / `TV-112` entries.
- Hardened scope-composition temporal coherence so current inputs observed after guard evaluation fail closed.
- Hardened scope-composition temporal coherence so current inputs exceeding their declared `max_age_seconds` fail closed.
- Added negative vectors for malformed date-time, post-evaluation temporal input reuse, and exceeded temporal max age.
- Added deep-read/cloudtainer triage notes for validator modularization, RFC 8785/JCS canonicalization, temporal helper reuse, and fixture deduplication.
- Left FT-0090 open for the broader digest and temporal-coherence generalization work.

## rev0090 — temporal-coherence-guard-refactor — 2026-06-09

- Added required `temporal_coherence` to `scope-composition-guard` and advanced the guard schema to `guard_version: rev0090`.
- Added `tools/temporal_coherence.py` to factor evaluation-window and stale-input checks out of the monolithic validator.
- Added semantic validation for guard-evaluation windows, required timestamp roles, stale/unchecked current inputs, and non-provenance temporal boundaries.
- Extended the mixed-layer attack corpus with `stale-composed-input-cannot-remain-current`.
- Added negative vectors for stale current-input reuse and invalid evaluation-window ordering.
- Closed FT-0089 and opened FT-0090 for generalizing temporal-coherence helpers beyond scope composition.

## rev0089 — schema-meta-orphan-coverage-audit — 2026-06-09

- Added schema-document meta-validation for every `schema/*.json` file.
- Removed invalid empty `allOf: []` arrays from four schema documents.
- Added schema `$id` consistency checking and normalized the recovery-attestation schema id domain.
- Made JSON Schema validation fail closed when `jsonschema` is unavailable.
- Added semantic-vector coverage enforcement for every `examples/**/*.json` fixture.
- Reclassified the historical rev0086 semantic-version-negotiation fixture as an explicit `fail_schema` vector.
- Tightened schema-failure expected-error substring matching.
- Ignored generated Python bytecode caches in manifest validation.
- Added `AUDIT-2026.06.09.md` and opened FT-0089 for temporal-coherence composition proofs.


## rev0088 — 2026-05-26 03:00 America/New_York

Closed FT-0087 by adding a mixed-layer scope-composition guard, an executable composition attack corpus, and replay-transparency validator scope refactoring.

- Added `schema/scope-composition-guard.schema.json` and `schema/scope-composition-decision-matrix.schema.json`.
- Added `tests/mixed-layer-scope-composition.yaml`.
- Added positive guard and discovery-returned guard fixtures.
- Added negative fixtures for profile-assessment upgrade, actionability upgrade, downgrade/lifecycle bypass, lifecycle/profile-drift bypass, and missing mixed-layer surfaces.
- Added `scope_composition_guard_summary` as non-satisfying profile-obligation evidence and regenerated profile normative digests.
- Refactored validator checks through `check_scope_composition_guard(...)` and `check_scope_composition_decision_matrix(...)`.
- Opened FT-0088 for temporal coherence, artifact-time monotonicity, and mixed-scope stale-state proofs.

## rev0087 — 2026-05-26 02:00 America/New_York

Closed FT-0086 by adding executable profile-compatibility drift decisions, downgrade-proof metadata for discovery negotiation, and rendered-profile consistency checks.

- Added `schema/profile-compatibility-drift-matrix.schema.json`, `schema/profile-compatibility-drift-decision.schema.json`, and `tests/profile-compatibility-drift-matrix.yaml`.
- Added optional `compatibility_drift` to profile compatibility statements.
- Added drift classes for equivalent, stricter-or-equal, weaker, incomparable, unknown, digest-rollover-compatible, and digest-rollover-without-equivalence cases.
- Added discovery downgrade proof metadata under `version_negotiation`.
- Added `downgrade_proof_policy` to semantic-version negotiation.
- Added positive examples for drift decisions, compatibility statements, semantic-version negotiation, and discovery downgrade proof.
- Added negative fixtures for weaker/unknown current drift, unproven digest rollover, missing drift on named portability workflows, missing downgrade proof, weaker downgrade semantics, and unsafe downgrade policy.
- Audited rendered profile Markdown files and added validator checks to keep forbidden evidence-class lists synchronized with the normative profile catalog.
- Opened FT-0087 for mixed-layer portability attack corpus and replay/lifecycle/profile drift composition tests.

## rev0086 — 2026-05-26 01:00 America/New_York

Closed FT-0085 by adding portable canonicalization, semantic-version negotiation, and byte-envelope digest-binding rules for digest-bound TimeSync surfaces and discovery-returned objects.

- Added `schema/digest-binding-policy.schema.json` and `schema/semantic-version-negotiation.schema.json`.
- Added `spec/54-portable-canonicalization-and-byte-envelope-bindings.md` and `spec/55-discovery-semantic-version-negotiation.md`.
- Extended discovery request/result metadata with `semantic_version`, `schema_uri`, `version_negotiation`, and `digest_binding`.
- Required current-use TimeSync-owned digest surfaces to use `json_canonicalization_scheme_rfc8785`; legacy Python sort-keys binding is now historical-only.
- Added byte-envelope binding checks requiring authenticated payload type, verification before payload parse, no JSON-canonicalization dependency for signature validation, and no raw payload byte export by default.
- Added semantic-version negotiation checks so unsupported newer result versions cannot be accepted as current exact semantics.
- Added `portable_digest_binding_policy_summary` as a non-satisfying evidence class and regenerated profile normative digests.
- Refactored validator discovery checks into reusable digest-binding and semantic-version helper functions.
- Added positive vectors TV-194 through TV-197 and negative vectors TV-N216 through TV-N221.
- Opened FT-0086 for cross-profile compatibility drift, downgrade proofs, and portability threat tests.

## rev0085 — 2026-05-26 00:00 America/New_York

Closed FT-0084 by adding executable aggregate correction-authority lifecycle decisions, lifecycle rollups, emergency-withdrawal resynchronization summaries, lifecycle portability aggregation, timestamp-role semantics, external transparency receipt references, disclosure-control references, PNT risk posture, and UTC transition hooks.

- Added `schema/aggregate-lifecycle-decision-table.schema.json` and `tests/aggregate-lifecycle-decision-table.yaml`.
- Required `decision_table_digest` and `current_interpretation_decision` in correction-authority lifecycle references.
- Added decision-table semantic checks for active, pending-rotation, expired, revoked, emergency-withdrawal, contested, and unknown/redacted lifecycle states.
- Added `aggregate_correction_authority_lifecycle_rollup` with lifecycle population, decision population, contestation-resolution, emergency-resynchronization, and portability aggregation surfaces.
- Added `aggregate_record_created_at` and tightened ordering for authorization, lifecycle, revocation, and notification observations.
- Added external transparency receipt references and statistical disclosure-control references as digest-bound aggregate-only hooks.
- Added PNT risk posture and UTC transition planning hooks outside the TimeState core.
- Added specs 48 through 53, positive fixtures TV-191 through TV-193, negative fixtures TV-N207 through TV-N215, acceptance tests, traceability rows, and revision-reference linting.
- Opened FT-0085 for portable canonicalization, version negotiation, and byte-envelope binding rules across digest-bound surfaces.

## rev0084 — 2026-05-23 06:30 America/New_York

Closed FT-0083 by adding correction-authority lifecycle, revocation, emergency-withdrawal, and contestation boundaries to aggregate correction-authority references.

- Added required `aggregate_summary.aggregate_revision_lineage.correction_authority_reference.authority_lifecycle`.
- Added `schema/aggregate-correction-authority-lifecycle.schema.json`.
- Added `spec/47-aggregate-correction-authority-lifecycle.md`.
- Added lifecycle posture for active, pending-rotation, expired, revoked, emergency-withdrawal, contested, and unknown correction authorities.
- Added `aggregate_correction_authority_lifecycle_summary` as a non-satisfying evidence class and regenerated profile digests.
- Added discovery validation and validator fixtures for lifecycle-bearing correction-authority references.
- Opened FT-0084 for contestation-resolution rollups, emergency-withdrawal notification resynchronization, and lifecycle portability aggregation.

## rev0083 — 2026-05-23 05:45 America/New_York

Closed FT-0082 by adding aggregate correction-authority references, notification cadence, and compatible-operator correction-chain portability boundaries.

- Added required `aggregate_summary.aggregate_revision_lineage.correction_authority_reference`.
- Added `schema/aggregate-correction-authority-reference.schema.json`.
- Added `spec/46-aggregate-correction-authority-and-notification.md`.
- Added `aggregate_correction_authority_summary` as a non-satisfying evidence class.
- Added positive portable correction-chain and discovery-returned correction-authority fixtures.
- Added negative fixtures for stale correction notification, unauthorized authority, authority roster/key leakage, missing compatibility digest, weaker authority equivalence, malformed discovery returns, and evidence-class misuse.
- Regenerated profile normative digests because the forbidden evidence-class set changed.
- Audited/refactored aggregate validator authority checks into `check_aggregate_correction_authority_reference(...)`, keeping relationship checks in `check_aggregate_revision_lineage(...)`.
- Opened FT-0083 for correction-authority lifecycle, revocation, emergency withdrawal, and contestation boundaries.

## rev0082 — 2026-05-23 05:00 America/New_York

Closed FT-0081 by adding aggregate publication correction, withdrawal, supersession, and longitudinal reconciliation lineage.

- Added required `aggregate_summary.aggregate_revision_lineage` to aggregate verifier audit summaries.
- Added `aggregate_revision_lineage_summary` as a non-satisfying evidence class.
- Added `spec/45-aggregate-publication-correction-and-lineage.md`.
- Added positive corrected, reconciled, and discovery-returned aggregate lineage fixtures.
- Added negative fixtures for missing prior digest, suppressed-delta leakage, current-visibility upgrade, non-monotonic lineage, adjacent-window reconciliation, malformed discovery returns, and evidence-class misuse.
- Regenerated profile normative digests because the forbidden evidence-class set changed.
- Audited/refactored aggregate validator lineage checks through `check_aggregate_revision_lineage(...)` and `digest_binds(...)`.
- Opened FT-0082 for correction-authority references, notification cadence, and correction-chain portability boundaries.

## rev0081 — 2026-05-23 04:15 America/New_York

Closed FT-0080 by adding aggregate publication cadence, suppression-threshold equivalence, and statistical-noise posture to detached aggregate verifier audit summaries.

Added:

- required `aggregate_summary.aggregate_privacy_controls`
- `aggregate_privacy_control_summary` as a non-satisfying evidence class
- `spec/44-aggregate-publication-cadence-and-privacy-controls.md`
- positive policy-bound noisy-count aggregate fixture
- negative fixtures for exact adjacent-window differencing, weaker threshold equivalence, unbound noisy counts, noise-based de-suppression, privacy-control upgrade attempts, discovery malformation, and evidence-class misuse
- `archive/FT-0080-CLOSURE.md`
- `archive/REV0080-TO-REV0081-MIGRATION-MAP.md`
- `archive/REV0080-AUDIT-VALIDATOR-REFACTOR.md`

Hardened:

- repeated aggregate publications must declare publication sequence and differencing-risk posture
- publication sequence after the first requires a previous aggregate-publication digest
- compatible-operator aggregate cohorts require digest-bound equivalent-or-stricter suppression-threshold posture
- noisy aggregate counts require a digest-bound external privacy policy
- statistical noise cannot be used to de-suppress groups below declared minimum group size
- privacy controls cannot update profile assessment, actionability, individual replay visibility, or TimeSync provenance

Refactored:

- shared validator helpers now cover repeated aggregate non-leakage / non-upgrade boundary checks and aggregate count normalization

Opened FT-0081 for aggregate-publication correction, withdrawal, supersession, and longitudinal reconciliation boundaries.

## rev0080 — 2026-05-23 03:30 America/New_York

Closed FT-0079 by adding aggregate compromise-era suppression and recovery-audit rollup semantics to detached aggregate verifier audit summaries.

Added:

- optional `aggregate_summary.compromise_era_suppression`
- optional `aggregate_summary.recovery_audit_rollup`
- `recovery_audit_rollup_summary` evidence class, non-satisfying for profile obligations
- `spec/43-aggregate-compromise-era-suppression-and-recovery-audit-rollup.md`
- positive aggregate suppression / recovery rollup / discovery fixtures
- negative fixtures for small-group leakage, exact incident-window leakage, current-visibility promotion, incident-forensics leakage, missing cross-operator compatibility digest, and evidence-class misuse

Hardened:

- compromise-era subsets have their own suppression threshold independent of total replay count
- recovery rollup subsets have their own suppression threshold independent of total replay count
- aggregate rollups cannot become individual current replay visibility
- aggregate rollups cannot export incident IDs, exact windows, affected authority identities, verifier identities, affected challenge-result IDs, recovery-attestation IDs, forensics, legal details, compatibility-statement material, or external provenance

Opened FT-0080 for aggregate rollup publication cadence, suppression-threshold equivalence, and statistical-noise / privacy-budget boundaries.

## rev0079 — 2026-05-23 02:45 America/New_York

Closed FT-0078 by adding digest-bound lifecycle-authority recovery attestation references and historical/contested replay-visibility semantics.

Added:

- `schema/policy-lifecycle-authority-recovery-attestation.schema.json`
- `spec/42-lifecycle-authority-recovery-attestation.md`
- `lifecycle_authority_recovery_attestation` evidence class
- recovered-current, historical-only, contested, and unknown recovery-attestation replay visibility effects
- positive/negative fixtures for recovery-attestation validation and discovery

Hardened:

- contained compromise used for current replay visibility now requires a current recovery attestation
- historical-only or contested recovery posture cannot be promoted to current replay visibility
- cross-operator recovery-attestation portability requires a compatibility-statement digest
- recovery-attestation references cannot export incident forensics, key material, authority rosters, delegation chains, legal-authority details, or external provenance

Opened FT-0079 for aggregate compromise-era suppression and recovery-audit rollup semantics.

## rev0078 — 2026-05-23 02:00 America/New_York

This revision closes FT-0077 by adding a compact lifecycle-authority rotation, delegation, and compromise-response boundary for transparency trust-policy references.

### Added
- `spec/41-lifecycle-authority-rotation-delegation-compromise.md`
- required `rotation_delegation_status` on `policy_lifecycle_authority_reference`
- required `authority_rotation_equivalence` on replay-transparency policy-lifecycle compatibility statements
- `lifecycle_authority_rotation_summary` evidence class, non-satisfying for profile obligations
- positive planned-rotation authority and replay-transparency fixtures
- negative fixtures for unresolved compromise, missing delegated authority digest/scope, unknown rotation, key-material leakage, weaker cross-operator rotation equivalence, discovery malformation, and evidence-class misuse

### Tightened
- profile evidence policies now forbid lifecycle-authority rotation summaries as profile-obligation evidence
- validator now checks that rotation/delegation/compromise posture updates replay visibility only
- compatibility statements cannot use weaker or unknown authority-rotation/delegation/compromise-response equivalence for current replay visibility

### Character of the revision
- authority-lifecycle-aware
- non-provenance-preserving
- replay-visibility-only
- keeps TimeState and profile assessment closed

# Changelog

## rev0077 — 2026-05-23T01:15:00-04:00 — policy-lifecycle authority discovery and anti-rollback sequencing

### Added
- `schema/policy-lifecycle-authority-reference.schema.json`.
- Required `lifecycle_authority_reference` in `transparency_trust_policy_reference`.
- Required `sequence_equivalence` in replay-transparency policy-lifecycle compatibility statements.
- `spec/40-policy-lifecycle-authority-discovery-and-anti-rollback.md`.
- Positive fixtures for lifecycle-authority references, replay receipts, and discovery-returned trust-policy references.
- Negative fixtures for rollback, stale/frozen status, unknown authority discovery, malformed renewal hints, non-monotonic sequence, topology leakage, weaker sequence equivalence, and malformed discovery return.

### Tightened
- Current replay visibility now requires known lifecycle-authority discovery, monotonic status sequencing, no rollback, and fresh status.
- Cross-operator replay-visibility policy equivalence now includes bounded lifecycle-authority sequence equivalence.

### Boundary
- No policy repository, status endpoint, API, trust-anchor material, policy language, authority credential, transparency log, witness/monitor roster, or provenance graph is exported.

## rev0076 — 2026-05-23T00:30:00-04:00 — transparency trust-policy lifecycle

- Closed FT-0075.
- Added required `lifecycle_status` to `transparency_trust_policy_reference`.
- Added required `policy_lifecycle_equivalence` to replay-transparency policy-equivalence compatibility statements.
- Added `spec/39-transparency-trust-policy-lifecycle.md`.
- Added semantic checks for expired, revoked, unknown-drift, and rollover-without-equivalence policy references treated as current replay visibility.
- Added semantic checks for expired or drift-weakened policy-lifecycle equivalence in compatibility statements.
- Added one positive lifecycle rollover fixture and six negative lifecycle/drift fixtures.
- Opened FT-0076 for policy-lifecycle authority discovery, renewal hints, and anti-rollback sequencing.

## rev0075 — 2026-05-22T16:00:00-04:00 — transparency trust-policy equivalence boundary

- Closed FT-0074.
- Added digest-bound `transparency_trust_policy_reference`.
- Added profile compatibility workflow `replay_transparency_policy_equivalence`.
- Added `transparency_policy_equivalence` object to profile compatibility statements.
- Added non-satisfying evidence class `transparency_trust_policy_reference`.
- Added positive replay/compatibility/discovery fixtures and negative policy-reference / weaker-equivalence fixtures.
- Regenerated P1-P6 normative profile digests.
- Opened FT-0075 for transparency trust-policy lifecycle, expiry, revocation, and drift semantics.

## rev0074 — 2026-05-22T15:00:00-04:00 — witnessed checkpoint / monitor cohort boundary

### Closed

- Closed FT-0073 by defining optional summary-only witness-checkpoint and monitor-cohort posture for replay-transparency review.

### Added

- `spec/37-witnessed-checkpoint-and-monitor-cohort-boundary.md`.
- Optional `witness_cohort_evaluation` on `challenge_replay_transparency_receipt`.
- Optional `aggregate_summary.monitor_cohort_coverage` on `aggregate_verifier_audit_summary`.
- `witness_cohort_summary` evidence class with `may_satisfy_profile_obligation: false`.
- Positive witnessed receipt and monitor-cohort aggregate fixtures.
- Negative fixtures for threshold failure, disagreement-current misuse, roster leakage, aggregate small-group leakage, profile-obligation misuse, and malformed discovery-returned witness posture.
- `archive/FT-0073-CLOSURE.md` and `archive/REV0073-TO-REV0074-MIGRATION-MAP.md`.

### Tightened

- Claimed witnessed or monitor-observed consistency requires checked checkpoint consistency and independent threshold posture.
- Witness or monitor disagreement cannot be treated as current replay visibility.
- Witness/monitor rosters, identities, dependency details, proof material, logs, and gossip transcripts remain outside TimeSync.
- Every profile now forbids `witness_cohort_summary` from satisfying profile obligations.

### Preserved

- The six-field TimeState core remains unchanged.
- Replay-transparency receipts remain detached review metadata.
- Witness/monitor posture cannot update profile conformance, validity horizon, current actionability, source traceability, or TimeSync provenance.

### Opened

- FT-0074: transparency trust-policy references and cross-operator threshold-equivalence boundaries.

---

## rev0073 — 2026-05-22T14:00:00-04:00 — transparency anchor freshness / checkpoint consistency

### Closed

- Closed FT-0072 by defining a compact `anchor_evaluation` boundary for replay-transparency receipts.

### Added

- `spec/36-transparency-anchor-freshness-and-checkpoint-boundary.md`.
- `anchor_evaluation` in `schema/replay-transparency-audit.schema.json`.
- Positive replay-transparency receipt with fresh anchor, checked-consistent checkpoint status, and no observed split-view signal.
- Negative fixtures for stale-current, unchecked-current, failed-current, split-view-current, and split-view-as-provenance misuse.
- `archive/FT-0072-CLOSURE.md` and `archive/REV0072-TO-REV0073-MIGRATION-MAP.md`.

### Tightened

- `challenge_replay_transparency_receipt` records now require `anchor_evaluation`.
- `current_at_evaluation` replay visibility requires included anchor, fresh anchor, checked-consistent checkpoint status, and no conflicting transparency view observed.
- Checkpoint proof material, conflict details, external-log provenance, witness/gossip internals, salts, preimages, verifier identities, and legal-authority details remain outside TimeSync.

### Opened

- FT-0073: witnessed-checkpoint and monitor-cohort trust boundaries without witness rosters or gossip transcripts.

---

## rev0072 — 2026-05-22T13:15:00-04:00 — replay transparency / aggregate verifier audit summaries

### Closed

- Closed FT-0071 by defining detached replay-transparency receipts and aggregate verifier audit summaries for authorized-verifier challenge-result replay.

### Added

- `schema/replay-transparency-audit.schema.json`.
- `spec/35-replay-transparency-and-aggregate-verifier-audit.md`.
- `challenge_replay_transparency_receipt` and `aggregate_verifier_audit_summary` record kinds.
- `replay_transparency_receipt` evidence class with `may_satisfy_profile_obligation: false`.
- Positive replay-transparency receipt, aggregate verifier audit summary, and discovery-returned transparency fixtures.
- Negative fixtures for unanchored receipts, replay-purpose upgrades, salt/preimage export, small-group aggregate leakage, verifier identity leakage, profile-obligation misuse, and malformed discovery-returned transparency records.
- `archive/FT-0071-CLOSURE.md` and `archive/REV0071-TO-REV0072-MIGRATION-MAP.md`.

### Tightened

- Replay-transparency records must not become profile evidence, current-actionability evidence, reassessment triggers, verifier authorization proofs, transport authentication, or TimeSync provenance.
- Aggregate verifier audit summaries must suppress counts below the declared minimum group size.
- Discovery-returned replay-transparency and aggregate verifier-audit records are nested-validated.
- Every profile now forbids `replay_transparency_receipt` from satisfying profile obligations.

### Preserved

- The six-field TimeState core remains unchanged.
- Authorized verifier challenge results remain detached commitment-verification receipts.
- Salt/preimage material, verifier rosters, legal-authority details, external transparency-log semantics, and external authorization workflows stay outside ordinary TimeSync exchange.

### Opened

- FT-0072: transparency-anchor freshness, checkpoint consistency, and split-view/equivocation boundaries.

---


## rev0071 — 2026-05-22T12:00:00-04:00 — challenge-result portability/replay/revocation

### Closed

- Closed FT-0070 by defining bounded portability, replay target binding, and revocation/current-usability semantics for detached authorized-verifier challenge results.

### Added

- `spec/34-challenge-result-portability-replay-revocation.md`.
- `portability_boundary` on authorized-verifier challenge records.
- `challenge_result.portable_result_state` for challenge-result records.
- Optional `replay_context` for bounded replay review.
- `compatible_workflows` on profile compatibility statements, including `authorized_verifier_challenge_result_portability`.
- Positive replay fixture for a P3 redacted commitment challenge result.
- Positive profile compatibility workflow fixture for P3 challenge-result portability.
- Negative fixtures for revoked results, missing revocation checks, replay-use upgrade attempts, replay target/profile-digest mismatch, cross-operator portability without compatibility, and weak compatibility workflow assertions.
- `archive/FT-0070-CLOSURE.md` and `archive/REV0070-TO-REV0071-MIGRATION-MAP.md`.

### Tightened

- Portable challenge results are usable only for commitment-verification review.
- Usable portable results require a checked-not-revoked status.
- Replay must preserve the original summary id, assessment id, and assessed-profile digest.
- Cross-operator portability requires a profile compatibility statement digest.
- Profile compatibility statements that name challenge-result portability cannot weaken evidence policy.
- Challenge-result current status cannot update or reopen a profile assessment.

### Preserved

- The six-field TimeState core remains unchanged.
- Salt/preimage material stays outside ordinary TimeSync exchange and retained evidence summaries.
- Challenge results remain detached review artifacts, not profile evidence, actionability evidence, transport authentication, credential assertions, audit chains, or provenance records.

### Opened

- FT-0071: replay-transparency receipts and aggregate verifier audit summaries without verifier roster or disclosure leakage.

---

## rev0070 — 2026-05-21T05:05:00-04:00 — authorized verifier challenge boundary

### Closed

- Closed FT-0069 by adding a detached authorized verifier challenge/result record for redacted salted commitments.

### Added

- `schema/authorized-verifier-challenge.schema.json`.
- `spec/33-authorized-verifier-challenge-boundary.md`.
- `authorized_verifier_disclosure` evidence class with `may_satisfy_profile_obligation: false`.
- Positive P3 challenge-result fixture that targets a redacted traceability commitment and carries only an opaque receipt/digest.
- Negative fixtures for expired challenge results, commitment target mismatch, salt/preimage export attempts, obligation misuse, and malformed discovery-returned challenge results.
- `archive/FT-0069-CLOSURE.md` and `archive/REV0069-TO-REV0070-MIGRATION-MAP.md`.

### Tightened

- Challenge results must bind to a summary id, assessment id, assessed profile, and target commitment value.
- If a referenced evidence summary is present, the target commitment must appear in it.
- Salt/preimage material must remain in an external authorized channel and must not be exported in ordinary TimeSync summaries.
- Challenge results cannot reopen assessments or satisfy profile obligations.

### Preserved

- The six-field TimeState core remains unchanged.
- Redacted external evidence references remain item-level binding handles.
- TimeSync records challenge review boundaries but does not become a verifier credential, authorization protocol, selective-disclosure proof system, audit chain, or provenance graph.

### Opened

- FT-0070: portability, replay, and revocation semantics for challenge results.

---


## rev0069 — 2026-05-21T04:20:00-04:00 — redacted external evidence references / salted commitments

### Closed

- Closed FT-0068 by adding a narrow redacted external evidence-reference and salted-commitment surface.

### Added

- `schema/redacted-external-evidence-reference.schema.json`.
- `input_items[*].external_evidence_reference` in evaluator evidence summaries.
- `external_evidence_reference` evidence class with `may_satisfy_profile_obligation: false`.
- `summary_with_salted_commitments` evidence-summary redaction mode.
- Required guard `external_evidence_interpreted_as_provenance: false`.
- `spec/32-redacted-external-evidence-references.md`.
- `archive/FT-0068-CLOSURE.md` and `archive/REV0068-TO-REV0069-MIGRATION-MAP.md`.
- Positive P3 redacted-reference evidence summary fixture.
- Negative fixtures for unsalted redacted digests, external-reference obligation misuse, external-provenance interpretation, short salts, and malformed discovery-returned redacted references.

### Tightened

- Bare digests over redacted input groups no longer satisfy the redaction guidance; salted commitments are required when the digest would reveal a low-cardinality hidden value by enumeration.
- Pointer-only external references cannot satisfy met profile obligations.
- Opaque external handles cannot be direct URIs.
- Every profile now forbids `external_evidence_reference` from satisfying profile obligations.

### Preserved

- The six-field TimeState core remains unchanged.
- TimeSync binds to external records but does not parse, validate, or interpret external provenance.
- Salt/preimage disclosure remains outside ordinary retained summaries.

### Opened

- FT-0069: authorized verifier challenge / disclosure boundary for salts and preimages.

---

## rev0068 — 2026-05-21T03:35:00-04:00 — profile-assessment validity horizon/current actionability

### Closed

- Closed FT-0067 by adding a profile-assessment-scoped validity horizon and current-actionability surface.

### Added

- `profile_assessments[*].validity_horizon`.
- `schema/validity-horizon.schema.json`.
- `spec/31-profile-assessment-validity-horizon.md`.
- `validity_horizon_summary` evidence class.
- `archive/FT-0067-CLOSURE.md` and `archive/REV0067-TO-REV0068-MIGRATION-MAP.md`.
- Positive P2 validity-horizon fixture.
- Negative fixtures for outside-window actionability, policy/actionability mismatch, export-time freshness promotion, and malformed discovery-returned validity horizon.

### Tightened

- P2/P3/P5/P6 now make `validity_horizon` profile-default.
- P2/P3/P5/P6 evidence minimum summaries include `assessment.validity_horizon`.
- Discovery-returned `validity_horizon` values are schema and semantic checked.
- The validator rejects export time as freshness/current-actionability basis.

### Preserved

- The six-field TimeState core remains unchanged.
- Validity horizon is not a policy engine and not transport negotiation.
- Retention remains distinct from actionability.

### Opened

- FT-0068: redacted external evidence references / salted commitments for low-cardinality hidden evidence values.

---

## rev0067 — 2026-05-21T02:50:00-04:00 — source diversity and common-mode dependency posture

### Closed

- Closed FT-0066 by adding a compact profile-facing source-diversity/common-mode dependency hook.

### Added

- `spec/30-source-diversity-and-common-mode-posture.md`.
- `extension_hooks.source_diversity_posture` in `schema/extension-hooks.schema.json` and local assessed state schema embedding.
- `source_diversity_summary` evidence class.
- `examples/p5-control-action-diverse-source.json`.
- Negative fixtures for single-source/multiple-root contradiction, same-root diversity overclaim, roster leakage, and malformed discovery-returned source diversity.
- `archive/FT-0066-CLOSURE.md` and `archive/REV0066-TO-REV0067-MIGRATION-MAP.md`.

### Tightened

- P4 and P5 now require source-diversity posture as profile-default.
- P4 and P5 evidence summary minimum items include `extension_hooks.source_diversity_posture`.
- Discovery-returned `source_diversity_posture` values are schema-validated.
- The validator rejects using same-root multi-source agreement as common-mode mitigation.

### Preserved

- The six-field TimeState core remains unchanged.
- The new hook does not export source rosters, path histories, raw observations, clock algorithms, or grandmaster-election data.
- Transport adapters remain below evaluator semantics and do not negotiate source diversity.

### Opened

- FT-0067: validity horizon/current-actionability semantics for retained or replayed assessments.

---

## rev0066 — 2026-05-21T02:05:00-04:00 — timescale realization and clock-continuity posture

### Closed

- Closed FT-0065 by adding compact profile-facing hooks for named realization, leap/smear behavior, backward-step policy, and monotonicity posture.

### Added

- `spec/29-timescale-realization-and-clock-continuity.md`.
- `extension_hooks.timescale_realization` in `schema/extension-hooks.schema.json` and local assessed state schema embedding.
- `extension_hooks.clock_continuity_posture` in `schema/extension-hooks.schema.json` and local assessed state schema embedding.
- `examples/p2-coordination-smeared-continuity.json`.
- Negative fixtures for inconsistent realization scale, smear-policy mismatch, missing named realization, and malformed discovery-returned realization.
- `archive/FT-0065-CLOSURE.md` and `archive/REV0065-TO-REV0066-MIGRATION-MAP.md`.

### Tightened

- `traceability_posture.reference_anchor: utc_named_realization` now requires an actual named `timescale_realization`.
- `timescale_realization.scale` is checked against `timestate.timescale` when both are specific.
- `timescale_realization.leap_handling` and `clock_continuity_posture.smear_policy` must not contradict each other.
- Discovery-returned extension hook values are schema-validated.
- Profile obligation item names and evidence minimum item names are checked against known TimeSync item surfaces.

### Preserved

- The six-field TimeState core remains unchanged.
- The new hooks do not expose source rosters, raw timing samples, clock algorithms, or grandmaster selection.
- Transport adapters remain below evaluator semantics and do not negotiate realization or continuity policy.

### Opened

- FT-0066: source-diversity and common-mode dependency posture without exporting a source roster or provenance graph.

---


## rev0065 — 2026-05-21T01:20:00-04:00 — evidence hardening and profile compatibility statements

### Closed

- Closed FT-0064 by adding detached signed profile compatibility statements.

### Added

- `spec/27-profile-catalog-compatibility.md`.
- `spec/28-profile-digest-canonicalization.md`.
- `schema/profile-compatibility-statement.schema.json`.
- `profiles/compatibility/p3-exact-equivalent-self.json`.
- Profile compatibility negative fixtures for exact-digest mismatch, third-party alias assertion, and missing digest.
- Evidence-summary negative fixtures for missing minimum items, unauthenticated obligation satisfaction, and malformed discovery-returned summaries.
- `archive/FT-0064-CLOSURE.md` and `archive/REV0064-TO-REV0065-MIGRATION-MAP.md`.

### Tightened

- Profile assessments now carry stable `assessment_id`.
- Evidence summaries now require `summary_id`, `obligation_results`, and `conclusion_binding.assessment_id`.
- `evidence_policy.default_visibility` is now only a visibility lane; retained requirement is represented by `retention_required`.
- `minimum_summary_items` is enforced for resolved profile evidence summaries.
- Forbidden obligation-satisfaction evidence classes are derived from the evidence class catalog and include `unauthenticated_source_claim`.
- Discovery-returned `evaluator_evidence_summary` values are nested-validated.
- Profile markdown digest rendering is validator-checked against `profiles/profile-catalog.json`.
- Profile digest canonicalization is documented as a normative rule.

### Preserved

- The six-field TimeState core remains unchanged.
- Transport adapters remain below evaluator semantics.
- Compatibility statements do not create a central registry, profile distribution mechanism, or negotiation protocol.
- Evidence summaries are still not provenance graphs.

### Opened

- FT-0065: timescale realization and clock-continuity posture without expanding the TimeState core.

---


## rev0064 — 2026-05-10T19:34:00-04:00 — evaluator evidence-input summaries

### Closed

- Closed FT-0063 by adding a compact evaluator evidence-input summary.

### Added

- `spec/23-evaluator-evidence-input-interface.md`.
- `spec/24-evidence-classes-and-visibility.md`.
- `spec/25-evaluator-review-and-replay.md`.
- `spec/26-evidence-non-provenance-guardrails.md`.
- `evaluator/evidence-class-catalog.json` and human-readable catalog notes.
- `schema/evaluator-evidence-summary.schema.json`.
- `schema/evidence-class-catalog.schema.json`.
- `evidence_policy` inside profile applicability maps.
- Retained export support for `evidence_input_summaries`.
- Evidence fixtures, negative misuse fixtures, and same-TimeState/different-profile evidence examples.

### Tightened

- Profile digests now include profile evidence policy.
- Exact profile-reference digest values are checked against the current catalog when the profile resolves.
- P3 and P5 retained exports require matching evidence summaries.
- `transport_metadata_only` may be noted but cannot satisfy profile obligations.
- Evidence summaries are explicitly barred from becoming source rosters, path histories, raw observation exports, or clock algorithm exports.

### Preserved

- The six-field TimeState core remains unchanged.
- Transport adapters remain below evaluator semantics.
- Evidence summaries are not provenance graphs and do not create a negotiation protocol.

### Opened

- FT-0064: cross-operator profile catalog interoperability without central profile distribution or negotiation.

---

## rev0063 — 2026-05-10T19:07:00-04:00 — minimal transport envelopes and adapter bindings

### Closed

- Closed FT-0062 by adding a minimal transport envelope and adapter catalog.

### Added

- `spec/18-minimal-transport-envelope.md`.
- `spec/19-adapter-binding-catalog.md`.
- `spec/20-retained-export-envelope.md`.
- `spec/21-transport-security-boundaries.md`.
- `spec/22-adapter-decision-table.md`.
- `transport/adapter-catalog.json` and `transport/ADAPTER-CATALOG.md`.
- `schema/transport-envelope.schema.json`.
- `schema/transport-adapter.schema.json`.
- `schema/transport-adapter-catalog.schema.json`.
- `schema/transport-capability.schema.json`.
- `schema/retained-export.schema.json`.
- Transport envelope examples and negative fixtures.
- Validator checks for adapter membership, allowed payload types, nested envelope payload validity, and retained export constraints.

### Tightened

- Envelope timestamps and carrier sequence numbers are explicitly not TimeState freshness.
- Envelope signatures may protect transport/export carriage but do not substitute for profile-reference digests or signed profile bindings.
- Detached retention export requires a retained local assessed state and the appropriate profile-reference strength.
- Adapter bindings are allowed to describe carriage, not conformance, fallback, or clock behavior.

### Preserved

- The six-field TimeState core remains unchanged.
- Discovery remains a flat request/result item surface, not a bundle protocol.
- Profile conformance remains local/export metadata scoped by a resolvable assessed profile.

### Opened

- FT-0063: minimal evaluator evidence-input summary.

---

## rev0062 — 2026-05-10T18:52:00-04:00 — applicability maps and semantic evaluator

### Closed

- Closed FT-0061 by adding concrete profile-local applicability maps for P1-P6.

### Added

- `profiles/profile-catalog.json` and per-profile applicability maps.
- `schema/profile-catalog.schema.json` and `schema/profile-applicability-map.schema.json`.
- `schema/extension-hooks.schema.json` and conditional result accounting in discovery schema.
- `spec/13-profile-local-applicability.md`.
- `spec/14-conformance-evaluation-algorithm.md`.
- `spec/15-export-retention-checklist.md`.
- `spec/16-threat-and-misuse-model.md`.
- `spec/17-schema-and-fixture-contract.md`.
- P1-P6 examples plus negative fixtures.
- `tests/semantic-test-vectors.yaml` and `tests/TRACEABILITY-MATRIX.md`.
- Semantic validator with catalog, fallback, interval, policy, and manifest checks.

### Preserved

- The six-field TimeState core remains unchanged.
- Applicability remains profile-local; no global applicability registry was introduced.
- Historical assessment validity remains separate from current-policy acceptance.

### Opened

- FT-0062: minimal transport/adapter binding.

---

# CHANGELOG

## rev0061 — 2026-05-10 18:29 America/New_York

This revision reconstructs the archive into a layered specification and closes the rev0060 lifecycle frontier.

### Added

- `spec/` living specification, ordered by semantic layer.
- `schema/` JSON schemas for TimeState, wire claims, local assessed state, profile references, profile assessment, profile objects, request/result shape, and boundary context.
- `profiles/` profile template and P1-P6 sketches.
- `tests/acceptance-tests.yaml` distilled from the prior semantic tests.
- `examples/` schema-valid example objects.
- `archive/MIGRATION-MAP.md` and `archive/FT-0060-CLOSURE.md`.
- `tools/validate_archive.py` and `VALIDATION-REPORT.md`.

### Tightened

- The narrow TimeState core remains six fields.
- Wire claims remain thinner than local assessed state.
- Profile conformance remains scoped by `assessed_profile`.
- `fallback` must carry a non-stronger applicability boundary.
- Profile-reference strength remains boundary-tiered.
- Retained assessments now separate historical conformance from current-policy acceptance.

### Research effect

The archive now has a stable living-spec layer. Historical notes remain available, but review can proceed against the reconstructed spec, schemas, examples, and acceptance tests.

### Character of the revision

- reconstructive
- implementation-facing
- lifecycle-clarifying
- still reduction-protective

## rev0032 — 2026-03-28 09:20 America/New_York

This revision tests whether the `local_private` anchor category should split.

### Added
- `LOCAL-PRIVATE-TEST.md`

### Tightened
- `TRACEABILITY-SEMANTICS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- local clocks and holdover states vary in important ways
- but the current differences are better described by regime, holdover capability, and evidence posture than by splitting the anchor family itself
- `local_private` therefore survives as one category for now
- the reduced traceability hook now looks stable enough to begin feeding back into the greenfield track

### Character of the revision
- more conservative
- more reduction-protective
- less likely to confuse operational degradation with anchor identity

## rev0033 — 2026-03-28 09:37 America/New_York

This revision feeds the stabilized traceability hook back into the greenfield track.

### Added
- `GREENFIELD-TRACEABILITY.md`

### Tightened
- `TRACKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current mechanisms surface identity, timescale, uncertainty, and malfeasance evidence in different places
- but they still do not jointly surface a compact native traceability posture
- in the greenfield track, this changes source-admission and exported-state boundaries before it justifies anything larger
- aggregation also wants a simple non-upgrade rule for traceability posture

### Character of the revision
- cross-track
- boundary-focused
- still conservative about core growth

## rev0034 — 2026-03-28 09:56 America/New_York

This revision tests whether the greenfield traceability hook must be default-visible.

### Added
- `DEFAULT-VISIBILITY-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- P5 wants traceability-adjacent state at the live measurement boundary
- P4 wants status / quality state by default inside synchronization control paths
- P3 still often carries its strongest traceability pressure at service and audit boundaries
- the best current fit is therefore not core promotion, but a distinction between globally native and profile-default visibility

### Character of the revision
- comparison-driven
- less binary
- still reduction-protective

## rev0035 — 2026-03-28 10:14 America/New_York

This revision tests whether the archive's new middle case deserves a named tier.

### Added
- `PROFILE-DEFAULT-TIER-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- `traceability_posture` is not the only hook that is stronger than optional without being archive-core
- `sync_dimension` now shows the same profile-default pattern at some P4/P5 boundaries
- `holdover_class` and `validity_scope` still do not clearly show the same pattern
- the archive now has enough evidence to name a tiny `profile_default` tier

### Character of the revision
- architecture-light
- hook-comparative
- still resistant to core growth

## rev0036 — 2026-03-28 10:31 America/New_York

This revision tests whether `holdover_class` should join the archive's new middle tier.

### Added
- `HOLDOVER-CLASS-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- demanding profiles repeatedly require visible holdover state, degraded regime, and timing quality
- but they still do not clearly require a richer reusable `holdover_class` to be default-visible across multiple boundaries
- this keeps the new `profile_default` tier smaller and more disciplined

### Character of the revision
- negative-result-friendly
- tier-stabilizing
- more careful about state versus class

## rev0037 — 2026-03-28 10:49 America/New_York

This revision tests whether `validity_scope` should join the archive's new middle tier.

### Added
- `VALIDITY-SCOPE-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- telecom material still presses status/selection semantics more strongly than reusable locality scope
- critical-infrastructure material supports honest degraded operation and relative-versus-absolute distinction, but not yet one repeated default-visible validity hook
- P6 remains the strongest home of `validity_scope`, yet that pressure is still too concentrated for tier admission
- the new `profile_default` tier now looks stabilized with two members

### Character of the revision
- negative-result-friendly
- tier-stabilizing
- ready to return to greenfield design work

## rev0038 — 2026-03-28 11:08 America/New_York

This revision sketches the thinnest greenfield response/state split the archive can currently justify.

### Added
- `GREENFIELD-RESPONSE-SKETCH.md`

### Tightened
- `TRACKS.md`
- `TIMESTATE.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 is increasingly explicit about the wire contract while leaving client-side algorithms out of scope
- NTS separates authenticated setup from later time-synchronization packets
- Roughtime shows how a compact signed bounded-time claim can travel on the wire
- TrueTime-like systems show why local client-facing state can still be richer than the wire
- the archive therefore now has a clean reason to distinguish a thin wire claim from a richer local assessed state

### Character of the revision
- architecture-light
- greenfield-forward
- still conservative about core growth

## rev0039 — 2026-03-28 11:27 America/New_York

This revision classifies `traceability_posture` across the archive's greenfield split.

### Added
- `TRACEABILITY-SPLIT-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- P5-like synchrophasor boundaries expect traceability to UTC, time accuracy, and leap-second status in the live time-status path
- P3-like finance boundaries still lean heavily on continuous comparison to UTC(NIST), documented uncertainty, synchronization procedure, logging, and certification
- `traceability_posture` therefore does not fit cleanly as source-claim only or local-assessment only
- the archive now treats it as the first clear dual-surface member of the `profile_default` tier

### Character of the revision
- profile-comparative
- greenfield-sharpening
- still conservative about core growth

## rev0040 — 2026-03-28 11:46 America/New_York

This revision classifies `sync_dimension` across the archive's greenfield split.

### Added
- `SYNC-DIMENSION-SPLIT-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- telecom timing material distinguishes explicit frequency and time/phase profiles and defines profile choices as part of the mechanism set needed for a given application
- smart-grid timing material likewise keeps time, phase, and frequency as distinct requirement families
- `sync_dimension` therefore looks less like a private local inference and less like a raw source claim than a profile-declared semantic
- the archive's two `profile_default` hooks now have different placement patterns

### Character of the revision
- classification-focused
- reduction-friendly
- still conservative about core growth

## rev0041 — 2026-03-28 12:05 America/New_York

This revision tests whether `profile_default` hooks need a discovery/request surface.

### Added
- `PROFILE-DEFAULT-DISCOVERY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 uses extension fields for optional features and future extensibility, which supports optional native surfaces without widening the core header
- telecom timing uses explicit unicast negotiation in at least one frequency-profile setting, which shows request behavior can be real but narrow and profile-shaped
- some demanding boundaries still want default-visible status rather than negotiation
- the archive therefore now prefers a small discovery/request surface, not a broad negotiation subsystem

### Character of the revision
- interface-focused
- reduction-protective
- still resisting protocol bloat

## rev0042 — 2026-03-28 12:24 America/New_York

This revision sketches the thinnest discovery/request surface the archive can currently justify.

### Added
- `DISCOVERY-REQUEST-SKETCH.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 extension fields support optional native surfaces without enlarging the core exchange
- telecom unicast negotiation shows that explicit request behavior can be real while still narrow and profile-shaped
- Roughtime version discovery shows a lightweight compatibility surface can remain small
- the archive therefore now has enough justification for one shared exposure vocabulary plus one optional request list

### Character of the revision
- architectural
- vocabulary-tightening
- still resisting grammar bloat

## rev0043 — 2026-03-28 12:43 America/New_York

This revision sketches the smallest relay/aggregation rule family the archive can currently justify.

### Added
- `RELAY-AGGREGATION-RULES.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 requirements acknowledge intermediates that may modify timing packets without breaking protected behavior
- boundary-clock style telecom timing regenerates downstream timing from a locally recovered reference rather than merely forwarding an upstream flow
- telecom protection behavior shows downstream chains may need an explicit weaker state when stronger traceability no longer holds
- the archive therefore now has enough justification for a four-rule family: preserve, downgrade, restate, unknown

### Character of the revision
- boundary-focused
- honesty-first
- still resisting provenance sprawl

## rev0044 — 2026-03-28 13:02 America/New_York

This revision tests whether relay/restatement needs a tiny reason vocabulary.

### Added
- `REASON-VOCABULARY-TEST.md`

### Tightened
- `RELAY-AGGREGATION-RULES.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- telecom timing already carries compact failure distinctions such as lossSync, lossAnnounce, and unusable
- NTP and related timing systems use compact reason-coded status in some error/degraded cases
- Roughtime gives an explicit inconsistency / malfeasance path
- the archive therefore now has enough justification for a very small optional reason layer without moving toward a status registry or fault tree

### Character of the revision
- explanation-tightening
- still reduction-protective
- still resisting status sprawl

## rev0045 — 2026-03-28 13:18 America/New_York

This revision tests whether `unknown` needs a tiny downstream consequence rule for `applicability`.

### Added
- `UNKNOWN-CONSEQUENCE-TEST.md`

### Tightened
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- integrity and warning-oriented timing guidance do not support leaving `unknown` consequence-free
- known uncertainty / quality is repeatedly tied to downstream usability decisions
- telecom failure semantics support withdrawing stronger decisions rather than silently preserving them
- the archive therefore now gives `unknown` one narrow rule: it may not sustain a stronger hook-dependent `applicability` claim by default
- the exact fallback still remains profile-local

### Character of the revision
- consequence-clarifying
- still reduction-protective
- no policy lattice

## rev0046 — 2026-03-28 13:34 America/New_York

This revision tests where the archive's tiny optional reason layer should live.

### Added
- `REASON-PLACEMENT-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some ecosystems do carry compact direct-source reasons on the wire
- but the stronger recurring case is that reasons arise or change at boundaries during selection, failover, holdover, downgrade, and restatement
- NTPv5's narrow wire scope reinforces keeping the broader reason layer out of the minimal wire claim
- the archive therefore now treats reasons as boundary-first, local-state-readable, and only wire-admissible when a profile already has a compact source-originated status path

### Character of the revision
- placement-clarifying
- still reduction-protective
- thin-wire preserving

## rev0047 — 2026-03-28 13:52 America/New_York

This revision tests whether boundary metadata now needs a named tiny surface.

### Added
- `BOUNDARY-CONTEXT-SURFACE-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some downstream behaviors depend on retained boundary context, not only on the recomputed timing state
- protection, path-trace, synchronization-uncertain, and loop-detection style signals all push in that direction
- the archive therefore now names one tiny wrapper, `boundary_context`, rather than leaving the pattern fully implicit
- the wrapper remains deliberately minimal: `action` plus optional `reason`

### Character of the revision
- wrapper-not-subsystem
- boundary-separating
- still reduction-protective

## rev0048 — 2026-03-28 14:07 America/New_York

This revision tests whether `boundary_context` needs its own expiry rule.

### Added
- `BOUNDARY-CONTEXT-EXPIRY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- boundary explanation matters while a changed state remains in force
- but richer forwarding/convergence behavior belongs to chain-context signals outside the current wrapper
- the archive therefore now keeps `boundary_context` state-coupled instead of giving it its own timer or retention ladder
- future chain-context surfaces may still need richer lifetime semantics, but this wrapper does not earn them yet

### Character of the revision
- lifetime-conservative
- wrapper-protective
- still reduction-first

## rev0049 — 2026-03-28 14:24 America/New_York

This revision tests how visible `boundary_context` should be.

### Added
- `BOUNDARY-CONTEXT-VISIBILITY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some profiles need boundary explanation by default because downstream control behavior changes immediately
- many other consumers still mainly need current state and quality, not the explanation every time
- request/response style retrieval remains a good fit for extra chain/boundary context in thinner protocols
- the archive therefore now treats `boundary_context` as requestable by default, with profile-default export only in narrower control-path cases

### Character of the revision
- visibility-narrowing
- still reduction-protective
- profile-sensitive without being profile-heavy

## rev0050 — 2026-03-28 14:42 America/New_York

This revision tests whether `boundary_context` can reuse the archive's existing discovery/request surface.

### Added
- `DISCOVERY-REUSE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- optional chain context is already retrieved through existing request/response patterns in contemporary timing design work
- narrow signaling/negotiation surfaces are enough for extra synchronization service/context in telecom profiles
- the archive therefore now treats the remaining issue as subject-level separation, not mechanism-level duplication
- one shared discovery/request surface survives; a second channel does not earn itself

### Character of the revision
- reuse-preferring
- still channel-thin
- semantics-separated without mechanism sprawl

## rev0051 — 2026-03-28 14:58 America/New_York

This revision tests whether the shared discovery/request surface needs explicit namespaces.

### Added
- `DISCOVERY-NAMESPACE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- typed optional fields and tagged items already carry most of the needed separation in contemporary timing-related designs
- telecom signaling practice likewise does not force a second namespace hierarchy for each semantic category
- the archive therefore now keeps the shared discovery/request surface flat
- distinct item names survive the ambiguity test; explicit namespaces do not earn themselves yet

### Character of the revision
- hierarchy-resistant
- still reduction-first
- semantics-kept-by-names not machinery


## rev0052 — 2026-04-26 13:59 America/New_York

This revision tests whether profiles need named request bundles.

### Added
- `REQUEST-BUNDLE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `PROBLEM-FRAME.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current timing protocol work continues to favor typed fields, tagged items, and specific service requests at the exchange boundary
- PTP profiles can bundle choices at the profile/configuration layer without making those bundles native request aliases
- synchrophasor timing clusters traceability, accuracy, leap status, and time quality as default measurement semantics rather than as optional request shorthand
- the archive therefore keeps the shared request surface item-level and treats aliases as local conveniences that must lower to explicit item names

### Character of the revision
- alias-resistant
- item-level
- convenience-tolerant without adding a second policy layer

## rev0053 — 2026-04-26 14:10 America/New_York

This revision tests whether operator-facing aliases need their own boundary.

### Added
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current protocol work keeps optional behavior and compatibility item- or tag-level rather than operator-intention-level
- profile and management material can carry configuration/operator concerns without making them exchange subjects
- local aliases are likely useful enough to document, but only as expansion sheets outside the shared request surface
- the archive therefore adds a small alias boundary as a quarantine, not as a new semantic layer

### Character of the revision
- human-layer-aware
- alias-quarantining
- still item-level
- documentation boundary, not protocol surface

## rev0054 — 2026-04-26 14:32 America/New_York

This revision tests request lifetime for the optional item-level request list.

### Added
- `REQUEST-LIFETIME-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current NTPv5 and Roughtime patterns keep ordinary optional request content attached to concrete exchanges and item identities
- NTS shows that setup/session state can exist, but should be explicit and separated from ordinary time-packet request semantics
- PTP profile material shows that persistent or forbidden behaviors belong in explicit profile/signaling rules, not in a silently remembered request list
- the archive therefore makes the ordinary request list exchange-scoped and reserves sticky behavior for a future explicit lease/subscription surface if pressure earns it

### Character of the revision
- lifecycle-tightening
- stateless-by-default
- profile/default separated from request persistence
- sticky behavior allowed only by explicit lease



## rev0055 — 2026-04-26 15:09 America/New_York

This revision tests response result shape for explicitly requested optional items.

### Added
- `REQUEST-RESULT-SHAPE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-LIFETIME-TEST.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- NTPv5 makes absence of an expected extension meaningful in a narrow item-level way, but does not require a broad error object
- Roughtime deliberately avoids protocol error reporting for malformed or unsupported request edges, warning against universal negative signaling
- PTP profile material keeps many allowed/forbidden/default choices at profile/configuration level rather than in every timing packet
- the archive therefore adopts a negative-only item-level result envelope for explicit optional requests, while keeping silence legitimate at invalid, unauthenticated, unrequested, and non-result-capable edges

### Character of the revision
- accountability-focused
- error-taxonomy-resistant
- item-level
- keeps success implicit in returned item content


## rev0056 — 2026-04-26 17:20 America/New_York

This revision tests required/default absence consequence.

### Added
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-RESULT-SHAPE-TEST.md`
- `REQUEST-LIFETIME-TEST.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current protocol patterns distinguish well-formed exchange validity from optional extension absence and profile/configuration constraints
- PTP profile material makes required/allowed/forbidden behavior a profile contract rather than ordinary request negotiation
- signed/tagged response systems show that response satisfaction can be contract-shaped without requiring a broad error-reporting layer
- the archive therefore treats missing profile-required/default visibility as profile-nonconforming by default and locally downgrade-triggering, while still allowing weaker local use or explicit profile fallback

### Character of the revision
- profile-contract-focused
- local-downgrade-aware
- still error-taxonomy-resistant
- preserves the optional/request versus required/default boundary

## rev0057 — 2026-04-27 12:55 America/New_York

This revision tests whether profile satisfaction needs a compact local marker.

### Added
- `PROFILE-CONFORMANCE-MARKER-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- profile satisfaction is real enough that downstream consumers should not have to rediscover hidden validation logic
- current protocol patterns do not justify a universal wire error object or manifest layer
- local assessed state now carries one small marker: `profile_conformance = satisfied | fallback | unsatisfied`
- fallback is explicit and weaker than full satisfaction

### Character of the revision
- local-state-focused
- reduction-protective
- makes rev0056 operational without widening the wire surface

## rev0058 — 2026-04-27 13:32 America/New_York

This revision tests whether fallback needs a shared weakened-applicability vocabulary.

### Added
- `FALLBACK-APPLICABILITY-VOCABULARY-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- existing protocols and profiles support local/profile consequence mapping more strongly than a universal fallback label set
- Roughtime and NTPv5 both warn against widening ordinary exchanges into broad diagnostic surfaces
- PTP profile material supports profile-local required/default/fallback behavior
- application domains still need explicit downstream use boundaries, so fallback must not be bare
- the archive therefore keeps fallback in `profile_conformance` and puts the weakened use boundary in existing `applicability`

### Character of the revision
- consequence-lane-preserving
- fallback-explicit but vocabulary-resistant
- profile-local
- downstream-safety guard without a policy lattice

## rev0059 — 2026-04-27 14:47 America/New_York

This revision tests whether profile conformance needs explicit profile identity.

### Added
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `FALLBACK-APPLICABILITY-VOCABULARY-TEST.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current NTPv5 keeps protocol support and extension behavior explicit while leaving local assessment outside the core wire protocol
- NTS shows that setup/profile-like context can be explicitly established outside the later time-packet path
- Roughtime keeps message interpretation bound to compact tag/key identities without broad manifests
- RFC 9760 reinforces that profiles are real constraints/defaults, not mere labels
- the archive therefore adds `assessed_profile` as local/export scope for `profile_conformance`, while rejecting a profile manifest or negotiation layer

### Character of the revision
- profile-scope-focused
- export-boundary-aware
- manifest-resistant
- keeps the minimal wire claim small


## rev0060 — 2026-04-27 15:41 America/New_York

This revision tests how strong an explicit `assessed_profile` reference must be.

### Added
- `PROFILE-REFERENCE-GRANULARITY-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- NTPv5 uses explicit version/draft identification where ambiguity would matter, while still keeping local algorithms outside the wire protocol
- NTS shows that setup context can bind later time exchanges without repeating all parameters in every packet
- Roughtime uses compact tags, known keys, and signed delegation/evidence where stronger binding is needed
- RFC 9760 gives PTP profiles explicit identity fields, including profile name, number, version, identifier, and specifying authority
- the archive therefore uses boundary-tiered profile-reference strength: id+version, plus authority, digest, or signed binding only when the consuming boundary requires it

### Character of the revision
- reference-strength-focused
- digest-when-needed
- signed-binding-resistant by default
- keeps profile distribution separate from assessed-state export

## rev0084 — 2026-05-23 06:30 America/New_York

This revision closes FT-0083 by adding correction-authority lifecycle, revocation, emergency-withdrawal, and contestation boundaries.

### Added

- `schema/aggregate-correction-authority-lifecycle.schema.json`
- `spec/47-aggregate-correction-authority-lifecycle.md`
- `archive/FT-0083-CLOSURE.md`
- `archive/REV0083-TO-REV0084-MIGRATION-MAP.md`
- `archive/REV0083-AUDIT-CORRECTION-LIFECYCLE-REFACTOR.md`
- positive lifecycle and emergency-withdrawal aggregate fixtures
- negative revoked/expired/emergency/contested lifecycle fixtures

### Tightened

- `aggregate_correction_authority_reference` now includes required `authority_lifecycle`.
- Revoked, expired, emergency-withdrawn, contested, unknown, or unchecked correction-authority lifecycle cannot support current aggregate interpretation.
- Emergency withdrawal requires a digest-bound withdrawal record and suppresses current interpretation.
- Pending or overturned contestation requires a digest-bound contestation record and cannot support current interpretation.
- `aggregate_correction_authority_lifecycle_summary` is forbidden as profile-obligation evidence.

### Audit/refactor

- Added `check_aggregate_correction_authority_lifecycle(...)`.
- Kept lifecycle checks separate from `check_aggregate_correction_authority_reference(...)` and `check_aggregate_revision_lineage(...)`.
- Regenerated profile digests because evidence policy changed.

### Character of the revision

- lifecycle-boundary-focused
- revocation-aware
- emergency-withdrawal-safe
- contestation-resistant
- aggregate-only and non-provenance

## rev0093 — 2026-06-12 20:43 America/New_York

This revision continues FT-0090 by doing the temporal-coherence work left after rev0092's digest hardening.

### Added

- `AUDIT-2026.06.12-rev0093.md`
- `archive/REV0092-TO-REV0093-MIGRATION-MAP.md`
- `archive/REV0093-AUDIT-TEMPORAL-COHERENCE-REFACTOR.md`
- temporal helper self-tests in `tools/temporal_coherence.py`
- five negative fixtures for post-evaluation or post-publication temporal evidence

### Tightened

- Checkpoint consistency `checked_at` cannot be after anchor evaluation.
- Witness/monitor `observed_at` cannot be after anchor evaluation.
- Transparency trust-policy revocation and drift checks cannot be after lifecycle evaluation.
- Aggregate lifecycle rollup windows cannot end after aggregate artifact creation/publication.

### Audit/refactor

- `tools/validate_archive.py` now imports temporal parsing and relation helpers from `tools/temporal_coherence.py`.
- Repeated timestamp relation logic was centralized where it had immediate negative-vector payoff.
- The validator remains large; further module splitting should target replay transparency, aggregate lifecycle, and discovery only where it removes duplicated executable logic.

### Character of the revision

- temporal-backfill-resistant
- evaluation-order-aware
- artifact-publication-aware
- helper-first, not registry-first
- TimeState-core-preserving
