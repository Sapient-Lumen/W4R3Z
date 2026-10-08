# Resilio change-detection coverage, rescan fallback, and observation-freshness fragmentation evaluation

## Purpose

The archive already had route provenance, representative-pair review, instrumentation posture, and diagnostic receipts.
What it still lacked was one explicit comparison document for another ordinary operator question:

> when the operator asks `how quickly should this change have been noticed, what detection plane was active, and how much blindness or delay was built into that answer?`, where does the product itself own the answer?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio is not vague about the ingredients.
It documents filesystem notifications, scheduled rescans, manual rescans, watcher exhaustion, notification-hostile storage, IgnoreList reread timing, and power-user rescan tuning.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- change detection and byte transfer are not the same stage
- filesystem notifications are the fastest detection path when they work
- scheduled rescans are a distinct fallback plane with a different latency profile
- some storage/network shapes are not expected to support notifications reliably
- watcher exhaustion and power-user tuning can materially widen blind windows
- manual rescan is a real operator probe, not merely cosmetic chrome

This is much better than products that pretend every subject is watched continuously and equally.

## What still should not be cloned

The detection-truth contract is still scattered and too support-shaped.
Current official Resilio docs still require the operator to combine at least four article families:

1. **How soon does synchronization start?** for the model of filesystem notifications, scheduled rescans every 600 seconds by default, on-demand rescans, and the fact that `folder_rescan_interval = 0` means no automatic rescan even on restart
2. **Agent run out of system notify watchers** for the Linux watcher-exhaustion warning, the fallback to periodic/manual rescan, and the sysctl-based attempt to raise watcher limits
3. **Ignoring files in Sync (Ignore List)** for the rule that IgnoreList rereads happen on change or, if notifications are not arriving, every `folder_rescan_interval`, with restart recommended for immediate effect
4. **Sync prevents HDD from sleeping on NAS** plus **Power user preferences** for the fact that operators may intentionally widen `folder_rescan_interval` to preserve sleep behavior, while profiler/log/config cadence settings create more runtime posture that affects freshness expectations

That means one ordinary answer is still reconstructed from several places:

- whether this subject is currently under notification-backed observation or rescan-backed observation
- what expected detection latency applies right now
- whether the latency budget was widened intentionally, accidentally, or because the substrate cannot do better
- whether manual rescan is evidence-gathering, a workaround, or the only currently viable detection plane
- what exact sentence is safe about freshness and blindness right now

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **continuous-watch overclaim** — treating `connected` or `running` as if every relevant path is being observed in real time
2. **delay-without-ownership** — letting operators discover only after the fact that blindness came from watcher exhaustion, unsupported storage, widened rescan cadence, or a deliberate zero-rescan posture

A serious sync product needs one stable public answer to four different questions:

- **detection-posture truth** — what observation planes were intended and currently active for this subject?
- **coverage truth** — which parts of the subject actually benefit from notifications, and which fall back to rescans or manual probes?
- **freshness truth** — what expected discovery latency and blind-window budget apply right now?
- **intervention truth** — what is the cheapest honest rung: wait, rescan, restore notification capacity, or revise posture?

## Replacement pages in this revision

This revision adds four fixed pages:

- `792` — Detection posture
- `793` — Observation coverage review
- `794` — Change freshness review
- `795` — Change-detection receipt

Together they make detection plane, expected latency, blind-window basis, and strongest safe sentence explicit before AnonSync lets `should have synced already`, `watching normally`, or `just rescan it` become durable incident language.

## Concrete product stance

Borrow from Resilio:

- candid separation of notifications, scheduled rescans, and manual rescans
- candid admission that some storage types and watcher limits break immediate detection
- candid power-user control over rescan cadence and related runtime costs
- candid acknowledgment that detection latency may be widened to preserve storage sleep or reduce pressure

Do not clone from Resilio:

- leaving detection truth split across FAQ prose, warning pages, IgnoreList timing notes, and NAS tuning advice
- letting operators infer freshness from `running` without a declared observation plane
- making manual rescan do triple duty as test, workaround, and hidden detection contract without first-class explanation
- leaving no durable receipt of which latency budget, blind window, and intervention rung applied at the time of judgment

## Evaluation summary

Resilio still deserves credit for not pretending that all file changes are discovered the same way.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `what change-detection coverage existed here, how stale could the observation be, and what is the least-strong honest move now?`

AnonSync should therefore make **change-detection coverage** a first-class product object.
Every serious missing-update, stale-view, or delay investigation should publish active detection plane, latency budget, blind-window basis, notification-coverage grade, cheapest honest intervention, strongest allowed sentence, and forbidden stronger sentence before the product treats `delayed`, `stuck`, or `needs rescan` as coherent incident truth.
