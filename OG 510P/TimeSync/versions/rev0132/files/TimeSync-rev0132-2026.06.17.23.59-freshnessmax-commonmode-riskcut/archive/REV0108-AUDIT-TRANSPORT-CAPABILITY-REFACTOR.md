# rev0108 audit — transport capability semantics

## Finding

Transport capability validation had remained relatively thin compared with the later digest, temporal, and transport-integrity work. It checked that an advertised adapter exists, that supported message types are allowed by that adapter, and that negative statuses contain the expected trio. It did not check the capability's profile or request-item claims against the profile catalog and adapter profile-reference policy.

## Why this matters

Capability metadata does not update TimeState and does not prove provenance. Still, it is a request-construction surface. If it can advertise unknown profiles or private/non-TimeSync request items, a consumer may build a request that appears locally authorized while bypassing the archive's profile-local boundary rules.

The most important concrete failure is an adapter catalog entry with:

```text
profile_reference_policy.may_carry_profile_reference = false
```

while its capability advertisement still contains `supported_profiles`. That is a direct contradiction between catalog policy and advertised capability.

## Refactor

Added `tools/transport_capability_semantics.py` and routed `check_transport_capability` through it. The helper owns adapter/profile/requestable-item alignment and has a standalone self-test.

## Negative coverage

Added three rendered fixtures, all patch-derived from the positive capability advertisement envelope:

```text
DF-0108-001 -> transport-capability-unknown-profile-invalid.json
DF-0108-002 -> transport-capability-unknown-request-item-invalid.json
DF-0108-003 -> transport-capability-profile-ref-forbidden-adapter-invalid.json
```

This preserves human-reviewable JSON while making copy drift visible to validation.

## Non-goals

rev0108 does not:

```text
make capability advertisements authoritative credentials
add transport negotiation state
allow envelope authentication to substitute for profile digest obligations
export source rosters or private adapter material
```
