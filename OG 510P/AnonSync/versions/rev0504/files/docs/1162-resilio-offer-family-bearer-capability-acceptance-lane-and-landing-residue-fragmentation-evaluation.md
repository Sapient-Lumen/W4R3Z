# Resilio offer-family, bearer-capability, acceptance-lane, and landing-residue fragmentation evaluation

## Why this pass exists

The archive already had serious work on share artifacts, browser handoff, bounded file handoff, and redemption lanes.
What the latest revision chain still lacked was one tighter current Resilio pass about a more ordinary operator question:

> what exact offer family am I issuing or claiming here, what proof or approval does it require, how does it arrive, and what local landing or residue contract comes with it?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Sync Share Dialog (Desktop)` still says **Advanced** folders share by link or QR with permission choices, while **Standard** folders also expose **Key**, and the major difference is that **keys do not have the approval mechanism**.
- the same current share-dialog docs still say link issuance can require approval for **only new peers** or for **all peers**, and can attach an expiration period after which no new peers can connect with that link.
- `Sharing single file` still says a file share is basically a **data transfer operation**, can contain one or a few files, defaults to **3 days** expiry, can be made non-expiring on desktop, and is **one-time one-way** rather than live sync.
- that same current single-file article still says **everyone who gets the generated link can download**, there is **no option to restrict the number of usage or ban some devices**, recipients can share the received files further, and changed files require a **new link**.
- `Sync doesn't start when opening Link in browser` and `Configuring WebUI` still say browser handoff can fail and that WebUI cannot claim a clicked link directly, forcing manual `+ -> Enter a key or link`.
- `Sync Preferences` still says single-file arrival has its own **default file location** on desktop.
- `Sharing files (Android)` and `Sharing files (iOS)` still show mobile single-file flow as a distinct lane with **3-day links**, QR receive, opinionated inbox surfaces, and distinct removal behavior between transfer rows and landed bytes.
- current single-file and mobile docs still say same-name destination collisions can create **`(1)`** suffixes and that removing a transfer from UI is not always the same as removing the landed bytes from the device.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that not every share artifact is the same family

Current docs still preserve useful differences among:

- Standard-folder keys
- folder links
- QR delivery
- single-file transfer links
- mobile carrier flows
- browser-opened links versus manual paste

That honesty is useful.

### 2) It admits that approval and openness are not the same

Current docs still make plain that:

- some links may require approval
- some remembered peers may bypass reapproval depending on policy
- Standard keys do not carry the same approval gate
- single-file links are effectively bearer offers with no usage-count ceiling or device ban

That is product-shaping truth.

### 3) It admits that arrival and residue differ by lane

Current docs still say receive location, collision outcome, transfer-list residue, and byte residue vary across desktop, WebUI, Android, and iOS.
That is contract truth, not UI trivia.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many articles

To answer `what exactly am I giving out here and how will it land there?` the operator may still need to combine:

- desktop share dialog
- single-file sharing
- browser-link troubleshooting
- WebUI configuration
- desktop preferences
- Android sharing
- iOS sharing
- power-user preferences

That is too much archaeology for one ordinary action.

### 2) `Share`, `Copy link`, `QR`, and `Enter a key or link` still compress different contracts

Those gestures can hide:

- approval requirement
- bearer openness
- expiry authority
- usage-cap absence
- one-way snapshot semantics
- destination-path authority
- name-collision outcome
- row-vs-byte residue differences

AnonSync should not inherit that compression.

### 3) landing and residue truth still arrives late

Current Resilio docs still make the operator discover after the fact that:

- a single-file receive is not a live subject
- a clicked link may fail only because handoff failed
- WebUI requires manual paste
- mobile UI removal can differ from device-byte removal
- same-name landings may silently suffix `(1)`

AnonSync should surface those truths before issuance or claim.

## Hard decisions for AnonSync

This pass freezes five decisions.

### Decision 1 — offer family is first-class product state

AnonSync should model at least these reviewed families:

- **governed folder grant**
- **approval-capable folder link**
- **approval-free key artifact**
- **bounded file-transfer offer**
- **manual-intake fallback artifact**

### Decision 2 — approval posture and bearer openness stay separate

`has a link` must never imply `is identified`, and `requires approval` must never imply `usage-limited`.

### Decision 3 — claim lane is weaker than claim success

Browser handoff, QR scan, manual paste, and WebUI entry are different intake lanes and must stay visible.

### Decision 4 — landing truth stays separate from offer truth

Offer family, destination authority, collision rule, and residue behavior are four separate truths.

### Decision 5 — receipts must preserve the blocked stronger sentence

Every serious offer issuance or claim should end with one receipt that can still say:

- what family the artifact really was
- what approval or openness posture applied
- how it was claimed
- where bytes landed
- what remained after UI cleanup
- which stronger sentence was rejected

## Replacement page family

This pass therefore adds five more ordinary product-owned pages:

- **Offer family contract sheet**
- **Bearer capability review**
- **Acceptance lane review**
- **Landing and residue review**
- **Offer-family lineage receipt**

## Bottom line

Resilio's current docs deserve credit for admitting that folder links, keys, QR flows, single-file transfer links, browser handoff, mobile receive lanes, and landing residue are materially different.
But AnonSync should still refuse any contract where the operator must stitch together several articles to answer:

> what did I actually issue, how open was it, how will it be claimed, where will it land, and what survives after the row disappears?
