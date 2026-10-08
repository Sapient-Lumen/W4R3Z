# TimeSync rev0132 acceptance scenarios and executable checks

`tests/acceptance-tests.yaml` contains 124 human-readable given/when/then scenarios. They remain acceptance scenarios: the validator checks their YAML structure, required fields, and unique IDs, but does not execute the prose as a full BDD suite.

Executable assurance comes from:

- `tools/ntp_bound.py` for shared exact NTP-family bound arithmetic.
- `tools/adapter_equivalence.py` for paired chrony-vs-ntpq equivalence.
- `tools/multisource_adjudicator.py` for current-use composition of multiple local assessed states.
- `tools/ntpq_adapter.py --self-test` for ntpq readvar/peers replay acceptance and fail-closed cases.
- `tools/chrony_adapter.py --self-test` and `tools/chrony_observation_eval.py --self-test` for primary/independent chrony comparison.
- 374 records in `tests/semantic-test-vectors.yaml`.
- 89 base-plus-patch checks in `tests/fixture-derivations.yaml`.
- 29 focused probes in `tools/mutation_survivor_audit.py`.
- 11 chrony adapter/evaluator golden cases in `tests/chrony-adapter-golden.yaml`.
- capture-envelope and fake-live subprocess self-tests in `tools/chrony_capture.py`.
- 7 exact profile-decision boundary cases in `tests/profile-decision-acceptance.yaml`.
- RFC 9249 crosswalk guard checks in `tools/rfc9249_crosswalk.py`.
- helper self-tests wired into `tools/validate_archive.py`.

Required commands:

```text
PYTHONDONTWRITEBYTECODE=1 python3 tools/validate_archive.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/ntp_bound.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/adapter_equivalence.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/multisource_adjudicator.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_policy.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/profile_decision_acceptance.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_capture.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_adapter.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/chrony_observation_eval.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/ntpq_adapter.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 tools/rfc9249_crosswalk.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/lint_revision_references.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/mutation_survivor_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/fixture_derivations.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/release_integrity.py
```

rev0132 acceptance focus:

```text
tools/multisource_adjudicator.py consumes local-assessed-state outputs, intersects overlapping intervals, and fails closed with a union interval when inputs cannot be safely combined.
MULTISOURCE-P1-CHRONY-NTPQ-OVERLAP-INTERSECTS checks the positive overlap/intersection path and common-mode carry-forward.
MULTISOURCE-P1-WEAK-FALLBACK-CANNOT-UPGRADE proves one fallback input prevents a satisfied output and that combined freshness uses the stalest admitted input.
MULTISOURCE-P1-DISJOINT-ASSESSED-INSTANTS-FAIL-CLOSED proves non-overlapping intervals are rejected as diagnostic_local_only.
TV-131-001 validates the generated local-assessed-state output for the multi-source overlap case.
TV-132-001 validates the stale-input freshness-max/common-mode fallback case.
```

retained rev0131 acceptance focus:

```text
tools/multisource_adjudicator.py prevents cherry-picking by intersecting overlapping intervals, carrying forward the weakest lane, and failing closed with a union interval when inputs cannot be safely combined.
```

retained rev0130 acceptance focus:

```text
tools/ntp_bound.py owns exact age, root-delay clamp, holdover growth, and interval endpoint arithmetic.
tools/adapter_equivalence.py proves equivalent chrony and ntpq evidence yields the same TimeState/P1 boundary result.
ADAPTER-EQUIV-CHRONY-NTPQ-P1-NORMAL checks the same interval, posture, applicability, actionability, and conformance through two independent parsers.
TV-130-001 validates the generated local-assessed-state output for the cross-adapter equivalent case.
```

rev0127 acceptance focus:

```text
tools/chrony_capture.py validates chronyc command/version/tracking/sources/sourcestats transcripts with wall-clock and monotonic brackets.
tools/chrony_adapter.py accepts capture envelopes through --capture, routes --live through the same capture path, and parses sourcestats as diagnostic-only observation evidence.
tools/chrony_observation_eval.py recomputes P1 decisions from chrony_observation JSON without importing the primary adapter.
tools/chrony_policy.py validates the P1 lane table loaded from evaluator/p1-chrony-policy.json.
tools/profile_decision_acceptance.py executes exact and one-nanosecond-after threshold crossings.
tools/rfc9249_crosswalk.py keeps chrony-specific observation fields out of the TimeState core until another adapter proof justifies them.

Fake-live capture harness exercises the real subprocess command runner with a temporary `chronyc` executable.
CHRONY-P1-SOURCESTATS-DIAGNOSTIC-CAPTURED verifies sourcestats parsing without changing the P1 decision.
CHRONY-P1-CAPTURE-TRACKING-INSTANT-AGE-GUARD verifies delayed diagnostic commands cannot reduce replay age.
The evaluator derives a conservative interval from chrony root delay/root dispersion/system offset plus skew-based replay growth.
Negative root delay is clamped to zero contribution and cannot narrow the interval.
CHRONY-P1-NORMAL-SATISFIED reaches P1 security_sensitive_time.
CHRONY-P1-STALE-FALLBACK falls back to coarse_logging.
CHRONY-P1-DISPLAY-HOLDOVER-FALLBACK falls back to display_time after the logging age window is exceeded.
Unsynchronised, leap-insert, high-distance, and missing-field cases fail closed or reject input.
TV-122-001, TV-122-002, TV-123-001, TV-124-001, TV-125-001, and TV-126-001 validate generated local-assessed-state outputs.
```

The transport integrity checks remain relational; they do not cryptographically verify signatures.
