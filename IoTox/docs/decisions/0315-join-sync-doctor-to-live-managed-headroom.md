# ADR 0315: Join sync doctor to live managed headroom

- Status: accepted and implemented
- Date: 2026-09-03

## Context

ADR 0288 deliberately stopped before a namespace existed. Its `sync-doctor` command reused the
production source rules and estimated one new revision, but could report only source-filesystem
space and default policy bounds. ADR 0290 later supplied a strict file-backed Agent configuration,
and ADR 0297 supplied authenticated namespace health, but neither joined a configured automation
source to the exact live immutable-store occupancy, incoming staging, nondefault quotas, and
filesystem headroom.

That gap matters before real working copies are admitted. A source can fit the generic defaults yet
not fit the selected namespace after retained objects and partial transfers are counted. A useful
answer must also be read-only: diagnosis must not initialize a missing namespace, create a lock,
publish a revision, or contact a peer merely to produce a reassuring report.

## Decision

Add the owner-local command:

```text
iotox sync-doctor-configured --config PATH NAMESPACE
```

It loads only the exact canonical Agent configuration, stable device identity, owner-private
namespace tree, and stable-device-signed automation tree. The selected namespace must be enabled,
already initialized, and have an active local publish, writable, or bidirectional source. The
command then:

1. applies the exact configured engine, projection rules, and nondefault quotas to the automation
   source through the existing race-detecting production source inspector;
2. acquires the already-existing namespace transaction without creating missing state;
3. authenticates and inventories the complete live immutable object directory, or tree-v2's
   reachable-plus-candidate object plan;
4. recursively inventories the engine's private incoming staging root under a fixed policy-derived
   entry bound;
5. refuses when the current store plus conservative next-revision estimates exceed byte, object,
   or staging quotas;
6. compares the conservative additional requirement with current filesystem availability, adding
   one complete writable projection reserve when source and managed storage share a filesystem; and
7. re-reads both policy stores before reporting success so one management generation cannot be
   spliced into another.

Every inspected transaction directory, lock, staging directory, and staging file must have its
exact owner-private type, ownership, mode, and link shape. A missing transaction boundary is
`not_found`; an unsafe existing boundary is a protocol refusal. The configured report is the strict
`iotox-sync-doctor-v2` grammar and adds namespace, exact automation generation and interval, managed
store/staging occupancy and quota headroom, filesystem capacity/availability/requirement, and
`managed-storage-headroom=ready`. The original pre-creation command remains byte-compatible v1 and
continues to say `managed-storage-headroom=not-probed`.

The check is a point-in-time observation, not a reservation. Source writers may change the tree
after it finishes, another Agent instance must not mutate the same owner-private store, and
filesystem free-space results can immediately change. The command does not start the Agent, query
a peer, prove convergence or storage durability, inspect backup custody, or make permanent deletion
safe.

## Consequences

Four owned checks bring the direct registry to 821. They cover the full configured CLI path with a
signed automation record and nondefault quota, content-v2 live staging and quota refusal, a missing
transaction boundary with zero creation, and a reconciled writable tree-v2 store with incoming
staging and shared-filesystem projection reserve.

This completes the repository mechanism for the trust-graduation plan's preflight-and-inventory
gate. Precious-data recommendation still requires the 24-hour three-writer soak, abrupt-storage
and ENOSPC/read-only campaign, representative-capacity measurements, explicit filesystem semantic
contract, recovery-rehearsal tooling, and deployment-appropriate protected-state/witness custody.
