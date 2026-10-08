# Resilio remedy hardening attestation postcondition durability, recurrence, and steady-state fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the intended state is true right now on the surfaces we checked`, `that state will remain true for the intended slice across later churn`, and `future arrivals or reconnecting lanes cannot silently re-open the old hazard` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say every folder added on one linked device automatically becomes available on all the other linked devices, so present realization and future-arrival durability are not the same question
- current `Synchronization Modes` docs still say disconnected folders remain visible and may later be connected, while selective-sync folders are placeholder-heavy and hydrate only when a source peer is online
- current `Disconnecting and Removing Folders` docs still say disconnected folders can be reconnected later, may reconnect to a different default path, and removed linked-device folders can still remain on unlinked remotes
- current `How to clear offline devices?` docs still say hiding an offline linked device is only a view cleanup and that the device will reappear if it ever comes back online
- current `How to pause syncing` docs still say paused peers still sync deletions and still rescan and index new files
- current `What if several people make changes to the same file?` docs still say an offline peer can later come online and overwrite newer online work
- current `Using Archive for file versioning and restoring deleted files` docs still say restored files can be pushed back into Archive again on rescan if Sync was not running
- current `Cannot download files` docs still say a mesh can advertise files that later collapse into ghost-file warnings when no peer still has the bytes
- current `Resilio Sync change log` still records recurrence-style failures such as all folders disconnecting when a 30-days-offline peer comes online, deleted files returning sometimes, and folders returning with `(1)` after path churn or re-adds

## Where the current contract still fragments

The problem is not that Resilio lacks durability-relevant clues.
The problem is that it still does not produce one first-class, case-scoped **postcondition-durability** object.

Today an operator can often infer only weaker truths such as:

- the target state is realized for the currently visible cohort, but future linked-device arrivals will inherit a different state unless checked again
- the folder is disconnected or placeholder-light right now, but it can later reconnect, hydrate, or revive through a different path
- an offline device was hidden from view, but it was not actually retired from the governing world and may later re-enter it
- a paused lane looks quiescent, but deletions and indexing still keep moving underneath the pause
- a restored file appears back, but later rescan or later-offline replay can still displace it
- the current mesh looks satisfied, but a ghost-file or path-duplication condition can later re-open the hazard after the initial realization sentence was published

Those are useful clues.
They are not the same as an explicit answer to `will the realized target state stay true for the governed slice across the next governing horizon, despite reconnects, future arrivals, hidden returners, paused-side effects, replay, restore, and path churn?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the target state is true here now`.
It needs to support claims such as:

- the target state is realized now, but durability is blocked by future-arrival inheritance risk
- the target state is realized for the current cohort, but reconnect or replay risk still dominates the next governing horizon
- the target state is realized and stable within a named steady-state horizon for a named slice only
- the target state is realized and recurrence-resistant for the governed slice, while broader stronger permanence language remains blocked

So AnonSync should not clone Resilio's present contract at this seam.
It should borrow the candor about reconnects, placeholders, hidden returners, pause semantics, restore fragility, and ghost-file warnings, while replacing the fragmented operator story with one first-class family for **postcondition durability, recurrence budget, steady-state horizon, and survivor-lane truth**.

