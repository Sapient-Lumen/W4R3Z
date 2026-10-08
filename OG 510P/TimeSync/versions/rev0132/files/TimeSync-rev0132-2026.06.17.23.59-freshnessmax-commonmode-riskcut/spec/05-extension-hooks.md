# 05 — Extension hooks

## Hook design rule

A hook is smaller than a profile field set and much smaller than a subsystem. It is a tiny typed surface used only where repeated pressure recurs across profiles.

A hook should be:

```text
small
reusable
interpretable without a standards catalog
safe to omit outside profiles that require it
removable if later pressure disappears
```

## Current hook set

### `traceability_posture`

A compact statement about recognized reference relationship and evidence posture.

```text
reference_anchor:
  utc_named_realization
  utc_unqualified
  profile_reference
  local_private
  unknown

evidence_posture:
  claimed
  traceable
  unknown
```

It may appear on both wire-adjacent claims and local assessed state when a profile requires it.

### `sync_dimension`

A compact declaration of the synchronization dimension that a profile or claim is about.

```text
time
phase
frequency
combination
unknown
```

This prevents frequency continuity, phase alignment, and ordinary clock-time use from being accidentally collapsed.

### `holdover_class`

A requestable hook for profile-specific holdover capability or classification. It is not profile-default across enough boundaries yet.

### `validity_scope`

A requestable hook for locality or scope-of-validity limits. It is strongest in degraded/local-continuity cases but not yet cross-profile-default.


### `timescale_realization`

A compact declaration of the realization behind a core timescale claim. It is used when `timestate.timescale` is too coarse for the assessed profile.

```text
scale: UTC | TAI | GPS | local_private | profile_defined | unknown
realization: string
leap_handling: standard_utc | smeared | continuous_utc_transition | not_applicable | unknown
tai_utc_offset_state: known | unknown | not_applicable
evidence_posture: claimed | traceable | profile_defined | not_applicable | unknown
```

This hook does not define a time service, source roster, or leap-second procedure. See `spec/29-timescale-realization-and-clock-continuity.md`.

### `clock_continuity_posture`

A compact declaration of local continuity assumptions relevant to profile evaluation.

```text
backward_step_policy: forbidden | bounded | permitted | unknown
smear_policy: none | leap_smear | policy_defined | not_applicable | unknown
monotonic_local_time: claimed | assessed | not_claimed | unknown
evidence_posture: claimed | assessed | profile_defined | not_applicable | unknown
```

This hook does not export a clock algorithm or monotonic-clock reading. See `spec/29-timescale-realization-and-clock-continuity.md`.

## Unknown consequence rule

If a stronger `applicability` claim depends on a hook that is now `unknown`, that stronger claim must not be preserved by default. A profile may define a weaker fallback, but `unknown` must not silently widen or preserve hook-dependent use.


## rev0068 source-diversity hook

`source_diversity_posture` summarizes dependency/common-mode posture without exporting a source roster, path history, raw observations, or clock-selection algorithm.
