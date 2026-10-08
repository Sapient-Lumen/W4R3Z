# Resilio remedy hardening drift, carry-forward, and retention fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still expose several ingredients that matter once a case has already re-entered guarded ordinary life and claims to be recurrence-hardened.
That candor is useful.

The strongest present ingredients are:

- current `Running Sync in configuration mode` docs still say Sync can apply the same settings on a number of different machines at program start, while also noting that config mode can set up only Standard folders, not Advanced
- current `Folder Preferences` docs still say important behavior remains folder-by-folder and desktop-only, including relay, tracker, LAN search, predefined hosts, Archive, overwrite-on-read-only, and download priority
- current `Power user preferences` and current `File download priority` docs still say global defaults can apply to existing and new shares, but once a share's priority is manually altered, later global changes no longer affect it, even if the operator sets that share back to `None`
- current `Ignoring files in Sync (Ignore List)` docs still say peer sameness is only advisable rather than compulsory, meaning different peers may honestly carry different ignore behavior
- current `Comprehensive guide to syncing (Desktop-Desktop)` and `Sync functionality in detail` docs still say linked devices automatically receive every folder and that approvals can be issued from any linked device
- current `Sync Service Troubleshooting on Windows` docs still say changing service principal or service storage can produce a new storage world where old folders are absent until they are re-added and re-shared
- current `Resilio Sync change log` still records settings not saved after autoupdate sometimes, lower permissions not always updating from a new link, new folders not always propagating to linked NAS, duplicate offline peers in config mode, and sync modes or placeholder behavior drifting after restart

## Where the current contract still fragments

The problem is not that Resilio lacks hardening knobs.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-retention** object.

Today the operator can often infer only weaker facts such as:

- the hardening looked correct when first deployed
- one default exists somewhere
- one folder still shows the safer preference
- one linked identity still appears healthy
- one service restart brought the app back with roughly the expected shape
- one manual override was applied in good faith earlier

Those are useful operational clues.
They are not the same as an explicit answer to `has the hardening for this case actually survived later drift, new scope, onboarding, overrides, and storage-world change across the required cohort?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-hardening claims than `we deployed the guardrail once` or `the settings still look roughly right right now`.
It needs to support claims such as:

- the guardrail still survives on every required cohort member after later overrides and later folder arrivals
- one share drifted out of the default and now carries a hardening debt that blocks the stronger recurrence-retained sentence
- the case is still recurrence-hardened for the original cohort, but not yet for future carry-forward surface created by linked-device or later-admission spread
- one service-world fork or storage-path rebirth reopened hardening review even though the visible UI looked calm afterward
- lower-risk defaults remain deployed, but one manually altered share, one divergent IgnoreList, or one unpropagated new folder keeps the stronger retained-hardening sentence blocked

AnonSync therefore needs a first-class object for **hardening retention and drift watch** rather than merely borrowing config, preference, ignore-list, or linked-device language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did this case's recurrence hardening actually survive drift and carry-forward over time?` — only by making the operator combine several operational surfaces:

- startup-time config deployment that is Standard-only
- per-folder desktop-only preferences
- global defaults with sticky manual-override exceptions
- peer-local IgnoreLists that only "should" match
- linked-device auto-spread and any-device approval memory
- service storage or principal changes that can silently create a new state world
- change-log knowledge about settings persistence, propagation, and mode-drift failures

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- recurrence hardening achieved once
- hardening retained for original cohort only
- hardening drift suspected
- manual override detached one lane from current defaults
- peer-local rule divergence blocks stronger retention
- linked-device carry-forward surface reopened
- service or storage-world fork reopened hardening review
- required-cohort hardening retained
- future carry-forward hardening retained
- recurrence-hardened-and-retained discharge achieved

That is why this tranche adds five more first-class pages: **Remedy-hardening-retention contract sheet**, **Remedy-hardening-retention review**, **Remedy-hardening-retention proof**, **Remedy-hardening-retention timeline**, and **Remedy-hardening-retention lineage receipt**.
