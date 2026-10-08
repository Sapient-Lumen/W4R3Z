# Resilio remedy watch health, drill freshness, and response-budget fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are candid that post-discharge safety depends on several operational surfaces that can go stale, go dark, or require manual diagnostic work.
That candor is useful.

The strongest ingredients from the present contract are:

- current `Sync Main View (Desktop)` docs still say the bell is only a notification surface and History is only general syncing activity for the last 30 days
- current `Settings on mobile platforms` docs still say disabling Android notifications lowers Sync's priority and can stop background work
- current `Guide to Linux, and Sync peculiarities` docs still say Linux notifications do not appear outside Sync UI
- current `Sync Preferences` docs still say debug logging is optional and exists mainly for later issue analysis
- current `Collecting debug logs manually` docs still say operators may need to enable debug logging, restart Sync, reproduce the issue, and then let logs accumulate for at least 15 minutes
- current `Agent run out of system notify watchers...` docs still say watcher exhaustion can force discovery to manual or periodic rescan
- current `Some internal tasks are taking time to complete` docs still say hidden operations can delay recovery and that the operator may need logs to understand whether recovery is timely
- current `Resilio Sync change log` still shows a history of fixes for blank or stale UI, missing indexing progress, and other cases where visible surfaces were weaker than runtime truth

## Where the current contract still fragments

The problem is not that Resilio hides every watch-health clue.
The problem is that it still lacks a first-class, case-scoped **remedy-watch-health** object.

Today the operator can often infer only weaker facts such as:

- a bell or mobile drawer might still surface something when a problem happens
- History still keeps a short operational trace window
- logs can be enabled if the operator already suspects a problem strongly enough
- watcher exhaustion and hidden-task backlog exist as warning families, but not as freshness or response-budget evidence for one discharged case
- Android background priority and Linux in-UI-only notifications make quiet surfaces weaker than proven watch health
- older change-log fixes prove that visible UI and runtime truth can drift, but there is still no typed product answer to whether this exact relapse guard was exercised recently enough and within budget

Those are useful operational clues.
They are not a watch-health contract.

## Why that matters for AnonSync

AnonSync needs to support stronger claims than `the case was discharged and the watch is armed somewhere`.
It needs to support claims such as:

- the case is still discharged, but the watch has not been canary-probed recently enough, so stronger guarded-ordinary-life claims stay blocked
- a relapse tripwire exists on paper, but the last successful end-to-end re-fence drill exceeded the allowed response budget, so the honest sentence remains `guard armed but response confidence stale`
- Android and Linux blind spots are acceptable only because a desktop-plus-log cohort recently passed a case-scoped detection drill inside budget
- watcher exhaustion or hidden-task backlog degraded the honest sentence from `response-budget proven` to `watch health stale pending reprobe`
- a discharged case may remain in ordinary life only while a typed freshness window, last successful probe, last successful drill, and maximum tolerated response budget all remain live

AnonSync therefore needs a first-class object for **remedy watch health** rather than merely borrowing notifications, warnings, history, logs, or platform caveats.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `after this case was discharged and surveillance was armed, how credible is that guard right now, and has it been exercised recently enough to trust its response budget?` — only by making the operator combine several operational surfaces:

- bell and notification delivery behavior
- short-horizon general History
- optional desktop and Android notification settings
- Linux in-UI-only notification behavior
- optional debug logging plus manual reproduction steps
- watcher-loss warnings and periodic-rescan fallbacks
- hidden-task backlog warnings
- change-log evidence that visible UI can be stale or incomplete relative to runtime truth

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- surveillance armed pending watch-health probe
- watch health stale
- canary probe in progress
- canary probe passed for named cohort only
- canary probe passed for required cohort
- response-budget drill passed
- response-budget drill failed or exceeded budget
- watch-health degraded by runtime blind spot
- watch-health degraded by evidence freshness lapse
- watch-health collapsed
- discharge continues but only under stale-guard warning
- guarded ordinary life remains honestly proven right now

That is why this tranche adds five more first-class pages: **Remedy-watch-health contract sheet**, **Remedy-watch-health review**, **Remedy-watch-health proof**, **Remedy-watch-health timeline**, and **Remedy-watch-health lineage receipt**.
