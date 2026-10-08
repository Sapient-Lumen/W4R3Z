# Resilio remedy surveillance, relapse detection, and re-fence fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that ordinary post-repair calm is only observed through operational surfaces that can differ by platform, delivery lane, and runtime conditions.
That candor is useful.

The strongest ingredients from the present contract are:

- current `Sync Main View (Desktop)` docs still say the bell lights up for approval requests or other notifications and that History shows general syncing activity for the last 30 days
- current `Sync Preferences` docs still say desktop notifications can be turned on or off
- current `Settings on mobile platforms` docs still say Android can disable Sync activity notifications and pending-approval notifications, and that disabling them lowers Sync's priority so the app may stop working in the background
- current `Guide to Linux, and Sync peculiarities` docs still say Linux has no tray icon and notifications do not appear outside Sync UI
- current `Core warnings` and related warning articles still expose concrete relapse-relevant classes such as lost watchers, delayed periodic rescans, no-source peers, database issues, and time-difference problems
- current `Resilio Sync change log` still says notifications are synchronized across devices, notifications exist for permission and licensing changes, and older releases fixed cases where UI could be blank or stale while Sync itself continued working

## Where the current contract still fragments

The problem is not that Resilio hides relapse signals.
The problem is that it still lacks a first-class, case-scoped **remedy-surveillance** object.

Today the operator can often infer only weaker facts such as:

- a desktop bell or mobile drawer may have shown some warning or approval signal
- general history still contains a short operational trace window
- some warnings exist, but they live in a separate troubleshooting family rather than in one case object
- Linux may require the operator to be inside Sync UI to notice the same issue that other platforms surface differently
- Android may lose background priority if notifications are disabled, making observed quiet weaker than watched quiet
- synchronized notifications across devices are still not the same as one authoritative answer to whether a discharged case is actively guarded against relapse

Those are useful operational clues.
They are not a relapse-surveillance contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the case was discharged and nothing noisy is visible`.
It needs to support claims such as:

- the case was discharged, but surveillance is only armed on a named desktop cohort while Linux and mobile blind spots keep stronger ordinary-life claims blocked
- a relapse signal was delivered somewhere, but required re-fencing authority did not yet trigger, so `ordinary life still guarded` remains weaker than `ordinary life still safe`
- background-priority degradation on Android keeps the honest sentence `surveillance armed with runtime blind spots` rather than `relapse-detectable ordinary lane`
- a warning family exists, but because history is short and notification delivery is optional, the stronger `case watch complete` sentence remains blocked
- a post-discharge case can stay open for ordinary use only while an explicit re-fence threshold, escalation lane, and required-cohort coverage remain armed

AnonSync therefore needs a first-class object for **remedy surveillance** rather than merely borrowing notifications, warnings, history, or platform caveats.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `after this case was discharged, is it still being watched strongly enough to catch relapse and automatically re-fence it when needed?` — only by making the operator combine several operational surfaces:

- bell and notification delivery behavior
- short-horizon general History
- desktop notification settings
- Android notification and background-priority behavior
- Linux in-UI-only notification behavior
- scattered warning families for watcher loss, no-source conditions, internal backlog, time drift, and database issues
- older change-log evidence that notifications and visible UI state can diverge from underlying runtime truth

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- discharge released pending surveillance arming
- surveillance armed for named cohort only
- surveillance armed with platform blind spots
- surveillance armed with runtime blind spots
- relapse signal observed pending re-fence threshold
- relapse threshold met pending re-fence
- automatic re-fence fired
- manual re-fence required
- surveillance collapsed
- discharge collapsed by relapse
- ordinary-lane continuation still guarded
- ordinary-lane continuation no longer honestly guarded

That is why this tranche adds five more first-class pages: **Remedy-surveillance contract sheet**, **Remedy-surveillance review**, **Remedy-surveillance proof**, **Remedy-surveillance timeline**, and **Remedy-surveillance lineage receipt**.
