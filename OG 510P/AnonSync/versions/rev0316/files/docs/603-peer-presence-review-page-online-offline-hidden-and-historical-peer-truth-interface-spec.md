# Peer presence review page — online, offline, hidden, and historical-peer truth interface spec

## Purpose

The archive already had membership and network-policy language.
What it still lacked was one exact page for the operator question:

> what does this peer row really mean right now: live peer, hidden peer, sleeping peer, paused peer, or merely historical peer memory?

## Core decision

Any non-trivial peer roster entry must compile to one first-class **Peer presence review** page.
That page is the semantic home of:

- current roster meaning
- live-connection witness
- hidden-vs-unlinked distinction
- pause / sleep / forbidden-network overlays
- strongest safe sentence and next reappearance basis

## Primary page layout

The page always renders the same top-level regions in the same order:

1. presence verdict strip
2. roster meaning card
3. live-witness card
4. overlays card
5. reappearance / receipt card

### 1) Presence verdict strip

Show:

- peer label
- current peer presence class (`live`, `listed-offline`, `hidden-offline`, `sleep-offline`, `paused-limited`, `historical-only`, `unknown`)
- strongest honest one-line summary

Allowed summaries:

- `Peer is connected now and visible in the roster`
- `Peer is hidden from view but not unlinked; it may reappear if it comes back online`
- `Peer is listed historically but currently disconnected`
- `Peer is online as a device, but this share is ineligible on the current network`
- `Peer is offline because the core is sleeping`

### 2) Roster meaning card

Show:

- whether the row comes from current connection or historical total
- whether the peer was hidden by the operator
- whether offline-aging or expiry settings may have changed roster visibility
- whether unlink or severance has actually occurred

The operator must be able to answer:

> is this row about current presence or only historical membership memory?

### 3) Live-witness card

Show:

- current connection witness
- last-confirmed online observation if known
- sync/posture mode for linked peers
- whether the connection evidence is direct, inferred, stale, or absent

### 4) Overlays card

Show rows for overlays that change how presence should be read:

- pause state
- share forbidden-network state
- seat mobile-data block
- auto-sleep / battery stop
- switched-off / no-core state

For each row show:

- applies now?
- strongest narrowed effect
- strongest unaffected nearby truth

### 5) Reappearance / receipt card

Show:

- whether automatic reappearance is expected
- what event would bring the peer back to live presence
- what event would actually remove or sever it instead
- resulting receipt class

## Behavior rules

- This page must appear whenever a peer row could otherwise overstate live participation.
- The product must not let `Hide device` read like `unlink` or `revoke`.
- The product must not let `online` read like `eligible for every share`.
- A stale or historical roster entry must visibly lose to fresher route evidence.

## Compact row contract

A compact row should preserve this order:

1. peer presence class
2. live witness freshness
3. most important overlay
4. strongest safe sentence
5. next reappearance basis

## Non-clone reason

Current official Resilio docs are candid about online dots, historical totals, hidden offline devices, forbidden-network stoppage, and auto-sleep.
AnonSync should keep the candor but own the review directly instead of leaving meaning split across roster, identity, and mobile help pages.
