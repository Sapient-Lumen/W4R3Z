# rev0067 refactor audit

## Added reusable layer

`src/muc5/response_matrix.py` packages the response-cycle machinery introduced ad hoc in rev0065 and rev0066:

```text
rev0067_response_matrix_arms()
response_matrix_specs()
response_matrix_stress_specs()
compare_response_matrix_by_life()
response_matrix_gate_report()
```

The refactor intentionally reuses the existing `ThreatResponseArm` and threat-response forensics instead of inventing another parallel schema.  This keeps old C++ shadow rollout, terminal mechanism, trajectory forensic, closure-feature, replay, and counter-ownership audits compatible.

## Public profile addition

`PublicProfileAgent` now supports `threat_surge` and aliases:

```text
threat_surge
threat_protect
threat_counterpressure
threat_face_surge
public_threat_surge
```

The profile uses only public `DecisionFrame` observations and legal action metadata.  It keeps the rev0066 own-spell counter guard: self-countering remains legal, but this public profile strongly penalizes selecting it accidentally.

## Tests

`tests/test_rev0067_response_matrix.py` verifies:

```text
threat_surge alias loading
self-counter penalty and stack-protection scoring
three threat axes present in each legal size cell
surge-refutation classification in the matrix comparator
```

## Retention

rev0067 generated 59,869 C++ transition rows during parity checking.  It ships compact transition samples and aggregated forensic tables only.  Full rev0067 raw transition CSV ballast is excluded by the artifact audit.
