# Python surface — rev0018

## `siblingbroadcast.py`

```text
SiblingCandidate
SiblingBroadcastPolicy
SiblingBroadcastPlan
SiblingStoreReceipt
SiblingBroadcastReport
plan_sibling_broadcast()
assess_sibling_broadcast()
```

Tests cover family-capped sibling planning, family-diverse receipt acceptance, one-family rejection, contradictory receipt quarantine, and useful-refusal pressure.

## `keyspacecartography.py`

```text
RegionObservation
CartographyPolicy
RegionSummary
ScoutAction
KeyspaceCartographyBook
```

Tests cover region holes, stale pruning, monoculture scouting, introducer/family pressure, and minimal diverse coverage acceptance.

## `surfaceaudit.py`

```text
SurfacePointerFinding
SurfacePointerAudit
audit_surface_pointers()
```

Tests cover missing public/registry pointers. The run script also emits a rev0018 surface audit artifact.
