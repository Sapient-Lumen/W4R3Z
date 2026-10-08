# Resilio remedy hardening baseline assimilation, future-arrival inheritance, and scaffold-retirement fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still usefully candid about how much *default behavior* and *future-arrival behavior* remain separate from one another after a change already looks approved and rollout-bounded.
That candor matters.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say once devices are linked, all Sync folders automatically become available from any of those devices, and approvals may happen from any linked device where the folder is present
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices auto-receive Owner access by default, and one-way linked-device lanes require a manual Standard-folder detour
- current `What's the difference between Standard and Advanced folders?` docs still say Standard folders have no Owner layer, peers can share the key they have onward, and on-the-fly permission changes are not possible there
- current `Sync Share Dialog (Desktop)` docs still say Standard-folder keys do not use the approval mechanism
- current `Running Sync in configuration mode` docs still say configuration mode applies pre-configured parameters at program start and can set up only Standard folders
- current `Folder Preferences` docs still say important synchronization behavior remains folder-by-folder and desktop-only
- current `Sync Preferences` docs still say the default folder path governs where arriving folders or files will be created for devices in Selective Sync or Synced modes
- current `Synchronization Modes` docs still say linked devices can remain in Disconnected, Selective Sync, or Synced states, producing materially different future-arrival behavior even under one identity

## Where the current contract still fragments

The problem is not that Resilio lacks ways to push safe defaults into practice.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-baseline** object.

Today the operator can often infer only weaker truths such as:

- the current pilot or required cohort received the new hardening
- linked devices will probably inherit something useful
- new arrivals will probably land in the default path
- one-way or special-case lanes can probably be recreated manually
- Standard keys or links can probably be used to keep new arrivals moving
- some folder-level settings already look aligned on desktop
- future arrivals will probably resemble the current safe world

Those are useful operational clues.
They are not the same as an explicit answer to `has this hardened change actually become the safe baseline for future arrivals, or are we still depending on temporary pilot scaffolds, detours, remembered approvals, or scattered defaults?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-rollout claims than `the rollout stayed bounded`.
It needs to support claims such as:

- the bounded rollout succeeded, but new arrivals would still inherit the old unsafe baseline
- the bounded rollout is safe for the current cohort, yet linked-device auto-spread and Standard-key semantics still block a stronger baseline sentence
- the hardening is baseline-assimilated for desktop full-sync arrivals, but not yet for mobile, Disconnected, Selective Sync, or future-onward-share lanes
- manual pilot or one-way detour scaffolds still exist, so the stronger `ordinary baseline` sentence remains blocked
- future admission is now safe because the hardened behavior has been absorbed into the continuing baseline and the temporary rollout scaffolds have been explicitly retired or scarred

AnonSync therefore needs a first-class object for **hardening baseline assimilation and future-arrival inheritance** rather than merely borrowing linked-device, key, config-mode, default-path, or folder-preference language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did this bounded, hardened change truly become the safe baseline for future arrivals, or are we still relying on rollout-era scaffolds and detours?` — only by making the operator combine several operational surfaces:

- linked-device automatic folder availability and cross-device approval
- default Owner spread across linked devices
- manual Standard-folder detours for one-way linked-device behavior
- Standard-folder onward sharing and lack of approval mechanism on keys
- startup-scoped config mode that can set up only Standard folders
- per-folder desktop-only preferences
- default arrival paths
- different linked-device synchronization modes

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- rollout bounded, but baseline still provisional
- baseline assimilated for current cohort only
- future-arrival inheritance safe for named surfaces only
- rollout-era scaffold still required
- scaffold retired but scar still active
- new arrival still depends on remembered approval or manual detour
- baseline assimilated, future-arrival safe, and scaffold-retired discharge achieved
- baseline assimilation collapsed or regressed

That is why this tranche adds five more first-class pages: **Remedy-hardening-baseline contract sheet**, **Remedy-hardening-baseline review**, **Remedy-hardening-baseline proof**, **Remedy-hardening-baseline timeline**, and **Remedy-hardening-baseline lineage receipt**.
