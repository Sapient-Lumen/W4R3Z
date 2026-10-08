# Resilio admission-instrument, approval-memory, and credential-afterlife fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `Comprehensive guide to syncing` docs still separate linked-identity automatic sharing from manual per-folder sharing via key, link, or QR code
- current `Sync Share Dialog (Desktop)` docs still say Standard folders support keys while keys differ from links specifically by approval mechanism
- those same current share-dialog docs still say links can require no approval, approval for only new peers, or approval for all peers on every new shared folder, and that links can also expire by time or by allowed use count
- current `Link structure and flow` docs still say the link carries a temporary key and expiration, and that link parameters are placed after the hash symbol and are not sent to Resilio server
- those same link-flow docs still say a joining peer sends a locally generated public key, the owner reviews the fingerprint, then generates an X509 certificate and signs an ACL entry granting access
- current `Key structure and flow` docs still say key changes are not distributed automatically: old-key peers continue syncing with each other and stop syncing with the peer that changed the key

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **what exactly was sent: a durable key, an expiring link, or only a QR rendering of one of those?**
2. **does the instrument itself require approval, and if so whose memory of prior approval still counts?**
3. **when is access merely requested versus actually granted by certificate and ACL issuance?**
4. **what does expiry actually kill: the invitation path, the already-issued credential, or neither?**
5. **what happens after local key rotation: does the whole cohort move, or does the mesh split into old and new admission lineages?**

Current Resilio docs still spread those answers across the manual-sharing guide, share dialog, key architecture, and link-flow explanation.

So a user can learn all the pieces and still not get one stable product answer to:

> what admission instrument exists here, what join gate it really implies, what durable credential got minted later, and what remains true after expiry, approval reuse, or key change?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow six habits directly:

- **say openly when transport wrapper and credential class are different truths**
- **say openly when approval is bypassed by instrument choice rather than by explicit policy grant**
- **say openly when QR is only a presentation form and not its own authority class**
- **say openly when a clicked link still has not granted access because certificate issuance has not happened**
- **say openly when link expiry blocks new joins but says nothing by itself about already-issued credentials**
- **say openly when local key rotation creates a lineage split rather than a cohort-wide migration**

But AnonSync should reject six weaker habits:

- one generic `shared` sentence that hides whether the operator sent a key or a link
- one generic `invite expired` sentence that hides whether existing access survived
- one generic `approved` badge that hides whether certificate issuance and ACL install actually completed
- a QR affordance that implies new authority instead of mere representation
- key-rotation language that implies everyone moved when only one peer changed
- join-state language that forces the operator to stitch together flow, approval memory, and credential afterlife from multiple pages

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1271` — Admission-instrument contract sheet
- `1272` — Join review
- `1273` — Grant-issuance proof
- `1274` — Credential-afterlife timeline
- `1275` — Admission-instrument lineage receipt

These pages keep the Resilio candor and reject the scattered-admission-contract problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that automatic identity linking, keys, links, QR rendering, approval memory, certificate issuance, and local key rotation are different truths; refuse any interface contract where the operator must reconstruct `what admission path exists here, when access became durable, and what survives expiry or key change?` from several help articles instead of one explicit admission-instrument object.
