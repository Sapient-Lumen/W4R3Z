# Detachment and revocation contract sheet page: action class, authority scope, and residue interface spec

## Purpose

The archive already has pages for seat posture, reachability provenance, operator attestation, and presence.
What it still lacked was one ordinary page for the narrower question:

> when an operator clicks hide, disconnect, remove, unlink, revoke, or uninstall, what exactly changes in authority, visibility, byte residency, and roster residue?

Current official Resilio docs make this seam concrete.
They separately describe hiding offline devices, disconnecting folders, removing folders from linked devices, peer-level revocation, self-unlinking, and uninstall cleanup residue.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Detachment and revocation contract sheet** whenever an action materially changes a relationship between a seat, a subject, and a roster record.

The sheet exists to answer six things in one place:

1. what detachment or revocation class is being performed
2. who has authority to perform it
3. what future updates or approvals it actually cuts off
4. what bytes or placeholders remain after the action
5. what roster or storage residue survives
6. what stronger sentence remains blocked

## Fixed page order

1. **Detachment header**
2. **Authority and scope card**
3. **Future-update boundary card**
4. **Residue card**
5. **Reappearance / reactivation card**
6. **Commit rail and blocked stronger sentence**

### 1) Detachment header

Show at minimum:

- `detachment_contract_id`
- actor handle
- subject ref or peer ref
- action class
- scope (`record-only`, `single-seat`, `selected-peer`, `linked-family`, `installation`, `identity`, `unknown`)
- strongest safe sentence
- stronger blocked sentence
- freshness of latest roster and byte observations

Supported action classes must include:

- `hide-roster-record`
- `disconnect-local-subject`
- `revoke-selected-peer-updates`
- `remove-linked-family-subject`
- `unlink-local-seat-from-identity`
- `uninstall-runtime`
- `certificate-takeover-rebind`

Example safe sentence:

- `Selected peer is cut off from future updates, but previously landed bytes remain outside this action's reach.`

### 2) Authority and scope card

Separate explicitly:

- who can perform the action
- what object is targeted
- whether the action is local-only or propagating
- whether it operates through identity membership, folder membership, or installation presence
- whether offline peers are still affected later

The operator must be able to answer:

> whose authority is this, and over what boundary does it actually apply?

### 3) Future-update boundary card

Show one row for each affected class:

- future metadata announcements
- future byte transfer
- future approval rights
- future appearance in linked-device rosters
- future automatic reconnect / rediscovery

Each row must show:

- `continues`
- `suspended`
- `revoked`
- `unknown`

The operator must be able to answer:

> what stops happening after this action, and what still can happen?

### 4) Residue card

Separate these residue classes explicitly:

- ordinary local bytes
- placeholder residue
- archive/service residue
- peer-list / device-list record residue
- remote-byte survivor scope
- identity / certificate residue

Each row must show whether the residue is preserved, removed, hidden, or not yet observed.

The operator must be able to answer:

> what is still around after the action, even if the UI looks cleaner?

### 5) Reappearance / reactivation card

This card must show whether the object can come back and how:

- cleared record reappears when the same device goes online again
- disconnected folder reconnects to the same or a new path
- removed linked-family folder survives on unlinked remote peers
- unlinked or uninstalled seat may remain as stale roster evidence elsewhere
- certificate takeover may replace app-visible objects without proving byte deletion

The operator must be able to answer:

> can this come back, and does that require a new explicit grant?

### 6) Commit rail and blocked stronger sentence

Allowed examples:

- `Hide stale roster record`
- `Disconnect local subject only`
- `Revoke selected peer from future updates`
- `Remove from linked family`
- `Unlink local seat`
- `Begin uninstall with residue review`
- `Export detachment receipt`

Blocked examples:

- `No one has the bytes anymore.`
- `This peer can never reappear.`
- `All access everywhere is revoked.`
- `Uninstall cleared every trace.`

## What this page prevents

Without this page, the product quietly conflates decluttering, future-update suspension, byte removal, and trust severance.
AnonSync must instead publish one effective detachment sentence with one visible claim ceiling.
