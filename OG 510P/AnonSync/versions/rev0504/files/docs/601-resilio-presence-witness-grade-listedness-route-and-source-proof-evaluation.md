# Resilio presence-witness grade, hidden-listed peers, and source-proof evaluation

## Why this pass exists

The archive already had member presence, network eligibility, pause truth, subject non-arrival, and witness locality work.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can this share transfer right now` or `why is this subject absent`.
It is now:

- whether a peer is merely **listed historically** or actually **online now**
- whether an online-looking peer is actually **eligible to participate** or is paused, forbidden-network, or sleeping
- whether a subject has a **current byte source** rather than only a route-visible or placeholder-only peer
- whether hiding an offline device changes authority or merely changes the list
- what durable receipt proves the strongest sentence the product is allowed to make about current presence

That seam is still materially real in current official Resilio docs.
They still say the desktop main view shows `X of Y peers`, with `X` as online peers and `Y` as total peers including offline ones, and that offline peers disconnect after 7 days unless power-user settings change it.
They still say clearing an offline device only hides it from view and does not unlink it, and that it reappears if it comes back online.
They still say linked devices show green/grey dots for online/offline and selected sync mode.
They still say a switched-off source device cannot sync because there is no cloud intermediary.
They still say `Stopped. Forbidden network` blocks peer connection and change detection for that share, and that Auto-sleep can make peers stop seeing the device online.
They still say ghost-file warnings occur when peers announced a subject but nobody currently has the full bytes anymore.
The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary sentence `what is actually present enough for me to trust this peer row or this subject row right now?` split across main-view, identity, hide-offline, mobile network, auto-sleep, pause, switched-off, and ghost-file docs.

## What current Resilio gets right

Current official docs still deserve credit for saying plainly that presence is not one bit.
They still distinguish several materially different truths:

- a peer can be in the `Y` total because it has been connected before without being online now
- a device can be hidden from the operator's list without being unlinked or revoked
- a green/grey dot is about current connection, not necessarily byte-source sufficiency for every subject
- a share can be visible yet stopped by forbidden-network policy or by sleeping-core state
- a subject can still be announced in the tree even after no peer retains the full bytes
- a switched-off device cannot act as a source because the system is peer-to-peer rather than cloud-backed

That is better than flattening everything into `online` or `missing`.
AnonSync should keep that candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct one ordinary answer from several pages:

- `Sync Main View (Desktop)` explains that `X of Y peers` mixes online-now with historical total peer count.
- `Sync Private Identity & Linking My Devices` explains green/grey dots and linked-device modes.
- `How to clear offline devices?` explains that hidden offline devices are not unlinked and can reappear.
- `Setting network interface per share`, `Settings on mobile platforms`, and `Configuring Auto Sleep & Battery Saver (Android)` explain why a visible share or device may still be ineligible or unseen.
- `How to pause syncing` explains that paused state still allows some non-payload effects.
- `Cannot download files / ... no source peers online for too long time` explains ghost announcements and placeholder-only source loss.
- `Will my devices still sync when switched off?` explains that a source must actually be online.

The operator therefore still has to do archaeology to answer a simple question:

> do I merely see historical membership, or do I have current eligible presence and a real byte source for this subject?

## Why this is a strong non-clone reason

This is not a cosmetic peer-list issue.
It changes the product's claim ceiling.
Without a first-class presence-witness object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `this peer is here` when it is only historically listed or hidden-offline
- `the device is online enough` when the share is actually forbidden-network or sleep-blocked
- `someone has the file` when the tree only has a ghost announcement and placeholders remain
- `the share is gone` when the device was only hidden from view and may return
- `this row proves recoverability` when no current byte source exists on any present peer

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a contract where presence meaning remains scattered across peer lists, mode dots, mobile settings, sleep policy, and ghost-file warnings.
It should instead make **presence witness grade** first-class.

That means every serious peer row or source-availability warning should publish, in one stable reviewed object:

- peer listedness grade
- route / connection witness grade
- policy eligibility grade
- source-byte witness grade for the subject in question
- strongest safe sentence
- stronger forbidden sentence
- next observation that would strengthen or weaken the claim

## New page family required

This pass therefore adds four explicit replacements:

1. **Presence witness** — what kind of presence proof exists right now for this peer/share/subject.
2. **Peer presence review** — whether a peer is listed, online, hidden, disconnected, sleeping, paused, or merely historical.
3. **Subject source witness** — whether any currently present peer still has the full bytes, only placeholders, or no source at all.
4. **Presence witness receipt** — durable safe language and next observation basis.

## Condensed design verdict

Borrow Resilio's candor that listedness, online dots, network eligibility, sleeping-core state, and current byte-source availability are materially different truths.
Do not clone a product contract where operators still have to reconstruct from several help pages whether a peer row or subject row is present enough to justify a strong action or statement.
