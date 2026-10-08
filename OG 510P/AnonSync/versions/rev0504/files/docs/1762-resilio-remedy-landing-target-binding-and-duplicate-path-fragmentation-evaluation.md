# Resilio remedy landing, target binding, and duplicate-path fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that moving bytes is not the same thing as proving the repair landed in the intended logical place.
That candor is useful.

The strongest ingredients from the present contract are:

- reconnect can propose a default path different from the original path and can create a new directory with a `(1)` suffix unless the operator manually points Sync back to the intended location
- moving or renaming a syncing folder has scope limits, and rename effects can remain local-only rather than propagating as a global folder-identity change
- connecting into a pre-existing non-empty directory requires an explicit confirmation because Sync will merge or exchange what it finds there
- placeholders can represent names without content, so a visible arrival can still be weaker than actual landed bytes
- `.sync` service files are critical, and completed transfer pieces are only renamed into their proper final place when the download completes
- Archive plus hash matching can sometimes rebind a rename without retransmitting data, but that still depends on Archive state and database continuity
- encrypted backup recovery can depend on keeping the encrypted folder attached and preserving its original database, keys, and unreadable stored bytes

## Where the current contract still fragments

The problem is not that Resilio hides landing complexity.
The problem is that it still lacks a first-class, case-scoped **remedy-landing** object.

Today the operator can often infer only weaker facts such as:

- repair bytes finished downloading somewhere
- a folder reconnected and now appears present again in the UI
- a non-empty destination was manually accepted
- a placeholder is visible where content may later be fetched
- an archive-backed rename probably avoided retransmission
- an encrypted backup peer probably still holds something recoverable

Those are useful operational clues.
They are not a landing contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the repair finished transferring`.
It needs to support claims such as:

- the right repaired object landed in the intended operative target rather than a duplicate path, side path, or placeholder-only shell
- the cure completed for a named pilot cohort, but required-cohort landing is still blocked because one target remains a duplicate directory or disconnected reattachment
- bytes landed, but the stronger sentence `repair landed as intended` stays blocked because `.sync` continuity, archive rebind evidence, or target binding is still ambiguous
- an encrypted or unreadable landing preserves substrate, but it is still weaker than an operative readable landing for the required cohort
- a merge into a pre-existing directory occurred, so safe adoption stays blocked until side-path and foreign-content risk are reviewed explicitly

AnonSync therefore needs a first-class object for **remedy landing** rather than merely borrowing reconnect, placeholder, archive, or folder-path vocabulary.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the right repair land in the right logical place for the right object and cohort, rather than in a duplicate, side path, placeholder-only shell, or unreadable backup lane?` — only by making the operator combine several operational surfaces:

- disconnect and reconnect path behavior
- move and rename caveats
- pre-populated folder merge confirmations
- placeholder and Selective Sync semantics
- `.sync` service-file behavior and final rename semantics
- Archive-backed rename behavior
- encrypted-backup restore caveats

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- landing requested
- bytes finished pending binding verification
- landed in duplicate or side path
- landed as placeholder-only shell
- landed unreadable or encrypted only
- landed via archive rebind but pending operative adoption
- landed for named cohort
- landed for required cohort
- landing misbound
- landing verification collapsed

That is why this tranche adds five more first-class pages: **Remedy-landing contract sheet**, **Remedy-landing review**, **Remedy-landing proof**, **Remedy-landing timeline**, and **Remedy-landing lineage receipt**.
