# Resilio action-matrix, threshold, and irreversible-act fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `Read Only`, `Read & Write`, `Owner`, linked-device Owner inheritance, source/local-share inheritance, revocation, and approval behavior are not one flat capability.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than coalition sufficiency:

> after the product knows who is valid and how many signers are enough, it still needs one first-class answer to **what exact act that coalition is sufficient to perform right now**.

Current Resilio materials still do not provide one typed action matrix for:

- acknowledge receipt of payment
- accept provisional settlement
- waive disputed or undisputed residue
- lift probation
- restore future-burst eligibility
- reopen a case after new evidence
- delegate or narrow authority
- appoint or ratify a successor

Instead, the operator still has to translate broad share permissions and folder-governance asymmetries into action-level meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `Sync Share Dialog (Desktop)` still says Advanced folders offer `Read Only`, `Read & Write`, and `Owner`, while Standard folders have no Owner level and peers can share the key onward.
- `User Management` still says only Owners can invite peers to Advanced folders, change permissions on the fly, and revoke access, while linked devices under one identity all act as Owners.
- `Sync functionality in detail` still says Owners can read, update, share the folder, change permissions, and revoke access, and that linked devices can approve access from any linked device.
- `What's the difference between Standard and Advanced folders?` still says Standard folders have no Owner concept, on-the-fly permission changes are unavailable there, and any peer can share the key without limitation.
- `How to create a Read Only folder while syncing across linked devices?` still says My Devices automatically sync folders to linked devices with Owner permission.
- `Sharing a folder locally` still says local shares cannot be granted Owner permission and inherit at most the source share's access level, while some permission changes require remove-and-reshare.
- `Disconnecting and Removing Folders` still says local identity-linked removal and remote retention can diverge.

This is strong operational candor.
It is not a first-class action matrix.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and UI surfaces:

- a broad role label like `Owner`
- whether the path is Advanced, Standard, linked-device, or local-share
- whether the action is protective, reversible, or irreversible
- whether the action narrows, preserves, or extinguishes future rights
- whether the action affects only this actor's slice or the whole creditor case

That means current official materials can help answer `can this peer share or revoke access to a folder?`
They still do not directly answer `can this coalition merely receive payment, or can it also waive residue, lift probation, normalize future burst, appoint a successor, or extinguish reopen rights?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- crisp role labels
- explicit inheritance ceilings
- explicit onward-share and revoke powers
- visible asymmetry between richer and poorer governance modes

But AnonSync should replace the page contract with a first-class **action authority matrix** where each action family has its own:

- action kind
- reversibility class
- minimum coalition threshold
- residue scope touched
- cooling or contest window if irreversible
- successor or countersign requirement if any
- reopen rule after execution

## Product decision tightened here

The new design line is:

- **coalition sufficiency is weaker than action sufficiency**
- **protective acts and irreversible release acts must not share the same threshold by default**
- **no broad role label may silently imply power for every stronger action**
- **the strongest sentence must always be attached to a typed act, not inferred from prestige of signer or role**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for identity, owner, approval, and inheritance ingredients.
Resilio remains on the non-clone side for the fairness-critical act model.

The reason is now precise:

> current Resilio docs still expose broad operational permissions rather than one typed action matrix for `receive`, `settle`, `waive`, `lift`, `normalize`, `delegate`, `succeed`, and `reopen`, so the operator still has to reconstruct action-level fairness from scattered role and share surfaces instead of one owned interface family.
