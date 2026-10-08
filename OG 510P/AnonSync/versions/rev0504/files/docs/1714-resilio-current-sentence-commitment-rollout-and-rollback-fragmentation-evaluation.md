# Resilio current-sentence commitment, rollout, and rollback fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `promotion looks allowed`, `the bell lit up`, `the History tab shows activity`, `the WebUI exists`, `API exists`, `optional columns can be enabled`, `notifications are synchronized`, and `every downstream consumer is now actually operating on the same stronger sentence` are not one flat truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than promotion:

> after the product knows **a stronger sentence is promotion-authorized**, it still needs one first-class answer to **whether that sentence is actually committed as current operative truth, for which consumer families, through which surfaces, with what rollout lag, and under what rollback rule**.

Current official Resilio materials still do not provide one typed current-sentence object for:

- distinguishing promotion-authorized from committed-current
- distinguishing internal current state from external consumer-current state
- distinguishing optional UI visibility from durable current truth
- preserving which consumers are still lagging, disconnected, hidden, or manually refreshed
- preserving whether currentness lives in a durable ledger versus a bell event, column setting, short-window history row, or API scrape
- preserving when rollback is armed, who can trigger it, and what lower sentence survives if rollback fires
- preserving whether the stronger sentence is current for all required consumers or only a narrower staged cohort

Instead, the operator still has to translate green checks, bell lights, notification preferences, short-window history, optional columns, WebUI settings, and change-log hints about API or synchronized notifications into a judgment about whether the stronger sentence is really the live operative sentence now.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Main View (Desktop)` still says the bell lights up when approval requests or other notifications arrive, History shows general syncing activity for the last 30 days, green check means synced with all connected peers, and columns are optional display choices.
- `Sync Preferences` still says notifications can be turned on or off for approval requests, start/end of syncing, and other events.
- `Configuring WebUI` still says Sync can be rendered through WebUI, which is the default UI on Linux/NAS and service installs, with its own listening and exposure configuration.
- `Power user preferences` still says transfer-retention in the UI can be trimmed with `keep_expired_transfer_days` and `keep_expired_transfer_num`, meaning some operational traces are explicitly bounded.
- `Resilio Sync change log` still says notifications are synchronized across linked devices, optional `Owner` and `Last transferred` columns were added, Sync API v2 was enabled, and some releases fixed cases where UI did not update or where events only appeared on one linked device.

This is strong operational candor.
It is not a first-class current-sentence contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether a stronger sentence was only allowed in principle or is actually the current operative sentence
- whether that sentence is current only in one UI surface, one linked device family, one API consumer, or all required consumers
- whether a missing notification means nothing happened, notifications were disabled, the UI is lagging, or the consumer simply was not in the subscribed cohort
- whether a history entry or optional column is enough to treat the sentence as current
- whether a rollback must be triggered because rollout lag, stale UI, or contradictory consumer state remains
- whether a lower sentence must stay operative for some consumers while a stronger sentence is already current for others

That means current official materials can help answer `did a notification arrive`, `can I render Sync in WebUI`, `what optional columns exist`, `is there an API`, or `how long some UI transfer traces remain visible`.
They still do not directly answer `what stronger sentence is current right now, for which consumer families, on what durable basis, and with what rollback exposure?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit bell-and-history candor for operational cues
- explicit acknowledgement that notification visibility is configurable
- explicit acknowledgement that WebUI, desktop UI, and API are all separate surfaces
- explicit acknowledgement that some traces are bounded or may lag
- explicit acknowledgement that UI presence is not the same thing as durable state truth

But AnonSync should replace the page contract with a first-class **current sentence** object where each stronger sentence has its own:

- source promotion receipt
- exact sentence that is candidate to become current
- currentness scope by consumer family
- commit lane and rollout strategy
- lagging or stale consumer list
- rollback authority and rollback conditions
- surviving lower sentence while rollout is partial
- current-sentence timeline
- current-sentence lineage receipt

## Product decision tightened here

The new design line is:

- **promotion-authorized is weaker than committed-current**
- **committed-current for a staged cohort is weaker than all-required-consumer current**
- **preview, staged current, core-current, all-required-current, rollback-armed, rolled-back, and superseded current are different truths**
- **bell events, UI columns, WebUI presence, and API reachability are evidence inputs, not the currentness verdict**
- **rollback preserves lower truth and prior-current history rather than pretending the stronger sentence never existed**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for operational candor about notifications, UI surfaces, optional columns, API availability, and bounded traces.
Resilio remains on the non-clone side for the fairness-critical current-sentence contract.

The reason is now precise:

> current Resilio docs still expose bell notifications, short-window history, optional columns, configurable notification visibility, WebUI surface choices, and API existence as separate operational facts rather than one typed current-sentence object for `what stronger sentence is actually live right now, for which consumers, with what rollout lag, and under what rollback rule?`, so the operator still has to reconstruct whether the product is merely allowed to speak the stronger sentence or has truly committed it as current operative truth.

