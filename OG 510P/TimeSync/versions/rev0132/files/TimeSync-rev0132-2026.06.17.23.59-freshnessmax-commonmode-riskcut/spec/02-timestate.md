# 02 — TimeState

## Design rule

The canonical time statement is an interval, not a lone scalar.

A consumer needs a bounded statement about true time, plus enough local assessment to decide whether that state remains appropriate for its downstream use.

## Minimal fields

```text
TimeState:
  interval
  timescale
  freshness
  regime
  source_posture
  applicability
```

### `interval`

A bounded estimate of the time interval in which true time lies.

Canonical shape:

```text
earliest
latest
```

A midpoint-plus-radius representation may be exported, but interval semantics are primary.

### `timescale`

The reference timescale of the estimate.

Examples:

```text
UTC
TAI
profile-local scale
local private scale
unknown
```

### `freshness`

A compact statement of how stale the state may be.

Possible representations:

```text
last successful discipline time
maximum staleness
last correction time
profile-defined freshness expression
```

### `regime`

A compact operating-condition label.

Recommended vocabulary:

```text
normal
degraded
holdover
partition_local
recovery
unknown
```

### `source_posture`

A compact trust/source condition behind the state.

Recommended vocabulary:

```text
single_source
multi_source_agreement
authenticated_only
mixed_authenticated
local_holdover_only
unknown
```

This is not a full source roster or provenance graph.

### `applicability`

A downstream-facing use boundary. It answers:

```text
What classes of use should trust this state now?
```

The core does not define one universal sector vocabulary. Profiles map this field into their own concrete use labels.

## What is intentionally outside the core

The minimal TimeState does not include by default:

```text
full source roster
full path history
full audit log
profile manifest
source packet transcript
sector compliance matrix
all timing statistics
phase/frequency state
operator alias expansion
request bundle status
revocation infrastructure
```

Those may exist in profiles, examples, logs, or local systems. They are not part of the invariant narrow waist.

## Relationship to profile conformance

TimeState carries `applicability`. Profile assessment metadata may additionally carry:

```text
assessed_profile
profile_conformance
assessment_time
policy_acceptance
```

Those are local/export assessment fields, not mandatory minimum wire-claim fields.
