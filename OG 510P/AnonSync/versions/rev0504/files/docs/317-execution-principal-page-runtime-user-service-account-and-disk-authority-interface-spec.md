# Execution principal page: runtime user, service account, and disk authority interface spec

## Purpose

This page answers one ordinary question:

> what exact OS principal is acting for this seat right now, why did that principal win, and what filesystem authority does that principal currently have over the subjects this seat claims to manage?

The page exists because `desktop app`, `service`, `daemon`, `headless host`, and `NAS package` are not merely launch styles.
They are different authority contracts with different path reach, storage roots, and continuity risk.

## Core decision

Every seat must render one first-class **Execution principal** page.
That page owns:

- runtime principal identity
- launch mode and host class
- selected storage root
- disk-authority summary
- continuity risk of switching to another principal
- the next honest action if authority is weaker than the seat claims

The workbench must not force the operator to infer runtime authorship from a tray icon, a service name, or a hidden path.

## Primary layout

The page always renders the same regions in the same order:

1. seat strip
2. principal contract card
3. storage-root card
4. disk-authority card
5. switch-risk card
6. principal receipts

### 1) Seat strip

Show:

- seat label
- host class: `desktop user session`, `service`, `daemon`, `headless user session`, `nas package`, `other host`
- runtime principal label
- current verdict: `authority-clear`, `authority-partial`, `authority-blocked`, `world-ambiguous`
- one next honest action

### 2) Principal contract card

This card publishes:

- effective runtime principal
- how that principal was chosen: `interactive login`, `configured service account`, `package default`, `manual daemon launch`, `other`
- whether the principal is mutable from this surface
- whether the principal is ordinary-user, system-level, package-internal, or provider-scoped
- whether another candidate principal exists and what stronger or weaker authority it would imply

The operator must be able to answer: **who is actually acting on disk for this seat?**

### 3) Storage-root card

This card publishes:

- canonical storage-root path or handle
- why this root won
- what state families live there: `identity`, `settings`, `share inventory`, `logs`, `diagnostics`, `other`
- whether the current root is tied to the current principal
- whether changing principal would imply a different storage root or a successor-world review

The operator must be able to answer: **which local world belongs to this principal?**

### 4) Disk-authority card

This card publishes:

- total subjects under management
- subjects with confirmed read authority
- subjects with confirmed write authority
- subjects with partial or stale authority proof
- strongest known blocker: `owner mismatch`, `group mismatch`, `acl/provider denial`, `path missing`, `network mount caveat`, `unknown`

The operator must be able to answer: **how much real disk authority does this principal currently have?**

### 5) Switch-risk card

This card publishes:

- proposed alternative principal or launch mode
- same-world versus successor-world verdict
- expected changes to storage root, identity custody, and visible share inventory
- whether reconnect / re-share / rebind work would be required
- minimum safe checkpoint before switching

The operator must be able to answer: **what breaks or forks if I switch principals?**

### 6) Principal receipts

Receipts show:

- principal changes
- launch-mode changes
- storage-root changes
- authority verdict changes
- switch reviews acknowledged or applied
- the actor and time

## Non-negotiable rules

### Rule 1 — the product may not hide behind the brand name

`AnonSync is syncing` is never a sufficient author.
The page must publish which OS principal is actually touching bytes.

### Rule 2 — principal and storage root stay adjacent

A runtime principal without its storage root is incomplete.
A storage root without its principal is misleading.
The page must keep them adjacent.

### Rule 3 — stronger authority must not look consequence-free

A switch from user-session authority to system-level authority may widen reach while also crossing into a different local world.
The page must publish both sides.

## Honest outputs

The page may conclude:

- `Running as current user; storage root preserved; write authority confirmed for 18 of 18 managed subjects.`
- `Running as package-internal user; two paths blocked by missing folder grant.`
- `Switch to Local System would widen path access but create a successor local world with empty inventory until rebind.`
- `Runtime principal unclear because launch path and storage root disagree; world review required.`

It may not collapse those outcomes into one generic `service running` badge.
