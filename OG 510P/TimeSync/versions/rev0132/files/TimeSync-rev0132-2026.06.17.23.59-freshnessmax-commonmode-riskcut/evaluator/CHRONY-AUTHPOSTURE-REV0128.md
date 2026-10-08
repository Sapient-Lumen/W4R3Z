# Chrony authentication posture — rev0128

## Problem

Chrony can report authentication-related state through `authdata` and `ntpdata`. These fields are operationally important, but a TimeSync adapter must not equate reported management output with independently verified cryptographic evidence.

## Rule

For rev0128:

```text
reported authentication != TimeSync-verified authentication
```

The adapter may preserve chrony-reported `NTS`, symmetric-key, and `Authenticated` values. It must not use them to:

- narrow the assessed interval;
- strengthen source posture;
- satisfy an otherwise-unsatisfied profile lane;
- claim named UTC traceability;
- claim TimeSync performed cryptographic verification.

## Output boundary

Authentication data appears in two places:

- `chrony_observation.authentication_summary`, as adapter-local diagnostics;
- `local_assessed_state.extension_hooks.authentication_posture`, as a no-overclaim signal.

The hook is intentionally constrained:

```json
{
  "verified_by_timesync": false,
  "used_for_decision": false,
  "profile_strengthening": "none"
}
```

## Test

`CHRONY-P1-AUTH-REPORTED-NO-OVERCLAIM` combines reported authentication with high-distance timing evidence. The expected result remains:

```text
profile_conformance = unsatisfied
actionability = not_actionable
applicability = diagnostic_local_only
```

## Future work

A future NTS verifier must check real cryptographic evidence: NTS-KE/TLS identity, AEAD-protected NTP extension fields, cookies, request/response binding, replay protections, and packet/session evidence. Until then, authentication text remains evidence about chrony state, not proof for TimeSync admission.
