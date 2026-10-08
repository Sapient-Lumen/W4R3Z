# Parent-source dependency review page — local-share placeholder inheritance and reconnect survivor map

## Purpose

Review any derived, local, or attached copy before the interface states that it is an independent second home for the data.
This page exists because a local copy may have its own path while still depending on a parent source share for actual bytes and future continuity.

## This review must distinguish

- derived path that has independent local bytes now;
- derived path that still relies on the parent source share for future materialization;
- parent source that is currently placeholder-only;
- parent disconnect or removal that will also remove the attached local share from Sync;
- reconnect workflows where the parent returns but the local share does not automatically reattach.

## Inputs the page must collect

### Dependency facts

- parent source share reference
- attached local-share reference
- current permission level inherited from parent
- whether parent currently has full bytes, mixed bytes, or placeholders only
- whether child can fetch from any peer other than the parent

### Lifecycle facts

- whether parent has been disconnected or removed
- whether child was automatically removed from Sync as a result
- whether parent has since been reconnected
- whether child has been manually reconnected yet

### Survivorship facts

- which bytes remain on disk in parent and child locations
- whether sync participation remains active for each
- whether permission downgrades on the parent have propagated to the child
- whether any source-proof cliff exists because the parent is no longer materialized

## Decision ladder

### Branch 1 — child currently independent enough for local access only

Use this branch when the child already has local bytes and immediate local access does not depend on the parent.
The page should show:

- local access truth
- whether future refresh still depends on the parent source
- that local access is weaker than sync independence

### Branch 2 — child path exists but parent still controls byte materialization

Use this branch when the child can only get missing content from the parent source share.
The page should show:

- that byte authority is upstream
- whether the parent is fully materialized or placeholder-only
- that child fetchability collapses if the parent lacks bytes
- that this is dependency truth, not a bug symptom

### Branch 3 — parent disconnect cascade

Use this branch when the parent was disconnected or removed and the attached local share was removed from Sync.
The page should show:

- what remained on disk
- what ceased syncing
- that parent reconnection alone does not automatically restore child sync participation
- the exact manual act needed to restore the child as a syncing object

### Branch 4 — permission or mode downgrade propagated from parent

Use this branch when the parent's permission or residency posture changed in a way that weakened the child.
The page should show:

- inherited downgrade basis
- current child capability ceiling
- whether local bytes remain but future writes or fetches are constrained
- that parent topology change is the cause of the child ceiling

## Required warnings

- `Separate path is weaker than separate source authority.`
- `Local share presence is weaker than independent byte materialization.`
- `Parent reconnect does not prove child reconnect.`
- `Inherited permission downgrade is a topology event, not a random local failure.`
- `Parent placeholder-only state can silently weaken child fetchability.`

## Review outputs

- dependency class
- parent materialization class
- child continuity class
- reconnect survivor map
- propagated capability ceiling
