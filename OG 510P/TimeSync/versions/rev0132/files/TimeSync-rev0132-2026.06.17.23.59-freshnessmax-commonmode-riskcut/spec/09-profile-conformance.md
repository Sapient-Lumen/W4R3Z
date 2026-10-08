# 09 — Profile conformance

## Local/export assessment triad

```text
assessed_profile
profile_conformance
applicability
```

Where:

```text
profile_conformance = satisfied | fallback | unsatisfied
```

## Meanings

### `satisfied`

The assessed state meets the active profile obligations for the exported boundary.

### `fallback`

Full profile satisfaction failed, but the profile defines a weaker acceptable mode.

Fallback must carry a non-stronger `applicability` boundary. It is not a universal downgrade label.

### `unsatisfied`

The profile is not met and no accepted fallback mode applies.

## Export rule

If assessed state crosses a boundary with `profile_conformance`, the evaluated profile must be resolvable by the receiver unless the boundary is sealed to exactly one profile.

## Required/default absence rule

If a profile requires or defaults an item and that item is missing:

```text
packet or exchange may remain valid
full profile satisfaction fails by default
local assessed state must withdraw hook-dependent stronger applicability
fallback may apply only if profile-defined
otherwise conformance is unsatisfied
```

## Fallback/applicability invariant

```text
profile_conformance: fallback
requires
applicability: <explicit non-stronger downstream-use boundary>
```

If no safe lower applicability can be expressed, the state should export as `unsatisfied` for that profile or remain diagnostic/local-only.

## Multiple assessments

A single local assessed state may carry multiple profile assessments. Each assessment is scoped independently:

```text
profile_assessments:
  - assessed_profile: P3@v1
    profile_conformance: unsatisfied
    applicability: diagnostic_local_only
  - assessed_profile: P1@v1
    profile_conformance: fallback
    applicability: coarse_logging
```

No universal conformance value is implied.
