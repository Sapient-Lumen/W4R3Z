# IoTox synchronization time machine

Status: live owner-local tree-v2 recovery surface (ADR 0294).

The time machine makes retained signed tree-v2 history inspectable and lets a writable owner restore
an older projection without moving any accepted branch backward. It is operational recovery
material, not a backup. Only live retained immutable records and objects are visible; garbage
collection may remove unpinned history, a compromised host can roll all local state back together,
and a lost machine is still a lost copy.

## Inspect retained history

```sh
iotox sync-history NAMESPACE [LIMIT]
iotox sync-diff NAMESPACE FROM_RECORD_HEX TO_RECORD_HEX
iotox sync-conflicts NAMESPACE [RECORD_HEX]
iotox sync-retention NAMESPACE
```

`sync-history` defaults to 64 records and accepts 1 through 128. Its order is canonical by writer,
then descending writer generation, then record digest. It is not a wall-clock order: independent
writers do not share a total revision counter. `current=1`, `checkpoint=1`, and `pinned=1` are
separate facts. Quarantined records are excluded.

`sync-diff` compares the exact candidate sets, including causal provenance, and separately reports
whether the ordinary projected content changed. Paths are rendered as hexadecimal bytes so newline,
control, and delimiter characters cannot forge output records. The response gives exact total
counts; path detail is a deterministic bounded prefix with an explicit omitted count.

`sync-conflicts` describes either the current merged frontier or one retained record. It reports all
candidate writer/generation/kind/content identities for each displayed path, never file contents.
Like diff output, detail is bounded and omission is explicit.

Pin a recovery point before retention work if it must remain selectable:

```sh
iotox sync-pin NAMESPACE RECORD_HEX
```

A pin retains the record's authenticated graph closure under current quotas. It does not make that
closure an independent copy or protect it from whole-host rollback, corruption, loss, or operator
removal.

## Restore as a new forward revision

Planning is read-only:

```sh
iotox sync-restore-plan NAMESPACE RECORD_HEX
```

The result binds an opaque `plan=PLAN_ID_HEX` to the exact namespace policy, authenticated
maintenance state, current multi-writer frontier, signed workspace generation, clean worktree
projection, target record/manifest, and required immutable objects. It reports writer membership,
cutoffs, pins, current and target conflicts, required and missing bytes, and `ready=0|1`.

Apply only the exact ready plan:

```sh
iotox sync-restore-forward NAMESPACE RECORD_HEX PLAN_ID_HEX
```

Apply re-derives the plan under the namespace transaction and compares its ID in constant time. A
dirty worktree, frontier advance, policy or maintenance change, workspace transition, missing object,
conflicted target, exhausted quota, wrong target, stale ID, or replay refuses before publication.

On success IoTox selects the target's conflict-free projection, re-authors every target path plus
needed deletions at the next local writer generation, and publishes against the exact current signed
frontier. If generation 2 is current and generation 1 is selected, the result is generation 3 with
generation 2 as `previous`; it is never generation 1 installed as HEAD. Ordinary reconciliation
then uses its existing signed exchange journal to project the new revision. If projection fails
after branch commit, the error names the durable forward record and a later reconciliation resumes
from signed state.

The historical target itself is never granted authority. The local device must already be an
authorized namespace writer and have writable or bidirectional automation for the exact worktree.
Target conflicts are refused rather than silently choosing a winner.

## Two similarly named operations

These commands intentionally do different jobs:

- `sync-restore NAMESPACE` reauthenticates and moves GC-quarantined immutable objects back into the
  live store. It does not change synchronized content.
- `sync-restore-forward NAMESPACE RECORD PLAN` authors historical content as a new forward revision.
  It never reads quarantine and never rewinds a branch.

There is no `sync-rollback`, branch-pointer reset, destructive purge, or claim that history replaces
recovery custody.
