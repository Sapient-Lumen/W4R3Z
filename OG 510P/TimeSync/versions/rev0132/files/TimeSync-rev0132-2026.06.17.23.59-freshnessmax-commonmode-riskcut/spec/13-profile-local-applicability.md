# 13 — Profile-local applicability

## Problem

The core TimeState needs an `applicability` field, but a single global vocabulary would either be too vague for demanding sectors or too large to remain a narrow waist.

## Rule

Applicability is interpreted through the active or assessed profile.

```text
(applicability label) + (assessed_profile) => meaningful downstream-use boundary
```

The label alone is not enough across mixed-profile boundaries.

## rev0062 concrete map

rev0062 defines concrete profile-local maps in:

```text
profiles/profile-catalog.json
profiles/applicability/*.json
```

Each map contains:

```text
applicability_labels:
  name
  rank
  optional dimension
  description

fallback_mappings:
  name
  from
  to
  trigger
  boundary_context_required
```

`rank` is profile-local. It is used only to check that a fallback target is not stronger than the source label inside the same profile map.

## No global downgrade lattice

There is no cross-profile assertion such as:

```text
P3.internal_recordkeeping == P1.coarse_logging
```

An implementation may map between profiles locally, but that mapping is a policy decision and must not be exported as if it were universal.

## Fallback rule

When `profile_conformance` is `fallback`, the exported `applicability` must be the target of a fallback mapping in the assessed profile map, unless the boundary is sealed and a local policy explicitly supplies equivalent mapping.

The fallback mapping explains why the weaker label is allowed; it does not certify that the original stronger use remains safe.

## Boundary-context interaction

A fallback mapping may require `boundary_context`. This is common when a downgrade is caused by loss, recovery, conflict, reconfiguration, or relay restatement.

If the selected fallback requires boundary context and the exported state lacks it, the fallback is not semantically complete.

## Consequence for multiple assessments

One TimeState may be simultaneously:

```text
P1 fallback: coarse_logging
P3 unsatisfied: diagnostic_local_only
P6 satisfied: partition_local_coordination
```

There is no single universal conformance result.
