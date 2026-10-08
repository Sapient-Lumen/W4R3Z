# TIMESTATE

This note drafts the first minimal TimeState for the archive.

It is meant to be:
- smaller than a full protocol status model,
- richer than a bare timestamp,
- and flexible enough to bridge current systems and future systems.

## Design rule

The canonical semantics should be an **interval**, not a lone scalar.

Why:
- TrueTime uses `[earliest, latest]`.
- Roughtime uses `timestamp + radius`.
- NTP / chrony expose max-error style quantities through root delay, root dispersion, and root distance.

These all point toward the same deeper need:
a timing client needs not just a claimed time, but a bounded statement about time.

## Minimal fields

### 1. `interval`
The estimated time interval in which true time currently lies.

Canonical meaning:
- `earliest`
- `latest`

Derived forms such as midpoint + radius may be exported, but the archive treats interval semantics as the more fundamental idea.

### 2. `timescale`
The reference timescale of the estimate.

Examples:
- UTC
- TAI
- profile-specific local or derived scales

This field exists because time semantics are part of the problem, not just formatting trivia.

### 3. `freshness`
A compact statement of how stale the state may be.

This may be represented as:
- time since last successful discipline,
- or a timestamp of last correction,
- or equivalent profile-specific semantics.

The point is that consumers need to know whether the state is still actively grounded.

### 4. `regime`
A compact label for the current operating condition.

Examples:
- normal
- degraded
- holdover
- partition-local
- recovery

This matters because downstream behavior may need to change even when the interval still looks usable.

### 5. `source_posture`
A compact statement of what kind of source/trust posture supports the state.

Not a full audit log.
Just enough to distinguish cases such as:
- single source
- multi-source agreement
- authenticated only
- mixed authenticated / unauthenticated
- local holdover only

### 6. `applicability`
A compact downstream-facing judgment about what classes of use this state is acceptable for.

The exact tier system is still open.
But some explicit downstream applicability signal looks load-bearing.

## Boundary note on `applicability`

The archive does **not** currently treat `applicability` as a full compliance verdict.
It is a coarse consequence signal.

rev0023 makes one additional boundary explicit:
`applicability` is not the same thing as the archive's provisional explanatory pair.
If `time_error_bound` and `rate_error_bound` ever matter,
they matter as reusable bound-bearing reasons beneath the consequence-facing label,
not as competing decision labels.

Profiles may map the same TimeState into much denser sector-specific judgments such as:
- acceptable for routine auth and logging
- acceptable for distributed ordering under profile X
- insufficient for traceable financial timestamping
- insufficient for phase-sensitive telecom or grid functions

That detail belongs mostly in profiles.
The core only needs the existence of an explicit consequence-facing signal.

## rev0025 boundary note

rev0025 adds one further distinction:
not every case that needs more than the minimal TimeState should force archive-wide promotion.

A profile may instead need a **widened profile-local boundary**.
Current archive judgment:
- P5 is the first clear case
- the widened semantic there is `time_error_bound`
- that case does not yet force the core to grow

This lets the archive acknowledge real interface pressure without mistaking the first such case for a universal requirement.

## Pressure note from rev0006

The six-scenario stress test did not force a seventh core field.
It did reveal a live pressure point:

Some domains care not only about epoch uncertainty but also about phase and frequency synchronization.
For now, the archive treats those as **profile extensions**, not as proof that the minimal TimeState is wrong.

## What is intentionally not in the minimal core

Not every TimeState should contain:
- full source roster
- full path history
- full governance workflow
- sector-specific policy details
- every raw timing statistic
- full phase / frequency state by default

Those may exist in richer profiles, but the minimal core should stay small.

## Archive judgment

This six-part shape remains the current best minimal candidate:
- interval
- timescale
- freshness
- regime
- source_posture
- applicability

Anything smaller currently looks likely to hide too much.
Anything much larger currently risks profile creep.


## rev0038 boundary note

rev0038 adds one architectural clarification:
this minimal TimeState now looks more like a **local assessed state** than a pure upstream wire claim.

That is useful because the six core fields mix:
- what was claimed upstream
- what the local system has inferred or judged
- and what downstream systems should do about the result

The archive does **not** treat this as a problem with the six-part core.
It treats it as a reason to distinguish:
- a thinner wire claim surface
- from a richer local assessed state surface

This preserves the core while giving the greenfield track a cleaner place to carry `profile_default` hooks when they are actually needed.

## rev0045 boundary note

rev0045 adds one small default consequence for `unknown`.

Current archive judgment:
- if a stronger `applicability` claim depends on a `profile_default` hook that is now `unknown`, that stronger claim may no longer be asserted by default
- the archive still does **not** impose one universal downgrade destination
- profiles may preserve weaker hook-independent applicability, or define a safer fallback explicitly

This keeps `applicability` honest without importing a policy lattice into the minimal core.


## rev0056 profile-conformance note

Missing profile-required/default evidence is handled at the profile-validation and local-assessment layer.

The minimal six-part `TimeState` does not gain a universal error field,
but its `applicability` value must not preserve a stronger claim that depended on a missing required/default hook.

rev0057 names the local validation outcome as `profile_conformance = satisfied | fallback | unsatisfied`; it remains local assessed metadata rather than a new minimum wire-claim field.

## rev0058 fallback/applicability note

rev0058 keeps `fallback` from becoming a competing consequence vocabulary.

Current archive judgment:
- `profile_conformance = fallback` is a validation outcome
- `applicability` remains the downstream use boundary
- fallback must not preserve a stronger hook-dependent applicability claim
- if no adequate lower applicability label exists, the state should be profile-`unsatisfied` or diagnostic/local only

This keeps the six-part TimeState stable while making fallback actionable enough not to become false reassurance.

## rev0059 assessed-profile note

rev0059 adds one scoped companion for exported local assessment:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
```

This does not change the six-part minimal TimeState.
It clarifies that conformance metadata is not meaningful without a profile scope.

Current archive judgment:
- `assessed_profile` belongs to local/export assessment metadata, not to every minimal source packet
- sealed single-profile boundaries may supply the profile identity through configuration or authenticated session context
- mixed, relayed, audited, or detached exports should carry an explicit resolvable profile reference
- one timing state may have multiple scoped assessments rather than one universal conformance value

This protects the core while preventing profile conformance from becoming a free-floating compliance claim.

## rev0060 profile-reference granularity note

rev0060 keeps the six-part minimal TimeState unchanged.

`assessed_profile` is still local/export assessment metadata. Its reference
strength depends on boundary need:
- versioned identifier when that is unambiguous
- authority when identifiers may collide
- digest when exact retained rules must be reconstructed
- signed binding only when the profile issuer or binding must be independently verified

A digest-backed profile reference binds the normative profile rules used for
assessment. It does not bind a source packet, certify a clock, or turn the
assessed state into a profile manifest.
