# Contact, link, approval, and succession spec

## Purpose

This document makes one narrow but important interface seam explicit:

- how AnonSync remembers peers and relationships
- how unknown or newly introduced peers are staged before trust
- how future approval is bounded instead of ambient
- how device succession carries forward only the right continuity

The archive already had devices, links, approvals, retirements, and stewardship records.
What it still lacked was one joined-up specification for how those pieces fit together as an operator contract.

## Why this needs its own spec

Resilio's official docs describe a powerful convenience model:

- linked devices automatically make all folders available across the linked set
- all of your own linked devices act as Owners
- a remote user can choose to automatically approve all of your linked devices for future sharing after approving one
- any linked device with the folder already active can approve a new peer
- linking two already-initialized devices can cause one device to lose its certificate and take over the other's configured shares

Those behaviors solve real friction.
They also show exactly why AnonSync should separate contact, link, grant, approval, and succession.
Otherwise “personal mesh convenience” quietly turns into broad standing authority.

Syncthing is useful here as a narrow counterexample, not as a whole product template:

- introducer behavior is explicit instead of ambient
- pending remote devices are first-class records in the API
- those pending records can later be removed, while durable ignore belongs in configuration

That validates two ideas this archive should keep:

- pending peer admission is a real interface seam
- bounded introductions are a real policy seam

## Core rules

### 1) Contact is not grant

A remembered peer relationship does not itself authorize any share, route, or local path adoption.
A contact may be trusted without having any current grant.

### 2) Linking is not identity merger

Linking may create a personal-device constellation and install policies.
It must not overwrite the local identity or silently absorb the full state of another initialized device.

### 3) Unknown peers land in a queue first

A new or newly introduced peer should first appear as a pending-peer record.
From there the operator can:

- trust it as a contact
- link it into a constellation
- accept a specific share claim
- dismiss it for later review
- ignore or quarantine it durably

### 4) Future approval is a bounded object

Approval memory is real user value.
But it should be a supported object with explicit:

- scope
- approver set
- maximum role
- expiry
- last-use facts

### 5) Introductions are explicit policy

One trusted device may be allowed to surface additional peers, but that policy must say whether it can only create pending records or can do anything wider.
The default should stay conservative.

### 6) Succession is reviewed continuity

Replacing a dead or stolen device should not require re-sharing everything.
But neither should successor continuity silently inherit every remembered approval or relationship.
The operator should review what carries forward.

## Supported objects

### Contact record

A durable relationship-memory object.

Fields:

- `contact_id`
- `relationship_class` (`self-device`, `known-peer`, `collaborator`, `unknown`)
- `contact_state` (`pending`, `trusted`, `quarantined`, `ignored`, `revoked`)
- `primary_device_ref` nullable
- `linked_group_ref` nullable
- `future_introduction_policy_ref` nullable
- `approval_summary`
- `successor_policy`
- `provenance_ref` nullable

Questions it answers:

- do we know this peer already?
- are they merely remembered, actively trusted, or deliberately ignored?
- what future approval or introduction rights exist, if any?

### Pending peer record

A queue record for an unknown or newly introduced peer.

Fields:

- `pending_peer_id`
- `observed_identity`
- `source` (`manual-invite`, `linked-introduction`, `share-announcement`, `recovery`, `direct-contact`)
- `candidate_contact_ref` nullable
- `candidate_link_ref` nullable
- `candidate_claim_ref` nullable
- `decision_status` (`pending`, `accepted`, `dismissed`, `ignored`, `quarantined`)
- `expires_at` nullable
- `provenance_ref` nullable

Rules:

- pending peers do not automatically create grants
- pending peers do not automatically create mounts
- a durable ignore decision should suppress future identical contact unless reviewed or revoked

### Introduction policy

A policy controlling whether one trusted device or link group may surface more peers.

Fields:

- `introduction_policy_id`
- `scope_type` (`link`, `share`, `tag`)
- `scope_id`
- `mode` (`disabled`, `pending-only`, `share-scoped`, `bounded-auto-link`)
- `max_permission`
- `requires_claim` boolean
- `requires_preflight` boolean
- `visible_share_scope` (`none`, `matched-only`, `all-in-scope`)
- `provenance_ref` nullable

Rules:

- `disabled` is the ordinary default
- `pending-only` may surface a peer without trusting it
- `bounded-auto-link` is intentionally rare and should usually require a plan or steward approval

### Approval grant

A bounded future-approval object.

This document does not redefine the approval object from the main interface spec.
It tightens its operational meaning:

- future approval should consume a named object, not hidden certificate memory
- successor carry-forward should be explicit
- linked-device exercise of an approval should be policy-scoped, not ambient

### Succession plan

A reviewed continuity plan for replacing one device with another.

Fields:

- `succession_plan_id`
- `predecessor_device_ref`
- `successor_device_ref`
- `contact_actions[]` (`carry`, `freeze`, `drop`, `review`)
- `approval_actions[]` (`carry`, `freeze`, `drop`, `review`)
- `grant_actions[]` (`carry`, `rebind`, `freeze`, `drop`)
- `route_actions[]` (`drop-known-hosts`, `review-known-hosts`, `carry-approved`) 
- `recovery_prerequisites[]`
- `review_status`
- `provenance_ref` nullable

Questions it answers:

- what exactly is continuity here?
- which remembered relationships or approvals survive?
- what must be re-approved by a human?

## Effective semantics

### Default personal constellation

A conservative personal-device constellation should usually behave like this:

1. linking creates relationship state only
2. shares may become visible as incoming state, not mounted paths
3. unknown peers introduced through the constellation land in pending state
4. future approval is absent unless explicitly granted
5. replacement continuity is reviewed through succession, not inferred from linking

### Bounded introduction mode

A stricter convenience posture may allow one trusted peer to introduce additional peers within one share class or one link group.
Even then, the usual outcome should be pending contact plus claimable visibility, not ambient owner-like authority.

### Successor replacement

A successor plan should be able to say:

- carry ordinary contact memory
- freeze all future approval until review
- rebind selected grants only after recovery preconditions pass
- drop old known-host direct paths unless re-verified

That gives AnonSync a much cleaner answer than “link the new laptop and hope the old authority model still makes sense.”

## CLI contract

### `anonsync contact`

```text
anonsync contact list
anonsync contact show ctc_01J...
anonsync contact trust ctc_01J... --class collaborator
anonsync contact quarantine ctc_01J... --reason "unexpected key rotation"
anonsync contact ignore ctc_01J... --reason "unsolicited peer"
anonsync contact set ctc_01J... --future-introductions pending-only
```

### `anonsync pending peer`

```text
anonsync pending peer list
anonsync pending peer show ppd_01J...
anonsync pending peer accept ppd_01J... --as-contact alex --plan
anonsync pending peer dismiss ppd_01J... --reason "review later"
anonsync pending peer ignore ppd_01J... --reason "unsolicited contact"
```

### `anonsync link`

```text
anonsync link set personal --introduction-policy disabled
anonsync link set personal --introduction-policy pending-only
anonsync link show personal --explain
```

### `anonsync device replace`

```text
anonsync device replace laptop-old --successor laptop-new --plan
anonsync device succession show scp_01J...
```

The plan output should say exactly which contacts, approvals, grants, and known-host records are carried, frozen, or dropped.

## API and event expectations

The daemon API should expose:

- contacts
- pending peers
- introduction-policy state through link or policy resources
- succession-plan detail through retirement/recovery resources

The event stream should expose at least:

- `contact.created`
- `contact.trusted`
- `contact.ignored`
- `pending_peer.observed`
- `pending_peer.accepted`
- `pending_peer.ignored`
- `succession.review_required`
- `succession.completed`

## Why this matters

This spec exists so AnonSync can keep the strongest part of modern sync convenience — easy multi-device and small-team operation — without inheriting the sloppiest part of the authority model.

The goal is not to make everything manual.
The goal is to make convenience compile into legible, bounded, inspectable state.
