# Terminal-review pre-mutation fence

## Parent ordering

In rev0806, the scheduler executor constructed execution-key vectors and called
claim/reclaim/abandon and owned-claim mutators. The daemon then aggregated that
completed pass and only afterward checked `stop_on_terminal_review`.

That ordering allowed this durable state:

```text
quarantined review row + runnable claimed rows
```

to produce this behavior:

```text
plan review and runnable mutations
build mutation-key filters
run mutations
observe review
stop daemon
```

The stop was real, but it was late.

## Rev0807 ordering

The executor now follows:

```text
load durable queue facts
validate and plan ordered groups
independently validate group metadata
observe terminal review
apply default-on mutation fence
only for unfenced groups: build key filters and call mutators
return explicit fence evidence
daemon records heartbeat and stops
```

The source audit verifies the fence appears before key-vector construction and
both mutation call sites.

## Durable integration fixture

The sync-domain corpus uses a copied checkpoint database containing one
quarantined row plus otherwise runnable claimed rows. It executes the scheduler
and daemon against independent copies and verifies:

- terminal review present;
- one review action observed;
- runnable mutations planned but all blocked;
- one mutation group and all its actions reported blocked;
- zero selected mutation groups/actions;
- zero execution-key filters;
- zero claim/abandon runs;
- zero owned-claim execution runs;
- zero completed workorders;
- zero chunk, receipt, and byte writes; and
- durable claimed/quarantined row counts plus review-event count unchanged.

The complete domain result is recorded in
`../validation/sync-domain-model.log`: **592 passed, 0 failed**.
