# Route-layer registry and handle-sprawl refactor

rev0282 adds `LEDGER-FAMILY-REGISTRY.json` to make support-layer ownership auditable. The archive now has many executable route-support layers. Without a registry, a later layer can silently become overbroad by binding every route to every row rather than binding a route to its owned row plus the metadata wrapper.

## Refactor performed in rev0282

The rev0280 composition/interface/global-consistency layer was overbound in the route rows: each route row carried all fourteen composition, interface, and global-consistency row IDs. The rows themselves were route-local. rev0282 narrows the route-row handles to the intended route-local-plus-wrapper pattern.

This does not weaken the composition gate. It makes the gate more accurate:

```text
route-local composition row + metadata wrapper
not every composition row in the archive
```

## Audit policy

The generated audit at `docs/30-program/route-layer-coverage-audit.generated.md` checks that registered route fields are nonempty and that route-local-plus-wrapper families do not expand into all-row binding by accident.

## rev0283 cardinality audit

The rev0282 registry exposed a second issue: many mature layers already behaved as route-local-plus-wrapper families, but the registry still labeled them only as nonempty route fields. rev0283 updates the registry policy for those families and declares `maximum_route_field_cardinality: 2` where the intended pattern is one route-owned row plus the metadata/provenance wrapper. This converts handle-sprawl detection from a loose warning into a machine-checkable cardinality rule.

