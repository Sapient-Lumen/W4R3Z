# Resilio dormant-return, re-entry, and stale-claim fragmentation evaluation

## Purpose

The archive already had freshness invalidation, next-observation opportunity, source-witness work, chronology-confidence review, and resume catch-up.
What it still lacked was the next ordinary operator answer:

> this seat or subject came back after dormancy; is this an ordinary healthy return, a chronology-risky re-entry, a hidden roster reappearance, or a stale announcement that still is not safely trustworthy?

Current official Resilio docs are candid enough that AnonSync needs a tighter answer.
Resilio does not pretend all returns mean the same thing.
It separately documents hidden-but-still-linked offline devices, offline peer expiration, restart/reopen re-indexing, offline edits that can overwrite later online work, clock/timezone invalidation, and ghost announcements that no peer still has as full bytes.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- a device that was hidden from the roster is not necessarily unlinked forever and can reappear when it comes back online
- a peer row that aged out of the ordinary list after 7 days is a different truth from a seat that never existed
- shutting down and later reopening can be a chronology-shaping event rather than a cosmetic resume
- offline local edits can outrank or overwrite changes made by peers that stayed online if chronology trust is weak
- invalid clocks or timezones make stale-return interpretation unsafe and can even leave mobile peers showing empty file lists
- some returning demand is only a ghost announcement because the subject was advertised earlier but no peer now retains full source bytes

This is better than products that flatten every comeback into one green `online again` story.

## What still should not be cloned

The re-entry contract is still scattered and too article-shaped.
Current official Resilio docs still require the operator to combine at least six different article families:

1. **Does Sync work in background?** for the fact that shutdown/re-open reindexes folders, gives them a new modification time, and can let offline edits overwrite changes made by peers that remained online.
2. **Sync Main View (Desktop)** for the fact that offline peers remain counted for a while and then are disconnected from the folder after 7 days.
3. **Power user preferences** for the fact that the offline-peer aging rule is actually a tunable `peer_expiration_days` setting whose default is 7 days.
4. **How to clear offline devices? (desktop only)** for the fact that clearing an offline device only hides it from view and it can reappear later without being unlinked.
5. **"Time difference" error** for the fact that chronology trust fails once peer time or timezone drift exceeds 600 seconds and that mobile peers may then show empty lists.
6. **Cannot download files / There are no source peers online for too long time** for the fact that some announced files are actually stale ghosts that nobody still has in full.

Historical changelog notes make the seam look even more like a durable contract issue rather than a one-off typo:

- historical published fixes still include reconnect-after-long-offline breakage and inability to download from a reconnected peer in some cases
- the maintained v3 line still runs through `3.1.2.1076`

That means one ordinary answer is still reconstructed from several places:

- whether the returning seat is merely visible again or actually trustworthy again
- whether dormancy changed chronology confidence enough to block ordinary `latest` language
- whether the returning seat still has full source bytes for the announced subjects
- whether the safest move is observe, quarantine, repair time, verify source reality, or widen review
- what exact sentence is safe right now: `ordinary wake`, `stale return under review`, `clock-invalid re-entry`, or `announcement persists but source is gone`

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat three follow-on mistakes after it already learned to model freshness budgets and late-claim gates:

1. **false normality** — treating a returning seat as ordinary healthy participation before dormancy, clock trust, and source reality are checked
2. **false disappearance** — treating a hidden or aged-out roster entry as gone forever when it may simply reappear later
3. **false freshness** — treating old announcements or offline edits as ordinary current truth when chronology or source reality has changed

A serious sync product now needs one stable public answer to four follow-up questions:

- **dormancy truth** — how long was this seat or subject effectively absent, hidden, or uncertain?
- **re-entry truth** — what exact kind of return is this?
- **continuity truth** — what chronology and source claims are still safe after the return?
- **action truth** — is the cheapest honest move to trust, quarantine, repair clocks, verify source, or escalate?

## Replacement pages in this revision

This revision adds four fixed pages:

- `807` — Re-entry case page
- `808` — Dormancy timeline page
- `809` — Stale-return review page
- `810` — Re-entry receipt

Together they make `what exactly came back, and how trustworthy is that return?` explicit before AnonSync lets `online again`, `latest`, or `should catch up now` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid separation of hidden-offline, aged-out, re-opened, clock-invalid, and ghost-announcement situations
- candid admission that dormancy can change chronology trust rather than merely delay transfer
- candid use of roster aging, clock validity, and source-bytes reality as real facts rather than cosmetic badges
- candid preservation of the possibility that a hidden device may still come back later

Do not clone from Resilio:

- leaving stale-return meaning split across background, main-view, identity, clock-error, and source-unavailable articles
- letting `online again` or `peer visible` masquerade as `safe to trust again`
- making operators infer whether a return is harmless, stale, dangerous, or merely incomplete
- leaving no durable receipt of dormancy facts, chronology confidence, source reality, and reopen conditions

## Evaluation summary

Resilio still deserves credit for naming the ingredients of a stale return.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `this thing came back after dormancy; what exactly returned, what stayed uncertain, and what stronger sentence is still forbidden?`

AnonSync should therefore make **re-entry after dormancy** a first-class product object.
Every serious long-offline return, hidden-device reappearance, clock-invalid comeback, or ghost-announcement aftermath should publish dormancy facts, return class, chronology confidence, source-reality verdict, strongest allowed sentence, and forbidden stronger sentence before the product treats the state as ordinary again.
