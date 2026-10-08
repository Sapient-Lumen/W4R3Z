# TimeSync rev0132 traceability matrix

## rev0132 executable adapter/capture traceability

| Area | Artifact | Validation |
|---|---|---|


| multi-source freshness max guard | `tools/multisource_adjudicator.py`, `tests/multisource-adjudication.yaml` | `MULTISOURCE-P1-WEAK-FALLBACK-CANNOT-UPGRADE` expects `freshness_max_staleness_ms: 3600000.0` so a stale admitted input cannot be hidden by a fresh one |
| multi-source common-mode carry-forward | `tools/multisource_adjudicator.py`, `tests/multisource-adjudication.yaml` | overlap cases expect `dependency_class: multiple_sources_same_root` and `common_mode_risk: possible_common_mode` when input states report same-root/common-mode posture |
| generated stale multi-source state | `examples/evaluator/multisource-p1-stale-freshnessmax-commonmode-fallback.json` | semantic vector `TV-132-001` |
| multi-source current-use adjudication | `tools/multisource_adjudicator.py`, `tests/multisource-adjudication.yaml` | overlap/intersection, weak-lane/no-upgrade, and disjoint/fail-closed cases are executed in validation |
| generated multi-source state | `examples/evaluator/multisource-p1-overlap-intersection-satisfied.json` | semantic vector `TV-131-001` |
| shared NTP bound arithmetic | `tools/ntp_bound.py` | self-test plus adapter/equivalence and golden suites prove exact age, root-delay clamp, rate-growth, and interval endpoints are common across NTP-family adapters |
| chrony/ntpq equivalent-state guard | `tools/adapter_equivalence.py`, `tests/adapter-equivalence.yaml`, paired fixtures under `examples/chrony/` and `examples/ntpq/` | `ADAPTER-EQUIV-CHRONY-NTPQ-P1-NORMAL` proves equivalent evidence yields identical interval, posture, applicability, actionability, and conformance |
| generated cross-adapter state | `examples/evaluator/cross-adapter-p1-equivalent-state.json` | semantic vector `TV-130-001` |
| ntpq second adapter | `tools/ntpq_adapter.py`, `examples/ntpq/rv-normal.txt`, `examples/ntpq/peers-normal.txt` | `NTPQ-P1-NORMAL-SATISFIED` and `TV-129-001` prove a non-chrony operational-state surface can generate a valid P1 TimeState |
| ntpq fail-closed cases | `examples/ntpq/rv-leap-unsync.txt`, `examples/ntpq/rv-high-distance.txt`, `examples/ntpq/rv-missing-rootdisp.txt` | `tests/ntpq-adapter-golden.yaml` rejects leap alarm, excessive root distance, and missing rootdisp |
| RFC 9249 ntpq comparison guard | `tests/rfc9249-ntpq-observation-crosswalk.yaml`, `tools/rfc9249_crosswalk.py` | ntpq observation fields are mapped/gap-classified and forbidden from core promotion |
| reported authentication no-overclaim | `tools/chrony_capture.py`, `tools/chrony_adapter.py`, `tools/chrony_observation_eval.py`, `examples/chrony/authdata-authenticated.txt`, `examples/chrony/ntpdata-authenticated.txt` | `CHRONY-P1-AUTH-REPORTED-NO-OVERCLAIM` and `TV-128-001` prove reported authentication cannot strengthen an unsafe P1 decision |
| capture replay instant age guard | `tools/chrony_capture.py`, `tests/fixtures/chrony/capture-delayed-tracking.json` | `CHRONY-P1-CAPTURE-TRACKING-INSTANT-AGE-GUARD` expects age from tracking command start and semantic vector `TV-127-001` |
| capture context split | `tools/chrony_capture.py`, `tools/chrony_adapter.py` | replay exposes `effective_collected_at` and `collector_collected_at` separately so later diagnostics cannot narrow the interval |
| fake-live chrony subprocess capture | `tools/chrony_capture.py` | `tools/chrony_capture.py --self-test` creates a temporary `chronyc`, runs the real subprocess path, and validates replay extraction |
| sourcestats command capture | `tools/chrony_capture.py`, `tests/fixtures/chrony/capture-normal.json` | capture envelope requires `chronyc -n sourcestats`; fixture duration and roles are checked |
| sourcestats parser | `tools/chrony_adapter.py`, `examples/chrony/sourcestats-normal.txt` | `CHRONY-P1-SOURCESTATS-DIAGNOSTIC-CAPTURED` expects three parsed rows and max freq skew `0.082` ppm |
| diagnostic-only sourcestats observation | `tests/fixtures/chrony/observation-sourcestats-normal.json` | observation includes `sourcestats_summary.used_for_decision=false`; P1 state is unchanged |
| generated sourcestats-captured state | `examples/evaluator/chrony-p1-sourcestats-captured-satisfied.json` | semantic vector `TV-126-001` |
| RFC 9249 comparison guard | `tests/rfc9249-chrony-observation-crosswalk.yaml`, `tools/rfc9249_crosswalk.py` | sourcestats estimator fields are classified as gaps/adapter-local and forbidden from core promotion |
| machine-readable P1 chrony policy | `evaluator/p1-chrony-policy.json`, `tools/chrony_policy.py` | policy self-test validates lane order, monotonic weaker thresholds, inclusive boundaries, and fail-closed rows |
| profile-decision boundary acceptance | `tests/profile-decision-acceptance.yaml`, `tools/profile_decision_acceptance.py` | exact and one-nanosecond-after threshold cases for security, logging, display, and diagnostic outcomes |
| independent observation evaluation | `tools/chrony_observation_eval.py` | self-test compares every successful chrony golden case against primary adapter output |
| receipt-derived runtime revision strings | `REVISION-RECEIPT.json`, `tools/chrony_adapter.py`, `tools/chrony_capture.py` | generated examples and capture fixtures carry current policy/capture revision without hard-coded tool strings |
| negative root delay hardening | `tools/chrony_adapter.py`, `examples/chrony/tracking-negative-root-delay.txt` | `CHRONY-P1-NEGATIVE-ROOT-DELAY-CONSERVATIVE`; `TV-123-001` |
| conservative interval derivation | `tools/chrony_adapter.py`, `tools/chrony_observation_eval.py` | golden bound checks; independent evaluator comparison; generated examples `TV-122-001` through `TV-127-001` |
| command collection discipline | `tools/chrony_capture.py` | rejects inverted monotonic intervals, command intervals outside collector bracket, and failed replay commands |

## retained rev0121 corrective traceability

| Area | Artifact | Validation |
|---|---|---|
| Exact submicrosecond interval ordering | `examples/negative/local-assessment-submicrosecond-interval-inverted-invalid.json` | semantic vector TV-N343; derivation DF-0121-001; exact-parser self-test |
| Receipt-derived revision identity | `REVISION-RECEIPT.json`, `tools/release_integrity.py` | release-integrity self-test and normal archive validation |
| Manifest/release-root identity | `MANIFEST.json`, `tools/build_release.py` | manifest v2 checks plus two-build byte comparison during release |
| Generated cache exclusion | `tools/release_integrity.py`, `tools/build_release.py` | physical release-tree scan and full manifest coverage |
| Mission reset toward external proof | `MISSION-COMPASS-2026.06.17-rev0121.md`, `frontier-ticket.json` | human review; FT-0121 acceptance criteria |

| Area | Artifact | Validation |
|---|---|---|
| Satisfied validity-horizon minimum item must be current | `examples/negative/evidence-summary-minimum-validity-horizon-stale-invalid.json` | semantic vector TV-N332; derivation DF-0119-001; mutation probe MP-0119-001 |
| Unsatisfied conformance cannot remain actionable | `examples/negative/local-assessment-unsatisfied-actionable-invalid.json` | semantic vector TV-N333; derivation DF-0119-002; mutation probe MP-0119-002 |
| Fallback metadata cannot survive satisfied upgrade | `examples/negative/local-assessment-fallback-upgraded-with-mapping-invalid.json` | semantic vector TV-N334; derivation DF-0119-003; mutation probe MP-0119-003 |
| Accepted policy cannot carry conditional actionability | `examples/negative/local-assessment-accepted-conditional-invalid.json` | semantic vector TV-N335; derivation DF-0119-004; mutation probe MP-0119-004 |
| Satisfied minimum item must be usable | `examples/negative/evidence-summary-minimum-profile-default-ignored-invalid.json` | semantic vector TV-N328; derivation DF-0118-001; mutation probe MP-0118-001 |
| Satisfied current minimum item must be fresh | `examples/negative/evidence-summary-minimum-policy-acceptance-stale-invalid.json` | semantic vector TV-N329; derivation DF-0118-002; mutation probe MP-0118-002 |
| Witness positive basis cannot be unchecked | `examples/negative/replay-transparency-witness-status-unchecked-invalid.json` | semantic vector TV-N330; derivation DF-0118-003; mutation probe MP-0118-003 |
| Witness consistent posture requires split-view none observed | `examples/negative/replay-transparency-witness-split-unchecked-invalid.json` | semantic vector TV-N331; derivation DF-0118-004; mutation probe MP-0118-004 |
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Transport binding-strength/protection alignment | `tools/transport_integrity.py` | helper self-test plus semantic vectors TV-N276 through TV-N278 |
| Signed payload must protect semantic payload | `examples/negative/transport-signed-payload-without-signature-invalid.json` | semantic vector TV-N276; derivation DF-0103-001 |
| Authenticated transport must cover semantic payload | `examples/negative/transport-authenticated-without-semantic-cover-invalid.json` | semantic vector TV-N277; derivation DF-0103-002 |
| Profile-reference-only integrity rejection | `examples/negative/transport-profile-reference-only-cover-invalid.json` | semantic vector TV-N278; derivation DF-0103-003 |

## retained rev0102 policy-equivalence traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Policy lifecycle equivalence temporal ordering | `tools/policy_equivalence_temporal.py` | semantic vectors TV-N273 through TV-N275 |
| Equivalence after signature rejection | `examples/negative/profile-compatibility-policy-equivalence-after-signature-invalid.json` | semantic vector TV-N273; derivation DF-0102-001 |
| Revocation after equivalence rejection | `examples/negative/profile-compatibility-policy-revocation-after-equivalence-invalid.json` | semantic vector TV-N274; derivation DF-0102-002 |
| Drift after equivalence rejection | `examples/negative/profile-compatibility-policy-drift-after-equivalence-invalid.json` | semantic vector TV-N275; derivation DF-0102-003 |

## retained rev0101 replay-transparency traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Replay transparency event/anchor/freshness timing | `tools/replay_transparency_temporal.py` | semantic vectors TV-N270 through TV-N272 |

## retained rev0100 authorized-verifier traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Authorized-verifier challenge/result/replay timing | `tools/authorized_verifier_temporal.py` | semantic vectors TV-N268 and TV-N269 |

## retained rev0099 profile-compatibility traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Profile compatibility statement timing | `tools/profile_compatibility_temporal.py` | semantic vectors TV-N266 and TV-N267 |

## retained rev0098 aggregate traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Aggregate artifact-time ordering | `tools/aggregate_temporal.py` | `check_aggregate_publication_temporal(...)`; semantic vector TV-N265 |
| Aggregate period interval extraction | `tools/aggregate_temporal.py` | helper self-test plus replay-transparency aggregate validation |
| Fixture derivation duplicate protection | `tools/fixture_derivations.py` | `validate_derivations()` rejects duplicate IDs and duplicate output paths |

## retained rev0097 policy-lifecycle traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Lifecycle authority temporal ordering | `tools/policy_lifecycle_temporal.py` | semantic vectors TV-N262 through TV-N264 |

## retained rev0096 transport and semantic-runner traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Transport envelope temporal boundary | `tools/transport_envelope_temporal.py` | semantic vectors TV-N259 through TV-N261 |
| Semantic vector execution | `tools/semantic_vectors.py` | `run_vectors(...)`; runner self-test |

## retained rev0095 retained-export and derivation traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| Retained-export artifact-time checks | `tools/retained_export_temporal.py` | semantic vectors TV-N256 through TV-N258 |
| Fixture derivation drift checks | `tools/fixture_derivations.py` and `tests/fixture-derivations.yaml` | `validate_derivations()` inside archive validation |

## retained rev0092 digest-hardening traceability

| Area | Artifact | Validation |
|---|---|---|
| Profile lifecycle actionability fails closed | `examples/negative/local-assessment-revoked-actionable-invalid.json` | semantic vector TV-N324; derivation DF-0117-001; mutation probe MP-0117-001 |
| Lifecycle-authority no-compromise effect pinned | `examples/negative/policy-lifecycle-authority-no-compromise-effect-invalid.json` | semantic vector TV-N325; derivation DF-0117-002; mutation probe MP-0117-002 |
| Aggregate lifecycle decision-table row posture pinned | `examples/negative/aggregate-lifecycle-decision-table-row-drift-invalid.json` | semantic vector TV-N326; derivation DF-0117-003; mutation probe MP-0117-003 |
| Retained operator record not current-use digest surface | `examples/negative/digest-binding-policy-retained-current-invalid.json` | semantic vector TV-N327; derivation DF-0117-004; mutation probe MP-0117-004 |
| JCS subset canonicalization | `tools/jcs.py` | `python3 tools/jcs.py`; `jcs_self_test()` inside archive validation |
| Strict JSON/I-JSON parse | `tools/jcs.py` | semantic vector TV-N243 |
| Profile-rule digest bytes | `profiles/profile-catalog.json` | `check_profile_catalog(...)` using `sha256_hexdigest(...)` |
