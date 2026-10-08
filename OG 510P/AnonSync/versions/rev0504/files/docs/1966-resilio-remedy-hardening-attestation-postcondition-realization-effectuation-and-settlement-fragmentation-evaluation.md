# Resilio remedy hardening attestation postcondition realization, effectuation, and settlement fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the mandate was issued`, `the route was executed`, `the folder is visible`, `the placeholder exists`, `the file was restored`, `the peer came back online`, and `the intended remedy is therefore actually true for everyone who matters` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Synchronization Modes` docs still say disconnected mode shows a folder without data, selective-sync mode shows placeholders rather than full bytes, and syncing a placeholder still depends on at least one peer with the file being online
- current `Running Sync on schedule` docs still say paused shares still propagate deletions and still rescan and index new files
- current `Using Archive for file versioning and restoring deleted files` docs still say restored files have an older modified timestamp than peers, must be restored while Sync is running, and can otherwise be moved right back into Archive on rescan as older
- current `What if several people make changes to the same file?` docs still say an offline peer that later comes online can overwrite later online changes and place the overwritten versions into Archive
- current `Can I connect two pre-populated pre-existing folders?` docs still say same-path files with different hashes are resolved by syncing the file with the latest timestamp and replacing the remote copy
- current `Does Sync work in background?` docs still say reopening Sync re-indexes folders and that offline updates can later overwrite changes made by peers who stayed online

## Where the current contract still fragments

The problem is not that Resilio lacks outcome-relevant observations.
The problem is that it still does not produce one first-class, case-scoped **postcondition-realization** object.

Today an operator can often infer only weaker truths such as:

- the mandate route ran, but the target state is only visible on one surface
- the folder exists here, but bytes are placeholders or still depend on peer availability
- a restoration happened, but it can still be re-archived or displaced by newer remote state
- a paused lane still carries deletions or indexing side effects that undercut the hoped-for result
- a returning offline peer can later reverse the seemingly realized state
- a pre-populated merge can replace remote content under timestamp rules the operator did not mean as the remedy itself

Those are useful clues.
They are not the same as an explicit answer to `did the intended postcondition actually become true for the intended subject and object slice, across the required worlds, and survive the immediate settlement hazards well enough for the stronger sentence?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the mandate was executable` or even `the route executed`.
It needs to support claims such as:

- the mandate executed, but the target postcondition is not yet observable anywhere that counts
- the target state is observable on one world only, while broader governed-slice realization remains blocked
- the target state is visible, but only as placeholders, metadata, or route-side evidence rather than full realized effect
- the target state is observable, but settlement remains open because rollback hazards still dominate
- contrary observation arrived after execution, so the stronger realization sentence collapsed
- the product can justify `named-slice postcondition observed` or `governed-slice postcondition realized`, but not yet `stable broader realization`

AnonSync therefore needs first-class objects for **target postcondition, beneficiary slice, governed object set, observation quorum, outcome witness class, settlement window, rollback or survivor hazard inventory, contrary observation state, highest honest realization sentence, and blocked stronger sentence** rather than leaving operators to infer realized truth from folder visibility, placeholder presence, archive restore rituals, pause behavior, timestamp tie-breaks, or offline-peer precedence.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `the mandate route ran, but did the intended state actually come true and stay true for the intended slice?` — only by making the operator combine several partially overlapping mechanics:

- disconnected and selective-sync visibility versus full-byte presence
- peer-online dependence for placeholder hydration
- pause lanes that still propagate some side effects
- archive restore behavior that can immediately lose again on rescan
- offline-peer precedence that can overwrite later online work
- pre-populated timestamp replacement rules
- restart or reopen re-indexing that can change what happens next

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **postcondition realization, effectuation, and settlement** directly.
Its interface family should let the product separate at least these truths:

- mandate routed only
- target postcondition not yet observed
- target postcondition observed for named slice only
- target postcondition observed, but settlement window open
- contrary observation or rollback hazard dominates
- postcondition realized for governed slice
- broader stronger realization sentence blocked
