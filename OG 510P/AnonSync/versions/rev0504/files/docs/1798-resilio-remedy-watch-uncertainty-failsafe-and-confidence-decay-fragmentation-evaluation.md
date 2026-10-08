# Resilio remedy watch uncertainty, fail-safe, and confidence-decay fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that a post-discharge guard can quietly lose credibility even when nothing obviously dramatic has happened.
That candor is useful.

The strongest ingredients from the present contract are:

- current `Sync Preferences` docs still say desktop notifications can be turned on or off and debug logging is optional, primarily for issue analysis
- current `Settings on mobile platforms` docs still say disabling Android notifications lowers Sync's priority and can stop background work
- current `Guide to Linux, and Sync peculiarities` docs still say Linux notifications do not appear outside Sync UI
- current `Sync Service Troubleshooting on Windows` docs still say some service setups lose filesystem update notifications and must learn updates on rescan or restart
- current `Agent run out of system notify watchers...` docs still say watcher exhaustion can force discovery to manual or periodic rescan
- current `My files don't sync` docs still say missing filesystem notifications may require restart or touching files so Sync rescans
- current `Collecting debug logs manually` docs still say operators may need to enable logging, restart Sync, reproduce the issue, and let logs accumulate for at least 15 minutes
- current `Resilio Sync change log` still shows force-rescan features and a history of fixes where visible surfaces were weaker than runtime truth

## Where the current contract still fragments

The problem is not that Resilio hides every uncertainty clue.
The problem is that it still lacks a first-class, case-scoped **remedy-watch-uncertainty** object.

Today the operator can often infer only weaker facts such as:

- notifications might still arrive on some platforms and not on others
- an Android peer might quietly lose background priority if notifications were disabled
- a Windows service setup might stop receiving update notifications and fall back to rescan or restart discovery
- watcher exhaustion might degrade freshness to periodic rescan
- a stale or quiet UI might not mean the case remains safely guarded
- logs can be gathered later, but only after the operator already suspects enough trouble to enable them and wait for new evidence

Those are useful operational clues.
They are not a fail-safe contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the watch was healthy the last time we checked`.
It needs to support claims such as:

- watch-health proof was current yesterday, but uncertainty budget expired this morning, so ordinary-life claims automatically degrade until fresh proof returns
- a required lane lost live notifications and fell back to periodic rescan, so the case stays discharged only under `uncertain, fail-safe pending` rather than `still safely guarded`
- a service or mobile blind spot is acceptable only because a typed fail-safe policy automatically re-fences or narrows ordinary-lane permissions once uncertainty crosses budget
- watch uncertainty can be declared before any confirmed relapse if detection coverage or freshness has become too weak
- ordinary life can continue only while a typed uncertainty budget, fallback discovery class, and fail-safe execution rule all remain live

AnonSync therefore needs a first-class object for **remedy watch uncertainty** rather than merely borrowing notification toggles, warning pages, logging workflows, service caveats, or rescan behavior.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `after this case was discharged and the guard once looked healthy, what happens when that guard's evidence goes stale or its signal path weakens?` — only by making the operator combine several operational surfaces:

- desktop notification settings
- Android background-priority coupling to notifications
- Linux in-UI-only notification behavior
- Windows service notification caveats
- watcher-loss warnings and periodic-rescan fallbacks
- rescan-or-restart troubleshooting guidance
- optional debug logging plus delayed evidence capture
- change-log evidence that rescan and stale-surface fixes keep mattering

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- watch health current but uncertainty budget armed
- uncertainty budget shrinking
- uncertainty declared for named cohort only
- uncertainty declared for required cohort
- signal path degraded but inside grace budget
- uncertainty over budget pending fail-safe
- automatic fail-safe re-fence fired
- automatic fail-safe narrowed permissions but did not fully re-fence
- manual fail-safe required
- uncertainty resolved by fresh proof
- uncertainty collapsed into unguarded ordinary life claim

That is why this tranche adds five more first-class pages: **Remedy-watch-uncertainty contract sheet**, **Remedy-watch-uncertainty review**, **Remedy-watch-uncertainty proof**, **Remedy-watch-uncertainty timeline**, and **Remedy-watch-uncertainty lineage receipt**.
