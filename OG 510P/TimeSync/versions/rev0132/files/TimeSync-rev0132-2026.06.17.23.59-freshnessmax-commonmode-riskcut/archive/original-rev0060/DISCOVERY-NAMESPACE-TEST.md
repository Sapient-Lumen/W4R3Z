# DISCOVERY-NAMESPACE-TEST

This note tests whether the archive's shared discovery/request surface needs explicit namespace separation for state versus explanation.

The archive already decided:
- one shared discovery/request mechanism
- separate requested subjects
- no second discovery channel

The remaining question is whether the shared surface now needs extra namespace machinery.

## Question

Does the shared discovery/request surface need explicit namespaces,
or is one request list with distinct item names already enough?

## Source pattern

The source base again favors the smaller answer.

- NTPv5 extension fields are distinguished by typed fields rather than by an extra namespace layer.
- Telecom signaling/TLV practice also relies on distinct types and item identities within one signaling surface.
- Roughtime-style tagged items likewise separate meaning by item identity, not by adding another hierarchy above the items.

That pattern suggests the archive should add namespacing only if name-level separation becomes concretely ambiguous.

## Smallest answer that survives the pressure

No explicit namespace layer is justified yet.

The current best rule is:

> one shared request list with distinct item names is enough,
> provided the names remain unambiguous and stable.

Examples in the archive's current shape:
- `traceability_posture`
- `sync_dimension`
- `boundary_context`

These do not currently collide in meaning.

## Why a request list is enough

### 1. The subjects are already semantically distinct
The archive is not trying to request two different things with the same name.
State/hook surfaces and explanation surfaces are different enough at the item-name level already.

### 2. Another hierarchy would be pure machinery
Adding namespaces now would increase syntax and documentation burden,
without solving a demonstrated ambiguity.

### 3. The archive can still escalate later if needed
If future items create collisions or make the request list muddy,
the archive can still introduce explicit namespace separation later.
Nothing about the current shape prevents that.

## Current archive judgment

The shared discovery/request surface does **not** need explicit namespaces yet.

Current default:
- one request list
- distinct item names
- no extra hierarchy above them

## What this still does **not** settle

This note still does not decide:
- whether profiles should be able to request named bundles of items
- whether operator-facing and machine-facing request forms should differ
- how much aliasing or shorthand the archive should tolerate in human-facing tools

## Next useful move

Test whether profile-level named bundles earn themselves,
or whether item-level requests are still enough.
