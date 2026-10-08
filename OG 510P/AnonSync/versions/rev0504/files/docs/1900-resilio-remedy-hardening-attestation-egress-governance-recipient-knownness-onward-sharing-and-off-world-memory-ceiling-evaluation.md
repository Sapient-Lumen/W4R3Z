# Resilio remedy hardening attestation egress governance, recipient knownness, onward-sharing, and off-world memory ceiling evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being fairly candid that sharing is not one flat lane.
That candor matters.

The strongest current ingredients are:

- current `Link structure and flow` docs still say folder sharing commonly travels by a link and that the receiving peer uses the temporary key in that link to request access from the owner
- current `Sync Share Dialog (Desktop)` docs still say links can be copied to clipboard or sent through e-mail and messenger, approval can be required for only new peers or for all peers, and an unchecked approval option lets a peer who gets the link connect and start syncing automatically
- the same share-dialog docs still say Advanced-folder Owners can share with other peers, while Standard folders have no Owner gate and all peers can share the folder further
- current `What's the difference between Standard and Advanced folders?` docs still say Standard-folder peers can share the key they have without any limitations
- current `User Management` docs still say Owners can invite new users to the folder and that all linked devices under one identity act as Owners
- current `Sync Private Identity & Linking My Devices` docs still say once a remote user approves one device they can choose to auto-approve all linked devices for future sharing
- current `Sharing single file` docs still say everyone who gets the generated link can download the shared files, there is no option to restrict number of usages or ban some devices, recipients can share the files further, and expiration can be disabled so the link never expires
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say keys or links can simply be copied to clipboard and sent using any convenient and trusted way
- current `Disconnecting and Removing Folders` docs still say even after removal from linked devices the folder may still remain on other remote devices not linked to the personal identity

Those are useful truths.
They still do not add up to one typed answer to:

> `after a ruling was corrected and our governed worlds were cleaned up, who outside governance might still hold it, who could further spread it, and what is the strongest honest global sentence we can still say?`

## Where the current contract still fragments

The problem is not that Resilio hides sharing.
The problem is that current outward-spread truth is still scattered across share dialogs, key versus link differences, owner privileges, linked-device trust expansion, file-send behavior, and remove/disconnect limits instead of being owned as one case-scoped off-world ceiling contract.

Today an operator can often infer only weaker truths such as:

- a link was generated once
- some peers probably received or used it
- one approval gate existed at one point
- one recipient may have had onward-share rights
- one single-file link may have been effectively public to whoever obtained it
- one Standard key may still be portable without owner oversight
- one linked family may silently widen future approval scope
- one removal affected governed devices but not all remote holders

Those are important clues.
They are not the same as an explicit answer to `which egress lanes existed, which recipients are actually known, which onward-sharing rights existed, which disclosures are still revocable versus irrevocable, which off-world copies remain merely suspected, and what stronger global-forgetting sentence must remain blocked forever or until named evidence appears?`

## Why that matters for AnonSync

AnonSync needs stronger language than `we erased our copies` or even `governed cohort is resurrection-resistant`.
It needs to support claims such as:

- the governed cohort is clean, but one historical share lane used a forwardable key whose downstream holders were never fully enumerated
- all named recipients were notified and governed copies were erased, but one earlier Owner could have reshared before revocation and that downstream tree remains only partially known
- a file-send link expired for new downloads, but previously delivered recipients can still hold or resend the bytes
- the strongest honest sentence is `off-world memory ceiling unknown`, not because the product failed to clean up its own world, but because the original egress posture was intentionally wider than later governance can prove away
- a case is safe for current governed use and even resurrection-resistant for the required cohort, while `globally forgotten` remains permanently blocked by historical externalization risk
- one explicit, case-owned receipt should preserve that ceiling so later operators do not accidentally overstate what revocation or erase work achieved

AnonSync therefore needs first-class objects for **egress-lane inventory, recipient-knownness class, onward-sharing authority, revocation reach ceiling, external-holder suspicion class, off-world memory ceiling, and blocked global sentence** rather than leaving operators to reconstruct that truth from share menus, permission prose, link TTLs, and removal caveats.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `who outside governance may still hold, forward, or remember this, and how global can our forgetting sentence honestly be?` — only by making the operator combine several partially overlapping operational surfaces:

- link flow and landing-page mechanics
- approval settings that differ between new peers and all peers
- copy-to-clipboard and messenger delivery paths
- Owner or Standard-key onward-sharing rights
- linked-device auto-approval expansion for future sharing
- file-send links that may never expire and cannot be usage-limited
- disconnect or removal behavior that stops short of clearing unlinked remote holders

That is enough to justify a harder product stance:

> AnonSync is not cloning Resilio because governed-world cleanup is not the same thing as off-world closure, and current externalization truth is still reconstructed from sharing mechanics and permission articles instead of owned by one stable page family that says which egress lanes existed, who is known to have received them, what onward-sharing power existed, what can still be revoked, and which stronger global sentence is permanently blocked.
