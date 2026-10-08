# 07 — Discovery, request, and result accounting

## Exposure classes

Shared items use a small exposure vocabulary:

```text
required
requestable
unavailable
unknown
```

Profiles may require/default an item at their boundary. Otherwise, optional items are requested explicitly.

## Request shape

Ordinary requests are flat lists of item names:

```text
request:
  items:
    - traceability_posture
    - sync_dimension
    - boundary_context
```

No native bundle layer is defined. Operator aliases are local only and must expand to explicit item names before exchange.

## Request lifetime

Ordinary item requests are exchange-scoped unless a profile/default or explicit future lease says otherwise.

## Result accounting

Returned requested content is its own success result.

Absent requested optional items may produce compact negative item results when the exchange has a result-capable response surface:

```text
unavailable
unknown
omitted
```

Unrequested optional items may remain silent.

## Required/default absence

Missing profile-required/default evidence is not ordinary optional-request absence. It is handled by profile satisfaction and local assessed consequence:

```text
packet may remain parseable
profile_conformance cannot be satisfied by default
hook-dependent stronger applicability must be withdrawn or weakened
fallback is possible only if the profile defines it
```

## Returned hook validation

When discovery returns known extension hooks such as `timescale_realization` or `clock_continuity_posture`, the returned value must match that hook's schema. A malformed hook value is not treated as a successful return.

This remains flat result accounting. Returning a realization or continuity hook does not create negotiation, profile selection, or a bundle lifecycle.
