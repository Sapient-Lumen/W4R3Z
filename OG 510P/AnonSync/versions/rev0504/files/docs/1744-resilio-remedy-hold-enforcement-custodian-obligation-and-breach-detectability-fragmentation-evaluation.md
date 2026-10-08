# Resilio remedy-hold enforcement, custodian obligation, and breach-detectability fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that preservation is shaped by real operational constraints rather than wishful labels.
That honesty is useful.

The strongest ingredients from the present contract are:

- Archive and retention are explicit settings rather than hidden magic
- purge timing depends on periodic scan rather than an always-on perfect janitor
- restore remains manual, so the operator is not tricked into assuming automatic repair
- archive-related parameter changes may require restart to apply cleanly
- notification loss and watcher exhaustion are explicitly acknowledged as environments where state discovery can lag
- free-space policies and some admin-side retention policies can legally stop syncing or even delete data outright

## Where the current contract still fragments

The problem is not that Resilio lacks operational warnings.
The problem is that it still has no first-class, case-scoped enforcement object for a preservation hold.

Today the operator can often infer only weaker facts such as:

- retention settings seem favorable right now
- a given peer probably still has an Archive directory
- somebody could manually refrain from clearing that Archive
- a warning about lost notifications or watcher exhaustion implies detection lag rather than guaranteed immediate breach visibility
- an admin profile may allow ordinary cleanup or even permanent deletion paths that compete with preserving repair substrate
- mobile or platform-specific lanes may have preservation limits that are operationally known but not case-bound or acknowledgment-bound

Those are useful clues.
They are not a hold-enforcement contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `repair material is being kept somewhere for now`.
It needs to support claims such as:

- every named custodian that matters to this case has acknowledged the hold and is currently bound by it
- some custodians are bound but one important lane remains unacknowledged, unsensed, or allowed to decay under ordinary policy
- the hold exists on paper but enforcement remains weak because Archive can still be cleared, disabled, dehydrated, or deleted without case-specific interception
- breach visibility is delayed, so `no breach observed` remains weaker than `no breach could plausibly have escaped detection`
- preservation is still intact on desktop custodians but not on mobile or delegated storage lanes, so stronger cure sentences stay blocked
- repair substrate still exists but the product cannot honestly say the hold is enforced across every cleanup, restart, rescan, free-space, and revocation path that matters

Resilio gives ingredients for these judgments.
It does not provide the judgment object itself.

## Non-clone conclusion

So the line stays hard:

- borrow Resilio's candor about periodic-scan-driven purge, restart-sensitive Archive parameters, manual clear, watcher-loss warnings, free-space thresholds, and admin retention policies that can bypass Archive
- do not clone a model where `hold exists` and `hold is actually enforced with breach-detection coverage` still have to be reconstructed from settings pages, warnings, platform notes, and profile knobs

AnonSync should therefore own a dedicated hold-enforcement page family rather than letting `preserved for now` silently impersonate `bound, breach-detectable, and safe against ordinary cleanup paths`.
