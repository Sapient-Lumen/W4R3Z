# Migration map — rev0127 to rev0128

## Operational change

Chrony retained captures now include two additional command roles when produced by the rev0128 collector:

- `authdata`: `chronyc authdata -a`
- `ntpdata`: `chronyc -n ntpdata`

These roles are used to populate adapter-local authentication diagnostics. They do not change the conservative time interval or P1 decision thresholds.

## Adapter change

`chrony_observation` now may contain `authentication_summary`. Local assessed states now may include `extension_hooks.authentication_posture` with explicit no-overclaim fields:

- `verified_by_timesync=false`
- `used_for_decision=false`
- `profile_strengthening=none`

Consumers should display these values as reported diagnostics only. They must not treat them as proof that NTS or symmetric-key authentication was verified by TimeSync.

## Fixture compatibility

Older rev0127 capture envelopes remain useful for replay if the required roles for that revision are present. Rev0128-generated captures include `authdata` and `ntpdata`; missing authentication commands should be treated as `not_observed`, not as authenticated or unauthenticated proof.

## Core invariant

No new TimeState field was added. The six-field core remains interval, timescale, freshness, regime, source posture, and applicability.
