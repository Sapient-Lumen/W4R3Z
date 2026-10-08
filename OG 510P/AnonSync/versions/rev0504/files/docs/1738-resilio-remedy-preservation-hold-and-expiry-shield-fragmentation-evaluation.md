# Resilio remedy-preservation hold, reservation, and expiry-shield fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that surviving repair material can still decay, rotate away, or remain awkward to preserve.
That honesty is useful.

The most valuable ingredients from the present contract are:

- Archive retention exists and can be lengthened, shortened, or even set to never delete
- maximum file-size ceilings can exclude some versions from protection
- Archive can be disabled, manually cleared, or left to age out under normal policy
- restore remains manual rather than silently self-healing
- Android Archive retention is short and fixed, while some platform/UI surfaces expose less Archive access than others
- purge timing depends on periodic scan and some settings changes need restart to apply correctly
- free-space thresholds and ordinary operational cleanup pressure can compete with keeping repair material around

## Where the current contract still fragments

The problem is not that Resilio lacks preservation knobs.
The problem is that it still has no first-class, case-scoped preservation-hold object.

Today the operator can often infer only weaker facts such as:

- Archive TTL was raised globally or per job
- a file version is probably still present somewhere in Archive
- somebody could manually avoid clearing that Archive
- some platform can restore the file only if the operator remembers to act before purge or storage pressure wins
- some version is still covered only indirectly by a coarse setting rather than by a named case reservation
- a cure lane exists right now, but nothing explicit says that ordinary cleanup, expiry, folder removal, or storage reclamation has been subordinated to preserving that lane

Those are useful evidence inputs.
They are not a first-class preservation contract.

## Why that matters for AnonSync

AnonSync is trying to say stronger things than `repair might still be possible right now`.
It needs to support claims such as:

- repair substrate for this named case is now under hold and may not age out through ordinary retention
- cure is currently possible but not preserved, so delay itself is part of the debt
- preservation covers named cohorts but not all required cohorts
- preservation relies on manual operator action and therefore carries breach risk
- the cure lane collapsed not because bytes never existed, but because the hold was never armed, was armed too late, or was breached by ordinary cleanup
- retention was set broadly enough to keep bytes, but there is still no explicit reservation saying which exact repair material is being protected for which case

Resilio gives clues for these judgments.
It does not provide the judgment object itself.

## Non-clone conclusion

So the line stays hard:

- borrow Resilio's candor about retention knobs, never-delete settings, manual clear, restart-sensitive Archive parameters, periodic-scan-triggered purge, and platform ceilings
- do not clone a model where `cure-capable now` and `preserved for this case` still have to be reconstructed from Archive settings, power-user preferences, periodic scans, and operator memory

AnonSync should therefore own a dedicated preservation-hold page family rather than treating `repair material still exists` as if it already implied `repair material is now being actively protected against decay`.
