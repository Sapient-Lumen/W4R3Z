# Join review page: approval requirement, link expiry, use count, and existing-peer memory interface spec

## Purpose

This page exists for the moment when a user is about to share a subject or approve an arriving peer and needs one concrete answer:

> what exactly will this join path require, who gets in automatically, when does this invitation stop working, and what ambiguity remains?

## Core decision

AnonSync must treat **join review** as first-class review state whenever admission truth depends on instrument choice, approval memory, link lifetime, or use-count limits.

## Review layout

1. **Join summary rail**
2. **Instrument comparison card**
3. **Approval-memory matrix**
4. **Expiry and use-count decision card**
5. **Receipts and next actions**

### 1) Join summary rail

Show:

- `selected_instrument`
- `selected_permission_class`
- `approval_requirement`
- `existing_peer_memory_rule`
- `expiry_rule`
- `use_count_rule`

Supported summary states:

- `key-no-approval`
- `link-auto-join`
- `link-approval-for-new-peers`
- `link-approval-for-all-peers`
- `time-limited-link`
- `use-limited-link`
- `qr-rendered-link`
- `unknown`

The operator must be able to answer:

> what will happen to the next person who receives this thing?

### 2) Instrument comparison card

Compare these columns side by side:

- `standard key`
- `read-only key`
- `link`
- `link rendered as QR`
- `identity-linked automatic appearance`

Each row must show:

- approval behavior
- expiry behavior
- use-count behavior
- install/browser handoff behavior
- grant-memory behavior
- strongest safe sentence

Hard rule:

- the page may never imply that QR alters authority or persistence; it only changes how the payload is delivered.

### 3) Approval-memory matrix

This matrix must separate:

- never approved peer
- already approved peer joining the same folder again
- already approved peer joining another shared folder
- peer arriving through a key that bypasses approval
- linked-identity appearance where no per-folder prompt exists

Each cell must show one of:

- `auto-admits`
- `asks-again`
- `approval-not-used`
- `not-applicable`
- `unknown`

And it must include a short reason.

The operator must be able to answer:

> who benefits from remembered trust, and where does remembered trust stop?

### 4) Expiry and use-count decision card

Show these truths separately:

- invitation valid until time
- invitation valid for remaining use count
- invitation expired for future joins
- already-issued grant unaffected by expiry
- current effect unknown

High-surprise callouts must include:

- `Expiry blocks new joins; it does not by itself retract already-issued access.`
- `Use count is consumed by successful use of the link, not by mere possession of the copied text.`
- `Choosing a key bypasses approval rather than satisfying it.`
- `Switching to QR does not create a safer or narrower credential.`

### 5) Receipts and next actions

Action rows must include:

- `share as key`
- `share as link`
- `set approval mode`
- `set expiry`
- `set use limit`
- `generate receipt`

Each action row must show:

- intended effect
- what stronger sentence remains blocked
- likely surprise cost
- review freshness

## Hard rules

- join review must focus on what the operator is about to cause, not just raw settings
- link expiry must never be described as revocation without a separate proof
- remembered approval must stay scoped; the product may not over-generalize it
- key choice must visibly translate into approval bypass, not just a UI mode switch
