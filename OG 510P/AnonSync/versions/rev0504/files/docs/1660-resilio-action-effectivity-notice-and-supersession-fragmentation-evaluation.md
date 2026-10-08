# Resilio action-effectivity, notice, and supersession fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that approval, permission change, revocation, notification, history, and disconnect are not one flat event.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than action sufficiency:

> after the product knows **which typed act a coalition may execute**, it still needs one first-class answer to **when that act becomes real, for whom, after what notice, and what later event supersedes or withdraws it**.

Current Resilio materials still do not provide one typed enactment lifecycle for:

- drafted but not executed acts
- executed but not yet effective acts
- effective-for-protective-use vs effective-for-irreversible-closure
- notice still pending to required recipients
- cooling window still running after execution
- contest-open acts
- superseded or narrowed acts
- withdrawn or reopened acts whose weaker sub-truths still survive

Instead, the operator still has to translate approval memory, permission toggles, notifications, history, and disconnect behavior into effectivity meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `User Management` still says Advanced-folder permissions can be changed on the fly and that disconnect revokes future updates while already synchronized files remain in place.
- `Sync functionality in detail` still says linked devices can approve connections from any linked device, that prior approval can be retained by certificate, and that folder links can optionally require approval for every peer.
- `What's the difference between Standard and Advanced folders?` still says Advanced folders store certificates of previously dealt-with users and can distinguish known vs new peers, while Standard folders cannot do on-the-fly permission change and do not reflect user identity the same way.
- `Sync Main View (Desktop)` still says the bell lights up for approval requests or other notifications and that History shows general syncing activity for the last 30 days.
- `Resilio Sync change log` still says Sync added synchronized notifications across linked devices, notifications for permission and licensing changes, a searchable and sortable history tab, and that share-dialog settings are remembered when the dialog is reopened.

This is strong operational candor.
It is not a first-class enactment lifecycle.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and UI surfaces:

- whether the act was only proposed or actually executed
- whether execution was immediately effective or still in a cooling state
- whether all required recipients were actually notified
- whether the act was visible only as a notification, only as general history, or as neither
- whether a later permission change, disconnect, or reopen superseded the earlier effect
- whether narrower truths survive after a broader effect is withdrawn

That means current official materials can help answer `did a permission change happen?`, `can this peer still get future updates?`, or `was there an approval request?`
They still do not directly answer `has the irreversible act actually taken effect for the whole required notice cohort, is it still contestable, and what exact earlier truth was superseded rather than erased?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit approval surfaces
- visible permission-change events
- synchronized notifications
- searchable history
- preserved divergence between future updates and already-received bytes

But AnonSync should replace the page contract with a first-class **action enactment lifecycle** where each typed act has its own:

- proposal state
- execution state
- notice cohort and delivery completeness
- effectivity rule
- cooling and contest timers
- supersession rule
- withdrawal and reopen aftermath

## Product decision tightened here

The new design line is:

- **executed act is weaker than effective act**
- **notice delivered to some watchers is weaker than notice completed for the required cohort**
- **protective acts may become effective immediately while irreversible acts default to notice plus cooling unless the contract says otherwise**
- **supersession must name exactly which earlier sentence is narrowed, preserved, or withdrawn**
- **no history row, bell notification, or role change may silently impersonate final effectivity**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for approvals, permission deltas, notifications, and history ingredients.
Resilio remains on the non-clone side for the fairness-critical effectivity model.

The reason is now precise:

> current Resilio docs still expose approvals, permission changes, notifications, and general history as separate operational surfaces rather than one typed enactment lifecycle for `drafted`, `executed`, `noticed`, `effective`, `contest-open`, `superseded`, and `withdrawn`, so the operator still has to reconstruct effectivity from scattered traces instead of one owned interface family.
