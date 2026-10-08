# Resilio consumer-uptake, decision-pinning, and rollback blast-radius fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that visibility, notification, rendering surface, browser behavior, and operational trace are separate layers.
That honesty is genuinely useful.

The most valuable ingredients from the present contract are:

- the bell and History are explicitly described as operational surfaces, not as semantic commitment objects
- notifications are explicitly configurable and may be disabled
- WebUI is explicitly its own rendering surface and default experience on Linux, NAS, and service installs
- browser or ad-block quirks can explicitly make expected WebUI controls disappear
- Archive access is explicitly different across Sync UI, WebUI, Android, and iOS
- the change log explicitly preserves that UI state, notifications, and API exposure have had their own drift and repair history

## Where the current contract still fragments

The problem is not that Resilio hides complexity.
The problem is that it exposes the relevant clues across too many places and still does not own the decisive question:

> who actually used this sentence version as decision basis, and what does rollback now cost?

Today the operator can often infer only weaker facts such as:

- some consumer could have rendered the state
- some notification may have fired
- some UI surface or browser did or did not show a relevant control
- some API or linked-device path may have exposed a share or event
- some archive or history trace still exists

Those are helpful evidence inputs.
They are not a first-class consumer-uptake contract.

## Why that matters for AnonSync

AnonSync is trying to make stronger semantic claims than `a file looked synced` or `a control looked present`.
It needs to support claims such as:

- this consumer merely rendered the stronger sentence and never pinned it
- this consumer pinned sentence version S-17 but did not yet use it for a bound decision
- this consumer used S-17 as decision basis and launched a reversible action
- this other consumer completed an irreversible downstream act against S-17
- rollback is now cheap for cohort A, moderate for cohort B, and high-cost for cohort C

Resilio gives clues for these judgments.
It does not provide the judgment object itself.

## Non-clone conclusion

So the line stays hard:

- borrow Resilio's candor about notifications, surface divergence, WebUI asymmetry, archive access, and UI/API drift
- do not clone a model where render, fetch, pin, decision use, downstream action, and rollback blast radius still have to be reconstructed from scattered help pages and operational traces

AnonSync should therefore own a dedicated page family for consumer uptake rather than treating `current` as the end of the story.
