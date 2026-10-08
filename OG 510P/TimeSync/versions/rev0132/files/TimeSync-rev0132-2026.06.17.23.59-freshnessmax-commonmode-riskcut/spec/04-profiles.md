# 04 — Profiles

## Role

A profile is a compact container for dense requirements that should not widen the invariant core.

A profile defines:

```text
identity and version/revision
authority or namespace when needed
purpose
dominant timing pressure
required/default visible items
requestable optional items
control-surface obligations
fallback modes
applicability mapping
reference-strength expectation
lifecycle/current-policy stance when retained
```

## Common profile family

```text
P1  general computing
P2  distributed coordination
P3  traceable finance
P4  precision network / telecom
P5  critical infrastructure precision timing
P6  local continuity / degraded operation
```

P4 remains one profile family with two lanes:

```text
Lane A  frequency continuity / syntonization
Lane B  phase / time alignment
```

The lanes may define different applicability consequences without splitting P4 prematurely.

## Profile-default tier

A profile may require some hooks by default at its boundary even though those hooks are not part of the invariant core.

Current profile-default hooks:

```text
traceability_posture
sync_dimension
```

Current requestable-but-not-default hooks:

```text
holdover_class
validity_scope
```

## Fallback discipline

A profile may define a weaker acceptable mode. If so, the exported assessment may use:

```text
profile_conformance: fallback
```

But exported fallback must carry an explicit non-stronger `applicability` boundary. A bare fallback claim is not actionable.

## Reference discipline

An exported `profile_conformance` marker must be scoped by a resolvable `assessed_profile`, unless the boundary is sealed to exactly one authenticated/configured profile.
