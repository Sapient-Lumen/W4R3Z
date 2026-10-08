# Resilio acknowledgment, assent, and reader-identity fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `notification`, `approval`, `linked device`, `owner`, `identity`, `certificate memory`, and `history` are not one flat assent truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than publication recall and reach:

> after the product knows **what was published, corrected, or withdrawn and which audiences were reached**, it still needs one first-class answer to **who merely received a signal, who actually opened the material, who acknowledged it, who assented to be bound by it, and whether that happened as a person, a device, a linked identity, or a folder-owner role**.

Current Resilio materials still do not provide one typed acknowledgment object for:

- distinguishing bell-visible notification from message-open proof
- distinguishing any-device approval from named-person acknowledgment
- distinguishing actor-attributed assent from identity-level or device-level convenience actions
- distinguishing fresh assent from remembered certificate trust or prior approvals
- showing when a linked-device owner action is enough for operational sync but still too weak for fairness-grade assent
- preserving who was merely notified versus who actually accepted an obligation, correction, or waiver
- proving when a stronger `personally acknowledged` or `binding assent` sentence remains blocked

Instead, the operator still has to translate linked-device approvals, owner permissions, synchronized notifications, and short-horizon history into assent meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Main View (Desktop)` still says the bell lights up for approval requests or other notifications and that History shows only general syncing activity for the last 30 days.
- `Sync Private Identity & Linking My Devices` still says all folders become visible and accessible on all linked devices and that a folder access request can be approved from any device where the folder is present in Selective Sync or Synced mode.
- `Sync functionality in detail` still says you can approve connections from any of your linked devices, not only the device that shared the folder initially, and that prior approval can be retained by certificate unless a folder is configured to require approval for every peer.
- `User Management` still says all linked devices under one identity act as Owners when sharing across your own linked devices.
- `Resilio Sync change log` still says notifications are synchronized across linked devices and that history is searchable and sortable.
- `How to create a Read Only folder while syncing across linked devices?` still says My Devices gives linked devices Owner permission by default, and that you must deliberately step outside that path to create a read-only posture on a linked device.

This is strong operational candor.
It is not a first-class acknowledgment-and-assent contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether a person merely had a notification available somewhere or actually opened the relevant material
- whether an approval executed from one linked device should count as person-specific assent or only identity-level operational permission
- whether owner capability is enough for the exact typed act, especially after corrections, waivers, or narrowed reliance rules
- whether a remembered certificate or prior approval is standing in for fresh acknowledgment of this version of the act
- whether a searchable history row proves awareness, or only that some operational event occurred
- whether synchronized notifications across devices collapse reader identity instead of clarifying it

That means current official materials can help answer `can this peer connect`, `can an owner approve`, or `will notifications appear across linked devices`.
They still do not directly answer `who actually saw this act, who acknowledged it, who assented to it, and in what capacity?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit linked-identity and device-identity modeling
- explicit owner / permission and approval routes
- visible notification surfaces
- searchable event history
- certificate and approval-memory candor

But AnonSync should replace the page contract with a first-class **acknowledgment and assent** object where each typed act has its own:

- recipient class and named-reader target set
- open-proof requirement
- acknowledgment requirement
- assent requirement
- actor-capacity requirement
- fresh-vs-remembered approval basis
- stronger blocked consent sentence
- acknowledgment lineage receipt

## Product decision tightened here

The new design line is:

- **notification delivered is weaker than message opened**
- **message opened is weaker than acknowledged understanding**
- **acknowledged understanding is weaker than assented obligation**
- **linked-identity or owner action is weaker than person-attributed assent unless that exact substitution is authorized**
- **remembered certificate trust is weaker than fresh assent to this act version**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for identity, owner, approval, notification, and event-trace candor.
Resilio remains on the non-clone side for the fairness-critical acknowledgment-and-assent contract.

The reason is now precise:

> current Resilio docs still expose bell notifications, any-device approvals, linked-device owner powers, retained certificate trust, and searchable history as separate operational facts rather than one typed assent object for `notified`, `opened`, `acknowledged`, `assented`, `actor capacity proven`, and `fresh assent still blocked`, so the operator still has to reconstruct whether anyone actually understood and bound themselves from scattered traces instead of one owned interface family.
