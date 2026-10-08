# FT-0061 closure — Profile-local applicability maps

## Frontier closed

FT-0061 asked how P1-P6 should define concrete applicability labels and fallback mappings without creating a universal sector-spanning applicability vocabulary.

## Resolution

rev0062 adds a profile-local applicability map for each profile family:

```text
profiles/profile-catalog.json
profiles/applicability/P1-general-computing.json
profiles/applicability/P2-distributed-coordination.json
profiles/applicability/P3-traceable-finance.json
profiles/applicability/P4-precision-network-telecom.json
profiles/applicability/P5-critical-infrastructure-precision.json
profiles/applicability/P6-local-continuity-degraded.json
```

Each map defines:

```text
profile id and version
profile lifecycle state
obligations
profile-local applicability labels
profile-local fallback mappings
reference-strength policy
normative-rules digest
```

## Key rule

Applicability labels are concrete enough for fixtures and semantic validation, but remain profile-local. The same label text may be reused across profiles only when its meaning is explicitly defined in that profile's map.

## Non-result

rev0062 does not create a global applicability registry, a global downgrade lattice, or a cross-sector compliance vocabulary.
