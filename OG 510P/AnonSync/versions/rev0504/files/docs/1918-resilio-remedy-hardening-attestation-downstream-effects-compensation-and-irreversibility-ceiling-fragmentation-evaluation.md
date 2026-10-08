# Resilio remedy hardening attestation downstream effects, compensation, and irreversibility ceiling fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging that stale or conflicting state can do real work in the world before operators fully unwind it.
That is useful.

The strongest present ingredients are:

- current `How soon does synchronization start?` docs still say changes start syncing immediately when detected, but other changes can also arrive by scheduled rescan or on Sync start
- current `Is one-way synchronization possible?` docs still say read-only overwrite mode can restore deleted files, revert edited files, and re-download an older name after a rename
- current `What if several people make changes to the same file?` docs still say an offline-returning peer can overwrite later online work and leave the overwritten versions only in Archive
- current `Can I connect two pre-populated pre-existing folders?` docs still say latest timestamp can replace remote content when same-path files differ
- current `Using Archive for file versioning and restoring deleted files` docs still say only manual restoring is possible and even a restored file can be re-archived if Sync later judges it older
- current `Sharing a folder locally` docs still say a source folder can keep driving other locations on the same computer and that local shares inherit or lower permissions with the source
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked devices make each added folder automatically available on the other linked devices with full read-write access

## Where the current contract still fragments

The problem is not that Resilio lacks effect mechanics.
The problem is that it still does not produce one first-class, case-scoped **downstream effects and compensation** object.

Today an operator can often infer only weaker truths such as:

- the stale or conflicting state probably already triggered syncing somewhere
- some overwrites or restores probably happened according to generic folder rules
- some old or replaced copies probably survive in Archive
- some same-computer or linked-device locations probably inherited the effect
- some manual restore might still be possible if the operator finds the right copy soon enough
- some later reconnect, restart, or rescan might still replay or reapply a stale consequence

Those are useful clues.
They are not the same as an explicit answer to `which downstream actions already landed, which ones can still be undone, which ones require compensation instead of rollback, and what is the highest honest restoration sentence now?`

## Why that matters for AnonSync

AnonSync needs stronger post-invalidation truth than `the old claim is no longer being served`.
It needs to support claims such as:

- all subscribers now tombstone the stale claim, but one queued automation already executed and still needs compensating action
- file or record rewrites are reversible for one cohort, while human decisions or exported external acts are only compensable
- new stale-triggered actions are quarantined, but already-started jobs are still draining
- some downstream effects are restorable from governed copies, while others survive only as an irreversibility ceiling that blocks stronger restoration language
- the strongest honest sentence is `stale truth no longer served, downstream restoration incomplete`, not because the product failed to publish a recall, but because effect remediation is a distinct problem from invalidation

AnonSync therefore needs first-class objects for **triggering stale version, downstream action ledger, actor class, effect class, reversibility class, queue-drain posture, undo owner, compensation obligation, irreversibility ceiling, and blocked restoration sentence** rather than leaving operators to reconstruct action truth from sync timing, overwrite rules, Archive residue, reconnect behavior, and inherited share mechanics.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `what already acted on the stale truth, what can still be undone, and what now requires compensation or an irreversibility ceiling?` — only by making the operator combine several partially overlapping mechanics:

- change detection that may be immediate or rescan-driven
- overwrite behavior on read-only lanes
- offline-return precedence that can replace later work
- timestamp-driven replacement for pre-populated joins
- Archive as a manual, not typed-compensation, lane
- same-computer local shares and linked-device propagation that inherit source effects

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **downstream effects and compensation** directly.
Its interface family should let the product separate at least these truths:

- stale truth still could trigger new work
- new triggers blocked, old queue still draining
- triggered action inventory incomplete
- reversible machine actions pending undo
- reversible human actions pending correction
- compensation required for named cohort
- irreversibility ceiling declared for named cohort
- named cohort restored
- named cohort compensated but not restored
- broader restoration sentence still blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-downstream-effects contract sheet**, **Remedy-hardening-attestation-downstream-effects review**, **Remedy-hardening-attestation-downstream-effects proof**, **Remedy-hardening-attestation-downstream-effects timeline**, and **Remedy-hardening-attestation-downstream-effects lineage receipt**.
